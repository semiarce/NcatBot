"""跨平台通用附件模型"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Union

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ncatbot.types.common.segment.base import MessageSegment

__all__ = [
    "AttachmentKind",
    "Attachment",
    "ImageAttachment",
    "VideoAttachment",
    "AudioAttachment",
    "FileAttachment",
]


class AttachmentKind(str, Enum):
    """附件类型标识"""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    OTHER = "other"


class Attachment(BaseModel):
    """可下载附件的跨平台描述

    各平台事件实体通过 ``HasAttachments`` mixin 将平台原生附件
    转换为 ``Attachment``，插件侧可统一处理。
    """

    name: str
    url: str
    size: Optional[int] = None
    content_type: Optional[str] = None
    kind: AttachmentKind = AttachmentKind.OTHER
    extra: Dict[str, Any] = Field(default_factory=dict)

    async def download(self, dest: Union[str, Path]) -> Path:
        """下载附件到本地目录

        Parameters
        ----------
        dest : str | Path
            目标**目录**。文件将保存为 ``dest / self.name``。

        Returns
        -------
        Path
            实际写入的文件路径。
        """
        import aiohttp

        dest = Path(dest)
        dest.mkdir(parents=True, exist_ok=True)
        filepath = dest / self.name

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                resp.raise_for_status()
                filepath.write_bytes(await resp.read())

        return filepath

    async def as_bytes(self) -> bytes:
        """下载到内存，返回原始字节"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                resp.raise_for_status()
                return await resp.read()

    def to_segment(self) -> "MessageSegment":
        """转为消息段（直接使用 URL，同平台内转发最快）"""
        from ncatbot.types.common.segment.media import File as FileSeg

        return FileSeg(file=self.url, file_name=self.name, file_size=self.size)

    async def to_local_segment(
        self, cache_dir: Union[str, Path] = ".cache/attachments"
    ) -> "MessageSegment":
        """先下载到本地，再转为消息段（跨平台安全）"""
        from ncatbot.types.common.segment.media import File as FileSeg

        local = await self.download(cache_dir)
        return FileSeg(file=str(local), file_name=self.name, file_size=self.size)


class ImageAttachment(Attachment):
    """图片附件"""

    kind: Literal[AttachmentKind.IMAGE] = AttachmentKind.IMAGE
    width: Optional[int] = None
    height: Optional[int] = None

    def to_segment(self) -> "MessageSegment":
        from ncatbot.types.common.segment.media import Image as ImageSeg

        return ImageSeg(file=self.url, file_name=self.name, file_size=self.size)

    async def to_local_segment(
        self, cache_dir: Union[str, Path] = ".cache/attachments"
    ) -> "MessageSegment":
        from ncatbot.types.common.segment.media import Image as ImageSeg

        local = await self.download(cache_dir)
        return ImageSeg(file=str(local), file_name=self.name, file_size=self.size)


class VideoAttachment(Attachment):
    """视频附件"""

    kind: Literal[AttachmentKind.VIDEO] = AttachmentKind.VIDEO
    duration: Optional[int] = None

    def to_segment(self) -> "MessageSegment":
        from ncatbot.types.common.segment.media import Video as VideoSeg

        return VideoSeg(file=self.url, file_name=self.name, file_size=self.size)

    async def to_local_segment(
        self, cache_dir: Union[str, Path] = ".cache/attachments"
    ) -> "MessageSegment":
        from ncatbot.types.common.segment.media import Video as VideoSeg

        local = await self.download(cache_dir)
        return VideoSeg(file=str(local), file_name=self.name, file_size=self.size)


class AudioAttachment(Attachment):
    """音频附件"""

    kind: Literal[AttachmentKind.AUDIO] = AttachmentKind.AUDIO
    duration: Optional[int] = None

    def to_segment(self) -> "MessageSegment":
        from ncatbot.types.common.segment.media import Record as RecordSeg

        return RecordSeg(file=self.url, file_name=self.name, file_size=self.size)

    async def to_local_segment(
        self, cache_dir: Union[str, Path] = ".cache/attachments"
    ) -> "MessageSegment":
        from ncatbot.types.common.segment.media import Record as RecordSeg

        local = await self.download(cache_dir)
        return RecordSeg(file=str(local), file_name=self.name, file_size=self.size)


class FileAttachment(Attachment):
    """文件附件"""

    kind: Literal[AttachmentKind.FILE] = AttachmentKind.FILE

    def to_segment(self) -> "MessageSegment":
        from ncatbot.types.common.segment.media import File as FileSeg

        return FileSeg(file=self.url, file_name=self.name, file_size=self.size)

    async def to_local_segment(
        self, cache_dir: Union[str, Path] = ".cache/attachments"
    ) -> "MessageSegment":
        from ncatbot.types.common.segment.media import File as FileSeg

        local = await self.download(cache_dir)
        return FileSeg(file=str(local), file_name=self.name, file_size=self.size)
