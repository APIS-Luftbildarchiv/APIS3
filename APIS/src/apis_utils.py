# -*- coding: utf-8 -*-
"""
/***************************************************************************
 APIS
                                 A QGIS plugin
 QGIS Plugin for APIS
                             -------------------
        begin                : 2015-04-10
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Johannes Liem/Luftbildarchiv Uni Wien
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
from PyQt5.QtCore import QSettings, QCoreApplication, QDateTime, QDir, QSize, QPoint
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QMessageBox, QPushButton
from qgis.core import QgsProject, QgsCoordinateTransform, QgsVectorLayer, QgsFeature

import os.path, sys, subprocess, exifread

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def ApisPluginSettings():
    """Get the plugin config status and settings from QSettings

    :returns: Configuration status of APIS plugin
    :rtype: QString

    :returns: Translated version of message.
    :rtype: QString

    """
    s = QSettings()
    if s.contains("APIS/config_ini"):
        if os.path.isfile(s.value("APIS/config_ini")):
            return IsApisIni(s.value("APIS/config_ini"))
        else:
            #Settings INI as stored does not exist
            return False, tr(u"Ausgewählte APIS INI Datei ({0}) ist nicht vorhanden!").format(s.value("APIS/config_ini"))
    else:
        #Settings INI is not stored
        return False, tr(u"Keine APIS INI Datei ausgewählt!")

def IsApisIni(ini):

    s = QSettings(ini, QSettings.IniFormat)
    requiredKeysIsFile = ['database_file']
    requiredKeysIsDir = ['flightpath_dir', 'image_dir', 'ortho_image_dir', 'repr_image_dir', 'insp_image_dir']
    requiredKeys = ['hires_vertical', 'hires_oblique_digital', 'hires_oblique_analog']

    isIni = True
    errorKeys = []
    for k in requiredKeysIsFile:
        key = "APIS/" + k
        if not s.contains(key) or not os.path.isfile(s.value(key)):
            isIni = False
            errorKeys.append(k)

    for k in requiredKeysIsDir:
        key = "APIS/" + k
        if not s.contains(key) or not os.path.isdir(s.value(key)):
            isIni = False
            errorKeys.append(k)

    for k in requiredKeys:
        key = "APIS/" + k
        if not s.contains(key):
            isIni = False
            errorKeys.append(k)

    return isIni, s if isIni else tr("Folgende Schlüssel in der INI Datei sind nicht korrekt oder nicht vorhanden: ") + ", ".join(errorKeys)

# ---------------------------------------------------------------------------
# Open Files or Folder
# ---------------------------------------------------------------------------

def OpenFileOrFolder(fileOrFolder):
    if os.path.exists(fileOrFolder):
        if sys.platform == 'linux2':
            subprocess.call(["xdg-open", fileOrFolder])
        else:
            os.startfile(fileOrFolder)
        return True
    else:
        return False

def OpenFolderAndSelect(file):
    if os.path.exists(file):
        subprocess.Popen(r'explorer /select,"{0}"'.format(os.path.abspath(file)))

# ---------------------------------------------------------------------------
# Recurring Tasks
# ---------------------------------------------------------------------------

def SelectionOrAll(parent=None):
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(u'Auswahl oder alle Einträge?')
    msgBox.setText(u'Wollen Sie die Auswahl oder alle Einträge verwenden?')
    msgBox.addButton(QPushButton(u'Auswahl'), QMessageBox.YesRole)
    msgBox.addButton(QPushButton(u'Alle Einträge'), QMessageBox.NoRole)
    msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
    return msgBox.exec_()

def PolygonOrPoint(parent=None):
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(u'Polygone, Punkte oder Beides?')
    msgBox.setText(u'Wollen Sie Polygone, Punkte oder beide Layer verwenden?')
    msgBox.addButton(QPushButton(u'Polygone'), QMessageBox.ActionRole)
    msgBox.addButton(QPushButton(u'Punkte'), QMessageBox.ActionRole)
    msgBox.addButton(QPushButton(u'Polygone und Punkte'), QMessageBox.ActionRole)
    msgBox.addButton(QPushButton(u'Abbrechen'), QMessageBox.RejectRole)
    ret = msgBox.exec_()
    if ret == 0:
        return True, False
    elif ret == 1:
        return False, True
    elif ret == 2:
        return True, True
    else:
        return None, None

def FileOrFolder(parent=None, title="APIS", text="Bitte wählen Sie eine Option", rejectText="OK"):
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(title)
    msgBox.setText(text)
    #msgBox.setText(u"Die ausgewählten Daten wurden in eine SHP Datei exportiert.")
    msgBox.addButton(QPushButton(u'In QGIS laden'), QMessageBox.ActionRole)
    msgBox.addButton(QPushButton(u'Verzeichnis öffnen'), QMessageBox.ActionRole)
    msgBox.addButton(QPushButton(u'Laden und öffnen'), QMessageBox.ActionRole)
    msgBox.addButton(QPushButton(rejectText), QMessageBox.AcceptRole)
    return msgBox.exec_()

def GenerateWeatherDescription(db, weatherCode):
    categories = ["Low Cloud Amount", "Visibility Kilometres", "Low Cloud Height", "Weather", "Remarks Mission", "Remarks Weather"]
    query = QSqlQuery(db)
    pos = 0
    help = 0
    weatherDescription = ""
    for c in weatherCode:
        qryStr = "select description from wetter where category = '{0}' and code = '{1}' limit 1".format(categories[pos-help], c)
        query.exec_(qryStr)
        query.first()
        fn = query.value(0)
        if pos <= 5:
            weatherDescription += categories[pos] + ': ' + fn
            if pos < 5:
               weatherDescription += '\n'
        else:
            weatherDescription += '; ' + fn

        if pos >= 5:
            help += 1
        pos += 1
    return weatherDescription

def VersionToCome(version="3.1"):
    QMessageBox.information(None, "Version 3", "Diese Funktion steht ab Version {0} zur Verfügung.".format(version))

def SetExportPath(path):
    QSettings().setValue("APIS/latest_export_dir", path)

def GetExportPath():
    return QSettings().value("APIS/latest_export_dir",  QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat).value("APIS/working_dir", QDir.home().dirName()))

def SetWindowSizeAndPos(window, size, pos):
    SetWindowSize(window, size)
    SetWindowPos(window, pos)

def SetWindowSize(window, size):
    QSettings().setValue("APIS/{0}_size".format(window), size)

def SetWindowPos(window, pos):
    QSettings().setValue("APIS/{0}_pos".format(window), pos)

def GetWindowSize(window):
    return QSettings().value("APIS/{0}_size".format(window), None)

def GetWindowPos(window):
    return QSettings().value("APIS/{0}_pos".format(window), None)

# ---------------------------------------------------------------------------
# Common Calculations
# ---------------------------------------------------------------------------

def GetMeridianAndEpsgGK(lon):
    '''
    :param lon: float Longitude in Grad
    :return meridian, epsg: int/long Meridian Streifen, int/long epsg Gauß-Krüger Österreich
    :rtype: int, int
    '''
    if lon < 11.8333333333:
        return 28, 31254
    elif lon > 14.8333333333:
        return 34, 31256
    else:
        return 31, 31255


def TransformGeometry(geom, srcCrs, destCrs):
    '''
    :param geom: QgsGeometry
    :param srcCrs: QgsCoordinateReferenceSystem Source CRS
    :param destCrs: QgsCoordinateReferenceSystem Destination CRS
    :return: geom: Transformed QgsGeometry
    :rtype: QgsGeometry
    '''
    geom.transform(QgsCoordinateTransform(srcCrs, destCrs, QgsProject.instance()))
    return geom

# ---------------------------------------------------------------------------
# Common Legacy convertions
# ---------------------------------------------------------------------------

def IdToIdLegacy(id):
    millennium = ""
    if id[2:4] == "19":
        millennium = "01"
    elif id[2:4] == "20":
        millennium = "02"
    return millennium + id[4:]

# ---------------------------------------------------------------------------
# Common DB Checks / Geometry Checks
# ---------------------------------------------------------------------------

def DbHasTable(db, table):
    query = QSqlQuery(db)
    query.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}'".format(table))
    query.exec_()
    query.first()
    #QMessageBox.information(None, "info", "{}".format(query.value(0) == table))
    if query.value(0) == table:
        return True
    else:
        return False

# FIXME : relocate to apis_site_dialog.py if only usage is apis_site_dialog:showEvent() # Don't!
def SiteHasFindspot(db, siteNumber):
    query = QSqlQuery(db)
    query.prepare(u"SELECT COUNT(*) FROM fundstelle WHERE fundortnummer = '{0}'".format(siteNumber))
    query.exec_()
    query.first()
    return query.value(0)


def SitesHaveFindspots(db, siteNumbers):
    sites = u", ".join(u"'{0}'".format(siteNumber) for siteNumber in siteNumbers)
    query = QSqlQuery(db)
    query.prepare(u"SELECT COUNT(*) FROM fundstelle WHERE fundortnummer IN ({0})".format(sites))
    query.exec_()
    query.first()
    return query.value(0)


def GetFindspotNumbers(db, siteNumbers):
    query = QSqlQuery(db)
    sites = u", ".join(u"'{0}'".format(siteNumber) for siteNumber in siteNumbers)
    query.prepare(u"SELECT fundortnummer || '.' || fundstellenummer FROM fundstelle WHERE fundortnummer  IN ({0})".format(sites))
    res = query.exec_()
    query.seek(-1)
    findspots = []
    while query.next():
        findspots.append(query.value(0))

    return findspots


def IsFilm(db, filmNumber):
    """
    Checks if filmNumber is a filmNumber in film Table
    :param db: Database
    :param filmNumber: 10 digit filmNumber
    :return:
    """
    query = QSqlQuery(db)
    query.prepare(u"SELECT COUNT(*) FROM film WHERE filmnummer = '{0}'".format(filmNumber))
    query.exec_()
    query.first()
    return query.value(0)


def ApisLogger(db, action, fromTable, primaryKeysWhere):
        toTable = fromTable + u"_log"

        q = QSqlQuery(db)
        q.exec_("PRAGMA table_info({0});".format(fromTable))
        q.seek(-1)
        fieldNames = []
        while (q.next()):
            fieldNames.append(str(q.record().value(1)))
        fieldNames.pop(0) # pop id
        query = QSqlQuery(db)
        query.prepare("INSERT INTO {0}({1}) SELECT {1} FROM {2} WHERE {3}".format(toTable, ", ".join(fieldNames), fromTable, primaryKeysWhere))
        res = query.exec_()
        if not res:
            QMessageBox.information(None, "SqlError", "{0}, {1}".format(query.lastError().text(), query.executedQuery()))

        import getpass
        query.prepare("UPDATE {0} SET aktion = '{1}', aktionsdatum = '{2}', aktionsuser = '{3}' WHERE rowid = (SELECT max(rowid) FROM {0})".format(toTable, action, QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"), getpass.getuser()))
        res = query.exec_()
        if not res:
            QMessageBox.information(None, "SqlError", "{0}, {1}".format(query.lastError().text(), query.executedQuery()))

# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------

# noinspection PyMethodMayBeStatic
def tr(message):
    """Get the translation for a string using Qt translation API.

    We implement this ourselves since we do not inherit QObject.

    :param message: String for translation.
    :type message: str, QString

    :returns: Translated version of message.
    :rtype: QString
    """
    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
    return QCoreApplication.translate('APIS', message)

# ---------------------------------------------------------------------------
# Reading EXIF
# ---------------------------------------------------------------------------
# https: // gist.github.com / snakeye / fdc372dbf11370fe29eb
def GetExifDataIfExist(data, key):
    return data[key] if key in data else None

def ConvertToDegress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    return float(value.values[0].num) / float(value.values[0].den) + (float(value.values[1].num) / float(value.values[1].den) / 60.0) + (float(value.values[2].num) / float(value.values[2].den) / 3600.0)

def GetExifForImage(image, altitude=False, longitude=False, latitude=False, exposure_time=False, focal_length=False, fnumber=False):
    # altitude, longitude, latitude, exposure time, focal length, fnumber
    # exif = [None, None, None, None, None, None]
    exif = {}
    if os.path.isfile(image):
        with open(image, 'rb') as f:
            tags = exifread.process_file(f, details=False)

            if altitude:
                gps_altitude = GetExifDataIfExist(tags, 'GPS GPSAltitude')
                gps_altitude_ref = GetExifDataIfExist(tags, 'GPS GPSAltitudeRef')
                if gps_altitude and gps_altitude_ref:
                    alt = float(gps_altitude.values[0].num / gps_altitude.values[0].den)
                    if gps_altitude_ref.values[0] == 1:
                        alt *= -1
                    exif["altitude"] = alt
                else:
                    exif["altitude"] = None

            if longitude:
                gps_longitude = GetExifDataIfExist(tags, 'GPS GPSLongitude')
                gps_longitude_ref = GetExifDataIfExist(tags, 'GPS GPSLongitudeRef')
                if gps_longitude and gps_longitude_ref:
                    lon = ConvertToDegress(gps_longitude)
                    if gps_longitude_ref.values[0] != 'E':
                        lon = 0 - lon
                    exif["longitude"] = lon
                else:
                    exif["longitude"] = None

            if latitude:
                gps_latitude = GetExifDataIfExist(tags, 'GPS GPSLatitude')
                gps_latitude_ref = GetExifDataIfExist(tags, 'GPS GPSLatitudeRef')
                if gps_latitude and gps_latitude_ref:
                    lat = ConvertToDegress(gps_latitude)
                    if gps_latitude_ref.values[0] != 'N':
                        lat = 0 - lat
                    exif["latitude"] = lat
                else:
                    exif["latitude"] = None

            if exposure_time:
                exif_exposure_time = GetExifDataIfExist(tags, 'EXIF ExposureTime')
                if exif_exposure_time:
                    exif["exposure_time"] = float(exif_exposure_time.values[0].num / exif_exposure_time.values[0].den)
                else:
                    exif["exposure_time"] = None

            if focal_length:
                exif_focal_length = GetExifDataIfExist(tags, 'EXIF FocalLength')
                if exif_focal_length:
                    exif["focal_length"] = float(exif_focal_length.values[0].num / exif_focal_length.values[0].den)
                else:
                    exif["focal_length"] = None

            if fnumber:
                exif_fnumber = GetExifDataIfExist(tags, 'EXIF FNumber')
                if exif_fnumber:
                    exif["fnumber"] = float(exif_fnumber.values[0].num / exif_fnumber.values[0].den)
                else:
                    exif["fnumber"] = None
    else:
        if altitude:
            exif["altitude"] = None
        if longitude:
            exif["longitude"] = None
        if latitude:
            exif["latitude"] = None
        if exposure_time:
            exif["exposure_time"] = None
        if focal_length:
            exif["focal_length"] = None
        if fnumber:
            exif["fnumber"] = None

    return exif
