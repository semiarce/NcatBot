# 多媒体消息段

> `DownloadableSegment` 可下载资源基类，以及 `Image`、`Record`、`Video`、`File` 四种多媒体类型。

---

## 目录

- [DownloadableSegment — 可下载资源基类](#downloadablesegment--可下载资源基类)
- [Image — 图片](#image--图片)
- [Record — 语音](#record--语音)
- [Video — 视频](#video--视频)
- [File — 文件](#file--文件)

---

## DownloadableSegment — 可下载资源基类

所有多媒体类型（Image / Record / Video / File）都继承自 `DownloadableSegment`，共享以下字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | `str` | ✅ | 文件标识：URL、本地路径或 base64 编码 |
| `url` | `str?` | ❌ | 文件下载地址（收到消息时由平台填充） |
| `file_id` | `str?` | ❌ | 文件 ID |
| `file_size` | `int?` | ❌ | 文件大小（字节） |
| `file_name` | `str?` | ❌ | 文件名 |

`file` 字段支持三种格式：

| 格式 | 示例 | 说明 |
|---|---|---|
| URL | `"https://example.com/img.png"` | 远程地址 |
| 本地路径 | `"file:///C:/img.png"` | 本地文件 |
| Base64 | `"base64://iVBORw0KGgo..."` | base64 编码数据 |

---

## Image — 图片

继承自 `DownloadableSegment`，额外字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `sub_type` | `int` | ❌ | `0` | 子类型 |
| `type` | `int?` | ❌ | `None` | `0` = 普通图片，`1` = 闪照 |

```python
from ncatbot.types.segment import Image

# 通过 URL 发送图片
img = Image(file="https://example.com/photo.jpg")

# 通过本地路径
img = Image(file="file:///C:/Users/photo.jpg")

# 通过 base64
img = Image(file="base64://iVBORw0KGgoAAAANSUhEUg...")

# 闪照
img = Image(file="https://example.com/photo.jpg", type=1)

img.to_dict()
# {"type": "image", "data": {"file": "https://example.com/photo.jpg", "sub_type": 0}}
```

---

## Record — 语音

继承自 `DownloadableSegment`，额外字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `magic` | `int?` | ❌ | 是否变声（`1` 为变声） |

```python
from ncatbot.types.segment import Record

rec = Record(file="https://example.com/audio.silk")
rec = Record(file="file:///C:/voice.amr", magic=1)  # 变声
rec.to_dict()
# {"type": "record", "data": {"file": "https://example.com/audio.silk"}}
```

---

## Video — 视频

继承自 `DownloadableSegment`，无额外字段。

```python
from ncatbot.types.segment import Video

vid = Video(file="https://example.com/video.mp4")
vid.to_dict()
# {"type": "video", "data": {"file": "https://example.com/video.mp4"}}
```

---

## File — 文件

继承自 `DownloadableSegment`，无额外字段。主要通过 `file_name` 字段指定文件名。

```python
from ncatbot.types.segment import File

f = File(file="https://example.com/doc.pdf", file_name="使用手册.pdf")
f.to_dict()
# {"type": "file", "data": {"file": "https://example.com/doc.pdf", "file_name": "使用手册.pdf"}}
```

---

[← 上一篇：基础消息段](basic.md) | [返回目录](README.md) | [下一篇：富文本消息段 →](rich.md)
