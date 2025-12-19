# MingDeng (明灯) 🏮

> 在学习的黑暗中，为你照亮前路

一个开源的 AI 学习助手，帮助所有学习者战胜知识爆炸、遗忘和拖延。

------

## 快速开始（按平台选择命令）

- Web 开发（macOS/Linux）：`./run_dev.sh`（一键启动后端 + 前端 http://localhost:8000）
- Web 开发（Windows）：`run_dev.bat`
- 桌面版（macOS/Linux 打包）：`./build_desktop.sh`（生成安装包，位于 src-tauri/target/release/bundle/）
- 桌面版（Windows 打包）：`build_desktop.bat`

----

## 项目愿景

**无论你是在学习编程、准备考研、学习英语，还是培养任何新技能，MingDeng 都能帮你：**

- 面对知识爆炸时不再迷茫
- 告别"第二天就忘了昨天的计划"
- 随时捕获学习灵感，不再遗忘
- 拥有一个真正"懂你"的 AI 学习伙伴

当用户因为 MingDeng 而坚持下来、学会了心仪的技能，那就是这个项目最大的成功 ✨

------

## 核心痛点与解决方案

### 痛点 1：知识爆炸，无从下手

**场景**：想学 Agentic RL，看到要学的东西一大堆（Python 异步、vLLM、SGLang、FSDP、LlamaFactory、DeepSpeed、Transformers、TRL、VeRL...），像无头苍蝇。

**MingDeng 的解决**：

- 你把要学的东西一次性告诉 MingDeng
- AI 自动分析依赖关系，拆解为每日小任务
- 自动排布未来 2-4 周的学习计划
- 第二天起，你只需打开应用，MingDeng 告诉你今天学什么

### 痛点 2：第二天就忘了昨天的计划

**MingDeng 的解决**：

- 计划一次性生成后，自动持久化
- 每天打开应用，直接看到今日任务
- **AI 记住你的学习历程，提供连贯的指导（核心！）**

### 痛点 3：碎片资源难管理（视频、博客、论文）

**场景**：看到一个讲 FSDP 的好视频，但现在在学别的，不知道存哪，会遗忘。

**MingDeng 的解决**：

- 快速保存资源链接
- 自动存入「资源库」
- AI 自动关联到相关学习任务
- 到了学习该知识点的那天，MingDeng 会推荐给你

### 痛点 4：每日制定 TODO 太繁琐

**MingDeng 的解决**：

- 一次性规划，自动执行
- 无需每天手动制定计划

------

## 核心功能

### 1. 批量生成学习计划（核心！）

**交互流程**：

1. 点击「生成学习计划」按钮
2. 在文本框中粘贴学习内容
3. AI 分析并生成计划预览
4. 拖拽调整任务顺序和日期
5. 确认后自动添加到日历

**AI 规划逻辑**：

- 分析依赖关系（基础知识优先）
- 拆解为具体可执行任务（15min-3h）
- 理论+实践交替
- 每日总时长控制在 2-4 小时
- 高难度任务分散，避免连续烧脑

### 2. 今日任务查看

**界面展示**：

```
📅 2025-10-10 星期四

□  学习 Python asyncio 基础          🟡 1.5h
   💡 推荐资源：你保存的 asyncio 视频

□  实践：异步爬虫项目                🔴 2h

✓  复习 Python 装饰器                🟢 30m
```

**难度标记**：

- 🟢 简单：基础概念、简单练习
- 🟡 中等：需要思考和实践
- 🔴 困难：复杂概念、综合应用

**操作**：

- 点击复选框完成任务
- 右键菜单：编辑、删除、移动、跳过
- 快捷键：Space 完成/取消，Ctrl+E 编辑

### 2.5. AI 智能重新排序（新功能！🆕）

**核心特性**：

