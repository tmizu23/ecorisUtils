# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *
import json
import os

class ChangeAttributeSettings():
    def __init__(self, name, column, value, menu, shortcut, cursor):
        self.name = name
        self.column = column
        self.value = value
        self.menu = menu
        self.shortcut = shortcut
        self.cursor = cursor

class ChangeAttribute(QgsMapTool):

    def __init__(self, canvas, iface):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.value = None  # current attribute value
        self.column = None  # current attribute column
        self.defaultCursor = QCursor(QPixmap(':/plugins/ecorisUtils/icon/Esc.svg'), 0, 0)
        self.canvas.setCursor(self.defaultCursor)  # default cursor

        # self.attribute_settings = []
        # # attribute list and icon
        # ## LMH
        # name = "LMH"
        # column = None
        # value = ["L", "M", "H"]
        # menu = ["L", "M", "H"]
        # shortcut = [Qt.Key_L, Qt.Key_M, Qt.Key_H]
        # cursor = [QCursor(QPixmap(':/plugins/ecorisUtils/icon/L.svg')),
        #                    QCursor(QPixmap(':/plugins/ecorisUtils/icon/M.svg')),
        #                    QCursor(QPixmap(':/plugins/ecorisUtils/icon/H.svg'))]
        # self.attribute_settings.append(ChangeAttributeSettings(name, column, value, menu, shortcut, cursor))
        #
        # ## koudou
        # name = "行動"
        # column = None
        # value = [u"飛翔", u"旋回上昇", u"ディスプレイ", u"攻撃", u"被攻撃", u"餌運び", u"探餌", u"狩り", u"巣材運び"]
        # menu = [u"飛翔 (A)", u"旋回上昇 (B)", u"ディスプレイ(C)", u"攻撃 (D)", u"被攻撃 (E)", u"餌運び (F)", u"探餌 (G)",
        #                         u"狩り (H)", u"巣材運び (I)"]
        # shortcut = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I]
        # cursor = [QCursor(QPixmap(':/plugins/ecorisUtils/icon/飛翔.svg')),
        #                       QCursor(QPixmap(':/plugins/ecorisUtils/icon/旋回上昇.svg')),
        #                       QCursor(QPixmap(':/plugins/ecorisUtils/icon/ディスプレイ.svg')),
        #                       QCursor(QPixmap(':/plugins/ecorisUtils/icon/攻撃.svg')),
        #                       QCursor(QPixmap(':/plugins/ecorisUtils/icon/被攻撃.svg')),
        #                       QCursor(QPixmap(':/plugins/ecorisUtils/icon/餌運び.svg')),
        #                       QCursor(QPixmap(':/plugins/ecorisUtils/icon/探餌.svg')),
        #                       QCursor(QPixmap(':/plugins/ecorisUtils/icon/狩り.svg')),
        #                       QCursor(QPixmap(':/plugins/ecorisUtils/icon/巣材運び.svg'))]
        # self.attribute_settings.append(ChangeAttributeSettings(name, column, value, menu, shortcut, cursor))

        # load setting and initialize menu
        self.load_settings()
        self.generate_menu()

    def load_file(self, json_file=None):
        if json_file is None:
            fname = QFileDialog.getOpenFileName(None, 'Load file', os.path.dirname(__file__),"json (*.json)")
            json_file = fname[0]
        if os.path.exists(json_file):
            self.attribute_settings = []
            self.log("{}".format(json_file))
            f = open(json_file, 'r')
            json_data = json.load(f)
            f.close()
            dirname = os.path.dirname(json_file)
            for j in json_data:
                name = j["name"]
                value = j["value"]
                menu = j["menu"]
                shortcut = [eval("Qt.Key_"+ s) for s in j["shortcut"]]
                cursor = [QCursor(QPixmap(os.path.join(dirname, svg)),0,0) for svg in j["cursor"]]
                column = None
                self.attribute_settings.append(ChangeAttributeSettings(name, column, value, menu, shortcut, cursor))
            self.generate_menu()
            settings = QSettings()
            settings.setValue("ecorisUtils/json_file", json_file)

    def load_settings(self):
        settings = QSettings()
        # try to load json_file
        json_file = settings.value("ecorisUtils/json_file")
        if json_file is None or not os.path.exists(json_file):
            json_file = os.path.join(os.path.dirname(__file__),"default_settings.json")
        self.load_file(json_file)

        for i, s in enumerate(self.attribute_settings):
            self.attribute_settings[i].column = settings.value("ecorisUtils/" + s.name)

    def generate_menu(self):
        self.menu = QMenu()

        for s in self.attribute_settings:
            if s.column is not None:
                submenu = self.menu.addMenu(s.name + "(" + s.column +")")
                for i, act in enumerate(s.menu):
                    submenu.addAction(act).triggered.connect(lambda checked, name=s.name,idx=i: self.set_attribute(name, idx))
                submenu.addSeparator()
                submenu.addAction(u"列再設定").triggered.connect(lambda checked, name=s.name: self.set_column(name))
                self.menu.addSeparator()
            else:
                self.menu.addAction(s.name + u"の列設定").triggered.connect(lambda checked, name=s.name: self.set_column(name))
                self.menu.addSeparator()

        self.menu.addAction("属性表示 (Esc)").triggered.connect(self.reset_value)
        self.menu.addSeparator()
        self.menu.addAction("設定ファイル").triggered.connect(lambda: self.load_file(None))

    def reset_value(self):
        self.value = None
        self.canvas.setCursor(self.defaultCursor)

    def set_column(self, name):
        layer = self.canvas.currentLayer()
        col_list = layer.fields().names()
        column, ok = QInputDialog.getItem(QInputDialog(), u"列選択", "", col_list, 0, False)
        COL = layer.fields().indexFromName(column)
        field_type = layer.fields()[COL].typeName()
        self.log("{}".format(field_type))
        if ok:
            if field_type == "String" or field_type == "string":
                settings = QSettings()
                for i, s in enumerate(self.attribute_settings):
                    if name == s.name:
                        self.attribute_settings[i].column = column
                        settings.setValue("ecorisUtils/" + s.name, column)
                    self.generate_menu()
            else:
                QMessageBox.warning(None, "Warning", u"文字列型の列を選択してください")


    def canvasPressEvent(self, event):
        layer = self.canvas.currentLayer()
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
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
        self.log("key:{}".format(event.key()))
        if event.key() == Qt.Key_Escape:
            self.reset_value()
            return

        for s in self.attribute_settings:
            if s.column is not None:
                for i, key in enumerate(s.shortcut):
                    if event.key() == key:
                        self.set_attribute(s.name, i)
                        return


    def set_attribute(self, name, idx):
        for s in self.attribute_settings:
            if name == s.name:
                self.column = s.column
                self.value = s.value[idx]
                self.canvas.setCursor(s.cursor[idx])
                break

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
                QMessageBox.warning(None, "Warning", u"列がありません。列を再設定してください。")

        self.canvas.refresh()


    def activate(self):
        self.canvas.setCursor(self.defaultCursor)
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
