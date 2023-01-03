#!/usr/bin/env python
import os

from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QImage
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsItem, QMessageBox, QGraphicsView, QGraphicsScene, QDialog, QProgressBar, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QSize, QObject, QMutex, QMutexLocker, QThread

from APIS.src.apis_utils import OpenFileOrFolder, GetWindowSize, GetWindowPos, SetWindowSizeAndPos


class QdGraphicsPixmapItem(QGraphicsPixmapItem):

    def __init__(self, path, size, parent=None):
        QGraphicsPixmapItem.__init__(self, parent)
        self._path = path
        self._loaded = False

        self._text = QGraphicsTextItem(self)
        self._text.setFont(QFont("Arial", 14))
        self._text.setPlainText(os.path.basename(path))
        self._text.setPos(0, size.height())

        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setFlags(self.flags() | QGraphicsItem.ItemIsSelectable)  # | QtGui.QGraphicsItem.ItemIsMovable )

    def setImage(self, image):
        self.setPixmap(QPixmap.fromImage(image))
        self._text.setPos(0, self.boundingRect().height())
        self._loaded = True

    def setPlainText(self, text):
        self._text.setPlainText(text)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.viewImage()
            #scene = self.scene()
            #scene.emit(SIGNAL("doubleClicked(QString)"), self._path)
            #scene.doubleClicked.emit(self._path)
        QGraphicsPixmapItem.mouseDoubleClickEvent(self, event)

    def viewImage(self):
        if os.path.isfile(self._path):
            OpenFileOrFolder(self._path)

        else:
            QMessageBox.warning(self, "Bild", u"Bild unter {0} nicht vorhanden".format(self._path))