- **自适应调整**：AI 根据你的学习速度和完成率，智能调整任务安排
- **记忆驱动**：利用 Mem0 记忆系统，了解你的学习习惯和节奏
- **两种重排模式**：
  - 📅 **从今天开始重排**：重新安排今天及之后的所有未完成任务
  - 🔁 **包含过期任务重排**：将所有未完成任务（包括过期的）重新规划

**智能调整逻辑**：

- 如果完成率 > 80%：AI 会适当增加任务密度或难度，帮你加快进度
- 如果完成率 < 50%：AI 会降低难度、延长时间，给予更多缓冲
- 保持任务依赖关系和学习顺序
- 合理分散高难度任务，避免连续烧脑

**使用方法**：

1. 在日历页面点击「🔄 AI重新排序」按钮
2. 选择重排模式：
   - 从今天开始重排（适合计划延误不多的情况）
   - 包含过期任务重排（适合有较多积压任务的情况）
3. AI 分析你的学习统计和历史记录
4. 自动重新安排任务日期和时间分配
5. 查看 AI 的调整建议和原因

**示例场景**：

```
情况1：你最近完成率90%，学习状态很好
→ AI：「检测到你的学习进度很棒！已适当增加任务密度，帮你更快达成目标。」

情况2：你最近完成率35%，可能任务太重
→ AI：「注意到你最近任务完成有些困难，已降低每日任务量，给你更多时间巩固。」

情况3：有5个任务过期了
→ AI：「已将5个过期任务与未来任务重新规划，优先安排基础任务，确保学习连贯性。」
```

### 3. AI 记忆对话（核心！）

**记忆系统的重要性**：

- 学习是累积的过程，AI 需要记住你的学习历程
- 记住你卡在哪个知识点
- 记住你更擅长哪种学习方式
- 提供个性化的建议和指导

**示例**：

```
你：vLLM 和 SGLang 有什么区别？

AI：根据你前几天学习的内容，vLLM 主要优势是...
    而 SGLang 更适合...
    考虑到你目前在学推理优化，我建议先深入 vLLM，因为...
```

**实现**：使用 Mem0 存储所有对话和学习日志，基于历史上下文回答问题。

### 4. 碎片资源捕获

**快速保存**：

- 输入资源链接或文本描述
- AI 自动分析内容
- 自动关联到相关学习任务
- 在执行任务时自动推荐

### 5. 学习进度统计

**展示内容**：

- 按难度分类的任务完成数（简单/中等/困难）
- 学习趋势图表（最近 4 周）
- AI 结合 Memory 生成个性化总结

**特点**：

- 只统计完成的任务数，不追踪学习时长
- AI 总结缓存 24 小时，节省 API 调用

------

## 技术架构

### 技术栈

```
Desktop:  Tauri 2.0（极轻量，< 5MB）
Frontend: HTML/CSS/JS + Tailwind CSS（原生，无框架）
Backend:  Python 3.9+ FastAPI（本地 HTTP 服务）
AI:       Mem0 (memory), OpenAI-compatible API
Storage:  JSON files (local)
```

**架构图**：

```
┌─────────────────────────────────┐
│   Tauri 桌面应用                 │
├─────────────────────────────────┤
│  前端（HTML/CSS/JS）             │
│   - 任务列表                     │
│   - 日历视图                     │
│   - AI 对话窗口                  │
│   - 配置界面                     │
├─────────────────────────────────┤
│  Tauri Commands (Rust)          │
│   ↓ HTTP 调用                    │
│  Python FastAPI 后端             │
│   - core/ 模块                   │
│   - Mem0 记忆                    │
│   - OpenAI API                   │
└─────────────────────────────────┘
```

**设计原则**：

- **极轻量**：安装包 < 5MB，内存占用 < 50MB
- **极简 UI**：少即是多，每个页面只做一件事
- **快速响应**：所有操作 < 100ms 反馈
- **键盘优先**：所有功能都有快捷键

### 如何使用（Web 与桌面）

