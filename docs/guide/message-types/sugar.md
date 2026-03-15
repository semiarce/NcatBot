# 语法糖 — MessageSugarMixin

> `BotAPIClient` 通过 `MessageSugarMixin` 提供便捷的消息发送方法，在插件中可通过 `self.api` 调用。

---

## 目录

- [便捷发送](#便捷发送)
- [类型专用发送](#类型专用发送)
- [合并转发发送](#合并转发发送)

---

## 便捷发送

`post_group_msg` / `post_private_msg` 接受关键字参数，自动组装 `MessageArray`：

```python
# 在插件的事件处理器中
await self.api.post_group_msg(
    group_id=123456,
    text="你好！",           # 文本
    at=654321,              # @某人
    reply=msg_id,           # 引用回复
    image="https://...",    # 图片
)
```

参数组装顺序为：`reply → at → text → image`。如果需要更复杂的组合，使用 `rtf` 参数传入完整的 `MessageArray`：

```python
msg = (
    MessageArray()
    .add_reply(msg_id)
    .add_text("自定义消息 ")
    .add_image("https://example.com/1.png")
    .add_image("https://example.com/2.png")
)
await self.api.post_group_msg(group_id=123456, rtf=msg)
```

直接发送 `MessageArray`：

```python
await self.api.post_group_array_msg(group_id=123456, msg=msg)
await self.api.post_private_array_msg(user_id=654321, msg=msg)
```

---

## 类型专用发送

| 方法 | 说明 |
|---|---|
| `send_group_text(group_id, text)` | 发送群文本（CQ 码会被解析） |
| `send_group_plain_text(group_id, text)` | 发送群纯文本（原样发送，不解析 CQ 码） |
| `send_group_image(group_id, image)` | 发送群图片 |
| `send_group_record(group_id, file)` | 发送群语音 |
| `send_group_file(group_id, file, name?)` | 发送群文件 |
| `send_private_text(user_id, text)` | 发送私聊文本 |
| `send_private_plain_text(user_id, text)` | 发送私聊纯文本 |
| `send_private_image(user_id, image)` | 发送私聊图片 |
| `send_private_record(user_id, file)` | 发送私聊语音 |
| `send_private_file(user_id, file, name?)` | 发送私聊文件 |

```python
# 发送群纯文本
await self.api.send_group_text(123456, "Hello!")

# 发送群图片
await self.api.send_group_image(123456, "https://example.com/img.png")

# 发送群语音
await self.api.send_group_record(123456, "https://example.com/voice.silk")

# 发送群文件
await self.api.send_group_file(123456, "https://example.com/doc.pdf", name="文档.pdf")
```

---

## 合并转发发送

```python
from ncatbot.types.segment import Forward, ForwardNode, PlainText

fwd = Forward(content=[
    ForwardNode(user_id="111", nickname="Bot", content=[PlainText(text="记录1")]),
    ForwardNode(user_id="111", nickname="Bot", content=[PlainText(text="记录2")]),
])

# 群合并转发
await self.api.post_group_forward_msg(group_id=123456, forward=fwd)

# 私聊合并转发
await self.api.post_private_forward_msg(user_id=654321, forward=fwd)
```

---

[← 上一篇：MessageArray](array.md) | [返回目录](README.md) | [下一篇：实战示例 →](examples.md)
