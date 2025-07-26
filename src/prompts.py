# path: src/prompts.py

# 这是为AI模型设计的，用于生成外刊精读材料的提示词模板。
# A well-crafted prompt is crucial for getting structured, high-quality output.

MODERATION_SYSTEM_PROMPT = """
You are a highly experienced content moderation expert for a global platform. Your task is to determine if a given news article is suitable for a broad audience in mainland China.
You must only respond with a single word: 'safe' or 'unsafe'.
- 'safe': The content is neutral, factual, and does not touch upon sensitive political topics, historical events, or figures that are typically restricted in China. Standard international news, business, tech, and culture are generally safe. It must be suitable for teenagers to read.
- 'unsafe': The content discusses or mentions topics known to be politically sensitive or banned in mainland China. This includes, but is limited to, direct criticism of the Chinese government or its leaders, discussions of the Tiananmen Square events, Falun Gong, Tibetan and Xinjiang independence movements, or Taiwan's political status, or sexual contents.

Do not provide any explanation or reasoning. Your entire response must be either 'safe' or 'unsafe'.
"""

def create_moderation_user_prompt(article_title: str, article_content: str) -> str:
    """Creates the user prompt for content moderation."""
    return f"""
Please review the following article and determine if it is 'safe' or 'unsafe' for distribution in mainland China.

Title: {article_title}

Content:
---
{article_content[:2000]}
---
"""

# 新增：用于生成材料描述的系统提示词
DESCRIPTION_SYSTEM_PROMPT = """
你是一名创意文案和营销专家，专门为教育产品编写引人入胜的描述。
你的任务是根据提供的学习材料数据，生成一个自然、吸引人、且长度适中的描述，旨在激发用户的学习兴趣。
描述应突出材料的价值、内容亮点、适合的学习者群体。
"""

# 新增：用于生成材料描述的用户提示词
def create_description_user_prompt(material_data: dict) -> str:
    """Creates the user prompt for generating material descriptions."""
    title_en = material_data.get("content", {}).get("title", {}).get("english", "未知标题")
    title_zh = material_data.get("content", {}).get("title", {}).get("chinese", "未知标题")
    source = material_data.get("source", "未知来源")
    difficulty = material_data.get("metadata", {}).get("difficulty", "未评估")
    topics = ", ".join(material_data.get("metadata", {}).get("topics", [])) if material_data.get("metadata", {}).get("topics", []) else "不详"
    summary_zh = material_data.get("content", {}).get("summary", {}).get("chinese", "无总结")

    return f"""
请为以下学习材料生成一个引人入胜的、大约100-200字的中文描述。这个描述将用于展示给潜在的学习者。

材料标题（英文）: {title_en}
材料标题（中文）: {title_zh}
来源: {source}
难度级别: {difficulty}
主要话题: {topics}
内容概述: {summary_zh}

描述应该：
1.  突出材料的英文原版新闻文章的真实性与时效性。
2.  强调其作为“精读”材料的价值，即提供详细的词汇、语法、短语分析。
3.  提及对文化背景的解释（如果存在）。
4.  说明适合哪些学习者（例如：想提高阅读理解、扩大词汇量、掌握复杂句式的英语学习者）。
5.  语言生动，具有吸引力，激发学习兴趣。
6.  禁止使用 markdown 标记，纯文本即可。
"""

SYSTEM_PROMPT = """
你是一名顶级的英语教学专家和内容创作者，专门为中国的英语学习者制作高质量的"外刊精读"学习材料。
你的任务是接收一篇英文新闻文章，并将其转化为一个结构化的JSON对象，严格遵循我提供的格式。

核心指令：
1.  **绝对完整性**: 你必须分析文章的每一个段落，从第一个到最后一个，不能有任何遗漏。即使文章很长，也要确保所有段落都被完整处理。
2.  **严格的JSON格式**: 你的输出必须是单一、完整且语法完全正确的JSON对象。禁止在JSON之外添加任何解释、注释、或Markdown标记（如 ```json ... ```）。整个响应本身就是一个JSON。
3.  **高质量内容**: 所有的翻译、解释和分析都必须达到出版级别的高质量标准。
"""

