# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'graph_definition_dialog.ui',
# licensing of 'graph_definition_dialog.ui' applies.
#
# Created: Wed Mar 11 11:00:26 2020
#      by: pyside2-uic  running on PySide2 5.13.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(659, 746)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.nameLineEdit = QtWidgets.QLineEdit(Dialog)
        self.nameLineEdit.setMaximumSize(QtCore.QSize(120, 16777215))
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.horizontalLayout_3.addWidget(self.nameLineEdit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 0, 1, 1)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_11.addWidget(self.label_6)
        self.startNodeLabel = QtWidgets.QLabel(Dialog)
        self.startNodeLabel.setObjectName("startNodeLabel")
        self.horizontalLayout_11.addWidget(self.startNodeLabel)
        spacerItem2 = QtWidgets.QSpacerItem(176, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem2)
        self.gridLayout.addLayout(self.horizontalLayout_11, 2, 0, 1, 1)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.graphTreeWidget = QtWidgets.QTreeWidget(Dialog)
        self.graphTreeWidget.setObjectName("graphTreeWidget")
        self.horizontalLayout_4.addWidget(self.graphTreeWidget)
        self.horizontalLayout_9.addLayout(self.horizontalLayout_4)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_8.addWidget(self.label)
        self.nodeTypeComboBox = QtWidgets.QComboBox(Dialog)
        self.nodeTypeComboBox.setObjectName("nodeTypeComboBox")
        self.horizontalLayout_8.addWidget(self.nodeTypeComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.TransitionEdit = QtWidgets.QVBoxLayout()
        self.TransitionEdit.setObjectName("TransitionEdit")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.TransitionEdit.addWidget(self.label_2)
        self.transitionListWidget = QtWidgets.QListWidget(Dialog)
        self.transitionListWidget.setObjectName("transitionListWidget")
        self.TransitionEdit.addWidget(self.transitionListWidget)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.addTransitionButton = QtWidgets.QPushButton(Dialog)
        self.addTransitionButton.setObjectName("addTransitionButton")
        self.horizontalLayout_7.addWidget(self.addTransitionButton)
        self.removeTransitionButton = QtWidgets.QPushButton(Dialog)
        self.removeTransitionButton.setObjectName("removeTransitionButton")
        self.horizontalLayout_7.addWidget(self.removeTransitionButton)
        self.TransitionEdit.addLayout(self.horizontalLayout_7)
        self.verticalLayout.addLayout(self.TransitionEdit)
        self.horizontalLayout_9.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.horizontalLayout_9, 3, 0, 1, 1)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.addActionButton = QtWidgets.QPushButton(Dialog)
        self.addActionButton.setObjectName("addActionButton")
        self.horizontalLayout_10.addWidget(self.addActionButton)
        self.removeGraphItemButton = QtWidgets.QPushButton(Dialog)
        self.removeGraphItemButton.setObjectName("removeGraphItemButton")
        self.horizontalLayout_10.addWidget(self.removeGraphItemButton)
        self.setToStartNodeButton = QtWidgets.QPushButton(Dialog)
        self.setToStartNodeButton.setObjectName("setToStartNodeButton")
        self.horizontalLayout_10.addWidget(self.setToStartNodeButton)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem3)
        self.gridLayout.addLayout(self.horizontalLayout_10, 4, 0, 1, 1)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_6.addWidget(self.label_4)
        self.selectedModelLabel = QtWidgets.QLabel(Dialog)
        self.selectedModelLabel.setObjectName("selectedModelLabel")
        self.horizontalLayout_6.addWidget(self.selectedModelLabel)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem4)
        self.addModelButton = QtWidgets.QPushButton(Dialog)
        self.addModelButton.setObjectName("addModelButton")
        self.horizontalLayout_6.addWidget(self.addModelButton)
        self.replaceModelButton = QtWidgets.QPushButton(Dialog)
        self.replaceModelButton.setObjectName("replaceModelButton")
        self.horizontalLayout_6.addWidget(self.replaceModelButton)
        self.gridLayout.addLayout(self.horizontalLayout_6, 5, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.collectionTreeWidget = QtWidgets.QTreeWidget(Dialog)
        self.collectionTreeWidget.setObjectName("collectionTreeWidget")
        self.horizontalLayout.addWidget(self.collectionTreeWidget)
        self.modelListWidget = QtWidgets.QListWidget(Dialog)
        self.modelListWidget.setObjectName("modelListWidget")
        self.horizontalLayout.addWidget(self.modelListWidget)
        self.gridLayout.addLayout(self.horizontalLayout, 6, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem5)
        self.selectButton = QtWidgets.QPushButton(Dialog)
        self.selectButton.setObjectName("selectButton")
        self.horizontalLayout_2.addWidget(self.selectButton)
        self.cancelButton = QtWidgets.QPushButton(Dialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_2.addWidget(self.cancelButton)
        self.gridLayout.addLayout(self.horizontalLayout_2, 7, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Generate Graph Definition", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("Dialog", "Name", None, -1))
        self.label_5.setText(QtWidgets.QApplication.translate("Dialog", "Graph Hierarchy", None, -1))
        self.label_6.setText(QtWidgets.QApplication.translate("Dialog", "Start Node", None, -1))
        self.startNodeLabel.setText(QtWidgets.QApplication.translate("Dialog", "None", None, -1))
        self.graphTreeWidget.headerItem().setText(0, QtWidgets.QApplication.translate("Dialog", "Name", None, -1))
        self.graphTreeWidget.headerItem().setText(1, QtWidgets.QApplication.translate("Dialog", "Type", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "Node Type", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Dialog", "Transitions", None, -1))
        self.addTransitionButton.setText(QtWidgets.QApplication.translate("Dialog", "Add", None, -1))
        self.removeTransitionButton.setText(QtWidgets.QApplication.translate("Dialog", "Remove", None, -1))
        self.addActionButton.setText(QtWidgets.QApplication.translate("Dialog", "Add Action To Graph", None, -1))
        self.removeGraphItemButton.setText(QtWidgets.QApplication.translate("Dialog", "Remove Node", None, -1))
        self.setToStartNodeButton.setText(QtWidgets.QApplication.translate("Dialog", "Set To Start Node", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("Dialog", "Selected Model: ", None, -1))
        self.selectedModelLabel.setText(QtWidgets.QApplication.translate("Dialog", "None", None, -1))
        self.addModelButton.setText(QtWidgets.QApplication.translate("Dialog", "Add Model To Action", None, -1))
        self.replaceModelButton.setText(QtWidgets.QApplication.translate("Dialog", "Replace Model", None, -1))
        self.collectionTreeWidget.headerItem().setText(0, QtWidgets.QApplication.translate("Dialog", "Name", None, -1))
        self.collectionTreeWidget.headerItem().setText(1, QtWidgets.QApplication.translate("Dialog", "Type", None, -1))
        self.selectButton.setText(QtWidgets.QApplication.translate("Dialog", "Ok", None, -1))
        self.cancelButton.setText(QtWidgets.QApplication.translate("Dialog", "Cancel", None, -1))

