"""
好友相关 API 测试用例
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from framework import test_case, APITestSuite


# ============================================================================
# 验证器函数
# ============================================================================

def validate_friend_list(result):
    """验证好友列表"""
    if result is None:
        return (False, "返回结果为空")
    if not isinstance(result.get("total_count"), int):
        return (False, "total_count 应为整数")
    if result.get("total_count") < 0:
        return (False, "total_count 不能为负数")
    return (True, "")


def validate_list_response(result):
    """验证列表类型响应"""
    if result is None:
        return (False, "返回结果为空")
    count = result.get("count")
    if count is None:
        return (False, "缺少 count 字段")
    return (True, "")


def validate_stranger_info(result):
    """验证陌生人信息"""
    if result is None:
        return (False, "返回结果为空")
    if not isinstance(result, dict):
        return (False, f"返回类型错误: {type(result)}")
    return (True, "")


def validate_action_result(result):
    """验证操作结果"""
    if result is None:
        return (False, "返回结果为空")
    if not result.get("action"):
        return (False, "缺少 action 字段")
    return (True, "")


# ============================================================================
# 测试用例
# ============================================================================

class FriendAPITests(APITestSuite):
    """好友相关 API 测试"""

    suite_name = "Friend API"
    suite_description = "测试好友管理相关 API"

    @staticmethod
    @test_case(
        name="获取好友列表",
        description="获取当前账号的好友列表",
        category="friend",
        api_endpoint="/get_friend_list",
        expected="返回好友列表，每个好友包含 user_id、nickname 等信息",
        tags=["friend", "query"],
        validator=validate_friend_list,
        show_result=True,
    )
    async def test_get_friend_list(api, data):
        """获取好友列表"""
        result = await api.get_friend_list()
        
        # 断言检查
        assert result is not None, "返回结果不能为空"
        assert isinstance(result, list), f"结果应为列表类型，实际: {type(result)}"
        
        sample = result[:5] if len(result) > 5 else result
        return {
            "total_count": len(result),
            "sample": [
                {"user_id": f.get("user_id"), "nickname": f.get("nickname")}
                for f in sample
            ],
        }

    @staticmethod
    @test_case(
        name="获取好友列表（带分类）",
        description="获取好友列表及分类信息",
        category="friend",
        api_endpoint="/get_friends_with_cat",
        expected="返回包含分类信息的好友列表",
        tags=["friend", "query"],
        validator=validate_list_response,
        show_result=True,
    )
    async def test_get_friends_with_cat(api, data):
        """获取好友列表（带分类）"""
        result = await api.get_friends_with_cat()
        
        # 断言检查
        assert result is not None, "返回结果不能为空"
        
        if isinstance(result, list):
            return {
                "count": len(result),
                "sample": result[:3],
            }
        return {"count": 0, "raw": str(result)[:200]}

    @staticmethod
    @test_case(
        name="获取最近联系人",
        description="获取最近的聊天联系人列表",
        category="friend",
        api_endpoint="/get_recent_contact",
        expected="返回最近联系人列表",
        tags=["contact", "query"],
        validator=validate_list_response,
        show_result=True,
    )
    async def test_get_recent_contact(api, data):
        """获取最近联系人"""
        result = await api.get_recent_contact()
        
        # 断言检查
        assert result is not None, "返回结果不能为空"
        
        if isinstance(result, list):
            return {
                "count": len(result),
                "sample": result[:3],
            }
        return {"count": 0, "raw": str(result)[:200]}

    @staticmethod
    @test_case(
        name="获取陌生人信息",
        description="获取指定 QQ 号的用户信息",
        category="friend",
        api_endpoint="/get_stranger_info",
        expected="返回用户的 user_id、nickname、sex、age 等信息",
        tags=["friend", "query"],
        validator=validate_stranger_info,
        show_result=True,
    )
    async def test_get_stranger_info(api, data):
        """获取陌生人信息"""
        target_user = data.get("target_user")
        if not target_user:
            raise ValueError("需要配置 target_user")

        result = await api.get_stranger_info(user_id=int(target_user))
        
        # 断言检查
        assert result is not None, "返回结果不能为空"
        
        return result

    @staticmethod
    @test_case(
        name="发送好友赞",
        description="给指定好友点赞",
        category="friend",
        api_endpoint="/send_like",
        expected="点赞成功",
        tags=["friend", "action"],
        validator=validate_action_result,
        show_result=True,
    )
    async def test_send_like(api, data):
        """发送好友赞"""
        target_user = data.get("target_user")
        if not target_user:
            raise ValueError("需要配置 target_user")

        friends_data = data.get("friends", {})
        times = friends_data.get("friend_operations", {}).get("send_like_count", 10)

        await api.send_like(user_id=int(target_user), times=times)
        return {
            "user_id": target_user,
            "times": times,
            "action": "send_like",
        }

    @staticmethod
    @test_case(
        name="好友戳一戳",
        description="戳一戳好友",
        category="friend",
        api_endpoint="/friend_poke",
        expected="戳一戳成功",
        tags=["friend", "action"],
        validator=validate_action_result,
        show_result=True,
    )
    async def test_friend_poke(api, data):
        """好友戳一戳"""
        target_user = data.get("target_user")
        if not target_user:
            raise ValueError("需要配置 target_user")

        await api.friend_poke(user_id=int(target_user))
        return {
            "user_id": target_user,
            "action": "friend_poke",
        }

    @staticmethod
    @test_case(
        name="获取好友消息历史",
        description="获取与指定好友的聊天记录",
        category="friend",
        api_endpoint="/get_friend_msg_history",
        expected="返回消息历史列表",
        tags=["friend", "history"],
        show_result=True,
    )
    async def test_get_friend_msg_history(api, data):
        """获取好友消息历史"""
        target_user = data.get("target_user")
        if not target_user:
            raise ValueError("需要配置 target_user")

        friends_data = data.get("friends", {})
        count = friends_data.get("message_history", {}).get("count", 20)

        result = await api.get_friend_msg_history(
            user_id=int(target_user),
            count=count,
        )

        messages = result.get("messages", []) if isinstance(result, dict) else []
        
        # 断言检查
        assert isinstance(messages, list), "messages 应为列表类型"
        
        return {
            "count": len(messages),
            "sample": [
                {
                    "message_id": m.get("message_id"),
                    "content": str(m.get("message", ""))[:50],
                }
                for m in messages[:3]
            ],
        }

        friends_data = data.get("friends", {})
        count = friends_data.get("message_history", {}).get("count", 20)

        result = await api.get_friend_msg_history(
            user_id=int(target_user),
            count=count,
        )

        messages = result.get("messages", []) if isinstance(result, dict) else []
        return {
            "count": len(messages),
            "sample": [
                {
                    "message_id": m.get("message_id"),
                    "content": str(m.get("message", ""))[:50],
                }
                for m in messages[:3]
            ],
        }


class FriendRequestTests(APITestSuite):
    """好友请求相关测试"""

    suite_name = "Friend Request API"
    suite_description = "测试好友申请处理 API"

    @staticmethod
    @test_case(
        name="设置好友申请处理",
        description="处理好友添加请求（需要有待处理的请求）",
        category="friend",
        api_endpoint="/set_friend_add_request",
        expected="好友请求处理成功",
        tags=["friend", "request"],
        requires_input=True,
    )
    async def test_set_friend_add_request(api, data):
        """设置好友申请处理"""
        flag = input("请输入好友请求 flag: ")
        approve = input("是否同意? (y/n, 默认y): ").lower() != "n"

        friends_data = data.get("friends", {})
        remark = friends_data.get("friend_requests", {}).get("remark", "")

        await api.set_friend_add_request(
            flag=flag,
            approve=approve,
            remark=remark if approve else "",
        )
        return {
            "flag": flag,
            "approve": approve,
            "remark": remark,
        }

    @staticmethod
    @test_case(
        name="删除好友",
        description="删除指定好友（谨慎使用）",
        category="friend",
        api_endpoint="/delete_friend",
        expected="好友删除成功",
        tags=["friend", "dangerous"],
        requires_input=True,
    )
    async def test_delete_friend(api, data):
        """删除好友"""
        target_user = input("请输入要删除的好友 QQ 号: ")
        confirm = input(f"确认删除好友 {target_user}? (yes/no): ")

        if confirm.lower() != "yes":
            raise Exception("用户取消操作")

        await api.delete_friend(user_id=int(target_user))
        return {
            "user_id": target_user,
            "action": "deleted",
        }
