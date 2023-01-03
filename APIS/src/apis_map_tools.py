# -*- coding: utf-8 -*
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from qgis.core import (
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsPointXY,
    QgsWkbTypes,
    QgsProject
)
from qgis.gui import QgsMapTool, QgsRubberBand, QgsVertexMarker

import math


class APISMapToolMixin():

    def setDiagonal(self, diagonal):
        self.diagonal = diagonal
    # def setLayer(self, pointLayer, polygonLayer):
    #     self.pointLayer = pointLayer
    #     self.polygonLayer = polygonLayer
    #     self.layer = pointLayer

    def transformCoordinates(self, screenPt):
        # return (self.toMapCoordinates(screenPt), self.toLayerCoordinates(self.layer, screenPt))
        return self.toMapCoordinates(screenPt)

    def calculateSquare(self, point):
        '''
        point in layer coordinates(QgsPoint)
        '''
        mapCrs = self.canvas.mapSettings().destinationCrs()
        utmCrs = QgsCoordinateReferenceSystem()
        utmCrs.createFromProj4(self.proj4Utm(point))
        ctFwd = QgsCoordinateTransform(mapCrs, utmCrs, QgsProject.instance())
        ctBwd = QgsCoordinateTransform(utmCrs, mapCrs, QgsProject.instance())

        pointGeom = QgsGeometry.fromPointXY(point)
        pointGeom.transform(ctFwd)
        pointUtm = QgsPointXY(pointGeom.asPoint())

        # calculate d
        d = self.diagonal / (2 * (2**0.5))

        left = pointUtm.x() - d
        bottom = pointUtm.y() - d
        right = pointUtm.x() + d
        top = pointUtm.y() + d

        p1 = QgsGeometry.fromPointXY(QgsPointXY(left, bottom))
        p2 = QgsGeometry.fromPointXY(QgsPointXY(right, bottom))
        p3 = QgsGeometry.fromPointXY(QgsPointXY(right, top))
        p4 = QgsGeometry.fromPointXY(QgsPointXY(left, top))

        p1.transform(ctBwd)
        p2.transform(ctBwd)
        p3.transform(ctBwd)
        p4.transform(ctBwd)

        mapPol = [p1.asPoint(), p2.asPoint(), p3.asPoint(), p4.asPoint(), p1.asPoint()]

        return mapPol

    def proj4Utm(self, p):

        mapCrs = self.canvas.mapSettings().destinationCrs()
        if not mapCrs.isGeographic():
            # if not geographic transform it to a geographic crs
            geographicCrs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
            ct = QgsCoordinateTransform(mapCrs, geographicCrs, QgsProject.instance())
            p = ct.transform(p)

        x = p.x()
        y = p.y()
        z = math.floor((x + 180) / 6) + 1

        if y >= 56.0 and y < 64.0 and x >= 3.0 and x < 12.0:
            z = 32

        # Special zones for Svalbard
        if y >= 72.0 and y < 84.0:
            if y >= 0.0 and y < 9.0:
                z = 31
            elif y >= 9.0 and y < 21.0:
                z = 33
            elif y >= 21.0 and y < 33.0:
                z = 35
            elif y >= 33.0 and y < 42.0:
                z = 37

        return "+proj=utm +zone={0} +datum=WGS84 +units=m +no_defs".format(int(z))


