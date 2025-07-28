# ===================================================================================
# Python file : plugin_manager.py
# Description:
# This module contains the PluginManager, which discovers, loads, and
# initializes all plugins from the 'plugins' directory.
# ===================================================================================

import os
import importlib.util
import inspect
from plugins.plugin_interface import MeshEditorPlugin

class PluginManager:
    """Discovers, loads, and manages all plugins."""
    def __init__(self, main_window): self.main_window, self.plugins, self.plugin_dir = main_window, [], "plugins"
    def load_plugins(self):
        if not os.path.isdir(self.plugin_dir): self.main_window.log_message('warning', f"Plugin directory '{self.plugin_dir}' not found."); return
        for fname in os.listdir(self.plugin_dir):
            if fname.endswith(".py") and not fname.startswith("__"):
                mod_name = f"plugins.{fname[:-3]}"
                try:
                    path = os.path.join(self.plugin_dir, fname); spec = importlib.util.spec_from_file_location(mod_name, path)
                    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
                    if hasattr(module, 'plugin_class') and inspect.isclass(module.plugin_class) and issubclass(module.plugin_class, MeshEditorPlugin):
                        self._initialize_plugin(module.plugin_class())
                except Exception as e: self.main_window.log_message('error', f"Failed to load plugin '{fname}': {e}")
    def _initialize_plugin(self, plugin):
        try:
            plugin.initialize(self.main_window); menu = plugin.get_menu()
            if menu: self.main_window.menuBar().addMenu(menu)
            self.plugins.append(plugin); self.main_window.log_message('info', f"Loaded plugin: '{plugin.get_name()}'.")
        except Exception as e: self.main_window.log_message('error', f"Failed to initialize plugin '{plugin.get_name()}': {e}")