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
from PyQt5.QtWidgets import QDialog, QMessageBox, QAbstractItemView, QHeaderView, QPushButton, QFileDialog, QMenu, QAction
from PyQt5.QtCore import QSettings, Qt, QDateTime, QFile, QDir
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon

from qgis.core import QgsDataSourceUri, QgsProject, QgsVectorLayer, QgsVectorFileWriter, QgsFeature

from APIS.src.apis_site import APISSite
from APIS.src.apis_utils import (SiteHasFindspot, SitesHaveFindspots, GetFindspotNumbers, OpenFileOrFolder,
                                 GetFindspotNumbers, GetWindowSize, GetWindowPos,
                                 SetWindowSizeAndPos, PolygonOrPoint, SelectionOrAll, FileOrFolder)
from APIS.src.apis_printer import APISPrinterQueue, APISListPrinter, APISTemplatePrinter, OutputMode
from APIS.src.apis_printing_options import APISPrintingOptions

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'ui', 'apis_site_selection_list.ui'), resource_suffix='')


class APISSiteSelectionList(QDialog, FORM_CLASS):
    def __init__(self, iface, dbm, imageRegistry, apisLayer, parent=None):
        """Constructor."""
        super(APISSiteSelectionList, self).__init__(parent)

        self.iface = iface
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.apisLayer = apisLayer

        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.setupUi(self)

        # Initial window size/pos last saved. Use default values for first time
        if GetWindowSize("site_selection_list"):
            self.resize(GetWindowSize("site_selection_list"))
        if GetWindowPos("site_selection_list"):
            self.move(GetWindowPos("site_selection_list"))

        self.query = None

        self.accepted.connect(self.onClose)
        self.rejected.connect(self.onClose)

        self.uiSiteListTableV.doubleClicked.connect(self.openSiteDialog)

        self.uiResetSelectionBtn.clicked.connect(self.uiSiteListTableV.clearSelection)

        mLayer = QMenu()
        mLayer.addSection("In QGIS laden")
        aLayerLoadSite = mLayer.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'layer.png')), "Fundort(e)")
        aLayerLoadSite.triggered.connect(self.loadSiteInQgis)
        aLayerLoadInterpretation = mLayer.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'layer.png')), "Interpretation(en)")
        aLayerLoadInterpretation.triggered.connect(self.loadSiteInterpretationInQgis)
        mLayer.addSection("SHP Export")
        aLayerExportSite = mLayer.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'shp_export.png')), "Fundort(e)")
        aLayerExportSite.triggered.connect(self.exportSiteAsShp)
        mLayer.addSection("In QGIS anzeigen")
        aLayerShowSite = mLayer.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'layer.png')), "Zu Fundort(e) zoomen")
        aLayerShowSite.triggered.connect(lambda: self.showSiteInQgis(zoomTo=True, select=False))
        aLayerSelectSite = mLayer.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'layer.png')), "Fundort(e) selektieren")
        aLayerSelectSite.triggered.connect(lambda: self.showSiteInQgis(zoomTo=False, select=True))
        aLayerShowAndSelectSite = mLayer.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'layer.png')), "Zu Fundort(e) zoomen und selektieren")
        aLayerShowAndSelectSite.triggered.connect(lambda: self.showSiteInQgis(zoomTo=True, select=True))
        self.uiLayerTBtn.setMenu(mLayer)
        self.uiLayerTBtn.clicked.connect(self.uiLayerTBtn.showMenu)

        mPdfExport = QMenu()
        aPdfExportSiteList = mPdfExport.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'pdf_export.png')), "Fundortliste")
        aPdfExportSiteList.triggered.connect(lambda: self.exportAsPdf(tab_list=True))
        aPdfExportSite = mPdfExport.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'pdf_export.png')), "Fundort")
        aPdfExportSite.triggered.connect(lambda: self.exportAsPdf(detail=True))
        aPdfExportSiteFindspotList = mPdfExport.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'pdf_export.png')), "Fundort und Funstellenliste")
        aPdfExportSiteFindspotList.triggered.connect(lambda: self.exportAsPdf(detail=True, subList=True))
        aPdfExportSiteFindspotListFindspot = mPdfExport.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'pdf_export.png')), "Fundort, Funstellenliste und Fundstellen")
        aPdfExportSiteFindspotListFindspot.triggered.connect(lambda: self.exportAsPdf(detail=True, subList=True, subDetail=True))
        self.uiPdfExportTBtn.setMenu(mPdfExport)
        self.uiPdfExportTBtn.clicked.connect(self.uiPdfExportTBtn.showMenu)

        self.siteDlg = None
        self.printingOptionsDlg = None

    def hideEvent(self,event):
        self.query = None

    def loadSiteListBySpatialQuery(self, query=None, info=None, update=False):
        if self.query is None:
            self.query = query

        self.model = self.dbm.queryToQStandardItemModel(self.query)

        if self.model is None or self.model.rowCount() < 1:
            if not update:
                QMessageBox.warning(self, "Fundort Auswahl", u"Es wurden keine Fundorte gefunden!")
            self.query = None
            self.done(1)
            return False

        self.setupTable()

        self.uiItemCountLbl.setText(str(self.model.rowCount()))
        if info != None:
            self.uiInfoLbl.setText(info)

        return True

    def setupTable(self):
        self.uiSiteListTableV.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.uiSiteListTableV.setModel(self.model)
        self.uiSiteListTableV.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.uiSiteListTableV.resizeColumnsToContents()
        self.uiSiteListTableV.resizeRowsToContents()
        self.uiSiteListTableV.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.uiSiteListTableV.selectionModel().selectionChanged.connect(self.onSelectionChanged)

    def onSelectionChanged(self):
        self.uiSelectionCountLbl.setText("{0}".format(len(self.uiSiteListTableV.selectionModel().selectedRows())))

    def openSiteDialog(self, idx):
        siteNumber = self.model.item(idx.row(), 0).text()
        if self.siteDlg is None:
            self.siteDlg = APISSite(self.iface, self.dbm, self.imageRegistry, self.apisLayer)
            self.siteDlg.siteEditsSaved.connect(self.reloadTable)
            self.siteDlg.siteDeleted.connect(self.reloadTable)
        self.siteDlg.openInViewMode(siteNumber)
        self.siteDlg.show()
        # Run the dialog event loop

        if self.siteDlg.exec_():
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
        self.siteDlg.removeSitesFromSiteMapCanvas()
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"For Site: {0}".format(siteNumber)))

    def reloadTable(self, editsSaved):
        self.query.exec_()
        #QMessageBox.information(None, "SqlQuery", self.query.executedQuery())
        self.loadSiteListBySpatialQuery(self.query, None, True)
        #QMessageBox.warning(None, self.tr(u"Load Site"), self.tr(u"Reload Table Now"))

    def showSiteInQgis(self, zoomTo=True, select=False):
        layer = self.apisLayer.requestSiteLayer()
        expression = "\"fundortnummer\" IN ({})".format(','.join(["'{}'".format(sN) for sN in self.getSiteList(False)]))
        self.apisLayer.selectFeaturesByExpression(layer, expression)
        if zoomTo:
            self.apisLayer.zoomToSelection(layer)
        if not select:
            layer.removeSelection()

    def loadSiteInQgis(self):
        siteList = self.askForSiteList()
        if siteList:
            #QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}".format(u", ".join(siteList)))
            polygon, point = PolygonOrPoint(parent=self)
            if polygon or point:
                #QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}, {1}".format(polygon, point))
                # get PolygonLayer
                subsetString = '"fundortnummer" IN (' + ','.join(['\'{0}\''.format(siteNumber) for siteNumber in siteList]) + ')'
                siteLayer = self.apisLayer.getSpatialiteLayer('fundort', subsetString)
                if polygon and siteLayer:
                    siteLayerMemory = self.apisLayer.createMemoryLayer(siteLayer, "fundort polygon")
                    siteLayerMemory.loadNamedStyle(self.apisLayer.getStylePath("sites_fp"))
                    # load PolygonLayer
                    self.apisLayer.addLayerToCanvas(siteLayerMemory, "Temp")
                if point and siteLayer:
                    # generate PointLayer
                    centerPointLayer = self.apisLayer.generateCenterPointMemoryLayer(siteLayer, "fundort punkt")
                    centerPointLayer.loadNamedStyle(self.apisLayer.getStylePath("sites_cp"))
                    # load PointLayer
                    self.apisLayer.addLayerToCanvas(centerPointLayer, "Temp")
                self.close()

    def loadSiteInterpretationInQgis(self):
        siteList = self.askForSiteList([2])
        if siteList:
            interpretationsToLoad = []
            noInterpretations = []
            intBaseDir = self.settings.value("APIS/int_base_dir")
            intDir = self.settings.value("APIS/int_dir")
            for siteNumber, kgName in siteList:
                country, siteNumberN = siteNumber.split(".")
                siteNumberN = siteNumberN.zfill(6)
                if country == u"AUT":
                    kgName = u"{0} ".format(kgName.lower().replace(".", "").replace("-", " ").replace("(", "").replace(")", ""))
                else:
                    kgName = ""
                #QMessageBox.information(None, 'info', u"{0}, {1}, {2}, {3}".format(siteNumber, siteNumberN, country, kgName))

                shpFile = u"luftint_{0}.shp".format(siteNumberN)
                intShpPath = os.path.normpath(os.path.join(intBaseDir, country, u"{0}{1}".format(kgName, siteNumberN), intDir, shpFile))
                if os.path.isfile(intShpPath):
                    interpretationsToLoad.append(intShpPath)
                else:
                    noInterpretations.append(siteNumber)

            if len(interpretationsToLoad) > 0:
                stylePath = self.apisLayer.getStylePath("interpretation")
                for intShp in interpretationsToLoad:
                    self.apisLayer.requestShapeFile(intShp, epsg=None, defaultEpsg=4312, layerName=None, groupName="Interpretationen", useLayerFromTree=True, addToCanvas=True, stylePath=stylePath)
                    #QMessageBox.information(None, u"Interpretation", intShp)
            else:
                QMessageBox.warning(self, u"Fundort Interpretation", u"Für die ausgewählten Fundorte ist keine Interpretation vorhanden.")

    def exportSiteAsShp(self):
        siteList = self.askForSiteList()
        if siteList:
            # QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}".format(u", ".join(siteList)))
            polygon, point = PolygonOrPoint(parent=self)
            if polygon or point:
                # QMessageBox.warning(None, self.tr(u"SiteList"), u"{0}, {1}".format(polygon, point))

                # get PolygonLayer
                subsetString = '"fundortnummer" IN (' + ','.join(['\'{0}\''.format(siteNumber) for siteNumber in siteList]) + ')'
                siteLayer = self.apisLayer.getSpatialiteLayer('fundort', subsetString)

                now = QDateTime.currentDateTime()
                time = now.toString("yyyyMMdd_hhmmss")
                if polygon and siteLayer:
                    # export PolygonLayer
                    self.apisLayer.exportLayerAsShp(siteLayer, time, name="Fundort_Polygon", groupName="Temp", styleName="sites_fp", parent=self)
                if point and siteLayer:
                    # generate PointLayer
                    centerPointLayer = self.apisLayer.generateCenterPointMemoryLayer(siteLayer)
                    # export PointLayer
                    self.apisLayer.exportLayerAsShp(centerPointLayer, time, name="Fundort_Punkt", groupName="Temp", styleName="sites_cp", parent=self)

    def exportAsPdf(self, tab_list=False, detail=False, subList=False, subDetail=False):
        if self.printingOptionsDlg is None:
            self.printingOptionsDlg = APISPrintingOptions(self)

        if tab_list and not detail and not subList and not subDetail:
            self.printingOptionsDlg.setWindowTitle("Druck Optionen: Fundortliste")
            filmProject = False
            personalData = False
        elif detail and not tab_list and not subList and not subDetail:
            self.printingOptionsDlg.setWindowTitle("Druck Optionen: Fundort")
            filmProject = True
            personalData = False
        elif detail and subList and not tab_list and not subDetail:
            self.printingOptionsDlg.setWindowTitle("Druck Optionen: Fundort und Funndstellenliste")
            filmProject = True
            personalData = False
        elif detail and subList and subDetail and not tab_list:
            self.printingOptionsDlg.setWindowTitle("Druck Optionen: Fundort, Funndstellenliste und Fundstellen")
            filmProject = True
            personalData = True
        else:
            self.printingOptionsDlg.setWindowTitle("Druck Optionen: Fundort Auswahl")
            filmProject = False
            personalData = False

        if self.uiSiteListTableV.model().rowCount() == 1:
            self.printingOptionsDlg.configure(False, False, visPersonalDataChk=personalData, visFilmProjectChk=filmProject)
        elif not self.uiSiteListTableV.selectionModel().hasSelection():
            self.printingOptionsDlg.configure(False, detail, visPersonalDataChk=personalData, visFilmProjectChk=filmProject)
        else:
            if len(self.uiSiteListTableV.selectionModel().selectedRows()) == 1:
                self.printingOptionsDlg.configure(True, detail, visPersonalDataChk=personalData, visFilmProjectChk=filmProject)
            elif len(self.uiSiteListTableV.selectionModel().selectedRows()) == self.uiSiteListTableV.model().rowCount():
                self.printingOptionsDlg.configure(False, detail, visPersonalDataChk=personalData, visFilmProjectChk=filmProject)
            else:
                self.printingOptionsDlg.configure(True, detail, visPersonalDataChk=personalData, visFilmProjectChk=filmProject)

        self.printingOptionsDlg.show()

        if self.printingOptionsDlg.exec_():
            # get settings from dialog
            printPersonalData = self.printingOptionsDlg.printPersonalData()
            printFilmProject = self.printingOptionsDlg.printFilmProject()
            selectionModeIsAll = self.printingOptionsDlg.selectionModeIsAll()
            outputMode = self.printingOptionsDlg.outputMode()

            siteList = self.getSiteList(selectionModeIsAll)
            if siteList:
                pdfsToPrint = []
                if tab_list:
                    pdfsToPrint.append({'type': APISListPrinter.SITE, 'idList': siteList})
                if detail:
                    for s in siteList:
                        pdfsToPrint.append({'type': APISTemplatePrinter.SITE, 'idList': [s], 'options': {'filmProject': printFilmProject}})
                        if SiteHasFindspot(self.dbm.db, s) and (subList or subDetail):
                            findspotList = GetFindspotNumbers(self.dbm.db, [s])
                            if findspotList:
                                if subList:
                                    pdfsToPrint.append({'type': APISListPrinter.FINDSPOT, 'idList': findspotList})
                                if subDetail:
                                    for f in findspotList:
                                        pdfsToPrint.append({'type': APISTemplatePrinter.FINDSPOT, 'idList': [f], 'options': {'personalData': printPersonalData}})

                if pdfsToPrint:
                    APISPrinterQueue(pdfsToPrint,
                                     outputMode,
                                     openFile=self.printingOptionsDlg.uiOpenFilesChk.isChecked(),
                                     openFolder=self.printingOptionsDlg.uiOpenFolderChk.isChecked(),
                                     dbm=self.dbm,
                                     parent=self)

    def askForSiteList(self, plusCols=None):
        if self.uiSiteListTableV.selectionModel().hasSelection():
            #Abfrage ob Fundorte der selektierten Bilder Exportieren oder alle
            ret = SelectionOrAll(parent=self)

            if ret == 0:
                siteList = self.getSiteList(False, plusCols)
            elif ret == 1:
                siteList = self.getSiteList(True, plusCols)
            else:
                return None
        else:
            siteList = self.getSiteList(True, plusCols)

        return siteList

    def getSiteList(self, getAll, plusCols=None):
        siteList = []
        site = []
        if self.uiSiteListTableV.selectionModel().hasSelection() and not getAll:
            rows = self.uiSiteListTableV.selectionModel().selectedRows()
            for row in rows:
                if plusCols:
                    site = []
                if not self.uiSiteListTableV.isRowHidden(row.row()):
                    if plusCols:
                        site.append(self.model.item(row.row(), 0).text())
                        for col in plusCols:
                            site.append(self.model.item(row.row(), col).text())
                        siteList.append(site)
                    else:
                        siteList.append(self.model.item(row.row(), 0).text())
        else:
            for row in range(self.model.rowCount()):
                if plusCols:
                    site = []
                if not self.uiSiteListTableV.isRowHidden(row):
                    if plusCols:
                        site.append(self.model.item(row, 0).text())
                        for col in plusCols:
                            site.append(self.model.item(row, col).text())
                        siteList.append(site)
                    else:
                        siteList.append(self.model.item(row, 0).text())

        return siteList

    def onClose(self):
        SetWindowSizeAndPos("site_selection_list", self.size(), self.pos())