class APISMapToolEmitPointAndSquare(QgsMapTool, APISMapToolMixin):

    # when mapping finished signal emitted that carries the Point and a Polygon Geometry (in Map Coordinates)
    mappingFinished = pyqtSignal(QgsGeometry, QgsGeometry, QgsCoordinateReferenceSystem)

    def __init__(self, canvas, diagonal=200):
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.vertexMarker = None
        self.rubberBand = None
        self.capturedPoint = None
        self.derivedPolygon = []
        self.capturing = False
        # self.setLayers(pointLayer, polygonLayer)
        self.setDiagonal(diagonal)
        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.capturing:
                self.startCapturing()
            self.setVertex(event.pos())
        elif event.button() == Qt.RightButton:
            point = self.getCapturedPoint()
            polygon = self.getDerivedPolygon()
            self.stopCapturing()
            if point is not None and polygon is not None:
                self.mappingFinished.emit(self.getPointGeometry(point), self.getPolygonGeometry(polygon), self.canvas.mapSettings().destinationCrs())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
            # self.removeLastVertex()
            event.ignore()
        if event.key() == Qt.Key_Escape:
            self.stopCapturing()
            self.clearScene()
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            point = self.getCapturedPoint()
            polygon = self.getDerivedPolygon()
            self.stopCapturing()
            if point is not None and polygon is not None:
                self.mappingFinished.emit(self.getPointGeometry(point), self.getPolygonGeometry(polygon), self.canvas.mapSettings().destinationCrs())

    def startCapturing(self):
        self.clearScene()

        self.vertexMarker = QgsVertexMarker(self.canvas)
        self.vertexMarker.setIconType(1)
        self.vertexMarker.setColor(QColor(220, 0, 0))
        self.vertexMarker.setIconSize(16)
        self.vertexMarker.setPenWidth(3)
        self.vertexMarker.show()

        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setWidth(2)
        self.rubberBand.setFillColor(QColor(220, 0, 0, 120))
        self.rubberBand.setStrokeColor(QColor(220, 0, 0))
        self.rubberBand.setLineStyle(Qt.DotLine)
        self.rubberBand.show()

        self.capturing = True

    def clearScene(self):
        if self.vertexMarker:
            self.canvas.scene().removeItem(self.vertexMarker)
            self.vertexMarker = None
        if self.rubberBand:
            self.canvas.scene().removeItem(self.rubberBand)
            self.rubberBand = None

    def stopCapturing(self):
        self.capturing = False
        self.capturedPoint = None
        self.derivedPolygon = []
        self.canvas.refresh()

    def setVertex(self, canvasPoint):
        mapPt = self.transformCoordinates(canvasPoint)

        # set/update vertexMarker Position
        self.vertexMarker.setCenter(mapPt)
        self.capturedPoint = mapPt

        # update rubberBand
        self.updateRubberBand()

    def updateRubberBand(self):
        if self.capturedPoint and self.rubberBand:

            # calculate Points
            self.derivedPolygon = self.calculateSquare(self.capturedPoint)

            self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
            for mapPt in self.derivedPolygon:
                self.rubberBand.addPoint(mapPt)

    def getCapturedPoint(self):
        point = self.capturedPoint

        if point is None:
            return None
        else:
            return point

    def getDerivedPolygon(self):
        polygon = self.derivedPolygon

        if polygon is None:
            return None
        else:
            return polygon

    def getPointGeometry(self, geom):
        return QgsGeometry.fromPointXY(geom)

    def getPolygonGeometry(self, geom):
        return QgsGeometry.fromPolygonXY([geom])

    def updateDiagonal(self, diagonal):
        self.setDiagonal(diagonal)
        # update Rubberband
        self.updateRubberBand()


