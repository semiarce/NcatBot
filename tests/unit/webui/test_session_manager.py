"""WUI-05 ~ WUI-08: SessionManager manages multiple HarnessProxy sessions"""

import pytest
from ncatbot.webui.session import SessionManager


async def test_create_and_get_session():
    """WUI-05: SessionManager can create and retrieve sessions"""
    mgr = SessionManager()
    sid = await mgr.create_session(platform="qq")
    assert isinstance(sid, str)
    assert len(sid) == 8
    proxy = mgr.get(sid)
    assert proxy is not None
    await mgr.destroy_all()


async def test_destroy_session():
    """WUI-06: SessionManager can destroy a session"""
    mgr = SessionManager()
    sid = await mgr.create_session(platform="qq")
    await mgr.destroy_session(sid)
    with pytest.raises(KeyError):
        mgr.get(sid)


async def test_cleanup_expired(monkeypatch):
    """WUI-07: SessionManager cleans up expired sessions"""
    mgr = SessionManager()
    mgr.SESSION_TIMEOUT = 0
    sid = await mgr.create_session(platform="qq")
    mgr._last_activity[sid] = 0
    await mgr.cleanup_expired()
    with pytest.raises(KeyError):
        mgr.get(sid)


async def test_get_unknown_session():
    """WUI-08: SessionManager raises KeyError for unknown session"""
    mgr = SessionManager()
    with pytest.raises(KeyError):
        mgr.get("nonexistent")
