#!/usr/bin/env python3
"""
API 连接测试脚本
用于诊断 API 配置问题
"""

import sys
import json
from pathlib import Path

# 添加 mingdeng 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "mingdeng"))

from core.config import config_manager
from openai import OpenAI

def test_api():
    """测试 API 连接"""

    print("=" * 60)
    print("MingDeng API 连接测试")
    print("=" * 60)
    print()

    # 1. 读取配置
    print("1. 读取配置...")
    api_config = config_manager.get_api_config()

    if not api_config:
        print("❌ 未找到 API 配置，请先在应用中配置")
        return

    base_url = api_config.get("base_url", "").rstrip("/")
    api_key = api_config.get("api_key", "")
    model = api_config.get("model", "")

    print(f"   Base URL: {base_url}")
    print(f"   API Key: {'*' * 10 if api_key else '(空)'}")
    print(f"   Model: {model}")
    print()

    # 2. 构建完整 URL
    print("2. 完整请求 URL:")
    full_url = f"{base_url}/chat/completions"
    print(f"   {full_url}")
    print()

    # 3. 测试连接
    print("3. 发送测试请求...")
    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "测试连接，请回复'连接成功'"}
            ],
            temperature=0,
            max_tokens=10
        )

        content = response.choices[0].message.content
        print(f"✅ 连接成功！")
        print(f"   响应: {content}")
        print()

    except Exception as e:
        print(f"❌ 连接失败！")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {str(e)}")
        print()

        # 提供诊断建议
        print("🔍 诊断建议:")
        error_msg = str(e).lower()

        if "404" in error_msg or "not found" in error_msg:
            print("   • 404 错误通常是 base_url 不正确")
            print("   • 请检查你的 API 文档，确认正确的 base_url")
            print("   • 常见格式：")
            print("     - OpenAI: https://api.openai.com/v1")
            print("     - Ollama: http://localhost:11434/v1")
            print("     - 某些服务可能不需要 /v1 后缀")
            print()
            print("   • 当前完整 URL: " + full_url)
            print("   • 请确认这个 URL 是否正确")

        elif "401" in error_msg or "unauthorized" in error_msg:
            print("   • 401 错误通常是 API Key 不正确")
            print("   • 请检查你的 API Key 是否有效")

        elif "connection" in error_msg or "timeout" in error_msg:
            print("   • 连接错误，请检查：")
            print("     - 网络连接是否正常")
            print("     - Base URL 是否可访问")
            print("     - 如果是本地服务，确认服务是否已启动")

        print()

    print("=" * 60)

if __name__ == "__main__":
    test_api()
