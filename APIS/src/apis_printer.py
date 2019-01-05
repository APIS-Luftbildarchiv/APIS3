# -*- coding: utf-8 -*

from PyQt5.QtWidgets import QMessageBox, QProgressDialog, QFileDialog
from PyQt5.QtCore import (Qt, pyqtSlot, pyqtSignal, QObject, QDateTime, QDir, QSettings, QFile,
                          QDate, QRectF)
from PyQt5.QtXml import QDomDocument
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtGui import QFont, QColor

from qgis.core import (Qgis, QgsMessageLog, QgsLayout, QgsProject, QgsLayoutExporter, QgsLayoutItemPage,
                       QgsReadWriteContext, QgsApplication, QgsVectorLayer, QgsRasterLayer, QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem, QgsLineSymbol, QgsHueSaturationFilter, QgsLayoutItemMap,
                       QgsDataSourceUri, QgsFeature, QgsGeometry, QgsLayoutUtils, QgsLayoutItem, QgsLayoutSize,
                       QgsLayoutPoint, QgsLayoutItemLabel, QgsRectangle, QgsLayoutItemTextTable, QgsLayoutFrame,
                       QgsLayoutMultiFrame, QgsLayoutTableColumn, QgsLayoutTable, QgsLayoutAligner, QgsLayoutItemGroup,
                       QgsLayoutItemPicture, QgsLayoutItemShape, QgsFillSymbol)

from APIS.src.apis_utils import GenerateWeatherDescription, OpenFileOrFolder, OpenFolderAndSelect

import traceback, sys, os, errno, shutil, random, math

from PyPDF2 import PdfFileMerger, PdfFileReader
from osgeo import ogr
import datetime


class SelectionMode:
    Selection = 0
    All = 1

class OutputMode:
    MergeNone = 0
    MergeAll = 1
    MergeByGroup = 2

