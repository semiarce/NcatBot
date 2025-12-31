"""
私聊消息相关 API 测试用例
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from framework import test_case, APITestSuite


# ============================================================================
# 辅助函数
# ============================================================================

async def send_private_test_message(api, target_user: int) -> str:
    """发送私聊测试消息并返回 message_id"""
    # 使用 post_private_msg 便捷方法
    result = await api.post_private_msg(
        user_id=target_user,
        text="[E2E 测试] 用于转发测试的临时消息",
    )
    # post_private_msg 直接返回 message_id (str)
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

class PrivateMessageTests(APITestSuite):
    """私聊消息 API 测试"""

    suite_name = "Private Message API"
    suite_description = "测试私聊消息发送相关 API"

    @staticmethod
    @test_case(
        name="发送私聊文本消息",
        description="向指定用户发送纯文本私聊消息",
        category="message",
        api_endpoint="/send_private_msg",
        expected="返回 message_id，目标用户应收到消息",
        tags=["private", "text"],
        show_result=True,
    )
    async def test_send_private_text(api, data):
        """发送私聊文本消息"""
        target_user = data.get("target_user")
        if not target_user:
            raise ValueError("需要配置 target_user")

        messages_data = data.get("messages", {})
        content = messages_data.get("text_messages", {}).get("private", {}).get(
            "simple", "[E2E 测试] 私聊文本消息测试"
        )

        result = await api.post_private_msg(
            user_id=int(target_user),
            text=content,
        )
        
        # post_private_msg 直接返回 message_id (str)
        message_id = get_message_id(result)
        assert message_id, "发送消息失败，未获取到 message_id"
        
        return {
            "message_id": message_id,
            "target_user": target_user,
            "content": content,
        }

    @staticmethod
    @test_case(
        name="转发私聊单条消息",
        description="先发送测试消息，然后转发该消息到私聊",
        category="message",
        api_endpoint="/forward_private_single_msg",
        expected="消息转发成功",
        tags=["private", "forward"],
        show_result=True,
    )
    async def test_forward_private_single_msg(api, data):
        """转发私聊单条消息"""
        target_user = data.get("target_user")
        if not target_user:
            raise ValueError("需要配置 target_user")
        
        # 先发送测试消息，send_private_test_message 返回的是 message_id (str)
        message_id = await send_private_test_message(api, int(target_user))
        
        assert message_id, "发送消息失败，未获取到 message_id"

        result = await api.forward_private_single_msg(
            user_id=int(target_user),
            message_id=int(message_id),
        )
        return {
            "target_user": target_user,
            "original_message_id": message_id,
            "result": model_to_dict(result),
        }

    @staticmethod
    @test_case(
        name="上传私聊文件",
        description="上传文件到私聊",
        category="message",
        api_endpoint="/upload_private_file",
        expected="文件上传成功",
        tags=["private", "file"],
        show_result=True,
    )
    async def test_upload_private_file(api, data):
        """上传私聊文件"""
        target_user = data.get("target_user")
        if not target_user:
            raise ValueError("需要配置 target_user")

        friends_data = data.get("friends", {})
        file_info = friends_data.get("private_file", {})
        file_path = file_info.get("test_file_path", "/tmp/test_upload.txt")
        file_name = file_info.get("file_name", "test_e2e_upload.txt")

        # 创建测试文件
        content = file_info.get("test_file_content", "这是一个 E2E 测试文件")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        result = await api.upload_private_file(
            user_id=int(target_user),
            file=file_path,
            name=file_name,
        )
        return {
            "target_user": target_user,
            "file_path": file_path,
            "file_name": file_name,
            "status": "success",
        }

    @staticmethod
    @test_case(
        name="获取私聊文件 URL",
        description="获取私聊文件下载链接（需要有效的 file_id）",
        category="message",
        api_endpoint="/get_private_file_url",
        expected="返回文件下载 URL",
        tags=["private", "file", "skip"],
        show_result=True,
    )
    async def test_get_private_file_url(api, data):
        """获取私聊文件 URL"""
        # 这个 API 需要有效的 file_id，但上传 API 不返回 file_id
        # 跳过此测试
        return {
            "status": "skipped",
            "reason": "上传 API 不返回 file_id，无法测试",
        }

    @staticmethod
    @test_case(
        name="发送私聊文件（post）",
        description="通过 post 方式发送私聊文件",
        category="message",
        api_endpoint="/post_private_file",
        expected="文件发送成功",
        tags=["private", "file"],
        show_result=True,
    )
    async def test_post_private_file(api, data):
        """发送私聊文件"""
        target_user = data.get("target_user")
        if not target_user:
            raise ValueError("需要配置 target_user")

        files_data = data.get("files", {})
        file_info = files_data.get("private_files", {})
        file_path = file_info.get("test_file_path", "/tmp/test_private_file.txt")

        # 创建测试文件
        content = file_info.get("test_file_content", "这是一个 E2E 测试私聊文件")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        result = await api.post_private_file(
            user_id=int(target_user),
            file=file_path,
        )
        return {
            "target_user": target_user,
            "file_path": file_path,
            "message_id": result,
        }

    @staticmethod
    @test_case(
        name="发送戳一戳",
        description="发送戳一戳消息",
        category="message",
        api_endpoint="/send_poke",
        expected="戳一戳发送成功",
        tags=["private", "poke"],
    )
    async def test_send_poke(api, data):
        """发送戳一戳"""
        target_user = data.get("target_user")
        if not target_user:
            raise ValueError("需要配置 target_user")

        await api.send_poke(user_id=int(target_user))
        return {
            "target_user": target_user,
            "action": "poke",
        }
