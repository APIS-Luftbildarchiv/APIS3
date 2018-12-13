# -*- coding: utf-8 -*

from PyQt5.QtWidgets import QMessageBox, QProgressDialog, QFileDialog
from PyQt5.QtCore import (Qt, QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QObject, QDateTime, QDir, QSettings, QFile,
                          QDate, QRectF)
from PyQt5.QtXml import QDomDocument
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtGui import QColor

from qgis.core import (Qgis, QgsMessageLog, QgsLayout, QgsProject, QgsLayoutExporter, QgsLayoutItemPage,
                       QgsReadWriteContext, QgsApplication, QgsVectorLayer, QgsRasterLayer, QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem, QgsLineSymbol, QgsHueSaturationFilter, QgsLayoutItemMap,
                       QgsDataSourceUri, QgsFeature, QgsGeometry, QgsLayoutUtils, QgsLayoutItem, QgsLayoutSize,
                       QgsLayoutPoint, QgsLayoutItemLabel, QgsRectangle)

from APIS.src.apis_utils import GenerateWeatherDescription

import traceback, sys, os, errno, shutil, random, math

from PyPDF2 import PdfFileMerger, PdfFileReader
from osgeo import ogr

class APISPrinterQueue(QObject):
    SINGLE = 0
    MERGE = 1

    def __init__(self, queue, mergeMode=SINGLE, dbm=None, parent=None):

        super(APISPrinterQueue, self).__init__(parent)

        self.printerQueue = queue
        self.mergeMode = mergeMode
        self.dbm = dbm
        self.parent = parent
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.saveTimestamp = None
        self.tempDirName = "temp_apis_print" #ToDo get from config
        self.saveTo = self._requestTargetFileOrDir()
        self.isCanceled = False

        if len(self.printerQueue) <= 1:
            self.mergeMode = self.SINGLE

        if self.saveTo:
            QgsMessageLog().logMessage("SaveTo: {0}".format(self.printerQueue), 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)
            QSettings().setValue("APIS/latest_export_dir", os.path.dirname(os.path.abspath(self.saveTo)))

            # if mergeMode is MERGE and more than one element in queue create a temporary folder in saveTo folder
            if self.mergeMode == self.MERGE and len(self.printerQueue) > 1:
                try:
                    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(self.saveTo)), self.tempDirName))
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise

            self.progress = QProgressDialog(parent=self.parent)
            self.progress.setLabelText("PDF Export ...")
            self.progress.setCancelButtonText("Abbrechen")
            self.progress.setWindowModality(Qt.WindowModal)
            self.progress.setMinimumDuration(1000)
            self.progress.setMinimum(0)
            self.progress.setMaximum(len(self.printerQueue) + self.mergeMode)
            self.progress.setValue(0)
            self.progress.canceled.connect(self._cancelPrinting)

            self._startPrinting()

    def _requestTargetFileOrDir(self):
        self.saveTimestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
        saveDir = QSettings().value("APIS/latest_export_dir", self.settings.value("APIS/working_dir", QDir.home().dirName()))
        if len(self.printerQueue) == 1:
            targetFileName = self._generateFileName(self.printerQueue[0]['type'], self.printerQueue[0]['idList'][0]) + "_{0}".format(self.saveTimestamp)
            self.printerQueue[0]['fileName'] = QFileDialog.getSaveFileName(self.parent, "APIS Pdf Export Datei", os.path.join(saveDir, targetFileName), "*.pdf")[0]
            return self.printerQueue[0]['fileName']
        elif len(self.printerQueue) > 1:
            # all of same type
            if self.mergeMode == self.SINGLE:
                targetDirPath = QFileDialog.getExistingDirectory(self.parent, "APIS Pdf Export Ordner", saveDir, QFileDialog.ShowDirsOnly)
                #iterate over Queue and generate FileNames
                for i in self.printerQueue:
                    i['fileName'] = os.path.join(targetDirPath, self._generateFileName(i['type'], i['idList'][0]) + "_{0}".format(self.saveTimestamp) + ".pdf")
                return targetDirPath
            elif self.mergeMode == self.MERGE:
                types = [i['type'] for i in self.printerQueue]
                output = []
                # generate collection filename
                for i in self.printerQueue:
                    if types.count(i['type']) == 1:
                        output.append(self._generateFileName(i['type'], i['idList'][0]))
                    elif types.count(i['type']) > 1:
                        o = self._generateFileName(i['type'], "Sammlung")
                        if o not in output:
                            output.append(o)
                targetFileName = "_".join(output) + "_{0}".format(self.saveTimestamp)
                targetFilePath = QFileDialog.getSaveFileName(self.parent, "APIS Pdf Export Datei", os.path.join(saveDir, targetFileName), "*.pdf")[0]
                targetDirPath = os.path.join(os.path.dirname(os.path.abspath(targetFilePath)), self.tempDirName)
                #iterate over Queue and generate temp FileNames
                for i in self.printerQueue:
                    i['fileName'] = os.path.join(targetDirPath, self._generateFileName(i['type'], i['idList'][0]) + "_{0}".format(self.saveTimestamp) + ".pdf")
                return targetFilePath
        else:
            return None

    def _generateFileName(self, type, id=None):
        id = id.replace('.', '_')
        if type == APISListPrinter.FILM:
            return APISFilmListPrinter.FILENAMETEMPLATE

        elif type == APISListPrinter.IMAGE:
            return APISImageListPrinter.FILENAMETEMPLATE

        elif type == APISListPrinter.SITE:
            return APISSiteListPrinter.FILENAMETEMPLATE

        elif type == APISListPrinter.FINDSPOT:
            return APISFindspotListPrinter.FILENAMETEMPLATE

        elif type == APISTemplatePrinter.FILM:
            return APISFilmTemplatePrinter.FILENAMETEMPLATE.format(id)

        elif type == APISTemplatePrinter.SITE:
            return APISSiteTemplatePrinter.FILENAMETEMPLATE.format(id)

        elif type == APISTemplatePrinter.FINDSPOT:
            return APISFindspotTemplatePrinter.FILENAMETEMPLATE.format(id)

        else:
            return None

    def _startPrinting(self):
        self.progress.forceShow()
        try:
            for printable in self.printerQueue:
                if self.isCanceled:
                    raise Exception('APISPrinterQueue', 'PrintingCanceled')
                self.progress.setLabelText("PDF Export: {0}".format(printable['fileName']))
                if printable['type'] == APISListPrinter.FILM:
                    # Prepare Printer
                    printable['printer'] = APISFilmListPrinter(printable['fileName'], printable['idList'])
                elif printable['type'] == APISListPrinter.IMAGE:
                    # Prepare Printer
                    printable['printer'] = APISImageListPrinter(printable['fileName'], printable['idList'])
                elif printable['type'] == APISListPrinter.SITE:
                    #Prepare Printer
                    printable['printer'] = APISSiteListPrinter(printable['fileName'], printable['idList'])
                elif printable['type'] == APISListPrinter.FINDSPOT:
                    # Prepare Printer
                    printable['printer'] = APISFindspotListPrinter(printable['fileName'], printable['idList'])
                elif printable['type'] == APISTemplatePrinter.FILM:
                    # Prepare Printer
                    printable['printer'] = APISFilmTemplatePrinter(printable['fileName'], printable['idList'][0], self.dbm)
                elif printable['type'] == APISTemplatePrinter.SITE:
                    # Prepare Printer
                    printable['printer'] = APISSiteTemplatePrinter(printable['fileName'], printable['idList'][0], self.dbm)
                elif printable['type'] == APISTemplatePrinter.FINDSPOT:
                    # Prepare Printer
                    printable['printer'] = APISFindspotTemplatePrinter(printable['fileName'], printable['idList'][0])
                else:
                    raise Exception('APISPrinterQueue', 'Specified printer type not recognized.')

                # Use Printer in Worker
                # printable['worker'] = Worker(self.execute_printer, printer=printable['printer'])  # Any other args, kwargs are passed to the run function
                # printable['worker'].signals.result.connect(self.print_output)
                # printable['worker'].signals.finished.connect(self.thread_complete)
                # Execute
                # self.threadPool.start(printable['worker'])

                printable['printed'] = printable['printer'].printPdf()
                self._updateProgress()

            if self.mergeMode == self.MERGE and len(self.printerQueue) > 1:
                merger = PdfFileMerger()
                for printable in self.printerQueue:
                    if printable['printed']:
                        merger.append(PdfFileReader(printable['fileName']), 'rb')

                with open(self.saveTo, 'wb') as fout:
                    merger.write(fout)
                    self._updateProgress()
                    shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(self.saveTo)), self.tempDirName))

        except Exception as inst:
            #tag, message = inst.args
            QgsMessageLog().logMessage("{0}".format(inst.args), 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)
            if inst.args[1] == 'PrintingCanceled':
                self._printingInterrupted()

    # def execute_printer(self, printer):
    #    res = printer.printPdf()
    #    return res

    # def print_output(self, res):
    #    # print(s)
    #    QgsMessageLog().logMessage("{0}".format(res[0]), 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)
    #    if res[1].pageCollection().pageCount() > 0:
    #        layoutExporter = QgsLayoutExporter(res[1])
    #        layoutExporter.exportToPdf(self.printerQueue[res[0]]['fileName'], QgsLayoutExporter.PdfExportSettings())

    # def thread_complete(self):
        # print("THREAD COMPLETE!")
    #    self.progress.setValue(self.progress.value() + 1)
    #    QgsMessageLog().logMessage("THREAD COMPLETE! {0}".format(self.threadPool.activeThreadCount()), 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)

    #def report_error(self, e):
    #    QgsMessageLog().logMessage("{0}".format(e), 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)

    def _updateProgress(self):
        self.progress.setValue(self.progress.value() + 1)

    def _cancelPrinting(self):
        self.isCanceled = True
        QgsMessageLog().logMessage("Printing was Canceled!", 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)

    def _printingInterrupted(self):

        cancelProgress = QProgressDialog(parent=self.parent)
        cancelProgress.setLabelText("PDF Export abbrechen ...")
        cancelProgress.setWindowModality(Qt.WindowModal)
        cancelProgress.setRange(0, 0)
        cancelProgress.setValue(0)
        cancelProgress.setCancelButton(None)
        cancelProgress.setWindowFlags(cancelProgress.windowFlags() | Qt.CustomizeWindowHint)
        cancelProgress.setWindowFlags(cancelProgress.windowFlags() & ~Qt.WindowCloseButtonHint)
        cancelProgress.forceShow()

        for printable in self.printerQueue:
            QgsApplication.instance().processEvents()
            if "printed" in printable and printable["printed"]:
                if os.path.exists(printable['fileName']):
                    os.remove(printable['fileName'])
            if os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(self.saveTo)), self.tempDirName)):
                shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(self.saveTo)), self.tempDirName))

        cancelProgress.cancel()


