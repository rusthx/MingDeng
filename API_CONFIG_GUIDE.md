# API 配置指南

## 问题诊断

如果你遇到 **404 page not found** 错误，说明 `base_url` 配置不正确。

### 使用诊断脚本

运行测试脚本查看详细的错误信息：

```bash
conda activate dl
python test_api.py
```

这个脚本会显示：
- 你的当前配置
- 完整的请求 URL
- 详细的错误信息和诊断建议

## Base URL 配置规则

### ⚠️ 重要原则

1. **不要在末尾加斜杠 `/`**
   - ✅ 正确：`https://api.openai.com/v1`
   - ❌ 错误：`https://api.openai.com/v1/`

2. **根据 API 文档确定是否需要 `/v1`**
   - 如果完整路径是 `https://xxx/v1/chat/completions` → base_url 填 `https://xxx/v1`
   - 如果完整路径是 `https://xxx/chat/completions` → base_url 填 `https://xxx`

3. **OpenAI SDK 会自动添加 `/chat/completions`**
   - 你只需要提供基础部分
   - SDK 会自动拼接完整路径

## 常见 API 服务配置

### 1. OpenAI 官方

```
Base URL: https://api.openai.com/v1
API Key: sk-...
Model: gpt-4o-mini
```

完整请求路径：`https://api.openai.com/v1/chat/completions`

### 2. Ollama (本地)

```
Base URL: http://localhost:11434/v1
API Key: ollama (任意字符串)
Model: qwen2.5:7b
```

完整请求路径：`http://localhost:11434/v1/chat/completions`

**注意**：
- Ollama 不需要真实的 API Key，填任意字符串即可
- 确保 Ollama 服务已启动：`ollama serve`
- 确保模型已下载：`ollama pull qwen2.5:7b`

### 3. DeepSeek

```
Base URL: https://api.deepseek.com/v1
API Key: sk-...
Model: deepseek-chat
```

完整请求路径：`https://api.deepseek.com/v1/chat/completions`

### 4. 智谱 GLM

```
Base URL: https://open.bigmodel.cn/api/paas/v4
API Key: ...
Model: glm-4
```

完整请求路径：`https://open.bigmodel.cn/api/paas/v4/chat/completions`

### 5. Moonshot (Kimi)

```
Base URL: https://api.moonshot.cn/v1
API Key: sk-...
Model: moonshot-v1-8k
```

完整请求路径：`https://api.moonshot.cn/v1/chat/completions`

### 6. vLLM (本地)

```
Base URL: http://localhost:8000/v1
API Key: EMPTY (任意字符串)
Model: your-model-name
```

完整请求路径：`http://localhost:8000/v1/chat/completions`

**启动 vLLM 服务**：
```bash
vllm serve your-model-name --host 0.0.0.0 --port 8000
```

### 7. LM Studio (本地)

```
Base URL: http://localhost:1234/v1
API Key: lm-studio (任意字符串)
Model: 你在 LM Studio 中加载的模型名称
```

完整请求路径：`http://localhost:1234/v1/chat/completions`

### 8. text-generation-webui (本地)

启动时添加 OpenAI API 扩展：
```bash
python server.py --api --extensions openai
```

```
Base URL: http://localhost:5000/v1
API Key: sk-111111111111111111111111111111111111111111111111
Model: 你加载的模型名称
```

## 故障排除

### 404 错误

**原因**：base_url 不正确

**解决方法**：
1. 运行 `python test_api.py` 查看完整请求 URL
2. 对照你的 API 文档，确认正确的 URL 格式
3. 常见问题：
   - 多余的末尾斜杠：`/v1/` → 改为 `/v1`
   - 缺少 `/v1`：某些服务需要 `/v1`，某些不需要
   - 路径错误：例如智谱 GLM 使用 `/api/paas/v4` 而不是 `/v1`

### 401 错误

**原因**：API Key 不正确或无效

**解决方法**：
1. 检查 API Key 是否正确
2. 检查 API Key 是否过期
3. 检查 API Key 是否有权限调用该模型

### Connection 错误

**原因**：网络连接问题或服务未启动

**解决方法**：
1. 检查网络连接
2. 如果是本地服务：
   - Ollama: `ollama serve`
   - vLLM: 检查服务是否在运行
   - LM Studio: 检查是否已启动服务器
3. 检查防火墙设置

## 验证配置

### 方法 1：使用测试脚本

```bash
python test_api.py
```

### 方法 2：使用应用内测试

1. 在应用中进入「⚙️ 配置」页面
2. 填写 API 配置
3. 点击「🧪 测试连接」按钮

### 方法 3：使用 curl 测试

```bash
# OpenAI 格式
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

如果 curl 能成功，但应用中失败，请运行 `python test_api.py` 查看详细信息。

## 需要帮助？

如果按照以上步骤仍无法解决问题，请：

1. 运行 `python test_api.py` 并保存输出
2. 提供你使用的 API 服务名称
3. 提供 API 文档中的完整 URL 格式
4. 提供错误信息的完整内容
