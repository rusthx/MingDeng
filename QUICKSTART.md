# MingDeng 快速开始指南

## 安装步骤

### 1. 克隆项目

```bash
cd /path/to/MingDeng
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
cd mingdeng
pip install -r requirements.txt
```

### 4. 启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

## 首次配置

### 1. 配置 API

**重要说明**: MingDeng 使用 **OpenAI API 规范**，支持任何兼容此规范的服务（不限于 OpenAI 官方）。

启动后，点击左侧「⚙️ 配置」：

#### 选项 A: 使用 OpenAI 官方服务
- API 基础 URL: `https://api.openai.com/v1`
- API 密钥: 你的 OpenAI API Key
- 模型名称: `gpt-4o`、`gpt-4o-mini` 等

#### 选项 B: 使用本地模型（Ollama，完全免费）
1. 先安装 Ollama: https://ollama.com/
2. 下载模型: `ollama pull qwen2.5:7b`
3. 在 MingDeng 中配置:
   - API 基础 URL: `http://localhost:11434/v1`
   - API 密钥: `ollama` (任意非空值即可)
   - 模型名称: `qwen2.5:7b`

#### 选项 C: 使用其他兼容 OpenAI API 规范的服务
- **DeepSeek**: `https://api.deepseek.com/v1`，模型: `deepseek-chat`
- **智谱 AI**: `https://open.bigmodel.cn/api/paas/v4/`，模型: `glm-4`
- **通义千问**: 参考官方文档配置
- **Moonshot (Kimi)**: `https://api.moonshot.cn/v1`，模型: `moonshot-v1-8k`
- **本地部署**: vLLM、LM Studio、text-generation-webui 等
- 任何提供 OpenAI API 规范接口的服务

### 2. 测试连接

点击「🧪 测试连接」确保配置正确

### 3. 保存配置

点击「💾 保存配置」

## 开始使用

### 1. 生成学习计划

1. 点击「📋 生成计划」
2. 输入你要学习的内容，例如:
   ```
   我想学习前端开发，需要掌握：
   - HTML 基础
   - CSS 样式
   - JavaScript 编程
   - React 框架
   ```
3. 选择学习模式（交叉学习 or 集中攻坚）
4. 点击「🚀 生成学习计划」
5. 查看生成的计划，确认后保存

### 2. 管理任务

- 在「🏠 首页」查看每日任务
- 点击「✅ 完成」标记任务完成
- 点击「⏭️ 跳过」将任务移到明天

### 3. 保存学习资源

1. 点击「📚 资源库」
2. 点击「💾 保存资源」
3. 输入资源链接或描述
4. 资源会自动关联到相关任务

### 4. 查看统计

点击「📊 统计」查看学习进度和成果

## 项目结构

```
mingdeng/
├── core/                    # 核心业务逻辑
│   ├── config.py           # 配置管理
│   ├── storage.py          # 数据存储
│   ├── ai.py               # AI 调用
│   ├── todo_manager.py     # 任务管理
│   ├── library_manager.py  # 资源库管理
│   └── plan_generator.py   # 计划生成
├── pages/                   # Streamlit 页面
│   ├── home.py             # 首页
│   ├── plan.py             # 计划生成
│   ├── library.py          # 资源库
│   ├── stats.py            # 统计
│   └── config.py           # 配置
├── data/                    # 数据文件（自动创建）
│   ├── config.json         # API 配置
│   ├── todos.json          # 任务数据
│   ├── library.json        # 资源库数据
│   └── backups/            # 备份文件
├── app.py                   # 主入口
└── requirements.txt         # 依赖列表
```

## 常见问题

### Q: 如何使用免费的本地模型？
A: 使用 Ollama + Qwen/Llama 等开源模型，完全免费。也可以用 vLLM、LM Studio 等工具本地部署，只要提供 OpenAI API 规范的接口即可。参考上面的「选项 B」。

### Q: 数据存储在哪里？
A: 所有数据存储在 `mingdeng/data/` 目录，不会上传到任何服务器。

### Q: 如何备份数据？
A: 直接复制 `data/` 目录。应用也会在重要操作前自动创建备份。

### Q: 遇到错误怎么办？
A:
1. 检查 API 配置是否正确
2. 确保网络连接正常（如果使用云端 API）
3. 查看终端输出的错误信息
4. 在 GitHub Issues 中反馈问题

## 下一步

- 阅读完整的 [README.md](README.md)
- 探索更多功能
- 根据需要调整学习计划
- 享受高效学习！

愿 MingDeng 成为你学习路上的一盏明灯 🏮