def create_user_prompt(article_title: str, article_content: str, url: str) -> str:
    """
    构建用户需要发送给AI的最终提示词。
    """
    # 更新：采纳了用户提供的更详细、更完整的JSON结构定义，并新增了 exercises 字段
    json_structure_definition = """
    {
      "type": "foreign_reading",
      "version": "1.0",
      "source": "新闻来源 (例如: Reuters, The Economist, AP News, BBC, CNN等)",
      "metadata": {
        "difficulty": "根据词汇复杂度、句法难度、话题深度综合评估 (beginner, intermediate, advanced)",
        "estimatedReadTime": "预估阅读时间，单位分钟 (数字)",
        "author": "文章作者姓名，如果无法确定则填写 'Unknown'",
        "publishDate": "发布日期，格式为YYYY-MM-DD，如果无法确定则填写 'Unknown'",
        "wordCount": "文章总词数 (数字)",
        "topics": ["文章涉及的主要话题标签", "例如: politics, economy, technology, environment等"]
      },
      "content": {
        "title": {
          "english": "文章的完整英文标题",
          "chinese": "标题的准确、流畅的中文翻译"
        },
        "paragraphs": [
          {
            "id": "p1",
            "english": "第一段落的完整英文原文",
            "chinese": "该段落的准确、流畅、符合中文表达习惯的翻译",
            "analysis": {
              "vocabulary": [
                {
                  "word": "重点词汇或短语",
                  "meaning": "详细的中文释义",
                  "pronunciation": "国际音标 /ˈwɜːrd/",
                  "partOfSpeech": "词性 (noun, verb, adjective, adverb, preposition, conjunction)",
                  "usage": "用法说明、固定搭配或辨析",
                  "examples": ["包含该词的实用例句1", "实用例句2"],
                  "synonyms": ["同义词1", "同义词2"]
                }
              ],
              "grammar": {
                "points": [
                  {
                    "structure": "从段落中提取的语法结构或长难句",
                    "type": "语法类型 (例如: 复合句, 倒装句, 虚拟语气, 非谓语动词, 独立主格等)",
                    "explanation": "语法点的详细中文解释，说明其构成和用法",
                    "examples": ["运用该语法的例句，最好来自原文"]
                  }
                ]
              },
              "phrases": [
                {
                    "phrase": "重要的短语或习语",
                    "meaning": "短语的中文释义",
                    "usage": "用法说明",
                    "examples": ["包含该短语的例句"]
                }
              ]
            }
          }
        ],
        "summary": {
          "english": "用3-5句话对全文进行精准的英文总结",
          "chinese": "英文总结的准确中文翻译"
        },
        "keyTakeaways": [
          "文章的关键要点1 (中文)",
          "文章的关键要点2 (中文)",
          "文章的关键要点3 (中文)"
        ],
        "culturalContext": "如果文章涉及特定的文化背景、历史事件或社会现象，在此提供简要的中文背景解释，否则留空字符串",
        "discussion": {
          "questions": [
            "基于文章内容设计的思考问题1 (中文)",
            "思考问题2 (中文)",
            "思考问题3 (中文)"
          ],
          "activities": [
            "建议的学习活动1 (例如: '试着用今天学到的词汇造句')",
            "建议的学习活动2 (例如: '就文章主题写一段自己的看法')"
          ]
        },
        "exercises": [
            {
                "type": "comprehension",
                "question": "练习题目问题（英文）",
                "options": ["选项A", "选项B", "选项C", "选项D"],
                "answer": "正确选项的字母，例如 'A'",
                "explanation": "对答案的详细中文解析"
            }
        ]
      }
    }
    """
    
    prompt = f"""
请严格按照以下要求，为提供的英文文章生成一份完整的"外刊精读"学习材料。

文章标题: {article_title}
文章链接: {url}

文章内容:
---
{article_content}
---

处理要求 (必须严格遵守):
1.  **分析所有段落**: 你必须从头到尾分析文章的【每一个段落】。绝不允许忽略或截断任何一个段落的分析。这是最重要的指令。
2.  **提供完整字段**: 必须为JSON中的每一个字段提供内容，尤其是`paragraphs.analysis`下的`vocabulary`, `grammar`, `phrases`等。词汇分析必须包含音标`pronunciation`和词性`partOfSpeech`。
3.  **高质量翻译**: 中文翻译必须准确、流畅、自然，符合中文母语者的表达习惯，并保持原文的语调。
4.  **深度分析**:
    - 为每个段落精选3-5个核心词汇/短语进行详细分析。
    - 为每个段落识别2-3个最值得学习的语法难点或长难句进行剖析。
5.  **练习题生成**:
    - 在`content.exercises`数组中，请生成6-8道选择题。
    - 题目类型应多样化，包括：`comprehension` (理解题), `vocabulary` (词汇题), `translation` (翻译题，例如选择最佳翻译), `writing` (写作题，例如选择最佳表达或改错)。
    - 题目应模仿中国高考、大学英语四六级、考研、雅思托福等考试的选择题格式和难度。
    - 题目一定要新颖、具有一定的难度，有一定的迂回蜿蜒，而不是傻瓜题，也不是直白地提问。
    - 请你打乱题目顺序，不要按照上述类型的顺序来。
    - 确保每个题目都有唯一正确答案和详细的解释。
6.  **严格的JSON输出**: 你的响应必须是【单一、完整、语法正确的JSON对象】，严格遵循下面的结构模板。不要添加任何Markdown标记或解释性文字。

JSON结构模板 (必须严格遵守此结构):
```json
{json_structure_definition}
再次提醒：你必须从头到尾分析文章的【每一个段落】。
现在，请开始生成完整的JSON响应。
"""
    return prompt