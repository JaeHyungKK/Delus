# -*- coding: utf-8 -*-

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from core.db import *


class Result(object):

    def __init__(self, time, path, file, access_mask, name, ip):
        self.time = time
        self.path = path
        self.file = file
        self.access_mask = access_mask
        self.name = name
        self.ip = ip


class SearchEngineWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(SearchEngineWindow, self).__init__(*args, **kwargs)
        self.setup_ui()

    def setup_ui(self):

        self.main_layout = QHBoxLayout(self)
        self.SearchEngineGLayout = QGridLayout()
        self.SearchEngineGLayout.setObjectName(u'SearchEngineLayout')
        self.SearchEngineHLayout = QHBoxLayout()
        self.SearchEngineHLayout.setObjectName(u"SearchEngineHLayout")

        self.SearchEnginelabel = QLabel()
        self.SearchEnginelabel.setObjectName(u"label")
        self.SearchEnginelabel.setMinimumSize(QSize(0, 25))

        self.SearchEngine_COB_date = QComboBox()
        self.SearchEngine_COB_date.setObjectName(u'날짜')
        self.SearchEngine_COB_date.setMinimumSize(QSize(5, 45))
        self.SearchEngine_COB_date.addItem(u'2021')

        self.SearchEngine_COB_drive = QComboBox()
        self.SearchEngine_COB_drive.setObjectName(u'네트워크 드라이브')
        self.SearchEngine_COB_drive.setMinimumSize(QSize(5, 45))

        # 드라이브 리스트 콤보 박스
        _drive_list = [u'M:', u'P:', u'Q:', u'T:', u'W:', u'X:', u'Z:']
        for drive in _drive_list:
            self.SearchEngine_COB_drive.addItem(drive)

        self.SearchEngine_COB_cstatus = QComboBox()
        self.SearchEngine_COB_cstatus.setObjectName(u'변경 사항')
        self.SearchEngine_COB_cstatus.setMinimumSize(QSize(10, 45))

        # 삭제 했거나 이동한 파일 및 폴더
        self.SearchEngine_COB_cstatus.addItem(u'삭제')

        # 수정한 파일 및 폴더
        self.SearchEngine_COB_cstatus.addItem(u'수정')

        # 경로 체크박스
        self.SearchEngine_CHB_path = QCheckBox(u'경로')
        self.SearchEngine_CHB_path.setObjectName(u'경로')
        self.SearchEngine_CHB_path.setMinimumSize(QSize(0, 25))

        # 파일 체크박스
        self.SearchEngine_CHB_file = QCheckBox(u'파일')
        self.SearchEngine_CHB_file.setObjectName(u'파일')
        self.SearchEngine_CHB_file.setMinimumSize(QSize(0, 25))

        # 검색 필터
        self.SearchEngine_LineE_filter = QLineEdit()
        self.SearchEngine_LineE_filter.setObjectName(u'검색 필터')
        self.SearchEngine_LineE_filter.setPlaceholderText(u'경로 혹은 파일명(확장자 포함)을 정확하게 입력 해주세요')
        self.SearchEngine_LineE_filter.setMinimumSize(QSize(0, 30))
        self.SearchEngine_LineE_filter.returnPressed.connect(self.drive_select)

        # 검색 버튼
        self.SearchEngine_PB_search = QPushButton('검색')
        self.SearchEngine_PB_search.setStyleSheet("border-style: solid;\n"
                                                  "border-width: 1px;\n"
                                                  "border-color: Dark Gray")
        self.SearchEngine_PB_search.setObjectName(u'검색 버튼')
        self.SearchEngine_PB_search.setMinimumSize(QSize(100, 25))

        # 검색 버튼 클릭시 self.drive_select 함수로 연결
        self.SearchEngine_PB_search.clicked.connect(self.drive_select)
        self.SearchEngineSpacer = QSpacerItem(15, 80, QSizePolicy.Minimum, QSizePolicy.Fixed)

        # 생성한 요소들을 검색엔진 H레이아웃에 추가
        self.SearchEngineHLayout.addWidget(self.SearchEnginelabel)
        self.SearchEngineHLayout.addWidget(self.SearchEngine_COB_drive)
        self.SearchEngineHLayout.addWidget(self.SearchEngine_COB_cstatus)
        self.SearchEngineHLayout.addWidget(self.SearchEngine_CHB_path)
        self.SearchEngineHLayout.addWidget(self.SearchEngine_CHB_file)
        self.SearchEngineHLayout.addWidget(self.SearchEngine_LineE_filter)
        self.SearchEngineHLayout.addWidget(self.SearchEngine_PB_search)

        # 스페이서 추가
        self.SearchEngineGLayout.addItem(self.SearchEngineSpacer)

        # 검색 결과 그리드 레이아웃 생성 후 텍스트 라벨 추가
        self.SearchEngine_Result_Layout = QVBoxLayout()
        self.SearchEngineGLayout.addLayout(self.SearchEngineHLayout, 0, 0, 1, 1)

        self.text_label = QLabel(u'')
        self.SearchEngine_Result_Layout.addWidget(self.text_label)

        # 테이블 위젯 생성
        self.tableWidget_log_info = QTableWidget()
        self.tableWidget_log_info.setObjectName(u"데이터 정보 테이블 위젯")

        self.header = self.tableWidget_log_info.horizontalHeader()
        self.header.setStretchLastSection(True)

        self._HEADER = {
            'tableWidget_local': {
                'header': ["시간", "경로", "파일", "결과", "사용자", "IP"],
                'size': [175, 570, 270, 100, 70, 70]
            }, }

        headers = self._HEADER.get('tableWidget_local')
        headers = headers.get('header')

        self.tableWidget_log_info.setStyleSheet("background-color: #f5f5f5;\n"
                                                 "color: Black;")
        self.tableWidget_log_info.setColumnCount(6)
        self.tableWidget_log_info.setSortingEnabled(True)
        self.tableWidget_log_info.setHorizontalHeaderLabels(headers)
        self.tableWidget_log_info.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget_log_info.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tableWidget_log_info.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for idx, width in enumerate(self._HEADER['tableWidget_local']['size']):
            self.tableWidget_log_info.setColumnWidth(idx, width)

        # 검색엔진 그리드 레이아웃에 검색 레이아웃, 테이블 위젯 추가
        self.SearchEngineGLayout.addLayout(self.SearchEngine_Result_Layout, 1, 0, 1, 1)
        self.SearchEngineGLayout.addWidget(self.tableWidget_log_info, 2, 0, 1, 1)

        # 메인 레이아웃에 검색 레이아웃 추가
        self.main_layout.addLayout(self.SearchEngineGLayout)

    def set_label(self, txt):
        self.msg.setText(txt)

    def show_search_result(self, text_label):
        """검색 버튼 클릭시 UI에서 경로 혹은 파일 체크 박스 클릭 유무과 데이터 결과에 대한 메세지를 보여준다."""
        self.text_label.setText(text_label)

    def get_log_list(self, cstatus, drive):

        # 검색 결과 레이아웃의 프로그레스 바를 리프레시 해준다.
        for i in range(self.SearchEngine_Result_Layout.count()):
            if i == 1:
                self.SearchEngine_Result_Layout.itemAt(i).widget().deleteLater()

        self.tableWidget_log_info.setSortingEnabled(False)
        self.tableWidget_log_info.clearContents()
        if self.SearchEngine_CHB_path.isChecked() is False and \
           self.SearchEngine_CHB_file.isChecked() is False:
            text_label = u'경로 혹은 파일의 체크박스를 선택 해주세요'
            self.show_search_result(text_label)

        path_or_file = None
        if self.SearchEngine_CHB_path.isChecked():
            # 경로를 체크했으면
            path_or_file = 0
        if self.SearchEngine_CHB_file.isChecked():
            # 파일을 체크 했으면
            path_or_file = 1

        search_line_edit = self.SearchEngine_LineE_filter.text()

        if search_line_edit is None or search_line_edit == '':
            return

        if path_or_file is None:
            return

        # 프로그레스 바
        self.prog = QProgressBar()
        self.prog.setMaximum(1000)

        style = """
                QProgressBar {
                                border: solid grey;
                                border-radius: 15px;
                                color: black;
                                }
                                QProgressBar::chunk 
                                {
                                background-color: #33BEFF;
                                border-radius :15px;
                                }
                """
        self.prog.setStyleSheet(style)
        self.prog.setAlignment(Qt.AlignCenter)

        # 검색한 경로나 파일에 대한 정보를 DB에서 받아온다.
        res = get_log_info(cstatus=cstatus, drive=drive, line_edit=search_line_edit, path_or_file=path_or_file)
        result = []

        if res is not None:
            for time, path, file, access_mask, ip in res:
                 """
                 get_log_info를 통해 log_info DB 에서 받아온 IP정보를 가지고 
                 smart_maker 데이터베이스 users 테이블에서 매치되는 닉네임을 가지고 온다.  
                 """
                 name = str(get_name_from_ip(ip))
                 r = Result(time, path, file, access_mask, name, ip)
                 result.append(r)

            # 결과의 개수에 따라 테이블 위젯에 row 카운드 한다.
            self.tableWidget_log_info.setRowCount(len(result))

            # 1000이라는 값을 결과의 개수로 나눈다.
            divide_percent = 1000/len(result)

            # 테이블 위젯에 결과를 추가한다.
            for row, r in enumerate(result):
                item1 = QTableWidgetItem(r.time)
                item2 = QTableWidgetItem(r.path)
                item3 = QTableWidgetItem(r.file)
                item4 = QTableWidgetItem(r.access_mask)
                item5 = QTableWidgetItem(r.name)
                item6 = QTableWidgetItem(r.ip)
                self.tableWidget_log_info.setItem(row, 0, item1)
                self.tableWidget_log_info.setItem(row, 1, item2)
                self.tableWidget_log_info.setItem(row, 2, item3)
                self.tableWidget_log_info.setItem(row, 3, item4)
                self.tableWidget_log_info.setItem(row, 4, item5)
                self.tableWidget_log_info.setItem(row, 5, item6)

                # row는 0부터 시작하니까 +1을 한다.
                row_num = row + 1

                increase_value = row_num * divide_percent
                self.prog.setValue(increase_value)

            # 프로그레스 바 추가
            self.SearchEngine_Result_Layout.addWidget(self.prog)

            res_num = len(result)
            # 컬럼을 오름차순으로 바꿔준다.
            self.tableWidget_log_info.sortByColumn(0, Qt.AscendingOrder)
            self.tableWidget_log_info.setSortingEnabled(True)

            text_label = u'검색 결과: {}개의 데이터가 검색 되었습니다.'.format(res_num)
            self.show_search_result(text_label)
        else:
            text_label = u'검색 결과:  {} 데이터의 정보가 존재하지 않습니다.'.format(search_line_edit)
            self.show_search_result(text_label)
            self.tableWidget_log_info.setRowCount(0)

    def status_table_connector(self, drive):
        """삭제이면 delete_move_ 를 수정이면 modified_ 테이블을 선택한다. """
        self.cstatus = None
        if self.SearchEngine_COB_cstatus.currentText() == u"삭제":
            self.cstatus = u'delete_move_'
        if self.SearchEngine_COB_cstatus.currentText() == u"수정":
            self.cstatus = u'modified_'

        # 드라이브 명을 추가하고 데이터 베이스에 연결해서 검색 결과를 얻는다.
        self.get_log_list(cstatus=self.cstatus, drive=drive)

    def drive_select(self):
        """ UI에서 드라이브명을 선택하면 self.drive 변수를 그에 맞춘다. """
        self.drive = None
        drive_dic = {
            u'M:': u'm', u'P:': u'p',  u'Q:': 'q', u'T:': u't',
            u'W:': u'w', u'X:': u'x', u'Z:': u'z'
        }
        # 콤보박스의 현재 텍스트 값과 같은 key를 활용해서 Velue를 얻는다.
        self.drive = drive_dic[self.SearchEngine_COB_drive.currentText()]

        self.status_table_connector(drive=self.drive)
