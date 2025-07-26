import os
from supabase import create_client, Client
from src import config

PROCESSED_URLS_FILE = "processed_urls.txt"

try:
    supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
except Exception as e:
    raise ImportError(f"Supabase客户端初始化失败: {e}")

def load_processed_urls() -> set:
    """Loads the set of already processed URLs from a file."""
    if not os.path.exists(PROCESSED_URLS_FILE):
        return set()
    with open(PROCESSED_URLS_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_processed_url(url: str):
    """Appends a new URL to the processed URLs file."""
    with open(PROCESSED_URLS_FILE, "a") as f:
        f.write(url + "\n")

def get_all_materials(limit: int = 100) -> list:
    """
    获取所有材料。
    
    Args:
        limit: 返回数量限制
        
    Returns:
        所有材料列表
    """
    try:
        response = supabase.table('materials').select('*').order('created_at', desc=True).limit(limit).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ 获取所有材料时出错: {e}")
        return []

def get_material(material_id: int) -> dict:
    """
    获取单个材料。
    
    Args:
        material_id: 材料ID
        
    Returns:
        材料详情
    """
    try:
        response = supabase.table('materials').select('*').eq('id', material_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ 获取材料时出错: {e}")
        return None

def update_material(material_id: int, title: str, content: str) -> bool:
    """
    更新材料。
    
    Args:
        material_id: 材料ID
        title: 新标题
        content: 新内容
        
    Returns:
        是否成功
    """
    try:
        response = supabase.table('materials').update({
            'title': title,
            'material_content': {
                'content': content
            }
        }).eq('id', material_id).execute()
        return True
    except Exception as e:
        print(f"❌ 更新材料时出错: {e}")
        return False