# -*- coding: utf-8 -*-

from __future__ import absolute_import
from builtins import object
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *

##ScalingFeature=name
##Scale=number 2.0

class ScalingFeature(object):

    def __init__(self, iface):
        self.iface = iface

    def run(self):
        qid = QInputDialog()

        input, ok = QInputDialog.getText(qid, "Enter Scale", "'Scale'",
                                         QLineEdit.Normal, "2.0")
        if ok:
            scale = input
            self.create(float(scale))


    def scalingPoint(self,cent,seg,scale):
        w = scale * (seg[0] - cent[0])
        h = scale * (seg[1] - cent[1])
        p = QgsPointXY(cent[0] + w, cent[1] + h)
        return p

    def create(self, scale):
        layer = self.iface.activeLayer()
        features = layer.selectedFeatures()
        if len(features)==0:
            features = layer.getFeatures()

        epsg = layer.crs().postgisSrid()


        if layer.geometryType()==QgsWkbTypes.LineGeometry or layer.geometryType()==QgsWkbTypes.PolygonGeometry:
            if layer.geometryType() == QgsWkbTypes.LineGeometry:
                geomtype = "LineString"
            elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                geomtype = "Polygon"
            uri = geomtype + "?crs=epsg:" + str(epsg)
            mem_layer = QgsVectorLayer(uri, 'scaling_layer', 'memory')
            prov = mem_layer.dataProvider()

            fields=layer.dataProvider().fields().toList()
            mem_layer.dataProvider().addAttributes(fields)
            mem_layer.updateFields()

            scaling_feature=[]
            for feature in features:
                new_feat = QgsFeature()
                new_feat.setAttributes(feature.attributes())
                geom = feature.geometry()
                geom.convertToSingleType()
                if layer.geometryType()==QgsWkbTypes.LineGeometry:
                    geom_points = geom.asPolyline()
                elif layer.geometryType()==QgsWkbTypes.PolygonGeometry:
                    geom_points = geom.asPolygon()[0]
                cent = feature.geometry().centroid().asPoint()
                points=[]
                for seg in geom_points:
                    p = self.scalingPoint(cent,seg,scale)
                    points.append(p)
                if layer.geometryType()==QgsWkbTypes.LineGeometry:
                    new_feat.setGeometry(QgsGeometry.fromPolylineXY(points))
                elif layer.geometryType()==QgsWkbTypes.PolygonGeometry:
                    new_feat.setGeometry(QgsGeometry.fromPolygonXY([points]))
                scaling_feature.append(new_feat)

            prov.addFeatures(scaling_feature)
            QgsProject.instance().addMapLayer(mem_layer)
        else:
            QMessageBox.warning(None, "Warning", u"ラインとポリゴン以外は変換できません")
