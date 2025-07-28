# ===================================================================================
# Python file : plugin_interface.py
# Description:
# Defines the abstract base class for all plugins, ensuring a consistent
# contract between the application and its extensions.
# ===================================================================================

from abc import ABC, abstractmethod

class MeshEditorPlugin(ABC):
    @abstractmethod
    def get_name(self): pass
    @abstractmethod
    def initialize(self, main_window): pass
    @abstractmethod
    def get_menu(self): pass