class APISPrinterQueue(QObject):

    def __init__(self, queue, outputMode, openFile=False, openFolder=False, dbm=None, imageRegistry=None, parent=None):

        super(APISPrinterQueue, self).__init__(parent)

        self.printerQueue = queue
        self.outputMode = outputMode
        self.openFile = openFile
        self.openFolder = openFolder
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.parent = parent
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.saveTimestamp = None
        self.tempDirName = "temp_apis_print" #ToDo get from config

        if len(self.printerQueue) <= 1:
            self.outputMode = OutputMode.MergeNone

        self.saveTo = self._requestTargetFileOrDir()
        self.isCanceled = False

        if self.saveTo:
            QgsMessageLog().logMessage("SaveTo: {0}".format(self.printerQueue), 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)
            QSettings().setValue("APIS/latest_export_dir", os.path.dirname(os.path.abspath(self.saveTo)))

            # if outputMode is OutputMode.OneFile and more than one element in queue create a temporary folder in saveTo folder
            if self.outputMode == OutputMode.MergeAll or self.outputMode == OutputMode.MergeByGroup:
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
            self.progress.setMaximum(len(self.printerQueue) + self.outputMode)
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
            if self.outputMode == OutputMode.MergeNone:
                targetDirPath = QFileDialog.getExistingDirectory(self.parent, "APIS Pdf Export Ordner", saveDir, QFileDialog.ShowDirsOnly)
                #iterate over Queue and generate FileNames
                for printable in self.printerQueue:
                    printable['fileName'] = os.path.join(targetDirPath, self._generateFileName(printable['type'], printable['idList'][0]) + "_{0}".format(self.saveTimestamp) + ".pdf")
                return targetDirPath

            elif self.outputMode == OutputMode.MergeAll:
                types = [printable['type'] for printable in self.printerQueue]
                output = []
                # generate collection filename
                for printable in self.printerQueue:
                    if types.count(printable['type']) == 1:
                        output.append(self._generateFileName(printable['type'], printable['idList'][0]))
                    elif types.count(printable['type']) > 1:
                        o = self._generateFileName(printable['type'], "Sammlung")
                        if o not in output:
                            output.append(o)
                targetFileName = "_".join(output) + "_{0}".format(self.saveTimestamp)
                targetFilePath = QFileDialog.getSaveFileName(self.parent, "APIS Pdf Export Datei", os.path.join(saveDir, targetFileName), "*.pdf")[0]
                targetDirPath = os.path.join(os.path.dirname(os.path.abspath(targetFilePath)), self.tempDirName)
                #iterate over Queue and generate temp FileNames
                for printable in self.printerQueue:
                    printable['fileName'] = os.path.join(targetDirPath, self._generateFileName(printable['type'], printable['idList'][0]) + "_{0}".format(self.saveTimestamp) + ".pdf")
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

        elif type == APISLabelPrinter.Oblique:
            return APISObliqueLabelPrinter.FILENAMETEMPLATE

        elif type == APISLabelPrinter.Vertical:
            return APISVerticalLabelPrinter.FILENAMETEMPLATE

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
                    printable['printer'] = APISFilmListPrinter(printable['fileName'], printable['idList'], self.dbm, self.imageRegistry)
                elif printable['type'] == APISListPrinter.IMAGE:
                    # Prepare Printer
                    printable['printer'] = APISImageListPrinter(printable['fileName'], printable['idList'], self.dbm, self.imageRegistry)
                elif printable['type'] == APISListPrinter.SITE:
                    # Prepare Printer
                    printable['printer'] = APISSiteListPrinter(printable['fileName'], printable['idList'], self.dbm)
                elif printable['type'] == APISListPrinter.FINDSPOT:
                    # Prepare Printer
                    printable['printer'] = APISFindspotListPrinter(printable['fileName'], printable['idList'], self.dbm)
                elif printable['type'] == APISTemplatePrinter.FILM:
                    # Prepare Printer
                    printable['printer'] = APISFilmTemplatePrinter(printable['fileName'], printable['idList'][0], self.dbm)
                elif printable['type'] == APISTemplatePrinter.SITE:
                    # Prepare Printer
                    printable['printer'] = APISSiteTemplatePrinter(printable['fileName'], printable['idList'][0], self.dbm)
                elif printable['type'] == APISTemplatePrinter.FINDSPOT:
                    # Prepare Printer
                    printable['printer'] = APISFindspotTemplatePrinter(printable['fileName'], printable['idList'][0], self.dbm)
                elif printable['type'] == APISLabelPrinter.Oblique:
                    printable['printer'] = APISObliqueLabelPrinter(printable['fileName'], printable['idList'], self.dbm)
                elif printable['type'] == APISLabelPrinter.Vertical:
                    printable['printer'] = APISVerticalLabelPrinter(printable['fileName'], printable['idList'], self.dbm)
                else:
                    raise Exception('APISPrinterQueue', 'Specified printer type not recognized.')

                printable['printed'] = printable['printer'].printPdf()
                self._updateProgress()

            if self.outputMode == OutputMode.MergeAll and len(self.printerQueue) > 1:
                merger = PdfFileMerger()
                for printable in self.printerQueue:
                    if printable['printed']:
                        merger.append(PdfFileReader(printable['fileName']), 'rb')

                with open(self.saveTo, 'wb') as fout:
                    merger.write(fout)
                    self._updateProgress()
                    shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(self.saveTo)), self.tempDirName))

            if self.openFolder:
                #OpenFileOrFolder(os.path.dirname(os.path.abspath(self.saveTo)))
                OpenFolderAndSelect(self.saveTo)

            if self.openFile:
                OpenFileOrFolder(os.path.abspath(self.saveTo))

        except Exception as inst:
            #tag, message = inst.args
            QgsMessageLog().logMessage("{0}".format(inst.args), 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)
            if inst.args[1] == 'PrintingCanceled':
                self._printingInterrupted()

    def _updateProgress(self):
        if self.progress.value() < self.progress.maximum():
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

        # Logo
        logo = self.layout.itemById('logo')
        if isinstance(logo, QgsLayoutItemPicture):
            logo.setPicturePath(os.path.join(*[QSettings().value("APIS/plugin_dir"), "templates", "layout", "Luftbildarchiv.png"]))
            logo.refreshPicture()

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

    def adjustItemsHightAndPos(self, adjustItemHightTxt, adjustItems):
        for itemId in adjustItemHightTxt:
            itemTxt = self.layout.itemById('{0}Txt'.format(itemId))
            if itemTxt:
                fontHeight = QgsLayoutUtils.fontHeightMM(itemTxt.font())
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

                itemTxt.attemptResize(QgsLayoutSize(w, newHeight))

        bottomBorder = 20.0
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
                itemMapPos = 0
                itemImgPos = 0
                if itemMap:
                    itemMap.attemptMove(QgsLayoutPoint(itemMap.pos().x(), y), useReferencePoint=False, page=currentPage)
                    itemMapPos = itemMap.pos().y() + itemMap.rectWithFrame().height()
                if itemImg:
                    itemImg.attemptMove(QgsLayoutPoint(itemImg.pos().x(), y), useReferencePoint=False, page=currentPage)
                    itemImgPos = itemImg.pos().y() + itemImg.rectWithFrame().height()

                if itemMap or itemImg:
                    newY = max(itemImgPos, itemMapPos) + 5.0

            if itemTxt and itemLbl:
                if i == 0:
                    y = itemTxt.pos().y()
                else:
                    y = newY
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
                        item = self.layout.itemById("footer_{0}".format(footer))
                        if isinstance(item, QgsLayoutItemLabel):
                            self.cloneLabel(self.layout, item, currentPage)
                        elif isinstance(item, QgsLayoutItemShape):
                            self.cloneShape(self.layout, item, currentPage)
                        footer += 1

                    # copy Logo
                    l = self.layout.itemById("logo")
                    if isinstance(l, QgsLayoutItemPicture):
                        logo = QgsLayoutItemPicture(self.layout)
                        logo.setPicturePath(l.picturePath())
                        logo.refreshPicture()
                        logo.attemptSetSceneRect(QRectF(l.pos().x(), l.pos().y(), l.rectWithFrame().width(), l.rectWithFrame().height()))
                        logo.attemptMove(QgsLayoutPoint(l.positionAtReferencePoint(QgsLayoutItem.UpperLeft)), useReferencePoint=False, page=currentPage)
                        self.layout.addItem(logo)

                itemTxt.attemptMove(QgsLayoutPoint(itemTxt.pos().x(), y), useReferencePoint=False, page=currentPage)
                itemLbl.attemptMove(QgsLayoutPoint(itemLbl.pos().x(), y), useReferencePoint=False, page=currentPage)

                i += 1

    def cloneLabel(self, layout, l, currentPage):
        label = QgsLayoutItemLabel(layout)
        label.attemptSetSceneRect(QRectF(l.pos().x(), l.pos().y(), l.rectWithFrame().width(), l.rectWithFrame().height()))
        label.attemptMove(QgsLayoutPoint(label.positionAtReferencePoint(QgsLayoutItem.UpperLeft)), useReferencePoint=False, page=currentPage)
        label.setBackgroundEnabled(True)
        label.setBackgroundColor(l.backgroundColor())
        label.setText(l.text())
        label.setVAlign(l.vAlign())
        label.setHAlign(l.hAlign())
        label.setMarginX(l.marginX())
        label.setMarginY(l.marginY())
        label.setFont(l.font())
        layout.addItem(label)

    def cloneShape(self, layout, s, currentPage):
        shape = QgsLayoutItemShape(layout)
        shape.setShapeType(s.shapeType())
        shape.setSymbol(s.symbol())
        shape.attemptSetSceneRect(QRectF(s.pos().x(), s.pos().y(), s.rectWithFrame().width(), s.rectWithFrame().height()))
        shape.attemptMove(QgsLayoutPoint(shape.positionAtReferencePoint(QgsLayoutItem.UpperLeft)), useReferencePoint=False, page=currentPage)
        layout.addItem(shape)


