import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# --- AI Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

# --- Supabase Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Validation ---
# 确保关键配置都已设置，否则程序启动时会报错，方便调试
if not OPENAI_API_KEY:
    raise ValueError("错误: 环境变量 OPENAI_API_KEY 未设置。")
if not OPENAI_API_BASE_URL:
    raise ValueError("错误: 环境变量 OPENAI_API_BASE_URL 未设置。")
if not SUPABASE_URL:
    raise ValueError("错误: 环境变量 SUPABASE_URL 未设置。")
if not SUPABASE_KEY:
    raise ValueError("错误: 环境变量 SUPABASE_KEY 未设置。")
