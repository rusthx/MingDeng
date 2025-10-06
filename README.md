# MingDeng (明灯) 🏮

> 在学习的黑暗中，为你照亮前路

一个开源的 AI 学习助手，帮助所有学习者战胜知识爆炸、遗忘和拖延。

---

## 项目愿景

**无论你是在学习编程、准备考研、学习英语，还是培养任何新技能，MingDeng 都能帮你：**
- 面对知识爆炸时不再迷茫
- 告别"第二天就忘了昨天的计划"
- 随时捕获学习灵感，不再遗忘
- 拥有一个真正"懂你"的 AI 学习伙伴

当用户因为 MingDeng 而坚持下来、学会了心仪的技能，那就是这个项目最大的成功 ✨

---

## 核心痛点与解决方案

### 痛点 1：知识爆炸，无从下手
**场景**：想学 Agentic RL，看到要学的东西一大堆（Python 异步、vLLM、SGLang、FSDP、LlamaFactory、DeepSpeed、Transformers、TRL、VeRL...），像无头苍蝇。

**MingDeng 的解决**：
- 你把要学的东西一次性告诉 MingDeng
- AI 自动分析依赖关系，拆解为每日小任务
- 自动排布未来 2-4 周的学习计划
- 第二天起，你只需要 `> today`，MingDeng 告诉你今天学什么

### 痛点 2：第二天就忘了昨天的计划
**MingDeng 的解决**：
- 计划一次性生成后，自动持久化
- 每天主动运行 `> today` 查看任务
- AI 记住你的学习历程，提供连贯的指导

### 痛点 3：碎片资源难管理（视频、博客、论文）
**场景**：看到一个讲 FSDP 的好视频，但现在在学别的，不知道存哪，会遗忘。

**MingDeng 的解决**：
- `> capture "资源链接 + 简短描述"`
- 自动存入「资源库」
- AI 自动关联到相关学习任务
- 到了学习该知识点的那天，MingDeng 会推荐给你

### 痛点 4：每日制定 TODO 太繁琐
**MingDeng 的解决**：
- 一次性规划，自动执行
- 无需每天手动制定计划

---

## 核心功能

### 1. 快速添加单个任务

**界面展示**：
- 顶部有「➕ 添加任务」按钮
- 点击后弹出输入框
- 支持自然语言输入（如"明天学习 Python 装饰器"）
- AI 自动解析时间和任务内容

**特点**：
- 所见即所得，直接在日历上看到新任务
- 支持快捷键（Ctrl+N）快速添加

### 2. 批量生成学习计划（核心！）

**界面展示**：
- 点击「📋 生成学习计划」按钮
- 在文本框中粘贴学习内容
- 选择学习模式（集中攻坚 / 交叉学习）
- AI 生成计划后展示预览
- 用户可以拖拽调整任务顺序和日期
- 确认后自动添加到日历

**功能演示**：
```
┌─────────────────────────────────────┐
│  📋 生成学习计划                     │
├─────────────────────────────────────┤
│  请输入你要学习的内容：              │
│  ┌───────────────────────────────┐  │
│  │ 我想学 Agentic RL，需要掌握： │  │
│  │ - Python 异步编程             │  │
│  │ - Inference (vLLM, SGLang)    │  │
│  │ - SFT (FSDP, LlamaFactory...) │  │
│  │ - RL (TRL, VeRL)              │  │
│  └───────────────────────────────┘  │
│                                      │
│  学习模式：                          │
│  ○ 🎯 集中攻坚  ● 🔄 交叉学习       │
│                                      │
│  ［生成计划］                        │
└─────────────────────────────────────┘

       ↓ AI 分析中...

┌─────────────────────────────────────┐
│  ✅ 学习计划生成完成                 │
├─────────────────────────────────────┤
│  共 18 个任务，预计 3 周完成         │
│                                      │
│  📅 第 1 周（基础建设）              │
│  ┌───────────────────────────────┐  │
│  │ 2025-10-08                    │  │
│  │ 🟡 学习 Python asyncio (1.5h) │  │
│  │ [拖动调整]                    │  │
│  ├───────────────────────────────┤  │
│  │ 2025-10-09                    │  │
│  │ 🔴 实践：异步爬虫 (2h)        │  │
│  └───────────────────────────────┘  │
│  ...                                 │
│                                      │
│  ［确认添加］ ［重新生成］          │
└─────────────────────────────────────┘
```

