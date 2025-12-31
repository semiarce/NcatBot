"""
群文件查询 API 测试用例
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from framework import test_case, APITestSuite


class GroupFileQueryTests(APITestSuite):
    """群文件查询 API 测试"""

    suite_name = "Group File Query API"
    suite_description = "测试群文件查询相关 API"

    @staticmethod
    @test_case(
        name="获取群根目录文件",
        description="获取群文件根目录下的文件列表",
        category="file",
        api_endpoint="/get_group_root_files",
        expected="返回群文件根目录列表",
        tags=["file", "query"],
    )
    async def test_get_group_root_files(api, data):
        """获取群根目录文件"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        result = await api.get_group_root_files(group_id=int(target_group))
        files = result.get("files", [])[:5] if isinstance(result, dict) else []
        folders = result.get("folders", [])[:5] if isinstance(result, dict) else []
        return {"files": files, "folders": folders}

    @staticmethod
    @test_case(
        name="获取文件夹内文件",
        description="获取指定文件夹内的文件列表",
        category="file",
        api_endpoint="/get_group_files_by_folder",
        expected="返回文件夹内的文件列表",
        tags=["file", "query"],
        requires_input=True,
    )
    async def test_get_group_files_by_folder(api, data):
        """获取文件夹内文件"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        folder_id = input("请输入文件夹 ID: ")

        result = await api.get_group_files_by_folder(
            group_id=int(target_group),
            folder_id=folder_id,
        )
        files = result.get("files", [])[:5] if isinstance(result, dict) else []
        folders = result.get("folders", [])[:5] if isinstance(result, dict) else []
        return {"folder_id": folder_id, "files": files, "folders": folders}

    @staticmethod
    @test_case(
        name="获取群文件 URL",
        description="获取群文件的下载链接",
        category="file",
        api_endpoint="/get_group_file_url",
        expected="返回文件下载 URL",
        tags=["file", "query"],
        requires_input=True,
    )
    async def test_get_group_file_url(api, data):
        """获取群文件 URL"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        file_id = input("请输入文件 ID: ")
        busid = input("请输入 busid (默认0): ") or "0"

        result = await api.get_group_file_url(
            group_id=int(target_group),
            file_id=file_id,
            busid=int(busid),
        )
        return {"file_id": file_id, "url": result}

    @staticmethod
    @test_case(
        name="获取文件信息",
        description="获取文件详细信息",
        category="file",
        api_endpoint="/get_file",
        expected="返回文件详细信息",
        tags=["file", "query"],
        requires_input=True,
    )
    async def test_get_file(api, data):
        """获取文件信息"""
        file_id = input("请输入文件 ID: ")
        result = await api.get_file(file_id=file_id)
        return result
