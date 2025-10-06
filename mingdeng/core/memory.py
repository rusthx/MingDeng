"""
Mem0 记忆系统模块
负责存储和检索学习历史、对话记录等
"""

from typing import List, Dict, Any, Optional
from pathlib import Path


class MemoryManager:
    """
    记忆管理器

    注意: Mem0 需要单独配置，这里提供基础接口
    如果未安装或未配置 Mem0，将使用简单的本地存储
    """

    def __init__(self, memory_dir: str = "data/memory"):
        """
        初始化记忆管理器

        Args:
            memory_dir: 记忆数据目录
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.mem0_client = None
        self._initialize_mem0()

    def _initialize_mem0(self):
        """
        初始化 Mem0 客户端

        如果 Mem0 未安装或配置失败，将使用本地存储
        """
        try:
            from mem0 import Memory
            # 使用本地向量存储
            config = {
                "vector_store": {
                    "provider": "chroma",
                    "config": {
                        "collection_name": "mingdeng_memory",
                        "path": str(self.memory_dir / "chroma_db")
                    }
                }
            }
            self.mem0_client = Memory.from_config(config)
        except ImportError:
            print("Mem0 未安装，将使用简化的记忆功能")
            self.mem0_client = None
        except Exception as e:
            print(f"初始化 Mem0 失败: {e}")
            self.mem0_client = None

    def is_available(self) -> bool:
        """
        检查 Mem0 是否可用

        Returns:
            是否可用
        """
        return self.mem0_client is not None

    def add_memory(
        self,
        content: str,
        user_id: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加记忆

        Args:
            content: 记忆内容
            user_id: 用户 ID
            metadata: 元数据

        Returns:
            是否添加成功
        """
        if not self.is_available():
            # 如果 Mem0 不可用，这里可以实现简单的本地存储
            print(f"记忆功能不可用，跳过添加: {content[:50]}...")
            return False

        try:
            self.mem0_client.add(
                content,
                user_id=user_id,
                metadata=metadata or {}
            )
            return True
        except Exception as e:
            print(f"添加记忆失败: {e}")
            return False

    def search_memory(
        self,
        query: str,
        user_id: str = "default",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        搜索相关记忆

        Args:
            query: 查询内容
            user_id: 用户 ID
            limit: 返回结果数量

        Returns:
            相关记忆列表
        """
        if not self.is_available():
            return []

        try:
            results = self.mem0_client.search(
                query,
                user_id=user_id,
                limit=limit
            )
            return results
        except Exception as e:
            print(f"搜索记忆失败: {e}")
            return []

    def get_all_memories(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """
        获取所有记忆

        Args:
            user_id: 用户 ID

        Returns:
            记忆列表
        """
        if not self.is_available():
            return []

        try:
            memories = self.mem0_client.get_all(user_id=user_id)
            return memories
        except Exception as e:
            print(f"获取记忆失败: {e}")
            return []

    def delete_memory(self, memory_id: str) -> bool:
        """
        删除指定记忆

        Args:
            memory_id: 记忆 ID

        Returns:
            是否删除成功
        """
        if not self.is_available():
            return False

        try:
            self.mem0_client.delete(memory_id)
            return True
        except Exception as e:
            print(f"删除记忆失败: {e}")
            return False

    def add_learning_log(
        self,
        task_name: str,
        content: str,
        task_id: Optional[str] = None
    ) -> bool:
        """
        添加学习日志

        Args:
            task_name: 任务名称
            content: 日志内容
            task_id: 任务 ID

        Returns:
            是否添加成功
        """
        metadata = {
            "type": "learning_log",
            "task_name": task_name
        }
        if task_id:
            metadata["task_id"] = task_id

        return self.add_memory(
            content=f"学习任务「{task_name}」: {content}",
            metadata=metadata
        )

    def add_conversation(
        self,
        user_message: str,
        ai_response: str,
        context: Optional[str] = None
    ) -> bool:
        """
        添加对话记录

        Args:
            user_message: 用户消息
            ai_response: AI 回复
            context: 上下文信息

        Returns:
            是否添加成功
        """
        content = f"用户: {user_message}\nAI: {ai_response}"
        if context:
            content = f"[{context}] {content}"

        metadata = {
            "type": "conversation",
            "user_message": user_message,
            "ai_response": ai_response
        }

        return self.add_memory(content=content, metadata=metadata)

    def get_learning_context(self, query: str, limit: int = 3) -> str:
        """
        获取学习上下文（用于增强 AI 对话）

        Args:
            query: 查询内容
            limit: 返回结果数量

        Returns:
            格式化的上下文字符串
        """
        memories = self.search_memory(query, limit=limit)

        if not memories:
            return ""

        context_parts = []
        for i, memory in enumerate(memories, 1):
            content = memory.get("memory", memory.get("content", ""))
            context_parts.append(f"{i}. {content}")

        return "相关学习历史:\n" + "\n".join(context_parts)


# 创建全局记忆管理器实例
memory_manager = MemoryManager()
