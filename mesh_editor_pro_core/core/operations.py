# ===================================================================================
# Python file : operations.py
# Description:
# This file contains backend functions for all mesh modifications, including
# the newly implemented Extrude, Revolve, Sweep, and Loft operations.
# ===================================================================================

import vtk

class MeshOperations:
    """A class to handle complex mesh operations as a backend service."""

    def _get_sanitized_polydata(self, polydata):
        """More aggressively cleans polydata to be watertight and manifold."""
        clean1 = vtk.vtkCleanPolyData(); clean1.SetInputData(polydata); clean1.Update()
        triangle = vtk.vtkTriangleFilter(); triangle.SetInputConnection(clean1.GetOutputPort())
        fill = vtk.vtkFillHolesFilter(); fill.SetInputConnection(triangle.GetOutputPort()); fill.SetHoleSize(1e6)
        clean2 = vtk.vtkCleanPolyData(); clean2.SetInputConnection(fill.GetOutputPort()); clean2.Update()
        normals = vtk.vtkPolyDataNormals(); normals.SetInputConnection(clean2.GetOutputPort()); normals.ConsistencyOn(); normals.AutoOrientNormalsOn()
        normals.Update(); return normals.GetOutput()

    def _is_mesh_valid_for_boolean(self, polydata):
        """Checks if a mesh is suitable for booleans."""
        if not polydata or polydata.GetNumberOfCells() == 0: return False
        feature_edges = vtk.vtkFeatureEdges(); feature_edges.SetInputData(polydata); feature_edges.BoundaryEdgesOn(); feature_edges.NonManifoldEdgesOn(); feature_edges.Update()
        return feature_edges.GetOutput().GetNumberOfCells() == 0

    def perform_boolean(self, polydata1, polydata2, operation_type):
        """Performs a boolean operation, raising a ValueError on failure."""
        p1 = self._get_sanitized_polydata(polydata1); p2 = self._get_sanitized_polydata(polydata2)
        if not self._is_mesh_valid_for_boolean(p1) or not self._is_mesh_valid_for_boolean(p2): raise ValueError("One or both meshes are not watertight or have non-manifold edges after sanitization.")
        bool_op = vtk.vtkBooleanOperationPolyDataFilter(); bool_op.SetInputData(0, p1); bool_op.SetInputData(1, p2)
        op_map = {'union': 0, 'intersection': 1, 'difference': 2}
        bool_op.SetOperation(op_map[operation_type]); bool_op.ReorientDifferenceCellsOn(); bool_op.SetTolerance(1e-6); bool_op.Update()
        result = bool_op.GetOutput()
        if not result or result.GetNumberOfPoints() == 0 or result.GetNumberOfCells() == 0: raise ValueError("Result was empty. Meshes may not intersect or the intersection may be ambiguous.")
        return result

    def perform_extrude(self, profile_data, length, vector=(0, 0, 1)):
        """Extrudes a profile along a vector."""
        if not profile_data or profile_data.GetNumberOfPoints() == 0: raise ValueError("Input profile for extrusion is empty.")
        extrude = vtk.vtkLinearExtrusionFilter(); extrude.SetInputData(profile_data); extrude.SetScaleFactor(1.0); extrude.SetExtrusionTypeToVectorExtrusion()
        extrude.SetVector(vector[0] * length, vector[1] * length, vector[2] * length); extrude.Update()
        return self._get_sanitized_polydata(extrude.GetOutput())

    def perform_revolve(self, profile_data, angle=360):
        """Revolves a profile around the Y-axis."""
        if not profile_data or profile_data.GetNumberOfPoints() == 0: raise ValueError("Input profile for revolution is empty.")
        revolve = vtk.vtkRotationalExtrusionFilter(); revolve.SetInputData(profile_data); revolve.SetResolution(60); revolve.SetAngle(angle); revolve.Update()
        return self._get_sanitized_polydata(revolve.GetOutput())

    def perform_sweep(self, profile_data, path_data):
        """Sweeps a profile along a path."""
        if not profile_data or profile_data.GetNumberOfPoints() == 0: raise ValueError("Input profile for sweep is empty.")
        if not path_data or path_data.GetNumberOfPoints() == 0: raise ValueError("Input path for sweep is empty.")
        sweep = vtk.vtkSweepFilter(); sweep.SetInputData(profile_data); sweep.SetSourceData(path_data); sweep.Update()
        return self._get_sanitized_polydata(sweep.GetOutput())

    def perform_loft(self, profiles):
        """Lofts a surface between two or more profiles."""
        if not profiles or len(profiles) < 2: raise ValueError("Loft requires at least two profiles.")
        append = vtk.vtkAppendPolyData()
        for pd in profiles:
            if pd and pd.GetNumberOfPoints() > 0: append.AddInputData(pd)
        append.Update()
        if append.GetOutput().GetNumberOfPoints() == 0: raise ValueError("None of the selected profiles contain valid geometry.")
        loft = vtk.vtkRuledSurfaceFilter(); loft.SetInputConnection(append.GetOutputPort()); loft.SetResolution(30, 30); loft.SetOnRatio(1); loft.Update()
        return self._get_sanitized_polydata(loft.GetOutput())