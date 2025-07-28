# ===================================================================================
# Python file : custom_interactor.py
# Description:
# Defines a custom VTK interactor style for picking points on 3D meshes, used
# for interactively defining the working plane.
# ===================================================================================

import vtk

class PickingInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """Custom interactor style for picking points on actors in the scene."""
    def __init__(self, callback): super().__init__(); self.callback = callback; self.AddObserver("LeftButtonPressEvent", self.on_left_press); self.picker = vtk.vtkCellPicker(); self.picker.SetTolerance(0.005)
    def on_left_press(self, obj, event):
        try:
            pos = self.GetInteractor().GetEventPosition(); self.picker.Pick(pos[0], pos[1], 0, self.GetDefaultRenderer())
            if self.picker.GetCellId() != -1:
                point = self.picker.GetPickPosition(); actor = self.picker.GetActor(); pdata = actor.GetMapper().GetInput()
                if not pdata.GetCellData().GetNormals():
                    nf = vtk.vtkPolyDataNormals(); nf.SetInputData(pdata); nf.ComputeCellNormalsOn(); nf.Update(); pdata = nf.GetOutput()
                self.callback(point, pdata.GetCellData().GetNormals().GetTuple(self.picker.GetCellId()))
            else: self.OnLeftButtonDown()
        except Exception: self.OnLeftButtonDown()