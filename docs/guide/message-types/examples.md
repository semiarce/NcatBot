# 实战示例

> 7 个完整场景，展示如何在插件中构造和发送各种消息。

---

## 目录

- [发送纯文本](#发送纯文本)
- [发送图文混排](#发送图文混排)
- [回复消息](#回复消息)
- [合并转发消息](#合并转发消息)
- [从收到的消息中提取图片](#从收到的消息中提取图片)
- [@全体成员 并发送提示](#全体成员-并发送提示)
- [发送音乐卡片](#发送音乐卡片)

---

## 发送纯文本

```python
from ncatbot.plugin import NcatBotPlugin

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        @self.bot.on_group_message()
        async def handle(event):
            if event.message.text == "你好":
                await self.api.send_group_text(event.group_id, "你好！")
```

---

## 发送图文混排

```python
from ncatbot.types.segment import MessageArray

@self.bot.on_group_message()
async def handle(event):
    msg = (
        MessageArray()
        .add_at(event.user_id)
        .add_text(" 送你一张图！")
        .add_image("https://example.com/gift.png")
    )
    await self.api.post_group_array_msg(event.group_id, msg)
```

---

## 回复消息

```python
from ncatbot.types.segment import MessageArray

@self.bot.on_group_message()
async def handle(event):
    # 方式一：使用 MessageArray
    msg = (
        MessageArray()
        .add_reply(event.message_id)
        .add_text("收到！")
    )
    await self.api.post_group_array_msg(event.group_id, msg)

    # 方式二：使用便捷方法
    await self.api.post_group_msg(
        event.group_id,
        text="收到！",
        reply=event.message_id,
    )
```

---

## 合并转发消息

```python
from ncatbot.types.segment import Forward, ForwardNode, PlainText, Image

@self.bot.on_group_message()
async def handle(event):
    if event.message.text == "日报":
        fwd = Forward(content=[
            ForwardNode(
                user_id="10000",
                nickname="日报Bot",
                content=[PlainText(text="📅 今日概要")],
            ),
            ForwardNode(
                user_id="10000",
                nickname="日报Bot",
                content=[
                    PlainText(text="活跃用户: 128"),
                    Image(file="https://example.com/chart.png"),
                ],
            ),
        ])
        await self.api.post_group_forward_msg(event.group_id, fwd)
```

---

## 从收到的消息中提取图片

```python
@self.bot.on_group_message()
async def handle(event):
    images = event.message.filter_image()
    if images:
        for img in images:
            print(f"图片文件: {img.file}")
            print(f"图片URL: {img.url}")
        await self.api.send_group_text(
            event.group_id, f"收到 {len(images)} 张图片"
        )
```

---

## @全体成员 并发送提示

```python
from ncatbot.types.segment import MessageArray

@self.bot.on_group_message()
async def handle(event):
    msg = (
        MessageArray()
        .add_at_all()
        .add_text(" 重要通知：明天放假！")
    )
    await self.api.post_group_array_msg(event.group_id, msg)
```

---

## 发送音乐卡片

```python
from ncatbot.types.segment import MessageArray, Music

@self.bot.on_group_message()
async def handle(event):
    if event.message.text == "点歌":
        music = Music(type="qq", id="12345")
        msg = MessageArray().add_segment(music)
        await self.api.post_group_array_msg(event.group_id, msg)
```

---

[← 上一篇：语法糖](sugar.md) | [返回目录](README.md)
