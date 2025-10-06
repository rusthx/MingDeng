# MingDeng 更新日志

## [1.0.0] - 2025-10-07

### 重要说明
明确了 **OpenAI API 规范** 的含义：
- MingDeng 支持**任何**遵循 OpenAI API 规范的服务
- 不仅限于 OpenAI 官方的模型
- 支持本地部署的开源模型（Ollama、vLLM 等）
- 支持国内外各种兼容服务（DeepSeek、智谱、Moonshot 等）

### 新增文档
- `API_COMPATIBILITY.md` - API 兼容性详细说明
- 包含多个服务商的配置示例
- 说明如何验证 API 兼容性

### 更新内容

#### 配置页面 (pages/config.py)
- 更新 API 配置说明文案
- 新增快捷配置模板：
  - OpenAI 官方
  - Ollama (本地)
  - DeepSeek
  - 智谱 GLM
  - Moonshot (Kimi)
- 优化模型名称提示信息

#### 文档更新
- `QUICKSTART.md`: 明确说明 OpenAI API 规范，添加更多服务商示例
- `STRUCTURE.md`: 更新技术栈说明和设计原则
- `app.py`: 更新欢迎页面说明

### 核心特性 (v1.0.0)

✅ **完整的后端 API**
- 配置管理
- JSON 存储层
- 备份管理（最多 10 个）
- AI 调用（基于 OpenAI API 规范）
- Mem0 记忆系统（可选）
- 任务管理
- 资源库管理
- 学习计划生成

✅ **Streamlit Web 界面**
- 首页（任务列表、日历视图）
- 计划生成页面
- 资源库页面
- 统计页面
- 配置页面

✅ **核心功能**
- AI 批量生成学习计划
- 学习模式选择（交叉学习/集中攻坚）
- 任务管理（完成/跳过/移动）
- 资源保存与 AI 自动关联
- 学习进度统计与可视化
- 数据备份与恢复

### 技术细节

**依赖项**:
- Python 3.9+
- streamlit
- openai (支持自定义 base_url)
- mem0ai (可选)
- plotly
- pandas
- pydantic
- streamlit-aggrid
- python-dateutil

**数据存储**:
- 本地 JSON 文件
- 自动备份机制
- 隐私安全

### 已知限制

1. Mem0 记忆系统为可选功能，未安装时会优雅降级
2. AI 学习总结功能为占位符，待后续实现
3. 数据导出功能即将推出
4. 暂不支持同时使用多个 API（可通过配置切换）

### 下一步计划

- [ ] AI 学习总结（基于 Memory）
- [ ] 数据导出（Markdown/PDF）
- [ ] 日历视图增强（拖拽调整）
- [ ] 任务提醒通知
- [ ] 主计划 + 子计划
- [ ] Electron 桌面应用

---

## 贡献者

感谢所有为 MingDeng 做出贡献的开发者！

---

**愿 MingDeng 成为你学习路上的一盏明灯 🏮**
