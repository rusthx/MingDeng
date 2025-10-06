"""
统计页面
展示学习进度和统计信息
"""

import streamlit as st
from datetime import datetime, timedelta
from core.todo_manager import todo_manager
import plotly.graph_objects as go


def show():
    """显示统计页面"""

    st.markdown("## 📊 学习统计")
    st.markdown("---")

    # 时间范围选择
    col1, col2 = st.columns([3, 1])

    with col1:
        time_range = st.selectbox(
            "时间范围",
            ["本周", "本月", "最近 30 天", "全部"],
            index=0
        )

    with col2:
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()

    # 计算时间范围
    today = datetime.now()
    if time_range == "本周":
        start_of_week = today - timedelta(days=today.weekday())
        start_date = start_of_week.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif time_range == "本月":
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif time_range == "最近 30 天":
        start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    else:
        # 全部：从一年前到今天
        start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

    st.markdown("---")

    # 获取统计数据
    stats = todo_manager.get_task_stats((start_date, end_date))

    # 概览指标
    st.markdown("### 📈 概览")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("总任务数", f"{stats['total']} 个")

    with col2:
        st.metric(
            "已完成",
            f"{stats['completed']} 个",
            delta=f"{stats['completion_rate']}%"
        )

    with col3:
        st.metric("待完成", f"{stats['pending']} 个")

    with col4:
        st.metric("已跳过", f"{stats['skipped']} 个")

    st.markdown("---")

    # 难度分布
    st.markdown("### 📊 任务难度分布")

    col1, col2 = st.columns(2)

    with col1:
        # 总任务难度分布
        difficulty_data = stats['by_difficulty']

        fig_difficulty = go.Figure(data=[
            go.Pie(
                labels=['🟢 简单', '🟡 中等', '🔴 困难'],
                values=[
                    difficulty_data['simple'],
                    difficulty_data['medium'],
                    difficulty_data['hard']
                ],
                marker=dict(colors=['#4CAF50', '#FFC107', '#F44336']),
                hole=0.3
            )
        ])

        fig_difficulty.update_layout(
            title="任务总量按难度分布",
            height=300
        )

        st.plotly_chart(fig_difficulty, use_container_width=True)

    with col2:
        # 已完成任务难度分布
        completed_difficulty = stats['completed_by_difficulty']

        fig_completed = go.Figure(data=[
            go.Pie(
                labels=['🟢 简单', '🟡 中等', '🔴 困难'],
                values=[
                    completed_difficulty['simple'],
                    completed_difficulty['medium'],
                    completed_difficulty['hard']
                ],
                marker=dict(colors=['#4CAF50', '#FFC107', '#F44336']),
                hole=0.3
            )
        ])

        fig_completed.update_layout(
            title="已完成任务按难度分布",
            height=300
        )

        st.plotly_chart(fig_completed, use_container_width=True)

    st.markdown("---")

    # 完成率详细
    st.markdown("### 🎯 完成率详细")

    col1, col2, col3 = st.columns(3)

    with col1:
        simple_total = difficulty_data['simple']
        simple_completed = completed_difficulty['simple']
        simple_rate = round(simple_completed / simple_total * 100, 1) if simple_total > 0 else 0
        st.metric(
            "🟢 简单任务完成率",
            f"{simple_rate}%",
            delta=f"{simple_completed}/{simple_total}"
        )

    with col2:
        medium_total = difficulty_data['medium']
        medium_completed = completed_difficulty['medium']
        medium_rate = round(medium_completed / medium_total * 100, 1) if medium_total > 0 else 0
        st.metric(
            "🟡 中等任务完成率",
            f"{medium_rate}%",
            delta=f"{medium_completed}/{medium_total}"
        )

    with col3:
        hard_total = difficulty_data['hard']
        hard_completed = completed_difficulty['hard']
        hard_rate = round(hard_completed / hard_total * 100, 1) if hard_total > 0 else 0
        st.metric(
            "🔴 困难任务完成率",
            f"{hard_rate}%",
            delta=f"{hard_completed}/{hard_total}"
        )

    st.markdown("---")

    # 学习计划列表
    st.markdown("### 📋 学习计划")

    plans = todo_manager.get_all_plans()

    if not plans:
        st.info("还没有学习计划")
    else:
        for plan in plans:
            tasks = plan.get('tasks', [])
            completed_tasks = len([t for t in tasks if t['status'] == 'completed'])
            total_tasks = len(tasks)
            completion_rate = round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0

            with st.expander(f"📁 {plan['name']}", expanded=False):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("总任务数", f"{total_tasks} 个")

                with col2:
                    st.metric("已完成", f"{completed_tasks} 个")

                with col3:
                    st.metric("完成率", f"{completion_rate}%")

                # 进度条
                st.progress(completion_rate / 100)

    st.markdown("---")

    # AI 学习总结（占位符）
    st.markdown("### 🤖 AI 学习总结")
    st.info("AI 学习总结功能即将推出...")
