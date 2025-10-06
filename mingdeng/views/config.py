"""
配置页面
用于配置 API 和用户信息
"""

import streamlit as st
from core.config import config_manager
from core.ai import ai_client


def show():
    """显示配置页面"""

    st.markdown("## ⚙️ 配置管理")
    st.markdown("---")

    # API 配置
    st.markdown("### 🔌 API 配置")
    st.info("""
    MingDeng 使用 **OpenAI API 规范**，支持任何兼容此规范的服务：
    - OpenAI 官方服务（GPT-4o、GPT-4o-mini 等）
    - 本地模型（Ollama、vLLM、LM Studio、text-generation-webui 等）
    - 其他云端服务（DeepSeek、智谱 GLM、通义千问、Moonshot 等）
    - 任何提供 OpenAI API 规范接口的服务
    """)

    st.warning("""
    **⚠️ Base URL 填写规则（重要！）**

    系统会自动添加 `/chat/completions`，所以你需要把这部分删掉：

    **例子**：
    - ❌ 错误：`https://router.shengsuanyun.com/api/v1/chat/completions`
    - ✅ 正确：`https://router.shengsuanyun.com/api/v1`

    - ❌ 错误：`https://api.openai.com/v1/chat/completions`
    - ✅ 正确：`https://api.openai.com/v1`

    **规则**：
    1. 删除末尾的 `/chat/completions` 或 `/completions`
    2. 删除末尾的斜杠 `/`
    3. 只保留基础地址部分
    """)

    # 加载当前配置
    api_config = config_manager.get_api_config()
    current_base_url = api_config.get("base_url", "") if api_config else ""
    current_api_key = api_config.get("api_key", "") if api_config else ""
    current_model = api_config.get("model", "") if api_config else ""

    # API 提供商选择（快捷配置模板）
    provider = st.selectbox(
        "快捷配置模板（可选）",
        ["自定义", "OpenAI 官方", "Ollama (本地)", "DeepSeek", "智谱 GLM", "Moonshot (Kimi)"],
        index=0 if not current_base_url else 0
    )

    # 根据模板预填充
    if provider == "OpenAI 官方":
        default_base_url = "https://api.openai.com/v1"
        default_model = "gpt-4o-mini"
    elif provider == "Ollama (本地)":
        default_base_url = "http://localhost:11434/v1"
        default_model = "qwen2.5:7b"
    elif provider == "DeepSeek":
        default_base_url = "https://api.deepseek.com/v1"
        default_model = "deepseek-chat"
    elif provider == "智谱 GLM":
        default_base_url = "https://open.bigmodel.cn/api/paas/v4"
        default_model = "glm-4"
    elif provider == "Moonshot (Kimi)":
        default_base_url = "https://api.moonshot.cn/v1"
        default_model = "moonshot-v1-8k"
    else:  # 自定义
        default_base_url = current_base_url
        default_model = current_model

    # 输入框
    base_url = st.text_input(
        "API 基础 URL",
        value=current_base_url or default_base_url,
        placeholder="例如: https://router.shengsuanyun.com/api/v1",
        help="只填写基础地址，不要包含 /chat/completions"
    )

    # 实时检查和提示
    if base_url:
        if "/chat/completions" in base_url or "/completions" in base_url:
            st.error("❌ 检测到 `/chat/completions` 或 `/completions`，请删除这部分！")
            suggested_url = base_url.replace("/chat/completions", "").replace("/completions", "").rstrip("/")
            st.info(f"💡 建议修改为: `{suggested_url}`")
        elif base_url.endswith("/"):
            st.warning("⚠️ 建议删除末尾的斜杠 `/`")
            st.info(f"💡 建议修改为: `{base_url.rstrip('/')}`")
        else:
            st.success(f"✅ 格式正确！完整请求地址将是: `{base_url}/chat/completions`")

    api_key = st.text_input(
        "API 密钥",
        value=current_api_key,
        type="password",
        help="你的 API 密钥（本地模型可能不需要）"
    )

    model = st.text_input(
        "模型名称",
        value=current_model or default_model,
        help="模型名称，取决于你使用的服务。例如: gpt-4o-mini (OpenAI), qwen2.5:7b (Ollama), deepseek-chat (DeepSeek), glm-4 (智谱), moonshot-v1-8k (Moonshot)"
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("💾 保存配置", type="primary", use_container_width=True):
            # 验证配置
            is_valid, error_msg = config_manager.validate_api_config(
                base_url, api_key, model
            )

            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                # 保存配置
                if config_manager.update_api_config(base_url, api_key, model):
                    # 刷新 AI 客户端
                    ai_client.refresh_client()
                    st.success("✅ API 配置已保存！")
                    st.rerun()
                else:
                    st.error("❌ 保存配置失败")

    with col2:
        if st.button("🧪 测试连接", use_container_width=True):
            # 临时更新配置进行测试
            config_manager.update_api_config(base_url, api_key, model)
            ai_client.refresh_client()

            with st.spinner("测试连接中..."):
                success, message = ai_client.test_connection()

            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")

    st.markdown("---")

    # 用户配置
    st.markdown("### 👤 用户配置")

    user_config = config_manager.get_user_config()
    current_name = user_config.get("name", "学习者") if user_config else "学习者"
    current_timezone = user_config.get("timezone", "Asia/Shanghai") if user_config else "Asia/Shanghai"

    user_name = st.text_input(
        "你的名字",
        value=current_name,
        help="用于个性化称呼"
    )

    timezone = st.selectbox(
        "时区",
        ["Asia/Shanghai", "Asia/Tokyo", "America/New_York", "Europe/London"],
        index=0
    )

    if st.button("💾 保存用户信息", use_container_width=True):
        if config_manager.update_user_config(user_name, timezone):
            st.success("✅ 用户信息已保存！")
        else:
            st.error("❌ 保存用户信息失败")

    st.markdown("---")

    # 数据管理
    st.markdown("### 🗄️ 数据管理")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("配置状态", "✅ 已配置" if config_manager.is_configured() else "⚠️ 未配置")

    with col2:
        if st.button("📦 查看备份", use_container_width=True):
            st.session_state['show_backups'] = True

    with col3:
        if st.button("📤 导出数据", use_container_width=True):
            st.info("导出功能即将推出...")

    # 显示备份列表
    if st.session_state.get('show_backups', False):
        st.markdown("#### 📦 备份列表")
        from core.backup_manager import backup_manager
        backups = backup_manager.list_backups()

        if not backups:
            st.info("暂无备份")
        else:
            for backup in backups:
                with st.expander(f"📁 {backup.get('created_at', '')} - {backup.get('reason', '')}"):
                    st.json(backup)

    st.markdown("---")

    # 关于信息
    st.markdown("### ℹ️ 关于 MingDeng")
    st.markdown("""
    **版本**: 1.0.0
    **开源协议**: MIT License
    **项目地址**: [GitHub](https://github.com/your-org/mingdeng)

    MingDeng 是一个开源的 AI 学习助手，帮助你战胜知识爆炸、遗忘和拖延。

    **特点**:
    - 🎯 AI 自动生成学习计划
    - 📚 智能资源管理
    - 📊 学习进度可视化
    - 🔒 数据本地存储，隐私安全
    """)
