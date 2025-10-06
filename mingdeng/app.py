"""
MingDeng - AI 学习助手
Streamlit 主入口
"""

import streamlit as st
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from core.config import config_manager
from views import home, plan, library, stats, config

# 页面配置
st.set_page_config(
    page_title="MingDeng - AI 学习助手",
    page_icon="🏮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        padding: 1rem 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-style: italic;
        margin-bottom: 2rem;
    }
    .task-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid;
    }
    .task-simple {
        border-left-color: #4CAF50;
        background-color: #f1f8f4;
    }
    .task-medium {
        border-left-color: #FFC107;
        background-color: #fff8e1;
    }
    .task-hard {
        border-left-color: #F44336;
        background-color: #ffebee;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """主函数"""

    # 检查 API 配置
    if not config_manager.is_configured():
        st.markdown("<div class='main-header'>🏮 MingDeng</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>在学习的黑暗中，为你照亮前路</div>", unsafe_allow_html=True)

        st.warning("### ⚠️ 欢迎使用 MingDeng！")
        st.info("""
        请先配置 API，然后开始使用。

        **支持的 API**: 任何遵循 OpenAI API 规范的服务
        - OpenAI 官方、DeepSeek、智谱 GLM、Moonshot (Kimi)
        - 本地模型：Ollama、vLLM、LM Studio 等
        """)

        st.markdown("---")
        st.markdown("## ⚙️ 配置")
        config.show()
        return

    # 已配置，显示主界面
    # 使用 tabs 来组织不同页面
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 首页",
        "📋 生成计划",
        "📚 资源库",
        "📊 统计",
        "⚙️ 配置"
    ])

    with tab1:
        home.show()

    with tab2:
        plan.show()

    with tab3:
        library.show()

    with tab4:
        stats.show()

    with tab5:
        config.show()


if __name__ == "__main__":
    main()
