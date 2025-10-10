# MingDeng 开发文档

## 架构设计

### 系统架构

```
┌─────────────────────────────────┐
│   Tauri 桌面应用 (Rust)          │
├─────────────────────────────────┤
│  前端（HTML/CSS/JS）             │
│   - 页面路由                     │
│   - UI 组件                      │
│   - API 调用                     │
├─────────────────────────────────┤
│  HTTP 通信 (127.0.0.1:8765)     │
├─────────────────────────────────┤
│  Python FastAPI 后端             │
│   - REST API 端点                │
│   - 业务逻辑                     │
│   - AI 集成                      │
│   - 数据存储                     │
└─────────────────────────────────┘
```

### 核心模块

#### Backend (Python)

1. **config.py** - 配置管理
   - API 配置（base_url, api_key, model）
   - 用户配置（name, timezone）
   - 配置加载和保存

2. **storage.py** - 数据存储
   - JSON 文件读写
   - todos.json（学习计划和任务）
   - library.json（资源库）

3. **ai.py** - AI 客户端
   - OpenAI 兼容 API 调用
   - 流式响应支持
   - 学习计划生成
   - 资源自动关联

4. **memory.py** - 记忆系统
   - Mem0 集成
   - 对话历史存储
   - 上下文检索

5. **todo_manager.py** - 任务管理
   - CRUD 操作
   - 日期过滤
   - 统计数据

6. **plan_generator.py** - 计划生成
   - AI 驱动的计划生成
   - 日期智能排布
   - 任务依赖分析

7. **library_manager.py** - 资源管理
   - 资源 CRUD
   - 自动关联任务
   - 关键词匹配

8. **backup_manager.py** - 备份管理
   - 自动备份
   - 备份恢复
   - 最多保留 10 个备份

#### Frontend (JavaScript)

1. **main.js** - 主逻辑
   - 页面路由
   - API 调用封装
   - 全局状态管理
   - 事件处理

2. **页面模块**
   - today.html - 今日任务
   - plan.html - 计划生成
   - stats.html - 统计
   - library.html - 资源库
   - settings.html - 设置

3. **style.css** - 样式
   - Tailwind CSS 扩展
   - 自定义组件样式
   - 动画效果

#### Tauri (Rust)

1. **main.rs** - 应用入口
   - Python 后端启动
   - 窗口管理
   - 系统托盘

## API 端点

### 配置 API

- `GET /api/config` - 获取配置
- `POST /api/config` - 更新配置

### 任务 API

- `GET /api/today` - 获取今日任务
- `GET /api/tasks/date/{date}` - 按日期获取任务
- `POST /api/tasks` - 创建任务
- `PUT /api/tasks/{id}` - 更新任务
- `DELETE /api/tasks/{id}` - 删除任务
- `POST /api/tasks/{id}/complete` - 完成任务
- `POST /api/tasks/{id}/uncomplete` - 取消完成

### 计划 API

- `GET /api/plans` - 获取所有计划
- `GET /api/plans/{id}` - 获取单个计划
- `DELETE /api/plans/{id}` - 删除计划
- `POST /api/plan/generate` - 生成学习计划

### AI API

- `POST /api/chat` - AI 对话（支持流式）

### 资源 API

- `GET /api/resources` - 获取所有资源
- `GET /api/resources/{id}` - 获取单个资源
- `POST /api/resources` - 创建资源
- `PUT /api/resources/{id}` - 更新资源
- `DELETE /api/resources/{id}` - 删除资源
- `GET /api/resources/task/{task_id}` - 获取任务关联资源

### 统计 API

- `GET /api/stats` - 获取学习统计

### 备份 API

- `POST /api/backup` - 创建备份
- `GET /api/backups` - 列出备份
- `POST /api/restore/{id}` - 恢复备份
- `DELETE /api/backups/{id}` - 删除备份

## 数据模型

### Config (config.json)

```json
{
  "api": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-...",
    "model": "gpt-4"
  },
  "user": {
    "name": "用户名",
    "timezone": "Asia/Shanghai"
  }
}
```

### Todo (todos.json)

