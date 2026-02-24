"""
Plugins System - Extensible plugin architecture

A modular plugin system for extending blockchain functionality. Features include:
- Plugin registration and management
- Dependency resolution
- Lifecycle management (install, enable, disable, uninstall)
- Configuration system
- Plugin communication
- Version management
"""

import importlib
import os
import sys
import pkgutil
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class PluginInfo:
    """Plugin information and metadata"""
    name: str
    version: str
    author: str
    description: str
    category: str
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True
    loaded: bool = False


@dataclass
class PluginConfig:
    """Plugin configuration"""
    name: str
    version: str
    config: Dict[str, Any] = field(default_factory=dict)


class Plugin:
    """Base class for all plugins"""
    
    def __init__(self, name: str, info: PluginInfo):
        self.name = name
        self.info = info
        self.config = {}
        self.enabled = info.enabled
    
    async def initialize(self, config: Dict = None):
        """Initialize plugin"""
        self.config = config or {}
        self.info.loaded = True
    
    async def start(self):
        """Start plugin"""
        self.enabled = True
        self.info.enabled = True
    
    async def stop(self):
        """Stop plugin"""
        self.enabled = False
        self.info.enabled = False
    
    async def shutdown(self):
        """Shutdown plugin"""
        self.info.loaded = False
    
    def get_info(self) -> PluginInfo:
        """Get plugin information"""
        return self.info
    
    def get_config(self) -> Dict:
        """Get plugin configuration"""
        return self.config
    
    async def on_block_created(self, block: Any):
        """Called when a new block is created"""
        pass
    
    async def on_block_added(self, block: Any):
        """Called when a block is added to the chain"""
        pass
    
    async def on_transaction_processed(self, transaction: Any):
        """Called when a transaction is processed"""
        pass