**AI 规划逻辑**：
- 分析依赖关系（基础知识优先）
- 拆解为具体可执行任务（15min-3h）
- 理论+实践交替
- 每日总时长控制在 2-4 小时
- 高难度任务分散，避免连续烧脑
- 根据选择的学习模式调整任务分布

**多计划管理**：
- 同时只能有一个**主计划**（如 Agentic RL）
- 可以添加**子计划**（如每日英语学习）
- 子计划会自动穿插到主计划中
- 在界面上用不同颜色标识主计划和子计划

**计划调整**：
- 拖拽任务到不同日期
- 批量延后/提前（选择计划 → 点击「调整时间」 → 输入天数）
- 修改任务难度（点击任务 → 选择难度等级）

### 2. 碎片资源捕获

```bash
# 快速保存
> capture "https://youtube.com/watch?v=xxx 讲 vLLM 原理的视频"
✅ 已保存到资源库！

# 或者纯文本
> capture "看到一个讲 FSDP 的好文章，改天要看"
✅ 已保存！

# 查看资源库
> library
📚 你的学习资源库：
  [未关联] https://youtube.com/xxx - vLLM 原理视频
  [已关联 → 学习 FSDP] 讲 FSDP 的好文章
  ...
```

**AI 自动关联逻辑**：
- 分析资源内容
- 匹配到相关学习任务
- 在执行任务时自动推荐

### 3. 每日任务查看

```bash
> today

📅 2025-10-10 星期四
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
今日任务：
[ ] 1. 🔴 阅读 vLLM 架构文档（1h）
    💡 推荐资源：你保存的 vLLM 原理视频

[ ] 2. 🟡 对比 Python 多线程 vs 异步（30min）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 输入 `done <id>` 完成任务
💬 输入 `skip <id>` 跳过任务（会自动重排）
💬 输入 `move <id> to <date>` 移动任务
```

**难度标记**：
- 🟢 简单：基础概念、简单练习
- 🟡 中等：需要思考和实践
- 🔴 困难：复杂概念、综合应用

### 4. AI 记忆对话

```bash
> chat "vLLM 和 SGLang 有什么区别？"

🤔 让我想想...
（检索你的学习历史）

根据你前几天学习的内容，vLLM 主要优势是...
而 SGLang 更适合...

考虑到你目前在学推理优化，我建议先深入 vLLM，因为...

💾 此对话已保存到学习日志
```

**记忆系统**：
- 存储所有对话和学习日志
- 基于历史上下文回答问题
- 提供个性化建议

### 5. 完成与跳过任务

```bash
# 完成任务
> done 1
✅ 已完成「阅读 vLLM 架构文档」

🤖 不错！继续保持。接下来建议：
   1. 💪 继续学习「部署 vLLM」（趁热打铁）
   2. 😌 休息 15 分钟，再继续
   
   输入数字选择，或按回车跳过

# 跳过任务（自动重排）
> skip 2
⏭️ 已跳过「对比多线程 vs 异步」
📅 已自动安排到明天

# 移动任务到指定日期
> move 2 to tomorrow
📅 已移动「对比多线程 vs 异步」到 2025-10-11

> move 3 to 2025-10-15
📅 已移动到 2025-10-15

# 修改任务难度
> edit 1 difficulty hard
✅ 已修改「阅读 vLLM 架构文档」难度为 🔴困难
```

**智能任务推荐**：
- 完成任务后，AI 会根据学习进度推荐下一步
- 可以选择立即继续，或休息一下
- 推荐是可选的，不会强制用户

### 6. 学习进度统计

**界面展示**：
- 顶部导航栏「📊 统计」入口
- 图表展示学习进度
- 按难度分类的任务分布
- AI 生成的学习总结

