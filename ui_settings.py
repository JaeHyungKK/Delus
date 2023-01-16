# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import partial
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from core.db import *
from mysql.connector.errors import IntegrityError
# from core.config import *
import math


class User(object):
    def __init__(self, user_id, team, nickname, name, login_id, email_address, ip):
        self.user_id = user_id
        self.team = team
        self.nickname = nickname
        self.name = name
        self.login_id = login_id
        self.email_addres = email_address
        self.ip = ip


class SettingsWindow(QDialog):
    def __init__(self, *args, **kwargs):
        super(SettingsWindow, self).__init__(*args, **kwargs)

        self.nickname = None
        self.user = None
        self.setup_ui()

    def setup_ui(self):

        WINDOW_TITLE = 'Drive Manager'
        self.main_layout = QHBoxLayout(self)
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(800, 500)

        # 폰트는 맑은 고딕
        self.font = QFont()
        self.font.setFamily("Malgun Gothic")
        self.font.setStyleStrategy(QFont.PreferQuality)
        self.font.setPointSize(9)

        # 이 레이아웃은 메인 레이아웃의 우측에 포함된 레이아웃이다.
        self.right_layout = QVBoxLayout()
        self.main_layout.addLayout(self.right_layout)

        # 우측 레이아웃에 그룹박스를 차례대로 만들어준다.
        self.result_gb = QGroupBox()
        self.result_gb_layout = QVBoxLayout(self.result_gb)
        self.using_netdrive_list_gb = QGroupBox()

        ####################################################################################################
        # 사용자 추가 관련
        ####################################################################################################

        # 사용자 추가 레이아웃
        self.user_add_layout = QHBoxLayout()

        # 사용자 추가 버튼
        self.user_add_button = QPushButton('추가')
        self.user_add_button.setStyleSheet("border-style: solid;\n"
                                           "border-width: 1px;\n"
                                           "border-color: Dark Gray")
        self.user_add_button.setFont(self.font)
        self.user_add_button.setMinimumSize(QSize(100, 25))
        self.user_add_button.clicked.connect(self.add_user)

        # 사용자 삭제 버튼
        self.user_del_button = QPushButton('삭제')
        self.user_del_button.setStyleSheet("border-style: solid;\n"
                                           "border-width: 1px;\n"
                                           "border-color: Dark Gray")
        self.user_del_button.setFont(self.font)
        self.user_del_button.setMinimumSize(QSize(100, 25))
        self.user_del_button.clicked.connect(self.del_user_mbox)

        # 레이아웃에 사용자 라벨 추가
        self.user_add_layout.addWidget(QLabel('사용자'))

        # 사용자 추가 레이아웃에 사용자 추가 & 삭제 버튼을 추가한다.
        self.user_add_layout.addWidget(self.user_add_button)
        self.user_add_layout.addWidget(self.user_del_button)
        self.user_add_layout.addItem(QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Fixed))


        ####################################################################################################
        # 네트워크 드라이브 추가, 삭제, 편집 버튼 집합
        ####################################################################################################
        self.function_button_layout = QHBoxLayout()

        # 네트워크 드라이브 추가 버튼
        self.drive_add_button = QPushButton('추가')
        self.drive_add_button.setStyleSheet("border-style: solid;\n"
                                              "border-width: 1px;\n"
                                              "border-color: Dark Gray")
        self.drive_add_button.setFont(self.font)
        self.drive_add_button.setMinimumSize(QSize(100, 25))
        self.drive_add_button.clicked.connect(self.add_network_drive)

        self.function_button_layout.addWidget(QLabel('네트워크 드라이브'))
        # 기능 버튼 레이아웃에 네트워크 드라이브 버튼을 추가한다.
        self.function_button_layout.addWidget(self.drive_add_button)
        self.function_button_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        # 검색 라인에딧
        self.input_search = QLineEdit()
        # self.input_search.setText('')
        self.input_search.setPlaceholderText('팀명 혹은 닉네임이나 이름을 검색 후 선택 해주세요')
        self.input_search.setMinimumSize(QSize(0, 30))
        self.input_search.setStyleSheet("color: White;")
        self.input_search.returnPressed.connect(self.show_user_info)

        # 검색버튼
        self.search_button = QPushButton()
        self.search_button.setText(u'검색')
        self.search_button.setStyleSheet("border-style: solid;\n"
                                          "border-width: 1px;\n"
                                          "border-color: Dark Gray")
        self.search_button.setMinimumSize(QSize(100, 25))
        self.search_button.clicked.connect(self.show_user_info)

        self.all_user_list_button = QPushButton()
        self.all_user_list_button.setText(u'모든 사용자 보기')
        self.all_user_list_button.setStyleSheet("border-style: solid;\n"
                                         "border-width: 1px;\n"
                                         "border-color: Dark Gray")
        self.all_user_list_button.setMinimumSize(QSize(150, 25))
        self.all_user_list_button.clicked.connect(self.show_all_user_info)

        self.search_layout = QHBoxLayout()
        self.search_layout.addWidget(self.input_search)
        self.search_layout.addWidget(self.search_button)
        self.search_layout.addWidget(self.all_user_list_button)

        # 검색 결과 레이아웃 및 텍스트
        self.search_result_layout = QHBoxLayout()
        self.search_result_main_text = QLabel('')

        self.search_result_layout.addWidget(self.search_result_main_text)

        # 유저 테이블 헤더 컬럼 사이즈
        self._USER_HEADER = {
            'tableWidget_local': {
                'size': [50, 110, 100, 90, 90, 250, 110]
            }, }

        # 유저 테이블 위젯 생성
        self.user_table = QTableWidget()
        self.user_table.setStyleSheet("background-color: #f5f5f5;\n"
                                      "color: Black;")

        # self.user_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # Row 전체를 선택
        self.user_table.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.user_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 수정 불가

        user_column_headers = ["번호", "팀", "닉네임", "이름", "아이디", "이메일 주소", "아이피"]
        self.user_table.setMinimumHeight(100)
        self.user_table.setColumnCount(7)
        self.user_table.setHorizontalHeaderLabels(user_column_headers)

        # 필드값이 수정되었을 경우
        self.user_table.itemChanged.connect(self.modified_items)

        # 필드를 선택했을 경우 선택된 아이템(유저)에 대한 정보를 보여준다.
        self.user_table.clicked.connect(self.show_selecteditems)

        for idx, width in enumerate(self._USER_HEADER['tableWidget_local']['size']):
            self.user_table.setColumnWidth(idx, width)

        # 레이아웃과 위젯들을 차례대로 추가
        self.result_gb_layout.addLayout(self.search_layout)
        self.result_gb_layout.addLayout(self.search_result_layout)
        self.result_gb_layout.addWidget(self.user_table)
        self.result_gb_layout.addLayout(self.user_add_layout)

        # 스플리터
        self.right_spliiter = QSplitter(Qt.Vertical)
        self.right_spliiter.setHandleWidth(20)
        self.right_spliiter.addWidget(self.result_gb)
        self.right_spliiter.addWidget(self.using_netdrive_list_gb)

        self.right_layout.addWidget(self.right_spliiter)

        # 사용중인 드라이브 리스트 컬럼 사이즈
        self._NETDRIVE_LIST_HEADER = {
            'tableWidget_local': {
                'size': [70, 80, 110, 200]
            }, }

        # 사용자의 네트워크 드라이브 리스트 레이아웃
        user_title = u"사용중인 네트워크 드라이브"

        self.using_netdrive_Glayout = QGridLayout()

        # 사용중인 네트워크 드라이브 테이블 위젯 생성
        self.using_netdrive_table = QTableWidget()
        self.using_netdrive_table.setStyleSheet("background-color: #f5f5f5;\n"
                                                "color: Black;")
        self.using_netdrive_table.setMinimumSize(550, 200)
        self.using_netdrive_list_gb.setLayout(self.using_netdrive_Glayout)

        netdrive_column_headers = ["드라이브", "호스트", "아이피", "비고"]
        self.using_netdrive_table.setColumnCount(4)
        self.using_netdrive_table.setSortingEnabled(True)
        self.using_netdrive_table.setHorizontalHeaderLabels(netdrive_column_headers)
        self.using_netdrive_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # Row 전체를 선택
        self.using_netdrive_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.using_netdrive_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 수정 불가

        for idx, width in enumerate(self._NETDRIVE_LIST_HEADER['tableWidget_local']['size']):
            self.using_netdrive_table.setColumnWidth(idx, width)

        # 사용중인 네트워크 드라이브 레이아웃에 위젯들을 새로 고침 후 추가한다.
        self.drive_refresh_layout(user_title)
        self.using_netdrive_Glayout.addWidget(self.using_netdrive_table, 1, 0, 1, 1)
        self.using_netdrive_Glayout.addLayout(self.function_button_layout, 2, 0, 1, 1)

    def show_search_result(self, text_label):
        """ 검색 결과를 보여준다. """
        for i in range(self.search_result_layout.count()):
            self.search_result_layout.itemAt(i).widget().deleteLater()
        text_label = QLabel(text_label)
        self.search_result_layout.addWidget(text_label)

    def drive_refresh_layout(self, user_title):
        """선택된 사용자 네트워크 드라이브가 나오도록 user_title 리프레시 한다."""
        # 그리드 레이아웃에선 itemitemAtPosition(0, 0) 이렇게 사용
        # 첫번째 row만 지우고 새로운 user_title로 refresh
        if self.using_netdrive_Glayout.itemAtPosition(0, 0) is not None:
            self.using_netdrive_Glayout.itemAtPosition(0, 0).widget().deleteLater()

        user_title = QLabel(user_title)
        user_title.setStyleSheet("font: 18px;")
        self.using_netdrive_Glayout.addWidget(user_title, 0, 0, 1, 1)

    def system_inform_ui(self):

        import socket
        import subprocess

        self.status_gb = QGroupBox()
        self.status_layout = QFormLayout(self.status_gb)
        self.status_layout.setSpacing(17)
        # 레이블
        self.status_layout.setLabelAlignment(Qt.AlignRight)

        host_info = subprocess.Popen(u'hostname',
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        host_info, err = host_info.communicate()
        host_info = host_info.split('\n')
        host_info = host_info[0]

        ip_addr_info = socket.gethostbyname(socket.getfqdn())

        mac_addr_info = subprocess.Popen(u'getmac',
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        mac_addr_info, err = mac_addr_info.communicate()
        mac_addr_info = mac_addr_info.splitlines()
        mac_addr_info = mac_addr_info[3]
        mac_addr_info = mac_addr_info[0:17]

        board_info = subprocess.Popen(u'wmic baseboard get manufacturer, product /format:list',
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        board_info, err = board_info.communicate()
        board_info = board_info.split('\n')
        for line in board_info:
            if line.startswith('Manufacturer'):
                m_line = line
                m_line = m_line.strip()
                m_line = line.split('=')
                m_line = '제조사 = ' + m_line[1]
            if line.startswith('Product'):
                p_line = line
                p_line = p_line.strip()
                p_line = line.split('=')
                p_line = '제품명 = ' + p_line[1]

        cpu_info = subprocess.Popen(u'wmic cpu get Name',
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cpu_info, err = cpu_info.communicate()
        cpu_info = cpu_info.split('\n')
        cpu_info = cpu_info[1]

        gpu_info = subprocess.Popen(u'wmic PATH Win32_VideoController get name',
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        gpu_info, err = gpu_info.communicate()
        gpu_info = gpu_info.split('\n')
        gpu_info = gpu_info[2]

        nic_info = subprocess.Popen(u'wmic nic get name',
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        nic_info, err = nic_info.communicate()
        nic_info = nic_info.split('\n')
        nic_info = nic_info[2]

        disk_info = subprocess.Popen(u'wmic diskdrive get model, size /format:list',
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        disk_info, err = disk_info.communicate()
        disk_info = disk_info.split('\n')

        memory_info = subprocess.Popen(u'wmic memorychip get manufacturer, speed, capacity /format:list ',
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        memory_info, err = memory_info.communicate()
        memory_info = memory_info.split('\n')

        self.status_layout.addRow(u'사용자 :', QLabel(u'{}'.format(host_info)))
        self.status_layout.addRow(u'아이피 주소 :', QLabel(u'{}'.format(ip_addr_info)))
        self.status_layout.addRow(u'물리 주소 :', QLabel(u'{}'.format(mac_addr_info)))
        self.status_layout.addRow(u'메인보드 :', QLabel(u'{} \n{}'.format(m_line, p_line)))
        self.status_layout.addRow(u'프로세스 :', QLabel(u'{}'.format(cpu_info)))
        self.status_layout.addRow(u'그래픽카드 :', QLabel(u'{}'.format(gpu_info)))
        self.status_layout.addRow(u'네트워크카드 :', QLabel(u'{}'.format(nic_info)))

        i = 0
        for line in disk_info:
            if line.startswith('Model'):
                m_line = line
                m_line = m_line.strip()
                m_line = m_line.split('=')
                m_line = '  제품명   = ' + m_line[1]
            if line.startswith('Size'):
                s_line = line
                s_line = s_line.strip()
                s_line = s_line.split('=')
                s_line = float(s_line[1])
                s_line = self.convert_size(s_line)
                s_line = '전체 용량 = ' + s_line
                i = i + 1
                self.status_layout.addRow(QLabel(u'하드디스크_{} :'.format(i)), QLabel(u'{}   \n{}'.format(s_line, m_line)))
        i = 0
        for line in memory_info:
            if line.startswith('Manufacturer'):
                m_line = line
                m_line = m_line.strip()
                m_line = m_line.split('=')
                m_line = '제조사 = ' + m_line[1]
            if line.startswith('Capacity'):
                c_line = line
                c_line = c_line.strip()
                c_line = c_line.split('=')
                c_line = float(c_line[1])
                c_line = self.convert_size(c_line)
                c_line = '용량 = ' + c_line
            if line.startswith('Speed'):
                s_line = line
                s_line = s_line.strip()
                s_line = s_line.split('=')
                s_line = '속도 = ' + s_line[1]
                i = i + 1
                self.status_layout.addRow(QLabel(u'메모리_{} :'.format(i)),
                                          QLabel(u'{}   {}   {}Mhz'.format(m_line, c_line, s_line)))

        self.right_layout.addWidget(self.status_gb)

    # 바이트 변환 함수
    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def init_alives(self):
        for i in range(self.right_layout.count()):
            item = self.right_layout.itemAt(i)
            widget = item.widget()
            widget.setParent(None)

    def select_tree_items(self):
        if self.item_netdrive.isSelected():
            self.init_alives()
            self.right_layout.addWidget(self.right_spliiter)
        if self.item_system.isSelected():
            self.init_alives()
            self.system_inform_ui()

    def show_selecteditems(self):
        """ 사용자 테이블 위젯에서 사용자를 클릭할 경우 사용중인 네트워크 드라이브 리스트를 보여준다. """
        for item in self.user_table.selectedItems():
            # row 함수로 선택된 아이템의 행 번호를 가져옴
            row = item.row()

            # 테이블위젯의 선택된 row에 colum 1번(아이디가 있는) item을 가져온다.
            item = self.user_table.item(row, 0)

            self.user = item.u

            # 테이블 위젯의 선택된 row에 cloum 3번 (닉네임이 있는) item을 가져온다.
            if self.user_table.item(row, 3) is not None:
                self.name = self.user_table.item(row, 3).text()
                user_title = self.name + u" - 사용중인 네트워크 드라이브"
                self.drive_refresh_layout(user_title)
            self.init_netdrive_list()

            break

    def append_to_usertable(self, result):
        """
        DB에서 가져온 사용자 정보(result)를 테이블 위젯에 보여준다.
        """
        self.user_table.setRowCount(0)
        self.user_table.setSortingEnabled(False)

        users = []

        for user_id, team, nickname, name, login_id, email_address, ip in result:
            u = User(user_id, team, nickname, name, login_id, email_address, ip)
            users.append(u)
        self.user_table.setRowCount(len(users))

        self.user_table.blockSignals(True)
        for row, u in enumerate(users):
            item1 = QTableWidgetItem(str(u.user_id))
            item1.u = u

            item2 = QTableWidgetItem(u.team)
            item3 = QTableWidgetItem(u.nickname)
            item4 = QTableWidgetItem(u.name)
            item5 = QTableWidgetItem(u.login_id)
            item6 = QTableWidgetItem(u.email_addres)
            item7 = QTableWidgetItem(u.ip)

            self.user_table.setItem(row, 0, item1)
            self.user_table.setItem(row, 1, item2)
            self.user_table.setItem(row, 2, item3)
            self.user_table.setItem(row, 3, item4)
            self.user_table.setItem(row, 4, item5)
            self.user_table.setItem(row, 5, item6)
            self.user_table.setItem(row, 6, item7)

        self.user_table.sortByColumn(1, Qt.AscendingOrder)
        self.user_table.blockSignals(False)

        text_lable = '{}명의 사용자가 검색 되었습니다.'.format(len(users))
        self.show_search_result(text_label=text_lable)

    def show_user_info(self):
        """
        검색 버튼 클릭시 사용자 정보를 보여준다.
        팀명, 닉네임, 이름
        """
        result = get_user_info(input_search=self.input_search.text())

        self.append_to_usertable(result)

        if not result:
            text_table = '존재 하지 않는 사용자입니다.'
            self.show_search_result(text_label=text_table)

    def show_all_user_info(self):
        """
        모든 사용자 보기 버튼 클릭시 사용자 정보를 보여준다.
        """
        result = get_all_user_info()
        if not result:
            self.search_layout.addWidget(self.search_button)

        self.append_to_usertable(result)

    def modified_items(self):
        """
        유저 테이블 위젯에서 유저 정보를 변경(수정)할 경우
        변경한 데이터, 변경한 데이터의 컬럼, 변경한 데이터의 데이터베이스 테이블 ID값을 알아내
        self.update_user_information 모듈을 통해 변경한 데이터를 데이터베이스에 업데이트 한다.
        """
        dbtable_column = {
                           1: 'team',
                           2: 'nickname',
                           3: 'name',
                           4: 'login_id',
                           5: 'email_address',
                           6: 'ip',
                         }

        for item in self.user_table.selectedItems():
            # 변경한 데이터
            modified_data = item.text()

            # 변경한 데이터의 컬럼값을 가져옴
            col = item.column()
            modified_feild = dbtable_column.get(col)

            # 변경한 데이터의 행을 가져와 그 행의 0번 컬럼에 있는 DB의 ID값을 가져온다.
            row = item.row()
            user_id = self.user_table.item(row, 0).text()

            update_user_information(modified_feild, modified_data, user_id)

    def init_user_list(self):
        """
        사용자 리스트 정보를 새로 받아온다.
        (삭제 되었을 경우)
        """
        self.show_user_info()

    def add_user(self):
        """사용자를 추가한다."""
        win = UserAddWindow(parent=self)
        result = win.exec_()
        if not result:
            return

    def unselected_user_mbox(self):
        title = '사용자'
        text = '선택된 사용자가 없습니다.'
        QMessageBox.information(self, title, text)

    def del_complete_mbox(self):
        """ 사용자가 삭제되면 메세지 박스를 띄워준다. """
        title = '삭제'
        text = '{} - 삭제 되었습니다.'.format(self.user.nickname)
        QMessageBox.information(self, title, text)

    def del_user(self):
        """ 사용자를 삭제한다. """
        user_id = self.user.user_id
        delete_user(users_id=user_id)
        self.init_user_list()
        self.init_netdrive_list()
        self.del_complete_mbox()

    def del_user_mbox(self):
        """ 사용자를 삭제하기 전 메세지 박스를 띄워 정말로 삭제할 것인지 물어본다. """
        self.setStyleSheet('Background-color: rgb(62, 62, 77);')
        if self.nickname is not None:
            title = '사용자 삭제'
            text = '사용자 {}를 정말로 삭제 하시겠습니까?'.format(self.user.nickname)
            r = QMessageBox.question(self, title, text)
            if r == QMessageBox.Yes:
                return self.del_user()
            elif r == QMessageBox.No:
                return False
        else:
            self.unselected_user_mbox()

    def init_netdrive_list(self):
        """
        설정에서 네트워크 드라이브 연결 버튼을 클릭 시
        사용자가 사용중인 네트워크 드라이브의 전체 정보를 불러온다.
        """
        self.using_netdrive_table.setRowCount(0)
        self.using_netdrive_table.setSortingEnabled(False)

        results = get_drive_list(user_id=self.user.user_id)

        self.using_netdrive_table.setRowCount(len(results))

        for row, (name, host, ip, desc, nid) in enumerate(results):
            item1 = QTableWidgetItem(name)
            item1.nid = nid
            self.using_netdrive_table.setItem(row, 0, item1)

            item2 = QTableWidgetItem(host)
            self.using_netdrive_table.setItem(row, 1, item2)

            item3 = QTableWidgetItem(ip)
            self.using_netdrive_table.setItem(row, 2, item3)

            item4 = QTableWidgetItem(desc)
            self.using_netdrive_table.setItem(row, 3, item4)

        self.using_netdrive_table.setSortingEnabled(True)
        self.using_netdrive_table.sortByColumn(0, Qt.AscendingOrder)

    def update_netdrive(self, selected_ids):
        """사용자의 네트워크 드라이브 리스트에 대한 정보를 업데이트 한다."""
        save_selected_netdrive(selected_ids=selected_ids, user_id=self.user.user_id)

        self.init_netdrive_list()

    def add_network_drive(self):
        """ 선택된 사용자에게 새로운 네트워크 드라이브를 추가해준다. """
        if self.user is None:
            return
        netdrives = []
        for row in range(self.using_netdrive_table.rowCount()):
            item = self.using_netdrive_table.item(row, 0)
            netdrives.append(item.nid)

        win = NetdriveListWindow(user=self.user, netdrives=netdrives, parent=self)
        result = win.exec_()
        if not result:
            return
        self.update_netdrive(win.selected_ids)


class UserAddWindow(QDialog):
    """사용자 추가 윈도우"""
    def __init__(self, *args, **kwargs):
        super(UserAddWindow, self).__init__(*args, **kwargs)
        self.setStyleSheet('Background-color: rgb(62, 62, 77);')

        self.ui()
        self.init()

    _TEAM_LIST = ['--team--', '기획팀', '미술팀', '영업팀', '개발팀', '디자인팀',
                  '경영지원팀', '사업팀']

    _AUTH_LIST = ['--auth id--', '1', '2']

    _MILLIONVOLT = '@gmail.com'

    _IP = '192.168.1.'

    def init(self):
        self.team_combobox.addItems(self._TEAM_LIST)
        self.auth_combobox.addItems(self._AUTH_LIST)
        self.auth_combobox.setCurrentIndex(1)
        self.assign_button.clicked.connect(self.assign)

    @property
    def team(self):
        return self.team_combobox.currentText()

    @property
    def nickname(self):
        return self.nickname_lineedit.text()

    @property
    def name(self):
        return self.name_lineedit.text()

    @property
    def id(self):
        return self.id_lineedit.text()

    @property
    def email(self):
        return self.email_lineedit.text() + self._MILLIONVOLT

    @property
    def ip(self):
        return self._IP + self.ip_lineedit.text()

    @property
    def auth_id(self):
        return self.auth_combobox.currentText()

    def assign(self):
        try:
            add_new_user(self.team, self.nickname, self.name, self.id, self.email, self.ip, self.auth_id)
            if self.question_message() is True:
                self.reset()
            else:
                self.close()
        except IntegrityError:
            return self.dup_email_error_mbox()
        except:
            self.error_mbox()

    def reset(self):
        self.nickname_lineedit.setText('')
        self.name_lineedit.setText('')
        self.id_lineedit.setText('')
        self.ip_lineedit.setText('')
        self.email_lineedit.setText('')
        self.auth_combobox.setCurrentIndex(1)
        self.team_combobox.setCurrentIndex(0)

    def ui(self):
        self.setWindowTitle('assign member')
        main_layout = QVBoxLayout()

        # team
        team_layout = QHBoxLayout()
        main_layout.addLayout(team_layout)
        team_label = QLabel('team : ')
        team_label.setFixedSize(80, 30)
        team_layout.addWidget(team_label)
        self.team_combobox = QComboBox()
        self.team_combobox.setMaxVisibleItems(30)
        team_layout.addWidget(self.team_combobox)

        # nickname
        nickname_layout = QHBoxLayout()
        main_layout.addLayout(nickname_layout)
        nickname_label = QLabel('nickname : ')
        nickname_label.setFixedSize(80, 30)
        nickname_layout.addWidget(nickname_label)
        self.nickname_lineedit = QLineEdit()
        nickname_layout.addWidget(self.nickname_lineedit)

        # name
        name_layout = QHBoxLayout()
        main_layout.addLayout(name_layout)
        name_label = QLabel('name : ')
        name_label.setFixedSize(80, 30)
        name_layout.addWidget(name_label)
        self.name_lineedit = QLineEdit()
        name_layout.addWidget(self.name_lineedit)

        # id
        id_layout = QHBoxLayout()
        main_layout.addLayout(id_layout)
        id_label = QLabel('id : ')
        id_label.setFixedSize(80, 30)
        id_layout.addWidget(id_label)
        self.id_lineedit = QLineEdit()
        id_layout.addWidget(self.id_lineedit)

        # email
        email_layout = QHBoxLayout()
        main_layout.addLayout(email_layout)
        email_label = QLabel('email : ')
        email_label.setFixedSize(80, 30)
        email_layout.addWidget(email_label)
        self.email_lineedit = QLineEdit()
        email_layout.addWidget(self.email_lineedit)
        email_label2 = QLabel(self._MILLIONVOLT)
        email_label2.setFixedSize(100, 30)
        email_layout.addWidget(email_label2)

        # ip
        ip_layout = QHBoxLayout()
        main_layout.addLayout(ip_layout)
        ip_label = QLabel('ip : ')
        ip_label.setFixedSize(80, 30)
        ip_layout.addWidget(ip_label)
        ip_label2 = QLabel(self._IP)
        ip_label2.setFixedSize(55, 30)
        ip_layout.addWidget(ip_label2)
        self.ip_lineedit = QLineEdit()
        ip_layout.addWidget(self.ip_lineedit)

        # auth
        auth_layout = QHBoxLayout()
        main_layout.addLayout(auth_layout)
        auth_label = QLabel('auth : ')
        auth_label.setFixedSize(80, 30)
        auth_layout.addWidget(auth_label)
        self.auth_combobox = QComboBox()
        auth_layout.addWidget(self.auth_combobox)

        # set button
        self.assign_button = QPushButton('DB 등록')
        main_layout.addWidget(self.assign_button)

        self.setLayout(main_layout)
        self.adjustSize()

    def complete_message(self, title='complete', text='사용자 등록이 완료 되었습니다.'):
        QMessageBox.information(self, title, text)

    def question_message(self, title='사용자 등록', text='사용자 {} 등록이 완료 되었습니다.\n계속 추가할까요?'):
        r = QMessageBox.question(self, title, text.format(self.nickname))
        if r == QMessageBox.Yes:
            return True
        elif r == QMessageBox.No:
            return False

    def dup_email_error_mbox(self, title='이메일 주소 중복', text='이메일 주소 {}가 데이터베이스에 존재하므로\n다른 이메일 주소를 사용하셔야됩니다.'):
        QMessageBox.information(self, title, text.format(self.email))

    def error_mbox(self, title='사용자 등록 실패', text='사용자 등록에 필요한 정보들을\n다시 한번 확인 해주세요'):
        QMessageBox.information(self, title, text)


class NetdriveListWindow(QDialog):
    """네트워크 드라이브 리스트를 보는 윈도우"""
    def __init__(self, user, netdrives, *args, **kwargs):
        super(NetdriveListWindow, self).__init__(*args, **kwargs)
        self.setStyleSheet('Background-color: White smoke;')

        self.user = user
        self.netdrives = netdrives
        self.setup_ui()

    def setup_ui(self):
        WINDOW_TITLE = 'Drive Manager'
        self.main_layout = QVBoxLayout(self)
        self.setWindowTitle(WINDOW_TITLE)

        self.font = QFont()
        self.font.setFamily("Malgun Gothic")
        self.font.setStyleStrategy(QFont.PreferQuality)
        #self.font.setPointSize(13)

        self.main_text = QLabel('사용할 네트워크 드라이브를 체크해주세요')
        self.main_text.setFont(self.font)
        self.main_text.setStyleSheet("font: 14pt;\n"
                                     "color: #696969;")
        self.main_text.setFixedSize(550, 30)
        self.main_text.setAlignment(Qt.AlignCenter)

        self.complete_button = QPushButton('완료')
        self.complete_button.setFont(self.font)
        self.complete_button.setStyleSheet('font: 14pt; \n'
                                           'color: #4169E1; \n'
                                           'background-color: WhiteSmoke;')

        self.complete_button.clicked.connect(self.on_complete_button_clicked)

        self.drive_list_gb = QGroupBox()
        self.drive_list_gb.setStyleSheet("Background-color: White; \n"
                                         'font: 11pt;')
        self.drive_list_gb_layout = QGridLayout(self.drive_list_gb)

        self.main_layout.addWidget(self.main_text)
        self.main_layout.addWidget(self.drive_list_gb)
        self.main_layout.addWidget(self.complete_button)

        self.setFixedSize(575, 350)

        self.init_netdrive_list()

    def check_changed_cb(self, cb):
        """체크박스 체크 여부에 따라 구분한다."""
        if cb.checkState():
            cb.setFont(self.font)
            cb.setStyleSheet('font-weight:bold;\n'
                             'color:DodgerBlue;\n'
                             'font: 11pt;')
        else:
            cb.setStyleSheet('font-weight:;')

    def init_netdrive_list(self):
        """전체 드라이브 리스트를 불러와서 드라이브 사용여부를 폰트로 구분한다."""
        conn = get_con_smart_maker()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, drive, description FROM netdrive '
            'ORDER BY drive, description',
        )
        results = cursor.fetchall()
        conn.close()
        total = len(results)
        result_count = 0
        column_count = 3
        row_count = int(math.ceil(total / float(column_count)))
        for column in range(column_count):
            for row in range(row_count):
                if result_count == total:
                    break
                nid, drive, desc = results[result_count]
                cb = QCheckBox('{}:  {}'.format(drive, desc))
                cb.setFont(self.font)
                cb.setStyleSheet('font: 11pt;')
                cb.nid = nid

                if nid in self.netdrives:
                    cb.setChecked(True)
                    self.check_changed_cb(cb)
                cb.clicked.connect(partial(self.check_changed_cb, cb))

                self.drive_list_gb_layout.addWidget(cb, row, column)

                result_count += 1

    def on_complete_button_clicked(self):
        self.selected_ids = []
        for column in range(self.drive_list_gb_layout.columnCount()):
            for row in range(self.drive_list_gb_layout.rowCount()):
                item = self.drive_list_gb_layout.itemAtPosition(row, column)
                if item:
                    cb = item.widget()
                    if cb.isChecked():
                        self.selected_ids.append(cb.nid)
        self.accept()