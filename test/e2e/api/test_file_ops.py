"""
群文件操作 API 测试用例
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from framework import test_case, APITestSuite


class GroupFileOperationTests(APITestSuite):
    """群文件操作 API 测试"""

    suite_name = "Group File Operation API"
    suite_description = "测试群文件上传、移动、重命名等操作"

    @staticmethod
    @test_case(
        name="上传群文件",
        description="上传文件到群文件",
        category="file",
        api_endpoint="/upload_group_file",
        expected="文件上传成功",
        tags=["file", "upload"],
    )
    async def test_upload_group_file(api, data):
        """上传群文件"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        files_data = data.get("files", {})
        file_info = files_data.get("group_files", {})
        file_path = file_info.get("test_file_path", "/tmp/test_group_file.txt")

        content = file_info.get("test_file_content", "这是一个 E2E 测试群文件")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        result = await api.upload_group_file(
            group_id=int(target_group),
            file=file_path,
            name="e2e_test_file.txt",
        )
        return {"target_group": target_group, "file_path": file_path, "result": result}

    @staticmethod
    @test_case(
        name="发送群文件（post）",
        description="通过 post 方式发送群文件",
        category="file",
        api_endpoint="/post_group_file",
        expected="文件发送成功",
        tags=["file", "upload"],
    )
    async def test_post_group_file(api, data):
        """发送群文件"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        files_data = data.get("files", {})
        file_info = files_data.get("group_files", {})
        file_path = file_info.get("test_file_path", "/tmp/test_group_file.txt")

        content = file_info.get("test_file_content", "这是一个 E2E 测试群文件")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        result = await api.post_group_file(group_id=int(target_group), file=file_path)
        return {"target_group": target_group, "file_path": file_path, "result": result}

    @staticmethod
    @test_case(
        name="创建群文件夹",
        description="在群文件中创建文件夹",
        category="file",
        api_endpoint="/create_group_file_folder",
        expected="文件夹创建成功",
        tags=["file", "folder"],
    )
    async def test_create_group_file_folder(api, data):
        """创建群文件夹"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        files_data = data.get("files", {})
        folder_name = files_data.get("group_files", {}).get(
            "test_folder_name", "E2E测试文件夹"
        )

        result = await api.create_group_file_folder(
            group_id=int(target_group), name=folder_name
        )
        return {"target_group": target_group, "folder_name": folder_name, "result": result}

    @staticmethod
    @test_case(
        name="移动群文件",
        description="移动群文件到指定文件夹",
        category="file",
        api_endpoint="/move_group_file",
        expected="文件移动成功",
        tags=["file", "operation"],
        requires_input=True,
    )
    async def test_move_group_file(api, data):
        """移动群文件"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        file_id = input("请输入要移动的文件 ID: ")
        parent_id = input("请输入源文件夹 ID (根目录为空): ") or "/"
        target_id = input("请输入目标文件夹 ID: ")

        result = await api.move_group_file(
            group_id=int(target_group),
            file_id=file_id,
            parent_directory=parent_id,
            target_directory=target_id,
        )
        return {"file_id": file_id, "from": parent_id, "to": target_id, "result": result}

    @staticmethod
    @test_case(
        name="重命名群文件",
        description="重命名群文件",
        category="file",
        api_endpoint="/rename_group_file",
        expected="文件重命名成功",
        tags=["file", "operation"],
        requires_input=True,
    )
    async def test_rename_group_file(api, data):
        """重命名群文件"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        files_data = data.get("files", {})
        default_name = files_data.get("group_files", {}).get(
            "rename_to", "renamed_e2e_test.txt"
        )

        file_id = input("请输入要重命名的文件 ID: ")
        parent_id = input("请输入文件所在文件夹 ID (根目录为空): ") or "/"
        new_name = input(f"请输入新文件名 (默认: {default_name}): ") or default_name

        result = await api.rename_group_file(
            group_id=int(target_group),
            file_id=file_id,
            parent_directory=parent_id,
            new_name=new_name,
        )
        return {"file_id": file_id, "new_name": new_name, "result": result}

    @staticmethod
    @test_case(
        name="删除群文件",
        description="删除群文件",
        category="file",
        api_endpoint="/delete_group_file",
        expected="文件删除成功",
        tags=["file", "operation", "dangerous"],
        requires_input=True,
    )
    async def test_delete_group_file(api, data):
        """删除群文件"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        file_id = input("请输入要删除的文件 ID: ")
        busid = input("请输入 busid (默认0): ") or "0"

        await api.delete_group_file(
            group_id=int(target_group), file_id=file_id, busid=int(busid)
        )
        return {"file_id": file_id, "action": "deleted"}

    @staticmethod
    @test_case(
        name="删除群文件夹",
        description="删除群文件夹",
        category="file",
        api_endpoint="/delete_group_folder",
        expected="文件夹删除成功",
        tags=["file", "folder", "dangerous"],
        requires_input=True,
    )
    async def test_delete_group_folder(api, data):
        """删除群文件夹"""
        target_group = data.get("target_group")
        if not target_group:
            raise ValueError("需要配置 target_group")

        folder_id = input("请输入要删除的文件夹 ID: ")

        await api.delete_group_folder(group_id=int(target_group), folder_id=folder_id)
        return {"folder_id": folder_id, "action": "deleted"}