**功能演示**：
```
┌─────────────────────────────────────────────────────────┐
│  📊 学习统计                                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  本周进度（2025-10-06 ~ 2025-10-12）                    │
│  ┌────────────────────────────────────────────────┐    │
│  │  ✅ 已完成：8 个任务                            │    │
│  │     🔴 困难：██ 2 个                            │    │
│  │     🟡 中等：████ 4 个                          │    │
│  │     🟢 简单：██ 2 个                            │    │
│  │                                                 │    │
│  │  ⏳ 进行中：3 个任务                            │    │
│  │  📅 计划中：12 个任务                           │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  学习趋势（最近 4 周）                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │  任务完成数                                     │    │
│  │  12│              ●●                            │    │
│  │   9│         ●●  ●●                            │    │
│  │   6│    ●●   ●●  ●●   ●●                       │    │
│  │   3│●● ●●   ●●  ●●   ●●                       │    │
│  │   0└────────────────────────                   │    │
│  │     W1  W2  W3  W4                             │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  总体进度                                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  ✅ 累计完成：45 个任务                         │    │
│  │  🎯 完成率：73%（本周）                        │    │
│  │  📈 进度：██████████████░░░░░░ 60%             │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ［查看 AI 总结］                                       │
└─────────────────────────────────────────────────────────┘
```

**AI 智能总结**（点击按钮后展示）：
```
┌─────────────────────────────────────────────────────────┐
│  🤖 AI 学习总结                                          │
├─────────────────────────────────────────────────────────┤
│  基于你的学习记忆，MingDeng 为你生成总结：              │
│                                                          │
│  本周你在推理优化方面取得了不错的进展，完成了 vLLM 的  │
│  核心概念学习。注意到你在 FSDP 相关任务上花费较多时间， │
│  建议下周放慢节奏，增加实践环节。                        │
│                                                          │
│  你已经连续学习 5 天了，周末可以适当休息调整 💪          │
│                                                          │
│  💡 提示：总结每 24 小时更新一次                        │
│  ［导出学习报告］                                       │
└─────────────────────────────────────────────────────────┘
```

**特点**：
- 只统计完成的任务数，不追踪学习时长（保持简单）
- 按难度分类统计（简单/中等/困难）
- 可视化图表展示趋势
- AI 结合 Memory 生成个性化总结
- 总结缓存 24 小时，节省 API 调用

```bash
# 自动备份触发条件：
# - 批量生成计划
# - 批量删除/修改任务

# 回退到上一次备份
> undo
⚠️  将回退到：2025-10-08 14:30（批量生成 Agentic RL 计划）
   这会撤销之后的所有更改，是否继续？[Y/n]

# 查看当前有哪些备份
> backups
1. 2025-10-08 14:30 - 批量生成 Agentic RL 计划（18个任务）
2. 2025-10-06 09:00 - 初始化
```

**备份策略（防止文件过多）**：
- 只在重要操作前备份（批量生成、批量修改）
- 保留最近 10 个备份
- 超过 10 个时，自动删除最旧的

---

## 命令速查

```bash
# 核心命令
plan              批量生成学习计划
today             查看今日任务
done <id>         完成任务
skip <id>         跳过任务（自动重排）
capture "<内容>"  保存学习资源
library           查看资源库
chat "<问题>"     AI 对话

# 管理命令
undo              回退到上一次备份
backups           查看备份历史
config            配置管理

# 快捷命令
add "<任务>"      快速添加单个任务（不是批量生成）
log "<内容>"      记录学习日志
cal               查看日历（未来功能）
stats             查看统计（未来功能）
```

---

## 技术架构

### 技术栈

```
Runtime:  Python 3.9+
AI:       Mem0 (memory), OpenAI-compatible API (用户自行配置)
Storage:  JSON files (local)
UI:       Streamlit (Web 界面) → Electron (桌面应用，可选)
```

**开发策略**：
- 所有功能围绕 **GUI** 设计
- 后端提供干净的 API 接口
- 接口可同时服务 Streamlit Web 和未来的 Electron 桌面应用

**重要说明**：
- MingDeng 使用 **OpenAI 兼容格式的 API**
- 支持任何兼容 OpenAI API 格式的服务：
  - OpenAI 官方 API
  - 其他云端服务（如 DeepSeek、智谱、通义千问等）
  - 本地模型服务（如 Ollama、LM Studio、vLLM 本地部署）
- 用户需要自行提供：`base_url`、`model_name`、`api_key`
- MingDeng 不提供 API 服务，不收集用户的 API 信息

### 项目结构