class APISTemplatePrinter:
    FILM = 1
    SITE = 2
    FINDSPOT = 3

    def __init__(self, fileName, id, template):
        self.fileName = fileName
        self.id = id
        self.template = template
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.layout = None

    def escape(self, s):
        for a, b in zip(['"', '\'', '&', '<', '>'], ['&quot;', '&apos;', '&amp;', '&lt;', '&gt;']):
            s = s.replace(a, b)
        return s

    def escape(self, s):
        s = s.replace("&", "&amp;")
        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        s = s.replace("\"", "&quot;")
        s = s.replace("'", "&apos;")
        return s

    def applySubstituteDict(self, templateStr, d):
        for key, value in d.items():
            templateStr = templateStr.replace("[{0}]".format(key), self.escape(value))
            #.replace("'", '&apos;').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
        return templateStr

    def loadTemplate(self, f, d):
        t = QDomDocument()
        t.setContent(QFile(f), False)
        t.setContent(self.applySubstituteDict(t.toString(), d))
        return t

    def printPdf(self):
        # Prepare Substitute Dict
        self.substituteDict = self.prepareSubstituteDict()

        # Load Template and Apply Substitute Dict
        templateDom = self.loadTemplate(self.template, self.substituteDict)

        # Create Layout and Load from Template
        self.layout = QgsLayout(QgsProject.instance())
        self.layout.loadFromTemplate(templateDom, QgsReadWriteContext())

        # Handle Maps: if Map exists generate LayerSet
        layerSet = []
        apisMap = self.layout.itemById('apis_map')
        if isinstance(apisMap, QgsLayoutItemMap):
            apisMap.setKeepLayerSet(False)
            vectorLayer = self.requestVectorLayer() #goes into Specialist printer #vectorCrs = QgsCoordinateReferenceSystem(4312, QgsCoordinateReferenceSystem.EpsgCrsId)
            if vectorLayer and vectorLayer.hasFeatures():
                rasterCrs = QgsCoordinateReferenceSystem(3857, QgsCoordinateReferenceSystem.EpsgCrsId)
                t = QgsCoordinateTransform(vectorLayer.crs(), rasterCrs, QgsProject.instance())
                extent = t.transform(vectorLayer.extent())
                extent = self.requestExtent(extent)
                if extent.height() > 0 and extent.width() > 0: #if all points were on the same location
                    layerSet.append(vectorLayer)

                    if self.requestBackgroundMap() == "oek50":
                        layerSet.extend(self.requestOekLayerSet())
                    else:
                        layerSet.append(self.requestWmsLayer(extent, apisMap.sizeWithUnits(), xyz=self.requestBackgroundMap()))
                    #

                    apisMap.setCrs(rasterCrs)
                    apisMap.zoomToExtent(extent)

                    QgsProject.instance().addMapLayers(layerSet, False)
                    apisMap.setLayers(layerSet)
                else:
                    self.layout.removeLayoutItem(apisMap)
            else:
                self.layout.removeLayoutItem(apisMap)

        # Handle Images

        # path = self.settings.value("APIS/repr_image_dir", QDir.home().dirName())
        # repImageName = self.getRepresentativeImage(siteDict['fundortnummer'])
        # if repImageName:
        #     path += u"\\" + repImageName + u".jpg"
        #
        #     repImageFile = QFile(path)
        #     if repImageFile.exists():
        #         itemImg.setPicturePath(path)
        #     else:
        #         # remove itemImg (to avoid red cross)
        #         composition.removeComposerItem(itemImg)
        # else:
        #     # remove itemImg (to avoid red cross)
        #     composition.removeComposerItem(itemImg)


        # Handle Adjustments (overflow)
        self.adjustItems()

        # Handle New Pages (e.g. All Rep. Images)

        # Export
        if self.layout.pageCollection().pageCount() > 0:
            layoutExporter = QgsLayoutExporter(self.layout)
            layoutExporter.exportToPdf(self.fileName, QgsLayoutExporter.PdfExportSettings())
            wasPrinted = True
        else:
            wasPrinted = False

        #QgsMessageLog().logMessage("Number of Items: {0}".format(len(layout.pageCollection().itemsOnPage(0))), 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)


        # Remove MapLayers
        if layerSet:
            QgsProject.instance().removeMapLayers([l.id() for l in layerSet])

        return wasPrinted

    def requestWmsLayer(self, extent, size, xyz='basemap', addToProject=False, addToCanvas=False):
        # basemap = "crs=EPSG:3857&dpiMode=7&format=image/png&layers=geolandbasemap&styles=normal&tileMatrixSet=google3857&zmax=7&zmin=0&url=https://www.basemap.at/wmts/1.0.0/WMTSCapabilities.xml"
        # basemap_grau = "crs=EPSG:3857&dpiMode=10&format=image/png&layers=bmapgrau&styles=normal&tileMatrixSet=google3857&url=https://www.basemap.at/wmts/1.0.0/WMTSCapabilities.xml"

        import math
        c = 40075016.6855785
        z = math.floor(min(math.log(c / (extent.width() / size.width()), 2) - 8, math.log(c / (extent.height() / size.height()), 2) - 8)) + 2

        if xyz == 'basemap':
            wmsString = "type=xyz&url=http://maps.wien.gv.at/basemap/bmaphidpi/normal/google3857/%7Bz%7D/%7By%7D/%7Bx%7D.jpeg&zmax={0}&zmin=0".format(int(z))
        else:
            # OSM
            wmsString = "type=xyz&url=http://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax={0}&zmin=0".format(int(z))

        rasterLayer = QgsRasterLayer(wmsString, "BackgroundMap", 'wms')
        # define the filter, assign filter to raster pipe, apply changes
        saturationFilter = QgsHueSaturationFilter()
        saturationFilter.setSaturation(-30)
        rasterLayer.pipe().set(saturationFilter)
        rasterLayer.triggerRepaint()

        if rasterLayer.isValid() and addToProject:
            QgsProject.instance().addMapLayers(rasterLayer, addToCanvas)

        return rasterLayer

    def requestOekLayerSet(self, m28=True, m31=True, m34=True, addToProject=False, addToCanvas=False):
        # ÖK Background
        oekLayerSet = []
        if m28:
            oekLayer28 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m28"), u"OKM28")
            oekLayer28.setCrs(QgsCoordinateReferenceSystem(31254, QgsCoordinateReferenceSystem.EpsgCrsId))
            oekLayerSet.append(oekLayer28)

        if m31:
            oekLayer31 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m31"), u"OKM31")
            oekLayer31.setCrs(QgsCoordinateReferenceSystem(31255, QgsCoordinateReferenceSystem.EpsgCrsId))
            oekLayerSet.append(oekLayer31)

        if m34:
            oekLayer34 = QgsRasterLayer(self.settings.value("APIS/oek50_gk_qgis_m34"), u"OKM34")
            oekLayer34.setCrs(QgsCoordinateReferenceSystem(31256, QgsCoordinateReferenceSystem.EpsgCrsId))
            oekLayerSet.append(oekLayer34)

        if oekLayerSet and addToProject:
            QgsProject.instance().addMapLayers(oekLayerSet, addToCanvas)

        return oekLayerSet


