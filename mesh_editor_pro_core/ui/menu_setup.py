# ===================================================================================
# Python file : menu_setup.py
# Description:
# This module creates the main menu bar, including the new "Advanced Shapes"
# submenu for Extrude, Revolve, Sweep, and Loft.
# ===================================================================================

from PyQt5.QtWidgets import QAction, QMenu

class MenuSetup:
    """Handles the creation of the standard application menus."""
    def __init__(self, main_window): self.main_window = main_window
    def setup_menus(self):
        menu_bar = self.main_window.menuBar()
        self._setup_file_menu(menu_bar)
        self._setup_edit_menu(menu_bar)
        self._setup_view_menu(menu_bar)
        self._setup_plane_menu(menu_bar)
        self._setup_create_menus(menu_bar)
        self._setup_modify_menu(menu_bar)
        self._setup_tools_menu(menu_bar)
        self._setup_help_menu(menu_bar)

    def _add_actions(self, menu, actions):
        """Helper to add actions to a menu."""
        for action_spec in actions:
            if action_spec is None: menu.addSeparator(); continue
            name, callback, *shortcut = action_spec
            action = QAction(name, self.main_window, triggered=callback)
            if shortcut: action.setShortcut(shortcut[0])
            menu.addAction(action)

    def _setup_file_menu(self, menu_bar):
        file_menu = menu_bar.addMenu("&File")
        self._add_actions(file_menu, [("New Project", self.main_window.new_project, "Ctrl+N"), ("Open...", self.main_window.open_project, "Ctrl+O"), ("Save", self.main_window.save_project, "Ctrl+S"), ("Save As...", self.main_window.save_project_as, "Ctrl+Shift+S"), None, ("Import...", self.main_window.import_file), ("Export...", self.main_window.save_project_as), None, ("Exit", self.main_window.close, "Alt+F4")])

    def _setup_edit_menu(self, menu_bar):
        edit_menu = menu_bar.addMenu("&Edit")
        self._add_actions(edit_menu, [("Undo", self.main_window.undo, "Ctrl+Z"), ("Redo", self.main_window.redo, "Ctrl+Y"), None, ("Delete", self.main_window.delete_selected_actor, "Del")])

    def _setup_view_menu(self, menu_bar):
        view_menu = menu_bar.addMenu("&View")
        self._add_actions(view_menu, [("Reset View", self.main_window.reset_camera_view)])
        panels = view_menu.addMenu("Panels")
        panels.addAction(self.main_window.left_dock.toggleViewAction())
        panels.addAction(self.main_window.bottom_dock.toggleViewAction())

    def _setup_plane_menu(self, menu_bar):
        plane_menu = menu_bar.addMenu("&Plane")
        self._add_actions(plane_menu, [("Define from Input...", self.main_window.define_plane_from_input), ("Define from Surface...", self.main_window.enter_plane_picking_mode), None, ("Reset to XY", self.main_window.reset_working_plane)])

    def _setup_create_menus(self, menu_bar):
        create_2d = menu_bar.addMenu("Create &2D")
        [create_2d.addAction(QAction(s, self.main_window, triggered=lambda c, sh=s.lower(): self.main_window.create_shape_gui(sh))) for s in ["Point", "Line", "Triangle", "Rectangle", "Circle"]]
        create_3d = menu_bar.addMenu("Create &3D")
        [create_3d.addAction(QAction(s, self.main_window, triggered=lambda c, sh=s.lower(): self.main_window.create_shape_gui(sh))) for s in ["Cube", "Sphere", "Cylinder", "Cone", "Pyramid"]]
        adv_shapes = create_3d.addMenu("Advanced Shapes")
        self._add_actions(adv_shapes, [("Extrude...", self.main_window.extrude_gui), ("Revolve...", self.main_window.revolve_gui), ("Sweep...", self.main_window.sweep_gui), ("Loft...", self.main_window.loft_gui)])

    def _setup_modify_menu(self, menu_bar):
        bool_ops = menu_bar.addMenu("&Modify").addMenu("Boolean Operations")
        self._add_actions(bool_ops, [("Union", lambda: self.main_window.perform_boolean_gui('union')), ("Intersection", lambda: self.main_window.perform_boolean_gui('intersection')), ("Difference", lambda: self.main_window.perform_boolean_gui('difference'))])

    def _setup_tools_menu(self, menu_bar):
        tools_menu = menu_bar.addMenu("&Tools")
        self._add_actions(tools_menu, [("Measure...", self.main_window.not_implemented), ("Settings...", self.main_window.not_implemented)])

    def _setup_help_menu(self, menu_bar):
        help_menu = menu_bar.addMenu("&Help")
        self._add_actions(help_menu, [("About", self.main_window.about_dialog)])