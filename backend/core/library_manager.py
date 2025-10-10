"""
Library Manager Module
Handles resource library management and auto-linking
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from .storage import library_storage
from .ai import ai_client
from .todo_manager import todo_manager


class LibraryManager:
    """Resource library management"""

    def __init__(self):
        self.storage = library_storage
        self.ai_client = ai_client
        self.todo_manager = todo_manager

    def create_resource(self, content: str, description: str = "",
                       resource_type: str = "other",
                       auto_link: bool = True) -> Dict[str, Any]:
        """
        Create a new resource

        Args:
            content: Resource URL or content
            description: Resource description
            resource_type: Type (video|article|paper|other)
            auto_link: Whether to auto-link to tasks

        Returns:
            Created resource
        """
        resource = {
            "id": str(uuid.uuid4()),
            "content": content,
            "description": description,
            "type": resource_type,
            "captured_at": datetime.now().isoformat(),
            "linked_tasks": [],
            "status": "unread"
        }

        # Auto-link to relevant tasks if enabled
        if auto_link:
            linked_task_id = self._auto_link_to_task(content, description)
            if linked_task_id:
                resource["linked_tasks"].append(linked_task_id)

        self.storage.add_resource(resource)
        return resource

    def _auto_link_to_task(self, content: str, description: str = "") -> Optional[str]:
        """
        Automatically link resource to a relevant task

        Args:
            content: Resource content
            description: Resource description

        Returns:
            Linked task ID or None
        """
        try:
            # Get all pending tasks
            all_tasks = self.todo_manager.get_all_tasks()
            pending_tasks = [t for t in all_tasks if t.get("status") == "pending"]

            if not pending_tasks:
                return None

            # Use AI to find relevant task
            resource_text = f"{content}\n{description}" if description else content

            # Simple keyword matching as fallback
            resource_lower = resource_text.lower()
            for task in pending_tasks:
                task_text = f"{task.get('task', '')} {' '.join(task.get('tags', []))}".lower()
                # Check for common keywords
                task_words = set(task_text.split())
                resource_words = set(resource_lower.split())
                common_words = task_words.intersection(resource_words)

                # If more than 2 common meaningful words, link
                meaningful_common = [w for w in common_words if len(w) > 3]
                if len(meaningful_common) >= 2:
                    return task["id"]

            return None
        except Exception as e:
            print(f"Error auto-linking resource: {e}")
            return None

    async def auto_link_with_ai(self, resource_id: str) -> Optional[str]:
        """
        Use AI to auto-link a resource to tasks

        Args:
            resource_id: Resource ID

        Returns:
            Linked task ID or None
        """
        resource = self.storage.get_resource_by_id(resource_id)
        if not resource:
            return None

        try:
            all_tasks = self.todo_manager.get_all_tasks()
            pending_tasks = [t for t in all_tasks if t.get("status") == "pending"]

            if not pending_tasks:
                return None

            resource_text = f"{resource['content']}\n{resource.get('description', '')}"
            result = await self.ai_client.auto_link_resource(resource_text, pending_tasks)

            linked_task_id = result.get("linked_task_id")
            if linked_task_id and linked_task_id not in resource["linked_tasks"]:
                resource["linked_tasks"].append(linked_task_id)
                self.storage.update_resource(resource_id, resource)

            return linked_task_id
        except Exception as e:
            print(f"Error with AI auto-linking: {e}")
            return None

    def get_all_resources(self) -> List[Dict[str, Any]]:
        """Get all resources"""
        return self.storage.get_resources()

    def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get resource by ID"""
        return self.storage.get_resource_by_id(resource_id)

    def update_resource(self, resource_id: str, updates: Dict[str, Any]) -> bool:
        """Update resource"""
        return self.storage.update_resource(resource_id, updates)

    def delete_resource(self, resource_id: str) -> bool:
        """Delete resource"""
        return self.storage.delete_resource(resource_id)

    def get_resources_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get all resources linked to a task

        Args:
            task_id: Task ID

        Returns:
            List of linked resources
        """
        all_resources = self.storage.get_resources()
        return [
            r for r in all_resources
            if task_id in r.get("linked_tasks", [])
        ]

    def link_resource_to_task(self, resource_id: str, task_id: str) -> bool:
        """
        Manually link a resource to a task

        Args:
            resource_id: Resource ID
            task_id: Task ID

        Returns:
            Success status
        """
        resource = self.storage.get_resource_by_id(resource_id)
        if not resource:
            return False

        if task_id not in resource.get("linked_tasks", []):
            if "linked_tasks" not in resource:
                resource["linked_tasks"] = []
            resource["linked_tasks"].append(task_id)
            return self.storage.update_resource(resource_id, resource)

        return True

    def unlink_resource_from_task(self, resource_id: str, task_id: str) -> bool:
        """
        Unlink a resource from a task

        Args:
            resource_id: Resource ID
            task_id: Task ID

        Returns:
            Success status
        """
        resource = self.storage.get_resource_by_id(resource_id)
        if not resource:
            return False

        linked_tasks = resource.get("linked_tasks", [])
        if task_id in linked_tasks:
            linked_tasks.remove(task_id)
            resource["linked_tasks"] = linked_tasks
            return self.storage.update_resource(resource_id, resource)

        return True


# Global library manager instance
library_manager = LibraryManager()
