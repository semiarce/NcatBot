"""
配置混入类

提供插件配置的便捷接口，实际配置管理委托给 PluginConfigService。
此类仅作为接口层，所有配置操作都通过服务完成。

采用"严格的写时保存"策略：
- 每次写配置时立即持久化
- self.config 是只读字典，不允许直接修改
- 必须通过 set_config() 或 self.config.update() 方法更新
"""

from typing import Any, Dict, Union, Callable, Optional, TYPE_CHECKING
from ncatbot.utils import get_log

if TYPE_CHECKING:
    from ncatbot.core.service import ServiceManager
    from ncatbot.core.service.builtin import ConfigItem, PluginConfig

LOG = get_log("ConfigMixin")


class ConfigMixin:
    """
    配置混入类
    
    为插件提供便捷的配置注册和访问接口。
    所有配置操作都委托给 PluginConfigService，此类仅提供接口封装。
    
    配置策略：
    - self.config 是只读字典（PluginConfig），禁止直接赋值
    - 读取配置：self.config["key"] 或 self.get_config("key")
    - 写入配置：self.set_config("key", value) 或 self.config.update("key", value)
    - 每次写入会触发原子保存到文件
    
    使用示例：
        ```python
        class MyPlugin(NcatBotPlugin):
            async def on_load(self):
                # 注册配置
                self.register_config(
                    name="api_key",
                    default_value="",
                    description="API 密钥",
                    value_type=str
                )
                
                # 读取配置（允许）
                api_key = self.config["api_key"]
                api_key = self.get_config("api_key")
                
                # 直接写入（禁止，会抛出 TypeError）
                self.config["api_key"] = "xxx"  # TypeError!
                
                # 正确的写入方式（触发原子保存）
                self.set_config("api_key", "new_value")
                self.config.update("api_key", "new_value")
        ```
    """
    
    # 类型提示（实际属性由 BasePlugin 提供）
    name: str
    config: Union[dict, "PluginConfig"]
    services: "ServiceManager"
    
    @property
    def _config_service(self):
        """获取配置服务（内部使用）"""
        return self.services.plugin_config if self.services else None
    
    def get_registered_configs(self) -> Dict[str, "ConfigItem"]:
        """获取本插件所有已注册的配置项"""
        config_service = self._config_service
        if config_service:
            return config_service.get_registered_configs(self.name)
        return {}

    def register_config(
        self,
        name: str,
        default_value: Any = None,
        description: str = "",
        value_type: type = str,
        metadata: Dict[str, Any] = None,
        on_change: Callable = None,
        *args,
        **kwargs,
    ) -> Optional["ConfigItem"]:
        """
        注册一个配置项
        
        注册后配置会自动添加到 self.config 中，无需手动同步。
        
        Args:
            name: 配置项名称
            default_value: 默认值（必须）
            description: 配置描述
            value_type: 值类型（支持 str, int, float, bool, dict, list）
            metadata: 额外元数据
            on_change: 值变更回调
            
        Returns:
            ConfigItem 实例
            
        Raises:
            TypeError: 如果未提供 default_value
            ValueError: 如果配置项已存在
        """
        # 兼容旧版参数
        if "default" in kwargs:
            default_value = kwargs["default"]

        if default_value is None:
            raise TypeError(
                "ConfigMixin.register_config() missing 1 required positional argument: 'default_value'"
            )

        LOG.debug(f"插件 {self.name} 注册配置 {name}")
        
        config_service = self._config_service
        if config_service:
            config_item = config_service.register_config(
                plugin_name=self.name,
                name=name,
                default_value=default_value,
                description=description,
                value_type=value_type,
                metadata=metadata,
                on_change=on_change,
            )
            # 同步 PluginConfig 包装器的内部数据
            if hasattr(self.config, '_sync_from_service'):
                self.config._sync_from_service()
            return config_item
        
        # 无配置服务时直接存储到本地（开发/测试场景）
        if isinstance(value_type, str):
            value_type = eval(value_type)
        if isinstance(self.config, dict) and self.config.get(name) is None:
            self.config[name] = default_value if isinstance(default_value, (dict, list)) else value_type(default_value)
        return None
    
    def get_config(self, name: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            name: 配置项名称
            default: 默认值（如果配置不存在）
            
        Returns:
            配置值
        """
        # 优先从本地 config 获取（无论是 PluginConfig 还是 dict）
        return self.config.get(name, default)
    
    def set_config(self, name: str, value: Any) -> tuple:
        """
        设置配置值（触发原子保存）
        
        此方法会立即将配置写入文件。
        
        Args:
            name: 配置项名称
            value: 新值
            
        Returns:
            (old_value, new_value) 元组
        """
        # 如果是 PluginConfig 包装器，使用其 update 方法
        if hasattr(self.config, 'update') and callable(getattr(self.config, 'update')):
            # PluginConfig.update 会触发原子保存
            return self.config.update(name, value)
        
        # 降级处理：无配置服务时直接修改本地字典（开发/测试场景）
        if isinstance(self.config, dict):
            old_value = self.config.get(name)
            self.config[name] = value
            return (old_value, value)
        
        raise TypeError(f"config 类型不支持: {type(self.config)}")
