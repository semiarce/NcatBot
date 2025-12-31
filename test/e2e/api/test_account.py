"""
账号相关 API 测试用例
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from framework import test_case, APITestSuite


# ============================================================================
# 验证器函数
# ============================================================================

def validate_login_info(result):
    """验证登录信息"""
    if not result:
        return (False, "返回结果为空")
    if not result.get("user_id"):
        return (False, "user_id 不存在或为空")
    if not result.get("nickname"):
        return (False, "nickname 不存在或为空")
    return (True, "")


def validate_status(result):
    """验证状态信息"""
    if not result:
        return (False, "返回结果为空")
    if not isinstance(result, dict):
        return (False, f"返回类型错误: {type(result)}")
    return (True, "")


def validate_version_info(result):
    """验证版本信息"""
    if not result:
        return (False, "返回结果为空")
    if not isinstance(result, dict):
        return (False, f"返回类型错误: {type(result)}")
    return (True, "")


# ============================================================================
# 测试用例
# ============================================================================

class AccountAPITests(APITestSuite):
    """账号相关 API 测试"""

    suite_name = "Account API"
    suite_description = "测试账号信息相关 API"

    @staticmethod
    @test_case(
        name="获取登录信息",
        description="获取当前登录的 QQ 账号基本信息",
        category="account",
        api_endpoint="/get_login_info",
        expected="返回包含 user_id 和 nickname 的信息",
        tags=["basic", "account"],
        validator=validate_login_info,
        show_result=True,
    )
    async def test_get_login_info(api, data):
        """获取登录信息"""
        result = await api.get_login_info()
        
        # 断言检查
        assert result is not None, "返回结果不能为空"
        assert hasattr(result, "user_id"), "结果应包含 user_id 属性"
        assert hasattr(result, "nickname"), "结果应包含 nickname 属性"
        assert result.user_id > 0, "user_id 应该是正整数"
        
        return {
            "user_id": result.user_id,
            "nickname": result.nickname,
        }

    @staticmethod
    @test_case(
        name="获取状态",
        description="获取 NapCat 运行状态信息",
        category="account",
        api_endpoint="/get_status",
        expected="返回 online 状态和 good 状态信息",
        tags=["basic", "status"],
        validator=validate_status,
        show_result=True,
    )
    async def test_get_status(api, data):
        """获取状态"""
        result = await api.get_status()
        
        # 断言检查
        assert result is not None, "返回结果不能为空"
        
        return result

    @staticmethod
    @test_case(
        name="获取版本信息",
        description="获取 NapCat 版本信息",
        category="account",
        api_endpoint="/get_version_info",
        expected="返回 app_name、app_version 等版本信息",
        tags=["basic", "version"],
        validator=validate_version_info,
        show_result=True,
    )
    async def test_get_version_info(api, data):
        """获取版本信息"""
        result = await api.get_version_info()
        
        # 断言检查
        assert result is not None, "返回结果不能为空"
        
        return result
