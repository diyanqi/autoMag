# path: src/supabase_uploader.py

from supabase import create_client, Client
from src import config
from src.ai_processor import generate_preview_content, generate_material_description
import re
from datetime import datetime

# 初始化 Supabase 客户端
try:
    supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
except Exception as e:
    raise ImportError(f"Supabase客户端初始化失败: {e}")

def extract_tags_from_material(material_data: dict) -> list:
    """
    从AI生成的材料中智能提取标签。
    
    Args:
        material_data: AI生成的完整材料数据
        
    Returns:
        标签列表
    """
    tags = set()
    
    # 添加基础标签
    tags.add("外刊精读")
    tags.add("英语学习")
    
    # 从来源添加标签
    source = material_data.get("source", "")
    if source:
        tags.add(source)
    
    # 从元数据添加标签
    metadata = material_data.get("metadata", {})
    
    # 添加难度标签
    difficulty = metadata.get("difficulty", "")
    if difficulty:
        difficulty_map = {
            "beginner": "初级",
            "intermediate": "中级", 
            "advanced": "高级"
        }
        tags.add(difficulty_map.get(difficulty, difficulty))
    
    # 添加话题标签
    topics = metadata.get("topics", [])
    topic_map = {
        "politics": "政治",
        "economy": "经济", 
        "technology": "科技",
        "environment": "环境",
        "health": "健康",
        "education": "教育",
        "culture": "文化",
        "sports": "体育",
        "business": "商业",
        "science": "科学"
    }
    
    for topic in topics:
        if topic in topic_map:
            tags.add(topic_map[topic])
        else:
            tags.add(topic)
    
    # 从标题中提取关键词作为标签
    title = material_data.get("content", {}).get("title", {}).get("english", "")
    if title:
        # 简单的关键词提取（可以根据需要改进）
        keywords = ["climate", "technology", "economy", "health", "education", "business", "politics"]
        for keyword in keywords:
            if keyword.lower() in title.lower():
                tags.add(keyword)
    
    return list(tags)

def generate_description(material_data: dict) -> str:
    """
    使用AI基于材料数据生成自然的描述。
    
    Args:
        material_data: AI生成的完整材料数据
        
    Returns:
        AI生成的描述文本
    """
    try:
        # 调用AI生成描述
        ai_description = generate_material_description(material_data)
        
        # 如果AI生成成功，返回AI描述
        if ai_description and len(ai_description.strip()) > 20:
            return ai_description.strip()
        else:
            print("⚠️ AI生成描述失败或内容过短，使用备用方案")
            # 如果AI生成失败，使用备用的简单描述
            return generate_fallback_description(material_data)
            
    except Exception as e:
        print(f"⚠️ AI生成描述时出错: {e}，使用备用方案")
        return generate_fallback_description(material_data)

def generate_fallback_description(material_data: dict) -> str:
    """
    备用的简单描述生成方案。
    
    Args:
        material_data: AI生成的完整材料数据
        
    Returns:
        生成的描述文本
    """
    try:
        content = material_data.get("content", {})
        
        # 基础信息
        title = content.get("title", {}).get("chinese", "精读材料")
        source = material_data.get("source", "知名外媒")
        difficulty = material_data.get("metadata", {}).get("difficulty", "intermediate")
        word_count = material_data.get("metadata", {}).get("wordCount", 0)
        read_time = material_data.get("metadata", {}).get("estimatedReadTime", 5)
        
        difficulty_map = {
            "beginner": "初级",
            "intermediate": "中级",
            "advanced": "高级"
        }
        difficulty_cn = difficulty_map.get(difficulty, "中级")
        
        # 统计词汇和语法点数量
        paragraphs = content.get("paragraphs", [])
        total_vocab = 0
        total_grammar = 0
        
        for para in paragraphs:
            analysis = para.get("analysis", {})
            total_vocab += len(analysis.get("vocabulary", []))
            total_grammar += len(analysis.get("grammar", {}).get("points", []))
        
        # 获取文章摘要
        summary = content.get("summary", {}).get("chinese", "")
        if len(summary) > 100:
            summary = summary[:100] + "..."
        
        # 生成描述
        description = f"来自{source}的{difficulty_cn}级英语精读材料。"
        
        if word_count > 0:
            description += f"全文约{word_count}词，"
        
        description += f"预计阅读时间{read_time}分钟。"
        
        if total_vocab > 0:
            description += f"包含{total_vocab}个重点词汇解析"
        
        if total_grammar > 0:
            description += f"和{total_grammar}个语法要点分析。"
        else:
            description += "。"
        
        if summary:
            description += f" 内容简介：{summary}"
        
        return description
        
    except Exception as e:
        print(f"⚠️ 生成备用描述时出错: {e}")
        return f"来自{material_data.get('source', '外媒')}的英语精读材料，适合英语学习者提升阅读理解能力。"

