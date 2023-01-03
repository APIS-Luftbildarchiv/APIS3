# -*- coding: utf-8 -*-
import os.path
import json

from PyQt5.QtCore import QSettings, QDir, QFile
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from qgis.core import (QgsProject, QgsDataSourceUri, QgsVectorLayer, QgsRasterLayer, QgsLayerTree, QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform, QgsRectangle, QgsVectorFileWriter, QgsFeature, QgsWkbTypes, Qgis, QgsMessageLog)

from APIS.src.apis_utils import FileOrFolder, OpenFileOrFolder

from osgeo import ogr, osr, gdal
from osgeo.gdalconst import GA_Update


class ApisLayerManager:
    def __init__(self, pluginDir, iface, dbm):
        self.layerTreeConfigFile = pluginDir + "\\layer_tree\\apis_layer_tree_config.json"
        self.stylesDir = pluginDir + "\\layer_tree\\styles\\"
        self.iface = iface
        self.dbm = dbm

        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        if self.settings.value("APIS/disable_site_and_findspot", "0") != "1":
            self.version = 2
        else:
            self.version = 1

        self.isLoaded = False

        self.tocRoot = QgsProject.instance().layerTreeRoot()

        self._imageObliqueCPLayer = None
        self._imageObliqueFPLayer = None
        self._imageObliqueCPLayerId = None
        self._imageObliqueFPLayerId = None

        self._imageVerticalCPLayer = None
        self._imageVerticalFPLayer = None
        self._imageVerticalCPLayerId = None
        self._imageVerticalFPLayerId = None

        self._siteLayer = None
        self._findspotLayer = None
        self._siteLayerId = None
        self._findspotLayerId = None

        self._loadApisLayerTreeConfig()

    def _loadApisLayerTreeConfig(self):
        if os.path.isfile(self.layerTreeConfigFile):
            with open(self.layerTreeConfigFile, 'r') as lT:
                layerTreeConfig = json.load(lT)
                self.__layers = layerTreeConfig["layers"]
                self.__groups = layerTreeConfig["groups"]
                #self.__groupsOrder = layerTreeConfig["groups_order"]
                self.isLoaded = True
        else:
            self.isLoaded = False

    def loadDefaultLayerTree(self):
        if self.isLoaded:
            self._loadDefaultApisLayers()

            # return
            #
            # uri = QgsDataSourceURI()
            # uri.setDatabase(self.dbm.db.databaseName())
            #
            # for layer in self.__layers:
            #     if "default" in self.__layers[layer] and self.__layers[layer]["default"]:
            #         #QMessageBox.information(None, "LayerTree", "LoadLayerTree {0}".format(len(self.__layers)))
            #         groupName = self.__groups[self.__layers[layer]["group"]]
            #         if not self.tocRoot.findGroup(groupName):
            #             idx = 0
            #             orderIdx = self.__groupsOrder.index(self.__layers[layer]["group"])
            #             for child in self.tocRoot.children():
            #                 if QgsLayerTree.isGroup(child):
            #                     i = self.__groupsOrder.index(self.__layers[layer]["group"])
            #
            #                     #idx = min(groupCount, )
            #             QMessageBox.information(None, "Sources", u"{0}, {1}".format(groupName, idx))
            #             g = self.tocRoot.insertGroup(idx, groupName)
            #             g.setCustomProperty("apis_group_id", self.__layers[layer]["group"])
            #
            #         group = self.tocRoot.findGroup(groupName)
            #
            #         #layersInGroup = group.findLayers()
            #         layerNamesInGroup = [layerInGroup.layerName() for layerInGroup in group.findLayers()]
            #
            #         if self.__layers[layer]["display_name"] not in layerNamesInGroup:
            #             uri.setDataSource('', self.__layers[layer]["name"], 'geometry')
            #             vectorLayer = QgsVectorLayer(uri.uri(), self.__layers[layer]["display_name"], 'spatialite')
            #             vectorLayer.loadNamedStyle(self.stylesDir + self.__layers[layer]["style"])
            #             QgsMapLayerRegistry.instance().addMapLayer(vectorLayer, False)
            #             group.insertLayer(0, vectorLayer)
            #             prfx = "dbname='"
            #             dSU = vectorLayer.dataProvider().dataSourceUri()
            #             ext = ".sqlite"
            #             dbPath = dSU[dSU.find(prfx) + len(prfx):dSU.find(ext) + len(ext)]
            #             #QMessageBox.information(None, "Sources", u"{0}, {1}".format(os.path.normpath(dbPath), os.path.normpath(self.dbm.db.databaseName())))

    # def _loadApisLayerGroups(self):
    #     #self.tocRoot = QgsProject.instance().layerTreeRoot()
    #     for groupId in self.__groups:
    #         groupName = self.__groups[groupId]["display_name"]
    #         self._addGroupIfMissing(groupName)

    def requestImageLayers(self):
        return [self.requestImageVerticalCpLayer(), self.requestImageVerticalFpLayer(), self.requestImageObliqueCpLayer(), self.requestImageObliqueFpLayer()]

    def requestSiteLayers(self):
        return [self.requestSiteLayer(), self.requestFindspotLayer()]

    def requestImageVerticalCpLayer(self):
        groupName = self.__groups[self.__layers["images_vertical_cp"]["group"]]["display_name"]
        self._addGroupIfMissing(groupName)
        stylePath = self.stylesDir + self.__layers["images_vertical_cp"]["style"]
        layer = self.requestSpatialiteTable(self.dbm.db.databaseName(), self.__layers["images_vertical_cp"]["name"],
                                            self.__layers["images_vertical_cp"]["display_name"], groupName, None, True, True, stylePath)
        return layer

    def requestImageVerticalFpLayer(self):
        groupName = self.__groups[self.__layers["images_vertical_fp"]["group"]]["display_name"]
        self._addGroupIfMissing(groupName)
        stylePath = self.stylesDir + self.__layers["images_vertical_fp"]["style"]
        layer = self.requestSpatialiteTable(self.dbm.db.databaseName(), self.__layers["images_vertical_fp"]["name"],
                                            self.__layers["images_vertical_fp"]["display_name"], groupName, None, True, True, stylePath)
        return layer

    def requestImageObliqueCpLayer(self):
        groupName = self.__groups[self.__layers["images_oblique_cp"]["group"]]["display_name"]
        self._addGroupIfMissing(groupName)
        stylePath = self.stylesDir + self.__layers["images_oblique_cp"]["style"]
        layer = self.requestSpatialiteTable(self.dbm.db.databaseName(), self.__layers["images_oblique_cp"]["name"],
                                            self.__layers["images_oblique_cp"]["display_name"], groupName, None, True, True, stylePath)
        return layer

    def requestImageObliqueFpLayer(self):
        groupName = self.__groups[self.__layers["images_oblique_fp"]["group"]]["display_name"]
        self._addGroupIfMissing(groupName)
        stylePath = self.stylesDir + self.__layers["images_oblique_fp"]["style"]
        layer = self.requestSpatialiteTable(self.dbm.db.databaseName(), self.__layers["images_oblique_fp"]["name"],
                                            self.__layers["images_oblique_fp"]["display_name"], groupName, None, True, True, stylePath)
        return layer

    def requestSiteLayer(self):
        groupName = self.__groups[self.__layers["sites"]["group"]]["display_name"]
        self._addGroupIfMissing(groupName)
        stylePath = self.stylesDir + self.__layers["sites"]["style"]
        layer = self.requestSpatialiteTable(self.dbm.db.databaseName(), self.__layers["sites"]["name"],
                                            self.__layers["sites"]["display_name"], groupName, None, True, True, stylePath)
        return layer

    def requestFindspotLayer(self):
        groupName = self.__groups[self.__layers["find_spots"]["group"]]["display_name"]
        self._addGroupIfMissing(groupName)
        stylePath = self.stylesDir + self.__layers["find_spots"]["style"]
        layer = self.requestSpatialiteTable(self.dbm.db.databaseName(), self.__layers["find_spots"]["name"],
                                            self.__layers["find_spots"]["display_name"], groupName, None, True, True, stylePath)
        return layer

    def requestSpatialiteLayer(self, layerName):
        if layerName in self.__layers:
            groupName = self.__groups[self.__layers[layerName]["group"]]["display_name"]
            self._addGroupIfMissing(groupName)
            stylePath = self.stylesDir + self.__layers[layerName]["style"]
            layer = self.requestSpatialiteTable(self.dbm.db.databaseName(), self.__layers[layerName]["name"],
                                                self.__layers[layerName]["display_name"], groupName, None, True, True, stylePath)
            return layer

    def _getPosOfPrevGroup(self, groupName):
        topLevelGroups = [child.name() for child in self.tocRoot.children() if QgsLayerTree.isGroup(child)]
        if groupName in topLevelGroups:
            return topLevelGroups.index(groupName)
        else:
            return None

    def _loadDefaultApisLayers(self):
        for layerId in self.__layers:
            if "default" in self.__layers[layerId] and self.__layers[layerId]["default"] <= self.version:
                # QMessageBox.information(None, "LayerTree", "LoadLayerTree {0}".format(len(self.__layers)))
                groupName = self.__groups[self.__layers[layerId]["group"]]["display_name"]
                self._addGroupIfMissing(groupName)
                stylePath = self.stylesDir + self.__layers[layerId]["style"]
                self.requestSpatialiteTable(self.dbm.db.databaseName(), self.__layers[layerId]["name"], self.__layers[layerId]["display_name"], groupName, None, True, True, stylePath)

    def _isApisGroupName(self, groupName):
        apisGroupNames = [self.__groups[groupId]["display_name"] for groupId in self.__groups]
        return groupName in apisGroupNames

    def _getApisGroupId(self, groupName):
        groupId = None
        for groupId in self.__groups:
            if groupName == self.__groups[groupId]["display_name"]:
                return groupId
        return groupId

    def _getApisLayerId(self, layerName):
        layerId = None
        for layerId in self.__layers:
            if "display_name" in self.__layers[layerId] and layerName == self.__layers[layerId]["display_name"]:
                return layerId
        return layerId

    def _addApisGroup(self, groupName):
        group = self.tocRoot.findGroup(groupName)
        if not group:
            groupId = self._getApisGroupId(groupName)
            posAfterId = self.__groups[groupId]["pos_after"]
            if posAfterId == 0 or posAfterId not in self.__groups or posAfterId == groupId:
                group = self.tocRoot.insertGroup(0, groupName)
                return group
            else:
                foundPrevGroup = False
                while not foundPrevGroup:
                    prevGroupName = self.__groups[posAfterId]["display_name"]
                    if self.tocRoot.findGroup(prevGroupName):
                        idx = self._getPosOfPrevGroup(prevGroupName)
                        idx += 1
                        group = self.tocRoot.insertGroup(idx, groupName)
                        foundPrevGroup = True
                        return group
                    else:
                        posAfterId = self.__groups[posAfterId]["pos_after"]
                        if posAfterId == 0:
                            group = self.tocRoot.insertGroup(0, groupName)
                            foundPrevGroup = True
                            return group
        else:
            return group

    def _addGroupIfMissing(self, groupName):
        group = self.tocRoot.findGroup(groupName)
        if not group:
            if self._isApisGroupName(groupName):
                group = self._addApisGroup(groupName)
            else:
                group = self.tocRoot.insertGroup(0, groupName)
            return group
        else:
            return group

    def _getLayerIdx(self, layer=None, group=None):
        #if layer and group:
        layerId = self._getApisLayerId(layer.name())
        #QMessageBox.information(None, "Blub", "{0}".format(layerId))

        if layerId and "in_group_pos_after" in self.__layers[layerId]:
            posAfterId = self.__layers[layerId]["in_group_pos_after"]
            if posAfterId == 0 or posAfterId not in self.__layers or posAfterId == layerId:
                return 0
            else:
                # foundPrevLayer = False
                # while not foundPrevLayer:
                prevLayerName = self.__layers[posAfterId]["display_name"]
                availableLayersInGroup = [lyr.name() for lyr in group.findLayers()]
                if prevLayerName in availableLayersInGroup:
                    return availableLayersInGroup.index(prevLayerName) + 1
                else:
                    return 0
                #QMessageBox.information(None, "Info", "{0}, {1}".format(prevLayerName, availableLayersInGroup))
                    #if prevLayerName in availableLayersInGroup:
                    #    foundPrevLayer = True

        return 0
        #QMessageBox.information(None, "Blub", "{0} in {1}".format(layer.name(), group.name()))
        #posAfterId = self.__groups[layerName]["in_group_pos_after"]
        #if posAfterId == 0 or posAfterId not in self.__layerName or posAfterId == groupId:

        # else:
        #    return 0

    def addLayerToCanvas(self, layer, groupName=None):
        try:
            ret = QgsProject.instance().addMapLayer(layer, False)
            if ret:
                if groupName:
                    group = self._addGroupIfMissing(groupName)
                    layerIdx = self._getLayerIdx(layer, group)
                    #QMessageBox.information(None, "blub", "{0}".format(layerIdx))
                    group.insertLayer(layerIdx, layer)
                    #group.addLayer(layer)
                else:
                    self.tocRoot.insertLayer(0, layer)
                return True
            else:
                return False
        except Exception:
            return False

    def loadOEK50Layers(self):

        m28VRT = self.settings.value("APIS/oek50_gk_qgis_m28", None)
        m31VRT = self.settings.value("APIS/oek50_gk_qgis_m31", None)
        m34VRT = self.settings.value("APIS/oek50_gk_qgis_m34", None)

        if m28VRT and os.path.isfile(m28VRT):
            oekLayer28 = QgsRasterLayer(m28VRT, "ok50_m28")
            self.addLayerToCanvas(oekLayer28, "oek50")

        if m31VRT and os.path.isfile(m31VRT):
            oekLayer31 = QgsRasterLayer(m31VRT, "ok50_m31")
            self.addLayerToCanvas(oekLayer31, "oek50")

        if m31VRT and os.path.isfile(m31VRT):
            oekLayer34 = QgsRasterLayer(m34VRT, "ok50_m34")
            self.addLayerToCanvas(oekLayer34, "oek50")

    def _loadSpaitaliteTable(self, databaseName, tableName, displayName=None, subsetString=None):
        try:
            if not displayName:
                displayName = tableName

            uri = QgsDataSourceUri()
            uri.setDatabase(databaseName)
            uri.setDataSource('', tableName, 'geometry')
            layer = QgsVectorLayer(uri.uri(), displayName, 'spatialite')
            if subsetString:
                layer.setSubsetString(subsetString)

            return layer
        except Exception as e:
            QMessageBox.warning(None, "Error Loading Spatialtie Table", u"{0}".format(e))
            return None

    # def _addSpatialiteLayerToCanvas(self, layer, groupName=None):
    #     ret = QgsMapLayerRegistry.instance().addMapLayer(layer, False)

    # def requestSiteLayer(self, addToCanvas=False):
    #     siteLayer = self._requestApisLayer(self._siteLayer, self._siteLayerId, 'fundort', addToCanvas)
    #     return siteLayer
    #
    # def _requestApisLayer(self, apisLayer, apisLayerId, layerName, addToCanvas=False):
    #     # Is site Layer in Canvas
    #     layerNamesInGroup = [layerInGroup.layerName() for layerInGroup in self.tocRoot.findLayers()]
    #
    #     # if apisLayer:
    #     #     return apisLayer
    #     # else:
    #     #     self._siteLayer = self.loadSpatialiteLayer()
    #     #
    #     # if apisLayer and addToCanvas:
    #     #     self._addSpatialiteLayerToCanvas(apisLayer)
    #     #
    #     # return apisLayer

    def requestSpatialiteTable(self, databaseName, tableName, displayName=None, groupName=None, subsetString=None, useLayerFromTree=True, addToCanvas=False, stylePath=None):
        try:
            layer = None
            if not displayName:
                displayName = tableName

            if useLayerFromTree:
                layer = self.findspatialiteLayerInTree(databaseName, tableName)
                if layer is not None and layer.subsetString() != "":
                    layer = None
                    #QMessageBox.information(None, "info", "subset: {}".format(layer.subsetString()))
            if layer is None:
                layer = self._loadSpaitaliteTable(databaseName, tableName, displayName, subsetString)

                if addToCanvas:
                    if stylePath:
                        layer.loadNamedStyle(stylePath)
                    self.addLayerToCanvas(layer, groupName)
            return layer
        except Exception as e:
            QMessageBox.warning(None, "Error Requesting Spatialtie Table", u"{0}".format(e))
            return None

    def requestShapeFile(self, shapeFilePath, epsg=None, defaultEpsg=None, layerName=None, groupName=None, useLayerFromTree=True, addToCanvas=False, stylePath=None):
        try:
            #QMessageBox.information(None, "Info", "LOAD SHP")
            layer = None
            if not layerName:
                layerName = os.path.basename(shapeFilePath)
                root, ext = os.path.splitext(layerName)
                if ext == '.shp':
                    layerName = root
            if useLayerFromTree:
                layer = self.findshapeFileLayerInTree(shapeFilePath)
            if layer is None:
                if not self.shapeFileHasCrs(shapeFilePath) and defaultEpsg:
                    # apply defaultEpsg To Shape file
                    spatialRef = osr.SpatialReference()
                    spatialRef.ImportFromEPSG(defaultEpsg)
                    spatialRef.MorphToESRI()
                    shapePrjFilePath = os.path.splitext(shapeFilePath)[0] + '.prj'
                    file = open(shapePrjFilePath, 'w')
                    file.write(spatialRef.ExportToWkt())
                    file.close()
                layer = QgsVectorLayer(shapeFilePath, layerName, "ogr")
                if epsg:
                    layer.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))
                if addToCanvas:
                    if stylePath:
                        layer.loadNamedStyle(stylePath)
                    self.addLayerToCanvas(layer, groupName)
            return layer
        except Exception as e:
            QMessageBox.warning(None, "Error Loading Shape File", u"{0}".format(e))
            return None

    def shapeFileHasCrs(self, shapeFilePath):
        shpDriver = ogr.GetDriverByName('ESRI Shapefile')
        dataSource = shpDriver.Open(shapeFilePath, 0)
        if dataSource:
            spatialRef = dataSource.GetLayer().GetSpatialRef()
            if spatialRef:
                return True
            else:
                return False
        else:
            return False

    def rasterFileHasCrs(self, rasterFilePath):
        dataSource = gdal.Open(rasterFilePath, GA_Update)
        if dataSource:
            QgsMessageLog.logMessage(f"GetSpatialRef: {dataSource.GetSpatialRef()}, GetProjection: {dataSource.GetProjection()}", tag="APIS", level=Qgis.Info)
            return True
        else:
            return False

    def findshapeFileLayerInTree(self, layerUri):
        for treeLayer in self.tocRoot.findLayers():
            if treeLayer.layer().type() == 0:  # 0 ... VectorLayer
                dSU = treeLayer.layer().dataProvider().dataSourceUri()
                if os.path.normpath(dSU[:dSU.find(u"|")]) == os.path.normpath(layerUri):
                    return treeLayer.layer()
        return None

    def findspatialiteLayerInTree(self, databaseUri, tableName):
        for treeLayer in self.tocRoot.findLayers():
            if treeLayer.layer().type() == 0:  # 0 ... VectorLayer
                dSU = treeLayer.layer().dataProvider().dataSourceUri()
                prfxDatabase = "dbname='"
                ext = ".sqlite"
                prfxTable = "table=\""
                sufxTable = "\" ("
                dSU_databaseUri = dSU[dSU.find(prfxDatabase) + len(prfxDatabase):dSU.find(ext) + len(ext)]
                dSU_tableName = dSU[dSU.find(prfxTable) + len(prfxTable):dSU.find(sufxTable)]
                # QMessageBox.information(None, "Sources", u"{0}, {1}".format(os.path.normpath(dbPath), os.path.normpath(self.dbm.db.databaseName())))
                #if os.path.normpath(dSU[:dSU.find(u"|")]) == os.path.normpath(layerUri):
                if os.path.normpath(dSU_databaseUri) == os.path.normpath(databaseUri) and dSU_tableName == tableName:
                    return treeLayer.layer()
        return None

    def getSpatialiteLayer(self, layerName, subsetString=None, displayName=None):
        if not displayName:
            displayName = layerName
        uri = QgsDataSourceUri()
        uri.setDatabase(self.dbm.db.databaseName())
        uri.setDataSource('', layerName, 'geometry')
        layer = QgsVectorLayer(uri.uri(), displayName, 'spatialite')
        if subsetString:
            layer.setSubsetString(subsetString)
        return layer

    def getStylesDir(self):
        return self.stylesDir

    def selectFeaturesByExpression(self, layer, expression):
        layer.selectByExpression(expression)

    def zoomToExtent(self, bbox):
        self.iface.mapCanvas().setExtent(bbox)
        self.iface.mapCanvas().refresh()

    def zoomToSelection(self, layer):
        if layer.selectedFeatureCount() > 0:
            bbox = layer.boundingBoxOfSelected()
            bbox.scale(1.1)
            transform = QgsCoordinateTransform(layer.crs(), self.iface.mapCanvas().mapSettings().destinationCrs(), QgsProject.instance())
            self.zoomToExtent(transform.transformBoundingBox(bbox))

    def zoomToSelections(self, layers):
        xMin = []
        yMin = []
        xMax = []
        yMax = []
        for layer in layers:
            if layer.selectedFeatureCount() > 0:
                bbox = layer.boundingBoxOfSelected()
                bbox.scale(1.1)
                transform = QgsCoordinateTransform(layer.crs(), self.iface.mapCanvas().mapSettings().destinationCrs(),
                                                   QgsProject.instance())
                bboxT = transform.transformBoundingBox(bbox)
                xMin.append(bboxT.xMinimum())
                yMin.append(bboxT.yMinimum())
                xMax.append(bboxT.xMaximum())
                yMax.append(bboxT.yMaximum())
        if xMin and yMin and xMax and yMax:
            self.zoomToExtent(QgsRectangle(min(xMin), min(yMin), max(xMax), max(yMax)))
        else:
            return False

    def exportLayerAsShp(self, layer, time, name="Apis_Export", groupName="Temp", styleName=None, parent=None):
        # check if layer has features to be exported
        if layer.hasFeatures():
            # get previous directory
            saveDir = self.settings.value("APIS/working_dir", QDir.home().dirName())
            # save file dialog
            layerName = QFileDialog.getSaveFileName(parent, u"SHP Datei Export Speichern", saveDir + "\\" + "{0}_{1}".format(name, time), "*.shp")[0]

            if layerName:
                check = QFile(layerName)
                if check.exists():
                    if not QgsVectorFileWriter.deleteShapeFile(layerName):
                        QMessageBox.warning(parent, "SHP Datei Export", u"Es ist nicht möglich die SHP Datei {0} zu überschreiben!".format(layerName))
                        return

                error = QgsVectorFileWriter.writeAsVectorFormat(layer, layerName, "UTF-8", layer.crs(), "ESRI Shapefile")
                if error[0] == QgsVectorFileWriter.NoError:
                    fof = FileOrFolder(parent=parent)
                    if fof == 0 or fof == 2:
                        # Shp Datei in QGIS laden
                        if styleName:
                            stylePath = self.stylesDir + self.__layers[styleName]["style"]
                        self.requestShapeFile(layerName, groupName=groupName, addToCanvas=True, stylePath=stylePath)
                    if fof == 1 or fof == 2:
                        # Ordner öffnen
                        OpenFileOrFolder(os.path.split(layerName)[0])
                else:
                    QMessageBox.warning(parent, "SHP Datei Export", u"Beim erstellen der SHP Datei ist ein Fehler aufgetreten: {0}".format(error))
        else:
            QMessageBox.warning(parent, "SHP Datei Export", u"Der zu exportierende Layer ({0}) hat keine Features.".format(layer.name()))
            return

    def mergeLayers(self, layers, name="Merged", parent=None):
        # check if Geom type is the same for all and if crs is the same for all
        crs = layers[0].sourceCrs()
        wkbType = layers[0].wkbType()
        for layer in layers:
            if not layer.sourceCrs() == crs:
                QMessageBox.warning(parent, "Merge Layers", "Zumindest einer der Layer hat ein anderes Referenz System.")
                return None
            if not layer.wkbType() == wkbType:
                QMessageBox.warning(parent, "Merge Layers", "Zumindest einer der Layer hat eine andere Geometrie.")
                return None
        feats = []
        fieldsList = []
        for layer in layers:
            fieldsList.append(layer.fields().toList())
            for feat in layer.getFeatures():
                geom = feat.geometry()
                attrs = feat.attributes()
                feature = QgsFeature()
                feature.setGeometry(geom)
                feature.setAttributes(attrs)
                feats.append(feature)

        # Create the merged layer by checking the geometry type of  the input files (for other types, please see the API documentation)
        if layer.wkbType() == QgsWkbTypes.Point:
            vLayer = QgsVectorLayer('Point?crs=' + crs.toWkt(), name, "memory")
        if layer.wkbType() == QgsWkbTypes.LineString:
            vLayer = QgsVectorLayer('LineString?crs=' + crs.toWkt(), name, "memory")
        if layer.wkbType() == QgsWkbTypes.Polygon:
            vLayer = QgsVectorLayer('Polygon?crs=' + crs.toWkt(), name, "memory")

        finalFieldList = []
        for fields in fieldsList:
            for f in fields:
                if not self._fieldInFields(f, finalFieldList):
                    finalFieldList.append(f)
        # Add the features to the merged layer
        prov = vLayer.dataProvider()
        prov.addAttributes(finalFieldList)
        vLayer.updateFields()
        vLayer.startEditing()
        prov.addFeatures(feats)
        vLayer.commitChanges()

        return vLayer

    def _fieldInFields(self, field, fieldList):
        for f in fieldList:
            if field == f:
                return True
        return False

    def generateCenterPointMemoryLayer(self, polygonLayer, displayName=None):
        if not displayName:
            displayName = polygonLayer.name()
        epsg = polygonLayer.crs().authid()
        # QMessageBox.warning(None, "EPSG", u"{0}".format(epsg))
        layer = QgsVectorLayer("Point?crs={0}".format(epsg), displayName, "memory")
        layer.setCrs(polygonLayer.crs())
        provider = layer.dataProvider()
        provider.addAttributes(polygonLayer.dataProvider().fields())
        layer.updateFields()
        pointFeatures = []
        for polygonFeature in polygonLayer.getFeatures():
            polygonGeom = polygonFeature.geometry()
            pointGeom = polygonGeom.centroid()
            # if center point is not on polygon get the nearest Point
            if not polygonGeom.contains(pointGeom):
                pointGeom = polygonGeom.pointOnSurface()
            pointFeature = QgsFeature()
            pointFeature.setGeometry(pointGeom)
            pointFeature.setAttributes(polygonFeature.attributes())
            pointFeatures.append(pointFeature)
        provider.addFeatures(pointFeatures)
        layer.updateExtents()
        return layer

    def createMemoryLayer(self, layer, layerName=None):
        if layer.hasFeatures:
            feats = []
            fields = layer.fields().toList()
            for feat in layer.getFeatures():
                geom = feat.geometry()
                attrs = feat.attributes()
                feature = QgsFeature()
                feature.setGeometry(geom)
                feature.setAttributes(attrs)
                feats.append(feature)

            if layerName is None:
                layerName = layer.name()

            if layer.wkbType() == QgsWkbTypes.Point:
                vLayer = QgsVectorLayer('Point?crs=' + layer.sourceCrs().toWkt(), layerName, "memory")
            if layer.wkbType() == QgsWkbTypes.LineString:
                vLayer = QgsVectorLayer('LineString?crs=' + layer.sourceCrs().toWkt(), layerName, "memory")
            if layer.wkbType() == QgsWkbTypes.Polygon:
                vLayer = QgsVectorLayer('Polygon?crs=' + layer.sourceCrs().toWkt(), layerName, "memory")

            prov = vLayer.dataProvider()
            prov.addAttributes(fields)
            vLayer.updateFields()
            vLayer.startEditing()
            prov.addFeatures(feats)
            vLayer.commitChanges()

            return vLayer
        else:
            return None

    def getStylePath(self, style):
        return self.stylesDir + self.__layers[style]["style"]

    def removeLayerGroupIfEmpty(self, groupName):
        group = self.tocRoot.findGroup(groupName)
        if group:
            count = len(group.findLayers())
            if count == 0:
                self.tocRoot.removeChildNode(group)
