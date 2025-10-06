"""
学习计划生成 API
使用 AI 批量生成学习计划
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
from .ai import ai_client
from .storage import storage
from .backup_manager import backup_manager


class PlanGenerator:
    """学习计划生成器"""

    # AI Prompt 模板
    PLAN_GENERATION_PROMPT = """你是 MingDeng 学习规划助手。用户想学习以下内容，请帮助拆解为可执行的学习计划。

用户输入：
{user_input}

学习模式：{learning_mode}

要求：
1. 分析依赖关系：识别哪些是基础知识，必须先学
2. 拆解为具体任务：每个任务 15min-3h，可操作
3. 评估难度和时长：简单/中等/困难
4. 智能排布时间：
   - 基础任务优先
   - 理论+实践交替
   - 每日总时长 2-4 小时
   - 高难度任务分散
   - 如果是「交叉学习」模式，将不同主题的任务交叉安排，避免连续学习同一主题
   - 如果是「集中攻坚」模式，同一主题的任务集中安排，便于深入学习
5. 建议 2-4 周完成
6. 从今天（{today}）开始安排

输出 JSON 格式：
{{
  "plan_name": "学习计划名称",
  "total_weeks": 3,
  "total_tasks": 18,
  "tasks": [
    {{
      "task": "任务描述（具体可执行）",
      "date": "2025-10-08",
      "estimated_time": 90,
      "difficulty": "simple|medium|hard",
      "priority": "high|medium|low",
      "tags": ["标签1", "标签2"],
      "prerequisites": []
    }}
  ]
}}