class QdThumbnailView(QGraphicsView):

    loading = pyqtSignal(int)
    doubleClicked = pyqtSignal(str)

    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        self._scene = QGraphicsScene()
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        #self.connect(self._scene, SIGNAL('doubleClicked(QString)'), self._itemDoubleClicked)
        #self._scene.doubleClicked.connect(self._itemDoubleClicked)
        self._pixmaps = {}

        self._scale = 0.45

        self._width = 450
        self._height = 450

        self.scale(self._scale, self._scale)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        imageOptions = QdImageOptions()
        imageOptions.setSize(self._width, self._height)

        self._loader = QdImageLoader(imageOptions, self, parent)

        self._loader.imageLoaded.connect(self.imageLoaded)
        self._loader.loadFinished.connect(self.finished)

        self._imagesPerRow = 5

    #def stopLoading(self):
        #self._loader.stopLoading()

    def load(self, images, positionedImages={}):
        self._scene.clear()
        self._pixmaps = {}

        from PyQt5.QtSvg import QSvgRenderer
        standardPixmapsvg = QSvgRenderer(self)
        standardPixmapsvg.setViewBox(QRect(0, 0, self._width, self._height))
        standardPixmapsvg.load("/usr/share/icons/gnome-human/scalable/status/image-loading.svg")
        self.standardPixmap = QPixmap(self._width, self._height)

        painter = QPainter(self.standardPixmap)
        painter.fillRect(QRect(0, 0, self._width, self._height), QBrush(self.palette().color(self.backgroundRole())))
        standardPixmapsvg.render(painter)

        imagesToLoad = images
        if positionedImages:
            imagesToLoad = positionedImages.keys()

        maxX = maxY = minX = minY = 0

        total = len(imagesToLoad)
        current = 0
        row = 0
        for path in images:
            #QtGui.QMessageBox.warning(None, "Bild", u"{0}".format(path))
            dirname  = os.path.dirname(path)
            basename = os.path.basename(path)
            if os.path.isdir(path) or os.path.basename(path).startswith('.'):
                continue

            cachePath = os.path.join(dirname, ".thumbnails/" + basename)
            if os.path.exists(cachePath) and os.stat(cachePath).st_mtime > os.stat(path):
                print('cache hit')
                imagePath = cachePath

            item = QdGraphicsPixmapItem(path, QSize(self._width, self._height))
            if positionedImages and path in positionedImages:
                x, y = positionedImages[path]
            else:
                modresult = current % self._imagesPerRow
                padding = 10
                if modresult == 0:
                    if current > 0:
                        row += 1
                    x = padding
                else:
                    x = padding + modresult * (self._width + padding)
                y = self._height * row
            current += 1
            minX = min(minX, x)
            minY = min(minY, y)
            maxX = max(maxX, x)
            maxY = max(maxY, y)

            #QtGui.QMessageBox.warning(None, "Bild", u"{0}, {1}, {2}".format(path, x, y))

            item.setPos(x, y)
            item.setPixmap(self.standardPixmap)

            self._pixmaps[path] = item
            self._scene.addItem(item)

        self._progressTotal = current
        self._progressCurrent = 0

        paths = list(self._pixmaps.keys())
        paths.sort()

        # load in background thread(s)
        self._loader.load(paths)
        self.setScene(self._scene)

    def imageCount(self):
        return self._progressTotal

    def imageLoaded(self, path, image):
        self._progressCurrent += 1
        self._pixmaps[str(path)].setImage(image)
        #self.emit(SIGNAL('loading(int)'), self._progressCurrent)
        self.loading.emit(self._progressCurrent)

    def finished(self):
        #self.emit(SIGNAL('loading(int)'), 100)
        self.loading.emit(self._progressCurrent)

    def wheelEvent(self, evt):
        mods = evt.modifiers()
        if mods == Qt.ControlModifier and evt.angleDelta().y() != 0:
            # Most mouse types work in steps of 15 degrees
            # in which case the delta value is a multiple of 120;
            # i.e., 120 units * 1/8 = 15 degrees

            numDegrees = evt.angleDelta().y() / 8
            numSteps = numDegrees / 15
            scaleBy = (5 * numSteps) / 100.0
            # newScale = self._scale + scaleBy
            # QMessageBox.information(None, "degrees", "{0}".format(scaleBy))
            # if newScale > 0.0 and newScale < 5.0:
            #     self.resetMatrix()
            #     self.centerOn(self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos())))
            self.scale(1 + scaleBy, 1 + scaleBy)
            self._scale += scaleBy
            return
        elif mods == Qt.ShiftModifier and self.scene().selectedItems():
            # TODO: scale individual images? show scale controls?
            pass

        QGraphicsView.wheelEvent(self, evt)

    def fitSelected(self):
        rect = None
        items = self.scene().selectedItems()
        for item in items:
            if rect is None:
                rect = item.sceneBoundingRect()
                continue
            rect = rect.united(item.sceneBoundingRect())
        if not rect:
            return
        self.fitInView(rect, Qt.KeepAspectRatio)

    def deleteSelected(self):
        items = self._scene.selectedItems()
        for item in items:
            self.scene().removeItem(item)
            if item._path in self._pixmaps:
                self._pixmaps.pop(item._path)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F:
            self.fitSelected()
        #elif event.key() == Qt.Key_Delete:
        #    self.deleteSelected()
        return QGraphicsView.keyPressEvent(self, event)

    def _itemDoubleClicked(self, path):
        #self.emit(SIGNAL("doubleClicked(QString)"), path)
        self.doubleClicked.emit(path)


class QdImageOptions(QObject):
    def __init__(self):
        QObject.__init__(self, None)
        self._width = 0
        self._height = 0
        self._ratio = Qt.KeepAspectRatio
        self._quality = Qt.SmoothTransformation

    def setSize(self, width, height):
        self._width = width
        self._height = height

    def setAspectRatio(self, aspectRatio):
        self._ratio = aspectRatio

    def setQuality(self, quality):
        self._quality = quality

    def load(self, path):
        image = QImage(path)
        if image.isNull():
            return image
        return image.scaled(self._width, self._height, self._ratio, self._quality)


