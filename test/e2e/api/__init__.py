"""
API 测试套件模块

包含所有分类的 API 测试用例。
"""

from .test_account import AccountAPITests
from .test_friend import FriendAPITests, FriendRequestTests
from .test_message_private import PrivateMessageTests
from .test_message_group import GroupMessageTests
from .test_message_ops import MessageOperationTests
from .test_message_forward import ForwardMessageTests
from .test_group_info import GroupInfoTests, GroupMemberTests, GroupAlbumTests
from .test_group_admin import GroupAdminTests, EssenceMessageTests
from .test_file_query import GroupFileQueryTests
from .test_file_ops import GroupFileOperationTests

# 所有测试套件
ALL_TEST_SUITES = [
    # 账号相关
    AccountAPITests,
    # 好友相关
    FriendAPITests,
    FriendRequestTests,
    # 消息相关
    PrivateMessageTests,
    GroupMessageTests,
    MessageOperationTests,
    ForwardMessageTests,
    # 群组相关
    GroupInfoTests,
    GroupMemberTests,
    GroupAlbumTests,
    GroupAdminTests,
    EssenceMessageTests,
    # 文件相关
    GroupFileQueryTests,
    GroupFileOperationTests,
]

__all__ = [
    # 测试套件
    "AccountAPITests",
    "FriendAPITests",
    "FriendRequestTests",
    "PrivateMessageTests",
    "GroupMessageTests",
    "MessageOperationTests",
    "ForwardMessageTests",
    "GroupInfoTests",
    "GroupMemberTests",
    "GroupAlbumTests",
    "GroupAdminTests",
    "EssenceMessageTests",
    "GroupFileQueryTests",
    "GroupFileOperationTests",
    # 常量
    "ALL_TEST_SUITES",
]