只返回 JSON，不要其他文字。"""

    def __init__(self):
        """初始化计划生成器"""
        pass

    def generate_plan(
        self,
        user_input: str,
        learning_mode: str = "交叉学习",
        start_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        生成学习计划

        Args:
            user_input: 用户输入的学习内容
            learning_mode: 学习模式（"集中攻坚" 或 "交叉学习"）
            start_date: 开始日期（可选，默认为今天）

        Returns:
            生成的计划字典，如果失败返回 None
        """
        if not ai_client.is_configured():
            raise ValueError("AI 客户端未配置，请先配置 API")

        # 确定开始日期
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")

        # 构建 Prompt
        prompt = self.PLAN_GENERATION_PROMPT.format(
            user_input=user_input,
            learning_mode=learning_mode,
            today=start_date
        )

        try:
            # 调用 AI 生成计划
            plan_data = ai_client.generate_json(
                prompt=prompt,
                temperature=0.7
            )

            if not plan_data:
                return None

            # 验证和处理生成的计划
            plan = self._process_generated_plan(plan_data, start_date)
            return plan

        except Exception as e:
            print(f"生成计划失败: {e}")
            return None

    def _process_generated_plan(
        self,
        plan_data: Dict[str, Any],
        start_date: str
    ) -> Dict[str, Any]:
        """
        处理 AI 生成的计划数据

        Args:
            plan_data: AI 生成的计划数据
            start_date: 开始日期

        Returns:
            处理后的计划字典
        """
        # 为计划添加 ID 和元数据
        plan = {
            "id": str(uuid.uuid4()),
            "name": plan_data.get("plan_name", "学习计划"),
            "created_at": datetime.now().isoformat(),
            "total_weeks": plan_data.get("total_weeks", 3),
            "total_tasks": plan_data.get("total_tasks", 0),
            "tasks": []
        }

        # 处理任务列表
        tasks = plan_data.get("tasks", [])
        for task_data in tasks:
            task = {
                "id": str(uuid.uuid4()),
                "task": task_data.get("task", ""),
                "date": task_data.get("date", start_date),
                "estimated_time": task_data.get("estimated_time", 60),
                "difficulty": task_data.get("difficulty", "medium"),
                "priority": task_data.get("priority", "medium"),
                "tags": task_data.get("tags", []),
                "status": "pending",
                "completed_at": None,
                "notes": "",
                "prerequisites": task_data.get("prerequisites", [])
            }
            plan["tasks"].append(task)

        plan["total_tasks"] = len(plan["tasks"])
        return plan

    def save_plan(self, plan: Dict[str, Any]) -> bool:
        """
        保存生成的计划

        Args:
            plan: 计划字典

        Returns:
            是否保存成功
        """
        # 保存前先备份
        backup_manager.create_backup(f"批量生成计划「{plan['name']}」")

        # 保存计划
        return storage.add_plan(plan)

    def preview_plan(
        self,
        user_input: str,
        learning_mode: str = "交叉学习"
    ) -> Optional[Dict[str, Any]]:
        """
        预览生成的计划（不保存）

        Args:
            user_input: 用户输入的学习内容
            learning_mode: 学习模式

        Returns:
            计划预览数据
        """
        plan = self.generate_plan(user_input, learning_mode)
        if not plan:
            return None

        # 构建预览信息
        preview = {
            "plan_name": plan["name"],
            "total_weeks": plan["total_weeks"],
            "total_tasks": plan["total_tasks"],
            "tasks_by_week": self._group_tasks_by_week(plan["tasks"]),
            "difficulty_distribution": self._get_difficulty_distribution(plan["tasks"]),
            "daily_time_estimate": self._get_daily_time_estimate(plan["tasks"])
        }

        return preview

    def _group_tasks_by_week(self, tasks: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """
        按周分组任务

        Args:
            tasks: 任务列表

        Returns:
            周 -> 任务列表的字典
        """
        tasks_by_week = {}

        if not tasks:
            return tasks_by_week

        # 找到最早的日期
        first_date = min(datetime.strptime(task["date"], "%Y-%m-%d") for task in tasks)

        for task in tasks:
            task_date = datetime.strptime(task["date"], "%Y-%m-%d")
            week_number = (task_date - first_date).days // 7 + 1

            if week_number not in tasks_by_week:
                tasks_by_week[week_number] = []

            tasks_by_week[week_number].append(task)

        return tasks_by_week

    def _get_difficulty_distribution(self, tasks: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        获取难度分布

        Args:
            tasks: 任务列表

        Returns:
            难度 -> 数量的字典
        """
        distribution = {
            "simple": 0,
            "medium": 0,
            "hard": 0
        }

        for task in tasks:
            difficulty = task.get("difficulty", "medium")
            if difficulty in distribution:
                distribution[difficulty] += 1

        return distribution

    def _get_daily_time_estimate(self, tasks: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        获取每日时长估算

        Args:
            tasks: 任务列表

        Returns:
            统计信息
        """
        tasks_by_date = {}
        for task in tasks:
            date = task["date"]
            if date not in tasks_by_date:
                tasks_by_date[date] = 0
            tasks_by_date[date] += task.get("estimated_time", 60)

        # 计算平均每日时长
        if tasks_by_date:
            daily_times = list(tasks_by_date.values())
            avg_time = sum(daily_times) / len(daily_times)
            max_time = max(daily_times)
            min_time = min(daily_times)
        else:
            avg_time = 0
            max_time = 0
            min_time = 0

        return {
            "avg_minutes": round(avg_time, 1),
            "max_minutes": max_time,
            "min_minutes": min_time
        }

    def adjust_plan_dates(
        self,
        plan_id: str,
        days_offset: int
    ) -> bool:
        """
        调整计划的所有任务日期

        Args:
            plan_id: 计划 ID
            days_offset: 天数偏移（正数延后，负数提前）

        Returns:
            是否成功
        """
        plan = storage.get_plan_by_id(plan_id)
        if not plan:
            return False

        # 调整所有任务的日期
        for task in plan.get("tasks", []):
            old_date = datetime.strptime(task["date"], "%Y-%m-%d")
            new_date = old_date + timedelta(days=days_offset)
            task["date"] = new_date.strftime("%Y-%m-%d")

        # 备份后保存
        backup_manager.create_backup(f"调整计划「{plan['name']}」日期")
        return storage.update_plan(plan_id, plan)


# 创建全局计划生成器实例
plan_generator = PlanGenerator()
