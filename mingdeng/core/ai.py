"""
OpenAI 兼容 API 调用模块
支持流式和非流式响应
"""

from typing import Generator, Optional, Dict, Any, List
import json
from openai import OpenAI
from .config import config_manager


class AIClient:
    """AI 客户端，支持 OpenAI 兼容格式的 API"""

    def __init__(self):
        """初始化 AI 客户端"""
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """初始化 OpenAI 客户端"""
        api_config = config_manager.get_api_config()
        if api_config and all(api_config.get(k) for k in ["base_url", "api_key", "model"]):
            # 规范化 base_url：确保没有末尾斜杠
            base_url = api_config["base_url"].rstrip("/")

            self.client = OpenAI(
                base_url=base_url,
                api_key=api_config["api_key"]
            )

    def is_configured(self) -> bool:
        """
        检查 AI 客户端是否已配置

        Returns:
            是否已配置
        """
        return self.client is not None

    def refresh_client(self):
        """刷新客户端配置"""
        self._initialize_client()

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """
        发送聊天请求

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数（0-2）
            max_tokens: 最大生成 token 数
            stream: 是否启用流式响应

        Returns:
            如果 stream=False，返回完整响应文本
            如果 stream=True，返回生成器
        """
        if not self.is_configured():
            raise ValueError("AI 客户端未配置，请先配置 API")

        api_config = config_manager.get_api_config()
        model = api_config["model"]

        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**kwargs)

            if stream:
                return self._stream_response(response)
            else:
                return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"AI 请求失败: {str(e)}")

    def _stream_response(self, response) -> Generator[str, None, None]:
        """
        处理流式响应

        Args:
            response: OpenAI 流式响应对象

        Yields:
            每个 token 的文本内容
        """
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def chat_with_system(
        self,
        user_message: str,
        system_message: str = "",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """
        带系统提示词的聊天请求

        Args:
            user_message: 用户消息
            system_message: 系统提示词
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            stream: 是否启用流式响应

        Returns:
            响应内容
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": user_message})

        return self.chat(messages, temperature, max_tokens, stream)

    def generate_json(
        self,
        prompt: str,
        system_message: str = "",
        temperature: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        """
        生成 JSON 格式的响应

        Args:
            prompt: 提示词
            system_message: 系统提示词
            temperature: 温度参数

        Returns:
            解析后的 JSON 对象，如果解析失败返回 None
        """
        if not system_message:
            system_message = "你是一个 JSON 生成助手。请只返回有效的 JSON 格式，不要包含其他文字。"

        try:
            response = self.chat_with_system(
                user_message=prompt,
                system_message=system_message,
                temperature=temperature,
                stream=False
            )

            # 尝试提取 JSON（可能被代码块包裹）
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            return json.loads(response.strip())

        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            print(f"原始响应: {response}")
            return None
        except Exception as e:
            print(f"生成 JSON 失败: {e}")
            return None

    def test_connection(self) -> tuple[bool, str]:
        """
        测试 API 连接

        Returns:
            (是否成功, 消息)
        """
        if not self.is_configured():
            return False, "AI 客户端未配置"

        try:
            response = self.chat_with_system(
                user_message="测试连接，请回复'连接成功'",
                temperature=0,
                max_tokens=10
            )
            return True, f"连接成功: {response}"
        except Exception as e:
            return False, f"连接失败: {str(e)}"


# 创建全局 AI 客户端实例
ai_client = AIClient()
