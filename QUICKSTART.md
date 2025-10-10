# MingDeng 快速开始指南 🚀

## 系统要求

- Python 3.9 或更高版本
- Rust 1.70 或更高版本（用于 Tauri）
- Node.js 16 或更高版本（用于 npm 脚本）

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/your-org/mingdeng.git
cd mingdeng
```

### 2. 安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
cd ..
```

或使用虚拟环境（推荐）：

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
cd backend
pip install -r requirements.txt
cd ..
```

### 3. 安装 Tauri CLI

```bash
npm install
```

或全局安装：

```bash
cargo install tauri-cli
```

### 4. 首次运行

开发模式：

```bash
npm run dev
```

或手动启动：

```bash
# 终端 1: 启动 Python 后端
npm run backend

# 终端 2: 启动 Tauri 应用
npm run tauri dev
```

## 首次配置

1. 启动应用后，点击左侧导航栏的「⚙️ 设置」
2. 在「API 配置」部分填写：
   - **API Base URL**: 你的 AI 服务 URL（例如：`https://api.openai.com/v1`）
   - **API Key**: 你的 API 密钥
   - **模型名称**: 模型名称（例如：`gpt-4`, `deepseek-chat`）
3. 点击「保存 API 配置」

### 支持的 AI 服务

MingDeng 支持任何 OpenAI 兼容格式的 API：

#### 云端服务

- **OpenAI**: `https://api.openai.com/v1`
- **DeepSeek**: `https://api.deepseek.com`
- **智谱 GLM**: `https://open.bigmodel.cn/api/paas/v4/`
- **通义千问**: 参考阿里云文档
- **其他兼容 OpenAI API 的服务**

#### 本地模型（免费）

使用 Ollama 运行本地模型：

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型（例如 Qwen）
ollama pull qwen2.5:7b

# 启动 Ollama 服务
ollama serve
```

在 MingDeng 设置中配置：
- **API Base URL**: `http://localhost:11434/v1`
- **API Key**: `ollama`（任意值）
- **模型名称**: `qwen2.5:7b`

## 使用指南

### 生成学习计划

1. 点击「📋 生成计划」
2. 在文本框中描述你的学习目标，例如：

```
我想学习 Python 数据分析，需要掌握：
- NumPy 和 Pandas 基础
- 数据可视化（Matplotlib, Seaborn）
- 数据清洗和预处理
- 简单的统计分析

我每天可以学习 2-3 小时，希望在 3 周内入门。
```

3. 选择开始日期
4. 点击「🤖 生成计划」
5. 预览生成的计划后，点击「✓ 保存计划」

### 查看今日任务

1. 点击「📅 今日任务」
2. 查看今天的学习任务
3. 完成任务后，勾选复选框
4. 点击「🗑️」可以删除任务

### 使用 AI 助手

1. 点击右下角的「💬」按钮打开聊天窗口
2. 输入问题，例如：
   - "如何学习 Python 异步编程？"
   - "vLLM 和 SGLang 有什么区别？"
   - "我应该先学哪个？"
3. AI 会根据你的学习历史提供个性化建议

### 保存学习资源

1. 点击「📚 资源库」
2. 输入资源链接（例如：YouTube 视频、博客文章）
3. 添加简短描述
4. 选择资源类型
5. 点击「➕ 添加资源」
6. AI 会自动将资源关联到相关任务

### 查看学习统计

1. 点击「📊 学习统计」
2. 查看你的：
   - 总任务数
   - 已完成任务数
   - 完成率
   - 按难度分类的完成情况

## 数据备份

### 自动备份

MingDeng 会在以下情况自动创建备份：
- 恢复备份前
- 最多保留 10 个备份

### 手动备份

1. 点击「⚙️ 设置」
2. 在「数据管理」部分点击「💾 创建备份」
3. 或点击左侧底部的「💾 创建备份」按钮

### 查看和恢复备份

1. 点击「⚙️ 设置」
2. 点击「📦 查看备份列表」
3. 选择要恢复的备份

## 常见问题

### Q: 启动后提示 "API request failed"

**A**: 请检查：
1. Python 后端是否正常运行（访问 http://127.0.0.1:8765）
2. API 配置是否正确（设置页面）
3. API Key 是否有效

### Q: 本地模型可以使用吗？

**A**: 可以！推荐使用 Ollama 运行本地模型，完全免费且隐私安全。参考上面的「本地模型」配置说明。

### Q: 我的数据存储在哪里？

**A**: 所有数据存储在项目根目录的 `data/` 文件夹：
- `data/config.json` - 配置文件（包含 API Key）
- `data/todos.json` - 学习计划和任务
- `data/library.json` - 资源库
- `data/backups/` - 备份文件
- `data/memory/` - AI 记忆数据（Mem0）

### Q: 如何更换 AI 模型？

**A**: 在设置页面修改「模型名称」即可，支持随时切换。

### Q: Mem0 是必需的吗？

**A**: 不是必需的。如果未安装 mem0ai，MingDeng 仍然可以正常工作，但 AI 不会记住你的学习历史。

安装 Mem0：

```bash
pip install mem0ai
```

## 开发指南

### 项目结构

```
mingdeng/
├── backend/              # Python FastAPI 后端
│   ├── core/            # 核心模块
│   ├── main.py          # API 入口
│   └── requirements.txt
├── src/                 # 前端
│   ├── pages/          # 页面 HTML
│   ├── index.html      # 主页面
│   ├── main.js         # JavaScript
│   └── style.css       # 样式
├── src-tauri/          # Tauri Rust
│   ├── src/
│   │   └── main.rs
│   └── Cargo.toml
└── data/               # 数据文件（不提交）
```

### 开发模式运行

```bash
# 方式 1: 使用 Tauri（推荐）
npm run dev

# 方式 2: 分别启动
npm run backend          # 终端 1
npm run tauri dev        # 终端 2
```

### 构建生产版本

```bash
npm run build
```

构建产物位于 `src-tauri/target/release/`

## 技术栈

- **桌面应用**: Tauri 2.0（Rust）
- **前端**: HTML/CSS/JS + Tailwind CSS
- **后端**: Python FastAPI
- **AI**: OpenAI-compatible API
- **记忆**: Mem0 (可选)
- **存储**: JSON 本地文件

## 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 许可证

MIT License - 完全开源，自由使用

---

**愿 MingDeng 成为你学习路上的一盏明灯 🏮**