class PluginSystem:
    """
    Plugin management system
    """
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.configurations: Dict[str, PluginConfig] = {}
        self.plugin_paths: List[str] = []
        self.dependency_graph: Dict[str, List[str]] = {}
    
    def add_plugin_path(self, path: str):
        """Add plugin search path"""
        if path not in self.plugin_paths:
            self.plugin_paths.append(path)
            if path not in sys.path:
                sys.path.insert(0, path)
    
    def find_plugins(self) -> List[Tuple[str, str]]:
        """Find available plugins in search paths"""
        plugins = []
        
        for path in self.plugin_paths:
            if os.path.exists(path):
                for _, name, ispkg in pkgutil.iter_modules([path]):
                    if ispkg:
                        # Check if it's a valid plugin package
                        plugin_dir = os.path.join(path, name)
                        plugin_file = os.path.join(plugin_dir, 'plugin.py')
                        if os.path.exists(plugin_file):
                            plugins.append((name, plugin_dir))
        
        return plugins
    
    def load_plugin(self, plugin_name: str, plugin_dir: str) -> Optional[Plugin]:
        """Load plugin from directory"""
        try:
            module_name = f"{plugin_name}.plugin"
            module = importlib.import_module(module_name)
            
            # Find Plugin subclass
            plugin_class = None
            for name, cls in module.__dict__.items():
                if isinstance(cls, type) and issubclass(cls, Plugin) and cls != Plugin:
                    plugin_class = cls
                    break
            
            if plugin_class:
                info = PluginInfo(
                    name=plugin_name,
                    version=getattr(module, '__version__', '1.0.0'),
                    author=getattr(module, '__author__', 'Unknown'),
                    description=getattr(module, '__description__', ''),
                    category=getattr(module, '__category__', 'General'),
                    dependencies=getattr(module, '__dependencies__', [])
                )
                
                plugin = plugin_class(plugin_name, info)
                self.plugins[plugin_name] = plugin
                self.plugin_info[plugin_name] = info
                
                # Resolve dependencies
                self._resolve_dependencies(plugin_name, info.dependencies)
                
                return plugin
            else:
                print(f"Could not find Plugin subclass in {module_name}")
                return None
        
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return None
    
    def _resolve_dependencies(self, plugin_name: str, dependencies: List[str]):
        """Resolve plugin dependencies"""
        self.dependency_graph[plugin_name] = dependencies
    
    async def initialize_plugins(self):
        """Initialize all loaded plugins"""
        # Sort plugins by dependencies
        plugin_order = self._sort_by_dependencies()
        
        for plugin_name in plugin_order:
            plugin = self.plugins[plugin_name]
            config = self.configurations.get(plugin_name, PluginConfig(plugin_name, '1.0.0')).config
            await plugin.initialize(config)
    
    async def start_plugins(self):
        """Start all plugins"""
        plugin_order = self._sort_by_dependencies()
        
        for plugin_name in plugin_order:
            plugin = self.plugins[plugin_name]
            await plugin.start()
    
    async def stop_plugins(self):
        """Stop all plugins"""
        # Stop in reverse dependency order
        plugin_order = self._sort_by_dependencies()
        for plugin_name in reversed(plugin_order):
            plugin = self.plugins[plugin_name]
            await plugin.stop()
    
    async def shutdown_plugins(self):
        """Shutdown all plugins"""
        plugin_order = self._sort_by_dependencies()
        for plugin_name in reversed(plugin_order):
            plugin = self.plugins[plugin_name]
            await plugin.shutdown()
    
    def _sort_by_dependencies(self) -> List[str]:
        """Topologically sort plugins by dependencies"""
        visited = set()
        order = []
        
        def dfs(plugin_name: str):
            if plugin_name in visited:
                return
            
            visited.add(plugin_name)
            
            if plugin_name in self.dependency_graph:
                for dep in self.dependency_graph[plugin_name]:
                    if dep in self.plugins and dep not in visited:
                        dfs(dep)
            
            order.append(plugin_name)
        
        for plugin_name in self.plugins:
            dfs(plugin_name)
        
        return order
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get plugin by name"""
        return self.plugins.get(name)
    
    def get_plugins(self, category: str = None) -> List[Plugin]:
        """Get all plugins, optionally filtered by category"""
        if category:
            return [p for p in self.plugins.values() if p.info.category == category]
        
        return list(self.plugins.values())
    
    def get_enabled_plugins(self) -> List[Plugin]:
        """Get all enabled plugins"""
        return [p for p in self.plugins.values() if p.enabled]
    
    def get_disabled_plugins(self) -> List[Plugin]:
        """Get all disabled plugins"""
        return [p for p in self.plugins.values() if not p.enabled]
    
    def enable_plugin(self, plugin_name: str):
        """Enable plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            self.plugin_info[plugin_name].enabled = True
    
    def disable_plugin(self, plugin_name: str):
        """Disable plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            self.plugin_info[plugin_name].enabled = False
    
    def remove_plugin(self, plugin_name: str):
        """Remove plugin"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            del self.plugin_info[plugin_name]
            if plugin_name in self.configurations:
                del self.configurations[plugin_name]
            if plugin_name in self.dependency_graph:
                del self.dependency_graph[plugin_name]
    
    def set_plugin_configuration(self, plugin_name: str, config: Dict):
        """Set plugin configuration"""
        if plugin_name not in self.configurations:
            self.configurations[plugin_name] = PluginConfig(
                plugin_name,
                self.plugin_info[plugin_name].version,
                config
            )
        else:
            self.configurations[plugin_name].config = config
    
    def get_plugin_configuration(self, plugin_name: str) -> Optional[Dict]:
        """Get plugin configuration"""
        if plugin_name in self.configurations:
            return self.configurations[plugin_name].config
        
        return None
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin information"""
        return self.plugin_info.get(plugin_name)
    
    def validate_plugins(self) -> List[Tuple[str, str]]:
        """Validate all loaded plugins and check for issues"""
        issues = []
        
        for plugin_name, plugin in self.plugins.items():
            # Check dependencies
            for dep in self.dependency_graph.get(plugin_name, []):
                if dep not in self.plugins:
                    issues.append((plugin_name, f"Missing dependency: {dep}"))
            
            # Check if plugin is enabled but not loaded
            if plugin.enabled and not plugin.info.loaded:
                issues.append((plugin_name, "Plugin is enabled but not loaded"))
        
        return issues
    
    async def trigger_event(self, event_name: str, *args, **kwargs):
        """Trigger event to all plugins"""
        method_name = f"on_{event_name}"
        
        for plugin in self.get_enabled_plugins():
            if hasattr(plugin, method_name):
                try:
                    await getattr(plugin, method_name)(*args, **kwargs)
                except Exception as e:
                    print(f"Error in plugin {plugin.name} handling {event_name}: {e}")
