# ===================================================================================
# Python file : sample_plugin.py
# Description:
# An example plugin that adds a simple menu and action. This file now uses an
# absolute import to prevent the 'no known parent package' error.
# ===================================================================================

from PyQt5.QtWidgets import QMenu, QMessageBox
from plugins.plugin_interface import MeshEditorPlugin

class SamplePlugin(MeshEditorPlugin):
    def __init__(self): self.main_window = None
    def get_name(self): return "Sample Plugin"
    def initialize(self, main_window): self.main_window = main_window
    def get_menu(self):
        menu = QMenu("Sample Plugin", self.main_window); action = menu.addAction("Say Hello"); action.triggered.connect(self.say_hello); return menu
    def say_hello(self):
        try: QMessageBox.information(self.main_window, "Hello", "Message from sample plugin!"); self.main_window.log_message('info', 'Sample plugin said hello.')
        except Exception as e: print(f"Error in sample plugin: {e}")

plugin_class = SamplePlugin