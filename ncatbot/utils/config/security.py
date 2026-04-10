"""配置安全工具 — 密码校验与 token 生成。"""

import random
import string
from re import search

# 生成 token 时使用的安全字符子集（URI 友好）
URI_SPECIAL_CHARS = "-_.~!()*"

# 校验时接受的特殊字符范围（包含常见密码特殊字符）
_ACCEPTED_SPECIAL_CHARS = set(URI_SPECIAL_CHARS + "@#$%^&+=!<>?/\\|{}[]`:;',\"")


def strong_password_check(password: str) -> bool:
    """检查密码强度：>=12 位，包含数字、大小写字母、特殊符号。"""
    patterns = [r"\d", "[a-z]", "[A-Z]"]
    return (
        len(password) >= 12
        and all(search(p, password) for p in patterns)
        and any(c in _ACCEPTED_SPECIAL_CHARS for c in password)
    )


def generate_strong_token(length: int = 16) -> str:
    """生成满足强度策略的随机 token。"""
    all_chars = string.ascii_letters + string.digits + URI_SPECIAL_CHARS
    while True:
        token = "".join(random.choice(all_chars) for _ in range(length))
        if strong_password_check(token):
            return token