class APISFilmTemplatePrinter(APISTemplatePrinter):
    FILENAMETEMPLATE = "Film_{0}"

    def __init__(self, fileName, id, dbm):
        self.dbm = dbm
        template = os.path.join(*[QSettings().value("APIS/plugin_dir"), "templates", "layout", "film.qpt"])
        APISTemplatePrinter.__init__(self, fileName, id, template)

    def prepareSubstituteDict(self):
        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT * FROM film WHERE filmnummer = '{0}'".format(self.id))
        query.exec_()

        substituteDict = {}
        query.seek(-1)
        while query.next():
            rec = query.record()
            for col in range(rec.count()):
                val = str(rec.value(col))
                if val.replace(" ", "") == '' or val == 'NULL':
                    val = "---"

                substituteDict[str(rec.fieldName(col))] = val

            substituteDict['projekt'] = substituteDict['projekt'].strip(";").replace(";", "\n")
            substituteDict['wetter_description'] = GenerateWeatherDescription(self.dbm.db, substituteDict['wetter'])
            substituteDict['datum_druck'] = QDate.currentDate().toString("yyyy-MM-dd")

        return substituteDict

    def requestBackgroundMap(self):
        return self.settings.value("APIS/film_print_map", "basemap")

    def requestVectorLayer(self):
        # request best available flightpath and return vector Layer

        # Vector Layer
        vectorLayer = QgsVectorLayer("LineString?crs=epsg:{0}&field=id:integer&index=yes".format(4326), "FlightPath", "memory")
        vectorLayer.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
        vectorLayer.renderer().setSymbol(QgsLineSymbol.createSimple({'color': '220,30,40', 'line_width': '0.4'}))

        flightpathDir = self.settings.value("APIS/flightpath_dir")
        shpDriver = ogr.GetDriverByName('ESRI Shapefile')

        # choice 1 = _lin.shp
        shpFile = flightpathDir + "\\" + self.id[2:6] + "\\" + self.id + "_lin.shp"
        dataSource = shpDriver.Open(shpFile, 0)
        if not vectorLayer.hasFeatures() and dataSource and dataSource.GetLayer().GetFeatureCount() > 0:
            features = []
            for sourceFeature in dataSource.GetLayer():
                feature = QgsFeature()
                feature.setGeometry(QgsGeometry.fromWkt(sourceFeature.GetGeometryRef().ExportToWkt()))
                features.append(feature)

            vectorLayer.dataProvider().addFeatures(features)
            vectorLayer.updateExtents()

        # choice 2 = _gps.shp + connect points if featureCount > 1
        shpFile = flightpathDir + "\\" + self.id[2:6] + "\\" + self.id + "_gps.shp"
        dataSource = shpDriver.Open(shpFile, 0)
        if not vectorLayer.hasFeatures() and dataSource and dataSource.GetLayer().GetFeatureCount() > 1:

            sortedFeatures = sorted(dataSource.GetLayer(), key=lambda f: f['bildnr'])
            pointList = []
            for feature in sortedFeatures:
                pointList.append(QgsGeometry.fromWkt(feature.GetGeometryRef().ExportToWkt()).asPoint())

            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPolylineXY(pointList))
            vectorLayer.dataProvider().addFeature(feature)
            vectorLayer.updateExtents()

        # choice 3 = from image mapping + connect points if featureCount > 1
        if not vectorLayer.hasFeatures():
            query = QSqlQuery(self.dbm.db)
            # Also load Attributes to be used while exporting, store in self.filmDict
            qryStr = "SELECT weise FROM film WHERE filmnummer = '{0}'".format(self.id)
            query.exec_(qryStr)
            query.first()
            rec = query.record()
            fn = rec.value(0)
            if fn == u"schräg":
                orientation = "schraeg"
            else:
                orientation = "senk"

            uri = QgsDataSourceUri()
            uri.setDatabase(self.dbm.db.databaseName())
            uri.setDataSource('', 'luftbild_{0}_cp'.format(orientation), 'geometry')
            sourceLayer = QgsVectorLayer(uri.uri(), 'kartierung {0} p'.format(self.id), 'spatialite')
            sourceLayer.setSubsetString(u'"filmnummer" = "{0}"'.format(self.id))
            coordinateTransform = QgsCoordinateTransform(sourceLayer.crs(), vectorLayer.crs(), QgsProject.instance())

            if sourceLayer.featureCount() > 1:
                sortedFeatures = sorted(sourceLayer.getFeatures(), key=lambda f: f['bildnummer_nn'])
                pointList = []
                for feature in sortedFeatures:
                    geom = feature.geometry()
                    geom.transform(coordinateTransform)
                    pointList.append(geom.asPoint())

                feature = QgsFeature()
                feature.setGeometry(QgsGeometry.fromPolylineXY(pointList))
                vectorLayer.dataProvider().addFeature(feature)
                vectorLayer.updateExtents()

        return vectorLayer

    def requestExtent(self, extent):
        extent.scale(1.1)
        return extent

    def adjustItems(self):
        return


