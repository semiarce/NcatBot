# 消息段基类与基础消息段

> `MessageSegment` 基类机制，以及 `PlainText`、`At`、`Face`、`Reply` 四种基础消息段。

---

## 目录

- [消息段基类 MessageSegment](#消息段基类-messagesegment)
- [PlainText — 纯文本](#plaintext--纯文本)
- [At — @某人](#at--某人)
- [Face — QQ 表情](#face--qq-表情)
- [Reply — 回复消息](#reply--回复消息)

---

## 消息段基类 MessageSegment

所有消息段继承自 `MessageSegment`（Pydantic `BaseModel`）。

| 属性 / 方法 | 说明 |
|---|---|
| `_type: ClassVar[str]` | 内部判别标识，对应 OB11 外层 `type` |
| `to_dict() → Dict` | 序列化为 OB11 格式 `{"type": "...", "data": {...}}` |
| `from_dict(data) → MessageSegment` | 从 OB11 字典解析为具体子类（委托给 `parse_segment`） |

```python
from ncatbot.types.segment import PlainText

seg = PlainText(text="Hello")
print(seg.to_dict())
# {"type": "text", "data": {"text": "Hello"}}
```

`parse_segment()` 根据 `type` 字段自动查找对应的子类并实例化：

```python
from ncatbot.types.segment import parse_segment

seg = parse_segment({"type": "at", "data": {"qq": "123456"}})
# 返回 At(qq='123456')
```

---

## PlainText — 纯文本

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `text` | `str` | ✅ | 文本内容 |

```python
from ncatbot.types.segment import PlainText

seg = PlainText(text="你好世界")
seg.to_dict()
# {"type": "text", "data": {"text": "你好世界"}}
```

---

## At — @某人

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `qq` | `str` | ✅ | QQ号（纯数字）或 `"all"` 表示 @全体成员 |

`qq` 字段会自动验证：必须为纯数字或 `"all"`，传入整数会自动转为字符串。

```python
from ncatbot.types.segment import At

# @某人
seg = At(qq="123456")
seg = At(qq=123456)     # 整数自动转换

# @全体成员
seg_all = At(qq="all")
```

---

## Face — QQ 表情

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | `str` | ✅ | QQ 表情 ID（自动转为字符串） |

```python
from ncatbot.types.segment import Face

seg = Face(id="178")    # 表情 ID
seg = Face(id=178)      # 整数自动转换
seg.to_dict()
# {"type": "face", "data": {"id": "178"}}
```

---

## Reply — 回复消息

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | `str` | ✅ | 被回复消息的 ID（自动转为字符串） |

```python
from ncatbot.types.segment import Reply

seg = Reply(id="12345")
seg = Reply(id=12345)   # 整数自动转换
seg.to_dict()
# {"type": "reply", "data": {"id": "12345"}}
```

---

[← 返回目录](README.md) | [下一篇：多媒体消息段 →](media.md)
