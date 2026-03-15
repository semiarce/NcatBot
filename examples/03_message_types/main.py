"""
03_message_types — 消息构造与解析

演示功能:
  - MessageArray 链式构造
  - 多种消息段: PlainText / At / Image / Reply / Record / Video / File
  - ForwardConstructor 合并转发消息
  - 从收到的消息中提取图片 URL
  - 使用插件自带的示例图片资源

使用方式:
  群里发 "图文"   → 收到图文混排消息（含示例图片）
  群里发 "转发"   → 收到合并转发消息
  群里发 "at我"   → 收到 @你 的消息
  群里发送图片    → Bot 提取并回显图片信息
"""

from pathlib import Path

from ncatbot.core.registry import registrar
from ncatbot.event import GroupMessageEvent
from ncatbot.plugin import NcatBotPlugin
from ncatbot.types import (
    Image,
    MessageArray,
    ForwardConstructor,
)
from ncatbot.utils import get_log

LOG = get_log("MessageTypes")

# 插件自带的示例资源路径
PLUGIN_DIR = Path(__file__).parent
EXAMPLE_IMAGE = PLUGIN_DIR / "resources" / "example.jpg"


class MessageTypesPlugin(NcatBotPlugin):
    name = "message_types"
    version = "1.0.0"
    author = "NcatBot"
    description = "消息构造与解析演示"

    async def on_load(self):
        LOG.info("MessageTypes 插件已加载")

    # ---- 图文混排 ----

    @registrar.on_group_command("图文")
    async def on_rich_text(self, event: GroupMessageEvent):
        """发送图文混排消息"""
        msg = MessageArray()
        msg.add_text("📸 这是一条图文混排消息:\n")
        msg.add_image(str(EXAMPLE_IMAGE))
        msg.add_text("\n以上是示例图片！")

        await self.api.post_group_array_msg(event.group_id, msg)

    # ---- @某人 ----

    @registrar.on_group_command("at我")
    async def on_at_me(self, event: GroupMessageEvent):
        """发送 @你 的消息"""
        msg = MessageArray()
        msg.add_at(event.user_id)
        msg.add_text(" 你被 At 了！")

        await self.api.post_group_array_msg(event.group_id, msg)

    # ---- 合并转发 ----

    @registrar.on_group_command("转发")
    async def on_forward(self, event: GroupMessageEvent):
        """发送合并转发消息"""
        fc = ForwardConstructor(user_id=str(event.self_id), nickname="Bot")

        fc.attach_text("这是转发消息的第一条 📝")
        fc.attach_text("这是转发消息的第二条 📝")

        # 也可以构造图文节点
        msg = MessageArray()
        msg.add_text("这条包含图片: ")
        msg.add_image(str(EXAMPLE_IMAGE))
        fc.attach_message(msg)

        forward = fc.build()
        await self.api.post_group_forward_msg(event.group_id, forward)

    # ---- 提取图片 ----

    @registrar.on_group_message()
    async def on_extract_image(self, event: GroupMessageEvent):
        """收到含图片的消息时，提取并回显图片信息"""
        images = event.message.filter(Image)
        if not images:
            return

        lines = [f"🖼️ 检测到 {len(images)} 张图片:"]
        for i, img in enumerate(images, 1):
            url = getattr(img, "url", None) or getattr(img, "file", "未知")
            lines.append(f"  图片 {i}: {url}")

        await event.reply("\n".join(lines))
