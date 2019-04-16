# -*- coding: utf-8 -*-

from __future__ import absolute_import
from builtins import object
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *

class RectangleArea(object):

    def __init__(self, iface):
        self.iface = iface


    def run(self):
        qid = QInputDialog()

        input, ok = QInputDialog.getText(qid, "Enter Rectangle size", "'Scale,Height,Width'",
                                         QLineEdit.Normal, "25000" + "," + "25" + "," + "17")
        if ok:
            scale = input.split(",")[0]
            height = input.split(",")[1]
            width = input.split(",")[2]
            self.create(float(scale),float(height),float(width))

    def create(self, scale, height, width):
        canvas = self.iface.mapCanvas()
        projectCRS = canvas.mapSettings().destinationCrs()
        if projectCRS.projectionAcronym() != "longlat":
            epsg = projectCRS.postgisSrid()
            uri = "Polygon?crs=epsg:" + str(epsg) + "&field=id:integer"
            mem_layer = QgsVectorLayer(uri, 'rectangular_area', 'memory')
            prov = mem_layer.dataProvider()

            x=width*scale/100
            y=height*scale/100

            p = canvas.extent().center()
            new_feat = QgsFeature()
            new_feat.setAttributes([0])
            p1 = QgsPointXY(p[0]-x/2.0, p[1]-y/2.0)
            p2 = QgsPointXY(p[0]+x/2.0, p[1]+y/2.0)
            new_ext = QgsRectangle(p1,p2)
            new_tmp_feat = new_ext.asWktPolygon()
            new_feat.setGeometry(QgsGeometry.fromWkt(new_tmp_feat))
            prov.addFeatures([new_feat])

            QgsProject.instance().addMapLayer(mem_layer)
        else:
            QMessageBox.warning(None, "Warning", u"プロジェクトの投影法を緯度経度から変更してください")