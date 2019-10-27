# -*- coding: utf-8 -*

import traceback

from PyQt5.QtCore import pyqtSignal, QObject, Qt, QThread
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QProgressBar, QPushButton, QMessageBox
from PyQt5.QtSql import QSqlQuery

from qgis.core import (QgsProject, QgsApplication, Qgis, QgsGeometry, QgsPointXY, QgsRectangle, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsMessageLog, QgsWkbTypes)
from qgis.gui import (QgsMapToolEmitPoint, QgsRubberBand)

from APIS.src.apis_image_selection_list import APISImageSelectionList
from APIS.src.apis_site_selection_list import APISSiteSelectionList
from APIS.src.apis_findspot_selection_list import APISFindspotSelectionList


class RectangleMapTool(QgsMapToolEmitPoint):
    def __init__(self, iface, dbm, imageRegistry, apisLayer):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.dbm = dbm
        self.imageRegistry = imageRegistry
        self.apisLayer = apisLayer

        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setColor(QColor(255, 128, 0, 255))
        self.rubberBand.setFillColor(QColor(255, 128, 0, 128))
        self.rubberBand.setWidth(1)

        self.topic = 'image'  # 'image', 'site', 'findspot'

        self.reset()

        self.imageSelectionListDlg = APISImageSelectionList(self.iface, self.dbm, self.imageRegistry, self.apisLayer, parent=self.iface.mainWindow())
        self.siteSelectionListDlg = APISSiteSelectionList(self.iface, self.dbm, self.imageRegistry, self.apisLayer, parent=self.iface.mainWindow())
        self.findspotSelectionListDlg = APISFindspotSelectionList(self.iface, self.dbm, self.imageRegistry, self.apisLayer, parent=self.iface.mainWindow())

        self.worker = None

    def setTopic(self, topic):
        self.topic = topic

    def deactivate(self):
        super(RectangleMapTool, self).deactivate()
        self.deactivated.emit()

    def activate(self):
        self.canvas.setCursor(QgsApplication.getThemeCursor(QgsApplication.Cursor.Select))

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        r = self.rectangle()

        #QMessageBox.warning(None, "Bild", u"Punkt: {0}".format(epsg))

        srcCrs = self.canvas.mapSettings().destinationCrs()
        destCrs = QgsCoordinateReferenceSystem(4312, QgsCoordinateReferenceSystem.EpsgCrsId)
        ct = QgsCoordinateTransform(srcCrs, destCrs, QgsProject.instance())
        if r is None:
            #QMessageBox.warning(None, "Bild", u"Punkt: {0}".format(self.endPoint.wellKnownText()))

            p = QgsGeometry.fromPointXY(self.endPoint)
            p.transform(ct)
            #QMessageBox.warning(None, "Bild", u"Punkt: {0}".format(self.endPoint.x()))
            #self.openImageSelectionListDialogByLocation(p.asWkt(8))
            self.startWorker(p.asWkt(8))

        else:
            #.warning(None, "Bild", u"Rechteck: {0}, {1}, {2}, {3}".format(r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum()))

            r2 = QgsGeometry.fromRect(r)
            r2.transform(ct)
            #QMessageBox.warning(None, "Bild", u"Polygon: {0}".format(r2.asoWkt(8)))
            #self.openImageSelectionListDialogByLocation(r2.asoWkt(8))
            self.startWorker(r2.asWkt(8))
            #print "Rectangle:", r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum()

    def openImageSelectionListDialogByLocation(self, query):
        # progressMessageBar = self.iface.messageBar().createMessage("Luftbilder werden gesucht")
        # progress = QProgressBar()
        # progress.setMinimum(0)
        # progress.setMaximum(0)
        # progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        # progressMessageBar.layout().addWidget(progress)
        # self.iface.messageBar().pushWidget(progressMessageBar, self.iface.messageBar().INFO)

        res = self.imageSelectionListDlg.loadImageListBySqlQuery(query)
        if res:
            self.imageSelectionListDlg.show()
            if self.imageSelectionListDlg.exec_():
                pass

        self.rubberBand.hide()

    def openSiteSelectionListDialogByLocation(self, query):
        info = u"gefunden für den ausgewählten Bereich."
        res = self.siteSelectionListDlg.loadSiteListBySpatialQuery(query, info)
        if res:
            self.siteSelectionListDlg.show()
            if self.siteSelectionListDlg.exec_():
                pass

        self.rubberBand.hide()

    def openFindspotSelectionListDialogByLocation(self, query):
        info = u"gefunden für den ausgewählten Bereich."
        res = self.findspotSelectionListDlg.loadFindspotListBySpatialQuery(query, info)
        if res:
            self.findspotSelectionListDlg.show()
            #if self.findspotSelectionListDlg.exec_():
            #    pass

        self.rubberBand.hide()

    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return

        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)

    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return

        point1 = QgsPointXY(startPoint.x(), startPoint.y())
        point2 = QgsPointXY(startPoint.x(), endPoint.y())
        point3 = QgsPointXY(endPoint.x(), endPoint.y())
        point4 = QgsPointXY(endPoint.x(), startPoint.y())

        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        self.rubberBand.addPoint(point4, True)    # true to update canvas
        self.rubberBand.show()

    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None

        return QgsRectangle(self.startPoint, self.endPoint)



    def startWorker(self, geometry):
        # create a new worker instance

        if self.worker is None:

            worker = Worker(self.dbm, geometry, self.topic)

            # configure the QgsMessageBar
            messageBar = self.iface.messageBar().createMessage(u'Räumliche Suche wird durchgeführt ...', )
            progressBar = QProgressBar()
            progressBar.setMinimum(0)
            progressBar.setMaximum(0)
            progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            cancelButton = QPushButton()
            cancelButton.setText('Cancel')
            cancelButton.clicked.connect(self.killWorker)
            messageBar.layout().addWidget(progressBar)
            self.progressBar = progressBar
            messageBar.layout().addWidget(cancelButton)
            self.iface.messageBar().pushWidget(messageBar, Qgis.MessageLevel.Info)
            self.messageBar = messageBar

            # start the worker in a new thread
            thread = QThread(self)
            worker.moveToThread(thread)
            worker.finished.connect(self.workerFinished)
            worker.error.connect(self.workerError)
            #worker.progress.connect(progressBar.setValue)
            thread.started.connect(worker.run)
            thread.start()
            self.thread = thread
            self.worker = worker

    def killWorker(self):
        self.worker.kill()
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(100)

    def workerFinished(self, query, topic):
        # clean up the worker and thread
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        # remove widget from message bar
        self.iface.messageBar().popWidget(self.messageBar)
        if query is not None:
            # report the result
            #query = result
            if not self.worker.killed:
                if topic == 'image':
                    self.openImageSelectionListDialogByLocation(query)
                elif topic == 'site':
                    self.openSiteSelectionListDialogByLocation(query)
                elif topic == 'findspot':
                    self.openFindspotSelectionListDialogByLocation(query)
            else:
                self.rubberBand.hide()
            #self.iface.messageBar().pushMessage('Result')
        else:
            # notify the user that something went wrong
            self.iface.messageBar().pushMessage('Something went wrong! See the message log for more information.', level=Qgis.MessageLevel.Critical, duration=3)

        self.worker = None

    def workerError(self, e, exception_string):
        QgsMessageLog.logMessage('Worker thread raised an exception:\n'.format(exception_string), level=Qgis.MessageLevel.Critical)


