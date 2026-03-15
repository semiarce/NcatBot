# 富文本消息段

> `Share`、`Location`、`Music`、`Json`、`Markdown` 五种富文本消息段。

---

## 目录

- [Share — 链接分享](#share--链接分享)
- [Location — 定位](#location--定位)
- [Music — 音乐](#music--音乐)
- [Json — JSON 消息](#json--json-消息)
- [Markdown — Markdown 消息](#markdown--markdown-消息)

---

## Share — 链接分享

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `url` | `str` | ✅ | 分享链接 |
| `title` | `str` | ✅ | 分享标题 |
| `content` | `str?` | ❌ | 分享描述 |
| `image` | `str?` | ❌ | 预览图 URL |

```python
from ncatbot.types.segment import Share

seg = Share(
    url="https://github.com/ncatbot/NcatBot",
    title="NcatBot",
    content="Python QQ 机器人框架",
    image="https://example.com/preview.png",
)
seg.to_dict()
# {"type": "share", "data": {"url": "...", "title": "NcatBot", "content": "...", "image": "..."}}
```

---

## Location — 定位

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `lat` | `float` | ✅ | 纬度 |
| `lon` | `float` | ✅ | 经度 |
| `title` | `str?` | ❌ | 位置标题 |
| `content` | `str?` | ❌ | 位置描述 |

```python
from ncatbot.types.segment import Location

seg = Location(lat=39.9042, lon=116.4074, title="北京", content="天安门广场")
seg.to_dict()
# {"type": "location", "data": {"lat": 39.9042, "lon": 116.4074, "title": "北京", "content": "天安门广场"}}
```

---

## Music — 音乐

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `type` | `Literal["qq", "163", "custom"]` | ✅ | 音乐平台：`"qq"` / `"163"` / `"custom"` |
| `id` | `str?` | ❌ | 歌曲 ID（`qq` / `163` 平台时使用） |
| `url` | `str?` | ❌ | 跳转链接（`custom` 类型时使用） |
| `audio` | `str?` | ❌ | 音频链接（`custom` 类型时使用） |
| `title` | `str?` | ❌ | 歌曲标题（`custom` 类型时使用） |

> **注意**：`Music` 的 `type` 字段保留 OB11 `data.type` 的原始语义，与基类 `_type` 不同。`_type = "music"` 是内部判别标识。

```python
from ncatbot.types.segment import Music

# QQ 音乐
seg = Music(type="qq", id="12345")

# 网易云音乐
seg = Music(type="163", id="67890")

# 自定义音乐卡片
seg = Music(
    type="custom",
    url="https://music.example.com",
    audio="https://music.example.com/song.mp3",
    title="自定义歌曲",
)
```

---

## Json — JSON 消息

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `data` | `str` | ✅ | JSON 字符串内容 |

```python
from ncatbot.types.segment import Json

seg = Json(data='{"app":"com.example","desc":"卡片消息"}')
seg.to_dict()
# {"type": "json", "data": {"data": "{\"app\":\"com.example\",\"desc\":\"卡片消息\"}"}}
```

---

## Markdown — Markdown 消息

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `content` | `str` | ✅ | Markdown 内容 |

```python
from ncatbot.types.segment import Markdown

seg = Markdown(content="# 标题\n**粗体**\n- 列表项")
seg.to_dict()
# {"type": "markdown", "data": {"content": "# 标题\n**粗体**\n- 列表项"}}
```

---

[← 上一篇：多媒体消息段](media.md) | [返回目录](README.md) | [下一篇：合并转发 →](forward.md)
