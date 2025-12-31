"""
群组信息查询 API 测试用例
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


def get_attr_safe(obj, attr, default=None):
    """安全获取属性"""
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


# ============================================================================
# 测试用例
# ============================================================================

class GroupInfoTests(APITestSuite):
    """群组信息查询 API 测试"""

    suite_name = "Group Info API"
    suite_description = "测试群组信息查询相关 API"

    @staticmethod
    @test_case(
        name="获取群列表",
        description="获取 Bot 加入的所有群列表",
        category="group",
        api_endpoint="/get_group_list",
        expected="返回群列表，每个群包含 group_id、group_name 等信息",
        tags=["group", "query"],
        show_result=True,
    )
    async def test_get_group_list(api, data):
        """获取群列表"""
        result = await api.get_group_list()
        
        # 断言检查
        assert result is not None, "返回结果不能为空"
        
        # 处理不同返回类型
        groups = result if isinstance(result, list) else getattr(result, 'groups', result)
        if hasattr(groups, '__iter__') and not isinstance(groups, (str, dict)):
            groups = list(groups)
        else:
            groups = [groups] if groups else []
        
        sample = groups[:5] if len(groups) > 5 else groups
        return {
            "total_count": len(groups),
            "sample": [
                {
                    "group_id": getattr(g, 'group_id', None) or (g.get("group_id") if isinstance(g, dict) else str(g)),
                    "group_name": getattr(g, 'group_name', None) or (g.get("group_name") if isinstance(g, dict) else ""),
                    "member_count": getattr(g, 'member_count', None) or (g.get("member_count") if isinstance(g, dict) else 0),
                }
                for g in sample
            ],
        }

    @staticmethod
    @test_case(
        name="获取群信息",
        description="获取指定群的详细信息",
        category="group",
        api_endpoint="/get_group_info",
        expected="返回群的详细信息",
        tags=["group", "query"],
        show_result=True,
    )
    async def test_get_group_info(api, data):
        """获取群信息"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        result = await api.get_group_info(group_id=int(target_group))
        
        # 断言检查
        assert result is not None, "返回结果不能为空"
        
        # 返回可能是模型对象，转换为字典显示
        if hasattr(result, '__dict__'):
            return {k: v for k, v in vars(result).items() if not k.startswith('_')}
        return result


class GroupMemberTests(APITestSuite):
    """群成员相关 API 测试"""

    suite_name = "Group Member API"
    suite_description = "测试群成员信息和管理 API"

    @staticmethod
    @test_case(
        name="获取群成员列表",
        description="获取指定群的成员列表",
        category="group",
        api_endpoint="/get_group_member_list",
        expected="返回群成员列表",
        tags=["group", "member", "query"],
        show_result=True,
    )
    async def test_get_group_member_list(api, data):
        """获取群成员列表"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        result = await api.get_group_member_list(group_id=int(target_group))
        
        # 断言检查
        assert result is not None, "返回结果不能为空"
        
        # 处理不同返回类型（可能是列表或 GroupMemberList 对象）
        members = result if isinstance(result, list) else getattr(result, 'members', result)
        if hasattr(members, '__iter__') and not isinstance(members, (str, dict)):
            members = list(members)
        else:
            members = [members] if members else []
        
        sample = members[:5] if len(members) > 5 else members
        return {
            "total_count": len(members),
            "sample": [
                {
                    "user_id": getattr(m, 'user_id', None) or (m.get("user_id") if isinstance(m, dict) else str(m)),
                    "nickname": getattr(m, 'nickname', None) or (m.get("nickname") if isinstance(m, dict) else ""),
                    "card": getattr(m, 'card', None) or (m.get("card") if isinstance(m, dict) else ""),
                    "role": getattr(m, 'role', None) or (m.get("role") if isinstance(m, dict) else ""),
                }
                for m in sample
            ],
        }

    @staticmethod
    @test_case(
        name="获取群成员信息",
        description="获取指定群成员的详细信息",
        category="group",
        api_endpoint="/get_group_member_info",
        expected="返回成员详细信息",
        tags=["group", "member", "query"],
        show_result=True,
    )
    async def test_get_group_member_info(api, data):
        """获取群成员信息"""
        target_group = data.get("target_group")
        target_user = data.get("target_user")
        if not target_group or not target_user:
            raise ValueError("需要配置 target_group 和 target_user")

        result = await api.get_group_member_info(
            group_id=int(target_group),
            user_id=int(target_user),
        )
        
        # 断言检查
        assert result is not None, "返回结果不能为空"
        
        # 返回可能是模型对象，转换为字典显示
        if hasattr(result, '__dict__'):
            return {k: v for k, v in vars(result).items() if not k.startswith('_')}
        return result

    @staticmethod
    @test_case(
        name="获取群禁言列表",
        description="获取群内被禁言的成员列表",
        category="group",
        api_endpoint="/get_group_shut_list",
        expected="返回禁言成员列表",
        tags=["group", "member", "query"],
        show_result=True,
    )
    async def test_get_group_shut_list(api, data):
        """获取群禁言列表"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        result = await api.get_group_shut_list(group_id=int(target_group))
        
        # 处理不同返回类型
        members = result if isinstance(result, list) else getattr(result, 'members', result)
        if hasattr(members, '__iter__') and not isinstance(members, (str, dict)):
            members = list(members)
        else:
            members = []
        
        return {
            "count": len(members),
            "list": members[:5] if members else [],
        }