```json
{
  "plans": [
    {
      "id": "uuid",
      "name": "学习计划名称",
      "created_at": "2025-10-10T14:30:00",
      "tasks": [
        {
          "id": "uuid",
          "task": "任务描述",
          "date": "2025-10-10",
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

### Library (library.json)

```json
{
  "resources": [
    {
      "id": "uuid",
      "content": "https://youtube.com/...",
      "description": "资源描述",
      "type": "video|article|paper|other",
      "captured_at": "2025-10-10T10:00:00",
      "linked_tasks": ["task_uuid"],
      "status": "unread|reading|completed"
    }
  ]
}
```

## 开发环境设置

### 1. Python 环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
cd backend
pip install -r requirements.txt
```

### 2. Rust 环境

```bash
# 安装 Rust (如果未安装)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 Tauri CLI
cargo install tauri-cli
```

### 3. 启动开发服务器

```bash
# 方式 1: Tauri 自动启动 Python 后端
npm run dev

# 方式 2: 手动启动
# 终端 1
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8765

# 终端 2
npm run tauri dev
```

## 调试技巧

### Python 后端调试

1. 查看日志输出
2. 使用 FastAPI 自动生成的文档：http://127.0.0.1:8765/docs
3. 使用 print() 或 logging 模块

### 前端调试

1. 打开 Chrome DevTools（开发模式下）
2. 查看 Console 输出
3. 使用 Network 标签查看 API 请求

### API 测试

使用 curl 或 Postman 测试 API：

```bash
# 获取今日任务
curl http://127.0.0.1:8765/api/today

# 创建任务
curl -X POST http://127.0.0.1:8765/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "...",
    "task": "学习 Python",
    "date": "2025-10-10",
    "estimated_time": 60,
    "difficulty": "medium"
  }'
```

## 性能优化

### 前端优化

1. 使用 Tailwind CSS CDN（开发）或 CLI（生产）
2. 懒加载页面内容
3. 缓存 API 响应
4. 使用 requestAnimationFrame 优化动画

### 后端优化

1. 使用异步 I/O（FastAPI + async/await）
2. 缓存 AI 响应（统计数据缓存 24 小时）
3. 批量操作减少文件 I/O
4. 使用流式响应减少等待时间

### 存储优化

1. 定期清理旧备份（最多 10 个）
2. 压缩 JSON 文件（生产环境）
3. 使用增量备份

## 测试

### 单元测试（Python）

```bash
cd backend
pytest
```

### 集成测试

```bash
# 启动后端
npm run backend

# 运行测试
python backend/tests/test_api.py
```

## 构建和发布

### 开发构建

```bash
npm run dev
```

### 生产构建

```bash
npm run build
```

构建产物：
- macOS: `src-tauri/target/release/bundle/macos/MingDeng.app`
- Windows: `src-tauri/target/release/MingDeng.exe`
- Linux: `src-tauri/target/release/bundle/appimage/mingdeng.AppImage`

### 发布清单

- [ ] 更新版本号（package.json, Cargo.toml, tauri.conf.json）
- [ ] 运行测试
- [ ] 更新 CHANGELOG.md
- [ ] 构建所有平台
- [ ] 创建 GitHub Release
- [ ] 上传构建产物
- [ ] 更新文档

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

- Python: 遵循 PEP 8
- JavaScript: 使用 ESLint
- Rust: 使用 `cargo fmt`

### 提交信息规范

```
type(scope): subject

body

footer
```

类型：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

## 常见问题

### Q: 如何添加新的 API 端点？

1. 在 `backend/main.py` 添加路由
2. 在对应的 manager 模块添加逻辑
3. 在前端 `main.js` 添加 API 调用
4. 更新文档

### Q: 如何添加新页面？

1. 在 `src/pages/` 创建 HTML 文件
2. 在 `main.js` 添加导航处理
3. 在 `index.html` 添加导航链接
4. 实现页面初始化逻辑

### Q: 如何修改 AI Prompt？

修改 `backend/core/ai.py` 中的 prompt 模板。

## 路线图

### v0.2.0
- [ ] 拖拽排序任务
- [ ] 日历视图
- [ ] 桌面通知
- [ ] 快捷键系统

### v0.3.0
- [ ] 数据导出/导入
- [ ] 主题切换（浅色/深色）
- [ ] 多语言支持
- [ ] 更多统计图表

### v1.0.0
- [ ] 云同步（可选）
- [ ] 移动端应用
- [ ] 插件系统
- [ ] 社区分享

## 许可证

MIT License

---

有问题？[提交 Issue](https://github.com/your-org/mingdeng/issues)
