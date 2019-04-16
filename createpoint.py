# -*- coding: utf-8 -*-

from __future__ import absolute_import
from builtins import object
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *


class CreatePoint(object):

    def __init__(self, iface):
        self.iface = iface

    def run(self):
        qid = QInputDialog()

        input, ok = QInputDialog.getText(qid, "Enter Coordinates", "Enter New Coordinates as 'xcoord,ycoord'",
                                         QLineEdit.Normal, "135" + "," + "35")
        if ok:
            x = input.split(",")[0]
            y = input.split(",")[1]
            self.create(float(x),float(y))

    def create(self,x,y):
        mem_layer = QgsVectorLayer("Point", "temporary_points", "memory")
        prov = mem_layer.dataProvider()
        new_feat = QgsFeature()
        new_feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x,y)))
        prov.addFeatures([new_feat])
        QgsProject.instance().addMapLayer(mem_layer)
