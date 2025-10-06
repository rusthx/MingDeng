# MingDeng API 兼容性说明

## 核心理念

**MingDeng 使用 OpenAI API 规范**，而不是绑定到特定的 AI 服务商。

这意味着：
- ✅ 你可以使用**任何**遵循 OpenAI API 规范的服务
- ✅ 不限于 OpenAI 官方的模型
- ✅ 支持本地部署的开源模型
- ✅ 可以随时切换不同的服务商

## OpenAI API 规范是什么？

OpenAI API 规范是一个标准化的 HTTP API 接口格式，包括：

- **端点结构**: `/v1/chat/completions`
- **请求格式**: JSON，包含 `messages`、`model`、`temperature` 等参数
- **响应格式**: JSON，包含 `choices`、`usage` 等字段
- **流式响应**: Server-Sent Events (SSE)

由于这个规范已经成为事实标准，很多服务都兼容它。

## 支持的服务列表

### 1. OpenAI 官方

```json
{
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "model": "gpt-4o-mini"
}
```

可用模型：
- `gpt-4o` (最新旗舰模型)
- `gpt-4o-mini` (性价比高)
- `gpt-4-turbo`
- `gpt-3.5-turbo`

### 2. 本地模型 - Ollama

```json
{
  "base_url": "http://localhost:11434/v1",
  "api_key": "ollama",
  "model": "qwen2.5:7b"
}
```

可用模型（需先下载）：
- `qwen2.5:7b` (通义千问，推荐)
- `llama3.2` (Meta Llama)
- `mistral` (Mistral AI)
- `deepseek-coder` (代码专用)

### 3. DeepSeek

```json
{
  "base_url": "https://api.deepseek.com/v1",
  "api_key": "sk-...",
  "model": "deepseek-chat"
}
```

### 4. 智谱 AI (GLM)

```json
{
  "base_url": "https://open.bigmodel.cn/api/paas/v4/",
  "api_key": "...",
  "model": "glm-4"
}
```

### 5. Moonshot (Kimi)

```json
{
  "base_url": "https://api.moonshot.cn/v1",
  "api_key": "sk-...",
  "model": "moonshot-v1-8k"
}
```

### 6. 通义千问 (Qwen)

需要参考阿里云百炼平台的文档配置。

### 7. 本地部署工具

#### vLLM
运行本地模型，提供 OpenAI API 兼容接口：
```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --port 8000
```

配置：
```json
{
  "base_url": "http://localhost:8000/v1",
  "api_key": "EMPTY",
  "model": "Qwen/Qwen2.5-7B-Instruct"
}
```

#### LM Studio
图形化界面，支持 OpenAI API 规范。

#### text-generation-webui
运行：
```bash
python server.py --api --extensions openai
```

## 如何选择？

### 需要最佳性能和体验
→ **OpenAI 官方** (gpt-4o-mini)
- 优点：质量高、稳定、速度快
- 缺点：需要付费

### 完全免费 + 隐私保护
→ **Ollama + Qwen2.5**
- 优点：免费、本地运行、隐私安全
- 缺点：需要本地算力

### 性价比
→ **DeepSeek**
- 优点：便宜、质量不错
- 缺点：需要付费

### 中文场景
→ **智谱 GLM** 或 **通义千问** 或 **Ollama + Qwen2.5**

## 验证 API 兼容性

如何判断一个 API 是否兼容 OpenAI 规范？

**测试方法**：

```bash
curl https://your-api-endpoint/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "model-name",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

如果返回类似这样的 JSON，就是兼容的：
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you?"
      }
    }
  ]
}
```

## 代码实现

MingDeng 使用 `openai` Python 包，它支持自定义 `base_url`：

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://any-compatible-api.com/v1",
    api_key="your-api-key"
)

response = client.chat.completions.create(
    model="any-model",
    messages=[{"role": "user", "content": "Hello"}]
)
```

这就是为什么 MingDeng 可以支持任何兼容 OpenAI API 规范的服务！

## 常见问题

### Q: 为什么不直接支持其他 API 格式（如 Anthropic Claude）？

A: 
1. OpenAI API 规范已经是事实标准
2. 大多数服务都提供兼容接口
3. 保持代码简单统一
4. Claude 可以通过代理转换为 OpenAI 格式

### Q: 本地模型性能如何？

A: 取决于你的硬件：
- **好的**: Apple Silicon Mac、NVIDIA 显卡
- **可用**: 现代 CPU（速度较慢）
- **推荐**: 至少 16GB 内存

### Q: 如何切换不同的 API？

A: 在「⚙️ 配置」页面，修改 base_url、api_key 和 model，保存即可。

### Q: 可以同时使用多个 API 吗？

A: 当前版本不支持，但你可以通过修改配置来切换。

---

**总结**: MingDeng 是一个开放、灵活的系统，你可以使用任何符合 OpenAI API 规范的服务，无论是云端还是本地！🎉
