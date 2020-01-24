# -*- coding: utf-8 -*

from PyQt5.QtCore import QSettings, QDir, Qt, QThread, QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QPushButton, QProgressBar
from qgis.core import QgsMessageLog, Qgis
from qgis.gui import QgsMessageBar

import re, json, os, datetime, sys
import traceback


class ApisImageRegistry(QObject):

    loaded = pyqtSignal(object)

    def __init__(self, pluginDir, iface):

        QObject.__init__(self)

        self.iface = iface
        self.registryFile = pluginDir + "\\" + "apis_image_registry.json" #self.settings.value("APIS/image_registry_file", None)

        # NE ... NoExtension
        self.__imageRegistryNE = None
        self.__hiResRegistryNE = None
        self.__i2cRegistryNE = None
        self.__orthoRegistryNE = None
        self.__mosaicRegistryNE = None
        self.__imageRegistry = None
        self.__hiResRegistry = None
        self.__i2cRegistry = None
        self.__orthoRegistry = None
        self.__mosaicRegistry = None

        self.isLoaded = False
        self.isSetup = False

        self.worker = None

    def setupSettings(self):
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        self.imageDirName = self.settings.value("APIS/image_dir")
        self.orthoDirName = self.settings.value("APIS/ortho_image_dir")
        self.imageDir = QDir(self.imageDirName)
        self.orthoDir = QDir(self.orthoDirName)

        self.imageFormats = self.settings.value("APIS/image_formats", [u'jpg'])
        self.hiResFormats = self.settings.value("APIS/hires_formats", [u'jpg', u'tif', u'sid', u'nef', u'raf', u'cr2', u'dng'])
        self.orthoFormats = self.settings.value("APIS/ortho_formats", [u'jpg', u'tif', u'sid'])

        self.imageFormatsStr = u"|".join(self.imageFormats)
        self.hiResFormatsStr = u"|".join(self.hiResFormats)
        self.orthoFormatsStr = u"|".join(self.orthoFormats)

        self.isSetup = True

    def registryIsSetup(self):
        return self.isSetup

    def setupRegistry(self):
        if self.registryFile and os.path.isfile(self.registryFile):
            if self.isOutdated():
                # If isOutdated > PopUp > Info: Local Image Registry is outdated > Please Update Image Registry
                # ask if update ImageRegistry
                msgBox = QMessageBox()
                msgBox.setWindowTitle(u'Image Registry')
                msgBox.setText(u'Die APIS Image Registry ist älter als ein Monat. Bitte führen Sie ein Update durch!')
                msgBox.addButton(QPushButton(u'Update'), QMessageBox.YesRole)
                msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.NoRole)
                ret = msgBox.exec_()

                if ret == 0:
                    self.updateRegistries()
                else:
                    self.loadRegistryFromFile()
            else:
                self.loadRegistryFromFile()
        else:
            # ask if generate ImageRegistry
            msgBox = QMessageBox()
            msgBox.setWindowTitle(u'Image Registry')
            msgBox.setText(u'Für die Verwendung von APIS muss eine Image Registry erstellt werden!')
            msgBox.addButton(QPushButton(u'Jetzt erstellen'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.NoRole)
            ret = msgBox.exec_()
            if ret == 0:
                self.updateRegistries()
            else:
                self.isLoaded = False

    def registryIsLoaded(self):
        return self.isLoaded

    def loadRegistryFromFile(self):
        #load self.__imageRegistry, self.__hiResRegistry, self.__orthoRegistry from JSON File
        if os.path.isfile(self.registryFile):
            with open(self.registryFile,'rU') as registry:
                registryDict = json.load(registry)
                self.__imageRegistryNE = registryDict["imageRegistryNE"]
                self.__hiResRegistryNE = registryDict["hiResRegistryNE"]
                self.__i2cRegistryNE = registryDict["i2cRegistryNE"]
                self.__orthoRegistryNE = registryDict["orthoRegistryNE"]
                self.__mosaicRegistryNE = registryDict["mosaicRegistryNE"]

                self.__imageRegistry = registryDict["imageRegistry"]
                self.__hiResRegistry = registryDict["hiResRegistry"]
                self.__i2cRegistry = registryDict["i2cRegistry"]
                self.__orthoRegistry = registryDict["orthoRegistry"]
                self.__mosaicRegistry = registryDict["mosaicRegistry"]
            self.isLoaded = True
            self.loaded.emit(True)
        else:
            self.isLoaded = False

    def writeRegistryToFile(self):
        # write self.__imageRegistry, self.__hiResRegistry, self.__orthoRegistry to JSON File
        # does registry file exist
        if os.path.isfile(self.registryFile):
            os.remove(self.registryFile)

        with open(self.registryFile, 'w') as f:
            registryDict = {
                "imageRegistryNE": self.__imageRegistryNE,
                "hiResRegistryNE" : self.__hiResRegistryNE,
                "i2cRegistryNE": self.__i2cRegistryNE,
                "orthoRegistryNE" : self.__orthoRegistryNE,
                "mosaicRegistryNE": self.__mosaicRegistryNE,
                "imageRegistry" : self.__imageRegistry,
                "hiResRegistry" : self.__hiResRegistry,
                "i2cRegistry": self.__i2cRegistry,
                "orthoRegistry" : self.__orthoRegistry,
                "mosaicRegistry": self.__mosaicRegistry
            }
            json.dump(registryDict, f)

    def isOutdated(self):
        if os.path.isfile(self.registryFile):
            today = datetime.datetime.today()
            creationDate = datetime.datetime.fromtimestamp(os.path.getctime(self.registryFile))
            modificationDate = datetime.datetime.fromtimestamp(os.path.getmtime(self.registryFile))
            if modificationDate > creationDate:
                fileAge = today - modificationDate
            else:
                fileAge = today - creationDate
            #QMessageBox.warning(None, "Zeit", "{0}".format(fileAge.days))
            if fileAge.days > 30:
                return True
            else:
                return False
            # Registry is Outdated > if local File is older than one month!

    def updateRegistries(self):
        self.startWorker()

    def hasImage(self, imageNumber):
        return True if imageNumber in self.__imageRegistryNE else False

    def hasHiRes(self, imageNumber):
        return True if imageNumber in self.__hiResRegistryNE else False

    def hasIns2Cam(self, imageNumber):
        return True if imageNumber in self.__i2cRegistryNE else False

    def hasOrtho(self, imageNumber):
        return True if imageNumber in self.__orthoRegistryNE else False

    def hasMosaic(self, imageNumber):
        filmNumber = imageNumber[:10]
        image = int(imageNumber[11:14])
        r = re.compile(r"^{0}*".format(filmNumber), re.IGNORECASE)
        mosaicCandidates = list(filter(r.match, self.__mosaicRegistryNE))
        mosaicsValid = []
        for mC in mosaicCandidates:
            fromTo = range(int(mC[11:14]), int(mC[15:18]) + 1)
            if image in fromTo:
                mosaicsValid.append(mC)
        return mosaicsValid
            # QMessageBox.information(None, "MosaicInfo", "{0}: {1}".format(imageNumber, ", ".join(mosaicsValid)))

    def hasOrthoOrMosaic(self, imageNumber):
        return self.hasOrtho(imageNumber) or bool(self.hasMosaic(imageNumber))

    def hasImageRE(self, imageNumber):
        r = re.compile(r"^{0}\.({1})$".format(imageNumber, self.imageFormatsStr), re.IGNORECASE)
        r = list(filter(r.match, self.__imageRegistry))
        return len(r)

    def hasHiResRE(self, imageNumber):
        r = re.compile(r"^{0}\.({1})$".format(imageNumber, self.hiResFormatsStr), re.IGNORECASE)
        r = list(filter(r.match, self.__hiResRegistry))
        return len(r)

    def hasIns2CamRE(self, imageNumber):
        pass

    def hasOrthoRE(self, imageNumber):
        r = re.compile(r"^{0}_op.+\.({1})$".format(imageNumber, self.orthoFormatsStr), re.IGNORECASE)
        r = list(filter(r.match, self.__orthoRegistry))
        return len(r)

    def hasMosaicRE(self, imageNumber):
        pass

    #filmNumber = OLD Film Number
    def getImageRegistryForFilm(self, filmNumber):
        imagesForFilm = []
        for imageNumber in self.__imageRegistryNE:
            if filmNumber in imageNumber:
                imagesForFilm.append(imageNumber)
        return imagesForFilm

    def startWorker(self):
        # create a new worker instance

        if self.worker is None:

            worker = UpdateRegistryWorker()

            # configure the QgsMessageBar
            messageBar = self.iface.messageBar().createMessage(u"Update Image Registry", u"Dieser Vorgang kann einige Minute dauern, bitte haben Sie Geduld!")
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
            self.iface.messageBar().pushWidget(messageBar, Qgis.Info)
            #self.iface.messageBar().widgetRemoved
            # messageBar

            self.messageBar = messageBar

            # start the worker in a new thread
            thread = QThread()
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
        #self.progressBar.setMaximum(100)
        #self.progressBar.setValue(100)

    def workerFinished(self, ret):
        # clean up the worker and thread
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        # remove widget from message bar
        self.iface.messageBar().popWidget(self.messageBar)
        if ret is not None:
            #report the result
            if not self.worker.killed:
                self.__imageRegistryNE = ret["imageRegistryNE"]
                self.__hiResRegistryNE = ret["hiResRegistryNE"]
                self.__i2cRegistryNE = ret["i2cRegistryNE"]
                self.__orthoRegistryNE = ret["orthoRegistryNE"]
                self.__mosaicRegistryNE = ret["mosaicRegistryNE"]

                self.__imageRegistry = ret["imageRegistry"]
                self.__hiResRegistry = ret["hiResRegistry"]
                self.__i2cRegistry = ret["i2cRegistry"]
                self.__orthoRegistry = ret["orthoRegistry"]
                self.__mosaicRegistry = ret["mosaicRegistry"]
                self.writeRegistryToFile()

                self.iface.messageBar().pushMessage(u"Update Image Registry", u"Das Update wurde erfolgreich abgeschloßen!", level=Qgis.Success, duration=5)
                self.isLoaded = True
                self.loaded.emit(True)
            else:
                self.iface.messageBar().pushMessage(u"Update Image Registry", u"Das Update wurde abgebrochen!", level=Qgis.Warning, duration=5)
                if os.path.isfile(self.registryFile):
                    os.remove(self.registryFile)
                self.isLoaded = False
                self.loaded.emit(False)
            #self.iface.messageBar().pushMessage('Result')
        else:
            # notify the user that something went wrong
            self.iface.messageBar().pushMessage('Something went wrong! See the message log for more information.', level=Qgis.Critical, duration=3)
            self.isLoaded = False
        self.worker = None

    def workerError(self, e, exception_string):
        QgsMessageLog.logMessage('APIS UpdateRegistryWorker thread raised an exception:\n'.format(exception_string), level=Qgis.Critical)

class UpdateRegistryWorker(QObject):
    '''Background worker for updating Image Registry'''

    finished = pyqtSignal(object)
    error = pyqtSignal(Exception, str)

    def __init__(self):
        QObject.__init__(self)
        self.killed = False
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

        # self.registryFile = pluginDir + "\\" + "apis_image_registry.json" #self.settings.value("APIS/image_registry_file", None)

        self.imageDirName = self.settings.value("APIS/image_dir")
        self.orthoDirName = self.settings.value("APIS/ortho_image_dir")
        self.imageDir = QDir(self.imageDirName)
        self.orthoDir = QDir(self.orthoDirName)

        self.imageFormats = self.settings.value("APIS/image_formats", ['jpg'])
        self.hiResFormats = self.settings.value("APIS/hires_formats", ['jpg', 'tif', 'sid', 'nef', 'raf', 'cr2', 'dng'])
        self.orthoFormats = self.settings.value("APIS/ortho_formats", ['jpg', 'tif', 'sid'])

        self.imageFormatsStr = "|".join(self.imageFormats)
        self.hiResFormatsStr = "|".join(self.hiResFormats)
        self.orthoFormatsStr = "|".join(self.orthoFormats)

    def run(self):
        try:
            self.updateImageRegistries()
            self.updateOrthoRegistries()

            if self.killed is False:
                ret = True
                ret = {
                    "imageRegistryNE": self.imageRegistryNE,
                    "hiResRegistryNE": self.hiResRegistryNE,
                    "i2cRegistryNE": self.i2cRegistryNE,
                    "orthoRegistryNE": self.orthoRegistryNE,
                    "mosaicRegistryNE": self.mosaicRegistryNE,
                    "imageRegistry": self.imageRegistry,
                    "hiResRegistry": self.hiResRegistry,
                    "i2cRegistry": self.i2cRegistry,
                    "orthoRegistry": self.orthoRegistry,
                    "mosaicRegistry": self.mosaicRegistry
                }
            else:
                ret = False
        except Exception as e:
            # forward the exception upstream
            self.error.emit(e, traceback.format_exc())
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    def updateImageRegistries(self):
        self.imageRegistry = []
        self.hiResRegistry = []
        self.i2cRegistry = []

        imageEntryList = self.imageDir.entryList(['??????????'], QDir.Dirs)
        for i in imageEntryList:
            if self.killed is True:
                # kill request received, exit loop early
                break
            iDir = QDir(self.imageDir.path() + '\\' + i)
            # FIXME implement solution for not just jpg but values from ini
            iEntryList = iDir.entryList([i + '_???.jpg'], QDir.Files)
            self.imageRegistry = self.imageRegistry + iEntryList

            hiResDirsEntryList = iDir.entryList(["highres*", "mrsid", "raw"], QDir.Dirs)
            hiResFilters = [i + '_???.' + ext for ext in self.hiResFormats]
            for hr in hiResDirsEntryList:
                if self.killed is True:
                    # kill request received, exit loop early
                    break
                hrDir = QDir(iDir.path() + '\\' + hr)
                hrEntryList = hrDir.entryList(hiResFilters, QDir.Files)
                self.hiResRegistry = self.hiResRegistry + hrEntryList

            i2cDirEntryList = iDir.entryList(["ins2cam"], QDir.Dirs)
            i2cFilters = [i + '_???.' + ext for ext in ['jpg', 'tif', 'tiff']]
            for i2c in i2cDirEntryList:
                if self.killed is True:
                    # kill request received, exit loop early
                    break
                i2cDir = QDir(iDir.path() + '\\' + i2c)
                i2cEntryList = i2cDir.entryList(i2cFilters, QDir.Files)
                self.i2cRegistry = self.i2cRegistry + i2cEntryList


        if self.killed is False:
            self.imageRegistryNE = [img[:14].replace('_', '.') for img in self.imageRegistry]
            self.hiResRegistryNE = [img[:14].replace('_', '.') for img in self.hiResRegistry]
            self.i2cRegistryNE = [img[:14].replace('_', '.') for img in self.i2cRegistry]

    def updateOrthoRegistries(self):
        import glob, os
        self.orthoRegistryNE = []
        self.orthoRegistry = []
        self.mosaicRegistryNE = []
        self.mosaicRegistry = []
        orthoEntryList = self.orthoDir.entryList(['??????????'], QDir.Dirs)
        for o in orthoEntryList:
            if self.killed is True:
                # kill request received, exit loop early
                break
            orthoFilters = [o + '_???_op*.' + ext for ext in self.orthoFormats]
            mosaicFilters = [o + '_???_???_op*.' + ext for ext in self.orthoFormats]
            oDir = QDir(self.orthoDir.path() + '\\' + o)
            oEntryList = oDir.entryList(orthoFilters, QDir.Files)
            mEntryList = oDir.entryList(mosaicFilters, QDir.Files)
            self.orthoRegistry = self.orthoRegistry + oEntryList
            self.mosaicRegistry = self.mosaicRegistry + mEntryList
        if self.killed is False:
            self.orthoRegistryNE = [img[:14].replace('_', '.') for img in self.orthoRegistry]
            self.mosaicRegistryNE = [f"{img[:10]}.{img[11:14]}-{img[15:18]}" for img in self.mosaicRegistry]
