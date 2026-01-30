<<<<<<< HEAD
import sys
import calendar
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# 12월 실제 데이터 샘플 (일부 추출)
DUTY_2025_12 = {
    "31": ["D", "O", "D", "D", "D", "O", "O", "D", "D", "N", "N", "N", "O", "O", "D", "D", "N", "N", "N", "O", "O", "D", "D", "D", "O", "N", "N", "O", "O", "D", "D"],
    "32": ["E", "O", "O", "E", "E", "O", "N", "N", "N", "O", "O", "E", "O", "O", "E", "E", "E", "E", "E", "O", "O", "E", "N", "N", "O", "E", "E", "N", "N", "O", "O"],
    "33": ["O", "E", "E", "O", "O", "D", "D", "N4", "N4", "N4", "O", "O", "D", "D", "O", "E", "N4", "N4", "O", "O", "D", "E", "O", "O", "D", "D", "D", "O", "O", "N4", "N4"]
    # ... 나머지 인원 데이터 포함
}

class VerticalTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        text = index.data()
        if text:
            painter.save()
            # Request 데이터(빨간색) 처리
            if "[R]" in text:
                painter.setPen(QColor("red"))
                text = text.replace("[R]", "")
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            # 세로 쓰기: 한 글자씩 줄바꿈
            v_text = "\n".join(list(text))
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, v_text)
            painter.restore()
        else:
            super().paint(painter, option, index)

class DutyAppV3(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 v3.0")
        self.setGeometry(30, 30, 1650, 980)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 상단 컨트롤바
        top_bar = QHBoxLayout()
        self.cb_request = QCheckBox("🔴 Request 입력 모드 (체크 시 빨간색 입력)")
        self.cb_request.toggled.connect(self.set_request_mode)
        
        self.year_month = QLabel("📅 2025년 12월 근무표 (분석 데이터 반영 완료)")
        top_bar.addWidget(self.year_month)
        top_bar.addStretch()
        top_bar.addWidget(self.cb_request)
        layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        self.setup_table1() # 설정 (D, E, N, O, M 순서)
        self.setup_table2() # 개인별 (색상 구분)
        self.setup_table3() # 병동별 (엑셀 레이아웃)
        
        layout.addWidget(self.tabs)

        # 하단 직원 명부
        footer = QLabel("<b>[간호사]</b> 31 최민애 | 32 김유하 | 33 김민경 | 34 김다인 | 35 김다솜 | 41 이미경 | 42 권수진 | 43 정지우 | 44 송선아 | 51 김도연 | 52 김나은 | 53 허예리 | 54 박수진 | 55 김민영<br>"
                        "<b>[보호사]</b> 36 전치구 | 37 김재호 | 38 송재웅 | 39 지정우 | 46 송현찬 | 47 김두현 | 48 하영기 | 56 서현도 | 57 김두현(주) | 58 제상수")
        footer.setStyleSheet("background: #f8f9fa; padding: 10px; border: 1px solid #ddd;")
        layout.addWidget(footer)

    def setup_table1(self):
        self.table1 = QTableWidget(24, 8)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "D", "E", "N", "O", "M", "비고"])
        # 순서 변경: D -> E -> N -> O -> M
        self.tabs.addTab(self.table1, "테이블 1 (근무 개수)")

    def setup_table2(self):
        self.table2 = QTableWidget(24, 33)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(i) for i in range(1, 32)])
        
        for r in range(24):
            # 간호사(0~13행) 옅은 노랑, 보호사(14~23행) 연한 하늘색
            color = QColor("#FFFFE0") if r < 14 else QColor("#E0FFFF")
            for c in range(33):
                item = QTableWidgetItem()
                item.setBackground(color)
                self.table2.setItem(r, c, item)
        
        self.tabs.addTab(self.table2, "테이블 2 (개인별 Duty)")

    def setup_table3(self, days=31):
        # 엑셀 화면 레이아웃 반영
        self.table3 = QTableWidget(12, days * 3 + 1)
        self.table3.setItemDelegate(VerticalTextDelegate())
        
        # 헤더 그리기 (날짜, 요일, D/E/N)
        for d in range(1, days + 1):
            col = (d - 1) * 3 + 1
            self.table3.setSpan(0, col, 1, 3) # 날짜 병합
            self.table3.setItem(0, col, QTableWidgetItem(str(d)))
            self.table3.setSpan(1, col, 1, 3) # 요일 병합
            
        self.table3.setItem(3, 0, QTableWidgetItem("3W 간호"))
        self.table3.setItem(4, 0, QTableWidgetItem("4W 간호"))
        self.table3.setItem(5, 0, QTableWidgetItem("5W 간호"))
        
        self.table3.setItem(8, 0, QTableWidgetItem("3W 보호"))
        self.table3.setItem(9, 0, QTableWidgetItem("4W 보호"))
        self.table3.setItem(10, 0, QTableWidgetItem("5W 보호"))

        self.tabs.addTab(self.table3, "테이블 3 (병동별 배치)")

    def set_request_mode(self, checked):
        self.request_mode = checked

    def handle_input(self, row, col, text):
        # Request 모드일 때 텍스트 앞에 [R] 태그를 붙여 빨간색 출력 유도
        if self.request_mode:
            text = f"[R]{text}"
