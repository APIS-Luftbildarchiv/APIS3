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

# Standard Libs
import os

# PyQt
from PyQt5.uic import loadUiType
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog  # , QMessageBox

# APIS
from APIS.src.apis_printer import OutputMode

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'ui', 'apis_printing_options.ui'), resource_suffix='')


class APISPrintingOptions(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(APISPrintingOptions, self).__init__(parent)
        self.isVisPersonalDataChk = False
        self.isVisFilmProjectChk = False
        self.setupUi(self)

    def configure(self, visSelectionModeGrp=True, visOutputModeGrp=True, visOneFileForEachRBtn=False, visPersonalDataChk=False, visFilmProjectChk=False):
        self.uiSelectionModeGrp.setVisible(visSelectionModeGrp)
        self.uiOutputModeGrp.setVisible(visOutputModeGrp)
        self.uiOneFileForEachRBtn.setVisible(visOneFileForEachRBtn)
        self.uiPersonalDataChk.setVisible(visPersonalDataChk)
        if visPersonalDataChk:
            self.uiPersonalDataChk.setCheckState(Qt.Checked)
        self.isVisPersonalDataChk = visPersonalDataChk
        self.uiFilmProjectChk.setVisible(visFilmProjectChk)
        if visFilmProjectChk:
            self.uiFilmProjectChk.setCheckState(Qt.Checked)
        self.isVisFilmProjectChk = visFilmProjectChk

        self.adjustSize()

    def addPrintingOption(self):

        self.adjustSize()

    def selectionModeIsAll(self):
        return self.uiPrintAllRBtn.isChecked()

    def outputMode(self):
        if self.uiOneFileRBtn.isChecked():
            return OutputMode.MergeAll
        elif self.uiOneFileForEachRBtn.isChecked():
            return OutputMode.MergeByGroup
        elif self.uiSingleFilesRBtn.isChecked():
            return OutputMode.MergeNone

    def printPersonalData(self):
        # QMessageBox.information(None, "Info", "print personal data: {0}, {1}".format(self.isVisPersonalDataChk, self.uiPersonalDataChk.isChecked()))
        if self.isVisPersonalDataChk:
            return self.uiPersonalDataChk.isChecked()
        else:
            return True

    def printFilmProject(self):
        # QMessageBox.information(None, "Info", "print personal data: {0}, {1}".format(self.isVisPersonalDataChk, self.uiPersonalDataChk.isChecked()))
        if self.isVisFilmProjectChk:
            return self.uiFilmProjectChk.isChecked()
        else:
            return True
