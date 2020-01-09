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
import sys
import sqlite3
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from qgis.utils import spatialite_connect

class ApisDbManager:
    def __init__(self, path):
        #db = QSqlDatabase.addDatabase('QSQLITE')
        #db.setDatabaseName(path)
        #if not db.open():
        #    QMessageBox.warning(None, "DB", "Database Error: {0}".format(db.lastError().text()))
        #else:
        #    query = db.exec_("""SELECT sqlite_version()""")
        #    query.next()
            #QMessageBox.information(None, "DB", "sqlite: {0}, spatialite: {1}".format(query.value(0), query.value(1)))

        #QMessageBox.warning(None, "DB", "QSPATIALITE: {0}".format(QSqlDatabase.isDriverAvailable('QSPATIALITE')))
        self.connectToDb("QSPATIALITE", path) #("QSQLITE", path)
        self.__dbWasUpdated = False

    def connectToDb(self, type, path):
        self.__db = QSqlDatabase.addDatabase(type)
        self.__db.setDatabaseName(path)
        if not self.__db.open():
            QMessageBox.warning(None, "DB", "Database Error: {0}".format(self.__db.lastError().text()))
            sys.exit(1)
        #else:
            #QMessageBox.warning(None, "DB", "Database Error: {0}".format(self.__db.isValid()))
            #self.__db.tables()
            #query = self.__db.exec_("""select * from film""")
            # iterate over the rows
          #  while query.next():
               # record = query.record()
                # print the value of the first column

    @property
    def db(self):
        return self.__db

    @property
    def dbRequiresUpdate(self):
        return self.__dbWasUpdated

    @dbRequiresUpdate.setter
    def dbRequiresUpdate(self, value):
        self.__dbWasUpdated = value

    def spatialQuery(self, qryStr, qryTpl = ()):
        con = spatialite_connect(self.__db.databaseName())
        c = con.cursor()
        q = c.execute(qryStr, qryTpl)
        #con.close()
        return q

    def queryToQStandardItemModel(self, query):
        '''
        query can be either a Q
        :param query:
        :return:
        '''
        model = QStandardItemModel()

        query.seek(-1)
        count = 0
        while query.next():
            rec = query.record()
            model.appendRow([QStandardItem('' if rec.value(col) == None else str(rec.value(col))) for col in range(rec.count())])
            count += 1

        if count > 0:
            for col in range(rec.count()):
                model.setHeaderData(col, Qt.Horizontal, rec.fieldName(col))
            return model
        else:
            return None
