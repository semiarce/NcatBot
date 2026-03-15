"""
06_hook_and_filter 插件离线测试

规范:
  PL-20: BEFORE_CALL Hook 过滤关键词 → SKIP
  PL-21: AFTER_CALL Hook 日志记录（不崩溃）
  PL-22: ON_ERROR Hook 捕获除零异常
  PL-23: 正常命令通过 Hook 链
"""

import pytest

from ncatbot.testing import PluginTestHarness, group_message, private_message

pytestmark = pytest.mark.asyncio

PLUGIN_NAME = "hook_and_filter"


@pytest.fixture
def examples_dir():
    from pathlib import Path

    return Path(__file__).resolve().parents[3] / "examples"


# ---- PL-20: 关键词过滤 ----


async def test_blocked_word_filtered(examples_dir):
    """PL-20: '回声 违禁词' → KeywordFilterHook SKIP → 不回复"""
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugin_dir=examples_dir
    ) as h:
        await h.inject(group_message("回声 违禁词", group_id="300", user_id="99"))
        await h.settle(0.1)

        # 被 Hook 拦截，不应有回复
        assert not h.api_called("send_group_msg")


async def test_blocked_word_spam(examples_dir):
    """PL-20b: '回声 spam' → 同样被拦截"""
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugin_dir=examples_dir
    ) as h:
        await h.inject(group_message("回声 spam", group_id="300", user_id="99"))
        await h.settle(0.1)

        assert not h.api_called("send_group_msg")


# ---- PL-21 & PL-23: 正常通过 Hook 链 ----


async def test_echo_normal(examples_dir):
    """PL-23: '回声 你好' → 通过过滤 → 回复 '🔊 你好'"""
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugin_dir=examples_dir
    ) as h:
        await h.inject(group_message("回声 你好", group_id="300", user_id="99"))
        await h.settle(0.1)

        assert h.api_called("send_group_msg")


# ---- PL-22: ON_ERROR Hook ----


async def test_error_hook_catches_exception(examples_dir):
    """PL-22: '除零' → ZeroDivisionError → ErrorNotifyHook 回复错误信息"""
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugin_dir=examples_dir
    ) as h:
        await h.inject(group_message("除零", group_id="300", user_id="99"))
        await h.settle(0.1)

        # ErrorNotifyHook 应通过 ctx.api 发送错误通知
        assert h.api_called("send_group_msg")


# ---- 私聊命令 ----


async def test_private_command(examples_dir):
    """私聊发 '私聊测试' → send_private_msg"""
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugin_dir=examples_dir
    ) as h:
        await h.inject(private_message("私聊测试", user_id="99"))
        await h.settle(0.1)

        assert h.api_called("send_private_msg")