class APISFilmTemplatePrinter(APISTemplatePrinter):
    FILENAMETEMPLATE = "Film_{0}"

    def __init__(self, fileName, id, dbm):
        self.dbm = dbm
        template = os.path.join(*[QSettings().value("APIS/plugin_dir"), "templates", "layout", "film_logo.qpt"])
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
        schema = []
        if dataSource:
            ldefn = dataSource.GetLayer().GetLayerDefn()
            schema = [ldefn.GetFieldDefn(n).name for n in range(ldefn.GetFieldCount())]
        if not vectorLayer.hasFeatures() and dataSource and dataSource.GetLayer().GetFeatureCount() > 1 and "bildnr" in schema:

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
        template = os.path.join(*[QSettings().value("APIS/plugin_dir"), "templates", "layout", "site_logo.qpt"])
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
        adjustItemHight = ["parzelle", "flur", "hoehe", "flaeche", "kommentar_lage", "kgs_lage", "befund",
                              "literatur", "detailinterpretation"]
        adjustItemsPos = ["parzelle", "flur", "hoehe", "flaeche", "kommentar_lage", "kgs_lage", "media", "befund",
                       "literatur", "detailinterpretation"]
        self.adjustItemsHightAndPos(adjustItemHight, adjustItemsPos)


class APISFindspotTemplatePrinter(APISTemplatePrinter):
    FILENAMETEMPLATE = "Fundstelle_{0}"

    def __init__(self, fileName, id, dbm):
        self.dbm = dbm
        template = os.path.join(*[QSettings().value("APIS/plugin_dir"), "templates", "layout", "findspot_logo.qpt"])
        APISTemplatePrinter.__init__(self, fileName, id, template)

    def prepareSubstituteDict(self):
        query = QSqlQuery(self.dbm.db)
        query.prepare("SELECT fundortnummer_nn, land, katastralgemeinde, katastralgemeindenummer, fundstelle.* FROM fundstelle, fundort WHERE fundstelle.fundortnummer = fundort.fundortnummer AND fundstelle.fundortnummer || '.' || fundstelle.fundstellenummer = '{0}'".format(self.id))
        query.exec_()

        substituteDict = {}
        query.seek(-1)
        while query.next():
            rec = query.record()
            for col in range(rec.count()):
                val = "{0}".format(rec.value(col)) #str(rec.value(col))
                if val.replace(" ", "") == '' or val == 'NULL': # TODO use .isNull()
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
                substituteDict['sicherheit'] = "kein Fundstelle"

        return substituteDict

    def adjustItems(self):
        adjustItemHight = ["kommentar_lage", "fundbeschreibung", "fundverbleib", "befund", "fundgeschichte", "literatur", "sonstiges"]
        adjustItemsPos = ["kommentar_lage", "fundbeschreibung", "fundverbleib", "befund", "fundgeschichte",
                           "literatur", "sonstiges"]
        self.adjustItemsHightAndPos(adjustItemHight, adjustItemsPos)


