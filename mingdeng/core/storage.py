"""
JSON 存储层
负责任务、资源库等数据的持久化
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class Storage:
    """JSON 存储管理器"""

    def __init__(self, data_dir: str = "data"):
        """
        初始化存储管理器

        Args:
            data_dir: 数据文件目录
        """
        self.data_dir = Path(data_dir)
        self.todos_file = self.data_dir / "todos.json"
        self.library_file = self.data_dir / "library.json"
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "backups").mkdir(exist_ok=True)
        (self.data_dir / "memory").mkdir(exist_ok=True)

    # ===== 任务数据管理 =====

    def load_todos(self) -> Dict[str, Any]:
        """
        加载任务数据

        Returns:
            任务数据字典
        """
        if not self.todos_file.exists():
            return self._get_default_todos()

        try:
            with open(self.todos_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"加载任务数据失败: {e}")
            return self._get_default_todos()

    def save_todos(self, data: Dict[str, Any]) -> bool:
        """
        保存任务数据

        Args:
            data: 任务数据字典

        Returns:
            是否保存成功
        """
        try:
            with open(self.todos_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存任务数据失败: {e}")
            return False

    def _get_default_todos(self) -> Dict[str, Any]:
        """
        获取默认任务数据结构

        Returns:
            默认任务数据字典
        """
        return {
            "plans": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

    # ===== 资源库数据管理 =====

    def load_library(self) -> Dict[str, Any]:
        """
        加载资源库数据

        Returns:
            资源库数据字典
        """
        if not self.library_file.exists():
            return self._get_default_library()

        try:
            with open(self.library_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"加载资源库数据失败: {e}")
            return self._get_default_library()

    def save_library(self, data: Dict[str, Any]) -> bool:
        """
        保存资源库数据

        Args:
            data: 资源库数据字典

        Returns:
            是否保存成功
        """
        try:
            with open(self.library_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存资源库数据失败: {e}")
            return False

    def _get_default_library(self) -> Dict[str, Any]:
        """
        获取默认资源库数据结构

        Returns:
            默认资源库数据字典
        """
        return {
            "resources": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

    # ===== 计划管理 =====

    def get_all_plans(self) -> List[Dict[str, Any]]:
        """
        获取所有学习计划

        Returns:
            计划列表
        """
        data = self.load_todos()
        return data.get("plans", [])

    def get_plan_by_id(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取计划

        Args:
            plan_id: 计划 ID

        Returns:
            计划字典，如果不存在则返回 None
        """
        plans = self.get_all_plans()
        for plan in plans:
            if plan.get("id") == plan_id:
                return plan
        return None

    def add_plan(self, plan: Dict[str, Any]) -> bool:
        """
        添加新计划

        Args:
            plan: 计划字典

        Returns:
            是否添加成功
        """
        data = self.load_todos()
        if "id" not in plan:
            plan["id"] = str(uuid.uuid4())
        if "created_at" not in plan:
            plan["created_at"] = datetime.now().isoformat()

        data["plans"].append(plan)
        data["last_updated"] = datetime.now().isoformat()
        return self.save_todos(data)

    def update_plan(self, plan_id: str, updated_plan: Dict[str, Any]) -> bool:
        """
        更新计划

        Args:
            plan_id: 计划 ID
            updated_plan: 更新后的计划字典

        Returns:
            是否更新成功
        """
        data = self.load_todos()
        plans = data.get("plans", [])

        for i, plan in enumerate(plans):
            if plan.get("id") == plan_id:
                updated_plan["id"] = plan_id
                updated_plan["updated_at"] = datetime.now().isoformat()
                plans[i] = updated_plan
                data["last_updated"] = datetime.now().isoformat()
                return self.save_todos(data)

        return False

    def delete_plan(self, plan_id: str) -> bool:
        """
        删除计划

        Args:
            plan_id: 计划 ID

        Returns:
            是否删除成功
        """
        data = self.load_todos()
        plans = data.get("plans", [])

        new_plans = [p for p in plans if p.get("id") != plan_id]
        if len(new_plans) == len(plans):
            return False

        data["plans"] = new_plans
        data["last_updated"] = datetime.now().isoformat()
        return self.save_todos(data)

    # ===== 任务管理 =====

    def get_tasks_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        获取指定日期的所有任务

        Args:
            date: 日期字符串 (YYYY-MM-DD)

        Returns:
            任务列表
        """
        all_tasks = []
        plans = self.get_all_plans()

        for plan in plans:
            tasks = plan.get("tasks", [])
            for task in tasks:
                if task.get("date") == date:
                    task["plan_id"] = plan.get("id")
                    task["plan_name"] = plan.get("name")
                    all_tasks.append(task)

        return all_tasks

    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取任务

        Args:
            task_id: 任务 ID

        Returns:
            任务字典，如果不存在则返回 None
        """
        plans = self.get_all_plans()
        for plan in plans:
            tasks = plan.get("tasks", [])
            for task in tasks:
                if task.get("id") == task_id:
                    task["plan_id"] = plan.get("id")
                    task["plan_name"] = plan.get("name")
                    return task
        return None

    def update_task(self, task_id: str, updated_task: Dict[str, Any]) -> bool:
        """
        更新任务

        Args:
            task_id: 任务 ID
            updated_task: 更新后的任务字典

        Returns:
            是否更新成功
        """
        data = self.load_todos()
        plans = data.get("plans", [])

        for plan in plans:
            tasks = plan.get("tasks", [])
            for i, task in enumerate(tasks):
                if task.get("id") == task_id:
                    updated_task["id"] = task_id
                    updated_task["updated_at"] = datetime.now().isoformat()
                    tasks[i] = updated_task
                    data["last_updated"] = datetime.now().isoformat()
                    return self.save_todos(data)

        return False

    # ===== 资源管理 =====

    def get_all_resources(self) -> List[Dict[str, Any]]:
        """
        获取所有资源

        Returns:
            资源列表
        """
        data = self.load_library()
        return data.get("resources", [])

    def add_resource(self, resource: Dict[str, Any]) -> bool:
        """
        添加新资源

        Args:
            resource: 资源字典

        Returns:
            是否添加成功
        """
        data = self.load_library()
        if "id" not in resource:
            resource["id"] = str(uuid.uuid4())
        if "captured_at" not in resource:
            resource["captured_at"] = datetime.now().isoformat()
        if "status" not in resource:
            resource["status"] = "unread"
        if "linked_tasks" not in resource:
            resource["linked_tasks"] = []

        data["resources"].append(resource)
        data["last_updated"] = datetime.now().isoformat()
        return self.save_library(data)

    def update_resource(self, resource_id: str, updated_resource: Dict[str, Any]) -> bool:
        """
        更新资源

        Args:
            resource_id: 资源 ID
            updated_resource: 更新后的资源字典

        Returns:
            是否更新成功
        """
        data = self.load_library()
        resources = data.get("resources", [])

        for i, resource in enumerate(resources):
            if resource.get("id") == resource_id:
                updated_resource["id"] = resource_id
                updated_resource["updated_at"] = datetime.now().isoformat()
                resources[i] = updated_resource
                data["last_updated"] = datetime.now().isoformat()
                return self.save_library(data)

        return False

    def delete_resource(self, resource_id: str) -> bool:
        """
        删除资源

        Args:
            resource_id: 资源 ID

        Returns:
            是否删除成功
        """
        data = self.load_library()
        resources = data.get("resources", [])

        new_resources = [r for r in resources if r.get("id") != resource_id]
        if len(new_resources) == len(resources):
            return False

        data["resources"] = new_resources
        data["last_updated"] = datetime.now().isoformat()
        return self.save_library(data)


# 创建全局存储管理器实例
storage = Storage()
