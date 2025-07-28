# ===================================================================================
#
# Description:
#   This module defines the WorkingPlaneManager class, responsible for creating,
#   managing, and visualizing the active 2D working plane in the 3D scene. It
#   calculates the necessary transformation to map 2D drawing coordinates onto
#   this plane in world space.
#
# ===================================================================================

import vtk
from .managed_actor import ManagedActor

class WorkingPlaneManager:
    """Manages the state and visualization of the active 2D working plane."""

    def __init__(self):
        self.plane = None
        self.transform = None
        self.visual_actor = None

    def is_active(self):
        """Check if a working plane is currently defined."""
        return self.plane is not None

    def create_from_origin_normal(self, origin, normal):
        """Creates a plane from a given origin and normal vector."""
        self.plane = vtk.vtkPlane()
        self.plane.SetOrigin(origin)
        self.plane.SetNormal(normal)
        self._generate_transform()

    def _generate_transform(self):
        """
        Generates a vtkTransform that maps the XY plane (z=0) to the
        working plane's position and orientation in 3D space.
        """
        normal = self.plane.GetNormal()
        origin = self.plane.GetOrigin()

        z_axis = (0, 0, 1)
        axis = vtk.vtkMath.Cross(z_axis, normal)
        angle = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(z_axis, normal))

        self.transform = vtk.vtkTransform()
        self.transform.Translate(origin)
        self.transform.RotateWXYZ(angle, axis)

    def get_transform(self):
        """Returns the transform to map 2D coordinates to the 3D plane."""
        return self.transform

    def update_visuals(self, renderer):
        """Creates or updates the visual representation of the plane."""
        if not self.is_active():
            return
        
        if self.visual_actor:
            renderer.RemoveActor(self.visual_actor)

        plane_source = vtk.vtkPlaneSource()
        plane_source.SetCenter(self.plane.GetOrigin())
        plane_source.SetNormal(self.plane.GetNormal())
        
        bounds = renderer.ComputeVisiblePropBounds()
        diag = vtk.vtkMath.Distance2BetweenPoints(
            [bounds[0], bounds[2], bounds[4]], 
            [bounds[1], bounds[3], bounds[5]]
        ) ** 0.5
        size = diag if diag > 0 else 20
        plane_source.SetPoint1(self.plane.GetOrigin() + vtk.vtkVector3d(size, 0, 0))
        plane_source.SetPoint2(self.plane.GetOrigin() + vtk.vtkVector3d(0, size, 0))
        plane_source.Update()
        
        transform_polydata = vtk.vtkTransformPolyDataFilter()
        transform_polydata.SetTransform(self.get_transform())
        transform_polydata.SetInputConnection(plane_source.GetOutputPort())
        transform_polydata.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(transform_polydata.GetOutputPort())

        self.visual_actor = ManagedActor(name="working_plane_visual")
        self.visual_actor.SetMapper(mapper)
        prop = self.visual_actor.GetProperty()
        prop.SetRepresentationToWireframe()
        prop.SetColor(0.7, 0.7, 0.9)
        prop.SetOpacity(0.5)
        prop.SetLighting(False)

        renderer.AddActor(self.visual_actor)

    def clear(self, renderer):
        """Clears the active plane and removes its visual representation."""
        if self.visual_actor:
            renderer.RemoveActor(self.visual_actor)
        self.plane = None
        self.transform = None
        self.visual_actor = None