```
mingdeng/
├── data/                    # 数据文件（不提交到 Git）
│   ├── config.json          # API 配置
│   ├── todos.json           # 任务数据
│   ├── library.json         # 资源库
│   ├── memory/              # Mem0 数据
│   └── backups/             # 版本备份（最多 10 个）
├── core/                    # 核心业务逻辑（提供接口给 GUI）
│   ├── __init__.py
│   ├── config.py            # 配置管理
│   ├── storage.py           # JSON 读写
│   ├── memory.py            # Mem0 封装
│   ├── ai.py                # LLM 调用（支持 streaming）
│   ├── todo_manager.py      # 任务逻辑 API
│   ├── library_manager.py   # 资源库 API
│   ├── plan_generator.py    # 批量生成学习计划 API
│   └── backup_manager.py    # 备份管理 API
├── pages/                   # Streamlit 页面
│   ├── home.py              # 首页（任务列表 + 日历）
│   ├── plan.py              # 批量生成学习计划
│   ├── library.py           # 资源库
│   ├── stats.py             # 统计与分析
│   └── config.py            # 配置管理
├── components/              # 可复用的 Streamlit 组件
│   ├── task_card.py         # 任务卡片
│   ├── chat_widget.py       # AI 对话窗口
│   └── calendar_view.py     # 日历视图
├── app.py                   # Streamlit 主入口
├── requirements.txt
├── .gitignore               # 忽略 data/ 目录
└── README.md
```

### 数据结构

#### config.json
```json
{
  "api": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-xxx",
    "model": "gpt-4"
  },
  "user": {
    "name": "用户名",
    "timezone": "Asia/Shanghai"
  }
}
```

**API 配置说明**：
- `base_url`：API 服务地址
  - OpenAI: `https://api.openai.com/v1`
  - 本地 Ollama: `http://localhost:11434/v1`
  - 其他服务：根据提供商文档填写
- `api_key`：你的 API 密钥（本地模型可能不需要）
- `model`：模型名称（如 `gpt-4`、`deepseek-chat`、`qwen-plus` 等）

#### todos.json
```json
{
  "plans": [
    {
      "id": "uuid",
      "name": "Agentic RL 学习计划",
      "created_at": "2025-10-08T14:30:00",
      "tasks": [
        {
          "id": "uuid",
          "task": "学习 Python asyncio 基础",
          "date": "2025-10-08",
          "estimated_time": 90,
          "difficulty": "simple|medium|hard",
          "priority": "high|medium|low",
          "tags": ["python", "async"],
          "status": "pending|completed|skipped",
          "completed_at": null,
          "notes": ""
        }
      ]
    }
  ]
}
```

#### library.json
```json
{
  "resources": [
    {
      "id": "uuid",
      "content": "https://youtube.com/xxx",
      "description": "vLLM 原理视频",
      "type": "video|article|paper|other",
      "captured_at": "2025-10-08T10:00:00",
      "linked_tasks": ["task_uuid"],
      "status": "unread|reading|completed"
    }
  ]
}
```

---

## 实现路线图

### Phase 1: Streamlit Web 界面

**后端核心 API**（为 GUI 提供服务）：
- [ ] 配置管理（config.py）
- [ ] JSON 存储层（storage.py）
- [ ] Mem0 记忆系统（memory.py）
- [ ] OpenAI 兼容 API 调用（ai.py，支持 streaming）
- [ ] 备份管理（backup_manager.py，最多 10 个）
- [ ] 任务管理 API（todo_manager.py）
- [ ] 资源库 API（library_manager.py）
- [ ] 学习计划生成 API（plan_generator.py）
  
**Streamlit 界面**：
- [ ] 首页（日历 + 任务列表，拖拽调整）
- [ ] 配置页面（API 设置）
- [ ] 计划生成页面（输入内容、选择模式、预览、编辑）
- [ ] 资源库页面（保存、列表、筛选）
- [ ] 统计页面（图表、AI 总结）
- [ ] 版本管理（备份列表、差异、回退）
- [ ] AI 对话组件（悬浮窗）
- [ ] 任务卡片组件
- [ ] 日历视图组件

**核心功能**：
- [ ] 快速添加任务
- [ ] 批量生成学习计划（AI 分析、拆解、排布）
- [ ] 学习模式选择（集中攻坚 / 交叉学习）
- [ ] 主计划 + 子计划
- [ ] 拖拽调整任务
- [ ] 修改任务难度
- [ ] 完成/跳过任务
- [ ] 智能任务推荐
- [ ] 资源保存与自动关联
- [ ] AI 记忆对话
- [ ] 学习进度统计
- [ ] 版本回退

### Phase 2: Electron 桌面应用（可选）

