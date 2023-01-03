# -*- coding: utf-8 -*-
"""
/***************************************************************************
 APISDialog
                                 A QGIS plugin
 APIS - Archaeological Prospection Information System - A QGIS Plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-04-10
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Johannes Liem (digitalcartography.org) and Aerial Archive of the University of Vienna
        email                : johannes.liem@digitalcartography.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import requests

from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import QSettings

from APIS.src.apis_utils import SetWindowSize, GetWindowSize

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'ui', 'apis_overpass_request.ui'), resource_suffix='')


class APISOverpassRequest(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(APISOverpassRequest, self).__init__(parent)

        self.setupUi(self)
        if GetWindowSize("overpass_request"):
            self.resize(GetWindowSize("overpass_request"))

        self.lon = None
        self.lat = None

        # More Info about Overpass API: https://wiki.openstreetmap.org/wiki/Overpass_API
        self.overpassUrl = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat).value("overpass_url", "https://overpass-api.de/api/interpreter")

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.uiRequestBtn.clicked.connect(self.executeRequest)
        self.uiAdminLevelList.itemDoubleClicked.connect(self.useSelection)

    def setLatLon(self, lat, lon):
        if lon >= -180.0 and lon <= 180.0 and lat >= -90 and lat <= 90:
            self.lat = lat
            self.lon = lon
            self.uiLonLbl.setText("{0:.5f}".format(self.lon))
            self.uiLatLbl.setText("{0:.5f}".format(self.lat))
            self.uiRequestBtn.setEnabled(True)
            self.executeRequest()

    def executeRequest(self):
        if self.lon and self.lat:
            r = requests.get("""{0}?data=[out:json];is_in({1},{2});area._[admin_level];out;""".format(self.overpassUrl, self.lat, self.lon))
            if r.status_code == 200:
                opJson = r.json()
                result = [(el['tags']['admin_level'], el['tags']['name']) for el in opJson['elements']]
                result.sort(key=lambda x: int(x[0]), reverse=True)
                for value in result:
                    self.uiAdminLevelList.addItem(u"[{0}]: {1}".format(value[0], value[1]))
                self.uiRequestBtn.setEnabled(False)
            else:
                QMessageBox.warning(self, u"Request Error", u"Fehler bei der online Abfrage (Status Code: {0}).".format(r.status_code))

    def useSelection(self, item):
        self.accept()
        #QMessageBox.warning(None, "RequestError", u"{0}".format(item.text().split(':')[1].strip()))

    def getSelection(self):
        selection = self.uiAdminLevelList.selectedItems()
        if len(selection) != 1:
            return None
        return u"{0}".format(selection[0].text().split(':')[1].strip())

    def onAccept(self):
        '''
        Check DB
        Save options when pressing OK button
        Update Plugin Status
        '''
        SetWindowSize("overpass_request", self.size())
        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        SetWindowSize("overpass_request", self.size())
        self.close()