class APISListPrinter:
    FILM = 4
    IMAGE = 5
    SITE = 6
    FINDSPOT = 7

    def __init__(self, fileName, queryStr):
        self.fileName = fileName
        self.info = None
        self.queryStr = queryStr

    def printPdf(self):
        # QgsMessageLog().logMessage("ListPrinter: {0}".format(self.FILENAMETEMPLATE), 'APIS', Qgis.MessageLevel.Warning, notifyUser=True)

        query = QSqlQuery(self.dbm.db)
        query.prepare(self.queryStr)
        query.exec_()

        # QMessageBox.information(None, "SQL", "{0}, {1}".format(query.lastError().text(), query.executedQuery()))

        layout = QgsLayout(QgsProject.instance())

        table = QgsLayoutItemTextTable(layout)
        layout.addMultiFrame(table)

        table.setResizeMode(QgsLayoutMultiFrame.RepeatUntilFinished)
        table.setHeaderMode(QgsLayoutTable.AllFrames)

        table.setGridStrokeWidth(0.2)
        table.setCellMargin(1.2)
        table.setHeaderFont(QFont("Arial", 9, QFont.DemiBold))
        table.setWrapBehavior(QgsLayoutTable.WrapText)

        layoutPageCollection = layout.pageCollection()
        page = QgsLayoutItemPage(layout)
        pageSize, pageOrientation = self.getPageSetup()
        page.setPageSize(pageSize, pageOrientation)
        layoutPageCollection.addPage(page)

        query.seek(-1)
        rec = query.record()
        cols = [QgsLayoutTableColumn()]
        cols[0].setWidth(0)
        cols[0].setHeading("#")
        for r in range(rec.count()):
            cols.append(QgsLayoutTableColumn())
            cols[-1].setWidth(0)
            cols[-1].setHeading("{}".format(rec.fieldName(r)))
        table.setColumns(cols)

        query.seek(-1)
        totalCount = 0
        while query.next():
            totalCount += 1

        QgsMessageLog().logMessage("QuerySize: {0}".format(len(str(totalCount))), 'APIS',
                                   Qgis.MessageLevel.Warning, notifyUser=True)

        query.seek(-1)
        rows = []
        while query.next():
            rec = query.record()
            row = []
            for r in range(rec.count()):
                updatedField = self.updateField(rec, r)
                if updatedField:
                    rec.setValue(r, updatedField)
                row.append("{}".format('' if rec.isNull(r) else rec.value(r)))
            rows.append([str(len(rows)+1).zfill(len(str(totalCount)))] + row)

        table.setContents(rows)

        frame = QgsLayoutFrame(layout, table)
        frame.attemptResize(QgsLayoutSize(page.pageSize().width(), page.pageSize().height()-40), True)
        table.addFrame(frame)


        for f in table.frames():
            pIdx = layoutPageCollection.pageNumberForPoint(f.pagePos())
            p = layoutPageCollection.page(pIdx)
            QgsLayoutAligner().alignItems(layout, [p, f], QgsLayoutAligner.AlignHCenter)
            f.attemptMoveBy(0, 21)

        for p in layoutPageCollection.pages():
            self._addLabel(layout, layoutPageCollection.pageNumber(p), self.header(), 5, 5, (p.pageSize().width()/2)-5, 12, marginX=2, font=QFont("Arial", 16, 75))
            self._addLabel(layout, layoutPageCollection.pageNumber(p), "Anzahl:\t{0}".format(totalCount), p.pageSize().width()/2, 5, (p.pageSize().width()/2)-5, 12, marginX=2, halign=Qt.AlignRight)

            #self._addLabel(layout, layoutPageCollection.pageNumber(p), "Luftbildarchiv, Institut für Urgeschichte und Historische Archäologie, Universität Wien", 5, p.pageSize().height()-5, (p.pageSize().width()*0.75)-5, 8, marginX=2, refPoint=QgsLayoutItem.LowerLeft)
            self._addShapeAndLogo(layout, layoutPageCollection.pageNumber(p), 5, p.pageSize().height()-5, (p.pageSize().width()*0.75)-5, 12, marginX=2, refPoint=QgsLayoutItem.LowerLeft)
            self._addLabel(layout, layoutPageCollection.pageNumber(p), "Seite {0}\n{1}".format(layoutPageCollection.pageNumber(p)+1, QDateTime.currentDateTime().toString("dd.MM.yyyy")), p.pageSize().width()-5, p.pageSize().height()-5, (p.pageSize().width()*0.25)-5, 12, marginX=2, refPoint=QgsLayoutItem.LowerRight, halign=Qt.AlignRight)


        # Export
        if layout.pageCollection().pageCount() > 0:
            layoutExporter = QgsLayoutExporter(layout)
            layoutExporter.exportToPdf(self.fileName, QgsLayoutExporter.PdfExportSettings())
            wasPrinted = True
        else:
            wasPrinted = False

        del(query)

        return wasPrinted

    def _addLabel(self, layout, pIdx, text, x, y, w, h, marginX=5, refPoint=QgsLayoutItem.UpperLeft, halign=Qt.AlignLeft, font=QFont("Arial", 8)):
        label = QgsLayoutItemLabel(layout)
        label.setReferencePoint(refPoint)
        label.attemptResize(QgsLayoutSize(w, h))
        label.attemptMove(QgsLayoutPoint(x, y), page=pIdx)
        label.setBackgroundEnabled(True)
        label.setBackgroundColor(QColor("#CCCCCC"))
        label.setText(text)
        label.setVAlign(Qt.AlignVCenter)
        label.setHAlign(halign)
        label.setMarginX(marginX)
        label.setFont(font)
        layout.addItem(label)

    def _addShapeAndLogo(self, layout, pIdx, x, y, w, h, marginX=5, refPoint=QgsLayoutItem.UpperLeft):
        # Shape
        shape = QgsLayoutItemShape(layout)
        shape.setReferencePoint(refPoint)
        shape.attemptResize(QgsLayoutSize(w, h))
        shape.attemptMove(QgsLayoutPoint(x, y), page=pIdx)
        sym = QgsFillSymbol.createSimple({'color': '204,204,204', 'style': 'solid', 'outline_style': 'no'})
        shape.setSymbol(sym)
        layout.addItem(shape)

        # Logo
        logo = QgsLayoutItemPicture(layout)
        logo.setReferencePoint(refPoint)
        logo.setPicturePath(os.path.join(*[QSettings().value("APIS/plugin_dir"), "templates", "layout", "Luftbildarchiv.png"]))
        logo.refreshPicture()
        logo.attemptResize(QgsLayoutSize(w-2, h-2))
        logo.attemptMove(QgsLayoutPoint(x+2, y-1), page=pIdx)
        layout.addItem(logo)



