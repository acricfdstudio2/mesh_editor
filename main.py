# ===================================================================================
# Python file : main.py
# Description:
# This is the main entry point for the Mesh Editor Pro application. It adds the
# project root to the system path and starts the main application window.
# ===================================================================================

import sys
import os
import vtk
from PyQt5.QtWidgets import QApplication, QMessageBox

try:
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
except Exception as e:
    print(f"Error setting up system path: {e}")

from mesh_editor_pro_core.main_window import MeshCreatorApp

def suppress_vtk_errors():
    """Suppresses the VTK error pop-up window."""
    try:
        null_output_window = vtk.vtkOutputWindow()
        vtk.vtkOutputWindow.SetInstance(null_output_window)
    except Exception as e:
        print(f"Could not suppress VTK errors: {e}")

if __name__ == "__main__":
    suppress_vtk_errors()
    app = QApplication(sys.argv)
    
    try:
        main_window = MeshCreatorApp()
        main_window.show()
    except Exception as e:
        print(f"Critical error during application startup: {e}")
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText("Application Failed to Start")
        msg_box.setInformativeText(str(e))
        msg_box.setWindowTitle("Startup Error")
        msg_box.exec_()
        sys.exit(1)
    
    sys.exit(app.exec_())