class APISSiteTemplatePrinter(APISTemplatePrinter):
    FILENAMETEMPLATE = "Fundort_{0}"

    def __init__(self, fileName, id, dbm):
        self.dbm = dbm
        template = os.path.join(*[QSettings().value("APIS/plugin_dir"), "templates", "layout", "site.qpt"])
        APISTemplatePrinter.__init__(self, fileName, id, template)

    def prepareSubstituteDict(self):
        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT * FROM fundort WHERE fundortnummer = '{0}'".format(self.id))
        query.exec_()

        substituteDict = {}
        query.seek(-1)
        while query.next():
            rec = query.record()
            for col in range(rec.count()):
                val = "{0}".format(rec.value(col)) #str(rec.value(col))
                if val.replace(" ", "") == '' or val == 'NULL':
                    val = "---"

                substituteDict[str(rec.fieldName(col))] = val

            substituteDict['datum_druck'] = QDate.currentDate().toString("dd.MM.yyyy")
            substituteDict['datum_ersteintrag'] = QDate.fromString(substituteDict['datum_ersteintrag'], "yyyy-MM-dd").toString("dd.MM.yyyy")
            substituteDict['datum_aenderung'] = QDate.fromString(substituteDict['datum_aenderung'], "yyyy-MM-dd").toString("dd.MM.yyyy")

            if substituteDict['sicherheit'] == "1":
                substituteDict['sicherheit'] = "sicher"
            elif substituteDict['sicherheit'] == "2":
                substituteDict['sicherheit'] = "wahrscheinlich"
            elif substituteDict['sicherheit'] == "3":
                substituteDict['sicherheit'] = "fraglich"
            elif substituteDict['sicherheit'] == "4":
                substituteDict['sicherheit'] = "kein Fundort"

            if substituteDict['meridian'] == "28":
                substituteDict['epsg_gk'] = "31254"
            elif substituteDict['meridian'] == "31":
                substituteDict['epsg_gk'] = "31255"
            elif substituteDict['meridian'] == "34":
                substituteDict['epsg_gk'] = "31256"
            else:
                substituteDict['epsg_gk'] = "---"

            substituteDict['epsg_mgi'] = "4312"

            query2 = QSqlQuery(self.dbm.db)
            query2.prepare(u"SELECT kg.katastralgemeindenummer AS kgcode, kg.katastralgemeindename AS kgname, round(100*Area(Intersection(Transform(fo.geometry, 31287), kg.geometry))/Area(Transform(fo.geometry, 31287))) AS percent FROM katastralgemeinden kg, fundort fo WHERE fundortnummer = '{0}' AND intersects(Transform(fo.geometry, 31287), kg.geometry) AND kg.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'katastralgemeinden' AND search_frame = Transform(fo.geometry, 31287)) ORDER  BY percent DESC".format(substituteDict['fundortnummer']))
            query2.exec_()
            query2.seek(-1)
            substituteDict['kgs_lage'] = ""
            while query2.next():
                rec2 = query2.record()
                substituteDict['kgs_lage'] += u"{0} {1} ({2} %)\n".format(rec2.value(0), rec2.value(1), rec2.value(2))

        return substituteDict

    def requestBackgroundMap(self):
        return self.settings.value("APIS/site_print_map", "oek50")

    def requestVectorLayer(self):
        # Site Layer
        stylesDir = QSettings().value("APIS/plugin_dir") + "\\layer_tree\\styles\\"
        uri = QgsDataSourceUri()
        uri.setDatabase(self.dbm.db.databaseName())
        uri.setDataSource('', 'fundort', 'geometry')
        vectorLayer = QgsVectorLayer(uri.uri(), 'fundort', 'spatialite')
        vectorLayer.setSubsetString('"fundortnummer" = "{0}"'.format(self.substituteDict['fundortnummer']))
        vectorLayer.setCrs(QgsCoordinateReferenceSystem(4312, QgsCoordinateReferenceSystem.EpsgCrsId))
        vectorLayer.loadNamedStyle(os.path.join(stylesDir, u"fundort_print.qml"))

        return vectorLayer

    def requestExtent(self, extent):
        scaleVal = max(extent.width(), extent.height())
        baseVal = max(float(self.settings.value("APIS/site_print_map_min_size", 1600.0)), scaleVal * 1.1)
        extent.scale(baseVal / scaleVal)


        return extent

    def getRepresentativeImage(self, siteNumber):
        query = QSqlQuery(self.dbm.db)
        query.prepare(u"SELECT CASE WHEN repraesentatives_luftbild IS NULL THEN 0 WHEN repraesentatives_luftbild ='_1' THEN 0 ELSE repraesentatives_luftbild END as repImage FROM fundort WHERE fundortnummer = '{0}'".format(siteNumber))
        res = query.exec_()
        query.first()
        if query.value(0) == 0:
            return False
        else:
            return str(query.value(0))

    def adjustItems(self):
        adjustItemHightTxt = ["parzelle", "flur", "hoehe", "flaeche", "kommentar_lage", "kgs_lage", "befund",
                              "literatur", "detailinterpretation"]

        for itemId in adjustItemHightTxt:
            itemTxt = self.layout.itemById('{0}Txt'.format(itemId))
            if itemTxt:
                fontHeight = QgsLayoutUtils.fontHeightMM(itemTxt.font())
                # oldHeight = itemTxt.rectWithFrame().height()
                displayText = str(itemTxt.text())
                w = itemTxt.rectWithFrame().width()
                boxWidth = w - 2 * itemTxt.marginX()
                lineCount = 0
                oldLineCount = 0
                spaceWidth = QgsLayoutUtils.textWidthMM(itemTxt.font(), " ")
                newText = u""
                for line in displayText.splitlines():
                    lineWidth = max(1.0, QgsLayoutUtils.textWidthMM(itemTxt.font(), line))
                    oldLineCount += math.ceil(lineWidth / boxWidth)
                    if lineWidth > boxWidth:
                        lineCount += 1
                        if lineCount > 1:
                            newText += u"\n"
                        accWordWidth = 0
                        wordNum = 0
                        for word in line.split():
                            wordNum += 1
                            wordWidth = QgsLayoutUtils.textWidthMM(itemTxt.font(), word)
                            accWordWidth += wordWidth
                            if accWordWidth > boxWidth:
                                if wordNum > 1:
                                    lineCount += 1
                                if wordWidth > boxWidth:
                                    accCharWidth = 0
                                    newWord = u""
                                    for char in word:
                                        charWidth = QgsLayoutUtils.textWidthMM(itemTxt.font(), char)
                                        accCharWidth += charWidth
                                        newWord += char
                                        if accCharWidth >= boxWidth - 5:
                                            # INSERT LINE BREAK
                                            lineCount += 1
                                            accCharWidth = 0
                                            newText += newWord
                                            newWord = u"\n"
                                    newText += newWord + u" "
                                    accWordWidth = accCharWidth + spaceWidth

                                else:
                                    if wordNum > 1:
                                        newText += u"\n" + word + u" "

                                    accWordWidth = wordWidth + spaceWidth

                            else:
                                accWordWidth += spaceWidth
                                newText += word + u" "


                    else:
                        lineCount += 1  # math.ceil(textWidth / boxWidth)
                        if lineCount > 1:
                            newText += u"\n"
                        newText += line

                itemTxt.setText(newText)

                newHeight = fontHeight * (lineCount + 0.5)
                newHeight += 2 * itemTxt.marginY() + 2

                # x = itemTxt.pos().x()
                # y = itemTxt.pos().y()
                # itemTxt.setItemPosition(x, y, w, newHeight, QgsLayoutItem.UpperLeft, True, 1)
                itemTxt.attemptResize(QgsLayoutSize(w, newHeight))

        adjustItems = ["parzelle", "flur", "hoehe", "flaeche", "kommentar_lage", "kgs_lage", "media", "befund",
                       "literatur", "detailinterpretation"]

        bottomBorder = 30.0
        topBorder = 27.0
        i = 0
        newY = 0.0
        currentPage = 0
        for itemId in adjustItems:
            itemTxt = self.layout.itemById(itemId + "Txt")
            itemLbl = self.layout.itemById(itemId + "Lbl")

            if itemId == "media":
                itemMap = self.layout.itemById("apis_map")
                itemImg = self.layout.itemById("rep_luftbild")

                y = newY + 5.0
                # self.layout.pageCollection().extendByNewPage()
                if itemMap:
                    itemMap.attemptMove(QgsLayoutPoint(itemMap.pos().x(), y), useReferencePoint=False, page=currentPage)
                    # TODO test if required: itemMap.zoomToExtent(extent)
                if itemImg:
                    itemImg.attemptMove(QgsLayoutPoint(itemImg.pos().x(), y), useReferencePoint=False, page=currentPage)

                newY = itemImg.pos().y() + itemImg.rectWithFrame().height() + 5.0

            if itemTxt and itemLbl:

                #x = itemTxt.pos().x()
                if i == 0:
                    y = itemTxt.pos().y()
                else:
                    y = newY
                #w = itemTxt.rectWithFrame().width()
                h = max(itemTxt.rectWithFrame().height(), itemLbl.rectWithFrame().height())
                newY = y + h
                if newY > 297 - bottomBorder:
                    #NEW PAGE
                    self.layout.pageCollection().extendByNewPage()
                    currentPage += 1
                    y = topBorder
                    newY = y + h

                    # copy Header
                    header = 1
                    while self.layout.itemById("header_{0}".format(header)):
                        self.cloneLabel(self.layout, self.layout.itemById("header_{0}".format(header)), currentPage)
                        header += 1

                    # copyFooter
                    footer = 1
                    while self.layout.itemById("footer_{0}".format(footer)):
                        self.cloneLabel(self.layout, self.layout.itemById("footer_{0}".format(footer)), currentPage)
                        footer += 1

                itemTxt.attemptMove(QgsLayoutPoint(itemTxt.pos().x(), y), useReferencePoint=False, page=currentPage)
                itemLbl.attemptMove(QgsLayoutPoint(itemLbl.pos().x(), y), useReferencePoint=False, page=currentPage)

                i += 1

    def cloneLabel(self, layout, l, currentPage):
        label = QgsLayoutItemLabel(layout)
        label.attemptSetSceneRect(QRectF(l.pos().x(), l.pos().y(), l.rectWithFrame().width(), l.rectWithFrame().height()))
        label.attemptMove(QgsLayoutPoint(label.positionAtReferencePoint(QgsLayoutItem.UpperLeft)), useReferencePoint=False, page=currentPage)
        label.setBackgroundEnabled(True)
        label.setBackgroundColor(QColor("#CCCCCC"))
        label.setText(l.text())
        label.setVAlign(l.vAlign())
        label.setHAlign(l.hAlign())
        label.setMarginX(l.marginX())
        label.setMarginY(l.marginY())
        label.setFont(l.font())
        layout.addItem(label)


