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

## 素材内容 JSON 结构

```typescript
// 素材内容JSON结构定义

// 基础结构接口
interface BaseMaterialContent {
  type: string; // 素材类型标识
  version: string; // 版本号，便于升级兼容
  metadata?: {
    author?: string;
    source?: string;
    difficulty?: 'beginner' | 'intermediate' | 'advanced';
    estimatedReadTime?: number; // 预计阅读时间（分钟）
    lastUpdated?: string;
  };
}

// 1. 外刊精读类型
interface ForeignReadingContent extends BaseMaterialContent {
  type: 'foreign_reading';
  source: string; // 来源：The Economist, Financial Times, etc.
  content: {
    title?: {
      english: string;
      chinese: string;
    };
    paragraphs: Array<{
      id?: string; // 段落ID，便于引用
      english: string; // 英文原文
      chinese: string; // 中文翻译
      analysis?: {
        vocabulary?: Array<{
          word: string;
          meaning: string;
          pronunciation?: string; // 音标
          usage?: string; // 用法说明
          examples?: string[]; // 例句
          synonyms?: string[]; // 同义词
          collocations?: string[]; // 搭配
        }>;
        grammar?: {
          points: Array<{
            structure: string; // 语法结构
            explanation: string; // 解释
            examples?: string[]; // 例句
          }>;
        };
        phrases?: Array<{
          phrase: string;
          meaning: string;
          usage?: string;
        }>;
        background?: string; // 背景知识
        culturalNotes?: string; // 文化注释
      };
      difficulty?: 'easy' | 'medium' | 'hard';
    }>;
    exercises?: Array<{
      type: 'comprehension' | 'vocabulary' | 'translation' | 'writing';
      question: string;
      options?: string[]; // 选择题选项
      answer?: string; // 答案
      explanation?: string; // 解析
    }>;
    summary?: {
      english: string;
      chinese: string;
    };
  };
}

// 2. 通用素材类型
interface GeneralMaterialContent extends BaseMaterialContent {
  type: 'general_material';
  content: {
    sections: Array<{
      id?: string;
      title: string;
      subtitle?: string;
      items: string[]; // 内容项目
      notes?: string[]; // 注释
      examples?: Array<{
        text: string;
        explanation?: string;
      }>;
    }>;
    templates?: Array<{
      title: string;
      content: string;
      usage?: string; // 使用场景
      variables?: string[]; // 可替换变量
    }>;
    exercises?: Array<{
      type: string;
      content: string;
      answer?: string;
      tips?: string[];
    }>;
    references?: Array<{
      title: string;
      url?: string;
      author?: string;
    }>;
  };
}

// 3. 扩展类型示例：视频讲解素材
interface VideoMaterialContent extends BaseMaterialContent {
  type: 'video_material';
  content: {
    videoUrl: string;
    duration: number; // 秒
    transcript?: string; // 字幕/文稿
    chapters?: Array<{
      title: string;
      startTime: number; // 开始时间（秒）
      endTime: number; // 结束时间（秒）
      description?: string;
    }>;
    supplementary?: {
      slides?: string[]; // 课件图片URLs
      notes?: string; // 补充笔记
      resources?: Array<{
        title: string;
        url: string;
        type: 'pdf' | 'doc' | 'link' | 'image';
      }>;
    };
  };
}

// 4. 扩展类型示例：音频材料
interface AudioMaterialContent extends BaseMaterialContent {
  type: 'audio_material';
  content: {
    audioUrl: string;
    duration: number;
    transcript?: string;
    speed?: 'slow' | 'normal' | 'fast';
    accent?: 'american' | 'british' | 'australian' | 'other';
    exercises?: Array<{
      type: 'listening_comprehension' | 'dictation' | 'pronunciation';
      question: string;
      timestamp?: number; // 相关音频时间点
      answer?: string;
    }>;
  };
}

// 联合类型
type MaterialContent = 
  | ForeignReadingContent 
  | GeneralMaterialContent 
  | VideoMaterialContent 
  | AudioMaterialContent;

// 预览内容结构（简化版，用于试读）
interface PreviewContent {
  type: string;
  version: string;
  content: any; // 简化的内容结构
  note: string; // 试读说明
  fullContentLength?: number; // 完整内容长度提示
}

// 示例数据

// 外刊精读示例
const foreignReadingExample: ForeignReadingContent = {
  type: 'foreign_reading',
  version: '1.0',
  source: 'The Economist',
  metadata: {
    difficulty: 'advanced',
    estimatedReadTime: 15,
    author: 'John Smith'
  },
  content: {
    title: {
      english: 'The Future of Renewable Energy',
      chinese: '可再生能源的未来'
    },
    paragraphs: [
      {
        id: 'p1',
        english: 'Renewable energy sources are rapidly becoming more cost-effective than traditional fossil fuels.',
        chinese: '可再生能源正在迅速变得比传统化石燃料更具成本效益。',
        analysis: {
          vocabulary: [
            {
              word: 'cost-effective',
              meaning: '性价比高的，成本效益好的',
              pronunciation: '/ˌkɒst ɪˈfektɪv/',
              usage: '形容词，用来描述投入产出比高的事物',
              examples: ['This method is more cost-effective than the previous one.'],
              synonyms: ['economical', 'efficient', 'profitable']
            }
          ],
          grammar: {
            points: [
              {
                structure: 'be becoming + adj.',
                explanation: '表示正在变得...',
                examples: ['The weather is becoming warmer.']
              }
            ]
          },
          background: '全球能源转型背景下，可再生能源技术不断进步，成本持续下降。'
        }
      }
    ],
    exercises: [
      {
        type: 'comprehension',
        question: 'What is the main trend mentioned in the paragraph?',
        options: [
          'Fossil fuels are becoming cheaper',
          'Renewable energy is becoming more cost-effective',
          'Energy consumption is decreasing',
          'Traditional energy is more popular'
        ],
        answer: 'Renewable energy is becoming more cost-effective',
        explanation: '段落明确提到可再生能源正在变得比传统化石燃料更具成本效益。'
      }
    ]
  }
};

// 通用素材示例
const generalMaterialExample: GeneralMaterialContent = {
  type: 'general_material',
  version: '1.0',
  metadata: {
    difficulty: 'intermediate',
    estimatedReadTime: 10
  },
  content: {
    sections: [
      {
        id: 'vocab',
        title: '环保核心词汇',
        items: [
          'sustainability - 可持续性',
          'carbon footprint - 碳足迹',
          'renewable energy - 可再生能源',
          'biodiversity - 生物多样性'
        ],
        examples: [
          {
            text: 'We need to focus on sustainability in our daily lives.',
            explanation: '我们需要在日常生活中关注可持续性。'
          }
        ]
      }
    ],
    templates: [
      {
        title: '环保议论文开头模板',
        content: 'In recent years, {TOPIC} has become a pressing concern that demands immediate attention from both individuals and governments.',
        usage: '用于环保主题的议论文开头',
        variables: ['TOPIC - 具体环保话题']
      }
    ]
  }
};

export type {
  MaterialContent,
  PreviewContent,
  ForeignReadingContent,
  GeneralMaterialContent,
  VideoMaterialContent,
  AudioMaterialContent
};
```