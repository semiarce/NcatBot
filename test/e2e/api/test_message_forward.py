"""
转发消息 API 测试用例
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from framework import test_case, APITestSuite


# ============================================================================
# 辅助函数
# ============================================================================

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

class ForwardMessageTests(APITestSuite):
    """转发消息 API 测试"""

    suite_name = "Forward Message API"
    suite_description = "测试转发消息相关 API"

    @staticmethod
    @test_case(
        name="发送合并转发消息",
        description="发送合并转发消息到群",
        category="message",
        api_endpoint="/send_forward_msg",
        expected="合并转发消息发送成功",
        tags=["forward"],
        show_result=True,
    )
    async def test_send_forward_msg(api, data):
        """发送合并转发消息"""
        from ncatbot.core.helper import ForwardConstructor
        
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        # 使用 ForwardConstructor 构建转发消息
        fc = ForwardConstructor(user_id="10000", nickname="E2E测试")
        fc.attach_text("[E2E 测试] 转发消息第一条")
        fc.attach_text("[E2E 测试] 转发消息第二条")
        
        forward = fc.to_forward()
        
        result = await api.post_group_forward_msg(
            group_id=int(target_group),
            forward=forward,
        )
        return {
            "target_group": target_group,
            "node_count": len(forward.content) if forward.content else 0,
            "message_id": result,
        }

    @staticmethod
    @test_case(
        name="发送群合并转发消息（post）",
        description="通过 post 方式发送群合并转发消息",
        category="message",
        api_endpoint="/post_group_forward_msg",
        expected="合并转发消息发送成功",
        tags=["forward"],
        show_result=True,
    )
    async def test_post_group_forward_msg(api, data):
        """发送群合并转发消息"""
        from ncatbot.core.helper import ForwardConstructor
        
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        # 使用 ForwardConstructor 构建转发消息
        fc = ForwardConstructor(user_id="10000", nickname="E2E测试")
        fc.attach_text("[E2E 测试] POST 转发消息测试")
        
        forward = fc.to_forward()
        
        result = await api.post_group_forward_msg(
            group_id=int(target_group),
            forward=forward,
        )
        return {
            "target_group": target_group,
            "message_id": result,
        }

    @staticmethod
    @test_case(
        name="通过 ID 发送群合并转发消息",
        description="先发送转发消息获取 res_id，然后通过 ID 转发（API 可能不支持）",
        category="message",
        api_endpoint="/send_group_forward_msg_by_id",
        expected="合并转发消息发送成功",
        tags=["forward", "skip"],
        show_result=True,
    )
    async def test_send_group_forward_msg_by_id(api, data):
        """通过 ID 发送群合并转发消息"""
        # 这个 API 需要获取到之前发送的转发消息的 res_id
        # 但 post_group_forward_msg 只返回 message_id，不返回 res_id
        # 跳过此测试
        return {
            "status": "skipped",
            "reason": "API 不返回 res_id，无法测试",
        }

    @staticmethod
    @test_case(
        name="获取转发消息内容",
        description="获取转发消息内容（需要 res_id）",
        category="message",
        api_endpoint="/get_forward_msg",
        expected="返回转发消息内容",
        tags=["forward", "query", "skip"],
        show_result=True,
    )
    async def test_get_forward_msg(api, data):
        """获取转发消息内容"""
        # 这个 API 需要 res_id，但我们无法获取
        return {
            "status": "skipped",
            "reason": "需要 res_id，无法测试",
        }
