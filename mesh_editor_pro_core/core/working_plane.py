# ===================================================================================
# Python file : working_plane.py
# Description:
# This module defines the backend logic for the working plane, including the
# fix for the vtk.vtkMath.Cross method.
# ===================================================================================

import vtk

class WorkingPlane:
    """Manages the state of the active 2D working plane."""

    def __init__(self):
        self.plane = vtk.vtkPlane(); self.transform = vtk.vtkTransform(); self.is_active = False; self.reset()
    def set_from_origin_normal(self, origin, normal):
        if vtk.vtkVector3d(normal).Norm() == 0: raise ValueError("Plane normal cannot be a zero vector.")
        self.plane.SetOrigin(origin); self.plane.SetNormal(normal); self._generate_transform(); self.is_active = True
    def _generate_transform(self):
        normal = self.plane.GetNormal(); origin = self.plane.GetOrigin(); z_axis = (0, 0, 1)
        axis = [0, 0, 0]; vtk.vtkMath.Cross(z_axis, normal, axis)
        angle = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(z_axis, normal))
        self.transform.Identity(); self.transform.Translate(origin); self.transform.RotateWXYZ(angle, axis); self.transform.Update()
    def get_transform(self): return self.transform
    def reset(self): self.set_from_origin_normal((0, 0, 0), (0, 0, 1)); self.is_active = False