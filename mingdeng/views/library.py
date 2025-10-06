"""
资源库页面
管理学习资源，查看关联任务
"""

import streamlit as st
from core.library_manager import library_manager
from core.storage import storage


def show():
    """显示资源库页面"""

    st.markdown("## 📚 学习资源库")
    st.markdown("---")

    # 添加资源表单（直接显示）
    st.markdown("### 💾 添加新资源")

    with st.form("add_resource_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            content = st.text_input(
                "资源链接或内容",
                placeholder="https://youtube.com/watch?v=xxx 或纯文本描述",
                help="可以是视频链接、文章链接、论文链接或纯文本笔记"
            )

        with col2:
            resource_type = st.selectbox(
                "类型",
                ["自动识别", "视频", "文章", "论文", "其他"]
            )

        description = st.text_area(
            "描述（可选）",
            placeholder="简要描述这个资源的内容",
            height=80
        )

        col1, col2 = st.columns([1, 5])
        with col1:
            submitted = st.form_submit_button("✅ 保存", type="primary", use_container_width=True)

        if submitted and content:
            resource_id = library_manager.capture_resource(
                content=content,
                description=description,
                auto_link=True
            )

            if resource_id:
                st.success("✅ 资源已保存！")
                st.rerun()
            else:
                st.error("❌ 保存资源失败")

    st.markdown("---")

    # 过滤选项
    col1, col2 = st.columns(2)

    with col1:
        filter_type = st.selectbox(
            "按类型过滤",
            ["全部", "视频", "文章", "论文", "其他"]
        )

    with col2:
        filter_status = st.selectbox(
            "按状态过滤",
            ["全部", "未读", "阅读中", "已完成"]
        )

    # 应用过滤
    type_map = {
        "全部": None,
        "视频": "video",
        "文章": "article",
        "论文": "paper",
        "其他": "other"
    }
    status_map = {
        "全部": None,
        "未读": "unread",
        "阅读中": "reading",
        "已完成": "completed"
    }

    resources = library_manager.get_all_resources(
        filter_type=type_map[filter_type],
        filter_status=status_map[filter_status]
    )

    # 显示资源列表
    st.markdown("---")

    if not resources:
        st.info("📝 还没有保存任何资源，在上方表单中添加第一个资源吧！")
    else:
        st.markdown(f"### 📋 找到 {len(resources)} 个资源")

        for resource in resources:
            show_resource_card(resource)


def show_resource_card(resource: dict):
    """显示资源卡片"""

    resource_type = resource.get("type", "other")
    status = resource.get("status", "unread")

    # 类型图标
    type_emoji = {
        "video": "🎥",
        "article": "📄",
        "paper": "📜",
        "other": "📌"
    }
    emoji = type_emoji.get(resource_type, "📌")

    # 状态图标
    status_emoji = {
        "unread": "📭",
        "reading": "📖",
        "completed": "✅"
    }
    status_icon = status_emoji.get(status, "📭")

    with st.expander(f"{emoji} {status_icon} {resource.get('content', '')[:80]}...", expanded=False):
        # 内容
        st.markdown(f"**内容**: {resource['content']}")

        if resource.get('description'):
            st.markdown(f"**描述**: {resource['description']}")

        st.caption(f"类型: {resource_type} | 状态: {status} | 捕获时间: {resource.get('captured_at', '')}")

        # 关联的任务
        linked_task_ids = resource.get('linked_tasks', [])
        if linked_task_ids:
            st.markdown("**关联任务**:")
            for task_id in linked_task_ids:
                task = storage.get_task_by_id(task_id)
                if task:
                    st.markdown(f"- {task['task']} ({task['date']})")
        else:
            st.caption("未关联到任何任务")

        # 操作按钮
        col1, col2, col3 = st.columns(3)

        with col1:
            new_status = st.selectbox(
                "更新状态",
                ["unread", "reading", "completed"],
                index=["unread", "reading", "completed"].index(status),
                key=f"status_{resource['id']}"
            )
            if new_status != status:
                if library_manager.update_resource_status(resource['id'], new_status):
                    st.success("✅ 状态已更新")
                    st.rerun()

        with col2:
            if st.button("🔗 关联任务", key=f"link_{resource['id']}"):
                st.info("关联功能：请在任务中选择相关资源")

        with col3:
            if st.button("🗑️ 删除", key=f"delete_{resource['id']}"):
                if library_manager.delete_resource(resource['id']):
                    st.success("✅ 资源已删除")
                    st.rerun()
