"""
配置管理模块
负责读取、写入和验证应用配置
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str = "data"):
        """
        初始化配置管理器

        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            配置字典
        """
        if not self.config_file.exists():
            return self._get_default_config()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self._get_default_config()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        保存配置文件

        Args:
            config: 配置字典

        Returns:
            是否保存成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get_api_config(self) -> Optional[Dict[str, str]]:
        """
        获取 API 配置

        Returns:
            API 配置字典，包含 base_url, api_key, model
        """
        config = self.load_config()
        return config.get("api")

    def update_api_config(self, base_url: str, api_key: str, model: str) -> bool:
        """
        更新 API 配置

        Args:
            base_url: API 基础 URL
            api_key: API 密钥
            model: 模型名称

        Returns:
            是否更新成功
        """
        config = self.load_config()
        config["api"] = {
            "base_url": base_url,
            "api_key": api_key,
            "model": model
        }
        return self.save_config(config)

    def get_user_config(self) -> Optional[Dict[str, str]]:
        """
        获取用户配置

        Returns:
            用户配置字典
        """
        config = self.load_config()
        return config.get("user")

    def update_user_config(self, name: str, timezone: str = "Asia/Shanghai") -> bool:
        """
        更新用户配置

        Args:
            name: 用户名
            timezone: 时区

        Returns:
            是否更新成功
        """
        config = self.load_config()
        config["user"] = {
            "name": name,
            "timezone": timezone
        }
        return self.save_config(config)

    def is_configured(self) -> bool:
        """
        检查是否已配置 API

        Returns:
            是否已配置
        """
        api_config = self.get_api_config()
        if not api_config:
            return False

        required_fields = ["base_url", "api_key", "model"]
        return all(api_config.get(field) for field in required_fields)

    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置

        Returns:
            默认配置字典
        """
        return {
            "api": {
                "base_url": "",
                "api_key": "",
                "model": ""
            },
            "user": {
                "name": "学习者",
                "timezone": "Asia/Shanghai"
            },
            "created_at": datetime.now().isoformat()
        }

    def validate_api_config(self, base_url: str, api_key: str, model: str) -> tuple[bool, str]:
        """
        验证 API 配置

        Args:
            base_url: API 基础 URL
            api_key: API 密钥
            model: 模型名称

        Returns:
            (是否有效, 错误信息)
        """
        if not base_url or not base_url.strip():
            return False, "API 基础 URL 不能为空"

        if not api_key or not api_key.strip():
            return False, "API 密钥不能为空"

        if not model or not model.strip():
            return False, "模型名称不能为空"

        # 验证 URL 格式
        if not base_url.startswith(("http://", "https://")):
            return False, "API 基础 URL 必须以 http:// 或 https:// 开头"

        return True, ""


# 创建全局配置管理器实例
config_manager = ConfigManager()
