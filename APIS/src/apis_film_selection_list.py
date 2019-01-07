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
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QHeaderView, QMenu
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QIcon

from APIS.src.apis_printer import APISPrinterQueue, APISTemplatePrinter, APISListPrinter, OutputMode
from APIS.src.apis_printing_options import APISPrintingOptions
from APIS.src.apis_utils import SelectionOrAll

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'ui', 'apis_film_selection_list.ui'), resource_suffix='')


class APISFilmSelectionList(QDialog, FORM_CLASS):
    def __init__(self, iface, model, dbm, imageRegistry, parent=None):
        """Constructor."""
        super(APISFilmSelectionList, self).__init__(parent)

        self.iface = iface
        self.model = model
        self.dbm = dbm
        self.imageRegistry = imageRegistry

        self.setupUi(self)

        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.printingOptionsDlg = None

        self.uiDisplayFlightPathBtn.clicked.connect(lambda: parent.openFlightPathDialog(self.getFilmList(), self))

        self.uiResetSelectionBtn.clicked.connect(self.uiFilmListTableV.clearSelection)

        mPdfExport = QMenu()
        aPdfExportFilmList = mPdfExport.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'pdf_export.png')), "Filmliste")
        aPdfExportFilmList.triggered.connect(lambda: self.exportAsPdf(tab_list=True))
        aPdfExportFilm = mPdfExport.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'pdf_export.png')), "Film")
        aPdfExportFilm.triggered.connect(lambda: self.exportAsPdf(detail=True))
        self.uiPdfExportTBtn.setMenu(mPdfExport)
        self.uiPdfExportTBtn.clicked.connect(self.uiPdfExportTBtn.showMenu)

        #self.accepted.connect(self.onAccepted)

        self.setupTable()

    def setupTable(self):
        self.uiFilmListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiFilmListTableV.setModel(self.model)
        self.uiFilmListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #hide and sort Columns
        self.visibleColumns = ['filmnummer', 'flugdatum', 'anzahl_bilder', 'weise', 'art_ausarbeitung', 'militaernummer', 'militaernummer_alt']
        vCIdx = []
        for vC in self.visibleColumns:
            vCIdx.append(self.model.fieldIndex(vC))

        for c in range(self.model.columnCount()):
            if c not in vCIdx:
                self.uiFilmListTableV.hideColumn(c)

        hH = self.uiFilmListTableV.horizontalHeader()
        for i in range(len(vCIdx)):
            hH.moveSection(hH.visualIndex(vCIdx[i]), i)

        self.uiFilmListTableV.resizeColumnsToContents()
        self.uiFilmListTableV.resizeRowsToContents()
        self.uiFilmListTableV.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # signals
        self.uiFilmListTableV.doubleClicked.connect(self.viewFilm)
        # self.uiFilmListTableV.selectionModel().selectionChanged.connect(self.onSelectionChanged)

        self.uiFilmListTableV.sortByColumn(0, Qt.AscendingOrder)

    def viewFilm(self):
        filmIdx = self.model.createIndex(self.uiFilmListTableV.currentIndex().row(), self.model.fieldIndex("filmnummer"))
        self.filmNumberToLoad = self.model.data(filmIdx)
        self.accept()


    def askForFilmList(self):
        if self.uiFilmListTableV.selectionModel().hasSelection():
            ret = SelectionOrAll()
            if ret == 0:
                filmList = self.getFilmList(False)
            elif ret == 1:
                filmList = self.getFilmList(True)
            else:
                return None
        else:
            filmList = self.getFilmList(True)

        return filmList

    def getFilmList(self, getAll=False):
        filmList = []
        if self.uiFilmListTableV.selectionModel().hasSelection() and not getAll:
            rows = self.uiFilmListTableV.selectionModel().selectedRows()
            for row in rows:
                # get filmnummer
                filmList.append(self.model.data(self.model.createIndex(row.row(), self.model.fieldIndex("filmnummer"))))
        else:
            rc = self.model.rowCount()
            while (self.model.canFetchMore()):
                self.model.fetchMore()
                rc = self.model.rowCount()
            for row in range(rc):
                filmList.append(self.model.data(self.model.createIndex(row, self.model.fieldIndex("filmnummer"))))

        return filmList

    def exportAsPdf(self, tab_list=False, detail=False):
        if self.printingOptionsDlg is None:
            self.printingOptionsDlg = APISPrintingOptions(self)

        if tab_list and not detail:
            self.printingOptionsDlg.setWindowTitle("Druck Optionen: Filmliste")
        elif detail and not tab_list:
            self.printingOptionsDlg.setWindowTitle("Druck Optionen: Film")
        else:
            self.printingOptionsDlg.setWindowTitle("Druck Optionen: Film und Filmliste")

        if self.uiFilmListTableV.model().rowCount() == 1:
            self.printingOptionsDlg.configure(False, False)
        elif not self.uiFilmListTableV.selectionModel().hasSelection():
            self.printingOptionsDlg.configure(False, detail)
        else:
            if len(self.uiFilmListTableV.selectionModel().selectedRows()) == 1:
                self.printingOptionsDlg.configure(True, detail)
            elif len(self.uiFilmListTableV.selectionModel().selectedRows()) == self.uiFilmListTableV.model().rowCount():
                self.printingOptionsDlg.configure(False, detail)
            else:
                self.printingOptionsDlg.configure(True, detail)

        self.printingOptionsDlg.show()

        if self.printingOptionsDlg.exec_():
            # get settings from dialog
            selectionModeIsAll = self.printingOptionsDlg.selectionModeIsAll()
            outputMode = self.printingOptionsDlg.outputMode()

            filmList = self.getFilmList(selectionModeIsAll)

            if filmList:
                pdfsToPrint = []
                if tab_list:
                    pdfsToPrint.append({'type': APISListPrinter.FILM, 'idList': filmList})

                if detail:
                    for f in filmList:
                        pdfsToPrint.append({'type': APISTemplatePrinter.FILM, 'idList': [f]})

                if pdfsToPrint:
                    APISPrinterQueue(pdfsToPrint,
                                     outputMode,
                                     openFile=self.printingOptionsDlg.uiOpenFilesChk.isChecked(),
                                     openFolder=self.printingOptionsDlg.uiOpenFolderChk.isChecked(),
                                     dbm=self.dbm,
                                     imageRegistry=self.imageRegistry,
                                     parent=self)

    def onAccepted(self):
        self.accept()