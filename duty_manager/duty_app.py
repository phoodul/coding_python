<<<<<<< HEAD
import sys
import pandas as pd
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# 직원 초기 데이터
STAFF_LIST = [
    (31, "최민애", "3W", "간호"), (32, "김유하", "3W", "간호"), (33, "김민경", "3W", "간호"),
    (34, "김다인", "3W", "간호"), (35, "김다솜", "3W", "간호"), (36, "전치구", "3W", "보호"),
    (37, "김재호", "3W", "보호"), (38, "송재웅", "3W", "보호"), (39, "지정우", "3W", "보호"),
    (41, "이미경", "4W", "간호"), (42, "권수진", "4W", "간호"), (43, "정지우", "4W", "간호"),
    (44, "송선아", "4W", "간호"), (46, "송현찬", "4W", "보호"), (47, "김두현", "4W", "보호"),
    (48, "하영기", "4W", "보호"), (51, "김도연", "5W", "간호"), (52, "김나은", "5W", "간호"),
    (53, "허예리", "5W", "간호"), (54, "박수진", "5W", "간호"), (55, "김민영", "5W", "간호"),
    (56, "서현도", "5W", "보호"), (57, "김두현(주)", "5W", "보호"), (58, "제상수", "5W", "보호")
]

class DutyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나눔과행복병원 근무표 생성기 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 상단 제어부
        self.header_layout = QHBoxLayout()
        self.btn_run = QPushButton("🚀 RUN (근무표 자동 완성)")
        self.btn_run.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 40px;")
        self.btn_run.clicked.connect(self.run_automation)
        
        self.btn_print = QPushButton("🖨️ A4 가로 출력 (Excel)")
        self.btn_print.clicked.connect(self.export_to_excel)
        
        self.header_layout.addWidget(QLabel("2026년 1월 근무표 생성기"))
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.btn_run)
        self.header_layout.addWidget(self.btn_print)
        self.layout.addLayout(self.header_layout)

        # 테이블 1, 2, 3 생성 및 배치
        self.tabs = QTabWidget()
        self.init_table1() # 직원 설정
        self.init_table2() # 개인별 Duty
        self.init_table3() # 병동별 배치표
        
        self.layout.addWidget(self.tabs)
        
        # 데이터 연동을 위한 시그널 연결
        self.table2.itemChanged.connect(self.sync_table2_to_others)
        self.table3.itemChanged.connect(self.sync_table3_to_others)

    def init_table1(self):
        self.table1 = QTableWidget(len(STAFF_LIST), 9)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "직종", "12/31 Duty", "연속일수", "D", "E", "N", "O"])
        for i, (num, name, ward, role) in enumerate(STAFF_LIST):
            self.table1.setItem(i, 0, QTableWidgetItem(str(num)))
            self.table1.setItem(i, 1, QTableWidgetItem(name))
            self.table1.setItem(i, 2, QTableWidgetItem(f"{ward} {role}"))
        self.tabs.addTab(self.table1, "테이블 1 (직원 설정)")

    def init_table2(self):
        self.table2 = QTableWidget(len(STAFF_LIST), 33) # 번호, 이름 + 31일
        headers = ["번호", "성함"] + [f"{i}\n{self.get_weekday(i)}" for i in range(1, 32)]
        self.table2.setHorizontalHeaderLabels(headers)
        
        for i, (num, name, ward, role) in enumerate(STAFF_LIST):
            self.table2.setItem(i, 0, QTableWidgetItem(str(num)))
            self.table2.setItem(i, 1, QTableWidgetItem(name))
            
        self.tabs.addTab(self.table2, "테이블 2 (개인별 Duty)")

    def init_table3(self):
        rows = ["3W 간호", "3W 보호", "4W 간호", "4W 보호", "5W 간호", "5W 보호"]
        self.table3 = QTableWidget(len(rows), 32) # 구분 + 31일
        self.table3.setHorizontalHeaderLabels(["구분"] + [f"{i}" for i in range(1, 32)])
        for i, row_name in enumerate(rows):
            self.table3.setItem(i, 0, QTableWidgetItem(row_name))
        self.tabs.addTab(self.table3, "테이블 3 (병동별 배치표)")

    def get_weekday(self, day):
        # 2026년 1월 1일은 목요일
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        idx = (day + 2) % 7 # 1월 1일 목요일 기준 보정
        return weekdays[idx]

    def sync_table2_to_others(self, item):
        # 입력 오류 검증 (간호사/보호사 코드 제한)
        row, col = item.row(), item.column()
        if col < 2: return # 이름/번호 수정 제외
        
        val = item.text().upper()
        is_nurse = "간호" in self.table1.item(row, 2).text()
        
        allowed = ['D', 'E', 'N', 'M', 'O', 'D5', 'N5', 'D4', 'N4'] if is_nurse else ['D', 'N', 'O']
        if val and val not in allowed:
            item.setBackground(QColor("red"))
        else:
            item.setBackground(QColor("white"))
            # 여기에 테이블 1의 합계 자동 계산 로직 추가 가능

    def sync_table3_to_others(self, item):
        # 테이블 3에서 X 입력 시 테이블 2 연동 로직
        pass

    def run_automation(self):
        QMessageBox.information(self, "알림", "지정된 제약 조건(N 3회, 연속 5일 등)을 바탕으로 빈칸을 채웁니다.")
        # 여기에 실제 수간호사님이 요청하신 1~8번 규칙 알고리즘 구현

    def export_to_excel(self):
        QMessageBox.information(self, "출력", "A4 가로 사이즈 최적화 엑셀 파일을 생성합니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DutyApp()
    window.show()
=======
import sys
import pandas as pd
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# 직원 초기 데이터
STAFF_LIST = [
    (31, "최민애", "3W", "간호"), (32, "김유하", "3W", "간호"), (33, "김민경", "3W", "간호"),
    (34, "김다인", "3W", "간호"), (35, "김다솜", "3W", "간호"), (36, "전치구", "3W", "보호"),
    (37, "김재호", "3W", "보호"), (38, "송재웅", "3W", "보호"), (39, "지정우", "3W", "보호"),
    (41, "이미경", "4W", "간호"), (42, "권수진", "4W", "간호"), (43, "정지우", "4W", "간호"),
    (44, "송선아", "4W", "간호"), (46, "송현찬", "4W", "보호"), (47, "김두현", "4W", "보호"),
    (48, "하영기", "4W", "보호"), (51, "김도연", "5W", "간호"), (52, "김나은", "5W", "간호"),
    (53, "허예리", "5W", "간호"), (54, "박수진", "5W", "간호"), (55, "김민영", "5W", "간호"),
    (56, "서현도", "5W", "보호"), (57, "김두현(주)", "5W", "보호"), (58, "제상수", "5W", "보호")
]

class DutyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나눔과행복병원 근무표 생성기 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 상단 제어부
        self.header_layout = QHBoxLayout()
        self.btn_run = QPushButton("🚀 RUN (근무표 자동 완성)")
        self.btn_run.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 40px;")
        self.btn_run.clicked.connect(self.run_automation)
        
        self.btn_print = QPushButton("🖨️ A4 가로 출력 (Excel)")
        self.btn_print.clicked.connect(self.export_to_excel)
        
        self.header_layout.addWidget(QLabel("2026년 1월 근무표 생성기"))
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.btn_run)
        self.header_layout.addWidget(self.btn_print)
        self.layout.addLayout(self.header_layout)

        # 테이블 1, 2, 3 생성 및 배치
        self.tabs = QTabWidget()
        self.init_table1() # 직원 설정
        self.init_table2() # 개인별 Duty
        self.init_table3() # 병동별 배치표
        
        self.layout.addWidget(self.tabs)
        
        # 데이터 연동을 위한 시그널 연결
        self.table2.itemChanged.connect(self.sync_table2_to_others)
        self.table3.itemChanged.connect(self.sync_table3_to_others)

    def init_table1(self):
        self.table1 = QTableWidget(len(STAFF_LIST), 9)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "직종", "12/31 Duty", "연속일수", "D", "E", "N", "O"])
        for i, (num, name, ward, role) in enumerate(STAFF_LIST):
            self.table1.setItem(i, 0, QTableWidgetItem(str(num)))
            self.table1.setItem(i, 1, QTableWidgetItem(name))
            self.table1.setItem(i, 2, QTableWidgetItem(f"{ward} {role}"))
        self.tabs.addTab(self.table1, "테이블 1 (직원 설정)")

    def init_table2(self):
        self.table2 = QTableWidget(len(STAFF_LIST), 33) # 번호, 이름 + 31일
        headers = ["번호", "성함"] + [f"{i}\n{self.get_weekday(i)}" for i in range(1, 32)]
        self.table2.setHorizontalHeaderLabels(headers)
        
        for i, (num, name, ward, role) in enumerate(STAFF_LIST):
            self.table2.setItem(i, 0, QTableWidgetItem(str(num)))
            self.table2.setItem(i, 1, QTableWidgetItem(name))
            
        self.tabs.addTab(self.table2, "테이블 2 (개인별 Duty)")

    def init_table3(self):
        rows = ["3W 간호", "3W 보호", "4W 간호", "4W 보호", "5W 간호", "5W 보호"]
        self.table3 = QTableWidget(len(rows), 32) # 구분 + 31일
        self.table3.setHorizontalHeaderLabels(["구분"] + [f"{i}" for i in range(1, 32)])
        for i, row_name in enumerate(rows):
            self.table3.setItem(i, 0, QTableWidgetItem(row_name))
        self.tabs.addTab(self.table3, "테이블 3 (병동별 배치표)")

    def get_weekday(self, day):
        # 2026년 1월 1일은 목요일
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        idx = (day + 2) % 7 # 1월 1일 목요일 기준 보정
        return weekdays[idx]

    def sync_table2_to_others(self, item):
        # 입력 오류 검증 (간호사/보호사 코드 제한)
        row, col = item.row(), item.column()
        if col < 2: return # 이름/번호 수정 제외
        
        val = item.text().upper()
        is_nurse = "간호" in self.table1.item(row, 2).text()
        
        allowed = ['D', 'E', 'N', 'M', 'O', 'D5', 'N5', 'D4', 'N4'] if is_nurse else ['D', 'N', 'O']
        if val and val not in allowed:
            item.setBackground(QColor("red"))
        else:
            item.setBackground(QColor("white"))
            # 여기에 테이블 1의 합계 자동 계산 로직 추가 가능

    def sync_table3_to_others(self, item):
        # 테이블 3에서 X 입력 시 테이블 2 연동 로직
        pass

    def run_automation(self):
        QMessageBox.information(self, "알림", "지정된 제약 조건(N 3회, 연속 5일 등)을 바탕으로 빈칸을 채웁니다.")
        # 여기에 실제 수간호사님이 요청하신 1~8번 규칙 알고리즘 구현

    def export_to_excel(self):
        QMessageBox.information(self, "출력", "A4 가로 사이즈 최적화 엑셀 파일을 생성합니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DutyApp()
    window.show()
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    sys.exit(app.exec())