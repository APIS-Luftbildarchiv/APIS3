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
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QHeaderView
from PyQt5.QtCore import QSettings  # Qt
from PyQt5.QtSql import QSqlQuery

from APIS.src.apis_utils import GetWindowSize, SetWindowSize
from APIS.src.apis_sharding import APISSharding

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'ui', 'apis_sharding_selection_list.ui'), resource_suffix='')


class APISShardingSelectionList(QDialog, FORM_CLASS):
    def __init__(self, iface, dbm, parent=None):
        """Constructor."""
        super(APISShardingSelectionList, self).__init__(parent)
        self.iface = iface
        self.dbm = dbm
        self.setupUi(self)

        # Initial window size/pos last saved. Use default values for first time
        if GetWindowSize("sharding_selection_list"):
            self.resize(GetWindowSize("sharding_selection_list"))

        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.siteNumber = None

        self.uiShardingListTableV.doubleClicked.connect(self.openShardingDialog)
        self.uiNewShardingBtn.clicked.connect(self.addNewSharding)

        self.accepted.connect(self.onClose)
        self.rejected.connect(self.onClose)

    def loadShardingListBySiteNumber(self, siteNumber):
        self.siteNumber = siteNumber
        self.uiSiteNumberLbl.setText(self.siteNumber)
        if self.siteNumber:
            query = QSqlQuery(self.dbm.db)
            query.prepare("SELECT begehung, datum, name, begehtyp, parzelle, funde FROM begehung WHERE fundortnummer = '{0}' ORDER BY date(datum)".format(self.siteNumber))
            query.exec_()

            self.model = self.dbm.queryToQStandardItemModel(query)

            if self.model is None or self.model.rowCount() < 1:
                self.uiShardingCountLbl.setText("0")
                return

            self.setupTable()

            self.uiShardingCountLbl.setText(u"{0}".format(self.model.rowCount()))

    def setupTable(self):
        self.uiShardingListTableV.setModel(self.model)
        self.uiShardingListTableV.setColumnHidden(0, True)
        self.uiShardingListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiShardingListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.uiShardingListTableV.resizeColumnsToContents()
        self.uiShardingListTableV.resizeRowsToContents()

        self.uiShardingListTableV.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def openShardingDialog(self, idx):
        shardingNumber = self.model.item(idx.row(), 0).text()
        shardingDlg = APISSharding(self.iface, self.dbm, parent=self)
        shardingDlg.shardingEditsSaved.connect(self.reloadShardingList)
        shardingDlg.openSharding(self.siteNumber, shardingNumber)
        # Run the dialog event loop
        res = shardingDlg.exec_()
        # if res:
        #     # reload the table after closing
        #     self.loadShardingListBySiteNumber(self.siteNumber)
        # QMessageBox.warning(None, "test", u"{0}".format(res))

    def addNewSharding(self):
        shardingDlg = APISSharding(self.iface, self.dbm, parent=self)
        shardingDlg.shardingEditsSaved.connect(self.reloadShardingList)
        # Run the dialog event loop
        shardingDlg.addNewSharding(self.siteNumber)

        res = shardingDlg.exec_()
        # if res:
        #     # reload the table after closing
        #     self.loadShardingListBySiteNumber(self.siteNumber)
        # QMessageBox.warning(None, "test", u"{0}".format(res))

    def reloadShardingList(self):
        self.loadShardingListBySiteNumber(self.siteNumber)

    def onClose(self):
        SetWindowSize("sharding_selection_list", self.size())
