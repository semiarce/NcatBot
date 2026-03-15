# 合并转发消息段

> `ForwardNode` 转发节点与 `Forward` 合并转发：构造新的合并转发或引用已有转发。

---

## 目录

- [ForwardNode — 转发节点](#forwardnode--转发节点)
- [Forward — 合并转发](#forward--合并转发)

---

## ForwardNode — 转发节点

`ForwardNode` 代表合并转发中的单条消息。它不是 `MessageSegment` 的子类，而是独立的 Pydantic `BaseModel`。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `user_id` | `str` | ✅ | 发送者 QQ（自动转为字符串） |
| `nickname` | `str` | ✅ | 发送者昵称（合并转发中的显示名） |
| `content` | `List[MessageSegment]` | ✅ | 消息内容（可包含多个消息段） |

`content` 字段支持传入 OB11 字典列表，会自动解析为 `MessageSegment` 对象。

```python
from ncatbot.types.segment import ForwardNode, PlainText, Image

node = ForwardNode(
    user_id="123456",
    nickname="小明",
    content=[PlainText(text="这是转发的第一条消息")],
)

# 也可以传入字典列表
node = ForwardNode(
    user_id=123456,
    nickname="小明",
    content=[
        {"type": "text", "data": {"text": "Hello"}},
        {"type": "image", "data": {"file": "https://example.com/img.png"}},
    ],
)
```

---

## Forward — 合并转发

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | `str?` | ❌ | 转发消息 ID（引用已有的合并转发） |
| `content` | `List[ForwardNode]?` | ❌ | 转发节点列表（构造新的合并转发） |

`Forward` 有两种使用方式：

### 方式一：引用已有的合并转发（通过 `id`）

```python
from ncatbot.types.segment import Forward

fwd = Forward(id="abc123")
fwd.to_dict()
# {"type": "forward", "data": {"id": "abc123"}}
```

### 方式二：构造新的合并转发（通过 `content`）

```python
from ncatbot.types.segment import Forward, ForwardNode, PlainText, Image

fwd = Forward(content=[
    ForwardNode(
        user_id="123456",
        nickname="小明",
        content=[PlainText(text="第一条消息")],
    ),
    ForwardNode(
        user_id="654321",
        nickname="小红",
        content=[
            PlainText(text="带图片的消息"),
            Image(file="https://example.com/img.png"),
        ],
    ),
])

fwd.to_dict()
# {"type": "forward", "data": {"content": [...]}}
```

### 嵌套合并转发

`ForwardNode` 的 `content` 中可以嵌套 `Forward`，实现多层转发。

---

[← 上一篇：富文本消息段](rich.md) | [返回目录](README.md) | [下一篇：MessageArray →](array.md)
