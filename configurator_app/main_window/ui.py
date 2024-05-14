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
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(865, 705)
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
        self.configure_projects_btn = QPushButton(self.widget)
        self.configure_projects_btn.setObjectName(u"configure_projects_btn")
        self.configure_projects_btn.setCheckable(True)

        self.verticalLayout_2.addWidget(self.configure_projects_btn)

        self.configure_scene_objs_btn = QPushButton(self.widget)
        self.configure_scene_objs_btn.setObjectName(u"configure_scene_objs_btn")
        self.configure_scene_objs_btn.setEnabled(False)
        self.configure_scene_objs_btn.setCheckable(True)

        self.verticalLayout_2.addWidget(self.configure_scene_objs_btn)

        self.configure_persons_btn = QPushButton(self.widget)
        self.configure_persons_btn.setObjectName(u"configure_persons_btn")
        self.configure_persons_btn.setEnabled(False)
        self.configure_persons_btn.setCheckable(True)

        self.verticalLayout_2.addWidget(self.configure_persons_btn)

        self.configure_rules_btn = QPushButton(self.widget)
        self.configure_rules_btn.setObjectName(u"configure_rules_btn")
        self.configure_rules_btn.setEnabled(False)
        self.configure_rules_btn.setCheckable(True)

        self.verticalLayout_2.addWidget(self.configure_rules_btn)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.show_scene_btn = QPushButton(self.widget)
        self.show_scene_btn.setObjectName(u"show_scene_btn")

        self.verticalLayout_2.addWidget(self.show_scene_btn)


        self.horizontalLayout.addWidget(self.widget)

        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout = QVBoxLayout(self.widget_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.widget_2)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_projects = QWidget()
        self.page_projects.setObjectName(u"page_projects")
        self.page_projects_layout = QVBoxLayout(self.page_projects)
        self.page_projects_layout.setObjectName(u"page_projects_layout")
        self.page_projects_layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.page_projects)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.page_projects_layout.addWidget(self.label)

        self.page_projects_content = QWidget(self.page_projects)
        self.page_projects_content.setObjectName(u"page_projects_content")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.page_projects_content.sizePolicy().hasHeightForWidth())
        self.page_projects_content.setSizePolicy(sizePolicy1)
        self.verticalLayout_5 = QVBoxLayout(self.page_projects_content)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)

        self.page_projects_layout.addWidget(self.page_projects_content)

        self.stackedWidget.addWidget(self.page_projects)
        self.page_scene_objs = QWidget()
        self.page_scene_objs.setObjectName(u"page_scene_objs")
        self.page_scene_objs_layout = QVBoxLayout(self.page_scene_objs)
        self.page_scene_objs_layout.setObjectName(u"page_scene_objs_layout")
        self.page_scene_objs_layout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.page_scene_objs)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.page_scene_objs_layout.addWidget(self.label_2)

        self.page_scene_objs_content = QWidget(self.page_scene_objs)
        self.page_scene_objs_content.setObjectName(u"page_scene_objs_content")
        sizePolicy1.setHeightForWidth(self.page_scene_objs_content.sizePolicy().hasHeightForWidth())
        self.page_scene_objs_content.setSizePolicy(sizePolicy1)
        self.verticalLayout_3 = QVBoxLayout(self.page_scene_objs_content)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)

        self.page_scene_objs_layout.addWidget(self.page_scene_objs_content)

        self.stackedWidget.addWidget(self.page_scene_objs)
        self.page_persons = QWidget()
        self.page_persons.setObjectName(u"page_persons")
        self.page_persons_layout = QVBoxLayout(self.page_persons)
        self.page_persons_layout.setObjectName(u"page_persons_layout")
        self.page_persons_layout.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.page_persons)
        self.label_3.setObjectName(u"label_3")
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.page_persons_layout.addWidget(self.label_3)

        self.page_persons_content = QWidget(self.page_persons)
        self.page_persons_content.setObjectName(u"page_persons_content")
        sizePolicy1.setHeightForWidth(self.page_persons_content.sizePolicy().hasHeightForWidth())
        self.page_persons_content.setSizePolicy(sizePolicy1)
        self.verticalLayout_4 = QVBoxLayout(self.page_persons_content)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)

        self.page_persons_layout.addWidget(self.page_persons_content)

        self.stackedWidget.addWidget(self.page_persons)
        self.page_rules = QWidget()
        self.page_rules.setObjectName(u"page_rules")
        self.page_rules_layout = QVBoxLayout(self.page_rules)
        self.page_rules_layout.setObjectName(u"page_rules_layout")
        self.page_rules_layout.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.page_rules)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.page_rules_layout.addWidget(self.label_4)

        self.page_rules_content = QWidget(self.page_rules)
        self.page_rules_content.setObjectName(u"page_rules_content")
        sizePolicy1.setHeightForWidth(self.page_rules_content.sizePolicy().hasHeightForWidth())
        self.page_rules_content.setSizePolicy(sizePolicy1)
        self.verticalLayout_6 = QVBoxLayout(self.page_rules_content)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)

        self.page_rules_layout.addWidget(self.page_rules_content)

        self.stackedWidget.addWidget(self.page_rules)

        self.verticalLayout.addWidget(self.stackedWidget)


        self.horizontalLayout.addWidget(self.widget_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 865, 25))
        MainWindow.setMenuBar(self.menubar)
#if QT_CONFIG(shortcut)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u041a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0442\u043e\u0440 \u0421\u041e\u0413\u0420\u0412", None))
        self.configure_projects_btn.setText(QCoreApplication.translate("MainWindow", u"\u0420\u0435\u0434\u0430\u043a\u0442\u043e\u0440 \u0441\u0446\u0435\u043d", None))
        self.configure_scene_objs_btn.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043e\u0431\u044a\u0435\u043a\u0442\u043e\u0432", None))
        self.configure_persons_btn.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430\n"
"\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439", None))
        self.configure_rules_btn.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043f\u0440\u0430\u0432\u0438\u043b\n"
"\u043d\u0430\u0431\u043b\u044e\u0434\u0435\u043d\u0438\u044f", None))
        self.show_scene_btn.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c\n"
"\u0441\u0446\u0435\u043d\u0443", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u0420\u0435\u0434\u0430\u043a\u0442\u043e\u0440 \u0441\u0446\u0435\u043d", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043e\u0431\u044a\u0435\u043a\u0442\u043e\u0432 \u0441\u0446\u0435\u043d\u044b", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043f\u0440\u0430\u0432\u0438\u043b \u043d\u0430\u0431\u043b\u044e\u0434\u0435\u043d\u0438\u044f", None))
    # retranslateUi