class APISFilmListPrinter(APISListPrinter):
    FILENAMETEMPLATE = "Filmliste"

    def __init__(self, fileName, idList, dbm, imageRegistry):
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        #define Info

        #define orientation

        #define query
        qryStr = "SELECT filmnummer AS Filmnummer, strftime('%d.%m.%Y', flugdatum) AS Flugdatum, anzahl_bilder AS Bildanzahl, weise AS Weise, art_ausarbeitung AS Art, militaernummer AS Militärnummer, militaernummer_alt AS 'Militärnummer Alt', CASE WHEN weise = 'senk.' THEN (SELECT count(*) from luftbild_senk_cp WHERE film.filmnummer = luftbild_senk_cp.filmnummer) ELSE (SELECT count(*) from luftbild_schraeg_cp WHERE film.filmnummer = luftbild_schraeg_cp.filmnummer) END AS Kartiert, 0 AS Gescannt FROM film WHERE filmnummer IN ({0}) ORDER BY {1}".format(",".join("'{0}'".format(film) for film in idList), ",".join("filmnummer='{0}' DESC".format(film) for film in idList))

        APISListPrinter.__init__(self, fileName, qryStr)

    def header(self):
        return "Filmliste"

    def getPageSetup(self):
        return "A4", QgsLayoutItemPage.Landscape

    def updateField(self, rec, r):
        fieldName = rec.fieldName(r)

        if fieldName == "Gescannt":
            return self.imageRegistry.hasImageRE(str(rec.value("filmnummer")) + "_.+")
        elif fieldName == "Ortho":
            return self.imageRegistry.hasOrthoRE(str(rec.value("filmnummer")) + "_.+")
        elif fieldName == "HiRes":
            return self.imageRegistry.hasHiResRE(str(rec.value("filmnummer")) + "_.+")
        else:
            return None


class APISImageListPrinter(APISListPrinter):
    FILENAMETEMPLATE = "Bildliste"

    def __init__(self, fileName, idList, dbm, imageRegistry):
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        #define Info

        #define orientation

        #define query
        qryStr = "SELECT * FROM (SELECT bildnummer AS Bildnummer, weise AS Weise, radius AS 'Radius/Maßstab', art_ausarbeitung AS Art, '' AS Gescannt, '' AS Ortho, '' AS HiRes FROM luftbild_schraeg_cp oI, film f WHERE oI.filmnummer = f.filmnummer AND bildnummer IN ({0}) UNION ALL SELECT bildnummer AS Bildnummer, weise AS Weise, CAST(massstab AS INT) AS 'Radius/Maßstab', art_ausarbeitung AS Art, '' AS Gescannt, '' AS Ortho, '' AS HiRes FROM luftbild_senk_cp vI, film f WHERE vI.filmnummer = f.filmnummer AND bildnummer IN ({0})) ORDER BY {1}".format(",".join("'{0}'".format(image) for image in idList), ", ".join("Bildnummer='{0}' DESC".format(image) for image in idList))

        APISListPrinter.__init__(self, fileName, qryStr)

    def header(self):
        return "Bildliste"

    def getPageSetup(self):
        return "A4", QgsLayoutItemPage.Portrait

    def updateField(self, rec, r):
        fieldName = rec.fieldName(r)

        if fieldName == "Gescannt":
            return "\u2713" if self.imageRegistry.hasImage(str(rec.value("bildnummer"))) else None
        elif fieldName == "Ortho":
            return "\u2713" if self.imageRegistry.hasOrtho(str(rec.value("bildnummer"))) else None
        elif fieldName == "HiRes":
            return "\u2713" if self.imageRegistry.hasHiRes(str(rec.value("bildnummer"))) else None
        else:
            return None


