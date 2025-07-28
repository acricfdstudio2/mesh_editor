# ===================================================================================
# Python file : main_window.py
# Description:
# Defines the main application window (GUI). This file has been reformatted for
# readability and to fix the syntax error.
# ===================================================================================

import vtk
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QDockWidget, QListWidget, QListWidgetItem,
                             QTabWidget, QTextEdit, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QInputDialog, QMenu, QMessageBox, QFileDialog, QAbstractItemView, QStatusBar)
from PyQt5.QtCore import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from mesh_editor_pro_core.core.commands import *
from mesh_editor_pro_core.core.managed_actor import ManagedActor
from mesh_editor_pro_core.core.operations import MeshOperations
from mesh_editor_pro_core.core.working_plane import WorkingPlane
from mesh_editor_pro_core.core.plugin_manager import PluginManager
from mesh_editor_pro_core.ui.dialogs import *
from mesh_editor_pro_core.ui.menu_setup import MenuSetup
from mesh_editor_pro_core.ui.custom_interactor import PickingInteractorStyle
from mesh_editor_pro_core.utils.file_io import FileHandler

class MeshCreatorApp(QMainWindow):
    """The main application window, responsible for the GUI."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mesh Editor Pro")
        self.setGeometry(50, 50, 1600, 1000)
        
        self.file_handler = FileHandler()
        self.mesh_ops = MeshOperations()
        self.working_plane = WorkingPlane()
        
        self.actors = []; self.actor_count = 0
        self.undo_stack = []; self.redo_stack = []
        self.current_project_path = None
        self.plane_visual_actor = None
        
        self.setup_ui_layout()
        self.setup_vtk()
        self.menu_builder = MenuSetup(self)
        self.menu_builder.setup_menus()

        self.plugin_manager = PluginManager(self)
        self.plugin_manager.load_plugins()
        
        self.interactor.Initialize()
        self.update_plane_visuals()
        self.log_message("info", "Application initialized successfully.")

    def setup_ui_layout(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        
        self.left_dock = QDockWidget("Tools", self)
        self.left_tabs = QTabWidget()
        self.cmd_win = QTextEdit(); self.cmd_win.setReadOnly(True)
        self.obj_browser = QListWidget()
        self.obj_browser.itemDoubleClicked.connect(self.rename_item)
        self.obj_browser.setContextMenuPolicy(Qt.CustomContextMenu)
        self.obj_browser.customContextMenuRequested.connect(self.browser_context_menu)
        self.left_tabs.addTab(self.cmd_win, "Command"); self.left_tabs.addTab(self.obj_browser, "Browser")
        self.left_dock.setWidget(self.left_tabs)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        self.bottom_dock = QDockWidget("Logs", self)
        self.bottom_tabs = QTabWidget()
        self.err_log = QTextEdit(); self.err_log.setReadOnly(True)
        console_widget = QWidget(); console_layout = QVBoxLayout(console_widget)
        console_layout.setContentsMargins(0, 0, 0, 0)
        self.py_out = QTextEdit(); self.py_out.setReadOnly(True)
        self.py_in = QLineEdit(); self.py_in.returnPressed.connect(self.execute_py_command)
        console_layout.addWidget(self.py_out); console_layout.addWidget(self.py_in)
        self.bottom_tabs.addTab(self.err_log, "Error Log"); self.bottom_tabs.addTab(console_widget, "Python Console")
        self.bottom_dock.setWidget(self.bottom_tabs)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_dock)
        
        self.setStatusBar(QStatusBar(self))
        self.show_status_message("Ready.")

    def setup_vtk(self):
        self.vtk_widget = QVTKRenderWindowInteractor(self.central_widget)
        self.layout.addWidget(self.vtk_widget, 1)
        self.renderer = vtk.vtkRenderer(); self.renderer.SetBackground(0.1, 0.2, 0.4)
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.def_style = vtk.vtkInteractorStyleTrackballCamera()
        self.pick_style = PickingInteractorStyle(self.on_surface_picked)
        self.interactor.SetInteractorStyle(self.def_style)

    def execute_command(self, command, log_msg=""):
        try:
            command.execute()
            self.undo_stack.append(command)
            self.redo_stack.clear()
            self._sync_actors_from_command(command, is_undo=False)
            self.reset_camera_view()
            self.log_message('info', log_msg)
            self.show_status_message("Operation successful.")
        except Exception as e:
            self.log_message('error', f"Command failed: {e}")

    def undo(self):
        if not self.undo_stack:
            return
        try:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)
            self._sync_actors_from_command(command, is_undo=True)
            self.reset_camera_view()
            self.log_message('info', "Undo performed.")
        except Exception as e:
            self.log_message('error', f"Undo failed: {e}")

    def redo(self):
        if not self.redo_stack:
            return
        try:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)
            self._sync_actors_from_command(command, is_undo=False)
            self.reset_camera_view()
            self.log_message('info', "Redo performed.")
        except Exception as e:
            self.log_message('error', f"Redo failed: {e}")

    def new_project(self):
        self.renderer.RemoveAllViewProps(); self.actors.clear(); self.undo_stack.clear()
        self.redo_stack.clear(); self.actor_count = 0; self.obj_browser.clear()
        self.current_project_path = None; self.reset_working_plane()
        self.log_message('info', "New project started.")

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open", "", "3D Files(*.stl *.ply *.vtk *.obj *.vtp)")
        if path: self.import_file(path)

    def save_project(self):
        if not self.current_project_path: self.save_project_as(); return
        try:
            self.file_handler.save_project(self.current_project_path, self.actors)
            self.log_message('info', f"Saved to {self.current_project_path}.")
        except Exception as e: self.log_message('error', str(e))

    def save_project_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "STL(*.stl);;PLY(*.ply);;VTK(*.vtk);;OBJ(*.obj);;VTP(*.vtp)")
        if path:
            try:
                self.file_handler.save_project(path, self.actors)
                self.current_project_path = path
                self.log_message('info', f"Saved to {path}.")
            except Exception as e: self.log_message('error', str(e))

    def import_file(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Import", "", "3D Files(*.stl *.ply *.vtk *.obj *.vtp)")
        if path:
            try:
                self._create_actor_from_polydata(self.file_handler.import_file(path), name=os.path.basename(path))
                self.log_message('info', f"Imported: {path}")
            except Exception as e: self.log_message('error', str(e))

    def perform_boolean_gui(self, op_type):
        if len(self.actors) < 2: self.log_message('warning', "Need at least two meshes."); return
        dialog = ObjectSelectionDialog("Select 2 Meshes", self.actors, QAbstractItemView.ExtendedSelection, self)
        if dialog.exec_() and len(dialog.sel) == 2:
            a1, a2 = dialog.sel
            self.log_message('info', f"Performing {op_type}...")
            try:
                result_pd = self.mesh_ops.perform_boolean(a1.GetMapper().GetInput(), a2.GetMapper().GetInput(), op_type)
                new_actor = self._create_actor_from_polydata(result_pd, f"{op_type}_result", execute=False)
                self.execute_command(BooleanOperationCommand(self.renderer, new_actor, a1, a2), "Boolean successful.")
            except Exception as e: self.log_message('error', f"Boolean failed: {e}")
            
    def extrude_gui(self):
        dialog = ObjectSelectionDialog("Select Profile to Extrude", self.actors, QAbstractItemView.SingleSelection, self)
        if dialog.exec_() and dialog.sel:
            actor = dialog.sel[0]
            param_dialog = ParameterDialog({'Length': (1, 0.1, 100, 2)}, self)
            if param_dialog.exec_():
                try:
                    length = param_dialog.getValues()['Length']
                    new_pd = self.mesh_ops.perform_extrude(actor.GetMapper().GetInput(), length)
                    new_actor = self._create_actor_from_polydata(new_pd, f"{actor.name}_ext", execute=False)
                    self.execute_command(ReplaceActorCommand(self.renderer, new_actor, actor), "Extrude successful.")
                except Exception as e: self.log_message('error', f"Extrude failed: {e}")

    def revolve_gui(self):
        dialog = ObjectSelectionDialog("Select Profile to Revolve", self.actors, QAbstractItemView.SingleSelection, self)
        if dialog.exec_() and dialog.sel:
            actor = dialog.sel[0]
            param_dialog = ParameterDialog({'Angle': (360, 1, 360, 0)}, self)
            if param_dialog.exec_():
                try:
                    angle = param_dialog.getValues()['Angle']
                    new_pd = self.mesh_ops.perform_revolve(actor.GetMapper().GetInput(), angle)
                    new_actor = self._create_actor_from_polydata(new_pd, f"{actor.name}_rev", execute=False)
                    self.execute_command(ReplaceActorCommand(self.renderer, new_actor, actor), "Revolve successful.")
                except Exception as e: self.log_message('error', f"Revolve failed: {e}")

    def sweep_gui(self):
        prof_dialog = ObjectSelectionDialog("Select Profile for Sweep", self.actors, QAbstractItemView.SingleSelection, self)
        if prof_dialog.exec_() and prof_dialog.sel:
            profile_actor = prof_dialog.sel[0]
            path_actors = [a for a in self.actors if a != profile_actor]
            if not path_actors: self.log_message('warning', "No other objects available for path."); return
            path_dialog = ObjectSelectionDialog("Select Path for Sweep", path_actors, QAbstractItemView.SingleSelection, self)
            if path_dialog.exec_() and path_dialog.sel:
                try:
                    path_actor = path_dialog.sel[0]
                    new_pd = self.mesh_ops.perform_sweep(profile_actor.GetMapper().GetInput(), path_actor.GetMapper().GetInput())
                    self._create_actor_from_polydata(new_pd, f"sweep_{profile_actor.name}")
                except Exception as e: self.log_message('error', f"Sweep failed: {e}")

    def loft_gui(self):
        dialog = ObjectSelectionDialog("Select 2+ Profiles for Loft", self.actors, QAbstractItemView.ExtendedSelection, self)
        if dialog.exec_() and len(dialog.sel) >= 2:
            try:
                profiles = [actor.GetMapper().GetInput() for actor in dialog.sel]
                new_pd = self.mesh_ops.perform_loft(profiles)
                self._create_actor_from_polydata(new_pd, "loft_result")
            except Exception as e: self.log_message('error', f"Loft failed: {e}")

    def create_shape_gui(self, shape_type):
        dialog_map = {"point": PointDialog, "line": LineDialog, "rectangle": RectangleDialog, "circle": CircleDialog}
        if shape_type in dialog_map:
            dialog = dialog_map[shape_type](self)
            if dialog.exec_(): self._create_actor_from_polydata(self._get_polydata_for_2d_shape(shape_type, dialog.getValues()), shape_type.capitalize())
        else:
            params_map = {'cube':{'Size':(1,0.1,10,2)}, 'sphere':{'Radius':(1,0.1,10,2),'Resolution':(32,3,100,0)}, 'cone':{'Radius':(0.5,0.1,10,2),'Height':(1,0.1,10,2),'Resolution':(32,3,100,0)}, 'cylinder':{'Radius':(0.5,0.1,10,2),'Height':(1,0.1,10,2),'Resolution':(32,3,100,0)}, 'pyramid':{'Sides':(4,3,12,0),'SideLength':(1,0.1,10,2),'Height':(1,0.1,10,2)}}
            if shape_type not in params_map: return
            source = self._get_source_for_3d_shape(shape_type)
            preview = ManagedActor("preview"); preview.GetProperty().SetRepresentationToWireframe(); preview.GetProperty().SetColor(1, 1, 0)
            mapper = vtk.vtkPolyDataMapper(); mapper.SetInputConnection(source.GetOutputPort()); preview.SetMapper(mapper)
            dialog = ParameterDialog(params_map[shape_type], self)
            dialog.vChanged.connect(lambda: self._update_source_for_3d_shape(source, shape_type, dialog.getValues()) or self.vtk_widget.GetRenderWindow().Render())
            self._update_source_for_3d_shape(source, shape_type, {k: v[0] for k, v in params_map[shape_type].items()})
            self.renderer.AddActor(preview)
            if dialog.exec_():
                self._update_source_for_3d_shape(source, shape_type, dialog.getValues())
                self._create_actor_from_polydata(source.GetOutput(), shape_type.capitalize())
            self.renderer.RemoveActor(preview)
            self.vtk_widget.GetRenderWindow().Render()

    def define_plane_from_input(self):
        dialog = PlaneDialog(self)
        if dialog.exec_():
            try:
                vals = dialog.getValues()
                self.working_plane.set_from_origin_normal((vals['OX'], vals['OY'], vals['OZ']), (vals['NX'], vals['NY'], vals['NZ']))
                self.log_message('info', 'Working plane set.'); self.update_plane_visuals()
            except Exception as e: self.log_message('error', str(e))

    def enter_plane_picking_mode(self):
        self.interactor.SetInteractorStyle(self.pick_style)
        self.show_status_message('PICKING MODE: Left-click surface.')

    def on_surface_picked(self, point, normal):
        try:
            self.working_plane.set_from_origin_normal(point, normal)
            self.log_message('info', 'Working plane set from pick.')
            self.update_plane_visuals()
        except Exception as e: self.log_message('error', str(e))
        finally:
            self.interactor.SetInteractorStyle(self.def_style)
            self.show_status_message("Ready.")

    def reset_working_plane(self):
        self.working_plane.reset()
        self.update_plane_visuals()
        self.log_message('info', 'Working plane reset.')

    def _create_actor_from_polydata(self, polydata, name=None, execute=True):
        if not polydata or polydata.GetNumberOfPoints() == 0: self.log_message('warning', "Empty geometry."); return None
        mapper = vtk.vtkPolyDataMapper(); mapper.SetInputData(polydata)
        final_name = name or f"Mesh_{self.actor_count + 1}"
        base_name, i = final_name, 1
        while any(a.name == final_name for a in self.actors): final_name = f"{base_name}_{i}"; i += 1
        if name is None: self.actor_count += 1
        actor = ManagedActor(name=final_name); actor.SetMapper(mapper)
        prop = actor.GetProperty(); prop.SetColor(vtk.vtkMath.Random(.7, 1), vtk.vtkMath.Random(.7, 1), vtk.vtkMath.Random(.7, 1))
        prop.SetEdgeVisibility(True); prop.SetEdgeColor(.1, .1, .1); prop.SetLineWidth(0.5)
        if not execute: return actor
        self.execute_command(AddActorCommand(self.renderer, actor), f"Created '{final_name}'."); return actor

    def _add_actor_to_scene(self, actor):
        self.actors.append(actor)
        self.obj_browser.addItem(QListWidgetItem(actor.name))

    def _remove_actor_from_scene(self, actor):
        if actor in self.actors: self.actors.remove(actor)
        for item in self.obj_browser.findItems(actor.name, Qt.MatchExactly): self.obj_browser.takeItem(self.obj_browser.row(item))

    def _get_polydata_for_2d_shape(self, shape_type, vals):
        pd = None
        if shape_type == 'point': p = vtk.vtkPoints(); p.InsertNextPoint(vals['X'], vals['Y'], 0); pd = vtk.vtkPolyData(); pd.SetPoints(p); g = vtk.vtkVertexGlyphFilter(); g.SetInputData(pd); g.Update(); pd = g.GetOutput()
        if shape_type == 'line': l = vtk.vtkLineSource(); l.SetPoint1(vals['X1'], vals['Y1'], 0); l.SetPoint2(vals['X2'], vals['Y2'], 0); l.Update(); pd = l.GetOutput()
        if shape_type == 'rectangle': pl = vtk.vtkPlaneSource(); w, h = vals['Width'] / 2, vals['Height'] / 2; pl.SetCenter(0, 0, 0); pl.SetPoint1(w, -h, 0); pl.SetPoint2(-w, h, 0); pl.Update(); pd = pl.GetOutput()
        if shape_type == 'circle': pg = vtk.vtkRegularPolygonSource(); pg.SetRadius(vals['Radius']); pg.SetNumberOfSides(int(vals['Resolution'])); pg.Update(); pd = pg.GetOutput()
        if pd and self.working_plane.is_active:
            t = vtk.vtkTransformPolyDataFilter(); t.SetTransform(self.working_plane.get_transform()); t.SetInputData(pd); t.Update(); return t.GetOutput()
        return pd

    def _get_source_for_3d_shape(self, st):
        return {'cube': vtk.vtkCubeSource, 'sphere': vtk.vtkSphereSource, 'cone': vtk.vtkConeSource, 'cylinder': vtk.vtkCylinderSource, 'pyramid': vtk.vtkConeSource}[st]()

    def _update_source_for_3d_shape(self, source, shape_type, vals):
        if shape_type == 'cube': source.SetXLength(vals['Size']); source.SetYLength(vals['Size']); source.SetZLength(vals['Size'])
        elif shape_type == 'sphere': source.SetRadius(vals['Radius']); source.SetThetaResolution(int(vals['Resolution'])); source.SetPhiResolution(int(vals['Resolution']))
        elif shape_type in ['cone', 'cylinder']: source.SetRadius(vals['Radius']); source.SetHeight(vals['Height']); source.SetResolution(int(vals['Resolution']))
        elif shape_type == 'pyramid': source.SetHeight(vals['Height']); source.SetRadius(vals['SideLength']); source.SetResolution(int(vals['Sides']))
        source.Update()

    def update_plane_visuals(self):
        if self.plane_visual_actor: self.renderer.RemoveActor(self.plane_visual_actor)
        if not self.working_plane.is_active: self.reset_camera_view(); return
        ps = vtk.vtkPlaneSource(); ps.SetCenter(0, 0, 0); ps.Update()
        bounds = self.renderer.ComputeVisiblePropBounds(); s = (vtk.vtkMath.Distance2BetweenPoints([bounds[0], bounds[2], bounds[4]], [bounds[1], bounds[3], bounds[5]])**0.5) or 20
        t = vtk.vtkTransform(); t.Scale(s, s, 1); t.Concatenate(self.working_plane.get_transform()); tf = vtk.vtkTransformPolyDataFilter(); tf.SetTransform(t); tf.SetInputConnection(ps.GetOutputPort()); tf.Update()
        m = vtk.vtkPolyDataMapper(); m.SetInputConnection(tf.GetOutputPort()); self.plane_visual_actor = ManagedActor("working_plane_visual"); self.plane_visual_actor.SetMapper(m)
        p = self.plane_visual_actor.GetProperty(); p.SetRepresentationToWireframe(); p.SetColor(0.7, 0.7, 0.9); p.SetOpacity(0.5); p.SetLighting(False)
        self.renderer.AddActor(self.plane_visual_actor); self.reset_camera_view()

    def _sync_actors_from_command(self, command, is_undo):
        op_map = {
            AddActorCommand: (lambda c: self._remove_actor_from_scene(c.actor), lambda c: self._add_actor_to_scene(c.actor)),
            DeleteActorCommand: (lambda c: self._add_actor_to_scene(c.actor), lambda c: self._remove_actor_from_scene(c.actor)),
            ReplaceActorCommand: (lambda c: (self._remove_actor_from_scene(c.new_actor), self._add_actor_to_scene(c.old_actor)), lambda c: (self._remove_actor_from_scene(c.old_actor), self._add_actor_to_scene(c.new_actor))),
            BooleanOperationCommand: (lambda c: (self._remove_actor_from_scene(c.new_actor), self._add_actor_to_scene(c.old_actor1), self._add_actor_to_scene(c.old_actor2)), lambda c: (self._remove_actor_from_scene(c.old_actor1), self._remove_actor_from_scene(c.old_actor2), self._add_actor_to_scene(c.new_actor)))
        }
        action = op_map[type(command)][0 if is_undo else 1]
        action(command)

    def log_message(self, level, msg):
        log_map = {'info': self.cmd_win, 'warning': self.err_log, 'error': self.err_log}
        color_map = {'info': 'black', 'warning': 'orange', 'error': 'red'}
        log_widget = log_map.get(level, self.cmd_win)
        log_widget.append(f"<font color='{color_map.get(level, 'black')}'><b>[{level.upper()}]</b> {msg}</font>")

    def browser_context_menu(self, point):
        item = self.obj_browser.itemAt(point)
        if not item or item.text() == "working_plane_visual": return
        menu = QMenu(); re_action = menu.addAction("Rename"); del_action = menu.addAction("Delete"); action = menu.exec_(self.obj_browser.mapToGlobal(point))
        if action == re_action: self.rename_item(item)
        elif action == del_action: self.delete_actor_by_name(item.text())

    def rename_item(self, item):
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_name)
        if not (ok and new_name and new_name != old_name): return
        base, i = new_name, 1
        while any(a.name == new_name for a in self.actors if a.name != old_name): new_name = f"{base}_{i}"; i += 1
        for actor in self.actors:
            if actor.name == old_name: actor.name = new_name; break
        item.setText(new_name)
        self.log_message('info', f"Renamed '{old_name}' to '{new_name}'.")

    def delete_actor_by_name(self, name):
        actor = next((a for a in self.actors if a.name == name), None)
        if actor: self.execute_command(DeleteActorCommand(self.renderer, actor), f"Deleted '{name}'.")

    def delete_selected_actor(self):
        selected = self.obj_browser.selectedItems()
        if selected: self.delete_actor_by_name(selected[0].text())
        else: self.log_message('warning', 'No object selected.')

    def execute_py_command(self):
        cmd = self.py_in.text()
        self.py_out.append(f"<font color='blue'>>>> {cmd}</font>")
        self.py_in.clear()
        try: exec(cmd, {"app": self, "vtk": vtk})
        except Exception as e: self.py_out.append(f"<font color='red'>{type(e).__name__}: {e}</font>")
        self.vtk_widget.GetRenderWindow().Render()

    def reset_camera_view(self): self.renderer.ResetCamera(); self.vtk_widget.GetRenderWindow().Render()
    def about_dialog(self): QMessageBox.about(self, "About Mesh Editor Pro", "Mesh Editor Pro\nVersion 2.4\nEnhanced stability and features.")
    def not_implemented(self): self.log_message("warning", "Feature not yet implemented.")
    def show_status_message(self, msg, timeout=5000): self.statusBar().showMessage(msg, timeout)