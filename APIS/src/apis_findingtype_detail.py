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
from PyQt5.QtWidgets import QDialog, QMessageBox, QAbstractItemView
from PyQt5.QtCore import QItemSelection, QItemSelectionModel
from PyQt5.QtSql import QSqlRelationalTableModel

from APIS.src.apis_utils import SetWindowSize, GetWindowSize

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'ui', 'apis_findingtype_detail.ui'), resource_suffix='')


class APISFindingTypeDetail(QDialog, FORM_CLASS):
    def __init__(self, iface, dbm, parent=None):
        """Constructor."""
        super(APISFindingTypeDetail, self).__init__(parent)
        self.iface = iface
        self.dbm = dbm
        self.setupUi(self)
        if GetWindowSize("findingtype_detail"):
            self.resize(GetWindowSize("findingtype_detail"))

        self.accepted.connect(self.onClose)
        self.rejected.connect(self.onClose)

        self.uiResetSelectionBtn.clicked.connect(lambda: self.setSelectionForFindingTypeDetail(self.uiFindingTypeDetailEdit.text().strip()))
        self.uiDropSelectionBtn.clicked.connect(lambda: self.setSelectionForFindingTypeDetail(""))

        self.setMode = False

    def loadList(self, findingType, findingTypeDetail):
        self.uiFindingTypeEdit.setText(findingType)
        self.uiFindingTypeDetailEdit.setText(findingTypeDetail)
        res = self.loadListForFindingType(findingType.strip())

        if res:
            self.setSelectionForFindingTypeDetail(findingTypeDetail.strip())
            return True
        else:
            return False

    def loadListForFindingType(self, findingType):
        model = QSqlRelationalTableModel(self, self.dbm.db)
        model.setTable(u"befundart")
        model.removeColumn(0)
        model.setFilter(u"befundart = '{0}' AND befundart_detail IS NOT NULL".format(findingType))
        model.select()

        if model.rowCount() < 1:
            QMessageBox.warning(self, "Result", u"Für die Befundart '{0}' wurden keine Detail Einträge gefunden.".format(findingType))
            return False

        self.uiFindingTypeDetailTableV.setModel(model)

        self.uiFindingTypeDetailTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiFindingTypeDetailTableV.verticalHeader().setVisible(False)
        self.uiFindingTypeDetailTableV.hideColumn(0)
        if findingType != "Siedlung":
            self.uiFindingTypeDetailTableV.hideColumn(2)
        #self.uiRemarksTableV.model().insertColumn(0)

        self.uiFindingTypeDetailTableV.resizeRowsToContents()
        self.uiFindingTypeDetailTableV.resizeColumnsToContents()
        self.uiFindingTypeDetailTableV.horizontalHeader().setStretchLastSection(True)

        self.uiFindingTypeDetailTableV.selectionModel().selectionChanged.connect(self.generateFindingTypeDetail)

        return True

    def setSelectionForFindingTypeDetail(self, findingTypeDetail):
        self.setMode = True

        # QMessageBox.warning(None, "not found", u"{0}, '{1}'".format(len(findingTypeDetailList),u",".join(findingTypeDetailList)))
        e = self.uiFindingTypeDetailTableV
        sm = e.selectionModel()
        sm.clearSelection()

        if len(findingTypeDetail) > 0:
            m = self.uiFindingTypeDetailTableV.model()
            rC = m.rowCount()
            selection = QItemSelection()

            notFound = []
            findingTypeDetailList = findingTypeDetail.split(',')
            for detail in findingTypeDetailList:
                found = False
                for r in range(rC):
                    mIdx = m.createIndex(r, m.fieldIndex("befundart_detail"))
                    # QMessageBox.warning(None, "WeatherCode", "{0}={1}".format(m.data(mIdx), weatherCode[i]))
                    if m.data(mIdx).lower() == detail.lower():
                        lIdx = m.createIndex(r, 0)
                        rIdx = m.createIndex(r, m.columnCount() - 1)
                        rowSelection = QItemSelection(lIdx, rIdx)
                        selection.merge(rowSelection, QItemSelectionModel.Select)
                        found = True
                        break
                if not found:
                    notFound.append(detail)
                sm.select(selection, QItemSelectionModel.Select)
            #QMessageBox.warning(None, "not found", u"{0}".format(len(notFound)))
            if len(notFound) > 0:
                QMessageBox.warning(self, u"Befundart Details", u"Die folgenden Einträge wurden nicht gefunden. Bitte wählen Sie von den verfügbaren Einträgen aus oder fügen Sie diese manuell zur Tabelle 'befundart' hinzu. [{0}]".format(u", ".join(notFound)))

        self.setMode = False

    def generateFindingTypeDetail(self):
        e = self.uiFindingTypeDetailTableV
        sm = e.selectionModel()
        details = []
        if sm.hasSelection():
            selIdcs = sm.selectedRows(e.model().fieldIndex("befundart_detail"))
            for i in selIdcs:
                details.append(e.model().data(i))
            details.sort()
            self.uiFindingTypeDetailNewEdit.setText(u",".join(details))
        else:
            self.uiFindingTypeDetailNewEdit.setText("")

    def getFindingTypeDetailText(self):
        return self.uiFindingTypeDetailNewEdit.text()

    def onClose(self):
        SetWindowSize("findingtype_detail", self.size())
