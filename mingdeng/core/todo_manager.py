"""
任务管理 API
提供任务的增删改查、状态管理等功能
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
from .storage import storage
from .backup_manager import backup_manager


class TodoManager:
    """任务管理器"""

    def __init__(self):
        """初始化任务管理器"""
        pass

    def get_today_tasks(self) -> List[Dict[str, Any]]:
        """
        获取今日任务

        Returns:
            今日任务列表
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return storage.get_tasks_by_date(today)

    def get_tasks_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取日期范围内的任务

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            日期 -> 任务列表的字典
        """
        result = {}
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            tasks = storage.get_tasks_by_date(date_str)
            if tasks:
                result[date_str] = tasks
            current += timedelta(days=1)

        return result

    def add_single_task(
        self,
        task_name: str,
        date: str,
        plan_id: Optional[str] = None,
        estimated_time: int = 60,
        difficulty: str = "medium",
        priority: str = "medium",
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        添加单个任务

        Args:
            task_name: 任务名称
            date: 日期 (YYYY-MM-DD)
            plan_id: 所属计划 ID（可选）
            estimated_time: 预计时长（分钟）
            difficulty: 难度（simple/medium/hard）
            priority: 优先级（high/medium/low）
            tags: 标签列表

        Returns:
            任务 ID，如果失败返回 None
        """
        task = {
            "id": str(uuid.uuid4()),
            "task": task_name,
            "date": date,
            "estimated_time": estimated_time,
            "difficulty": difficulty,
            "priority": priority,
            "tags": tags or [],
            "status": "pending",
            "completed_at": None,
            "notes": "",
            "created_at": datetime.now().isoformat()
        }

        # 如果指定了计划 ID，添加到该计划
        if plan_id:
            plan = storage.get_plan_by_id(plan_id)
            if plan:
                plan["tasks"].append(task)
                if storage.update_plan(plan_id, plan):
                    return task["id"]
            return None
        else:
            # 如果没有指定计划，创建一个"快速任务"计划
            quick_plan_id = self._get_or_create_quick_plan()
            plan = storage.get_plan_by_id(quick_plan_id)
            plan["tasks"].append(task)
            if storage.update_plan(quick_plan_id, plan):
                return task["id"]
            return None

    def _get_or_create_quick_plan(self) -> str:
        """
        获取或创建"快速任务"计划

        Returns:
            快速任务计划的 ID
        """
        plans = storage.get_all_plans()
        for plan in plans:
            if plan.get("name") == "快速任务":
                return plan["id"]

        # 如果不存在，创建一个
        quick_plan = {
            "id": str(uuid.uuid4()),
            "name": "快速任务",
            "created_at": datetime.now().isoformat(),
            "tasks": []
        }
        storage.add_plan(quick_plan)
        return quick_plan["id"]

    def complete_task(self, task_id: str, notes: str = "") -> bool:
        """
        完成任务

        Args:
            task_id: 任务 ID
            notes: 完成笔记

        Returns:
            是否成功
        """
        task = storage.get_task_by_id(task_id)
        if not task:
            return False

        task["status"] = "completed"
        task["completed_at"] = datetime.now().isoformat()
        if notes:
            task["notes"] = notes

        return storage.update_task(task_id, task)

    def skip_task(self, task_id: str, new_date: Optional[str] = None) -> bool:
        """
        跳过任务（自动重排到下一天或指定日期）

        Args:
            task_id: 任务 ID
            new_date: 新日期（可选，默认为明天）

        Returns:
            是否成功
        """
        task = storage.get_task_by_id(task_id)
        if not task:
            return False

        task["status"] = "skipped"

        # 如果没有指定新日期，默认移到明天
        if not new_date:
            tomorrow = datetime.now() + timedelta(days=1)
            new_date = tomorrow.strftime("%Y-%m-%d")

        task["date"] = new_date

        return storage.update_task(task_id, task)

    def move_task(self, task_id: str, new_date: str) -> bool:
        """
        移动任务到指定日期

        Args:
            task_id: 任务 ID
            new_date: 新日期 (YYYY-MM-DD)

        Returns:
            是否成功
        """
        task = storage.get_task_by_id(task_id)
        if not task:
            return False

        task["date"] = new_date
        return storage.update_task(task_id, task)

    def update_task_difficulty(self, task_id: str, difficulty: str) -> bool:
        """
        更新任务难度

        Args:
            task_id: 任务 ID
            difficulty: 难度（simple/medium/hard）

        Returns:
            是否成功
        """
        task = storage.get_task_by_id(task_id)
        if not task:
            return False

        task["difficulty"] = difficulty
        return storage.update_task(task_id, task)

    def get_task_stats(self, date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """
        获取任务统计信息

        Args:
            date_range: 日期范围 (start_date, end_date)，默认为本周

        Returns:
            统计信息字典
        """
        if not date_range:
            # 默认统计本周
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            start_date = start_of_week.strftime("%Y-%m-%d")
            end_date = end_of_week.strftime("%Y-%m-%d")
        else:
            start_date, end_date = date_range

        tasks_by_date = self.get_tasks_by_date_range(start_date, end_date)
        all_tasks = []
        for tasks in tasks_by_date.values():
            all_tasks.extend(tasks)

        # 统计信息
        stats = {
            "total": len(all_tasks),
            "completed": len([t for t in all_tasks if t["status"] == "completed"]),
            "pending": len([t for t in all_tasks if t["status"] == "pending"]),
            "skipped": len([t for t in all_tasks if t["status"] == "skipped"]),
            "by_difficulty": {
                "simple": len([t for t in all_tasks if t["difficulty"] == "simple"]),
                "medium": len([t for t in all_tasks if t["difficulty"] == "medium"]),
                "hard": len([t for t in all_tasks if t["difficulty"] == "hard"])
            },
            "completed_by_difficulty": {
                "simple": len([t for t in all_tasks if t["status"] == "completed" and t["difficulty"] == "simple"]),
                "medium": len([t for t in all_tasks if t["status"] == "completed" and t["difficulty"] == "medium"]),
                "hard": len([t for t in all_tasks if t["status"] == "completed" and t["difficulty"] == "hard"])
            },
            "completion_rate": 0
        }

        if stats["total"] > 0:
            stats["completion_rate"] = round(stats["completed"] / stats["total"] * 100, 1)

        return stats

    def get_all_plans(self) -> List[Dict[str, Any]]:
        """
        获取所有学习计划

        Returns:
            计划列表
        """
        return storage.get_all_plans()

    def delete_plan(self, plan_id: str) -> bool:
        """
        删除学习计划

        Args:
            plan_id: 计划 ID

        Returns:
            是否成功
        """
        # 删除前先备份
        backup_manager.create_backup(f"删除计划前备份")
        return storage.delete_plan(plan_id)

    def bulk_move_tasks(
        self,
        plan_id: str,
        days_offset: int
    ) -> bool:
        """
        批量移动计划中的所有任务

        Args:
            plan_id: 计划 ID
            days_offset: 天数偏移（正数为延后，负数为提前）

        Returns:
            是否成功
        """
        plan = storage.get_plan_by_id(plan_id)
        if not plan:
            return False

        # 更新所有任务的日期
        for task in plan.get("tasks", []):
            old_date = datetime.strptime(task["date"], "%Y-%m-%d")
            new_date = old_date + timedelta(days=days_offset)
            task["date"] = new_date.strftime("%Y-%m-%d")

        # 备份后保存
        backup_manager.create_backup(f"批量调整计划「{plan['name']}」时间")
        return storage.update_plan(plan_id, plan)


# 创建全局任务管理器实例
todo_manager = TodoManager()