def clean_original_content(content: str) -> str:
    """
    清理原始内容，移除多余的空白和格式。
    
    Args:
        content: 原始文章内容
        
    Returns:
        清理后的内容
    """
    # 移除多余的空白行
    content = re.sub(r'\n\s*\n', '\n\n', content)
    # 移除首尾空白
    content = content.strip()
    # 限制长度（如果需要）
    if len(content) > 50000:  # 50KB限制
        content = content[:50000] + "...[内容被截断]"
    
    return content

def upload_material(material_data: dict, original_link: str, original_content: str = "", creator_email: str = "magBot@inkcraft.cn") -> dict:
    """
    将生成的素材JSON上传到Supabase数据库。

    Args:
        material_data: 由AI生成的完整JSON对应的字典。
        original_link: 文章的原始链接。
        original_content: 文章的原始内容。
        creator_email: 创建者邮箱地址。

    Returns:
        Supabase返回的插入结果。
    """
    print(f"📤 准备上传到Supabase...")

    try:
        # 从AI生成的数据中提取信息
        content = material_data.get("content", {})
        metadata = material_data.get("metadata", {})

        paragraph_count = len(content.get('paragraphs', []))

        if paragraph_count <= 5:
            # 认为出错了，不会上传到数据库
            print(f"⚠️ 文章段落数过少，仅有{str(paragraph_count)}段，不上传到数据库")
            return None
        
        # 提取标题
        title = content.get("title", {}).get("chinese", 
                content.get("title", {}).get("english", "未命名文章"))
        
        # 生成智能描述
        description = generate_description(material_data)
        
        # 提取和生成标签
        tags = extract_tags_from_material(material_data)
        
        # 生成预览内容
        preview_content = generate_preview_content(material_data)
        
        # 清理原始内容
        cleaned_original_content = clean_original_content(original_content) if original_content else ""
        
        # 生成价格
        price = 0.00
        featured = False
        if 11 <= paragraph_count <= 14:
            price = 0.10
        elif 15 <= paragraph_count <= 18:
            price = 0.20
        elif 19 <= paragraph_count <= 22:
            price = 0.30
        elif 23 <= paragraph_count <= 30:
            price = 0.40
            featured = True
        elif paragraph_count > 30:
            price = 0.50
            featured = True

        # 准备要插入的数据对象
        data_to_insert = {
            # 基础信息
            'title': title,
            'description': description,
            'tags': tags,
            'category': 'foreign_reading',  # 固定为外刊精读类别
            
            # 内容字段
            'original_content': cleaned_original_content,
            'original_link': original_link,
            'material_content': material_data,  # 完整的AI生成内容
            'preview_content': preview_content,  # 预览内容
            
            # 定价和权限
            'price': price,  # 默认免费，可以后续调整
            'creator_email': creator_email,
            'owners': [creator_email],  # 初始拥有者是创建者
            
            # 统计信息
            'purchase_count': 0,
            'view_count': 0,
            
            # 发布状态
            'is_published': True,   # 默认发布
            'is_featured': featured,   # 默认不推荐，可以后续手动调整
        }

        print(f"📊 上传信息摘要:")
        print(f"   标题: {title}")
        print(f"   来源: {material_data.get('source', 'Unknown')}")
        print(f"   难度: {metadata.get('difficulty', 'Unknown')}")
        print(f"   标签数量: {len(tags)}")
        print(f"   段落数量: {len(content.get('paragraphs', []))}")

        # 执行插入操作
        response = supabase.table('materials').insert(data_to_insert).execute()

        # 检查是否有错误
        if response.data:
            inserted_record = response.data[0]
            print(f"✅ 成功上传素材到Supabase!")
            print(f"   记录ID: {inserted_record['id']}")
            print(f"   创建时间: {inserted_record['created_at']}")
            print(f"   标题: {inserted_record['title']}")
            return inserted_record
        else:
            # 错误处理
            error_message = "未知错误"
            if hasattr(response, 'error') and response.error:
                error_message = f"Supabase API 错误: {response.error.message}"
            elif 'error_description' in str(response):
                error_message = f"Supabase API 错误: {response}"
            else:
                error_message = "Supabase返回了未知错误，但没有明确的错误信息。"
            
            raise Exception(error_message)

    except Exception as e:
        print(f"❌ 上传到Supabase时出错: {e}")
        raise ConnectionError(f"上传到Supabase时出错: {e}")