class Worker(QObject):

    finished = pyqtSignal(object, str)
    error = pyqtSignal(Exception, str)

    '''Example worker for calculating the total area of all features in a layer'''
    def __init__(self, dbm, geometry, topic):
        QObject.__init__(self)
        self.dbm = dbm
        self.killed = False
        self.geometryWkt = geometry
        self.topic = topic

    def run(self):
        query = None
        try:
            epsg = 4312
            query = QSqlQuery(self.dbm.db)
            if self.topic == 'image':
                query.prepare("SELECT cp.bildnummer AS bildnummer, cp.filmnummer AS filmnummer, cp.radius AS mst_radius, f.weise AS weise, f.art_ausarbeitung AS art FROM film AS f, luftbild_schraeg_cp AS cp WHERE f.filmnummer = cp.filmnummer AND cp.bildnummer IN (SELECT fp.bildnummer FROM luftbild_schraeg_fp AS fp WHERE NOT IsEmpty(fp.geometry) AND Intersects(GeomFromText('{0}',{1}), fp.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_schraeg_fp' AND search_frame = GeomFromText('{0}',{1}) )) UNION ALL SELECT  cp_s.bildnummer AS bildnummer, cp_S.filmnummer AS filmnummer, cp_s.massstab, f_s.weise, f_s.art_ausarbeitung FROM film AS f_s, luftbild_senk_cp AS cp_s WHERE f_s.filmnummer = cp_s.filmnummer AND cp_s.bildnummer IN (SELECT fp_s.bildnummer FROM luftbild_senk_fp AS fp_s WHERE NOT IsEmpty(fp_s.geometry) AND Intersects(GeomFromText('{0}',{1}), fp_s.geometry) AND rowid IN (SELECT rowid FROM SpatialIndex WHERE f_table_name = 'luftbild_senk_fp' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY filmnummer, bildnummer".format(self.geometryWkt, epsg))
            elif self.topic == 'site':
                query.prepare("SELECT fundortnummer, flurname, katastralgemeinde, fundgewinnung, sicherheit FROM fundort WHERE fundortnummer IN (SELECT DISTINCT fo.fundortnummer FROM fundort fo WHERE NOT IsEmpty(fo.geometry) AND NOT IsEmpty(GeomFromText('{0}',{1})) AND Intersects(GeomFromText('{0}',{1}), fo.geometry) AND fo.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundort' AND search_frame = GeomFromText('{0}',{1}) ) ) ORDER BY katastralgemeindenummer, land, fundortnummer_nn".format(self.geometryWkt, epsg))
            elif self.topic == 'findspot':
                query.prepare("SELECT fs.fundortnummer, fs.fundstellenummer, fo.katastralgemeinde, datierung_zeitstufe, datierung_periode, datierung_periode_detail, befundart, befundart_detail, fs.sicherheit, kultur FROM fundstelle fs, fundort fo WHERE fs.fundortnummer = fo.fundortnummer AND (fs.fundortnummer || '.' || fs.fundstellenummer) IN (SELECT DISTINCT (fst.fundortnummer || '.' || fst.fundstellenummer) AS fsn FROM fundstelle fst WHERE NOT IsEmpty(fst.geometry) AND NOT IsEmpty(GeomFromText('{0}',{1})) AND Intersects(GeomFromText('{0}', {1}), fst.geometry) AND fst.ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'fundstelle' AND search_frame = GeomFromText('{0}', {1}))) ORDER BY fo.katastralgemeindenummer, fo.land, fo.fundortnummer_nn, fs.fundstellenummer".format(self.geometryWkt, epsg))
                #self.kill()
            query.exec_()
        except Exception as e:
            # forward the exception upstream
            self.error.emit(e, traceback.format_exc())
        finally:
            self.finished.emit(query, self.topic)

    def kill(self):
        self.killed = True