如果需要独立桌面应用，后端 API 可直接复用：
- [ ] Electron 封装
- [ ] 系统托盘、通知
- [ ] 快捷键

### TODO（未来可能的功能）

- [ ] 学习状态追踪
- [ ] 紧急任务插入
- [ ] 任务标签系统
- [ ] 资源评价
- [ ] 学习里程碑
- [ ] 笔记链接
- [ ] 时间段规划
- [ ] 失败友好设计
- [ ] 依赖任务
- [ ] 多语言

---

## 关键实现细节

### 1. 批量生成计划的 AI Prompt

```python
PLAN_GENERATION_PROMPT = """
你是 MingDeng 学习规划助手。用户想学习以下内容，请帮助拆解为可执行的学习计划。

用户输入：
{user_input}

要求：
1. 分析依赖关系：识别哪些是基础知识，必须先学
2. 拆解为具体任务：每个任务 15min-3h，可操作
3. 评估难度和时长：简单/中等/困难
4. 智能排布时间：
   - 基础任务优先
   - 理论+实践交替
   - 每日总时长 2-4 小时
   - 高难度任务分散
5. 建议 2-4 周完成

输出 JSON 格式：
{{
  "plan_name": "学习计划名称",
  "total_weeks": 3,
  "tasks": [
    {{
      "task": "任务描述（具体可执行）",
      "date": "2025-10-08",
      "estimated_time": 90,
      "difficulty": "simple|medium|hard",
      "tags": ["标签"],
      "prerequisites": ["前置任务ID（如果有）"]
    }}
  ]
}}

只返回 JSON，不要其他文字。
"""
```

### 2. 资源自动关联逻辑

```python
AUTO_LINK_PROMPT = """
用户保存了以下学习资源：
{resource_content}

当前学习计划中的任务：
{tasks_list}

请判断这个资源最适合关联到哪个任务（如果有）。

输出 JSON：
{{
  "linked_task_id": "uuid 或 null",
  "reason": "关联理由"
}}
"""
```

### 3. 备份管理逻辑

```python
class BackupManager:
    MAX_BACKUPS = 10  # 最多保留 10 个备份
    
    def create_backup(self, reason: str):
        """创建备份，超过 10 个时删除最旧的"""
        backup_file = f"backups/todos_{timestamp}.json"
        # 保存备份
        # 如果备份数 > 10，删除最旧的
        
    def list_backups(self):
        """列出所有备份"""
        
    def restore_backup(self, backup_id: int):
        """恢复到指定备份"""
```

---

## 性能目标

- 批量生成计划（10-20 个任务）：< 10 秒
- AI 对话响应（streaming）：首字 < 1 秒
- `today` 命令加载：< 0.5 秒
- 资源自动关联：< 2 秒

---

## 安全与隐私

- ✅ 所有数据本地存储（`data/` 目录）
- ✅ API 配置存在 `config.json`（已加入 `.gitignore`）
- ✅ MingDeng 不提供 API 服务，用户需自行配置
- ✅ MingDeng 不收集、不上传用户的 API 信息和学习数据
- ✅ Mem0 数据可选本地或云端
- ✅ 支持数据导出（JSON 格式）

---

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/your-org/mingdeng.git
cd mingdeng

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动 Streamlit 界面
streamlit run app.py

# 浏览器自动打开 http://localhost:8501

# 4. 首次配置
在界面上点击「⚙️ 配置」：
- 选择 API 提供商（OpenAI / Ollama / 其他）
- 输入 API Key 和模型名称
- 输入你的名字
- 点击「保存配置」

# 5. 开始使用
- 点击「📋 生成学习计划」创建你的第一个学习计划
- 或点击「➕ 添加任务」快速添加单个任务
- 在日历上查看和管理你的学习任务
```

---

## 开发者指南

### 给 Claude Code 的实现指引

**核心设计理念**：
- 所有功能围绕 **GUI** 设计
- 后端提供干净的 API 接口（函数）
- 接口可同时服务 Web 和未来的桌面应用

**实现顺序**：
1. **后端 API**：config.py → storage.py → backup_manager.py → ai.py → memory.py → todo_manager.py → library_manager.py → plan_generator.py
2. **Streamlit GUI**：app.py（主入口）→ pages/（各页面）→ components/（组件）

**关键技术点**：
- 后端函数设计要干净，方便 GUI 调用
- 使用 st.session_state 管理界面状态
- 拖拽功能可使用 streamlit-aggrid
- AI 对话支持 streaming（打字机效果）
- 备份自动清理（保留最近 10 个）
- 所有 API 配置支持 OpenAI 兼容格式

**数据结构设计见下方 JSON Schema**

### 代码规范

- **变量命名**：简洁但清晰（如 `task_id`, `backup_file`）
- **函数**：单一职责，易测试
- **错误处理**：友好的用户提示，避免程序崩溃
- **注释**：关键逻辑必须注释，复杂算法需详细说明
- **日志**：重要操作（生成计划、备份、恢复）需记录日志

### 依赖项

```txt
# requirements.txt

