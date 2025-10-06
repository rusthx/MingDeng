"""
首页 - 任务列表和日历视图
"""

import streamlit as st
from datetime import datetime, timedelta
from core.todo_manager import todo_manager
from core.library_manager import library_manager


def show():
    """显示首页"""

    st.markdown("## 🏠 我的学习任务")
    st.markdown("---")

    # 顶部操作栏
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        if st.button("➕ 添加任务", use_container_width=True):
            st.session_state['show_add_task_modal'] = True

    with col2:
        view_mode = st.selectbox(
            "视图",
            ["今日任务", "本周任务", "所有计划"],
            label_visibility="collapsed"
        )

    with col3:
        filter_status = st.selectbox(
            "状态",
            ["全部", "待完成", "已完成", "已跳过"],
            label_visibility="collapsed"
        )

    st.markdown("---")

    # 显示添加任务对话框
    if st.session_state.get('show_add_task_modal', False):
        show_add_task_modal()

    # 根据视图模式显示不同内容
    if view_mode == "今日任务":
        show_today_tasks(filter_status)
    elif view_mode == "本周任务":
        show_week_tasks(filter_status)
    else:
        show_all_plans(filter_status)


def show_add_task_modal():
    """显示添加任务对话框"""

    with st.form("add_task_form"):
        st.markdown("### ➕ 添加任务")

        task_name = st.text_input("任务名称", placeholder="例如：学习 Python 装饰器")

        col1, col2 = st.columns(2)
        with col1:
            task_date = st.date_input("日期", value=datetime.now())
        with col2:
            estimated_time = st.number_input("预计时长（分钟）", min_value=15, max_value=240, value=60, step=15)

        col1, col2 = st.columns(2)
        with col1:
            difficulty = st.selectbox("难度", ["simple", "medium", "hard"], index=1)
        with col2:
            priority = st.selectbox("优先级", ["high", "medium", "low"], index=1)

        tags = st.text_input("标签（用逗号分隔）", placeholder="python, 基础")

        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button("✅ 添加", type="primary", use_container_width=True)
        with col2:
            canceled = st.form_submit_button("❌ 取消", use_container_width=True)

        if submitted and task_name:
            # 处理标签
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

            # 添加任务
            task_id = todo_manager.add_single_task(
                task_name=task_name,
                date=task_date.strftime("%Y-%m-%d"),
                estimated_time=estimated_time,
                difficulty=difficulty,
                priority=priority,
                tags=tag_list
            )

            if task_id:
                st.success(f"✅ 任务「{task_name}」已添加！")
                st.session_state['show_add_task_modal'] = False
                st.rerun()
            else:
                st.error("❌ 添加任务失败")

        if canceled:
            st.session_state['show_add_task_modal'] = False
            st.rerun()


def show_today_tasks(filter_status: str):
    """显示今日任务"""

    today = datetime.now().strftime("%Y-%m-%d")
    st.markdown(f"### 📅 {today} 的任务")

    tasks = todo_manager.get_today_tasks()

    # 应用状态过滤
    tasks = apply_status_filter(tasks, filter_status)

    if not tasks:
        st.info("今天没有任务，休息一下吧 😊")
        return

    # 显示任务
    for task in tasks:
        show_task_card(task)


def show_week_tasks(filter_status: str):
    """显示本周任务"""

    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    st.markdown(f"### 📅 本周任务 ({start_of_week.strftime('%Y-%m-%d')} ~ {end_of_week.strftime('%Y-%m-%d')})")

    tasks_by_date = todo_manager.get_tasks_by_date_range(
        start_of_week.strftime("%Y-%m-%d"),
        end_of_week.strftime("%Y-%m-%d")
    )

    if not tasks_by_date:
        st.info("本周没有任务")
        return

    # 按日期显示
    for date_str in sorted(tasks_by_date.keys()):
        st.markdown(f"#### {date_str}")
        tasks = apply_status_filter(tasks_by_date[date_str], filter_status)

        if tasks:
            for task in tasks:
                show_task_card(task)
        else:
            st.caption("没有任务")


def show_all_plans(filter_status: str):
    """显示所有计划"""

    st.markdown("### 📋 所有学习计划")

    plans = todo_manager.get_all_plans()

    if not plans:
        st.info("还没有学习计划，点击「📋 生成计划」创建一个吧！")
        return

    for plan in plans:
        with st.expander(f"📁 {plan['name']} ({len(plan.get('tasks', []))} 个任务)", expanded=False):
            st.caption(f"创建于: {plan.get('created_at', '')}")

            tasks = apply_status_filter(plan.get('tasks', []), filter_status)

            if not tasks:
                st.caption("没有匹配的任务")
            else:
                for task in tasks:
                    show_task_card(task, show_date=True)


def show_task_card(task: dict, show_date: bool = False):
    """显示任务卡片"""

    difficulty = task.get("difficulty", "medium")
    status = task.get("status", "pending")

    # 难度标记
    difficulty_emoji = {
        "simple": "🟢",
        "medium": "🟡",
        "hard": "🔴"
    }
    emoji = difficulty_emoji.get(difficulty, "🟡")

    # 状态标记
    status_emoji = {
        "pending": "⏳",
        "completed": "✅",
        "skipped": "⏭️"
    }
    status_icon = status_emoji.get(status, "⏳")

    # 创建任务卡片
    card_class = f"task-{difficulty}"

    with st.container():
        col1, col2, col3 = st.columns([6, 2, 2])

        with col1:
            task_title = f"{status_icon} {emoji} {task['task']}"
            if show_date:
                task_title += f" ({task['date']})"
            st.markdown(f"**{task_title}**")

            # 显示标签
            if task.get('tags'):
                tags_str = " ".join([f"`{tag}`" for tag in task['tags']])
                st.caption(tags_str)

            # 显示推荐资源
            resources = library_manager.get_resources_for_task(task['id'])
            if resources:
                st.caption(f"💡 推荐资源: {len(resources)} 个")

        with col2:
            st.caption(f"⏱️ {task.get('estimated_time', 60)} 分钟")

        with col3:
            if status == "pending":
                if st.button("✅ 完成", key=f"complete_{task['id']}", use_container_width=True):
                    if todo_manager.complete_task(task['id']):
                        st.success("任务已完成！")
                        st.rerun()

                if st.button("⏭️ 跳过", key=f"skip_{task['id']}", use_container_width=True):
                    if todo_manager.skip_task(task['id']):
                        st.info("任务已跳过到明天")
                        st.rerun()
            elif status == "completed":
                st.success("已完成")


def apply_status_filter(tasks: list, filter_status: str) -> list:
    """应用状态过滤"""

    if filter_status == "全部":
        return tasks
    elif filter_status == "待完成":
        return [t for t in tasks if t['status'] == 'pending']
    elif filter_status == "已完成":
        return [t for t in tasks if t['status'] == 'completed']
    elif filter_status == "已跳过":
        return [t for t in tasks if t['status'] == 'skipped']

    return tasks
