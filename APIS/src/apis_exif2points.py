# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# Points2One
# Copyright (C) 2010 Pavol Kapusta <pavol.kapusta@gmail.com>
# Copyright (C) 2010, 2013, 2015 Goyo <goyodiaz@gmail.com>
#
# -----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ---------------------------------------------------------------------

from PyQt5.QtCore import QSettings, QFile, QVariant, Qt
from PyQt5.QtWidgets import QMessageBox, QProgressBar
from qgis.core import (QgsWkbTypes, QgsVectorFileWriter, QgsFields, QgsField, QgsCoordinateReferenceSystem, QgsFeature,
                       QgsGeometry, QgsPointXY)
from qgis.core import QgsMessageLog, Qgis

from APIS.src.apis_utils import GetExifForImage

#import pyexiv2 as exif
import exifread

import glob
import os.path
import os, errno

class Exif2Points(object):
    """Data processing for Point2One."""

    def __init__(self, iface, filmNumber):
        self.settings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
        self.filmNumber = filmNumber
        self.iface = iface
        self.imagePath = os.path.normpath(self.settings.value("APIS/image_dir"))
        self.filmPath = os.path.join(self.imagePath, self.filmNumber)
        self.images = glob.glob(os.path.normpath(self.filmPath + "\\" + self.filmNumber + "_*.*"))
        self.flightPath = os.path.join(os.path.normpath(self.settings.value("APIS/flightpath_dir")),
                                       self.yearFromFilm(self.filmNumber))

        if not os.path.exists(self.flightPath):
            os.makedirs(self.flightPath)

        self.shpFile = os.path.normpath(self.flightPath + "\\" + self.filmNumber + "_gps.shp")

    def run(self):
        """Create the output shapefile."""
        if os.path.isdir(self.filmPath) and len(self.images) > 0:
            check = QFile(self.shpFile)
            if check.exists():
                if not QgsVectorFileWriter.deleteShapeFile(self.shpFile):
                    self.iface.messageBar().pushMessage(u"Error",
                                                        u"Die Datei existiert bereits und kann nicht überschrieben werden (Eventuell in QGIS geladen!).",
                                                        level=Qgis.MessageLevel.Critical, duration=10)
                    return None

            # fields
            fields = QgsFields()
            fields.append(QgsField("bildnr", QVariant.Int))
            fields.append(QgsField("lat", QVariant.Double))
            fields.append(QgsField("lon", QVariant.Double))
            fields.append(QgsField("alt", QVariant.Double))

            writer = QgsVectorFileWriter(str(self.shpFile), "UTF-8", fields, QgsWkbTypes.Point, QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId), "ESRI Shapefile")

            mb = self.iface.messageBar().createMessage(u"EXIF",
                                                       u"Die EXIF Daten (Geo Koordinaten und Höhe) werden aus den Bildern ausgelesen")
            progress = QProgressBar()
            progress.setMinimum(0)
            progress.setMaximum(0)
            progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            mb.layout().addWidget(progress)
            self.iface.messageBar().pushWidget(mb, Qgis.MessageLevel.Info)

            hasFeatures = False
            for feature in self.iter_images_as_features():
                writer.addFeature(feature)
                hasFeatures = True
            del writer

            if hasFeatures:
                self.iface.messageBar().clearWidgets()
                self.iface.messageBar().pushMessage(u"EXIF",
                                                    u"Die Shape Datei wurde erfolgreich erstellt und in QGIS geladen!",
                                                    level=Qgis.MessageLevel.Success, duration=10)
                return self.shpFile
            else:
                QMessageBox.warning(None, "Bilder", u"Die vorhandenen Bilder enthalten keine GPS Information.")
                return None
        else:
            QMessageBox.warning(None, "Verzeichnis", u"Es wurde kein Bildverzeichnis für diesen Film gefunden.")
            return None

    # https: // gist.github.com / snakeye / fdc372dbf11370fe29eb
    # TODO remove if utils approach works
    def _get_if_exist(self, data, key):
        return data[key] if key in data else None

    # TODO remove if utils approach works
    def _convert_to_degress(self, value):
        """
        Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
        :param value:
        :type value: exifread.utils.Ratio
        :rtype: float
        """
        return float(value.values[0].num) / float(value.values[0].den) + (float(value.values[1].num) / float(value.values[1].den) / 60.0) + (float(value.values[2].num) / float(value.values[2].den) / 3600.0)

    # TODO remove if utils approach works
    def get_exif_location(self, exif_data):
        """
        Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
        """
        lat = None
        lon = None
        alt = None

        gps_latitude = self._get_if_exist(exif_data, 'GPS GPSLatitude')
        gps_latitude_ref = self._get_if_exist(exif_data, 'GPS GPSLatitudeRef')
        gps_longitude = self._get_if_exist(exif_data, 'GPS GPSLongitude')
        gps_longitude_ref = self._get_if_exist(exif_data, 'GPS GPSLongitudeRef')
        gps_altitude = self._get_if_exist(exif_data, 'GPS GPSAltitude')
        gps_altitude_ref = self._get_if_exist(exif_data, 'GPS GPSAltitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = self._convert_to_degress(gps_latitude)
            if gps_latitude_ref.values[0] != 'N':
                lat = 0 - lat

            lon = self._convert_to_degress(gps_longitude)
            if gps_longitude_ref.values[0] != 'E':
                lon = 0 - lon

        if gps_altitude and gps_altitude_ref:
            alt = float(gps_altitude.values[0].num / gps_altitude.values[0].den)
            if gps_altitude_ref.values[0] == 1:
                alt *= -1

        return lat, lon, alt

    def iter_images_as_features(self):
        for image in self.images:
            exif = GetExifForImage(image, altitude=True, longitude=True, latitude=True)
            # TODO remove if utils approach works
            #with open(image, 'rb') as f:
            #tags = exifread.process_file(f, details=False)
            #ddlat, ddlon, alt = self.get_exif_location(tags)

            if exif["latitude"] and exif["longitude"]:
                imageName = os.path.basename(image)
                imageNumber = int(imageName[11:14])
                attributes = [imageNumber, exif["latitude"], exif["longitude"], exif["altitude"]]

                feature = QgsFeature()
                feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(exif["longitude"], exif["latitude"])))
                feature.setAttributes(attributes)
                yield feature

    def log_warning(self, message):
        """Log a warning."""
        self.logger.append(message)

    def get_logger(self):
        """Return the list of logged warnings."""
        return self.logger

    def yearFromFilm(self, film):
        return film[2:6]