# 核心依赖
streamlit>=1.28.0          # Web 界面框架
mem0ai>=0.1.0              # 记忆系统
openai>=1.0.0              # OpenAI 兼容 API 客户端
python-dateutil>=2.8.0     # 日期处理

# UI 增强
streamlit-aggrid>=0.3.0    # 表格组件（支持拖拽）
plotly>=5.0.0              # 可视化图表
pandas>=2.0.0              # 数据处理

# 工具库
pydantic>=2.0.0            # 数据验证
```

---

## 贡献指南

MingDeng 是一个纯公益项目，我们欢迎任何形式的贡献：
- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 💻 提交代码

**贡献前请阅读**：我们的目标是让用户用着开心、方便，所有设计决策都应以用户体验为先。

### 提交 Issue

报告 Bug 时，请提供：
1. 操作系统和 Python 版本
2. 复现步骤
3. 期望行为 vs 实际行为
4. 相关日志或截图

### 提交 Pull Request

1. Fork 项目
2. 创建特性分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 开启 Pull Request

---

## FAQ

### Q: MingDeng 支持哪些 AI 服务？
A: 支持所有 OpenAI 兼容格式的 API，包括：
- **云端服务**：OpenAI、Claude（通过代理）、DeepSeek、智谱 GLM、通义千问、Kimi 等
- **本地模型**：Ollama、LM Studio、vLLM 本地部署等
- 只要支持 OpenAI API 格式，都可以使用

### Q: MingDeng 收费吗？需要订阅吗？
A: MingDeng 完全免费开源，不收费、无订阅。但你需要自己准备 AI API（可以用免费的本地模型，也可以购买云端 API）。

### Q: 我的 API Key 安全吗？
A: 你的 API Key 只存储在本地的 `config.json` 文件中，MingDeng 不会上传或收集任何用户信息。

### Q: 数据存储在哪里？
A: 所有数据本地存储在 `data/` 目录，不会上传到任何服务器（除非你选择 Mem0 云端存储）。

### Q: 可以使用免费的本地模型吗？
A: 可以！推荐使用 Ollama + Qwen 或 Llama 等开源模型，完全免费。配置示例：
```json
{
  "api": {
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
    "model": "qwen2.5:7b"
  }
}
```

### Q: 如何备份我的学习数据？
A: 直接复制 `data/` 目录即可。我们也提供了内置的版本回退功能。

### Q: 可以导出学习报告吗？
A: Phase 2 会支持导出功能，可以生成 Markdown 格式的学习报告。

---

## 路线图

- [x] 项目初始化
- [ ] MVP 核心功能（Phase 1）
- [ ] 体验优化（Phase 2）
- [ ] GUI 界面（Phase 3）
- [ ] 移动端支持
- [ ] 多语言支持

---

## 许可证

MIT License - 完全开源，自由使用

```
MIT License

Copyright (c) 2025 MingDeng Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 致谢

感谢所有为 MingDeng 做出贡献的开发者和用户！

特别感谢：
- Mem0 团队提供优秀的记忆系统
- OpenAI 提供强大的 LLM API
- 所有提供反馈和建议的用户

---

## 联系我们

- **GitHub Issues**: [提交问题](https://github.com/your-org/mingdeng/issues)
- **讨论区**: [参与讨论](https://github.com/your-org/mingdeng/discussions)
- **邮件**: mingdeng@example.com

---

**愿 MingDeng 成为你学习路上的一盏明灯 🏮**

当你因为 MingDeng 而坚持下来、学会了心仪的技能，请回来告诉我们你的故事！

---

*最后更新：2025-10-07*  
*文档版本：1.0.0*