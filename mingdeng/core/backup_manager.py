"""
备份管理模块
负责版本备份和恢复，最多保留 10 个备份
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class BackupManager:
    """备份管理器"""

    MAX_BACKUPS = 10  # 最多保留 10 个备份

    def __init__(self, data_dir: str = "data"):
        """
        初始化备份管理器

        Args:
            data_dir: 数据文件目录
        """
        self.data_dir = Path(data_dir)
        self.backup_dir = self.data_dir / "backups"
        self.todos_file = self.data_dir / "todos.json"
        self.library_file = self.data_dir / "library.json"
        self._ensure_backup_dir()

    def _ensure_backup_dir(self):
        """确保备份目录存在"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, reason: str = "手动备份") -> Optional[str]:
        """
        创建备份，超过 10 个时删除最旧的

        Args:
            reason: 备份原因

        Returns:
            备份 ID（时间戳），如果失败返回 None
        """
        try:
            # 生成备份 ID（时间戳）
            backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 创建备份元数据
            backup_metadata = {
                "id": backup_id,
                "reason": reason,
                "created_at": datetime.now().isoformat(),
                "files": []
            }

            # 备份 todos.json
            if self.todos_file.exists():
                backup_todos = self.backup_dir / f"todos_{backup_id}.json"
                shutil.copy2(self.todos_file, backup_todos)
                backup_metadata["files"].append("todos.json")

            # 备份 library.json
            if self.library_file.exists():
                backup_library = self.backup_dir / f"library_{backup_id}.json"
                shutil.copy2(self.library_file, backup_library)
                backup_metadata["files"].append("library.json")

            # 保存备份元数据
            metadata_file = self.backup_dir / f"metadata_{backup_id}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(backup_metadata, f, indent=2, ensure_ascii=False)

            # 清理旧备份
            self._cleanup_old_backups()

            return backup_id

        except Exception as e:
            print(f"创建备份失败: {e}")
            return None

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        列出所有备份，按时间倒序

        Returns:
            备份列表
        """
        backups = []

        # 查找所有元数据文件
        metadata_files = sorted(self.backup_dir.glob("metadata_*.json"), reverse=True)

        for metadata_file in metadata_files:
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                backups.append(metadata)
            except Exception as e:
                print(f"读取备份元数据失败 {metadata_file}: {e}")

        return backups

    def restore_backup(self, backup_id: str) -> bool:
        """
        恢复到指定备份

        Args:
            backup_id: 备份 ID

        Returns:
            是否恢复成功
        """
        try:
            # 在恢复前先创建一个备份
            self.create_backup("恢复前自动备份")

            # 恢复 todos.json
            backup_todos = self.backup_dir / f"todos_{backup_id}.json"
            if backup_todos.exists():
                shutil.copy2(backup_todos, self.todos_file)

            # 恢复 library.json
            backup_library = self.backup_dir / f"library_{backup_id}.json"
            if backup_library.exists():
                shutil.copy2(backup_library, self.library_file)

            return True

        except Exception as e:
            print(f"恢复备份失败: {e}")
            return False

    def delete_backup(self, backup_id: str) -> bool:
        """
        删除指定备份

        Args:
            backup_id: 备份 ID

        Returns:
            是否删除成功
        """
        try:
            # 删除元数据文件
            metadata_file = self.backup_dir / f"metadata_{backup_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()

            # 删除 todos 备份
            backup_todos = self.backup_dir / f"todos_{backup_id}.json"
            if backup_todos.exists():
                backup_todos.unlink()

            # 删除 library 备份
            backup_library = self.backup_dir / f"library_{backup_id}.json"
            if backup_library.exists():
                backup_library.unlink()

            return True

        except Exception as e:
            print(f"删除备份失败: {e}")
            return False

    def _cleanup_old_backups(self):
        """清理旧备份，只保留最新的 MAX_BACKUPS 个"""
        backups = self.list_backups()

        # 如果备份数超过限制，删除最旧的
        if len(backups) > self.MAX_BACKUPS:
            for backup in backups[self.MAX_BACKUPS:]:
                backup_id = backup.get("id")
                if backup_id:
                    self.delete_backup(backup_id)
                    print(f"自动删除旧备份: {backup_id}")

    def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        获取备份详细信息

        Args:
            backup_id: 备份 ID

        Returns:
            备份信息字典，如果不存在返回 None
        """
        metadata_file = self.backup_dir / f"metadata_{backup_id}.json"
        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return metadata
        except Exception as e:
            print(f"读取备份信息失败: {e}")
            return None

    def compare_with_backup(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        比较当前数据与备份的差异

        Args:
            backup_id: 备份 ID

        Returns:
            差异信息字典
        """
        try:
            differences = {
                "backup_id": backup_id,
                "todos_diff": None,
                "library_diff": None
            }

            # 比较 todos.json
            backup_todos = self.backup_dir / f"todos_{backup_id}.json"
            if backup_todos.exists() and self.todos_file.exists():
                with open(backup_todos, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                with open(self.todos_file, 'r', encoding='utf-8') as f:
                    current_data = json.load(f)

                # 简单对比计划数量和任务数量
                backup_plans = len(backup_data.get("plans", []))
                current_plans = len(current_data.get("plans", []))

                backup_tasks = sum(len(p.get("tasks", [])) for p in backup_data.get("plans", []))
                current_tasks = sum(len(p.get("tasks", [])) for p in current_data.get("plans", []))

                differences["todos_diff"] = {
                    "plans": {
                        "backup": backup_plans,
                        "current": current_plans,
                        "diff": current_plans - backup_plans
                    },
                    "tasks": {
                        "backup": backup_tasks,
                        "current": current_tasks,
                        "diff": current_tasks - backup_tasks
                    }
                }

            # 比较 library.json
            backup_library = self.backup_dir / f"library_{backup_id}.json"
            if backup_library.exists() and self.library_file.exists():
                with open(backup_library, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                with open(self.library_file, 'r', encoding='utf-8') as f:
                    current_data = json.load(f)

                backup_resources = len(backup_data.get("resources", []))
                current_resources = len(current_data.get("resources", []))

                differences["library_diff"] = {
                    "resources": {
                        "backup": backup_resources,
                        "current": current_resources,
                        "diff": current_resources - backup_resources
                    }
                }

            return differences

        except Exception as e:
            print(f"比较备份差异失败: {e}")
            return None


# 创建全局备份管理器实例
backup_manager = BackupManager()
