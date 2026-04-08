"""WUI-09 ~ WUI-14: RecordingEngine captures operations and exports Scenario DSL"""

from ncatbot.webui.recorder import RecordingEngine


def test_recording_lifecycle():
    """WUI-09: RecordingEngine start/stop/is_recording"""
    rec = RecordingEngine()
    assert not rec.is_recording
    rec.start()
    assert rec.is_recording
    rec.stop()
    assert not rec.is_recording


def test_record_inject_and_settle():
    """WUI-10: RecordingEngine captures inject+settle pairs as steps"""
    rec = RecordingEngine()
    rec.start()
    rec.record_inject("message.group", {"text": "/help"})
    rec.record_settle(
        [
            {
                "action": "send_group_msg",
                "params": {"message": [{"type": "text", "data": {"text": "帮助"}}]},
            }
        ]
    )
    assert len(rec.steps) == 1
    assert rec.steps[0].event_type == "message.group"


def test_record_ignores_when_not_recording():
    """WUI-11: RecordingEngine ignores calls when not recording"""
    rec = RecordingEngine()
    rec.record_inject("message.group", {"text": "hi"})
    rec.record_settle([])
    assert len(rec.steps) == 0


def test_record_settle_without_inject():
    """WUI-12: RecordingEngine ignores settle without preceding inject"""
    rec = RecordingEngine()
    rec.start()
    rec.record_settle([{"action": "foo", "params": {}}])
    assert len(rec.steps) == 0


def test_start_clears_previous_steps():
    """WUI-13: RecordingEngine.start() clears previous recording"""
    rec = RecordingEngine()
    rec.start()
    rec.record_inject("message.group", {"text": "hi"})
    rec.record_settle([])
    assert len(rec.steps) == 1
    rec.start()
    assert len(rec.steps) == 0


def test_export_scenario_dsl():
    """WUI-14: RecordingEngine exports valid Scenario DSL code"""
    rec = RecordingEngine()
    rec.start()
    rec.record_inject("message.group", {"text": "/ping", "group_id": "123"})
    rec.record_settle(
        [
            {
                "action": "send_group_msg",
                "params": {"message": [{"type": "text", "data": {"text": "pong"}}]},
            }
        ]
    )
    rec.record_inject("notice.poke", {"user_id": "111", "target_id": "222"})
    rec.record_settle([])
    rec.stop()

    code = rec.export_scenario_dsl()
    assert "from ncatbot.testing import TestHarness, Scenario" in code
    assert "from ncatbot.testing.factories import qq" in code
    assert "qq.group_message" in code
    assert "text='/ping'" in code
    assert "qq.poke" in code
    assert "scenario.assert_api_called" in code
    assert "scenario.assert_api_text" in code
    assert "'pong'" in code
    assert "await scenario.run(h)" in code