class APISFindspotTemplatePrinter(APISTemplatePrinter):
    FILENAMETEMPLATE = "Fundstelle_{0}"

    def __init__(self, fileName, id):
        template = os.path.join(*[QSettings().value("APIS/plugin_dir"), "templates", "layout", "test_template.qpt"])
        APISTemplatePrinter.__init__(self, fileName, id, template)


class APISListPrinter:
    FILM = 4
    IMAGE = 5
    SITE = 6
    FINDSPOT = 7

    def __init__(self, fileName, idList):
        self.idList = idList
        self.fileName = fileName
        self.info = None
        self.query = None

    def printPdf(self):
        QgsMessageLog().logMessage("ListPrinter: {0}".format(self.FILENAMETEMPLATE), 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)
        layout = QgsLayout(QgsProject.instance())
        layoutPageCollection = layout.pageCollection()
        page = QgsLayoutItemPage(layout)
        layoutPageCollection.addPage(page)
        layoutPageCollection.extendByNewPage()
        QgsMessageLog().logMessage("ListPrinter PageCount: {0}".format(layoutPageCollection.pageCount()), 'APIS', Qgis.MessageLevel.Warning,
                                   notifyUser=True)

        # Export
        if layout.pageCollection().pageCount() > 0:
            layoutExporter = QgsLayoutExporter(layout)
            layoutExporter.exportToPdf(self.fileName, QgsLayoutExporter.PdfExportSettings())
            wasPrinted = True
        else:
            wasPrinted = False

        return wasPrinted


