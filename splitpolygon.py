# -*- coding: utf-8 -*-

from builtins import range
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *
import math
import numpy as np

class SplitPolygon(QgsMapTool):

    def __init__(self, canvas,iface):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface

    def runSplit(self):

        #選択フィーチャからポリゴンレイヤー取得

        polygon_layer, polygons = self.selectedPolygonFeatures()
        line_layer, lines = self.selectedLineFeatures()
        if polygon_layer is None:
            QMessageBox.warning(None, "Warning", u"ポリゴンレイヤが選択されていません。")
            return
        if line_layer is None:
            QMessageBox.warning(None, "Warning", u"ラインレイヤが選択されていません。")
            return

        polygon_layer.invertSelection()
        invert_selection_ids = polygon_layer.selectedFeatureIds()
        polygon_layer.invertSelection()

        for line in lines:
            self.splitSelectedPolygonByLine(line)
            polygon_layer.selectByIds(invert_selection_ids)
            polygon_layer.invertSelection()
        polygon_layer.removeSelection()
        line_layer.removeSelection()

    def splitSelectedPolygonByLine(self,line):
        polygon_layer, polygons = self.selectedPolygonFeatures()
        line_geom = QgsGeometry(line.geometry())
        polygon_layer.beginEditCommand("Features split")
        for i, polygon in enumerate(polygons):
            polygon_geom = QgsGeometry(polygon.geometry())
            # QGIS 3 reports as multiline or multipolygon for single in QGIS 2.
            polygon_geom.convertToSingleType()
            line_geom.convertToSingleType()
            result, newGeometries, topoTestPoints = polygon_geom.splitGeometry(line_geom.asPolyline(), False)
            if result == 0:
                newFeatures = self.makeFeaturesFromGeometries(polygon_layer, polygon, newGeometries)
                polygons[i].setGeometry(polygon_geom)
                polygon_layer.updateFeature(polygons[i])
                polygon_layer.addFeatures(newFeatures)
            elif result == 1001 or result == 1002:
                #self.log("{}".format(result))
                QMessageBox.warning(None, "Warning", u"ジオメトリが不正です。")
        polygon_layer.endEditCommand()


    def dtGetFeatureForId(self,layer, fid):
        '''Function that returns the QgsFeature with FeatureId *fid* in QgsVectorLayer *layer*'''
        feat = QgsFeature()

        if layer.getFeatures(QgsFeatureRequest().setFilterFid(fid)).nextFeature(feat):
            return feat
        else:
            return None

    def dtCreateFeature(self,layer):
        '''Create an empty feature for the *layer*'''
        if isinstance(layer, QgsVectorLayer):
            newFeature = QgsFeature()
            provider = layer.dataProvider()
            fields = layer.fields()

            newFeature.initAttributes(fields.count())

            for i in range(fields.count()):
                newFeature.setAttribute(i, provider.defaultValue(i))

            return newFeature
        else:
            return None

    def dtCopyFeature(self, layer, srcFeature=None, srcFid=None):
        '''Copy the QgsFeature with FeatureId *srcFid* in *layer* and return it. Alternatively the
        source Feature can be given as paramter. The feature is not added to the layer!'''
        if srcFid != None:
            srcFeature = self.dtGetFeatureForId(layer, srcFid)

        if srcFeature:
            newFeature = self.dtCreateFeature(layer)

            # # copy the attribute values#
            # pkFields = layer.dataProvider().pkAttributeIndexes()
            # fields = layer.pendingFields()
            # for i in range(fields.count()):
            #     # do not copy the PK value if there is a PK field
            #     if i in pkFields:
            #         continue
            #     else:
            #         newFeature.setAttribute(i, srcFeature[i])

            return newFeature
        else:
            return None

    def makeFeaturesFromGeometries(self, layer, srcFeat, geometries):
        '''create new features from geometries and copy attributes from srcFeat'''
        newFeatures = []

        for aGeom in geometries:
            newFeat = self.dtCopyFeature(layer, srcFeat)
            newFeat.setGeometry(aGeom)
            newFeatures.append(newFeat)

        return newFeatures

    def selectedPolygonFeatures(self):
        layer_list = QgsProject.instance().layerTreeRoot().children()
        layers = [lyr.layer() for lyr in layer_list]
        layer = None
        features = []
        for l in layers:
            if QgsProject.instance().layerTreeRoot().findLayer(l.id()).isVisible():
                if l.type() == QgsMapLayer.VectorLayer and l.geometryType() == QgsWkbTypes.PolygonGeometry:
                    fids = l.selectedFeatureIds()
                    features = [self.getFeatureById(l,fid) for fid in fids]
                    if len(features) > 0:
                        layer = l
                        return layer, features
        return layer, features

    def selectedLineFeatures(self):
        layer_list = QgsProject.instance().layerTreeRoot().children()
        layers = [lyr.layer() for lyr in layer_list]
        layer = None
        features = []
        for l in layers:
            if QgsProject.instance().layerTreeRoot().findLayer(l.id()).isVisible():
                if l.type() == QgsMapLayer.VectorLayer and l.geometryType() == QgsWkbTypes.LineGeometry:
                    fids = l.selectedFeatureIds()
                    features = [self.getFeatureById(l,fid) for fid in fids]
                    if len(features) > 0:
                        layer = l
                        return layer, features
        return layer, features

    def getFeatureById(self,layer,featid):
        features = [f for f in layer.getFeatures(QgsFeatureRequest().setFilterFids([featid]))]
        if len(features) != 1:
            return None
        else:
            return features[0]

    def check_crs(self):
        layer = self.canvas.currentLayer()
        renderer = self.canvas.mapSettings()
        self.layerCRS = layer.crs()
        self.projectCRS = renderer.destinationCrs()
    def showSettingsWarning(self):
        pass
    def activate(self):
        self.cursor = QCursor()
        self.cursor.setShape(Qt.ArrowCursor)
        self.canvas.setCursor(self.cursor)
        self.runSplit()

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
