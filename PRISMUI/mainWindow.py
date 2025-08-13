# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QSizePolicy,
    QWidget)

class Ui_App(object):
    def setupUi(self, App):
        if not App.objectName():
            App.setObjectName(u"App")
        App.resize(800, 600)
        self.menu = QWidget(App)
        self.menu.setObjectName(u"menu")
        self.menu.setGeometry(QRect(0, 0, 111, 601))
        self.menuLabel = QLabel(self.menu)
        self.menuLabel.setObjectName(u"menuLabel")
        self.menuLabel.setGeometry(QRect(0, 10, 111, 20))
        self.menuLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overviewButton = QPushButton(self.menu)
        self.overviewButton.setObjectName(u"overviewButton")
        self.overviewButton.setGeometry(QRect(0, 40, 111, 51))
        self.cpuButton = QPushButton(self.menu)
        self.cpuButton.setObjectName(u"cpuButton")
        self.cpuButton.setGeometry(QRect(0, 90, 111, 51))
        self.gpuButton = QPushButton(self.menu)
        self.gpuButton.setObjectName(u"gpuButton")
        self.gpuButton.setGeometry(QRect(0, 140, 111, 51))
        self.ramButton = QPushButton(self.menu)
        self.ramButton.setObjectName(u"ramButton")
        self.ramButton.setGeometry(QRect(0, 190, 111, 51))
        self.coolingButton = QPushButton(self.menu)
        self.coolingButton.setObjectName(u"coolingButton")
        self.coolingButton.setGeometry(QRect(0, 240, 111, 51))
        self.storageButton = QPushButton(self.menu)
        self.storageButton.setObjectName(u"storageButton")
        self.storageButton.setGeometry(QRect(0, 290, 111, 51))
        self.specButton = QPushButton(self.menu)
        self.specButton.setObjectName(u"specButton")
        self.specButton.setGeometry(QRect(0, 340, 111, 51))
        self.exitButton = QPushButton(self.menu)
        self.exitButton.setObjectName(u"exitButton")
        self.exitButton.setGeometry(QRect(0, 550, 111, 51))
        self.display = QWidget(App)
        self.display.setObjectName(u"display")
        self.display.setGeometry(QRect(110, 0, 691, 601))

        self.retranslateUi(App)

        QMetaObject.connectSlotsByName(App)
    # setupUi

    def retranslateUi(self, App):
        App.setWindowTitle(QCoreApplication.translate("App", u"App", None))
        self.menuLabel.setText(QCoreApplication.translate("App", u"Menu", None))
        self.overviewButton.setText(QCoreApplication.translate("App", u"Overview", None))
        self.cpuButton.setText(QCoreApplication.translate("App", u"CPU", None))
        self.gpuButton.setText(QCoreApplication.translate("App", u"GPU", None))
        self.ramButton.setText(QCoreApplication.translate("App", u"RAM", None))
        self.coolingButton.setText(QCoreApplication.translate("App", u"Cooling", None))
        self.storageButton.setText(QCoreApplication.translate("App", u"Storage", None))
        self.specButton.setText(QCoreApplication.translate("App", u"Specifications", None))
        self.exitButton.setText(QCoreApplication.translate("App", u"Exit", None))
    # retranslateUi

