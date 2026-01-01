"""
插件配置类型定义

包含：
- PluginConfig: 只读配置字典包装器
- ConfigItem: 配置项元数据封装类
"""

from typing import Any, Dict, Optional, Callable, Iterator, Union, TYPE_CHECKING
from collections.abc import Mapping
import copy

if TYPE_CHECKING:
    from .plugin_config_service import PluginConfigService

# 支持的配置值类型
ConfigValueType = Union[str, int, float, bool, list, dict]


class PluginConfig(Mapping):
    """
    只读配置字典包装器
    
    此类包装插件配置，禁止直接修改（如 config["key"] = value），
    只能通过 update/set 方法更新，这会触发原子写入操作。
    
    使用示例：
        ```python
        # 读取配置（允许）
        value = self.config["key"]
        value = self.config.get("key", default)
        
        # 直接写入（禁止，抛出 TypeError）
        self.config["key"] = value  # TypeError!
        
        # 正确的更新方式
        self.config.update("key", value)      # 更新单个键
        self.config.bulk_update({"k1": v1})   # 批量更新
        ```
    """
    
    def __init__(
        self, 
        plugin_name: str, 
        data: Dict[str, Any],
        config_service: "PluginConfigService"
    ):
        """
        初始化只读配置包装器
        
        Args:
            plugin_name: 插件名称
            data: 配置数据字典（将被深拷贝）
            config_service: 配置服务引用（用于原子写入）
        """
        self._plugin_name = plugin_name
        self._data: Dict[str, Any] = copy.deepcopy(data)
        self._config_service = config_service
    
    # -------------------------------------------------------------------------
    # Mapping 接口实现（只读操作）
    # -------------------------------------------------------------------------
    
    def __getitem__(self, key: str) -> Any:
        """获取配置值"""
        return self._data[key]
    
    def __iter__(self) -> Iterator[str]:
        """迭代配置键"""
        return iter(self._data)
    
    def __len__(self) -> int:
        """返回配置项数量"""
        return len(self._data)
    
    def __contains__(self, key: object) -> bool:
        """检查配置是否存在"""
        return key in self._data
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，不存在返回默认值"""
        return self._data.get(key, default)
    
    def keys(self):
        """返回所有配置键"""
        return self._data.keys()
    
    def values(self):
        """返回所有配置值"""
        return self._data.values()
    
    def items(self):
        """返回所有配置键值对"""
        return self._data.items()
    
    def __repr__(self) -> str:
        return f"PluginConfig({self._plugin_name!r}, {self._data!r})"
    
    # -------------------------------------------------------------------------
    # 禁止的操作（抛出 TypeError）
    # -------------------------------------------------------------------------
    
    def __setitem__(self, key: str, value: Any) -> None:
        """禁止直接设置配置"""
        raise TypeError(
            f"PluginConfig 不支持直接赋值 config[{key!r}] = value。"
            f"请使用 self.set_config({key!r}, value) 或 self.config.update({key!r}, value)"
        )
    
    def __delitem__(self, key: str) -> None:
        """禁止直接删除配置"""
        raise TypeError(
            f"PluginConfig 不支持直接删除 del config[{key!r}]。"
            f"请使用 self.config.remove({key!r})"
        )
    
    # -------------------------------------------------------------------------
    # 允许的写操作（触发原子保存）
    # -------------------------------------------------------------------------
    
    def update(self, key: str, value: Any) -> tuple:
        """
        更新单个配置项（触发原子写入）
        
        Args:
            key: 配置键
            value: 新值
            
        Returns:
            (old_value, new_value) 元组
        """
        # 通过服务设置并触发原子写入
        result = self._config_service.set_atomic(self._plugin_name, key, value)
        # 同步本地数据
        self._data[key] = result[1]
        return result
    
    def remove(self, key: str) -> Any:
        """
        删除配置项（触发原子写入）
        
        Args:
            key: 配置键
            
        Returns:
            被删除的值
        """
        if key not in self._data:
            raise KeyError(key)
        
        old_value = self._data.pop(key)
        self._config_service.delete_config_item(self._plugin_name, key)
        return old_value
    
    def bulk_update(self, updates: Dict[str, Any]) -> None:
        """
        批量更新配置项（单次原子写入）
        
        Args:
            updates: 要更新的配置字典
        """
        if not updates:
            return
        
        self._config_service.set_plugin_config_atomic(self._plugin_name, updates)
        self._data.update(updates)
    
    def _sync_from_service(self) -> None:
        """从服务同步数据（内部使用）"""
        self._data = copy.deepcopy(
            self._config_service._configs.get(self._plugin_name, {})
        )


class ConfigItem:
    """配置项封装类"""
    
    def __init__(
        self,
        name: str,
        default_value: Any,
        description: str,
        value_type: type,
        metadata: Optional[Dict[str, Any]],
        plugin_name: str,
        on_change: Optional[Callable] = None,
    ):
        self.name = name
        self.default_value = default_value
        self.description = description
        self.value_type = value_type
        self.metadata = metadata or {}
        self.plugin_name = plugin_name
        self.on_change = on_change

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ConfigItem):
            return self.name == other.name and self.plugin_name == other.plugin_name
        if isinstance(other, str):
            return self.name == other
        return False

    def parse_value(self, value: Any) -> Any:
        """解析值为目标类型"""
        # dict 和 list 类型直接返回（深拷贝）
        if self.value_type in (dict, list):
            if isinstance(value, self.value_type):
                return copy.deepcopy(value)
            elif isinstance(value, str):
                import json
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, self.value_type):
                        return parsed
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"无法将 {value!r} 转换为 {self.value_type.__name__}")
        
        # bool 类型特殊处理
        if self.value_type is bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                if value.lower() in ["true", "1", "yes", "on"]:
                    return True
                elif value.lower() in ["false", "0", "no", "off"]:
                    return False
            raise ValueError(f"Invalid boolean value: {value}")
        
        # 其他基本类型
        return self.value_type(value)