class APISSiteListPrinter(APISListPrinter):
    FILENAMETEMPLATE = "Fundortliste"

    def __init__(self, fileName, idList, dbm):
        self.dbm = dbm
        #define Info

        #define orientation

        #define query
        qryStr = "SELECT fundortnummer AS Fundortnummer, katastralgemeindenummer AS 'KG Nummer', katastralgemeinde AS 'KG Name', flurname AS Flurname, fundgewinnung AS Fundgewinnung, sicherheit AS Sicherheit FROM fundort WHERE fundortnummer IN ({0}) ORDER BY {1}".format(",".join("'{0}'".format(site) for site in idList), ",".join("fundortnummer='{0}' DESC".format(site) for site in idList))

        APISListPrinter.__init__(self, fileName, qryStr)

    def header(self):
        return "Fundortliste"

    def getPageSetup(self):
        return "A4", QgsLayoutItemPage.Landscape

    def updateField(self, rec, r):
        return None


class APISFindspotListPrinter(APISListPrinter):
    FILENAMETEMPLATE = "Fundstellenliste"

    def __init__(self, fileName, idList, dbm):
        self.dbm = dbm
        # define Info

        # define orientation

        # define query
        qryStr = "SELECT fs.fundortnummer || '.' || fs.fundstellenummer AS Fundstellenummer, fo.katastralgemeindenummer AS 'KG Nummer', fo.katastralgemeinde AS 'KG Name', datierung_zeit || ',' || datierung_periode || ',' || datierung_periode_detail || ',' || phase_von || '-' || phase_bis AS Datierung, fundart AS Fundart FROM fundstelle fs, fundort fo WHERE fs.fundortnummer = fo.fundortnummer AND fs.fundortnummer || '.' || fs.fundstellenummer IN ({0}) ORDER BY {1}".format(",".join("'{0}'".format(findspot) for findspot in idList),  ",".join("fs.fundortnummer || '.' || fs.fundstellenummer='{0}' DESC".format(findspot) for findspot in idList))

        APISListPrinter.__init__(self, fileName, qryStr)

    def header(self):
        return "Fundstellenliste"

    def getPageSetup(self):
        return "A4", QgsLayoutItemPage.Landscape

    def updateField(self, rec, r):
        return None


class APISLabelPrinter:
    Oblique = 8
    Vertical = 9

    def __init__(self, fileName):
        self.fileName = fileName

    def printPdf(self):
        self.layout = QgsLayout(QgsProject.instance())
        layoutPageCollection = self.layout.pageCollection()
        page = QgsLayoutItemPage(self.layout)
        page.setPageSize("A4", QgsLayoutItemPage.Portrait)
        layoutPageCollection.addPage(page)

        left = 0
        right = 0
        top = 0
        bottom = 0

        self.colCount = int((page.pageSize().width() - (left + right)) / self.labelWidth())
        self.rowCount = int((page.pageSize().height() - (top + bottom)) / self.labelHeight())
        #QMessageBox.information(None, "info", "cols: {0} rows: {1}".format(self.colCount, self.rowCount))
        self.currentCol = 0
        self.currentRow = 0
        self.labelCount = 0
        self.pageCount = 1

        #generate Labels
        labelGroups = []
        for labelData in self.labelsData:
            newLabelGroups = self._generateLabel(labelData)
            labelGroups += newLabelGroups

        #QMessageBox.information(None, "Info", "{0}".format(len(labelGroups)))

        for labelGroup in labelGroups:
            dx = self.currentCol * self.labelWidth()
            dy = self.currentRow * self.labelHeight()
            labelGroup.attemptMove(QgsLayoutPoint(dx, dy), page=self.pageCount-1)
            self.layout.addItem(labelGroup)
            self.currentCol += 1
            if self.currentCol >= self.colCount:
                self.currentCol = 0
                self.currentRow += 1
            if self.currentRow >= self.rowCount:
                self.currentRow = 0
                self.pageCount += 1
                layoutPageCollection.extendByNewPage()

        # Export
        if self.layout.pageCollection().pageCount() > 0:
            layoutExporter = QgsLayoutExporter(self.layout)
            layoutExporter.exportToPdf(self.fileName, QgsLayoutExporter.PdfExportSettings())
            wasPrinted = True
        else:
            wasPrinted = False

        return wasPrinted

    def _generateLabel(self, labelData):
        x = 0
        y = 0
        maxH = 0
        labelGroups = []
        for key in self.labelItemOrder:
            for item in labelData[key]:

                w = self.labelWidth() * self.labelLayout[key]['width']
                h = self.labelHeight() * self.labelLayout[key]['height']
                maxH = max(maxH, h)

                if x+w > self.labelWidth():
                    x = 0
                    y += maxH
                    maxH = max(maxH, h)

                if y+h > self.labelHeight():
                    y = 0
                    x = 0

                if y == 0:
                    labelGroups.append(QgsLayoutItemGroup(self.layout))

                    labelGroups[-1].attemptResize(QgsLayoutSize(self.labelWidth(), self.labelHeight()))
                    labelGroups[-1].attemptMove(QgsLayoutPoint(0, 0))

                label = self._generateLabelItem(u"{0}".format(item), x, y, w, h, key)
                labelGroups[-1].addItem(label)

                x += w

        return labelGroups

    def _generateLabelItem(self, text, x, y, w, h, key):
        label = QgsLayoutItemLabel(self.layout)
        label.attemptResize(QgsLayoutSize(w, h))
        label.attemptMove(QgsLayoutPoint(x, y))
        label.setText(text)
        label.setVAlign(self.labelLayout[key]['valign'])
        label.setHAlign(self.labelLayout[key]['halign'])
        label.setMarginX(0)
        label.setMarginY(0)
        label.setFont(self.labelLayout[key]['font'])
        self.layout.addItem(label)
        return label

