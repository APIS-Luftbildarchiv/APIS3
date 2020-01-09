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
from osgeo import ogr

from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QTableWidgetItem, QHeaderView, QCheckBox, QMenu, QMessageBox,
                             QPushButton)
from PyQt5.QtCore import QSettings, Qt, QVariant, QDateTime
from PyQt5.QtGui import QIcon
from PyQt5.QtSql import QSqlQuery

from qgis.core import (QgsProject, QgsDataSourceUri, QgsVectorLayer, QgsField, QgsFields, QgsFeature, QgsGeometry,
                       QgsCoordinateReferenceSystem, QgsPoint, QgsMessageLog, Qgis, QgsPointXY, QgsWkbTypes,
                       QgsCoordinateTransform)

from APIS.src.apis_points2path import Points2Path
from APIS.src.apis_utils import (TransformGeometry, SetWindowSizeAndPos, GetWindowSize, GetWindowPos, OpenFileOrFolder,
                                 FileOrFolder)

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'ui', 'apis_flight_path.ui'), resource_suffix='')


class APISFlightPath(QDialog, FORM_CLASS):

    def __init__(self, iface, dbm, apisLayer, parent=None):
        """Constructor."""
        super(APISFlightPath, self).__init__(parent)
        self.iface = iface
        self.dbm = dbm
        self.apisLayer = apisLayer
        self.setupUi(self)

        # Initial window size/pos last saved. Use default values for first time
        if GetWindowSize("flight_path"):
            self.resize(GetWindowSize("flight_path"))
        if GetWindowPos("flight_path"):
            self.move(GetWindowPos("flight_path"))

        self.filmsDict = {}
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.uiLayerTBtn.setEnabled(False)

        self.shpDriver = ogr.GetDriverByName('ESRI Shapefile')

        self.rejected.connect(self.onClose)
        self.accepted.connect(self.onClose)

        mSelect = QMenu()
        mSelect.addSection("Linien")
        aSelectBestAvailableLine = mSelect.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'flightpath.png')), "Beste Verfügbarkeit")
        aSelectBestAvailableLine.triggered.connect(lambda: self.selectBestAvailable([2,4,6]))
        aSelectFlightGpsPoint = mSelect.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'flightpath.png')), "GPS Flug")
        aSelectFlightGpsPoint.triggered.connect(lambda: self.selectColumns([2]))
        aSelectCameraGpsPoint = mSelect.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'flightpath.png')), "GPS Kamera")
        aSelectCameraGpsPoint.triggered.connect(lambda: self.selectColumns([4]))
        aSelectImageMappingPoint = mSelect.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'flightpath.png')), "Bildkartierung")
        aSelectImageMappingPoint.triggered.connect(lambda: self.selectColumns([6]))
        mSelect.addSection("Punkte")
        aSelectBestAvailablePoint = mSelect.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'flightpath.png')), "Beste Verfügbarkeit")
        aSelectBestAvailablePoint.triggered.connect(lambda: self.selectBestAvailable([1,3,5]))
        aSelectFlightGpsPoint = mSelect.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'flightpath.png')), "GPS Flug")
        aSelectFlightGpsPoint.triggered.connect(lambda: self.selectColumns([1]))
        aSelectCameraGpsPoint = mSelect.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'flightpath.png')), "GPS Kamera")
        aSelectCameraGpsPoint.triggered.connect(lambda: self.selectColumns([3]))
        aSelectImageMappingPoint = mSelect.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'flightpath.png')), "Bildkartierung")
        aSelectImageMappingPoint.triggered.connect(lambda: self.selectColumns([5]))
        mSelect.addSeparator()
        aSelectDeselectAll = mSelect.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'flightpath.png')), "Alle auswählen")
        aSelectDeselectAll.triggered.connect(lambda: self.selectAll(True))
        aSelectAll = mSelect.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'flightpath.png')), "Alle zurücksetzen")
        aSelectAll.triggered.connect(lambda: self.selectAll(False))
        self.uiSelectionTBtn.setMenu(mSelect)
        self.uiSelectionTBtn.clicked.connect(self.uiSelectionTBtn.showMenu)

        mLayer = QMenu()
        aLoadLayerInQgis = mLayer.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'layer.png')), "In QGIS laden")
        aLoadLayerInQgis.triggered.connect(self.loadLayerInQgis)
        aExportLayerAsShp = mLayer.addAction(QIcon(os.path.join(QSettings().value("APIS/plugin_dir"), 'ui', 'icons', 'shp_export.png')), "Als SHP Datei exportieren")
        aExportLayerAsShp.triggered.connect(self.exportLayerAsShp)
        self.uiLayerTBtn.setMenu(mLayer)
        self.uiLayerTBtn.clicked.connect(self.uiLayerTBtn.showMenu)

    def showEvent(self, evnt):
        self.selectAll(False)
        self.uiLayerTBtn.setEnabled(False)

    def onClose(self):
        SetWindowSizeAndPos("flight_path", self.size(), self.pos())

    def viewFilms(self, films):

        table = self.uiFlightPathAvailabilityTable
        table.setRowCount(0)
        self.filmsDict = {}
        for film in films:
            self.filmsDict[film] = {}
            flightPathDirectory = self.settings.value("APIS/flightpath_dir") + "\\" + self.yearFromFilm(film)

            chkBoxFlightGpsPoint = QCheckBox("nicht verfügbar")
            chkBoxFlightGpsPoint.setEnabled(False)
            chkBoxFlightGpsPoint.stateChanged.connect(self.checkExportable)
            chkBoxFlightGpsLine = QCheckBox("nicht verfügbar")
            chkBoxFlightGpsLine.setEnabled(False)
            chkBoxFlightGpsLine.stateChanged.connect(self.checkExportable)
            chkBoxCameraGpsPoint = QCheckBox("nicht verfügbar")
            chkBoxCameraGpsPoint.setEnabled(False)
            chkBoxCameraGpsPoint.stateChanged.connect(self.checkExportable)
            chkBoxCameraGpsLine = QCheckBox("nicht verfügbar")
            chkBoxCameraGpsLine.setEnabled(False)
            chkBoxCameraGpsLine.stateChanged.connect(self.checkExportable)
            chkBoxImageMappingPoint = QCheckBox("nicht verfügbar")
            chkBoxImageMappingPoint.setEnabled(False)
            chkBoxImageMappingPoint.stateChanged.connect(self.checkExportable)
            chkBoxImageMappingLine = QCheckBox("nicht verfügbar")
            chkBoxImageMappingLine.setEnabled(False)
            chkBoxImageMappingLine.stateChanged.connect(self.checkExportable)

            if os.path.isdir(flightPathDirectory):

                if os.path.isfile(flightPathDirectory + "\\" + film + ".shp"): #AND MORE THAN ONE FEATURE
                    chkBoxFlightGpsPoint.setText("verfügbar")
                    chkBoxFlightGpsPoint.setEnabled(True)

                if os.path.isfile(flightPathDirectory + "\\" + film + "_lin.shp"):
                    chkBoxFlightGpsLine.setText("verfügbar")
                    chkBoxFlightGpsLine.setEnabled(True)


                shpFile = flightPathDirectory + "\\" + film + "_gps.shp"
                dataSource = self.shpDriver.Open(shpFile, 0)  # 0 means read-only. 1 means writeable.
                if dataSource:
                    ldefn = dataSource.GetLayer().GetLayerDefn()
                    schema = [ldefn.GetFieldDefn(n).name for n in range(ldefn.GetFieldCount())]
                    if "bildnr" in schema:
                        chkBoxCameraGpsPoint.setText("verfügbar")
                        chkBoxCameraGpsPoint.setEnabled(True)
                        if dataSource.GetLayer().GetFeatureCount() > 1:
                            chkBoxCameraGpsLine.setText("verfügbar")
                            chkBoxCameraGpsLine.setEnabled(True)

            # Kartierung
            # Input Filmnummer, weise > je nacch weise andere Tabelle (CenterPoint) für Select (COUNT)
            # Wenn für Film Bilder kartiert sind ja anzeigen
            query = QSqlQuery(self.dbm.db)
            #Also load Attributes to be used while exporting, store in self.filmDict
            qryStr = "select weise, flugdatum, fotograf, pilot, flugzeug, abflug_zeit, ankunft_zeit, flugzeit, abflug_flughafen, ankunft_flughafen, wetter, target from film where filmnummer = '{0}'".format(film)
            query.exec_(qryStr)
            query.first()
            rec = query.record()
            fn = rec.value(0)
            if fn == u"schräg":
                orientation = "schraeg"
            else:
                orientation = "senk"
            self.filmsDict[film]['orientation'] = orientation

            for col in range(1, rec.count()):
                self.filmsDict[film][rec.fieldName(col)] = str(rec.value(col))

            qryStr = "select count(*) from luftbild_{0}_cp where filmnummer = '{1}'".format(orientation, film)
            query.exec_(qryStr)
            query.first()
            fn = query.value(0)
            if fn > 0:
                chkBoxImageMappingPoint.setText("verfügbar")
                chkBoxImageMappingPoint.setEnabled(True)
            if fn > 1:
                chkBoxImageMappingLine.setText("verfügbar")
                chkBoxImageMappingLine.setEnabled(True)

            rowPosition = table.rowCount()
            table.insertRow(rowPosition)
            table.setItem(rowPosition, 0, QTableWidgetItem(film))
            table.setCellWidget(rowPosition, 1, chkBoxFlightGpsPoint)
            table.setCellWidget(rowPosition, 2, chkBoxFlightGpsLine)
            table.setCellWidget(rowPosition, 3, chkBoxCameraGpsPoint)
            table.setCellWidget(rowPosition, 4, chkBoxCameraGpsLine)
            table.setCellWidget(rowPosition, 5, chkBoxImageMappingPoint)
            table.setCellWidget(rowPosition, 6, chkBoxImageMappingLine)

            table.resizeRowsToContents()
            table.resizeColumnsToContents()
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def selectBestAvailable(self, columns):
        self.selectColumns(columns, False)
        table = self.uiFlightPathAvailabilityTable
        for row in range(0, table.rowCount()):
            for column in columns:
                chkBox = table.cellWidget(row, column)
                if chkBox.isEnabled():
                    chkBox.setChecked(True)
                    break

    def selectColumns(self, columns, checked=True):
        table = self.uiFlightPathAvailabilityTable
        for row in range(0, table.rowCount()):
            for column in columns:
                chkBox = table.cellWidget(row, column)
                if chkBox.isEnabled():
                    chkBox.setChecked(checked)

    def selectAll(self, checked):
        table = self.uiFlightPathAvailabilityTable
        for row in range(0, table.rowCount()):
            for column in range(1, table.columnCount()):
                chkBox = table.cellWidget(row, column)
                if chkBox.isEnabled():
                    chkBox.setChecked(checked)

    def checkExportable(self):
        filmsBySourceType = self.getSelection()
        checkCount = 0
        for sourceType in filmsBySourceType:
            if sourceType:
                checkCount += 1

        if checkCount > 0:
            self.uiLayerTBtn.setEnabled(True)
        else:
            self.uiLayerTBtn.setEnabled(False)

    def getSelection(self):
        filmsBySourceType = [[],[],[],[],[],[]]
        table = self.uiFlightPathAvailabilityTable
        for row in range(0, table.rowCount()):
            film = table.item(row, 0).text()
            for column in range(1, table.columnCount()):
                chkBox = table.cellWidget(row, column)
                if chkBox.isEnabled() and chkBox.isChecked():
                    filmsBySourceType[column-1].append(film)
        return filmsBySourceType

    def exportLayerAsShp(self):
        flightPathPointLayer, flightPathLineLayer = self.requestFlightPathLayer()
        now = QDateTime.currentDateTime()
        time = now.toString("yyyyMMdd_hhmmss")
        if flightPathPointLayer.hasFeatures():
            self.apisLayer.exportLayerAsShp(flightPathPointLayer, time, name="Flugwege_Punkt", groupName="Flugwege", styleName="flight_path_pnt", parent=self)
        if flightPathLineLayer.hasFeatures():
            self.apisLayer.exportLayerAsShp(flightPathLineLayer, time, name="Flugwege_Linie", groupName="Flugwege", styleName="flight_path_lin", parent=self)

    def loadLayerInQgis(self):
        flightPathPointLayer, flightPathLineLayer = self.requestFlightPathLayer()
        if flightPathPointLayer.hasFeatures():
            flightPathPointLayer.loadNamedStyle(self.apisLayer.getStylePath("flight_path_pnt"))
            self.apisLayer.addLayerToCanvas(flightPathPointLayer, "Flugwege")
        if flightPathLineLayer.hasFeatures():
            flightPathLineLayer.loadNamedStyle(self.apisLayer.getStylePath("flight_path_lin"))
            self.apisLayer.addLayerToCanvas(flightPathLineLayer, "Flugwege")

    def requestFlightPathLayer(self):
        # https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/vector.html#memory-provider
        filmsBySourceType = self.getSelection()
        epsg = 4326
        vectorCrs = QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId)
        flightPathPointLayer = QgsVectorLayer("MultiPoint?crs=epsg:{0}".format(epsg), "FlugwegePunkt", "memory")
        flightPathLineLayer = QgsVectorLayer("MultiLineString?crs=epsg:{0}".format(epsg), "FlugwegeLinie", "memory")
        flightPathPointLayer.setCrs(vectorCrs)
        flightPathPointLayer.setCrs(vectorCrs)

        flightPathPointProvider = flightPathPointLayer.dataProvider()
        flightPathLineProvider = flightPathLineLayer.dataProvider()

        # add fields
        fields = [QgsField("filmnummer", QVariant.String),
                  QgsField("flugweg_quelle", QVariant.String),
                  QgsField("flugdatum", QVariant.String),
                  QgsField("fotograf", QVariant.String),
                  QgsField("pilot", QVariant.String),
                  QgsField("flugzeug", QVariant.String),
                  QgsField("abflug_zeit", QVariant.String),
                  QgsField("ankunft_zeit", QVariant.String),
                  QgsField("flugzeit", QVariant.String),
                  QgsField("abflug_flughafen", QVariant.String),
                  QgsField("ankunft_flughafen", QVariant.String),
                  QgsField("wetter", QVariant.String),
                  QgsField("target", QVariant.String),
                  QgsField("orientation", QVariant.String)]

        flightPathPointProvider.addAttributes(fields)
        flightPathLineProvider.addAttributes(fields)

        flightPathPointLayer.updateFields()  # tell the vector layer to fetch changes from the provider
        flightPathLineLayer.updateFields()

        pointFeatureList = []
        lineFeatureList = []

        # Point: Flight GPS
        for filmNumber in filmsBySourceType[0]:
            # load .shp file, get geometries as multigeometry
            pointFeatureList.append(self.getFeatureWithMultiGeomFromOgrShp(filmNumber, ".shp", ogr.wkbMultiPoint, "flight_gps", vectorCrs))

        # Point: Camera GPS
        for filmNumber in filmsBySourceType[2]:
            # load _gps.shp file, get geometries as multigeometry
            pointFeatureList.append(self.getFeatureWithMultiGeomFromOgrShp(filmNumber, "_gps.shp", ogr.wkbMultiPoint, "camera_gps", vectorCrs))

        # Point: Image Mapping
        for filmNumber in filmsBySourceType[4]:
            # load image_cp based on orientation from APIS db
            pointFeatureList.append(self.getFeatureWithMultiGeomFromSpatialite(filmNumber, QgsWkbTypes.geometryType(QgsWkbTypes.MultiPoint), "image_mapping"))

        # Line: Flight GPS
        for filmNumber in filmsBySourceType[1]:
            # load _lin.shp file, get geometries as multigeometry
            lineFeatureList.append(self.getFeatureWithMultiGeomFromOgrShp(filmNumber, "_lin.shp", ogr.wkbMultiLineString, "flight_gps", vectorCrs))

        # Line: Camera GPS
        for filmNumber in filmsBySourceType[3]:
            # load _gps.shp file create line with Points2Path, get geometry as multigeometry
            lineFeatureList.append(self.multiPointToLineString(self.getFeatureWithMultiGeomFromOgrShp(filmNumber, "_gps.shp", ogr.wkbMultiPoint, "camera_gps", vectorCrs, sortBy='bildnr')))

        # Line: Image Mapping
        for filmNumber in filmsBySourceType[5]:
            # load image_cp based on orientation from APIS db create line with Points2Path, get geometry as multigeometry
            lineFeatureList.append(self.multiPointToLineString(self.getFeatureWithMultiGeomFromSpatialite(filmNumber, QgsWkbTypes.geometryType(QgsWkbTypes.MultiPoint), "image_mapping")))

        flightPathPointProvider.addFeatures([pF for pF in pointFeatureList if pF is not None])
        flightPathLineProvider.addFeatures([lF for lF in lineFeatureList if lF is not None])

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        flightPathPointLayer.updateExtents()
        flightPathLineLayer.updateExtents()

        return flightPathPointLayer, flightPathLineLayer

    def getFeatureWithMultiGeomFromOgrShp(self, filmNumber, shpExtension, geomType, source, targetCrs, sortBy=None):
        flightPathDirectory = self.settings.value("APIS/flightpath_dir") + "\\" + self.yearFromFilm(filmNumber)
        shpFile = flightPathDirectory + "\\" + filmNumber + shpExtension
        dataSource = self.shpDriver.Open(shpFile, 0)
        if dataSource:
            sourceCrs = QgsCoordinateReferenceSystem()
            spatialRef = dataSource.GetLayer().GetSpatialRef()
            if spatialRef:
                sourceCrs.createFromProj4(dataSource.GetLayer().GetSpatialRef().ExportToProj4())
            else:
                sourceCrs.createFromId(4326, type=QgsCoordinateReferenceSystem.EpsgCrsId)

            # Create QgsMultiPointGeometry; iterate over all Points and add to MultiGeometry
            if sortBy:
                layer = sorted(dataSource.GetLayer(), key=lambda f: f[sortBy])
            else:
                layer = dataSource.GetLayer()

            sourceMultiGeom = ogr.Geometry(geomType)
            for feature in layer:
                sourceMultiGeom.AddGeometry(feature.GetGeometryRef())
            targetMultiGeom = QgsGeometry(QgsGeometry.fromWkt(sourceMultiGeom.ExportToWkt()))
            targetMultiGeom.convertToMultiType()

            feature = QgsFeature()
            feature.setGeometry(TransformGeometry(targetMultiGeom, sourceCrs, targetCrs))
            feature.setAttributes([filmNumber, source] + self.getAttributesForFilm(filmNumber))
            return feature
        else:
            return None

    def getFeatureWithMultiGeomFromSpatialite(self, filmNumber, geomType, source):
        uri = QgsDataSourceUri()
        uri.setDatabase(self.dbm.db.databaseName())
        uri.setDataSource('', 'luftbild_{0}_cp'.format(self.filmsDict[filmNumber]['orientation']), 'geometry')
        sourceLayer = QgsVectorLayer(uri.uri(), 'kartierung {0} p'.format(filmNumber), 'spatialite')
        sourceLayer.setSubsetString(u'"filmnummer" = "{0}"'.format(filmNumber))

        sourceCrs = sourceLayer.crs()
        targetCrs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
        coordinateTransform = QgsCoordinateTransform(sourceCrs, targetCrs, QgsProject.instance())

        if sourceLayer.hasFeatures():
            targetMultiGeom = QgsGeometry()
            sortedFeatures = sorted(sourceLayer.getFeatures(), key=lambda f: f['bildnummer_nn'])
            pointList = []
            for feature in sortedFeatures:
                sourceSingleGeom = feature.geometry()
                sourceSingleGeom.transform(coordinateTransform)
                point = sourceSingleGeom.asPoint()
                pointList.append(point)
                targetMultiGeom.addPointsXY([point], geomType)

            if geomType == QgsWkbTypes.geometryType(QgsWkbTypes.MultiLineString):
                targetMultiGeom = QgsGeometry.fromPolylineXY(pointList)

            feature = QgsFeature()
            feature.setGeometry(targetMultiGeom)
            feature.setAttributes([filmNumber, source] + self.getAttributesForFilm(filmNumber))
            return feature
        else:
            return None

    def multiPointToLineString(self, feature):
        geom = feature.geometry()
        pointList =[]
        for g in geom.asGeometryCollection():
            pointList.append(g.asPoint())

        feature.setGeometry(QgsGeometry.fromPolylineXY(pointList))
        return feature

    def getAttributesForFilm(self, filmNumber):
        attributes = []
        attributes.append(self.filmsDict[filmNumber]['flugdatum'])
        attributes.append(self.filmsDict[filmNumber]['fotograf'])
        attributes.append(self.filmsDict[filmNumber]['pilot'])
        attributes.append(self.filmsDict[filmNumber]['flugzeug'])
        attributes.append(self.filmsDict[filmNumber]['abflug_zeit'])
        attributes.append(self.filmsDict[filmNumber]['ankunft_zeit'])
        attributes.append(self.filmsDict[filmNumber]['flugzeit'])
        attributes.append(self.filmsDict[filmNumber]['abflug_flughafen'])
        attributes.append(self.filmsDict[filmNumber]['ankunft_flughafen'])
        attributes.append(self.filmsDict[filmNumber]['wetter'])
        attributes.append(self.filmsDict[filmNumber]['target'])
        attributes.append(self.filmsDict[filmNumber]['orientation'])
        return attributes

    def yearFromFilm(self, film):
        return film[2:6]



