# -*- coding: utf-8 -*-
def classFactory(iface):
    from .ecorisutils import ecorisUtils
    return ecorisUtils(iface)