class APISObliqueLabelPrinter(APISLabelPrinter):
    FILENAMETEMPLATE = "Etiketten_Schräg"

    def __init__(self, fileName, idList, dbm):
        query = QSqlQuery(dbm.db)
        title = u"Uni Wien - IUHA - Luftbildarchiv"
        qryStr = u"SELECT luftbild_schraeg_fp.bildnummer AS bildnummer, '[' || fundortnummer || '][' || katastralgemeindenummer  || ' ' || katastralgemeinde || ']' AS fundort_kg FROM fundort, luftbild_schraeg_fp WHERE luftbild_schraeg_fp.bildnummer IN ({0}) AND Intersects(fundort.geometry, luftbild_schraeg_fp.geometry)AND fundort.rowid IN (SELECT rowid FROM spatialindex WHERE f_table_name='fundort' AND search_frame=luftbild_schraeg_fp.geometry) ORDER BY luftbild_schraeg_fp.bildnummer, katastralgemeindenummer, fundortnummer_nn".format(
            u",".join(u"'{0}'".format(image) for image in idList))
        query.prepare(qryStr)
        query.exec_()
        self.labelsData = []

        for imageNumber in idList:
            labelData = {
                'title': [title],
                'bildnummer': [imageNumber],
                'fundort_kg': []
            }
            query.seek(-1)
            while query.next():
                rec = query.record()
                if rec.value("bildnummer") == imageNumber:
                    labelData['fundort_kg'].append(rec.value("fundort_kg"))

            self.labelsData.append(labelData)

        self.labelItemOrder = ['title', 'bildnummer', 'fundort_kg']
        self.labelLayout = {
            'title': {'width': 1.0, 'height': 1.0 / 3.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter,
                      'valign': Qt.AlignVCenter},
            'bildnummer': {'width': 1.0, 'height': 1.0 / 3.0, 'font': QFont("Arial", 6, QFont.Bold),
                           'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
            'fundort_kg': {'width': 1.0, 'height': 1.0 / 3.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter,
                           'valign': Qt.AlignVCenter}
        }

        APISLabelPrinter.__init__(self, fileName)

    def labelWidth(self):
        return 42.0

    def labelHeight(self):
        return 10.0

class APISVerticalLabelPrinter(APISLabelPrinter):
    FILENAMETEMPLATE = "Etiketten_Senkrecht"

    def __init__(self, fileName, idList, dbm):
        query = QSqlQuery(dbm.db)
        title = u"Uni Wien - IUHA - Luftbildarchiv"
        qryStr = u"SELECT luftbild_senk_fp.bildnummer AS bildnummer, film.kamera, luftbild_senk_cp.fokus, luftbild_senk_cp.hoehe, luftbild_senk_cp.massstab, film.militaernummer AS mil_num, film.flugdatum, '[' || fundortnummer || '][' || katastralgemeindenummer  || ' ' || katastralgemeinde || ']' AS fundort_kg FROM film, fundort, luftbild_senk_cp, luftbild_senk_fp WHERE luftbild_senk_fp.filmnummer = film.filmnummer AND luftbild_senk_cp.bildnummer = luftbild_senk_fp.bildnummer AND luftbild_senk_fp.bildnummer IN ({0}) AND Intersects(fundort.geometry, luftbild_senk_fp.geometry)AND fundort.rowid IN (SELECT rowid FROM spatialindex WHERE f_table_name='fundort' AND search_frame=luftbild_senk_fp.geometry) ORDER BY luftbild_senk_fp.bildnummer, katastralgemeindenummer, fundortnummer_nn".format(
            u",".join(u"'{0}'".format(image) for image in idList))
        query.prepare(qryStr)
        query.exec_()
        self.labelsData = []
        query.seek(-1)
        count = 0
        while query.next():
            count += 1

        # Keine FOs
        if count == 0:
            qryStrOblique = u"SELECT luftbild_senk_cp.bildnummer AS bildnummer, film.kamera, luftbild_senk_cp.fokus, luftbild_senk_cp.hoehe, luftbild_senk_cp.massstab, film.militaernummer AS mil_num, film.flugdatum FROM film, luftbild_senk_cp WHERE luftbild_senk_cp.filmnummer = film.filmnummer AND luftbild_senk_cp.bildnummer IN ({0}) ORDER BY luftbild_senk_cp.bildnummer".format(
                u",".join(u"'{0}'".format(image) for image in idList))
            query.prepare(qryStr)
            query.exec_()

        for imageNumber in idList:
            labelData = {
                'title': [title],
                'bildnummer': [imageNumber],
                'mil_nummer': [],
                'flugdatum': [],
                'kamera': [],
                'fokus': [],
                'massstab': [],
                'hoehe': [],
                'fundort_kg': []
            }

            query.seek(-1)
            while query.next():
                rec = query.record()
                if rec.value("bildnummer") == imageNumber:
                    if len(labelData['mil_nummer']) < 1:
                        if rec.isNull("mil_nummer"):
                            labelData['mil_nummer'].append(u"Mil#: -")
                        else:
                            labelData['mil_nummer'].append(u"Mil#: {0}".format(rec.value("mil_num")))

                    if len(labelData['flugdatum']) < 1:
                        if rec.isNull("flugdatum"):
                            labelData['flugdatum'].append(u"kein Flugdatum")
                        else:
                            labelData['flugdatum'].append(u"Flug vom {0}".format(
                                datetime.datetime.strptime(rec.value("flugdatum"), '%Y-%m-%d').strftime('%d.%m.%Y')))

                    if len(labelData['kamera']) < 1:
                        if rec.isNull("kamera"):
                            labelData['kamera'].append(u"Kamera: -")
                        else:
                            labelData['kamera'].append(u"Kamera: {0}".format(rec.value("kamera")))

                    if len(labelData['fokus']) < 1:
                        if rec.isNull("fokus"):
                            labelData['fokus'].append(u"Fokus: -")
                        else:
                            labelData['fokus'].append(u"Fokus: {0:.2f}".format(float(rec.value("fokus"))))

                    if len(labelData['massstab']) < 1:
                        if rec.isNull("massstab"):
                            labelData['massstab'].append(u"Mst. -")
                        else:
                            labelData['massstab'].append(u"Mst. 1:{0}".format(int(rec.value("massstab"))))

                    if len(labelData['hoehe']) < 1:
                        if rec.isNull("hoehe"):
                            labelData['hoehe'].append(u"Höhe: -")
                        else:
                            labelData['hoehe'].append(u"Höhe: {0}m".format(rec.value("hoehe")))

                    if count > 0:
                        if rec.isNull("fundort_kg"):
                            labelData['fundort_kg'].append(u"---")
                        else:
                            labelData['fundort_kg'].append(rec.value("fundort_kg"))

            self.labelsData.append(labelData)

        self.labelItemOrder = ['title', 'bildnummer', 'mil_nummer', 'flugdatum', 'kamera', 'fokus', 'massstab', 'hoehe',
                          'fundort_kg']
        self.labelLayout = {
            'title': {'width': 1.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter,
                      'valign': Qt.AlignVCenter},
            'bildnummer': {'width': 1.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 6, QFont.Bold),
                           'halign': Qt.AlignCenter, 'valign': Qt.AlignVCenter},
            'mil_nummer': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter,
                           'valign': Qt.AlignVCenter},
            'flugdatum': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter,
                          'valign': Qt.AlignVCenter},
            'kamera': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter,
                       'valign': Qt.AlignVCenter},
            'fokus': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter,
                      'valign': Qt.AlignVCenter},
            'massstab': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter,
                         'valign': Qt.AlignVCenter},
            'hoehe': {'width': 1.0 / 2.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter,
                      'valign': Qt.AlignVCenter},
            'fundort_kg': {'width': 1.0, 'height': 1.0 / 6.0, 'font': QFont("Arial", 5), 'halign': Qt.AlignCenter,
                           'valign': Qt.AlignVCenter}
        }
        APISLabelPrinter.__init__(self, fileName)

    def labelWidth(self):
        return 70.0

    def labelHeight(self):
        return 35.0