- **Web 开发模式**：`cd backend && pip install -r requirements.txt`，`cd .. && npm install`；启动后端 `npm run backend`；启动前端 `cd src && python3 -m http.server 8000`，浏览器访问 `http://localhost:8000`。可用 `run_dev.sh` / `run_dev.bat` 一键拉起。
- **桌面调试（Tauri Dev）**：仓库根运行 `npm run tauri dev`，Tauri 会自动起本地静态服并启动 Python 后端。
- **桌面打包**：macOS/Linux 执行 `./build_desktop.sh`，Windows 运行 `build_desktop.bat`；产物位于 `src-tauri/target/release/bundle/`，双击安装/运行，无需手动启动后端。

### 桌面版运行时的后端和数据

- 后端何时启动：每次打开桌面应用时自动拉起内置的 Python 后端，关闭窗口后后端随即退出，不会后台常驻。
- 内置 Python 环境：打包时会把项目根的 `backend-venv/` 一起放进安装包，运行时优先使用它（如设置了 `MINGDENG_PYTHON` 则用你指定的解释器）。
- 数据存储位置：桌面版会把 `config.json`、`todos.json`、`library.json`、备份、记忆等文件写到系统的应用数据目录，而不是源码目录。
  - macOS: `~/Library/Application Support/com.mingdeng`
  - Windows: `%AppData%\\com.mingdeng`
  - Linux: `~/.local/share/com.mingdeng`

### 项目结构

```
mingdeng/
├── src-tauri/              # Tauri Rust 后端
│   ├── src/
│   │   ├── main.rs         # Tauri 主入口
│   │   └── commands.rs     # 调用 Python API 的桥接
│   ├── tauri.conf.json     # Tauri 配置
│   └── Cargo.toml
│
├── src/                    # 前端（极简）
│   ├── index.html          # 主页面
│   ├── style.css           # Tailwind CSS
│   ├── main.js             # 核心逻辑
│   ├── pages/
│   │   ├── today.html      # 今日任务
│   │   ├── plan.html       # 生成计划
│   │   └── stats.html      # 统计
│   └── components/
│       ├── task-card.js    # 任务卡片组件
│       └── chat-widget.js  # AI 对话组件
│
├── backend/                # Python 后端
│   ├── main.py             # FastAPI 主入口
│   ├── core/
│   │   ├── config.py       # 配置管理
│   │   ├── storage.py      # JSON 读写
│   │   ├── memory.py       # Mem0 封装
│   │   ├── ai.py           # LLM 调用（支持 streaming）
│   │   ├── todo_manager.py # 任务逻辑 API
│   │   ├── library_manager.py  # 资源库 API
│   │   ├── plan_generator.py   # 批量生成学习计划 API
│   │   └── backup_manager.py   # 备份管理 API
│   └── requirements.txt
│
├── data/                   # 数据文件（不提交到 Git）
│   ├── config.json         # API 配置
│   ├── todos.json          # 任务数据
│   ├── library.json        # 资源库
│   ├── memory/             # Mem0 数据
│   └── backups/            # 版本备份（最多 10 个）
│
├── .gitignore
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

**重要说明**：

- MingDeng 使用 **OpenAI 兼容格式的 API**
- 支持任何兼容 OpenAI API 格式的服务（OpenAI、本地 Ollama、其他云端服务）
- 用户需要自行提供：`base_url`、`model_name`、`api_key`
- MingDeng 不提供 API 服务，不收集用户的 API 信息

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

------

## 功能清单

### 核心模块

**后端 API**（Python FastAPI）：

- [ ] `backend/core/config.py`：配置管理
- [ ] `backend/core/storage.py`：JSON 存储层
- [ ] `backend/core/ai.py`：OpenAI 兼容 API 调用（支持 streaming）
- [ ] `backend/core/memory.py`：Mem0 记忆系统集成
- [ ] `backend/core/todo_manager.py`：任务 CRUD API
- [ ] `backend/core/plan_generator.py`：AI 生成学习计划
- [ ] `backend/core/library_manager.py`：资源库管理
- [ ] `backend/core/backup_manager.py`：备份管理（最多 10 个）
- [ ] `backend/main.py`：FastAPI 路由

**前端界面**（HTML/CSS/JS）：

- [ ] `src/index.html`：主页面框架
- [ ] `src/style.css`：Tailwind CSS 样式
- [ ] `src/main.js`：核心 JS 逻辑
- [ ] `src/pages/today.html`：今日任务页面
- [ ] `src/pages/plan.html`：生成计划页面
- [ ] `src/pages/stats.html`：统计页面
- [ ] `src/components/task-card.js`：任务卡片组件
- [ ] `src/components/chat-widget.js`：AI 对话悬浮窗

**Tauri 桌面应用**（Rust）：

- [ ] `src-tauri/src/main.rs`：Tauri 主入口
- [ ] `src-tauri/src/commands.rs`：Rust Commands（调用 Python API）
- [ ] 启动时自动启动 Python 后端
- [ ] 系统托盘图标
- [ ] 窗口管理（最小化到托盘）

**功能特性**：

- [ ] 拖拽调整任务
- [ ] AI streaming 响应（打字机效果）
- [ ] 快捷键系统（Ctrl+N, Ctrl+P, Ctrl+K, Ctrl+,, Space）
- [ ] 加载状态与错误处理
- [ ] 数据备份与恢复
- [ ] 设置页面（API 配置、外观切换）

### API 端点设计

```
POST   /api/config          # 保存配置
GET    /api/config          # 读取配置
GET    /api/today           # 获取今日任务
POST   /api/tasks           # 创建任务
PUT    /api/tasks/{id}      # 更新任务
DELETE /api/tasks/{id}      # 删除任务
POST   /api/plan/generate   # 批量生成学习计划
POST   /api/plan/reschedule # AI 智能重新排序任务（新增！🆕）
POST   /api/chat            # AI 对话（支持 streaming）
POST   /api/resources       # 保存资源
GET    /api/resources       # 获取资源列表
GET    /api/stats           # 获取统计数据
POST   /api/backup          # 创建备份
GET    /api/backups         # 列出备份
POST   /api/restore/{id}    # 恢复备份
```

------

## 关键实现细节

### 1. Tauri 调用 Python 的方式

**方案**：Python FastAPI 作为本地 HTTP 服务

```rust
// src-tauri/src/commands.rs
use reqwest;

