# -*- coding: utf-8 -*-

# Import the PyQt and the QGIS libraries
from __future__ import absolute_import
from builtins import object
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *

#Import own classes and tools
from .mergetwolines import MergeTwoLines
from .movewithsnapping import MoveWithSnapping
from .featureselection import FeatureSelection
from .splitpolygon import SplitPolygon
from .splitline import SplitLine
from .changeattribute import ChangeAttribute

from .createpoint import CreatePoint
from .rectanglearea import RectangleArea
from .scalingfeature import ScalingFeature

# initialize Qt resources from file resources.py
from . import resources


class ecorisUtils(object):

    def __init__(self, iface):
      # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.active = False

    def initGui(self):
        settings = QSettings()
        # create toolbar for this plugin
        self.toolbar = self.iface.addToolBar("ecorisUtils")


        # Get the tool
        self.mergetwolines = MergeTwoLines(self.iface)
        self.movewithsnapping = MoveWithSnapping(self.canvas, self.iface)
        self.changeattribute = ChangeAttribute(self.canvas, self.iface)
        self.featureselection = FeatureSelection(self.canvas, self.iface)
        self.splitpolygon = SplitPolygon(self.canvas, self.iface)
        self.splitline = SplitLine(self.canvas, self.iface)
        self.scalingfeature = ScalingFeature(self.iface)
        self.createpoint = CreatePoint(self.iface)
        self.rectanglearea = RectangleArea(self.iface)

        

        # Create action
        self.actionFeatureSelection = QAction(QIcon(":/plugins/ecorisUtils/icon/iconFeatureSelection.svg"),u"フィーチャ選択", self.iface.mainWindow())
        self.actionFeatureSelection.setObjectName("FeatureSelection")
        self.actionFeatureSelection.setEnabled(True)
        self.actionFeatureSelection.setCheckable(True)
        self.actionFeatureSelection.triggered.connect(self.feature_selection)
        self.toolbar.addAction(self.actionFeatureSelection)

        # Create action
        self.actionChangeAttribute = QAction(QIcon(":/plugins/ecorisUtils/icon/iconChangeAttribute.svg"),u"属性変更", self.iface.mainWindow())
        self.actionChangeAttribute.setObjectName("ChangeAttribute")
        self.actionChangeAttribute.setEnabled(False)
        self.actionChangeAttribute.setCheckable(True)
        self.actionChangeAttribute.triggered.connect(self.change_attribute)
        self.toolbar.addAction(self.actionChangeAttribute)

        # Create action
        self.actionSplitPolygon = QAction(QIcon(":/plugins/ecorisUtils/icon/iconSplitPolygon.svg"),u"ポリゴン分割", self.iface.mainWindow())
        self.actionSplitPolygon.setObjectName("SplitPolygon")
        self.actionSplitPolygon.setEnabled(False)
        self.actionSplitPolygon.setCheckable(True)
        self.actionSplitPolygon.triggered.connect(self.split_polygon)
        self.toolbar.addAction(self.actionSplitPolygon)

        # Create action
        self.actionSplitLine = QAction(QIcon(":/plugins/ecorisUtils/icon/iconSplitLine.svg"),u"ライン分割", self.iface.mainWindow())
        self.actionSplitLine.setObjectName("SplitLine")
        self.actionSplitLine.setEnabled(False)
        self.actionSplitLine.setCheckable(True)
        self.actionSplitLine.triggered.connect(self.split_line)
        self.toolbar.addAction(self.actionSplitLine)

        # Create action
        self.actionMergeTwoLines = QAction(QIcon(":/plugins/ecorisUtils/icon/iconMergeTwoLines.svg"),u"ライン結合", self.iface.mainWindow())
        self.actionMergeTwoLines.setObjectName("MergeTwoLines")
        self.actionMergeTwoLines.setEnabled(False)
        self.actionMergeTwoLines.setCheckable(False)
        self.actionMergeTwoLines.triggered.connect(self.merge_two_lines)
        self.toolbar.addAction(self.actionMergeTwoLines)

        # Create action
        self.actionMoveWithSnapping = QAction(QIcon(":/plugins/ecorisUtils/icon/iconMoveWithSnapping.svg"),u"スナップして移動", self.iface.mainWindow())
        self.actionMoveWithSnapping.setObjectName("MoveWithSnapping")
        self.actionMoveWithSnapping.setEnabled(False)
        self.actionMoveWithSnapping.setCheckable(True)
        self.actionMoveWithSnapping.triggered.connect(self.move_with_snapping)
        self.toolbar.addAction(self.actionMoveWithSnapping)

        # Create action
        self.actionCreatePoint = QAction(QIcon(":/plugins/ecorisUtils/icon/iconCreatePoint.svg"),u"座標からポイント作成", self.iface.mainWindow())
        self.actionCreatePoint.setObjectName("CreatePoint")
        self.actionCreatePoint.setEnabled(True)
        self.actionCreatePoint.setCheckable(False)
        self.actionCreatePoint.triggered.connect(self.create_point)
        self.toolbar.addAction(self.actionCreatePoint)

        # Create action
        self.actionRectangleArea = QAction(QIcon(":/plugins/ecorisUtils/icon/iconRectangleArea.svg"),u"範囲枠作成", self.iface.mainWindow())
        self.actionRectangleArea.setObjectName("RectangleArea")
        self.actionRectangleArea.setEnabled(True)
        self.actionRectangleArea.setCheckable(False)
        self.actionRectangleArea.triggered.connect(self.rectangle_area)
        self.toolbar.addAction(self.actionRectangleArea)

        # Create action
        self.actionScalingFeature = QAction(QIcon(":/plugins/ecorisUtils/icon/iconScalingFeature.svg"),u"フィーチャ拡大縮小", self.iface.mainWindow())
        self.actionScalingFeature.setObjectName("ScalingFeature")
        self.actionScalingFeature.setEnabled(True)
        self.actionScalingFeature.setCheckable(False)
        self.actionScalingFeature.triggered.connect(self.scaling_feature)
        self.toolbar.addAction(self.actionScalingFeature)

        # Connect to signals for button behaviour
        self.iface.layerTreeView().currentLayerChanged.connect(self.toggle)
        self.canvas.mapToolSet.connect(self.deactivate)


    def merge_two_lines(self):
        self.mergetwolines.merge()

    def move_with_snapping(self):
        self.canvas.setMapTool(self.movewithsnapping)
        self.actionMoveWithSnapping.setChecked(True)

    def feature_selection(self):
        self.canvas.setMapTool(self.featureselection)
        self.actionFeatureSelection.setChecked(True)

    def change_attribute(self):
        self.canvas.setMapTool(self.changeattribute)
        self.actionChangeAttribute.setChecked(True)

    def split_polygon(self):
        self.canvas.setMapTool(self.splitpolygon)
        self.actionSplitPolygon.setChecked(True)

    def split_line(self):
        self.canvas.setMapTool(self.splitline)
        self.actionSplitLine.setChecked(True)

    def create_point(self):
        self.createpoint.run()
        
    def rectangle_area(self):
        self.rectanglearea.run()
    
    def scaling_feature(self):
        self.scalingfeature.run()
        
    def toggle(self):
        mc = self.canvas
        layer = mc.currentLayer()
        if layer is None:
            return

        #Decide whether the plugin button/menu is enabled or disabled
        if (layer.isEditable() and (layer.geometryType() == QgsWkbTypes.LineGeometry or
                                    layer.geometryType() == QgsWkbTypes.PolygonGeometry or
                                    layer.geometryType() == QgsWkbTypes.PointGeometry)):

            self.actionMergeTwoLines.setEnabled(True)
            self.actionMoveWithSnapping.setEnabled(True)
            self.actionSplitPolygon.setEnabled(True)
            self.actionChangeAttribute.setEnabled(True)
            self.actionSplitLine.setEnabled(True)

            try:  # remove any existing connection first
                layer.editingStopped.disconnect(self.toggle)
            except TypeError:  # missing connection
                pass
            layer.editingStopped.connect(self.toggle)
            try:
                layer.editingStarted.disconnect(self.toggle)
            except TypeError:  # missing connection
                pass
        else:
            self.actionMergeTwoLines.setEnabled(False)
            self.actionMoveWithSnapping.setEnabled(False)
            self.actionSplitPolygon.setEnabled(False)
            self.actionChangeAttribute.setEnabled(False)
            self.actionSplitLine.setEnabled(False)

            if (layer.type() == QgsMapLayer.VectorLayer and
                    (layer.geometryType() == QgsWkbTypes.LineGeometry or
                     layer.geometryType() == QgsWkbTypes.PolygonGeometry or
                     layer.geometryType() == QgsWkbTypes.PointGeometry)):
                try:  # remove any existing connection first
                    layer.editingStarted.disconnect(self.toggle)
                except TypeError:  # missing connection
                    pass
                layer.editingStarted.connect(self.toggle)
                try:
                    layer.editingStopped.disconnect(self.toggle)
                except TypeError:  # missing connection
                    pass


    def deactivate(self):
        #self.actionMergeTwoLines.setChecked(False)
        self.actionMoveWithSnapping.setChecked(False)
        self.actionFeatureSelection.setChecked(False)
        self.actionSplitPolygon.setChecked(False)
        self.actionChangeAttribute.setChecked(False)
        self.actionSplitLine.setChecked(False)

    def unload(self):
        self.toolbar.removeAction(self.actionMergeTwoLines)
        self.toolbar.removeAction(self.actionMoveWithSnapping)
        self.toolbar.removeAction(self.actionFeatureSelection)
        self.toolbar.removeAction(self.actionSplitPolygon)
        self.toolbar.removeAction(self.actionChangeAttribute)
        self.toolbar.removeAction(self.actionSplitLine)
        del self.toolbar

    def log(self, msg):
        QgsMessageLog.logMessage(msg, 'MyPlugin', Qgis.Info)
