# path: src/ai_processor.py

import json
import openai
from src import config
from src.prompts import SYSTEM_PROMPT, create_user_prompt, MODERATION_SYSTEM_PROMPT, create_moderation_user_prompt, DESCRIPTION_SYSTEM_PROMPT, create_description_user_prompt
import re

# Import json5 for robust JSON parsing
try:
    import json5
except ImportError:
    json5 = None
    print("🚨 警告：json5库未安装。请运行 'pip install json5' 以获得更健壮的JSON解析能力。")

# 初始化 OpenAI 客户端
try:
    client = openai.OpenAI(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_API_BASE_URL,
    )
except Exception as e:
    raise ImportError(f"OpenAI客户端初始化失败: {e}")

def is_article_safe(title: str, content: str) -> bool:
    """
    Checks if an article is safe for distribution.

    Args:
        title: The title of the article.
        content: The content of the article.

    Returns:
        True if the article is safe, False otherwise.
    """
    print(f"🛡️  Performing safety check for: {title}")
    user_prompt = create_moderation_user_prompt(title, content)
    try:
        completion = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[
                {"role": "system", "content": MODERATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=5,
            extra_body={"chat_template_kwargs": {"thinking":False}},
        )

        message = completion.choices[0].message
        
        # --- 健壮性修复 ---
        # 在调用 .strip() 之前，检查 message 和 message.content 是否存在
        if message and message.content:
            response = message.content.strip().lower()
            if response == "safe":
                print("✅ Safety check passed.")
                return True
            else:
                print(f"❌ Safety check failed. Reason from AI: {response}")
                return False
        else:
            # 如果AI返回空内容，则默认为不安全，保证"安全失败"
            print("❌ Safety check failed. Reason: AI returned an empty response.")
            return False
        # --- 修复结束 ---

    except openai.APIError as e:
        print(f"Could not complete safety check due to API error: {e}")
        return False # Fail safe
    except Exception as e:
        # 增加一个通用的异常捕获，以防其他意外错误
        print(f"An unexpected error occurred during safety check: {e}")
        return False # Fail safe

def generate_material_description(material_data: dict) -> str:
    """
    使用AI为材料生成自然、吸引人的描述。

    Args:
        material_data: 完整的材料数据字典

    Returns:
        AI生成的材料描述
    """
    print("🎨 正在使用AI生成材料描述...")
    
    user_prompt = create_description_user_prompt(material_data)
    
    try:
        completion = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[
                {"role": "system", "content": DESCRIPTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,  # 稍高的温度以获得更有创意的描述
            max_tokens=500,   # 限制描述长度
            extra_body={"chat_template_kwargs": {"thinking":False}},
        )

        message = completion.choices[0].message
        
        if message and message.content:
            description = message.content.strip()
            print(f"✅ AI描述生成成功，长度: {len(description)} 字符")
            return description
        else:
            print("❌ AI返回空描述")
            return ""

    except openai.APIError as e:
        print(f"❌ AI API错误: {e}")
        return ""
    except Exception as e:
        print(f"❌ 生成描述时发生未知错误: {e}")
        return ""

def generate_reading_material(title: str, content: str, url: str) -> dict:
    """
    调用AI模型生成精读材料，使用流式传输并在终端实时输出，并进行健壮的JSON解析。

    Args:
        title: 文章标题。
        content: 文章正文。

    Returns:
        一个解析好的Python字典。
    """
    print("🔄 正在调用AI模型生成精读内容（流式传输）...")
    
    user_prompt = create_user_prompt(title, content, url)
    
    try:
        # 创建流式请求
        stream = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"}, 
            extra_body={"chat_template_kwargs": {"thinking":False}},
            max_tokens=3533000,
            stream=True
        )
        
        print("📡 开始接收流式响应...")
        print("-" * 50)
        
        raw_response = ""
        
        # 处理流式响应
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                chunk_content = chunk.choices[0].delta.content
                raw_response += chunk_content
                
                # 实时输出到终端
                print(chunk_content, end='', flush=True)
        
        print()
        print("-" * 50)
        print("✅ 流式传输完成")
        
        # --- 鲁棒性 JSON 解析处理 ---
        parsed_json = None
        
        # 尝试标准JSON解析
        try:
            parsed_json = json.loads(raw_response)
            print("✅ AI内容生成完毕，标准JSON解析成功。")
            return parsed_json
        except json.JSONDecodeError as e:
            print(f"⚠️ 标准JSON解析失败: {e}。尝试使用更健壮的解析器...")
            
        # 尝试使用json5进行更健壮的解析
        if parsed_json is None and json5:
            try:
                parsed_json = json5.loads(raw_response)
                print("✅ 使用json5成功解析。")
                return parsed_json
            except Exception as json5_e:
                print(f"❌ json5解析失败: {json5_e}")
        elif parsed_json is None and not json5:
            print("🚨 警告：json5库未安装，无法进行更健壮的JSON解析。")

        # 最终尝试：手动提取JSON字符串并再次尝试标准解析
        if parsed_json is None:
            print("⚠️ 尝试手动提取JSON对象并解析...")
            try:
                # 使用正则表达式来更准确地查找可能的JSON对象
                # 这个正则表达式尝试匹配一个以'{'开始并以'}'结束，并且中间可能包含任何字符的字符串，
                # 但对于嵌套结构和复杂错误仍有限。
                match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if match:
                    json_str_potential = match.group(0)
                    parsed_json = json.loads(json_str_potential)
                    print("✅ 手动提取并标准JSON解析成功。")
                    return parsed_json
                else:
                    raise ValueError("在AI响应中找不到有效的JSON对象结构。")
            except (json.JSONDecodeError, ValueError) as e:
                print("❌ 最终解析失败。")
                print("--- 原始响应 ---")
                print(raw_response)
                print("-----------------")
                raise ValueError(f"无法解析AI的响应: {e}")

    except openai.APIError as e:
        raise ConnectionError(f"AI API返回错误: {e}")
    except Exception as e:
        raise RuntimeError(f"调用AI时发生未知错误: {e}")

def generate_preview_content(material_data: dict) -> dict:
    """
    基于完整的material_data生成预览内容，只包含前2个段落和部分词汇。
    
    Args:
        material_data: 完整的材料数据字典
        
    Returns:
        预览内容的字典
    """
    try:
        preview_data = {
            "type": material_data.get("type", "foreign_reading"),
            "version": material_data.get("version", "1.0"),
            "source": material_data.get("source", ""),
            "metadata": material_data.get("metadata", {}),
            "content": {
                "title": material_data.get("content", {}).get("title", {}),
                "paragraphs": [],
                "summary": {
                    "english": "Preview available. Full content includes detailed analysis of all paragraphs.",
                    "chinese": "预览版本。完整版本包含所有段落的详细分析。"
                }
            }
        }
        
        original_paragraphs = material_data.get("content", {}).get("paragraphs", [])[:2]
        for paragraph in original_paragraphs:
            preview_paragraph = paragraph.copy()
            if "analysis" in preview_paragraph and "vocabulary" in preview_paragraph["analysis"]:
                preview_paragraph["analysis"]["vocabulary"] = preview_paragraph["analysis"]["vocabulary"][:2]
            if "analysis" in preview_paragraph and "grammar" in preview_paragraph["analysis"]:
                 if "points" in preview_paragraph["analysis"]["grammar"]:
                    preview_paragraph["analysis"]["grammar"]["points"] = preview_paragraph["analysis"]["grammar"]["points"][:1]
            
            preview_data["content"]["paragraphs"].append(preview_paragraph)
        
        preview_data["content"]["preview_note"] = "This is a preview version. Full content contains analysis of all paragraphs with complete vocabulary and grammar explanations."
        
        return preview_data
        
    except Exception as e:
        print(f"⚠️ 生成预览内容时出错: {e}")
        return {
            "type": "foreign_reading",
            "version": "1.0",
            "content": {
                "title": material_data.get("content", {}).get("title", {"english": "Preview", "chinese": "预览"}),
                "preview_note": "Preview content generation failed. Please check the full content."
            }
        }