=======
import sys
import calendar
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# 12월 실제 데이터 샘플 (일부 추출)
DUTY_2025_12 = {
    "31": ["D", "O", "D", "D", "D", "O", "O", "D", "D", "N", "N", "N", "O", "O", "D", "D", "N", "N", "N", "O", "O", "D", "D", "D", "O", "N", "N", "O", "O", "D", "D"],
    "32": ["E", "O", "O", "E", "E", "O", "N", "N", "N", "O", "O", "E", "O", "O", "E", "E", "E", "E", "E", "O", "O", "E", "N", "N", "O", "E", "E", "N", "N", "O", "O"],
    "33": ["O", "E", "E", "O", "O", "D", "D", "N4", "N4", "N4", "O", "O", "D", "D", "O", "E", "N4", "N4", "O", "O", "D", "E", "O", "O", "D", "D", "D", "O", "O", "N4", "N4"]
    # ... 나머지 인원 데이터 포함
}

class VerticalTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        text = index.data()
        if text:
            painter.save()
            # Request 데이터(빨간색) 처리
            if "[R]" in text:
                painter.setPen(QColor("red"))
                text = text.replace("[R]", "")
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            # 세로 쓰기: 한 글자씩 줄바꿈
            v_text = "\n".join(list(text))
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, v_text)
            painter.restore()
        else:
            super().paint(painter, option, index)

class DutyAppV3(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 v3.0")
        self.setGeometry(30, 30, 1650, 980)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 상단 컨트롤바
        top_bar = QHBoxLayout()
        self.cb_request = QCheckBox("🔴 Request 입력 모드 (체크 시 빨간색 입력)")
        self.cb_request.toggled.connect(self.set_request_mode)
        
        self.year_month = QLabel("📅 2025년 12월 근무표 (분석 데이터 반영 완료)")
        top_bar.addWidget(self.year_month)
        top_bar.addStretch()
        top_bar.addWidget(self.cb_request)
        layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        self.setup_table1() # 설정 (D, E, N, O, M 순서)
        self.setup_table2() # 개인별 (색상 구분)
        self.setup_table3() # 병동별 (엑셀 레이아웃)
        
        layout.addWidget(self.tabs)

        # 하단 직원 명부
        footer = QLabel("<b>[간호사]</b> 31 최민애 | 32 김유하 | 33 김민경 | 34 김다인 | 35 김다솜 | 41 이미경 | 42 권수진 | 43 정지우 | 44 송선아 | 51 김도연 | 52 김나은 | 53 허예리 | 54 박수진 | 55 김민영<br>"
                        "<b>[보호사]</b> 36 전치구 | 37 김재호 | 38 송재웅 | 39 지정우 | 46 송현찬 | 47 김두현 | 48 하영기 | 56 서현도 | 57 김두현(주) | 58 제상수")
        footer.setStyleSheet("background: #f8f9fa; padding: 10px; border: 1px solid #ddd;")
        layout.addWidget(footer)

    def setup_table1(self):
        self.table1 = QTableWidget(24, 8)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "D", "E", "N", "O", "M", "비고"])
        # 순서 변경: D -> E -> N -> O -> M
        self.tabs.addTab(self.table1, "테이블 1 (근무 개수)")

    def setup_table2(self):
        self.table2 = QTableWidget(24, 33)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(i) for i in range(1, 32)])
        
        for r in range(24):
            # 간호사(0~13행) 옅은 노랑, 보호사(14~23행) 연한 하늘색
            color = QColor("#FFFFE0") if r < 14 else QColor("#E0FFFF")
            for c in range(33):
                item = QTableWidgetItem()
                item.setBackground(color)
                self.table2.setItem(r, c, item)
        
        self.tabs.addTab(self.table2, "테이블 2 (개인별 Duty)")

    def setup_table3(self, days=31):
        # 엑셀 화면 레이아웃 반영
        self.table3 = QTableWidget(12, days * 3 + 1)
        self.table3.setItemDelegate(VerticalTextDelegate())
        
        # 헤더 그리기 (날짜, 요일, D/E/N)
        for d in range(1, days + 1):
            col = (d - 1) * 3 + 1
            self.table3.setSpan(0, col, 1, 3) # 날짜 병합
            self.table3.setItem(0, col, QTableWidgetItem(str(d)))
            self.table3.setSpan(1, col, 1, 3) # 요일 병합
            
        self.table3.setItem(3, 0, QTableWidgetItem("3W 간호"))
        self.table3.setItem(4, 0, QTableWidgetItem("4W 간호"))
        self.table3.setItem(5, 0, QTableWidgetItem("5W 간호"))
        
        self.table3.setItem(8, 0, QTableWidgetItem("3W 보호"))
        self.table3.setItem(9, 0, QTableWidgetItem("4W 보호"))
        self.table3.setItem(10, 0, QTableWidgetItem("5W 보호"))

        self.tabs.addTab(self.table3, "테이블 3 (병동별 배치)")

    def set_request_mode(self, checked):
        self.request_mode = checked

    def handle_input(self, row, col, text):
        # Request 모드일 때 텍스트 앞에 [R] 태그를 붙여 빨간색 출력 유도
        if self.request_mode:
            text = f"[R]{text}"
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
        # 이후 연동 로직 실행