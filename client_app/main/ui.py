# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 700)
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(800, 700))
        self.action_run_online = QAction(MainWindow)
        self.action_run_online.setObjectName(u"action_run_online")
        self.action_run_online.setCheckable(True)
        self.action_run_offline = QAction(MainWindow)
        self.action_run_offline.setObjectName(u"action_run_offline")
        self.action_run_offline.setCheckable(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"QWidget{\n"
"	background-color: rgb(248, 255, 253);\n"
"}\n"
"QPushButton{\n"
"	background-color: rgb(206, 227, 255);\n"
"}")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 30, -1, -1)
        self.camera_page_btn = QPushButton(self.widget)
        self.camera_page_btn.setObjectName(u"camera_page_btn")
        self.camera_page_btn.setCheckable(True)

        self.verticalLayout_2.addWidget(self.camera_page_btn)

        self.networking_page_btn = QPushButton(self.widget)
        self.networking_page_btn.setObjectName(u"networking_page_btn")
        self.networking_page_btn.setCheckable(True)

        self.verticalLayout_2.addWidget(self.networking_page_btn)

        self.offine_project_select_page_btn = QPushButton(self.widget)
        self.offine_project_select_page_btn.setObjectName(u"offine_project_select_page_btn")
        self.offine_project_select_page_btn.setCheckable(True)

        self.verticalLayout_2.addWidget(self.offine_project_select_page_btn)

        self.person_select_page_btn = QPushButton(self.widget)
        self.person_select_page_btn.setObjectName(u"person_select_page_btn")
        self.person_select_page_btn.setCheckable(True)

        self.verticalLayout_2.addWidget(self.person_select_page_btn)

        self.callibration_page_btn = QPushButton(self.widget)
        self.callibration_page_btn.setObjectName(u"callibration_page_btn")
        self.callibration_page_btn.setCheckable(True)

        self.verticalLayout_2.addWidget(self.callibration_page_btn)

        self.tracking_page_btn = QPushButton(self.widget)
        self.tracking_page_btn.setObjectName(u"tracking_page_btn")
        self.tracking_page_btn.setCheckable(True)

        self.verticalLayout_2.addWidget(self.tracking_page_btn)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.show_scene_window_btn = QPushButton(self.widget)
        self.show_scene_window_btn.setObjectName(u"show_scene_window_btn")

        self.verticalLayout_2.addWidget(self.show_scene_window_btn)


        self.horizontalLayout.addWidget(self.widget)

        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout = QVBoxLayout(self.widget_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.widget_2)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_camera = QWidget()
        self.page_camera.setObjectName(u"page_camera")
        self.page_camera_layout = QVBoxLayout(self.page_camera)
        self.page_camera_layout.setSpacing(0)
        self.page_camera_layout.setObjectName(u"page_camera_layout")
        self.page_camera_layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.page_camera)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.page_camera_layout.addWidget(self.label)

        self.page_camera_content = QWidget(self.page_camera)
        self.page_camera_content.setObjectName(u"page_camera_content")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.page_camera_content.sizePolicy().hasHeightForWidth())
        self.page_camera_content.setSizePolicy(sizePolicy2)
        self.verticalLayout_7 = QVBoxLayout(self.page_camera_content)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)

        self.page_camera_layout.addWidget(self.page_camera_content)

        self.stackedWidget.addWidget(self.page_camera)
        self.page_offline_project_select = QWidget()
        self.page_offline_project_select.setObjectName(u"page_offline_project_select")
        self.verticalLayout_3 = QVBoxLayout(self.page_offline_project_select)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.page_offline_project_select)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.verticalLayout_3.addWidget(self.label_4)

        self.page_offline_project_select_content = QWidget(self.page_offline_project_select)
        self.page_offline_project_select_content.setObjectName(u"page_offline_project_select_content")
        sizePolicy2.setHeightForWidth(self.page_offline_project_select_content.sizePolicy().hasHeightForWidth())
        self.page_offline_project_select_content.setSizePolicy(sizePolicy2)
        self.verticalLayout_4 = QVBoxLayout(self.page_offline_project_select_content)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_3.addWidget(self.page_offline_project_select_content)

        self.stackedWidget.addWidget(self.page_offline_project_select)
        self.page_select_person = QWidget()
        self.page_select_person.setObjectName(u"page_select_person")
        self.verticalLayout_10 = QVBoxLayout(self.page_select_person)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.label_6 = QLabel(self.page_select_person)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font)
        self.label_6.setTextFormat(Qt.AutoText)
        self.label_6.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.verticalLayout_10.addWidget(self.label_6)

        self.page_select_person_content = QWidget(self.page_select_person)
        self.page_select_person_content.setObjectName(u"page_select_person_content")
        sizePolicy2.setHeightForWidth(self.page_select_person_content.sizePolicy().hasHeightForWidth())
        self.page_select_person_content.setSizePolicy(sizePolicy2)
        self.verticalLayout_11 = QVBoxLayout(self.page_select_person_content)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_10.addWidget(self.page_select_person_content)

        self.stackedWidget.addWidget(self.page_select_person)
        self.page_network = QWidget()
        self.page_network.setObjectName(u"page_network")
        self.page_network_layout = QVBoxLayout(self.page_network)
        self.page_network_layout.setSpacing(0)
        self.page_network_layout.setObjectName(u"page_network_layout")
        self.page_network_layout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.page_network)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.page_network_layout.addWidget(self.label_2)

        self.page_network_content = QWidget(self.page_network)
        self.page_network_content.setObjectName(u"page_network_content")
        sizePolicy2.setHeightForWidth(self.page_network_content.sizePolicy().hasHeightForWidth())
        self.page_network_content.setSizePolicy(sizePolicy2)
        self.verticalLayout_6 = QVBoxLayout(self.page_network_content)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)

        self.page_network_layout.addWidget(self.page_network_content)

        self.stackedWidget.addWidget(self.page_network)
        self.page_callibration = QWidget()
        self.page_callibration.setObjectName(u"page_callibration")
        self.verticalLayout_8 = QVBoxLayout(self.page_callibration)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.page_callibration)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font)
        self.label_5.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.verticalLayout_8.addWidget(self.label_5)

        self.page_callibration_content = QWidget(self.page_callibration)
        self.page_callibration_content.setObjectName(u"page_callibration_content")
        sizePolicy2.setHeightForWidth(self.page_callibration_content.sizePolicy().hasHeightForWidth())
        self.page_callibration_content.setSizePolicy(sizePolicy2)
        self.verticalLayout_9 = QVBoxLayout(self.page_callibration_content)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_8.addWidget(self.page_callibration_content)

        self.stackedWidget.addWidget(self.page_callibration)
        self.page_tracking = QWidget()
        self.page_tracking.setObjectName(u"page_tracking")
        self.page_tracking_layout = QVBoxLayout(self.page_tracking)
        self.page_tracking_layout.setSpacing(0)
        self.page_tracking_layout.setObjectName(u"page_tracking_layout")
        self.page_tracking_layout.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.page_tracking)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.page_tracking_layout.addWidget(self.label_3)

        self.page_tracking_content = QWidget(self.page_tracking)
        self.page_tracking_content.setObjectName(u"page_tracking_content")
        sizePolicy2.setHeightForWidth(self.page_tracking_content.sizePolicy().hasHeightForWidth())
        self.page_tracking_content.setSizePolicy(sizePolicy2)
        self.verticalLayout_5 = QVBoxLayout(self.page_tracking_content)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)

        self.page_tracking_layout.addWidget(self.page_tracking_content)

        self.stackedWidget.addWidget(self.page_tracking)

        self.verticalLayout.addWidget(self.stackedWidget)


        self.horizontalLayout.addWidget(self.widget_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 25))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