class APISFilmListPrinter(APISListPrinter):
    FILENAMETEMPLATE = "Filmliste"

    def __init__(self, fileName, idList):
        #define Info

        #define orientation

        #define query

        APISListPrinter.__init__(self, fileName, idList)


class APISImageListPrinter(APISListPrinter):
    FILENAMETEMPLATE = "Bildliste"

    def __init__(self, fileName, idList):
        #define Info

        #define orientation

        #define query

        APISListPrinter.__init__(self, fileName, idList)


class APISSiteListPrinter(APISListPrinter):
    FILENAMETEMPLATE = "Fundortliste"

    def __init__(self, fileName, idList):
        #define Info

        #define orientation

        #define query

        APISListPrinter.__init__(self, fileName, idList)

    #def printPdf(self):
        #QgsMessageLog().logMessage("SiteListPrinter: {0}".format(self.FILENAMETEMPLATE), 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)

    #def setupInfo(self):
        #("Fundortliste", "Fundortliste speichern", "Fundortliste", 22)

    #def
        # qryStr = u"SELECT filmnummer AS Filmnummer, strftime('%d.%m.%Y', flugdatum) AS Flugdatum, anzahl_bilder AS Bildanzahl, weise AS Weise, art_ausarbeitung AS Art, militaernummer AS Militärnummer, militaernummer_alt AS 'Militärnummer Alt', CASE WHEN weise = 'senk.' THEN (SELECT count(*) from luftbild_senk_cp WHERE film.filmnummer = luftbild_senk_cp.filmnummer) ELSE (SELECT count(*) from luftbild_schraeg_cp WHERE film.filmnummer = luftbild_schraeg_cp.filmnummer) END AS Kartiert, 0 AS Gescannt FROM film WHERE filmnummer IN ({0}) ORDER BY filmnummer".format(u",".join(u"'{0}'".format(site) for site in siteList))
        # qryStr = u"SELECT fundortnummer AS Fundortnummer, katastralgemeindenummer AS 'KG Nummer', katastralgemeinde AS 'KG Name', flurname AS Flurname, fundgewinnung AS Fundgewinnung, sicherheit AS Sicherheit FROM fundort WHERE fundortnummer IN ({0}) ORDER BY land, katastralgemeindenummer, fundortnummer_nn".format(u",".join(u"'{0}'".format(site) for site in siteList))
        # printer = ApisListPrinter(self, self.dbm, self.imageRegistry, True, False, None, 1)
        # printer
        # printer.setQuery(qryStr)


class APISFindspotListPrinter(APISListPrinter):
    FILENAMETEMPLATE = "Fundstellenliste"

    def __init__(self, fileName, idList):
        # define Info

        # define orientation

        # define query

        APISListPrinter.__init__(self, fileName, idList)


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done