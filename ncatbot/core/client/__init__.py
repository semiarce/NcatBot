# 向后兼容：BotClient 已迁移至 ncatbot.app，推荐使用 from ncatbot.app import BotClient

__all__ = ["BotClient"]


def __getattr__(name: str):
    if name == "BotClient":
        from ncatbot.app.client import BotClient

        return BotClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
