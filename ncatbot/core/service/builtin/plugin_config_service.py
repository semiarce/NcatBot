"""
插件配置服务

负责所有插件配置的统一管理和持久化。
采用"严格的写时保存"策略，每次写配置时立即持久化。
"""

from typing import Any, Dict, Optional, Callable
from pathlib import Path
import yaml
import aiofiles
import asyncio
import copy

from ..base import BaseService
from ncatbot.utils import get_log
from ncatbot.utils.config.constants import CONFIG_PATH
from .plugin_config_types import PluginConfig, ConfigItem

LOG = get_log("PluginConfigService")


class PluginConfigService(BaseService):
    """插件配置服务 - 统一管理所有插件的配置"""
    
    name: str = "plugin_config"
    description: str = "插件配置服务 - 统一管理所有插件的配置"
    
    def __init__(self, **config: Any):
        super().__init__(**config)
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._config_items: Dict[str, Dict[str, ConfigItem]] = {}
        self._config_path = Path(CONFIG_PATH)
        self._dirty = False
    
    async def on_load(self) -> None:
        await self._load_from_file()
        LOG.info("插件配置服务已加载，已加载 %d 个插件的配置", len(self._configs))
    
    async def on_close(self) -> None:
        await self._save_to_file()
        LOG.info("插件配置服务已关闭，配置已保存")
    
    # -------------------------------------------------------------------------
    # 配置注册
    # -------------------------------------------------------------------------
    
    def register_config(
        self,
        plugin_name: str,
        name: str,
        default_value: Any,
        description: str = "",
        value_type: type = str,
        metadata: Optional[Dict[str, Any]] = None,
        on_change: Optional[Callable] = None,
    ) -> ConfigItem:
        """注册一个配置项"""
        if plugin_name not in self._config_items:
            self._config_items[plugin_name] = {}
        
        if name in self._config_items[plugin_name]:
            raise ValueError(f"插件 {plugin_name} 的配置 {name} 已存在")
        
        if isinstance(value_type, str):
            value_type = eval(value_type)
        
        config_item = ConfigItem(
            name=name,
            default_value=default_value,
            description=description,
            value_type=value_type,
            metadata=metadata,
            plugin_name=plugin_name,
            on_change=on_change,
        )
        
        self._config_items[plugin_name][name] = config_item
        
        if plugin_name not in self._configs:
            self._configs[plugin_name] = {}
        
        if name not in self._configs[plugin_name]:
            if value_type in (dict, list):
                self._configs[plugin_name][name] = copy.deepcopy(default_value)
            else:
                self._configs[plugin_name][name] = value_type(default_value) if not isinstance(default_value, value_type) else default_value
            self._dirty = True
        
        LOG.debug(f"插件 {plugin_name} 注册配置 {name}")
        return config_item
    
    def get_registered_configs(self, plugin_name: str) -> Dict[str, ConfigItem]:
        """获取指定插件的所有已注册配置项"""
        return self._config_items.get(plugin_name, {})
    
    # -------------------------------------------------------------------------
    # 配置读写
    # -------------------------------------------------------------------------
    
    def get(self, plugin_name: str, name: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._configs.get(plugin_name, {}).get(name, default)
    
    def set(self, plugin_name: str, name: str, value: Any) -> tuple:
        """设置配置值（非原子，仅标记脏数据）"""
        if plugin_name not in self._configs:
            self._configs[plugin_name] = {}
        
        old_value = self._configs[plugin_name].get(name)
        
        config_item = self._config_items.get(plugin_name, {}).get(name)
        if config_item:
            value = config_item.parse_value(value)
            if config_item.on_change and old_value != value:
                try:
                    config_item.on_change(old_value, value)
                except Exception as e:
                    LOG.warning(f"配置 {plugin_name}.{name} 变更回调失败: {e}")
        
        self._configs[plugin_name][name] = value
        self._dirty = True
        return (old_value, value)
    
    def set_atomic(self, plugin_name: str, name: str, value: Any) -> tuple:
        """设置配置值（原子操作，立即保存）"""
        result = self.set(plugin_name, name, value)
        self._atomic_save()
        return result
    
    def delete_config_item(self, plugin_name: str, name: str) -> None:
        """删除单个配置项（原子操作）"""
        if plugin_name in self._configs and name in self._configs[plugin_name]:
            del self._configs[plugin_name][name]
            self._dirty = True
            self._atomic_save()
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """获取指定插件的所有配置（返回副本）"""
        return self._configs.get(plugin_name, {}).copy()
    
    def get_plugin_config_wrapper(self, plugin_name: str) -> PluginConfig:
        """获取插件配置的只读包装器"""
        if plugin_name not in self._configs:
            self._configs[plugin_name] = {}
        return PluginConfig(plugin_name, self._configs[plugin_name], self)
    
    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> None:
        """批量设置插件配置（非原子）"""
        if plugin_name not in self._configs:
            self._configs[plugin_name] = {}
        self._configs[plugin_name].update(config)
        self._dirty = True
    
    def set_plugin_config_atomic(self, plugin_name: str, config: Dict[str, Any]) -> None:
        """批量设置插件配置（原子操作，立即保存）"""
        self.set_plugin_config(plugin_name, config)
        self._atomic_save()
    
    def delete_plugin_config(self, plugin_name: str) -> None:
        """删除插件的所有配置"""
        if plugin_name in self._configs:
            del self._configs[plugin_name]
            self._dirty = True
        if plugin_name in self._config_items:
            del self._config_items[plugin_name]
    
    # -------------------------------------------------------------------------
    # 持久化
    # -------------------------------------------------------------------------
    
    def _atomic_save(self) -> None:
        """原子保存配置"""
        if not self._dirty:
            return
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._save_to_file())
        except RuntimeError:
            self._save_to_file_sync()
    
    def _save_to_file_sync(self) -> None:
        """同步保存配置到文件"""
        if not self._dirty:
            return
        try:
            existing_data = {}
            if self._config_path.exists():
                with open(self._config_path, "r", encoding="utf-8") as f:
                    existing_data = yaml.safe_load(f.read()) or {}
            
            existing_data["plugin_config"] = self._configs
            tmp_path = self._config_path.with_suffix('.tmp')
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(yaml.dump(existing_data, sort_keys=False, allow_unicode=True, default_flow_style=False))
            tmp_path.replace(self._config_path)
            self._dirty = False
            LOG.debug("插件配置已同步保存")
        except Exception as e:
            LOG.error(f"同步保存插件配置失败: {e}")
    
    async def _load_from_file(self) -> None:
        """从配置文件加载插件配置"""
        try:
            if not self._config_path.exists():
                return
            async with aiofiles.open(self._config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(await f.read()) or {}
            self._configs = data.get("plugin_config", {})
            LOG.debug(f"从配置文件加载了 {len(self._configs)} 个插件的配置")
        except Exception as e:
            LOG.error(f"加载插件配置失败: {e}")
            self._configs = {}
    
    async def _save_to_file(self) -> None:
        """保存插件配置到配置文件（原子写入）"""
        if not self._dirty:
            return
        try:
            existing_data = {}
            if self._config_path.exists():
                async with aiofiles.open(self._config_path, "r", encoding="utf-8") as f:
                    existing_data = yaml.safe_load(await f.read()) or {}
            
            existing_data["plugin_config"] = self._configs
            tmp_path = self._config_path.with_suffix('.tmp')
            async with aiofiles.open(tmp_path, "w", encoding="utf-8") as f:
                await f.write(yaml.dump(existing_data, sort_keys=False, allow_unicode=True, default_flow_style=False))
            tmp_path.replace(self._config_path)
            self._dirty = False
            LOG.debug("插件配置已保存")
        except Exception as e:
            LOG.error(f"保存插件配置失败: {e}")
    
    async def force_save(self) -> None:
        """强制保存配置"""
        self._dirty = True
        await self._save_to_file()
    
    async def migrate_from_legacy(self, plugin_name: str, legacy_config: Dict[str, Any]) -> None:
        """从旧格式迁移配置"""
        if plugin_name not in self._configs:
            self._configs[plugin_name] = {}
        for key, value in legacy_config.items():
            if key not in self._configs[plugin_name]:
                self._configs[plugin_name][key] = value
        self._dirty = True
        LOG.info(f"已迁移插件 {plugin_name} 的旧配置")
