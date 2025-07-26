# autoMag - 自动化外刊精读内容生成器

`autoMag` 是一个Python项目，旨在自动化地从指定的在线新闻源抓取文章，利用AI（OpenAI兼容模型）生成结构化的“外刊精读”学习材料，并将其上传到Supabase数据库，为您的Next.js英语学习平台提供内容。

## 功能

- 从任意URL抓取新闻文章标题和正文。
- 调用AI模型，根据高度定制化的提示词生成包含词汇、语法、翻译和总结的JSON数据。
- 鲁棒的JSON解析机制，确保AI输出的稳定性。
- 将最终生成的数据无缝上传到指定的Supabase数据表。

## 设置步骤

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd autoMag
```

### 2. 创建并激活虚拟环境

推荐使用虚拟环境来管理依赖。

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

项目的所有敏感信息（API密钥等）都通过环境变量管理。

- 复制 `.env.example` 文件并重命名为 `.env`。
- 编辑 `.env` 文件，填入你自己的密钥和URL：
  - `OPENAI_API_KEY`: 你的OpenAI或兼容平台的API Key。
  - `OPENAI_API_BASE_URL`: API的端点URL。
  - `SUPABASE_URL`: 你的Supabase项目URL。
  - `SUPABASE_KEY`: 你的Supabase项目 **service_role key**。这非常重要，因为需要写权限。请妥善保管此密钥。

## 如何使用

配置完成后，你可以通过命令行来运行整个流程。只需提供一个你想处理的新闻文章URL即可。

```bash
source ./.venv/bin/activate
python main.py 
```

程序将会依次执行：抓取 -> AI处理 -> 上传，并在控制台输出每一步的状态。

## 注意事项

- **新闻抓取**: `src/news_fetcher.py` 中的抓取逻辑是通用的。对于一些结构特殊的网站，你可能需要进入该文件，微调BeautifulSoup的选择器（例如 `soup.find(...)` 部分）以获得最佳的抓取效果。
- **Supabase表结构**: `src/supabase_uploader.py` 中 `data_to_insert` 对象的键名需要与你Supabase中 `materials` 表的列名完全对应。请确保你已创建了该表，且 `content` 列的类型为 `JSONB`。
