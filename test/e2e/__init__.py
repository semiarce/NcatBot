"""
端到端测试模块
"""

from pathlib import Path

E2E_ROOT = Path(__file__).parent
DATA_DIR = E2E_ROOT / "data"

__all__ = ["E2E_ROOT", "DATA_DIR"]
