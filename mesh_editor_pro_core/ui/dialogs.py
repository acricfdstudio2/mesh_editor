# ===================================================================================
# Python file : dialogs.py
# Description:
# Contains all custom QDialog classes used for user input. This module is
# entirely part of the GUI layer.
# ===================================================================================

from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QFormLayout, QListWidget, QDoubleSpinBox, QSlider, QHBoxLayout, QSpinBox, QVBoxLayout, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal

class BaseShapeDialog(QDialog):
    def __init__(self, p=None): super().__init__(p); self.l = QFormLayout(self); self.w = {}
    def add_spinbox(self, n, lbl, d=0.0, min_v=-1e4, max_v=1e4, dec=2): s=QDoubleSpinBox(); s.setRange(min_v,max_v); s.setValue(d); s.setDecimals(dec); self.l.addRow(lbl,s); self.w[n]=s; return s
    def finalize(self): b=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); b.accepted.connect(self.accept); b.rejected.connect(self.reject); self.l.addWidget(b)
    def getValues(self): return {n:w.value() for n,w in self.w.items()}
class PointDialog(BaseShapeDialog):
    def __init__(self,p=None): super().__init__(p); self.setWindowTitle("Point"); self.add_spinbox("X","X:"); self.add_spinbox("Y","Y:"); self.finalize()
class LineDialog(BaseShapeDialog):
    def __init__(self,p=None): super().__init__(p); self.setWindowTitle("Line"); self.add_spinbox("X1","Start X:",-1); self.add_spinbox("Y1","Start Y:"); self.add_spinbox("X2","End X:",1); self.add_spinbox("Y2","End Y:"); self.finalize()
class RectangleDialog(BaseShapeDialog):
    def __init__(self,p=None): super().__init__(p); self.setWindowTitle("Rectangle"); self.add_spinbox("Width","W:",2,0.1); self.add_spinbox("Height","H:",1,0.1); self.finalize()
class CircleDialog(BaseShapeDialog):
    def __init__(self,p=None): super().__init__(p); self.setWindowTitle("Circle"); self.add_spinbox("Radius","R:",1,0.1); s=QSpinBox(); s.setRange(3,200); s.setValue(32); self.l.addRow("Res:",s); self.w["Resolution"]=s; self.finalize()
class PlaneDialog(BaseShapeDialog):
    def __init__(self,p=None): super().__init__(p); self.setWindowTitle("Plane"); self.add_spinbox("OX","O X:"); self.add_spinbox("OY","O Y:"); self.add_spinbox("OZ","O Z:"); self.add_spinbox("NX","N X:"); self.add_spinbox("NY","N Y:"); self.add_spinbox("NZ","N Z:",1); self.finalize()
class ParameterDialog(QDialog):
    vChanged = pyqtSignal()
    def __init__(self, p, parent=None):
        super().__init__(parent); self.setWindowTitle("Parameters"); l=QFormLayout(self); self.w={}
        for n,(d,min_v,max_v,dec) in p.items():
            sb=QDoubleSpinBox(); sb.setRange(min_v,max_v); sb.setValue(d); sb.setDecimals(dec); sb.setSingleStep(10**(-dec)); sl=QSlider(Qt.Horizontal); sl.setRange(0,1000)
            sl.valueChanged.connect(lambda p,s=sb,mn=min_v,mx=max_v:s.setValue(mn+(p/1000)*(mx-mn))); sb.valueChanged.connect(lambda v,s=sl,mn=min_v,mx=max_v:s.setValue(int(((v-mn)/(mx-mn))*1000) if mx>mn else 0))
            sb.valueChanged.emit(d); sb.valueChanged.connect(self.vChanged.emit); h=QHBoxLayout(); h.addWidget(sb); h.addWidget(sl); l.addRow(f"{n}:",h); self.w[n]=sb
        b=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); b.accepted.connect(self.accept); b.rejected.connect(self.reject); l.addWidget(b)
    def getValues(self): return {n:w.value() for n,w in self.w.items()}
class ObjectSelectionDialog(QDialog):
    def __init__(self, t, a, m, p=None):
        super().__init__(p); self.setWindowTitle(t); l=QVBoxLayout(self); self.lw=QListWidget(); self.lw.addItems([act.name for act in a if act.name!="working_plane_visual"]); self.lw.setSelectionMode(m); l.addWidget(self.lw)
        b=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); b.accepted.connect(self.accept); b.rejected.connect(self.reject); l.addWidget(b); self.sel=[]
    def accept(self):
        amap={a.name:a for a in self.parent().actors}; [self.sel.append(amap[i.text()]) for i in self.lw.selectedItems() if i.text() in amap]; super().accept()