#if QT_CONFIG(shortcut)
#endif // QT_CONFIG(shortcut)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.action_run_online)
        self.menu.addAction(self.action_run_offline)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u041a\u043b\u0438\u0435\u043d\u0442 \u0421\u041e\u0413\u0420\u0412", None))
        self.action_run_online.setText(QCoreApplication.translate("MainWindow", u"\u041e\u043d\u043b\u0430\u0439\u043d", None))
        self.action_run_offline.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0444\u043b\u0430\u0439\u043d", None))
        self.camera_page_btn.setText(QCoreApplication.translate("MainWindow", u"\u041a\u0430\u043c\u0435\u0440\u0430", None))
        self.networking_page_btn.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0435\u0442\u044c", None))
        self.offine_project_select_page_btn.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0431\u043e\u0440 \u043f\u0440\u043e\u0435\u043a\u0442\u0430", None))
        self.person_select_page_btn.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0431\u043e\u0440\n"
"\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f", None))
        self.callibration_page_btn.setText(QCoreApplication.translate("MainWindow", u"\u041a\u0430\u043b\u0438\u0431\u0440\u043e\u0432\u043a\u0430", None))
        self.tracking_page_btn.setText(QCoreApplication.translate("MainWindow", u"\u0422\u0440\u0435\u043a\u0438\u043d\u0433", None))
        self.show_scene_window_btn.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c\n"
"\u0441\u0446\u0435\u043d\u0443", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043a\u0430\u043c\u0435\u0440\u044b", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0444\u043b\u0430\u0439\u043d \u0440\u0435\u0436\u0438\u043c \u0440\u0430\u0431\u043e\u0442\u044b", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0431\u043e\u0440 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u0441\u0435\u0442\u0438", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u041a\u0430\u043b\u0438\u0431\u0440\u043e\u0432\u043a\u0430 \u0432\u0437\u0433\u043b\u044f\u0434\u0430", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u0442\u0440\u0435\u043a\u0438\u043d\u0433\u0430", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u0420\u0435\u0436\u0438\u043c \u0440\u0430\u0431\u043e\u0442\u044b", None))
    # retranslateUi

