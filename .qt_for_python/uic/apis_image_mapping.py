# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\data\development\apis\APIS3\APIS\ui\apis_image_mapping.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_apisImageMappingDialog(object):
    def setupUi(self, apisImageMappingDialog):
        apisImageMappingDialog.setObjectName("apisImageMappingDialog")
        apisImageMappingDialog.resize(395, 825)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/APIS/icons/apis.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        apisImageMappingDialog.setWindowIcon(icon)
        apisImageMappingDialog.setLayoutDirection(QtCore.Qt.LeftToRight)
        apisImageMappingDialog.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Austria))
        apisImageMappingDialog.setFloating(False)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_4 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.uiFilmSelectionHorizontalLayout = QtWidgets.QHBoxLayout()
        self.uiFilmSelectionHorizontalLayout.setObjectName("uiFilmSelectionHorizontalLayout")
        self.uiFilmSelectionBtn = QtWidgets.QPushButton(self.dockWidgetContents)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/plugins/APIS/icons/film_selection.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiFilmSelectionBtn.setIcon(icon1)
        self.uiFilmSelectionBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiFilmSelectionBtn.setAutoDefault(False)
        self.uiFilmSelectionBtn.setObjectName("uiFilmSelectionBtn")
        self.uiFilmSelectionHorizontalLayout.addWidget(self.uiFilmSelectionBtn)
        self.uiCurrentFilmNumberEdit = QtWidgets.QLineEdit(self.dockWidgetContents)
        self.uiCurrentFilmNumberEdit.setStyleSheet("background-color: rgb(218, 218, 218);")
        self.uiCurrentFilmNumberEdit.setFrame(True)
        self.uiCurrentFilmNumberEdit.setReadOnly(True)
        self.uiCurrentFilmNumberEdit.setObjectName("uiCurrentFilmNumberEdit")
        self.uiFilmSelectionHorizontalLayout.addWidget(self.uiCurrentFilmNumberEdit)
        self.verticalLayout.addLayout(self.uiFilmSelectionHorizontalLayout)
        self.line_2 = QtWidgets.QFrame(self.dockWidgetContents)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.uiMappingGridLayout = QtWidgets.QGridLayout()
        self.uiMappingGridLayout.setObjectName("uiMappingGridLayout")
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        self.label.setMaximumSize(QtCore.QSize(10, 16777215))
        self.label.setObjectName("label")
        self.uiMappingGridLayout.addWidget(self.label, 1, 1, 1, 1)
        self.uiYCoordinateLbl = QtWidgets.QLabel(self.dockWidgetContents)
        self.uiYCoordinateLbl.setObjectName("uiYCoordinateLbl")
        self.uiMappingGridLayout.addWidget(self.uiYCoordinateLbl, 2, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_5.setObjectName("label_5")
        self.uiMappingGridLayout.addWidget(self.label_5, 0, 0, 1, 3)
        self.uiXCoordinateLbl = QtWidgets.QLabel(self.dockWidgetContents)
        self.uiXCoordinateLbl.setObjectName("uiXCoordinateLbl")
        self.uiMappingGridLayout.addWidget(self.uiXCoordinateLbl, 1, 2, 1, 1)
        self.uiSetCenterPointBtn = QtWidgets.QPushButton(self.dockWidgetContents)
        self.uiSetCenterPointBtn.setMaximumSize(QtCore.QSize(32, 32))
        self.uiSetCenterPointBtn.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/plugins/APIS/icons/center_point.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiSetCenterPointBtn.setIcon(icon2)
        self.uiSetCenterPointBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiSetCenterPointBtn.setCheckable(True)
        self.uiSetCenterPointBtn.setChecked(False)
        self.uiSetCenterPointBtn.setFlat(False)
        self.uiSetCenterPointBtn.setObjectName("uiSetCenterPointBtn")
        self.uiMappingGridLayout.addWidget(self.uiSetCenterPointBtn, 1, 0, 2, 1)
        self.label_3 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_3.setMaximumSize(QtCore.QSize(10, 16777215))
        self.label_3.setObjectName("label_3")
        self.uiMappingGridLayout.addWidget(self.label_3, 2, 1, 1, 1)
        self.uiAddCenterPointBtn = QtWidgets.QPushButton(self.dockWidgetContents)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/plugins/APIS/icons/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiAddCenterPointBtn.setIcon(icon3)
        self.uiAddCenterPointBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiAddCenterPointBtn.setObjectName("uiAddCenterPointBtn")
        self.uiMappingGridLayout.addWidget(self.uiAddCenterPointBtn, 3, 0, 1, 3)
        self.verticalLayout.addLayout(self.uiMappingGridLayout)
        self.uiMappingDetailsGridLayout = QtWidgets.QGridLayout()
        self.uiMappingDetailsGridLayout.setContentsMargins(0, -1, -1, -1)
        self.uiMappingDetailsGridLayout.setObjectName("uiMappingDetailsGridLayout")
        self.uiCancelCenterPointBtn = QtWidgets.QPushButton(self.dockWidgetContents)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/plugins/APIS/icons/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiCancelCenterPointBtn.setIcon(icon4)
        self.uiCancelCenterPointBtn.setIconSize(QtCore.QSize(11, 11))
        self.uiCancelCenterPointBtn.setObjectName("uiCancelCenterPointBtn")
        self.uiMappingDetailsGridLayout.addWidget(self.uiCancelCenterPointBtn, 1, 1, 1, 1)
        self.uiSaveCenterPointBtn = QtWidgets.QPushButton(self.dockWidgetContents)
        self.uiSaveCenterPointBtn.setIcon(icon3)
        self.uiSaveCenterPointBtn.setIconSize(QtCore.QSize(11, 11))
        self.uiSaveCenterPointBtn.setObjectName("uiSaveCenterPointBtn")
        self.uiMappingDetailsGridLayout.addWidget(self.uiSaveCenterPointBtn, 1, 0, 1, 1)
        self.uiMappingDetailsTBox = QtWidgets.QToolBox(self.dockWidgetContents)
        self.uiMappingDetailsTBox.setEnabled(True)
        self.uiMappingDetailsTBox.setObjectName("uiMappingDetailsTBox")
        self.pageOblique = QtWidgets.QWidget()
        self.pageOblique.setGeometry(QtCore.QRect(0, 0, 375, 312))
        self.pageOblique.setObjectName("pageOblique")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.pageOblique)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_8 = QtWidgets.QLabel(self.pageOblique)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 0, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.pageOblique)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 0, 2, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.pageOblique)
        self.label_13.setObjectName("label_13")
        self.gridLayout_3.addWidget(self.label_13, 2, 0, 1, 1)
        self.uiProjectObliqueCombo = QtWidgets.QComboBox(self.pageOblique)
        self.uiProjectObliqueCombo.setObjectName("uiProjectObliqueCombo")
        self.gridLayout_3.addWidget(self.uiProjectObliqueCombo, 3, 1, 1, 3)
        self.uiImageNumberToSpn = QtWidgets.QSpinBox(self.pageOblique)
        self.uiImageNumberToSpn.setMinimum(1)
        self.uiImageNumberToSpn.setMaximum(999)
        self.uiImageNumberToSpn.setObjectName("uiImageNumberToSpn")
        self.gridLayout_3.addWidget(self.uiImageNumberToSpn, 0, 3, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.pageOblique)
        self.label_11.setObjectName("label_11")
        self.gridLayout_3.addWidget(self.label_11, 1, 2, 1, 1)
        self.uiImageNumberFromSpn = QtWidgets.QSpinBox(self.pageOblique)
        self.uiImageNumberFromSpn.setMinimum(1)
        self.uiImageNumberFromSpn.setMaximum(999)
        self.uiImageNumberFromSpn.setObjectName("uiImageNumberFromSpn")
        self.gridLayout_3.addWidget(self.uiImageNumberFromSpn, 0, 1, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.pageOblique)
        self.label_14.setObjectName("label_14")
        self.gridLayout_3.addWidget(self.label_14, 3, 0, 1, 1)
        self.uiImageDiameterSpn = QtWidgets.QSpinBox(self.pageOblique)
        self.uiImageDiameterSpn.setMinimum(150)
        self.uiImageDiameterSpn.setMaximum(3000)
        self.uiImageDiameterSpn.setProperty("value", 350)
        self.uiImageDiameterSpn.setObjectName("uiImageDiameterSpn")
        self.gridLayout_3.addWidget(self.uiImageDiameterSpn, 1, 1, 1, 1)
        self.uiAddProjectObliqueBtn = QtWidgets.QPushButton(self.pageOblique)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiAddProjectObliqueBtn.sizePolicy().hasHeightForWidth())
        self.uiAddProjectObliqueBtn.setSizePolicy(sizePolicy)
        self.uiAddProjectObliqueBtn.setText("")
        self.uiAddProjectObliqueBtn.setIcon(icon3)
        self.uiAddProjectObliqueBtn.setObjectName("uiAddProjectObliqueBtn")
        self.gridLayout_3.addWidget(self.uiAddProjectObliqueBtn, 4, 4, 1, 1)
        self.uiRemoveProjectObliqueBtn = QtWidgets.QPushButton(self.pageOblique)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiRemoveProjectObliqueBtn.sizePolicy().hasHeightForWidth())
        self.uiRemoveProjectObliqueBtn.setSizePolicy(sizePolicy)
        self.uiRemoveProjectObliqueBtn.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/plugins/APIS/icons/remove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiRemoveProjectObliqueBtn.setIcon(icon5)
        self.uiRemoveProjectObliqueBtn.setObjectName("uiRemoveProjectObliqueBtn")
        self.gridLayout_3.addWidget(self.uiRemoveProjectObliqueBtn, 5, 4, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.pageOblique)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 1, 0, 1, 1)
        self.uiFlightHeightObliqueSpn = QtWidgets.QSpinBox(self.pageOblique)
        self.uiFlightHeightObliqueSpn.setMaximum(99999)
        self.uiFlightHeightObliqueSpn.setObjectName("uiFlightHeightObliqueSpn")
        self.gridLayout_3.addWidget(self.uiFlightHeightObliqueSpn, 1, 3, 1, 1)
        self.uiProjectObliqueList = QtWidgets.QListWidget(self.pageOblique)
        self.uiProjectObliqueList.setObjectName("uiProjectObliqueList")
        self.gridLayout_3.addWidget(self.uiProjectObliqueList, 4, 0, 3, 4)
        self.uiImageDescriptionObliqueEdit = QtWidgets.QLineEdit(self.pageOblique)
        self.uiImageDescriptionObliqueEdit.setObjectName("uiImageDescriptionObliqueEdit")
        self.gridLayout_3.addWidget(self.uiImageDescriptionObliqueEdit, 2, 1, 1, 3)
        self.uiEditProjectTableObliqueBtn = QtWidgets.QPushButton(self.pageOblique)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiEditProjectTableObliqueBtn.sizePolicy().hasHeightForWidth())
        self.uiEditProjectTableObliqueBtn.setSizePolicy(sizePolicy)
        self.uiEditProjectTableObliqueBtn.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/plugins/APIS/icons/sketch.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiEditProjectTableObliqueBtn.setIcon(icon6)
        self.uiEditProjectTableObliqueBtn.setObjectName("uiEditProjectTableObliqueBtn")
        self.gridLayout_3.addWidget(self.uiEditProjectTableObliqueBtn, 3, 4, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_3)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/plugins/APIS/icons/kartierung_schraeg.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiMappingDetailsTBox.addItem(self.pageOblique, icon7, "")
        self.pageVertical = QtWidgets.QWidget()
        self.pageVertical.setGeometry(QtCore.QRect(0, 0, 358, 317))
        self.pageVertical.setObjectName("pageVertical")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.pageVertical)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.uiEditProjectTableVerticalBtn = QtWidgets.QPushButton(self.pageVertical)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiEditProjectTableVerticalBtn.sizePolicy().hasHeightForWidth())
        self.uiEditProjectTableVerticalBtn.setSizePolicy(sizePolicy)
        self.uiEditProjectTableVerticalBtn.setText("")
        self.uiEditProjectTableVerticalBtn.setIcon(icon6)
        self.uiEditProjectTableVerticalBtn.setObjectName("uiEditProjectTableVerticalBtn")
        self.gridLayout.addWidget(self.uiEditProjectTableVerticalBtn, 3, 2, 1, 1)
        self.uiRemoveProjectVerticalBtn = QtWidgets.QPushButton(self.pageVertical)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiRemoveProjectVerticalBtn.sizePolicy().hasHeightForWidth())
        self.uiRemoveProjectVerticalBtn.setSizePolicy(sizePolicy)
        self.uiRemoveProjectVerticalBtn.setText("")
        self.uiRemoveProjectVerticalBtn.setIcon(icon5)
        self.uiRemoveProjectVerticalBtn.setObjectName("uiRemoveProjectVerticalBtn")
        self.gridLayout.addWidget(self.uiRemoveProjectVerticalBtn, 5, 2, 1, 1)
        self.uiImageNumberSpn = QtWidgets.QSpinBox(self.pageVertical)
        self.uiImageNumberSpn.setMinimum(1)
        self.uiImageNumberSpn.setMaximum(999)
        self.uiImageNumberSpn.setObjectName("uiImageNumberSpn")
        self.gridLayout.addWidget(self.uiImageNumberSpn, 0, 1, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.pageVertical)
        self.label_16.setObjectName("label_16")
        self.gridLayout.addWidget(self.label_16, 3, 0, 1, 1)
        self.uiProjectVerticalList = QtWidgets.QListWidget(self.pageVertical)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiProjectVerticalList.sizePolicy().hasHeightForWidth())
        self.uiProjectVerticalList.setSizePolicy(sizePolicy)
        self.uiProjectVerticalList.setObjectName("uiProjectVerticalList")
        self.gridLayout.addWidget(self.uiProjectVerticalList, 4, 0, 3, 2)
        self.uiFlightHeightVerticalSpn = QtWidgets.QSpinBox(self.pageVertical)
        self.uiFlightHeightVerticalSpn.setMinimum(1)
        self.uiFlightHeightVerticalSpn.setMaximum(99999)
        self.uiFlightHeightVerticalSpn.setProperty("value", 100)
        self.uiFlightHeightVerticalSpn.setObjectName("uiFlightHeightVerticalSpn")
        self.gridLayout.addWidget(self.uiFlightHeightVerticalSpn, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.pageVertical)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 1)
        self.uiAddProjectVerticalBtn = QtWidgets.QPushButton(self.pageVertical)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiAddProjectVerticalBtn.sizePolicy().hasHeightForWidth())
        self.uiAddProjectVerticalBtn.setSizePolicy(sizePolicy)
        self.uiAddProjectVerticalBtn.setText("")
        self.uiAddProjectVerticalBtn.setIcon(icon3)
        self.uiAddProjectVerticalBtn.setObjectName("uiAddProjectVerticalBtn")
        self.gridLayout.addWidget(self.uiAddProjectVerticalBtn, 4, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.pageVertical)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)
        self.uiProjectVerticalCombo = QtWidgets.QComboBox(self.pageVertical)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiProjectVerticalCombo.sizePolicy().hasHeightForWidth())
        self.uiProjectVerticalCombo.setSizePolicy(sizePolicy)
        self.uiProjectVerticalCombo.setObjectName("uiProjectVerticalCombo")
        self.gridLayout.addWidget(self.uiProjectVerticalCombo, 3, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.pageVertical)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 2, 0, 1, 1)
        self.uiImageDescriptionVerticalEdit = QtWidgets.QLineEdit(self.pageVertical)
        self.uiImageDescriptionVerticalEdit.setObjectName("uiImageDescriptionVerticalEdit")
        self.gridLayout.addWidget(self.uiImageDescriptionVerticalEdit, 2, 1, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/plugins/APIS/icons/kartierung_senkrecht.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiMappingDetailsTBox.addItem(self.pageVertical, icon8, "")
        self.uiMappingDetailsGridLayout.addWidget(self.uiMappingDetailsTBox, 0, 0, 1, 2)
        self.verticalLayout.addLayout(self.uiMappingDetailsGridLayout)
        self.line_3 = QtWidgets.QFrame(self.dockWidgetContents)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout.addWidget(self.line_3)
        self.uiFootprintsVerticalLayout = QtWidgets.QVBoxLayout()
        self.uiFootprintsVerticalLayout.setObjectName("uiFootprintsVerticalLayout")
        self.label_15 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_15.setObjectName("label_15")
        self.uiFootprintsVerticalLayout.addWidget(self.label_15)
        self.uiGenerateFootprintsBtn = QtWidgets.QPushButton(self.dockWidgetContents)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/plugins/APIS/icons/footprints.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiGenerateFootprintsBtn.setIcon(icon9)
        self.uiGenerateFootprintsBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiGenerateFootprintsBtn.setObjectName("uiGenerateFootprintsBtn")
        self.uiFootprintsVerticalLayout.addWidget(self.uiGenerateFootprintsBtn)
        self.verticalLayout.addLayout(self.uiFootprintsVerticalLayout)
        self.line_4 = QtWidgets.QFrame(self.dockWidgetContents)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.verticalLayout.addWidget(self.line_4)
        self.uiAutoImportHorizontalLayout = QtWidgets.QVBoxLayout()
        self.uiAutoImportHorizontalLayout.setObjectName("uiAutoImportHorizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_2.setObjectName("label_2")
        self.uiAutoImportHorizontalLayout.addWidget(self.label_2)
        self.uiAutoImportBtn = QtWidgets.QPushButton(self.dockWidgetContents)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/plugins/APIS/icons/monoplot.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uiAutoImportBtn.setIcon(icon10)
        self.uiAutoImportBtn.setIconSize(QtCore.QSize(24, 24))
        self.uiAutoImportBtn.setObjectName("uiAutoImportBtn")
        self.uiAutoImportHorizontalLayout.addWidget(self.uiAutoImportBtn)
        self.verticalLayout.addLayout(self.uiAutoImportHorizontalLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        apisImageMappingDialog.setWidget(self.dockWidgetContents)

        self.retranslateUi(apisImageMappingDialog)
        self.uiMappingDetailsTBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(apisImageMappingDialog)

    def retranslateUi(self, apisImageMappingDialog):
        _translate = QtCore.QCoreApplication.translate
        apisImageMappingDialog.setWindowTitle(_translate("apisImageMappingDialog", "APIS Bilder Kartierung"))
        self.label_4.setText(_translate("apisImageMappingDialog", "1. Film auswählen"))
        self.uiFilmSelectionBtn.setText(_translate("apisImageMappingDialog", "Filmnummer"))
        self.label.setText(_translate("apisImageMappingDialog", "X:"))
        self.uiYCoordinateLbl.setText(_translate("apisImageMappingDialog", "---"))
        self.label_5.setText(_translate("apisImageMappingDialog", "2. Bildmittelpunkt(e) setzen"))
        self.uiXCoordinateLbl.setText(_translate("apisImageMappingDialog", "---"))
        self.label_3.setText(_translate("apisImageMappingDialog", "Y:"))
        self.uiAddCenterPointBtn.setText(_translate("apisImageMappingDialog", "Hinzufügen"))
        self.uiCancelCenterPointBtn.setText(_translate("apisImageMappingDialog", "Abbrechen"))
        self.uiSaveCenterPointBtn.setText(_translate("apisImageMappingDialog", "Hinzufügen"))
        self.label_8.setText(_translate("apisImageMappingDialog", "Bildnummer von:"))
        self.label_9.setText(_translate("apisImageMappingDialog", "bis:"))
        self.label_13.setText(_translate("apisImageMappingDialog", "Beschreibung:"))
        self.label_11.setText(_translate("apisImageMappingDialog", "Höhe:"))
        self.label_14.setText(_translate("apisImageMappingDialog", "Projekt(e):"))
        self.label_10.setText(_translate("apisImageMappingDialog", "Durchmesser:"))
        self.uiMappingDetailsTBox.setItemText(self.uiMappingDetailsTBox.indexOf(self.pageOblique), _translate("apisImageMappingDialog", "schräg"))
        self.label_16.setText(_translate("apisImageMappingDialog", "Projekt(e):"))
        self.label_6.setText(_translate("apisImageMappingDialog", "Bildnummer:"))
        self.label_7.setText(_translate("apisImageMappingDialog", "Höhe:"))
        self.label_12.setText(_translate("apisImageMappingDialog", "Beschreibung:"))
        self.uiMappingDetailsTBox.setItemText(self.uiMappingDetailsTBox.indexOf(self.pageVertical), _translate("apisImageMappingDialog", "senkrecht"))
        self.label_15.setText(_translate("apisImageMappingDialog", "3. Footprints erstellen"))
        self.uiGenerateFootprintsBtn.setText(_translate("apisImageMappingDialog", "Footprints erstellen"))
        self.label_2.setText(_translate("apisImageMappingDialog", "Auto Import:"))
        self.uiAutoImportBtn.setText(_translate("apisImageMappingDialog", "Auto Import Digitale Bilder"))

import resource_rc
