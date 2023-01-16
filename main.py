# -*- coding: utf-8 -*-
# coding=gbk

import sys
import platform
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *

# GUI FILE
from app_modules import *
from ui_search_engine import SearchEngineWindow
from core.sys_config import *


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        UIFunctions.removeTitleBar(True)

        # 윈도우 타이틀
        self.setWindowTitle(WINDOW_TITLE)
        UIFunctions.labelTitle(self, 'Delus')
        UIFunctions.labelDescription(self, '')

        # 윈도우 기본 사이즈
        startSize = QSize(1000, 720)
        self.resize(startSize)
        self.setMinimumSize(startSize)

        # 토글 메뉴 사이즈
        self.ui.btn_toggle_menu.clicked.connect(lambda: UIFunctions.toggleMenu(self, 220, True))

        # 커스텀 메뉴 추가
        self.ui.stackedWidget.setMinimumWidth(20)
        UIFunctions.addNewMenu(self, "Search", "btn_home", "url(:/16x16/icons/16x16/cil-find-in-page.png)", True)
        UIFunctions.addNewMenu(self, "Realtime", "btn_drive_manager", "url(:/16x16/icons/16x16/cil-devices.png)", True)
        UIFunctions.addNewMenu(self, "Delus", "btn_widgets", "url(:/16x16/icons/16x16/cil-equalizer.png)", False)

        # 시작 메뉴
        UIFunctions.selectStandardMenu(self, "btn_home")

        # 시작페이지
        self.ui.stackedWidget.setCurrentWidget(self.ui.SearchEngine_widget)

        # 유저 아이콘 show hide
        UIFunctions.userIcon(self, "Delus", "", True)

        # 윈도우 Resize, Move
        def moveWindow(event):
            if UIFunctions.returStatus() == 1:
                UIFunctions.maximize_restore(self)

            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        # 위젯 Move
        self.ui.frame_label_top_btns.mouseMoveEvent = moveWindow

        UIFunctions.uiDefinitions(self)

        # 테이블 위젯 파라미터
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.show()

    def Button(self):
        """클릭에 따라 페이지가 변한다."""
        btnWidget = self.sender()

        # 기본 페이지 DetaInfo
        if btnWidget.objectName() == "btn_home":
            self.ui.Settings_widget.setParent(None)
            self.ui.stackedWidget.addWidget(self.ui.SearchEngine_widget)
            UIFunctions.resetStyle(self, "btn_home")
            UIFunctions.labelPage(self, "RS")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

        # 두번째 페이지 Drive Manager
        if btnWidget.objectName() == "btn_drive_manager":
            self.ui.SearchEngine_widget.setParent(None)
            self.ui.stackedWidget.addWidget(self.ui.Settings_widget)
            UIFunctions.resetStyle(self, "btn_drive_manager")
            UIFunctions.labelPage(self, "Drive_Manager")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

    # 마우스 이벤트
    def eventFilter(self, watched, event):
        if watched == self.le and event.type() == QtCore.QEvent.MouseButtonDblClick:
            print("pos: ", event.pos())

    # 마우스 클릭 이벤트
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    window = MainWindow()
    sys.exit(app.exec_())