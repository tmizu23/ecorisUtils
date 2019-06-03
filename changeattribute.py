# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *

class ChangeAttribute(QgsMapTool):

    def __init__(self, canvas, iface):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.value = None  # current attribute value
        self.column = None  # current attribute column
        self.canvas.setCursor(Qt.ArrowCursor)  # default cursor

        # attribute list and icon
        ## LMH
        self.LMH_column = None
        self.LMH_value = ["L", "M", "H"]
        self.LMH_menu_str = ["L", "M", "H"]
        self.LMH_shortcut_list = [Qt.Key_L, Qt.Key_M, Qt.Key_H]
        self.LMH_cursor = [QCursor(QPixmap(':/plugins/ecorisUtils/icon/L.svg')),
                           QCursor(QPixmap(':/plugins/ecorisUtils/icon/M.svg')),
                           QCursor(QPixmap(':/plugins/ecorisUtils/icon/H.svg'))]

        ## koudou
        self.koudou_column = None
        self.koudou_value = [u"飛翔", u"旋回上昇", u"ディスプレイ", u"攻撃", u"被攻撃", u"餌運び", u"探餌", u"狩り", u"巣材運び"]
        self.koudou_menu_str = [u"飛翔 (A)", u"旋回上昇 (B)", u"ディスプレイ(C)", u"攻撃 (D)", u"被攻撃 (E)", u"餌運び (F)", u"探餌 (G)",
                                u"狩り (H)", u"巣材運び (I)"]
        self.koudou_shortcut_list = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I]
        self.koudou_cursor = [QCursor(QPixmap(':/plugins/ecorisUtils/icon/飛翔.svg')),
                              QCursor(QPixmap(':/plugins/ecorisUtils/icon/旋回上昇.svg')),
                              QCursor(QPixmap(':/plugins/ecorisUtils/icon/ディスプレイ.svg')),
                              QCursor(QPixmap(':/plugins/ecorisUtils/icon/攻撃.svg')),
                              QCursor(QPixmap(':/plugins/ecorisUtils/icon/被攻撃.svg')),
                              QCursor(QPixmap(':/plugins/ecorisUtils/icon/餌運び.svg')),
                              QCursor(QPixmap(':/plugins/ecorisUtils/icon/探餌.svg')),
                              QCursor(QPixmap(':/plugins/ecorisUtils/icon/狩り.svg')),
                              QCursor(QPixmap(':/plugins/ecorisUtils/icon/巣材運び.svg'))]

        # load setting and initialize menu
        self.load_settings()
        self.generate_menu()

    def load_settings(self):
        settings = QSettings()
        self.LMH_column = settings.value("ecorisUtils/LMH_column")
        self.koudou_column = settings.value("ecorisUtils/koudou_column")

    def generate_menu(self):
        self.menu = QMenu()

        if self.LMH_column is not None:
            submenu = self.menu.addMenu(self.LMH_column)
            for i, act in enumerate(self.LMH_menu_str):
                submenu.addAction(act).triggered.connect(lambda checked, process_type="LMH",idx=i: self.set_attribute(process_type, idx))
            submenu.addSeparator()
            LMH_Action = submenu.addAction(u"列再設定")
            LMH_Action.triggered.connect(lambda: self.set_column("LMH"))
            self.menu.addSeparator()
        else:
            LMH_Action = self.menu.addAction(u"LMHの列設定")
            LMH_Action.triggered.connect(lambda: self.set_column("LMH"))
            self.menu.addSeparator()

        if self.koudou_column is not None:
            submenu = self.menu.addMenu(self.koudou_column)
            for i, act in enumerate(self.koudou_menu_str):
                submenu.addAction(act).triggered.connect(lambda checked, process_type="koudou", idx=i: self.set_attribute(process_type, idx))
            submenu.addSeparator()
            koudou_Action = submenu.addAction(u"列再設定")
            koudou_Action.triggered.connect(lambda: self.set_column("koudou"))
            self.menu.addSeparator()
        else:
            koudou_Action = self.menu.addAction(u"行動の列設定")
            koudou_Action.triggered.connect(lambda: self.set_column("koudou"))
            self.menu.addSeparator()
        reset_value_Action = self.menu.addAction("属性表示 (Esc)")
        reset_value_Action.triggered.connect(self.reset_value)

    def reset_value(self):
        self.value = None
        self.canvas.setCursor(Qt.ArrowCursor)

    def set_column(self, process_type):
        layer = self.canvas.currentLayer()
        col_list = layer.fields().names()
        column, ok = QInputDialog.getItem(QInputDialog(), u"列選択", "", col_list, 0, False)
        COL = layer.fields().indexFromName(column)
        field_type = layer.fields()[COL].typeName()
        if ok:
            if field_type == "String":
                settings = QSettings()
                if process_type == "LMH":
                    self.LMH_column = column
                    settings.setValue("ecorisUtils/LMH_column", column)
                elif process_type == "koudou":
                    self.koudou_column = column
                    settings.setValue("ecorisUtils/koudou_column", column)
                self.generate_menu()
            else:
                QMessageBox.warning(None, "Warning", u"文字列型の列を選択してください")


    def canvasPressEvent(self, event):
        layer = self.canvas.currentLayer()
        if not layer or layer.type() != QgsMapLayer.VectorLayer or layer.geometryType() != QgsWkbTypes.LineGeometry:
            return
        if event.button() == Qt.RightButton:
            self.menu.exec_(self.canvas.mapToGlobal(QPoint(event.pos().x() + 5, event.pos().y())))
        else:
            #layer.removeSelection()
            point = self.toMapCoordinates(event.pos())
            near, f = self.getNearFeature(layer, point)
            if near:
                #layer.select(f.id())
                if self.column is None or self.value is None:
                    self.editAttribute(f, None, None, showdlg=True)
                else:
                    self.editAttribute(f, self.column, self.value)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reset_value()
        elif self.LMH_column is not None:
            for i, key in enumerate(self.LMH_shortcut_list):
                if event.key() == key:
                    self.set_attribute("LMH",i)
                    break
        elif self.koudou_column is not None:
            for i, key in enumerate(self.koudou_shortcut_list):
                if event.key() == key:
                    self.set_attribute("koudou", i)
                    break

    def set_attribute(self, process_type, idx):
        if process_type == "LMH":
            self.column = self.LMH_column
            self.value = self.LMH_value[idx]
            self.canvas.setCursor(self.LMH_cursor[idx])
        elif process_type == "koudou":
            self.column = self.koudou_column
            self.value = self.koudou_value[idx]
            self.canvas.setCursor(self.koudou_cursor[idx])


    def getNearFeature(self, layer,point):
        d = self.canvas.mapUnitsPerPixel() * 10
        rect = QgsRectangle((point.x() - d), (point.y() - d), (point.x() + d), (point.y() + d))
        self.check_crs()
        if self.layerCRS.srsid() != self.projectCRS.srsid():
            rectGeom = QgsGeometry.fromRect(rect)
            rectGeom.transform(QgsCoordinateTransform(self.projectCRS, self.layerCRS, QgsProject.instance()))
            rect = rectGeom.boundingBox()
        request = QgsFeatureRequest()
        request.setLimit(1)
        request.setFilterRect(rect)
        f = [feat for feat in layer.getFeatures(request)]  # only one because of setlimit(1)
        if len(f)==0:
            return False,None
        else:
            return True,f[0]

    def check_crs(self):
        layer = self.canvas.currentLayer()
        renderer = self.canvas.mapSettings()
        self.layerCRS = layer.crs()
        self.projectCRS = renderer.destinationCrs()

    def editAttribute(self, f, column, value, showdlg=False):
        layer = self.canvas.currentLayer()
        layer.beginEditCommand("edited attribute")
        if showdlg:
            dlg = self.iface.getFeatureForm(layer, f)
            if dlg.exec_():
                layer.endEditCommand()
            else:
                layer.destroyEditCommand()
        else:
            COL = layer.fields().indexFromName(column)
            if COL >= 0:
                layer.changeAttributeValue(f.id(), COL, value)
                layer.endEditCommand()
            else:
                layer.destroyEditCommand()
                QMessageBox.warning(None, "Warning", u"列がありません。列を再設定してください。ｒ")

        self.canvas.refresh()


    def activate(self):
        self.cursor = QCursor()
        self.cursor.setShape(Qt.ArrowCursor)
        self.canvas.setCursor(self.cursor)
        self.alt = False

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False
    def isTransient(self):
        return False
    def isEditTool(self):
        return True
    def log(self,msg):
        QgsMessageLog.logMessage(msg, 'MyPlugin',Qgis.Info)
