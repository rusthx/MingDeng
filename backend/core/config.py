"""
Configuration Management Module
Handles loading and saving user configuration
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class APIConfig(BaseModel):
    """API Configuration"""
    base_url: str = Field(default="https://api.openai.com/v1", description="API Base URL")
    api_key: str = Field(default="", description="API Key")
    model: str = Field(default="gpt-4", description="Model Name")


class UserConfig(BaseModel):
    """User Configuration"""
    name: str = Field(default="User", description="User Name")
    timezone: str = Field(default="Asia/Shanghai", description="Timezone")


class Config(BaseModel):
    """Main Configuration"""
    api: APIConfig = Field(default_factory=APIConfig)
    user: UserConfig = Field(default_factory=UserConfig)


class ConfigManager:
    """Configuration Manager"""

    def __init__(self, config_path: str = "data/config.json"):
        self.config_path = Path(config_path)
        self.config: Config = self._load_config()

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Config:
        """Load configuration from file"""
        self._ensure_data_dir()

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Config(**data)
            except Exception as e:
                print(f"Error loading config: {e}")
                return Config()
        else:
            # Create default config
            config = Config()
            self.save_config(config)
            return config

    def save_config(self, config: Config) -> bool:
        """Save configuration to file"""
        try:
            self._ensure_data_dir()
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
            self.config = config
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_config(self) -> Config:
        """Get current configuration"""
        return self.config

    def update_api_config(self, base_url: Optional[str] = None,
                         api_key: Optional[str] = None,
                         model: Optional[str] = None) -> bool:
        """Update API configuration"""
        if base_url:
            self.config.api.base_url = base_url
        if api_key:
            self.config.api.api_key = api_key
        if model:
            self.config.api.model = model

        return self.save_config(self.config)

    def update_user_config(self, name: Optional[str] = None,
                          timezone: Optional[str] = None) -> bool:
        """Update user configuration"""
        if name:
            self.config.user.name = name
        if timezone:
            self.config.user.timezone = timezone

        return self.save_config(self.config)

    def is_configured(self) -> bool:
        """Check if API is configured"""
        return bool(self.config.api.api_key and self.config.api.base_url)


# Global config manager instance
config_manager = ConfigManager()
