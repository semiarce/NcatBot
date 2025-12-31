"""
消息操作和查询 API 测试用例

测试流程：先发送测试消息获取 message_id，然后用于后续操作测试
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from framework import test_case, APITestSuite


# ============================================================================
# 辅助函数
# ============================================================================

async def send_test_message(api, target_group: int) -> str:
    """发送测试消息并返回 message_id"""
    # 使用 post_group_msg 便捷方法
    result = await api.post_group_msg(
        group_id=target_group,
        text="[E2E 测试] 用于查询/操作测试的临时消息",
    )
    # post_group_msg 直接返回 message_id (str)
    return result


def get_message_id(result) -> str:
    """从结果中提取 message_id"""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return str(result.get("message_id", ""))
    if isinstance(result, int):
        return str(result)
    # 尝试从对象属性获取
    msg_id = getattr(result, 'message_id', None)
    if msg_id is not None:
        return str(msg_id)
    return str(result)


def model_to_dict(obj):
    """将模型对象转换为字典"""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, '__dict__'):
        return {k: v for k, v in vars(obj).items() if not k.startswith('_')}
    return str(obj)


# ============================================================================
# 测试用例
# ============================================================================

class MessageQueryTests(APITestSuite):
    """消息查询 API 测试"""

    suite_name = "Message Query API"
    suite_description = "测试消息查询相关 API（自动发送测试消息）"

    @staticmethod
    @test_case(
        name="获取消息详情",
        description="先发送测试消息，然后根据 message_id 获取消息详情",
        category="message",
        api_endpoint="/get_msg",
        expected="返回消息的完整信息",
        tags=["query"],
        show_result=True,
    )
    async def test_get_msg(api, data):
        """获取消息详情"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")
        
        # 先发送测试消息，send_test_message 返回的是 message_id (str)
        message_id = await send_test_message(api, int(target_group))
        
        assert message_id, "发送消息失败，未获取到 message_id"
        
        # 获取消息详情
        result = await api.get_msg(message_id=int(message_id))
        
        return {
            "test_message_id": message_id,
            "result": model_to_dict(result),
        }

    @staticmethod
    @test_case(
        name="获取群历史消息",
        description="获取指定群的历史消息记录",
        category="message",
        api_endpoint="/get_group_msg_history",
        expected="返回消息历史列表",
        tags=["query", "history"],
        show_result=True,
    )
    async def test_get_group_msg_history(api, data):
        """获取群历史消息"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        messages_data = data.get("messages", {})
        count = messages_data.get("history_query", {}).get("count", 10)

        result = await api.get_group_msg_history(
            group_id=int(target_group),
            count=count,
        )

        # 处理返回结果
        if isinstance(result, dict):
            messages = result.get("messages", [])
        elif hasattr(result, 'messages'):
            messages = result.messages
        else:
            messages = []
        
        return {
            "count": len(messages) if messages else 0,
            "sample": [
                {
                    "message_id": getattr(m, 'message_id', None) or (m.get("message_id") if isinstance(m, dict) else None),
                    "sender": getattr(getattr(m, 'sender', None), 'nickname', None) or (m.get("sender", {}).get("nickname") if isinstance(m, dict) else None),
                    "raw_message": str(getattr(m, 'raw_message', None) or (m.get("raw_message", "") if isinstance(m, dict) else ""))[:50],
                }
                for m in (list(messages)[:3] if messages else [])
            ],
        }


class MessageOperationTests(APITestSuite):
    """消息操作 API 测试"""

    suite_name = "Message Operation API"
    suite_description = "测试消息撤回、表情回应等操作"

    @staticmethod
    @test_case(
        name="撤回消息",
        description="先发送测试消息，然后撤回该消息",
        category="message",
        api_endpoint="/delete_msg",
        expected="消息被成功撤回",
        tags=["operation"],
        show_result=True,
    )
    async def test_delete_msg(api, data):
        """撤回消息"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")
        
        # 先发送测试消息，send_test_message 返回的是 message_id (str)
        message_id = await send_test_message(api, int(target_group))
        
        assert message_id, "发送消息失败，未获取到 message_id"
        
        # 撤回消息
        await api.delete_msg(message_id=int(message_id))
        
        return {
            "message_id": message_id,
            "action": "deleted",
            "status": "success",
        }

    @staticmethod
    @test_case(
        name="设置消息表情回应",
        description="先发送测试消息，然后对消息设置表情回应",
        category="message",
        api_endpoint="/set_msg_emoji_like",
        expected="表情回应设置成功",
        tags=["operation", "emoji"],
        show_result=True,
    )
    async def test_set_msg_emoji_like(api, data):
        """设置消息表情回应"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")
        
        # 先发送测试消息，send_test_message 返回的是 message_id (str)
        message_id = await send_test_message(api, int(target_group))
        
        assert message_id, "发送消息失败，未获取到 message_id"
        
        # 设置表情回应（使用笑脸表情 128516）
        emoji_id = 128516
        await api.set_msg_emoji_like(
            message_id=int(message_id),
            emoji_id=emoji_id,
        )
        
        return {
            "message_id": message_id,
            "emoji_id": emoji_id,
            "action": "emoji_like",
            "status": "success",
        }

    @staticmethod
    @test_case(
        name="获取消息表情回应",
        description="先发送测试消息并设置表情，然后获取表情回应列表",
        category="message",
        api_endpoint="/fetch_emoji_like",
        expected="返回表情回应列表",
        tags=["query", "emoji"],
        show_result=True,
    )
    async def test_fetch_emoji_like(api, data):
        """获取消息表情回应"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")
        
        # 先发送测试消息，send_test_message 返回的是 message_id (str)
        message_id = await send_test_message(api, int(target_group))
        
        assert message_id, "发送消息失败，未获取到 message_id"
        
        # 先设置一个表情回应
        emoji_id = 128516
        emoji_type = 1
        try:
            await api.set_msg_emoji_like(
                message_id=int(message_id),
                emoji_id=emoji_id,
            )
        except Exception:
            pass  # 忽略设置失败
        
        # 获取表情回应
        result = await api.fetch_emoji_like(
            message_id=int(message_id),
            emoji_id=emoji_id,
            emoji_type=emoji_type,
        )
        
        return {
            "message_id": message_id,
            "emoji_id": emoji_id,
            "emoji_type": emoji_type,
            "result": model_to_dict(result),
        }
