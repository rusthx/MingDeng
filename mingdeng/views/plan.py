"""
计划生成页面
使用 AI 批量生成学习计划
"""

import streamlit as st
from core.plan_generator import plan_generator
from datetime import datetime


def show():
    """显示计划生成页面"""

    st.markdown("## 📋 生成学习计划")
    st.markdown("---")

    st.info("""
    💡 **使用提示**:
    - 输入你想学习的内容，AI 会自动分析依赖关系
    - 拆解为每日可执行的小任务（15min-3h）
    - 理论+实践交叉安排，避免连续烧脑
    - 建议 2-4 周完成
    """)

    # 输入学习内容
    user_input = st.text_area(
        "📝 请输入你要学习的内容",
        height=200,
        placeholder="""例如：
我想学习 Agentic RL，需要掌握：
- Python 异步编程
- Inference (vLLM, SGLang)
- SFT (FSDP, LlamaFactory, DeepSpeed)
- RL (TRL, VeRL)

或者简单地输入：
学习前端开发：HTML, CSS, JavaScript, React
""",
        help="详细描述你想学习的内容，AI 会根据这些信息生成计划"
    )

    # 学习模式选择
    col1, col2 = st.columns(2)

    with col1:
        learning_mode = st.radio(
            "学习模式",
            ["🔄 交叉学习", "🎯 集中攻坚"],
            help="交叉学习：不同主题交叉安排，避免疲劳\n集中攻坚：同一主题集中学习，深入掌握"
        )

    with col2:
        start_date = st.date_input(
            "开始日期",
            value=datetime.now(),
            help="计划的开始日期"
        )

    st.markdown("---")

    # 生成计划按钮
    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("🚀 生成学习计划", type="primary", use_container_width=True):
            if not user_input or not user_input.strip():
                st.error("❌ 请输入学习内容")
            else:
                generate_plan(user_input, learning_mode, start_date)

    with col2:
        if st.button("🔄 重置", use_container_width=True):
            st.rerun()

    # 显示生成的计划（如果有）
    if 'generated_plan' in st.session_state:
        show_generated_plan()


def generate_plan(user_input: str, learning_mode: str, start_date):
    """生成学习计划"""

    mode = "交叉学习" if "交叉" in learning_mode else "集中攻坚"

    with st.spinner("🤔 AI 正在分析学习内容并生成计划..."):
        try:
            plan = plan_generator.generate_plan(
                user_input=user_input,
                learning_mode=mode,
                start_date=start_date.strftime("%Y-%m-%d")
            )

            if plan:
                st.session_state['generated_plan'] = plan
                st.success("✅ 学习计划生成成功！")
                st.rerun()
            else:
                st.error("❌ 生成计划失败，请检查 API 配置或重试")

        except Exception as e:
            st.error(f"❌ 生成计划时出错: {str(e)}")


def show_generated_plan():
    """显示生成的计划"""

    plan = st.session_state['generated_plan']

    st.markdown("---")
    st.markdown("## ✅ 生成的学习计划")

    # 计划概览
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("计划名称", plan['name'])
    with col2:
        st.metric("总任务数", f"{plan['total_tasks']} 个")
    with col3:
        st.metric("预计周数", f"{plan.get('total_weeks', 3)} 周")

    st.markdown("---")

    # 任务列表预览
    st.markdown("### 📅 任务列表")

    # 按周分组显示
    tasks = plan.get('tasks', [])

    if not tasks:
        st.warning("计划中没有任务")
        return

    # 按日期分组
    tasks_by_date = {}
    for task in tasks:
        date = task['date']
        if date not in tasks_by_date:
            tasks_by_date[date] = []
        tasks_by_date[date].append(task)

    # 显示任务
    for date in sorted(tasks_by_date.keys()):
        st.markdown(f"#### 📆 {date}")

        for task in tasks_by_date[date]:
            difficulty_emoji = {
                "simple": "🟢",
                "medium": "🟡",
                "hard": "🔴"
            }
            emoji = difficulty_emoji.get(task['difficulty'], "🟡")

            st.markdown(f"""
            - {emoji} **{task['task']}**
              ⏱️ {task['estimated_time']} 分钟 | 优先级: {task['priority']} | 标签: {', '.join(task.get('tags', []))}
            """)

    st.markdown("---")

    # 统计信息
    st.markdown("### 📊 计划统计")

    # 难度分布
    difficulty_dist = {
        "simple": len([t for t in tasks if t['difficulty'] == 'simple']),
        "medium": len([t for t in tasks if t['difficulty'] == 'medium']),
        "hard": len([t for t in tasks if t['difficulty'] == 'hard'])
    }

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟢 简单任务", f"{difficulty_dist['simple']} 个")
    with col2:
        st.metric("🟡 中等任务", f"{difficulty_dist['medium']} 个")
    with col3:
        st.metric("🔴 困难任务", f"{difficulty_dist['hard']} 个")

    # 每日时长估算
    daily_times = {}
    for task in tasks:
        date = task['date']
        daily_times[date] = daily_times.get(date, 0) + task.get('estimated_time', 60)

    if daily_times:
        avg_time = sum(daily_times.values()) / len(daily_times)
        max_time = max(daily_times.values())
        min_time = min(daily_times.values())

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("平均每日时长", f"{int(avg_time)} 分钟")
        with col2:
            st.metric("最长一天", f"{int(max_time)} 分钟")
        with col3:
            st.metric("最短一天", f"{int(min_time)} 分钟")

    st.markdown("---")

    # 保存或重新生成
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button("✅ 确认并保存计划", type="primary", use_container_width=True):
            if plan_generator.save_plan(plan):
                st.success("✅ 计划已保存！你可以在首页查看任务。")
                del st.session_state['generated_plan']
                st.balloons()
                st.rerun()
            else:
                st.error("❌ 保存计划失败")

    with col2:
        if st.button("🔄 重新生成", use_container_width=True):
            del st.session_state['generated_plan']
            st.rerun()

    with col3:
        if st.button("❌ 取消", use_container_width=True):
            del st.session_state['generated_plan']
            st.rerun()