def update_material_stats(material_id: str, increment_views: bool = False, increment_purchases: bool = False) -> bool:
    """
    更新材料的统计信息。
    
    Args:
        material_id: 材料的ID
        increment_views: 是否增加浏览量
        increment_purchases: 是否增加购买量
        
    Returns:
        更新是否成功
    """
    try:
        updates = {}
        
        if increment_views:
            # 获取当前浏览量并增加1
            current = supabase.table('materials').select('view_count').eq('id', material_id).execute()
            if current.data:
                current_views = current.data[0].get('view_count', 0)
                updates['view_count'] = current_views + 1
        
        if increment_purchases:
            # 获取当前购买量并增加1
            current = supabase.table('materials').select('purchase_count').eq('id', material_id).execute()
            if current.data:
                current_purchases = current.data[0].get('purchase_count', 0)
                updates['purchase_count'] = current_purchases + 1
        
        if updates:
            response = supabase.table('materials').update(updates).eq('id', material_id).execute()
            if response.data:
                print(f"✅ 成功更新材料统计信息: {updates}")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ 更新统计信息时出错: {e}")
        return False

def get_material_by_id(material_id: str) -> dict:
    """
    根据ID获取材料信息。
    
    Args:
        material_id: 材料ID
        
    Returns:
        材料信息字典
    """
    try:
        response = supabase.table('materials').select('*').eq('id', material_id).execute()
        if response.data:
            return response.data[0]
        return {}
    except Exception as e:
        print(f"❌ 获取材料信息时出错: {e}")
        return {}

def search_materials(query: str = "", category: str = "", tags: list = [], limit: int = 20) -> list:
    """
    搜索材料。
    
    Args:
        query: 搜索关键词
        category: 类别筛选
        tags: 标签筛选
        limit: 返回数量限制
        
    Returns:
        材料列表
    """
    try:
        query_builder = supabase.table('materials').select('*')
        
        # 只显示已发布的材料
        query_builder = query_builder.eq('is_published', True)
        
        # 类别筛选
        if category:
            query_builder = query_builder.eq('category', category)
        
        # 标签筛选
        if tags:
            for tag in tags:
                query_builder = query_builder.contains('tags', [tag])
        
        # 关键词搜索（在标题和描述中搜索）
        if query:
            query_builder = query_builder.or_(f'title.ilike.%{query}%,description.ilike.%{query}%')
        
        # 排序和限制
        query_builder = query_builder.order('created_at', desc=True).limit(limit)
        
        response = query_builder.execute()
        return response.data if response.data else []
        
    except Exception as e:
        print(f"❌ 搜索材料时出错: {e}")
        return []

def get_featured_materials(limit: int = 10) -> list:
    """
    获取推荐材料。
    
    Args:
        limit: 返回数量限制
        
    Returns:
        推荐材料列表
    """
    try:
        response = supabase.table('materials').select('*').eq('is_published', True).eq('is_featured', True).order('created_at', desc=True).limit(limit).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ 获取推荐材料时出错: {e}")
        return []

def get_popular_materials(limit: int = 10) -> list:
    """
    获取热门材料（按浏览量排序）。
    
    Args:
        limit: 返回数量限制
        
    Returns:
        热门材料列表
    """
    try:
        response = supabase.table('materials').select('*').eq('is_published', True).order('view_count', desc=True).limit(limit).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ 获取热门材料时出错: {e}")
        return []

def get_recent_materials(limit: int = 20) -> list:
    """
    获取最新材料。
    
    Args:
        limit: 返回数量限制
        
    Returns:
        最新材料列表
    """
    try:
        response = supabase.table('materials').select('*').eq('is_published', True).order('created_at', desc=True).limit(limit).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ 获取最新材料时出错: {e}")
        return []