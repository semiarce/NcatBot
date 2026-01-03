"""
API 错误类型定义
"""

from __future__ import annotations

import sys
import traceback
from typing import Optional

from ncatbot.utils import get_log, ncatbot_config, NcatBotError

LOG = get_log("API")


class NapCatAPIError(Exception):
    """NapCat API 调用错误"""

    def __init__(self, info: str, retcode: Optional[int] = None):
        LOG.error(f"NapCatAPIError: {info}")
        if ncatbot_config.debug:
            # 检查是否有活动的异常上下文
            if sys.exc_info()[0] is not None:
                LOG.info(f"stacktrace:\n{traceback.format_exc()}")
            else:
                # 没有活动异常时，输出当前调用栈
                LOG.info(f"stacktrace:\n{''.join(traceback.format_stack()[:-1])}")
        self.info = info
        self.retcode = retcode
        super().__init__(info)


class APIValidationError(NcatBotError):
    """API 参数验证错误"""

    logger = LOG

    def __init__(self, message: str):
        super().__init__(f"参数验证失败: {message}")
