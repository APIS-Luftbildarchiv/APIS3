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

from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QTableWidgetItem, QComboBox
from PyQt5.QtCore import Qt

from qgis.core import QgsDataSourceUri, QgsVectorLayer

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'ui', 'apis_site_edit_findspot_conflict_handling.ui'), resource_suffix='')


class APISSiteEditFindspotConflictHandling(QDialog, FORM_CLASS):

    ACTION_0 = "FS belassen"
    ACTION_1 = "FS an FO anpassen"
    ACTION_2 = "FS zuschneiden"

    def __init__(self, iface, dbm, polygonDict, parent=None):
        """Constructor."""
        super(APISSiteEditFindspotConflictHandling, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface
        self.dbm = dbm
        self.polygonDict = polygonDict
        self.closeAble = True

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)

        self.uiCancelEditBtn.clicked.connect(self.onReject)
        self.uiResumeEditBtn.clicked.connect(self.onAccept)

        self.uiFindspotAssessmentTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.loadTable()

    def loadTable(self):
        sites = u", ".join(u"'{0}'".format(siteNumber) for siteNumber in self.polygonDict)

        # Fundstellen des Fundortes Editieren
        uri = QgsDataSourceUri()
        uri.setDatabase(self.dbm.db.databaseName())
        uri.setDataSource('', 'fundstelle', 'geometry')
        findSpotLayer = QgsVectorLayer(uri.uri(), u'Fundstelle', 'spatialite')
        findSpotLayer.setSubsetString(u'"fundortnummer" IN ({0})'.format(sites))

        if findSpotLayer.featureCount() > 0:
            fSIter = findSpotLayer.getFeatures()
            for fSFeature in fSIter:
                fSGeom = fSFeature.geometry()
                sN = fSFeature.attribute("fundortnummer")
                fSN = fSFeature.attribute("fundstellenummer")

                fSNumber = u"{0}.{1}".format(sN, fSN)
                #QMessageBox.information(None, 'Error', u"{0}, {1}, {2}".format(self.polygonDict[sN][0], self.polygonDict[sN][1], self.polygonDict[sN][2]))
                #dj0 = self.polygonDict[sN][0].disjoint(fSGeom)
                #tc0 = self.polygonDict[sN][0].touches(fSGeom)
                #eq0 = self.polygonDict[sN][0].equals(fSGeom)
                #co0 = self.polygonDict[sN][0].contains(fSGeom)
                #co2 = self.polygonDict[sN][2].contains(fSGeom)
                #eq1 = fSGeom.equals(self.polygonDict[sN][1])
                #wi0 = self.polygonDict[sN][0].within(fSGeom)
                #ol0 = self.polygonDict[sN][0].overlaps(fSGeom)
                if self.polygonDict[sN][0].disjoint(fSGeom):
                    relationship = "disjoint"
                    action = [self.ACTION_1]
                elif self.polygonDict[sN][0].touches(fSGeom):
                    relationship = "touches"
                    action = [self.ACTION_1]
                elif self.polygonDict[sN][0].equals(fSGeom):
                    relationship = "equal"
                    action = [self.ACTION_0]
                elif self.polygonDict[sN][0].contains(fSGeom) or self.polygonDict[sN][2].contains(fSGeom):
                    relationship = "contains"
                    if fSGeom.equals(self.polygonDict[sN][1]):
                        action = [self.ACTION_1, self.ACTION_0]
                    else:
                        action = [self.ACTION_0, self.ACTION_1]
                elif self.polygonDict[sN][0].within(fSGeom):
                    relationship = "within"
                    action = [self.ACTION_1]
                elif self.polygonDict[sN][0].overlaps(fSGeom):
                    relationship = "overlaps"
                    if fSGeom.equals(self.polygonDict[sN][1]):
                        action = [self.ACTION_1, self.ACTION_2]
                    else:
                        action = [self.ACTION_2, self.ACTION_1]
                else:
                    relationship = "error"
                    action = []

                rowPos = self.uiFindspotAssessmentTable.rowCount()
                self.uiFindspotAssessmentTable.insertRow(rowPos)

                self.uiFindspotAssessmentTable.setItem(rowPos, 0, QTableWidgetItem(fSNumber))
                self.uiFindspotAssessmentTable.setItem(rowPos, 1, QTableWidgetItem(relationship))

                if len(action) > 1:
                    comboBox = QComboBox()
                    comboBox.addItems(action)
                    self.uiFindspotAssessmentTable.setCellWidget(rowPos, 2, comboBox)
                else:
                    self.uiFindspotAssessmentTable.setItem(rowPos, 2, QTableWidgetItem(", ".join(action)))

    def getActions(self):
        '''
        :return: dict
        '''
        actions = {}
        for row in range(self.uiFindspotAssessmentTable.rowCount()):
            fS = self.uiFindspotAssessmentTable.item(row, 0).text()
            cellType = self.uiFindspotAssessmentTable.cellWidget(row, 2)
            if cellType is None:
                action = self.uiFindspotAssessmentTable.item(row, 2).text()
            else:
                action = cellType.currentText()

            if action == self.ACTION_1:
                actions[fS] = 1
            elif action == self.ACTION_2:
                actions[fS] = 2
            else:
                actions[fS] = 0

        return actions

    def onAccept(self):
        '''
        Check DB
        Save options when pressing OK button
        Update Plugin Status
        '''

        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        #QMessageBox.information(None, u"Abbrechen", u"Vorgang wird abgebrochen!")
        if self.closeAble:
            self.close()

    def closeEvent(self, evnt):
        if self.closeAble:
            super(APISSiteEditFindspotConflictHandling, self).closeEvent(evnt)
        else:
            evnt.ignore()
            #self.setWindowState(QtCore.Qt.WindowMinimized)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and not self.closeAble:
            event.ignore()
