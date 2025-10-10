"""
Todo Manager Module
Handles task and plan management operations
"""

import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from .storage import todo_storage


class TodoManager:
    """Task and plan management"""

    def __init__(self):
        self.storage = todo_storage

    def create_plan(self, name: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a new learning plan

        Args:
            name: Plan name
            tasks: List of tasks

        Returns:
            Created plan
        """
        # Generate unique IDs for plan and tasks
        plan_id = str(uuid.uuid4())
        for task in tasks:
            if "id" not in task:
                task["id"] = str(uuid.uuid4())
            # Set default values
            task.setdefault("status", "pending")
            task.setdefault("completed_at", None)
            task.setdefault("notes", "")
            task.setdefault("priority", "medium")
            task.setdefault("tags", [])

        plan = {
            "id": plan_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "tasks": tasks
        }

        self.storage.add_plan(plan)
        return plan

    def get_all_plans(self) -> List[Dict[str, Any]]:
        """Get all plans"""
        return self.storage.get_plans()

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan by ID"""
        return self.storage.get_plan_by_id(plan_id)

    def update_plan(self, plan_id: str, updates: Dict[str, Any]) -> bool:
        """Update plan"""
        plan = self.storage.get_plan_by_id(plan_id)
        if not plan:
            return False

        plan.update(updates)
        return self.storage.update_plan(plan_id, plan)

    def delete_plan(self, plan_id: str) -> bool:
        """Delete plan"""
        return self.storage.delete_plan(plan_id)

    def get_today_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks for today"""
        today = date.today().isoformat()
        return self.storage.get_tasks_by_date(today)

    def get_tasks_by_date(self, task_date: str) -> List[Dict[str, Any]]:
        """Get tasks for specific date"""
        return self.storage.get_tasks_by_date(task_date)

    def create_task(self, plan_id: str, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new task in a plan

        Args:
            plan_id: Plan ID
            task: Task data

        Returns:
            Created task or None
        """
        plan = self.storage.get_plan_by_id(plan_id)
        if not plan:
            return None

        # Generate task ID and set defaults
        task["id"] = str(uuid.uuid4())
        task.setdefault("status", "pending")
        task.setdefault("completed_at", None)
        task.setdefault("notes", "")
        task.setdefault("priority", "medium")
        task.setdefault("tags", [])

        plan["tasks"].append(task)
        self.storage.update_plan(plan_id, plan)

        return task

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a task

        Args:
            task_id: Task ID
            updates: Fields to update

        Returns:
            Success status
        """
        # Handle completion
        if updates.get("status") == "completed" and "completed_at" not in updates:
            updates["completed_at"] = datetime.now().isoformat()
        elif updates.get("status") == "pending":
            updates["completed_at"] = None

        return self.storage.update_task(task_id, updates)

    def complete_task(self, task_id: str) -> bool:
        """Mark task as completed"""
        return self.update_task(task_id, {
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        })

    def uncomplete_task(self, task_id: str) -> bool:
        """Mark task as pending"""
        return self.update_task(task_id, {
            "status": "pending",
            "completed_at": None
        })

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from all plans

        Args:
            task_id: Task ID

        Returns:
            Success status
        """
        plans = self.storage.get_plans()
        for plan in plans:
            original_count = len(plan["tasks"])
            plan["tasks"] = [t for t in plan["tasks"] if t["id"] != task_id]
            if len(plan["tasks"]) < original_count:
                self.storage.update_plan(plan["id"], plan)
                return True
        return False

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks from all plans"""
        plans = self.storage.get_plans()
        all_tasks = []
        for plan in plans:
            all_tasks.extend(plan.get("tasks", []))
        return all_tasks

    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        all_tasks = self.get_all_tasks()
        for task in all_tasks:
            if task["id"] == task_id:
                return task
        return None

    def get_stats(self) -> Dict[str, Any]:
        """
        Get learning statistics

        Returns:
            Statistics data
        """
        all_tasks = self.get_all_tasks()

        stats = {
            "total_tasks": len(all_tasks),
            "completed": 0,
            "pending": 0,
            "skipped": 0,
            "by_difficulty": {
                "simple": {"total": 0, "completed": 0},
                "medium": {"total": 0, "completed": 0},
                "hard": {"total": 0, "completed": 0}
            },
            "completion_rate": 0.0
        }

        for task in all_tasks:
            status = task.get("status", "pending")
            difficulty = task.get("difficulty", "medium")

            # Count by status
            if status == "completed":
                stats["completed"] += 1
            elif status == "skipped":
                stats["skipped"] += 1
            else:
                stats["pending"] += 1

            # Count by difficulty
            if difficulty in stats["by_difficulty"]:
                stats["by_difficulty"][difficulty]["total"] += 1
                if status == "completed":
                    stats["by_difficulty"][difficulty]["completed"] += 1

        # Calculate completion rate
        if stats["total_tasks"] > 0:
            stats["completion_rate"] = round(
                (stats["completed"] / stats["total_tasks"]) * 100, 1
            )

        return stats


# Global todo manager instance
todo_manager = TodoManager()
