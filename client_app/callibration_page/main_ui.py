# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'page.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QProgressBar,
    QPushButton, QScrollArea, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_page_callibration(object):
    def setupUi(self, page_callibration):
        if not page_callibration.objectName():
            page_callibration.setObjectName(u"page_callibration")
        page_callibration.resize(647, 472)
        self.verticalLayout = QVBoxLayout(page_callibration)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.start_callibration_btn = QPushButton(page_callibration)
        self.start_callibration_btn.setObjectName(u"start_callibration_btn")

        self.verticalLayout.addWidget(self.start_callibration_btn)

        self.stop_callibration_btn = QPushButton(page_callibration)
        self.stop_callibration_btn.setObjectName(u"stop_callibration_btn")

        self.verticalLayout.addWidget(self.stop_callibration_btn)

        self.widget = QWidget(page_callibration)
        self.widget.setObjectName(u"widget")
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)

        self.widget_2 = QWidget(self.widget)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_3 = QVBoxLayout(self.widget_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.add_callibration_point_btn = QPushButton(self.widget_2)
        self.add_callibration_point_btn.setObjectName(u"add_callibration_point_btn")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_callibration_point_btn.sizePolicy().hasHeightForWidth())
        self.add_callibration_point_btn.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.add_callibration_point_btn)

        self.export_data_btn = QPushButton(self.widget_2)
        self.export_data_btn.setObjectName(u"export_data_btn")

        self.verticalLayout_3.addWidget(self.export_data_btn)


        self.gridLayout.addWidget(self.widget_2, 1, 0, 1, 1)

        self.scrollArea = QScrollArea(self.widget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.callibration_points_content = QWidget()
        self.callibration_points_content.setObjectName(u"callibration_points_content")
        self.callibration_points_content.setGeometry(QRect(0, 0, 519, 331))
        self.verticalLayout_2 = QVBoxLayout(self.callibration_points_content)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setWidget(self.callibration_points_content)

        self.gridLayout.addWidget(self.scrollArea, 1, 1, 1, 1)


        self.verticalLayout.addWidget(self.widget)

        self.callibration_progress_bar = QProgressBar(page_callibration)
        self.callibration_progress_bar.setObjectName(u"callibration_progress_bar")
        self.callibration_progress_bar.setMaximum(10)
        self.callibration_progress_bar.setValue(0)
        self.callibration_progress_bar.setTextVisible(True)
        self.callibration_progress_bar.setInvertedAppearance(False)
        self.callibration_progress_bar.setTextDirection(QProgressBar.TopToBottom)

        self.verticalLayout.addWidget(self.callibration_progress_bar)

        self.finish_callibration_btn = QPushButton(page_callibration)
        self.finish_callibration_btn.setObjectName(u"finish_callibration_btn")

        self.verticalLayout.addWidget(self.finish_callibration_btn)


        self.retranslateUi(page_callibration)

        QMetaObject.connectSlotsByName(page_callibration)
    # setupUi

    def retranslateUi(self, page_callibration):
        page_callibration.setWindowTitle(QCoreApplication.translate("page_callibration", u"Form", None))
        self.start_callibration_btn.setText(QCoreApplication.translate("page_callibration", u"\u041d\u0430\u0447\u0430\u0442\u044c \u043a\u0430\u043b\u0438\u0431\u0440\u043e\u0432\u043a\u0443", None))
        self.stop_callibration_btn.setText(QCoreApplication.translate("page_callibration", u"\u041f\u0440\u0435\u0440\u0432\u0430\u0442\u044c \u043a\u0430\u043b\u0438\u0431\u0440\u043e\u0432\u043a\u0443", None))
        self.label.setText(QCoreApplication.translate("page_callibration", u"\u0413\u043e\u0442\u043e\u0432\u044b\u0435 \u0442\u043e\u0447\u043a\u0438 \u043a\u0430\u043b\u0438\u0431\u0440\u043e\u0432\u043a\u0438", None))
        self.add_callibration_point_btn.setText(QCoreApplication.translate("page_callibration", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0442\u043e\u0447\u043a\u0443\n"
"\u043a\u0430\u043b\u0438\u0431\u0440\u043e\u0432\u043a\u0438", None))
        self.export_data_btn.setText(QCoreApplication.translate("page_callibration", u"\u0412\u044b\u0433\u0440\u0443\u0437\u0438\u0442\u044c\n"
"\u0434\u0430\u043d\u043d\u044b\u0435", None))
        self.callibration_progress_bar.setFormat(QCoreApplication.translate("page_callibration", u"%v/%m", None))
        self.finish_callibration_btn.setText(QCoreApplication.translate("page_callibration", u"\u0417\u0430\u043a\u043e\u043d\u0447\u0438\u0442\u044c \u043a\u0430\u043b\u0438\u0431\u0440\u043e\u0432\u043a\u0443", None))
    # retranslateUi

