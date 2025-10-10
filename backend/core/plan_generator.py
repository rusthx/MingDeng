"""
Plan Generator Module
Handles AI-powered learning plan generation
"""

from typing import Dict, Any
from datetime import datetime, timedelta, date
from .ai import ai_client
from .todo_manager import todo_manager


class PlanGenerator:
    """Learning plan generator using AI"""

    def __init__(self):
        self.ai_client = ai_client
        self.todo_manager = todo_manager

    async def generate_plan(self, user_input: str, start_date: str = None) -> Dict[str, Any]:
        """
        Generate a learning plan from user input

        Args:
            user_input: User's learning goals/topics
            start_date: Optional start date (defaults to today)

        Returns:
            Generated plan with tasks
        """
        # Get AI-generated plan structure
        plan_data = await self.ai_client.generate_plan(user_input)

        # Adjust dates if start_date is provided
        if start_date:
            plan_data = self._adjust_plan_dates(plan_data, start_date)
        else:
            # Default: start from today
            plan_data = self._adjust_plan_dates(plan_data, datetime.now().date().isoformat())

        # Create the plan in storage
        created_plan = self.todo_manager.create_plan(
            name=plan_data.get("plan_name", "新学习计划"),
            tasks=plan_data.get("tasks", [])
        )

        return {
            "success": True,
            "plan": created_plan,
            "message": f"成功生成学习计划：{created_plan['name']}，包含 {len(created_plan['tasks'])} 个任务"
        }

    def _adjust_plan_dates(self, plan_data: Dict[str, Any], start_date: str) -> Dict[str, Any]:
        """
        Adjust task dates to start from a specific date

        Args:
            plan_data: Plan data from AI
            start_date: Start date (ISO format)

        Returns:
            Plan data with adjusted dates
        """
        try:
            base_date = datetime.fromisoformat(start_date).date()
        except:
            base_date = datetime.now().date()

        tasks = plan_data.get("tasks", [])

        # If tasks already have dates, calculate offset
        if tasks and "date" in tasks[0]:
            try:
                first_task_date = datetime.fromisoformat(tasks[0]["date"]).date()
                offset = (base_date - first_task_date).days

                # Apply offset to all tasks
                for task in tasks:
                    if "date" in task:
                        task_date = datetime.fromisoformat(task["date"]).date()
                        new_date = task_date + timedelta(days=offset)
                        task["date"] = new_date.isoformat()
            except:
                # If date parsing fails, use sequential dates
                self._assign_sequential_dates(tasks, base_date)
        else:
            # No dates provided, assign sequential dates
            self._assign_sequential_dates(tasks, base_date)

        return plan_data

    def _assign_sequential_dates(self, tasks: list, start_date: date):
        """
        Assign sequential dates to tasks

        Args:
            tasks: List of tasks
            start_date: Starting date
        """
        current_date = start_date
        daily_time = 0  # Track daily time in minutes

        for task in tasks:
            estimated_time = task.get("estimated_time", 60)

            # If adding this task exceeds 4 hours, move to next day
            if daily_time + estimated_time > 240:  # 4 hours = 240 minutes
                current_date += timedelta(days=1)
                daily_time = 0

            task["date"] = current_date.isoformat()
            daily_time += estimated_time

    async def regenerate_plan(self, plan_id: str, modifications: str) -> Dict[str, Any]:
        """
        Regenerate a plan with modifications

        Args:
            plan_id: Existing plan ID
            modifications: User's modification requests

        Returns:
            Updated plan
        """
        # Get existing plan
        existing_plan = self.todo_manager.get_plan(plan_id)
        if not existing_plan:
            return {
                "success": False,
                "message": "计划不存在"
            }

        # Generate prompt for modification
        prompt = f"""
现有学习计划：{existing_plan['name']}
包含 {len(existing_plan['tasks'])} 个任务

用户的修改要求：
{modifications}

请根据用户要求调整学习计划。保持原有任务的合理部分，根据要求进行调整。

输出 JSON 格式（与原格式相同）：
{{
  "plan_name": "调整后的计划名称",
  "tasks": [...]
}}
"""

        # Get AI-generated modifications
        plan_data = await self.ai_client.generate_plan(prompt)

        # Update the existing plan
        existing_plan["name"] = plan_data.get("plan_name", existing_plan["name"])
        existing_plan["tasks"] = plan_data.get("tasks", existing_plan["tasks"])

        # Ensure all tasks have IDs
        for task in existing_plan["tasks"]:
            if "id" not in task:
                import uuid
                task["id"] = str(uuid.uuid4())

        # Save updated plan
        self.todo_manager.update_plan(plan_id, existing_plan)

        return {
            "success": True,
            "plan": existing_plan,
            "message": "计划已更新"
        }


# Global plan generator instance
plan_generator = PlanGenerator()