class GroupAlbumTests(APITestSuite):
    """群相册 API 测试"""

    suite_name = "Group Album API"
    suite_description = "测试群相册相关 API（部分 API 可能不被 NapCat 支持）"

    @staticmethod
    @test_case(
        name="获取群相册列表",
        description="获取群相册列表（注意：此 API 可能不被当前版本 NapCat 支持）",
        category="group",
        api_endpoint="/get_group_album_list",
        expected="返回群相册列表",
        tags=["group", "album", "query", "experimental"],
    )
    async def test_get_group_album_list(api, data):
        """获取群相册列表"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        result = await api.get_group_album_list(group_id=int(target_group))
        return {
            "count": len(result) if isinstance(result, list) else "unknown",
            "albums": result[:3] if isinstance(result, list) else result,
        }

    @staticmethod
    @test_case(
        name="上传图片到群相册",
        description="上传图片到群相册（注意：此 API 可能不被当前版本 NapCat 支持）",
        category="group",
        api_endpoint="/upload_image_to_group_album",
        expected="图片上传成功",
        tags=["group", "album", "upload", "experimental"],
        requires_input=True,
    )
    async def test_upload_image_to_group_album(api, data):
        """上传图片到群相册"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        groups_data = data.get("groups", {})
        album_info = groups_data.get("album", {})
        image_path = album_info.get("test_image_path", "/tmp/test_album.png")

        album_id = input(f"请输入相册 ID (留空使用默认): ") or album_info.get("album_id")

        # 创建测试图片（简单的 1x1 PNG）
        import base64
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        with open(image_path, "wb") as f:
            f.write(png_data)

        result = await api.upload_image_to_group_album(
            group_id=int(target_group),
            file=image_path,
            album_id=album_id,
        )
        return {
            "target_group": target_group,
            "image_path": image_path,
            "album_id": album_id,
            "result": result,
        }

    @staticmethod
    @test_case(
        name="群打卡",
        description="群打卡签到",
        category="group",
        api_endpoint="/set_group_sign",
        expected="打卡成功",
        tags=["group", "sign"],
    )
    async def test_set_group_sign(api, data):
        """群打卡"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        result = await api.set_group_sign(group_id=int(target_group))
        return {
            "target_group": target_group,
            "action": "sign",
            "result": result,
        }
