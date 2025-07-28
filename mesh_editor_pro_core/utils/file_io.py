# ===================================================================================
# Python file : file_io.py
# Description:
# Handles all file input/output operations. This module is pure backend logic,
# raising exceptions on failure and containing no GUI code.
# ===================================================================================

import vtk

class FileHandler:
    """Manages saving and loading of mesh files as a backend service."""

    def save_project(self, file_path, actors):
        """Saves the geometric data of all actors to a single file."""
        try:
            if not actors: raise ValueError("Scene is empty. Nothing to save.")
            ext = "." + file_path.split('.')[-1].lower()
            writer_map = {'.stl': vtk.vtkSTLWriter, '.ply': vtk.vtkPLYWriter, '.vtk': vtk.vtkPolyDataWriter, '.obj': vtk.vtkOBJWriter, '.vtp': vtk.vtkXMLPolyDataWriter}
            if ext not in writer_map: raise ValueError(f"Unsupported file extension: {ext}")
            append = vtk.vtkAppendPolyData()
            for actor in actors:
                if actor.name != "working_plane_visual" and actor.GetMapper() and actor.GetMapper().GetInput(): append.AddInputData(actor.GetMapper().GetInput())
            append.Update()
            if append.GetOutput().GetNumberOfPoints() == 0: raise ValueError("No valid geometry found to save.")
            writer = writer_map[ext](); writer.SetFileName(file_path); writer.SetInputConnection(append.GetOutputPort()); writer.Write()
        except Exception as e: raise IOError(f"Failed to save project to {file_path}: {e}")

    def import_file(self, file_path):
        """Loads geometric data from a file."""
        try:
            ext = "." + file_path.split('.')[-1].lower()
            reader_map = {'.stl': vtk.vtkSTLReader, '.ply': vtk.vtkPLYReader, '.vtk': vtk.vtkPolyDataReader, '.obj': vtk.vtkOBJReader, '.vtp': vtk.vtkXMLPolyDataReader}
            if ext not in reader_map: raise ValueError(f"Unsupported file extension: {ext}")
            reader = reader_map[ext](); reader.SetFileName(file_path); reader.Update(); return reader.GetOutput()
        except Exception as e: raise IOError(f"Failed to import file {file_path}: {e}")