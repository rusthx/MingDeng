"""
资源库管理 API
提供资源的保存、检索、关联任务等功能
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import re
from .storage import storage
from .ai import ai_client


class LibraryManager:
    """资源库管理器"""

    def __init__(self):
        """初始化资源库管理器"""
        pass

    def capture_resource(
        self,
        content: str,
        description: str = "",
        auto_link: bool = True
    ) -> Optional[str]:
        """
        捕获资源

        Args:
            content: 资源内容（URL 或文本）
            description: 资源描述
            auto_link: 是否自动关联到相关任务

        Returns:
            资源 ID，如果失败返回 None
        """
        # 判断资源类型
        resource_type = self._detect_resource_type(content)

        resource = {
            "id": str(uuid.uuid4()),
            "content": content,
            "description": description,
            "type": resource_type,
            "captured_at": datetime.now().isoformat(),
            "linked_tasks": [],
            "status": "unread"
        }

        # 如果启用自动关联，尝试关联到相关任务
        if auto_link and ai_client.is_configured():
            linked_task_ids = self._auto_link_to_tasks(content, description)
            if linked_task_ids:
                resource["linked_tasks"] = linked_task_ids

        if storage.add_resource(resource):
            return resource["id"]
        return None

    def _detect_resource_type(self, content: str) -> str:
        """
        检测资源类型

        Args:
            content: 资源内容

        Returns:
            资源类型（video/article/paper/other）
        """
        # 检测 URL
        url_pattern = r'https?://[^\s]+'
        if re.match(url_pattern, content):
            # 判断是否为视频
            if any(domain in content.lower() for domain in ['youtube.com', 'youtu.be', 'bilibili.com', 'vimeo.com']):
                return "video"
            # 判断是否为论文
            if any(domain in content.lower() for domain in ['arxiv.org', 'scholar.google', 'doi.org']):
                return "paper"
            # 默认为文章
            return "article"

        # 如果不是 URL，判断为其他类型
        return "other"

    def _auto_link_to_tasks(
        self,
        content: str,
        description: str
    ) -> List[str]:
        """
        自动关联到相关任务

        Args:
            content: 资源内容
            description: 资源描述

        Returns:
            关联的任务 ID 列表
        """
        try:
            # 获取所有计划的任务
            plans = storage.get_all_plans()
            all_tasks = []
            for plan in plans:
                for task in plan.get("tasks", []):
                    task_copy = task.copy()
                    task_copy["plan_name"] = plan.get("name", "")
                    all_tasks.append(task_copy)

            if not all_tasks:
                return []

            # 构建任务列表字符串
            tasks_str = "\n".join([
                f"- {task['id']}: {task['task']} ({task.get('plan_name', '')})"
                for task in all_tasks[:20]  # 限制最多 20 个任务
            ])

            # 使用 AI 判断关联
            prompt = f"""用户保存了以下学习资源：
内容: {content}
描述: {description}

当前学习计划中的任务（最多显示 20 个）：
{tasks_str}

请判断这个资源最适合关联到哪个任务（如果有）。

输出 JSON 格式：
{{
  "linked_task_ids": ["task_id1", "task_id2"],  # 最多 2 个相关任务 ID，如果没有相关任务则为空数组
  "reason": "关联理由"
}}

只返回 JSON，不要其他文字。"""

            result = ai_client.generate_json(
                prompt=prompt,
                temperature=0.3
            )

            if result and "linked_task_ids" in result:
                return result["linked_task_ids"]

        except Exception as e:
            print(f"自动关联任务失败: {e}")

        return []

    def get_all_resources(
        self,
        filter_type: Optional[str] = None,
        filter_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取所有资源

        Args:
            filter_type: 过滤类型（video/article/paper/other）
            filter_status: 过滤状态（unread/reading/completed）

        Returns:
            资源列表
        """
        resources = storage.get_all_resources()

        # 应用过滤
        if filter_type:
            resources = [r for r in resources if r.get("type") == filter_type]
        if filter_status:
            resources = [r for r in resources if r.get("status") == filter_status]

        # 按捕获时间倒序排列
        resources.sort(key=lambda x: x.get("captured_at", ""), reverse=True)

        return resources

    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取资源

        Args:
            resource_id: 资源 ID

        Returns:
            资源字典，如果不存在返回 None
        """
        resources = storage.get_all_resources()
        for resource in resources:
            if resource.get("id") == resource_id:
                return resource
        return None

    def update_resource_status(
        self,
        resource_id: str,
        status: str
    ) -> bool:
        """
        更新资源状态

        Args:
            resource_id: 资源 ID
            status: 状态（unread/reading/completed）

        Returns:
            是否成功
        """
        resource = self.get_resource_by_id(resource_id)
        if not resource:
            return False

        resource["status"] = status
        return storage.update_resource(resource_id, resource)

    def link_resource_to_task(
        self,
        resource_id: str,
        task_id: str
    ) -> bool:
        """
        手动关联资源到任务

        Args:
            resource_id: 资源 ID
            task_id: 任务 ID

        Returns:
            是否成功
        """
        resource = self.get_resource_by_id(resource_id)
        if not resource:
            return False

        # 检查是否已关联
        linked_tasks = resource.get("linked_tasks", [])
        if task_id not in linked_tasks:
            linked_tasks.append(task_id)
            resource["linked_tasks"] = linked_tasks
            return storage.update_resource(resource_id, resource)

        return True

    def unlink_resource_from_task(
        self,
        resource_id: str,
        task_id: str
    ) -> bool:
        """
        取消资源与任务的关联

        Args:
            resource_id: 资源 ID
            task_id: 任务 ID

        Returns:
            是否成功
        """
        resource = self.get_resource_by_id(resource_id)
        if not resource:
            return False

        linked_tasks = resource.get("linked_tasks", [])
        if task_id in linked_tasks:
            linked_tasks.remove(task_id)
            resource["linked_tasks"] = linked_tasks
            return storage.update_resource(resource_id, resource)

        return True

    def get_resources_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        """
        获取与任务关联的资源

        Args:
            task_id: 任务 ID

        Returns:
            资源列表
        """
        all_resources = storage.get_all_resources()
        linked_resources = []

        for resource in all_resources:
            if task_id in resource.get("linked_tasks", []):
                linked_resources.append(resource)

        return linked_resources

    def delete_resource(self, resource_id: str) -> bool:
        """
        删除资源

        Args:
            resource_id: 资源 ID

        Returns:
            是否成功
        """
        return storage.delete_resource(resource_id)

    def search_resources(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索资源

        Args:
            query: 搜索关键词

        Returns:
            匹配的资源列表
        """
        all_resources = storage.get_all_resources()
        results = []

        query_lower = query.lower()
        for resource in all_resources:
            # 在内容和描述中搜索
            content = resource.get("content", "").lower()
            description = resource.get("description", "").lower()

            if query_lower in content or query_lower in description:
                results.append(resource)

        return results


# 创建全局资源库管理器实例
library_manager = LibraryManager()