class QdImageLoader(QObject):
    _mutex = QMutex()
    loadFinished = pyqtSignal()
    imageLoaded = pyqtSignal(str, object)

    def __init__(self, imageOptions=None, parent=None, dialog=None):
        QObject.__init__(self, parent)
        self._imageOptions = imageOptions

        self._threads = []
        for i in range(QThread.idealThreadCount()):
            thread = QdImageLoaderThread(self)
            self._threads.append(thread)
            #self.connect(thread, SIGNAL('loaded(QString, QImage)'), self.loaded)
            thread.loaded.connect(self.loaded)
            #self.connect(thread, SIGNAL('finished()'), self.threadFinished)
            thread.finished.connect(self.threadFinished)
        self._stopped = True

        self._paths = []
        self._index = 0

        #self.connect( dialog, SIGNAL('rejected()'), self.terminateLoading )
        dialog.rejected.connect(self.terminateLoading)

    def threadFinished(self):
        if not self._stopped:
            for thread in self._threads:
                if not thread.isFinished():
                    return
            #self.emit(SIGNAL('loadFinished()'))
            self.loadFinished.emit()

    def load(self, paths):
        self._stopped = False
        self.stopLoading()

        # when this goes out of scope the lock is opened
        locker = QMutexLocker(QdImageLoader._mutex)

        self._paths = paths
        self._index = 0

        for thread in self._threads:
            thread.start(QThread.IdlePriority)

    def imageOptions(self):
        return self._imageOptions

    def consume(self):
        # when this goes out of scope the lock is opened
        locker = QMutexLocker(QdImageLoader._mutex)
        if self._index == len(self._paths):
            return None

        path = self._paths[self._index]
        self._index += 1
        return path

    def loaded(self, path, image):
        if not self._stopped:
            #self.emit(SIGNAL('imageLoaded(QString, QImage)'), path, image)
            self.imageLoaded.emit(path, image)

    def stopLoading(self, emitSignal=False):
        self._stopped = True
        for thread in self._threads:
            thread.wait()
        self._stopped = False

        # when this goes out of scope the lock is opened
        locker = QMutexLocker(QdImageLoader._mutex)
        self._paths = []

        if emitSignal:
            #self.emit(SIGNAL('loadFinished()'))
            self.loadFinished.emit()

    def stopped(self):
        return self._stopped

    def terminateLoading(self):
        self.stopLoading()
        self._stopped = True


class QdImageLoaderThread(QThread):
    loaded = pyqtSignal(str, object)
    finished = pyqtSignal()

    def __init__(self, loader):
        QThread.__init__(self, loader)
        self.setTerminationEnabled(True)
        self._loader = loader
        self._options = self._loader.imageOptions()

    def emitLoaded(self, path, image):
        #self.emit(SIGNAL("loaded(QString, QImage)"), path, image)
        self.loaded.emit(path, image)

    def run(self):
        while not self._loader.stopped():
            path = self._loader.consume()  # path, options
            if not path:
                break

            if self._options:
                self.emitLoaded(path, self._options.load(path))
                self.msleep(10)
                continue

            image = QImage(path)
            self.emitLoaded(path, image)
            self.msleep(10)
        self.finished.emit()


class APISThumbViewer(QDialog):

    #doubleClicked = pyqtSignal(str)

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._iconView = QdThumbnailView(self)
        self._progress = QProgressBar(self)
        self._progress.setFormat("Generating thumbnails: %v of %m")
        self._progress.hide()

        layout.addWidget(self._iconView)
        layout.addWidget(self._progress)

        self._iconView.doubleClicked.connect(self._itemDoubleClicked)
        self._iconView.loading.connect(self.updateProgress)

        self.setWindowTitle("Apis Thumb Viewer")
        self.setModal(True)
        # Initial window size/pos last saved. Use default values for first time
        if GetWindowSize("thumb_viewer"):
            self.resize(GetWindowSize("thumb_viewer"))
        else:
            self.resize(1000, 600)
        if GetWindowPos("thumb_viewer"):
            self.move(GetWindowPos("thumb_viewer"))

        self.rejected.connect(self.onClose)

    def load(self, images, positionedImages={}):
        self._iconView.load(images, positionedImages)
        self._progress.setRange(0, self._iconView.imageCount())

    def updateProgress(self, progress):
        self._progress.setValue(progress)
        if progress == self._iconView.imageCount():
            self._progress.hide()
        elif not self._progress.isVisible():
            self._progress.show()

    def _itemDoubleClicked(self, path):
        #self.emit(SIGNAL('doubleClicked(QString)'), path)
        self.doubleClicked.emit(path)

    def onClose(self):
        SetWindowSizeAndPos("thumb_viewer", self.size(), self.pos())


if __name__ == '__main__':
    import glob

    app = QApplication([])
    widget = APISThumbViewer()
    #images = # list of images you want to view as thumbnails
    filmid = '01850205'
    imagePath = os.path.normpath("C:\\apis\\daten\\luftbild")
    filmPath = os.path.join(imagePath, filmid)
    images = glob.glob(os.path.normpath(filmPath + "\\" + filmid + "_*.*"))
    images.sort()
    widget.load(images)

    widget.resize(1000, 600)
    widget.show()
    app.exec_()