class APISMapToolEmitPolygonAndPoint(QgsMapTool, APISMapToolMixin):

    mappingFinished = pyqtSignal(QgsGeometry, QgsGeometry, QgsCoordinateReferenceSystem)

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.rubberBand = None
        self.tempRubberBand = None
        self.vertexMarker = None
        self.capturedPoints = []
        self.derivedPoint = None
        self.capturing = False
        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.capturing:
                self.startCapturing()
            self.addVertex(event.pos())
        elif event.button() == Qt.RightButton:
            point = self.getDerivedPoint()
            polygon = self.getCapturedPolygon()
            self.stopCapturing()
            if point is not None and polygon is not None:
                pointGeom = self.getPointGeometry(point)
                polygonGeom = self.getPolygonGeometry(polygon)
                if pointGeom is not None and polygonGeom is not None:
                    self.mappingFinished.emit(pointGeom, polygonGeom, self.canvas.mapSettings().destinationCrs())
                else:
                    self.clearScene()
            else:
                self.clearScene()

    def canvasMoveEvent(self, event):
        if self.tempRubberBand is not None and self.capturing:
            mapPt = self.transformCoordinates(event.pos())
            self.tempRubberBand.movePoint(mapPt)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
            self.removeLastVertex()
            event.ignore()
        if event.key() == Qt.Key_Escape:
            self.stopCapturing()
            self.clearScene()
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            point = self.getDerivedPoint()
            polygon = self.getCapturedPolygon()
            self.stopCapturing()
            if point is not None and polygon is not None:
                pointGeom = self.getPointGeometry(point)
                polygonGeom = self.getPolygonGeometry(polygon)
                if pointGeom is not None and polygonGeom is not None:
                    self.mappingFinished.emit(pointGeom, polygonGeom, self.canvas.mapSettings().destinationCrs())
                else:
                    self.clearScene()
            else:
                self.clearScene()

    def startCapturing(self):
        self.clearScene()

        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setWidth(2)
        self.rubberBand.setFillColor(QColor(220, 0, 0, 120))
        self.rubberBand.setStrokeColor(QColor(220, 0, 0))
        self.rubberBand.setLineStyle(Qt.DotLine)
        self.rubberBand.show()

        self.tempRubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.tempRubberBand.setWidth(2)
        self.tempRubberBand.setFillColor(QColor(0, 0, 0, 0))
        self.tempRubberBand.setStrokeColor(QColor(220, 0, 0))
        self.tempRubberBand.setLineStyle(Qt.DotLine)
        self.tempRubberBand.show()

        self.vertexMarker = QgsVertexMarker(self.canvas)
        self.vertexMarker.setIconType(1)
        self.vertexMarker.setColor(QColor(220, 0, 0))
        self.vertexMarker.setIconSize(16)
        self.vertexMarker.setPenWidth(3)
        self.vertexMarker.show()

        self.capturing = True

    def clearScene(self):
        if self.vertexMarker:
            self.canvas.scene().removeItem(self.vertexMarker)
            self.vertexMarker = None
        if self.rubberBand:
            self.canvas.scene().removeItem(self.rubberBand)
            self.rubberBand = None
        if self.tempRubberBand:
            self.canvas.scene().removeItem(self.tempRubberBand)
            self.tempRubberBand = None

    def stopCapturing(self):
        if self.vertexMarker and self.rubberBand and self.rubberBand.numberOfVertices() < 3:
            self.canvas.scene().removeItem(self.vertexMarker)
            self.vertexMarker = None
        if self.rubberBand and self.rubberBand.numberOfVertices() < 3:
            self.canvas.scene().removeItem(self.rubberBand)
            self.rubberBand = None
        if self.tempRubberBand:
            self.canvas.scene().removeItem(self.tempRubberBand)
            self.tempRubberBand = None
        self.capturing = False
        self.capturedPoints = []
        self.derivedPoint = None
        self.canvas.refresh()

    def addVertex(self, canvasPoint):
        mapPt = self.transformCoordinates(canvasPoint)

        self.rubberBand.addPoint(mapPt)
        self.capturedPoints.append(mapPt)

        bandSize = self.rubberBand.numberOfVertices()
        if bandSize > 2:

            rubGeom = self.rubberBand.asGeometry()
            cpGeom = rubGeom.centroid()
            if not rubGeom.contains(cpGeom):
                cpGeom = rubGeom.pointOnSurface()
            # nearestCp = rubGeom.nearestPoint(cpGeom)
            self.vertexMarker.setCenter(cpGeom.asPoint())
            self.derivedPoint = cpGeom.asPoint()
            self.vertexMarker.show()

        self.tempRubberBand.reset(QgsWkbTypes.PolygonGeometry)
        firstPoint = self.rubberBand.getPoint(0, 0)
        self.tempRubberBand.addPoint(firstPoint)
        self.tempRubberBand.movePoint(mapPt)
        self.tempRubberBand.addPoint(mapPt)

    def removeLastVertex(self):
        if not self.capturing:
            return

        bandSize = self.rubberBand.numberOfVertices()
        tempBandSize = self.tempRubberBand.numberOfVertices()
        numPoints = len(self.capturedPoints)

        if bandSize < 1 or numPoints < 1:
            return

        self.rubberBand.removePoint(-1)

        if bandSize > 1:
            if tempBandSize > 1:
                point = self.rubberBand.getPoint(0, bandSize - 2)
                self.tempRubberBand.movePoint(tempBandSize - 2, point)
        else:
            self.tempRubberBand.reset(QgsWkbTypes.PolygonGeometry)

        bandSize = self.rubberBand.numberOfVertices()
        if bandSize < 3:
            self.vertexMarker.hide()
        else:
            rubGeom = self.rubberBand.asGeometry()
            cpGeom = rubGeom.centroid()
            if not rubGeom.contains(cpGeom):
                cpGeom = rubGeom.pointOnSurface()
            # nearestCp = rubGeom.nearestPoint(cpGeom)
            self.vertexMarker.setCenter(cpGeom.asPoint())
            self.derivedPoint = cpGeom.asPoint()
            self.vertexMarker.show()

        del self.capturedPoints[-1]

    def getCapturedPolygon(self):
        polygon = self.capturedPoints

        if len(polygon) < 3:
            return None
        else:
            return polygon

    def getDerivedPoint(self):
        point = self.derivedPoint

        if point is None:
            return None
        else:
            return point

    def getPointGeometry(self, geom):
        p = QgsGeometry.fromPointXY(geom)
        if p.isGeosValid() and not p.isEmpty():
            return p
        else:
            return None

    def getPolygonGeometry(self, geom):
        p = QgsGeometry.fromPolygonXY([geom])
        if p.isGeosValid() and not p.isEmpty():
            return p
        else:
            return None
