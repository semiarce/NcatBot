"""
群管理操作 API 测试用例
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from framework import test_case, APITestSuite


class GroupAdminTests(APITestSuite):
    """群管理操作 API 测试"""

    suite_name = "Group Admin API"
    suite_description = "测试群管理操作相关 API（需要管理员权限）"

    @staticmethod
    @test_case(
        name="设置群名片",
        description="设置指定群成员的群名片",
        category="group",
        api_endpoint="/set_group_card",
        expected="成功设置群名片",
        tags=["group", "admin", "member"],
        requires_input=True,
    )
    async def test_set_group_card(api, data):
        """设置群名片"""
        target_group = data.get("target_group")
        target_user = data.get("target_user")
        if not target_group or not target_user:
            raise ValueError("需要配置 target_group 和 target_user")

        groups_data = data.get("groups", {})
        card = groups_data.get("member_operations", {}).get("card", "E2E测试名片")
        new_card = input(f"请输入新的群名片 (默认: {card}): ") or card

        await api.set_group_card(
            group_id=int(target_group),
            user_id=int(target_user),
            card=new_card,
        )
        return {
            "group_id": target_group,
            "user_id": target_user,
            "new_card": new_card,
        }

    @staticmethod
    @test_case(
        name="群组禁言",
        description="禁言指定群成员",
        category="group",
        api_endpoint="/set_group_ban",
        expected="目标成员被禁言",
        tags=["group", "admin", "ban"],
        requires_input=True,
    )
    async def test_set_group_ban(api, data):
        """群组禁言"""
        target_group = data.get("target_group")
        target_user = data.get("target_user")
        if not target_group or not target_user:
            raise ValueError("需要配置 target_group 和 target_user")

        groups_data = data.get("groups", {})
        default_duration = groups_data.get("member_operations", {}).get(
            "ban_duration", 60
        )
        duration = input(f"请输入禁言时长秒 (0=解除, 默认{default_duration}): ")
        duration = int(duration) if duration else default_duration

        await api.set_group_ban(
            group_id=int(target_group),
            user_id=int(target_user),
            duration=duration,
        )
        return {
            "group_id": target_group,
            "user_id": target_user,
            "duration": duration,
            "action": "ban" if duration > 0 else "unban",
        }

    @staticmethod
    @test_case(
        name="全员禁言",
        description="开启或关闭群全员禁言",
        category="group",
        api_endpoint="/set_group_whole_ban",
        expected="群全员禁言状态改变",
        tags=["group", "admin", "ban"],
        requires_input=True,
    )
    async def test_set_group_whole_ban(api, data):
        """全员禁言"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        enable = input("开启全员禁言? (y/n, 默认n): ").lower() == "y"

        await api.set_group_whole_ban(
            group_id=int(target_group),
            enable=enable,
        )
        return {
            "group_id": target_group,
            "whole_ban": enable,
        }

    @staticmethod
    @test_case(
        name="踢出群成员",
        description="将成员踢出群（谨慎使用）",
        category="group",
        api_endpoint="/set_group_kick",
        expected="成员被踢出群",
        tags=["group", "admin", "dangerous"],
        requires_input=True,
    )
    async def test_set_group_kick(api, data):
        """踢出群成员"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        target_user = input("请输入要踢出的成员 QQ 号: ")
        confirm = input(f"确认踢出 {target_user}? (yes/no): ")

        if confirm.lower() != "yes":
            raise Exception("用户取消操作")

        reject_add = input("是否拒绝此人再次加群? (y/n, 默认n): ").lower() == "y"

        await api.set_group_kick(
            group_id=int(target_group),
            user_id=int(target_user),
            reject_add_request=reject_add,
        )
        return {
            "group_id": target_group,
            "user_id": target_user,
            "reject_add": reject_add,
        }

    @staticmethod
    @test_case(
        name="设置群管理员",
        description="设置或取消群管理员",
        category="group",
        api_endpoint="/set_group_admin",
        expected="管理员状态改变",
        tags=["group", "admin", "dangerous"],
        requires_input=True,
    )
    async def test_set_group_admin(api, data):
        """设置群管理员"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        target_user = input("请输入目标成员 QQ 号: ")
        enable = input("设为管理员? (y/n): ").lower() == "y"

        await api.set_group_admin(
            group_id=int(target_group),
            user_id=int(target_user),
            enable=enable,
        )
        return {
            "group_id": target_group,
            "user_id": target_user,
            "admin": enable,
        }

    @staticmethod
    @test_case(
        name="设置群头衔",
        description="设置群成员专属头衔",
        category="group",
        api_endpoint="/set_group_special_title",
        expected="头衔设置成功",
        tags=["group", "admin", "member"],
        requires_input=True,
    )
    async def test_set_group_special_title(api, data):
        """设置群头衔"""
        target_group = data.get("target_group")
        target_user = data.get("target_user")
        if not target_group or not target_user:
            raise ValueError("需要配置 target_group 和 target_user")

        groups_data = data.get("groups", {})
        default_title = groups_data.get("member_operations", {}).get(
            "special_title", "E2E测试头衔"
        )
        title = input(f"请输入头衔 (默认: {default_title}): ") or default_title

        await api.set_group_special_title(
            group_id=int(target_group),
            user_id=int(target_user),
            special_title=title,
        )
        return {
            "group_id": target_group,
            "user_id": target_user,
            "special_title": title,
        }


class EssenceMessageTests(APITestSuite):
    """精华消息 API 测试"""

    suite_name = "Essence Message API"
    suite_description = "测试精华消息相关 API"

    @staticmethod
    @test_case(
        name="获取精华消息列表",
        description="获取群精华消息列表",
        category="group",
        api_endpoint="/get_essence_msg_list",
        expected="返回精华消息列表",
        tags=["group", "essence", "query"],
        show_result=True,
    )
    async def test_get_essence_msg_list(api, data):
        """获取精华消息列表"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        result = await api.get_essence_msg_list(group_id=int(target_group))
        return {
            "count": len(result) if isinstance(result, list) else "unknown",
            "sample": result[:3] if isinstance(result, list) else result,
        }

    @staticmethod
    @test_case(
        name="设置精华消息",
        description="将消息设为精华",
        category="group",
        api_endpoint="/set_essence_msg",
        expected="消息被设为精华",
        tags=["group", "essence", "admin"],
        requires_input=True,
    )
    async def test_set_essence_msg(api, data):
        """设置精华消息"""
        message_id = input("请输入要设为精华的 message_id: ")

        await api.set_essence_msg(message_id=int(message_id))
        return {
            "message_id": message_id,
            "action": "set_essence",
        }

    @staticmethod
    @test_case(
        name="删除精华消息",
        description="取消消息的精华状态",
        category="group",
        api_endpoint="/delete_essence_msg",
        expected="精华消息被取消",
        tags=["group", "essence", "admin"],
        requires_input=True,
    )
    async def test_delete_essence_msg(api, data):
        """删除精华消息"""
        message_id = input("请输入要取消精华的 message_id: ")

        await api.delete_essence_msg(message_id=int(message_id))
        return {
            "message_id": message_id,
            "action": "delete_essence",
        }
