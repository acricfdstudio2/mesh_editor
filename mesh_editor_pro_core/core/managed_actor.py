# ===================================================================================
# Python file : managed_actor.py
# Description:
# Defines a custom actor class that inherits from vtk.vtkLODActor to support
# Level-Of-Detail rendering, ensuring consistent use of VTKLODActor.
# ===================================================================================

import vtk

class ManagedActor(vtk.vtkLODActor):
    """
    A vtk.vtkLODActor subclass to hold a custom name and manage its properties.
    """
    def __init__(self, name=""):
        super().__init__()
        self.name = name