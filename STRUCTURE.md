# MingDeng 项目结构

```
MingDeng/
├── README.md                    # 项目主文档（完整的功能说明）
├── QUICKSTART.md                # 快速开始指南
├── USAGE_GUIDE.md               # 详细使用指南
├── PROJECT_STATUS.md            # 项目实现状态
├── .gitignore                   # Git 忽略配置
│
└── mingdeng/                    # 主应用目录
    ├── app.py                   # Streamlit 主入口
    ├── requirements.txt         # Python 依赖
    │
    ├── core/                    # 核心业务逻辑层
    │   ├── __init__.py
    │   ├── config.py            # 配置管理（API、用户配置）
    │   ├── storage.py           # JSON 存储层（数据持久化）
    │   ├── backup_manager.py    # 备份管理（自动备份，最多 10 个）
    │   ├── ai.py                # AI 调用（OpenAI 兼容，支持 streaming）
    │   ├── memory.py            # Mem0 记忆系统（可选）
    │   ├── todo_manager.py      # 任务管理 API
    │   ├── library_manager.py   # 资源库管理 API
    │   └── plan_generator.py    # 学习计划生成 API
    │
    ├── pages/                   # Streamlit 页面模块
    │   ├── __init__.py
    │   ├── home.py              # 首页（任务列表、日历视图）
    │   ├── plan.py              # 计划生成页面
    │   ├── library.py           # 资源库页面
    │   ├── stats.py             # 统计页面
    │   └── config.py            # 配置页面
    │
    ├── components/              # 可复用 UI 组件（预留）
    │   └── __init__.py
    │
    └── data/                    # 数据目录（自动创建，不提交到 Git）
        ├── config.json          # API 和用户配置
        ├── todos.json           # 任务数据
        ├── library.json         # 资源库数据
        ├── memory/              # Mem0 数据
        └── backups/             # 备份文件（最多 10 个）
            ├── metadata_*.json
            ├── todos_*.json
            └── library_*.json
```

## 模块说明

### 核心层 (core/)

**config.py** - 配置管理
- 加载/保存 API 配置
- 验证 API 配置
- 用户配置管理

**storage.py** - 数据持久化
- JSON 文件读写
- 计划 CRUD 操作
- 任务 CRUD 操作
- 资源 CRUD 操作

**backup_manager.py** - 备份管理
- 创建备份
- 列出备份
- 恢复备份
- 自动清理旧备份（保留最多 10 个）

**ai.py** - AI 调用
- 基于 OpenAI API 规范的客户端
- 支持任何兼容此规范的服务（OpenAI、Ollama、DeepSeek 等）
- 流式响应支持
- JSON 生成
- 连接测试

**memory.py** - 记忆系统
- Mem0 集成（可选）
- 学习日志存储
- 对话记录
- 上下文检索

**todo_manager.py** - 任务管理
- 今日任务查询
- 任务完成/跳过
- 任务移动
- 批量调整
- 统计分析

**library_manager.py** - 资源库管理
- 资源捕获
- 类型自动识别
- AI 自动关联任务
- 资源搜索

**plan_generator.py** - 计划生成
- AI 批量生成计划
- 学习模式（交叉/集中）
- 计划预览
- 日期调整

### 页面层 (pages/)

**home.py** - 首页
- 今日任务列表
- 本周任务视图
- 所有计划视图
- 快速添加任务
- 任务操作（完成/跳过）

**plan.py** - 计划生成
- 学习内容输入
- 模式选择
- AI 生成
- 计划预览
- 保存计划

**library.py** - 资源库
- 资源保存
- 资源列表
- 过滤（类型、状态）
- 关联管理

**stats.py** - 统计
- 概览指标
- 难度分布
- 完成率分析
- 计划进度

**config.py** - 配置
- API 配置
- 用户配置
- 连接测试
- 备份管理

## 数据流

```
用户交互 (Streamlit UI)
    ↓
页面层 (pages/)
    ↓
核心 API (core/)
    ↓
数据层 (storage.py)
    ↓
JSON 文件 (data/)
```

## AI 调用流程

```
用户输入
    ↓
plan_generator.py / library_manager.py
    ↓
ai.py (OpenAI 兼容 API)
    ↓
外部 AI 服务 (OpenAI / Ollama / DeepSeek 等)
    ↓
解析结果
    ↓
返回给用户
```

## 备份流程

```
重要操作 (批量生成/删除)
    ↓
backup_manager.create_backup()
    ↓
复制 todos.json + library.json
    ↓
保存到 data/backups/
    ↓
清理旧备份 (超过 10 个)
```

## 技术栈

- **前端**: Streamlit (Python Web 框架)
- **后端**: Python 3.9+
- **AI**: 基于 OpenAI API 规范（支持 OpenAI、Ollama、DeepSeek、智谱、Moonshot 等）
- **记忆**: Mem0 (可选)
- **存储**: JSON 文件
- **可视化**: Plotly

## 依赖项

见 `mingdeng/requirements.txt`：
- streamlit
- openai
- mem0ai (可选)
- plotly
- pandas
- pydantic

## 设计原则

1. **模块化**: 核心逻辑与 UI 分离
2. **开放兼容**: 使用 OpenAI API 规范，支持任何兼容的服务
3. **本地优先**: 数据本地存储，隐私安全
4. **优雅降级**: Mem0 等可选功能未安装时仍可用
5. **用户友好**: 简洁直观的界面

---

**愿 MingDeng 成为你学习路上的一盏明灯 🏮**