#[tauri::command]
async fn get_today_tasks() -> Result<String, String> {
    let response = reqwest::get("http://localhost:8765/api/today")
        .await
        .map_err(|e| e.to_string())?;
    
    response.text().await.map_err(|e| e.to_string())
}

#[tauri::command]
async fn create_task(task: String) -> Result<String, String> {
    let client = reqwest::Client::new();
    let response = client
        .post("http://localhost:8765/api/tasks")
        .json(&task)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    response.text().await.map_err(|e| e.to_string())
}
```

**Python 后端启动**：

```rust
// src-tauri/src/main.rs
use std::process::Command;

fn main() {
    // 启动 Python FastAPI 后端
    let _backend = Command::new("python")
        .args(&["backend/main.py"])
        .spawn()
        .expect("Failed to start Python backend");

    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_today_tasks,
            create_task,
            // ... 其他命令
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 2. 批量生成计划的 AI Prompt

```python
PLAN_GENERATION_PROMPT = """
你是 MingDeng 学习规划助手。用户想学习以下内容，请帮助拆解为可执行的学习计划。

用户输入：
{user_input}

要求：
1. 分析依赖关系：识别哪些是基础知识，必须先学
2. 拆解为具体任务：每个任务 15min-3h，可操作
3. 评估难度和时长：simple/medium/hard
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
      "tags": ["标签"]
    }}
  ]
}}

只返回 JSON，不要其他文字。
"""
```

### 3. 资源自动关联逻辑

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

### 4. 备份管理逻辑

```python
class BackupManager:
    MAX_BACKUPS = 10  # 最多保留 10 个备份
    
    def create_backup(self, reason: str):
        """创建备份，超过 10 个时删除最旧的"""
        backup_file = f"backups/todos_{timestamp}.json"
        # 保存备份
        # 如果备份数 > 10，删除最旧的
```

### 5. AI 对话 Streaming

```python
# backend/core/ai.py
async def chat_stream(prompt: str, memory_context: str):
    """流式返回 AI 回复"""
    messages = [
        {"role": "system", "content": memory_context},
        {"role": "user", "content": prompt}
    ]
    
    async for chunk in client.chat.completions.create(
        model=config.model,
        messages=messages,
        stream=True
    ):
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
// src/components/chat-widget.js
async function sendMessage(message) {
    const response = await fetch('http://localhost:8765/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message})
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        appendToChatWindow(chunk);  // 打字机效果
    }
}
```

------

## 性能目标

- 应用启动时间：< 2 秒
- 批量生成计划（10-20 个任务）：< 10 秒
- AI 对话响应（streaming）：首字 < 1 秒
- 任务列表加载：< 0.5 秒
- 内存占用：< 50MB
- 安装包体积：< 5MB

------

## 安全与隐私

- ✅ 所有数据本地存储（`data/` 目录）
- ✅ API 配置存在 `config.json`（已加入 `.gitignore`）
- ✅ MingDeng 不提供 API 服务，用户需自行配置
- ✅ MingDeng 不收集、不上传用户的 API 信息和学习数据
- ✅ Mem0 数据可选本地或云端
- ✅ 支持数据导出（JSON 格式）

------

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/your-org/mingdeng.git
cd mingdeng

# 2. 安装 Python 依赖
cd backend
pip install -r requirements.txt

# 3. 安装 Tauri 依赖
cd ../src-tauri
cargo build

# 4. 开发模式运行
npm run tauri dev

# 5. 首次配置
在界面上点击「⚙️ 设置」：
- 输入 API Base URL、API Key、模型名称
- 输入你的名字
- 点击「保存配置」

# 6. 开始使用
- 点击「生成学习计划」创建你的第一个学习计划
- 或快速添加单个任务
- 在日历上查看和管理你的学习任务
```

------

## 依赖项

```txt
# backend/requirements.txt
fastapi>=0.104.0
uvicorn>=0.24.0
mem0ai>=0.1.0
openai>=1.0.0
python-dateutil>=2.8.0
pydantic>=2.0.0
# src-tauri/Cargo.toml
[dependencies]
tauri = "2.0"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
reqwest = { version = "0.11", features = ["json"] }
```

------

## FAQ

### Q: 为什么选择 Tauri 而不是 Electron？

A: Tauri 的安装包体积 < 5MB（Electron 通常 > 150MB），内存占用 < 50MB（Electron 常 > 200MB），更符合"极轻量"的目标。

### Q: MingDeng 支持哪些 AI 服务？

A: 支持所有 OpenAI 兼容格式的 API，包括：

- **云端服务**：OpenAI、DeepSeek、智谱 GLM、通义千问等
- **本地模型**：Ollama、LM Studio、vLLM 本地部署等

### Q: 我的 API Key 安全吗？

A: 你的 API Key 只存储在本地的 `config.json` 文件中，MingDeng 不会上传或收集任何用户信息。

### Q: 数据存储在哪里？

A: 所有数据本地存储在 `data/` 目录，不会上传到任何服务器。

### Q: 可以使用免费的本地模型吗？

A: 可以！推荐使用 Ollama + Qwen 或 Llama 等开源模型，完全免费。

------

## 许可证

MIT License - 完全开源，自由使用

------

**愿 MingDeng 成为你学习路上的一盏明灯 🏮**
