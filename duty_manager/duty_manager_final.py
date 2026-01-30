<<<<<<< HEAD
import sys
import calendar
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# 1. 전체 직원 명단 (요청하신 번호와 이름 그대로 반영)
NURSES = [
    (31, "최민애"), (32, "김유하"), (33, "김민경"), (34, "김다인"), (35, "김다솜"),
    (41, "이미경"), (42, "권수진"), (43, "정지우"), (44, "송선아"),
    (51, "김도연"), (52, "김나은"), (53, "허예리"), (54, "박수진"), (55, "김민영")
]
AIDES = [
    (36, "전치구"), (37, "김재호"), (38, "송재웅"), (39, "지정우"),
    (46, "송현찬"), (47, "김두현"), (48, "하영기"),
    (56, "서현도"), (57, "김두현(주)"), (58, "제상수")
]

class VerticalTextDelegate(QStyledItemDelegate):
    """이름을 세로로 쓰고 빨간색 Request를 처리하는 데리게이트"""
    def paint(self, painter, option, index):
        text = str(index.data() or "")
        if text:
            painter.save()
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

class DutyAppFinal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 관리 시스템 v4.1")
        self.setGeometry(20, 20, 1700, 980)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 상단 제어바
        top_bar = QHBoxLayout()
        self.year_sel = QSpinBox()
        self.year_sel.setRange(2024, 2030)
        self.year_sel.setValue(2025)
        self.month_sel = QComboBox()
        self.month_sel.addItems([f"{i:02d}" for i in range(1, 13)])
        self.month_sel.setCurrentText("12")
        self.month_sel.currentTextChanged.connect(self.refresh_all)
        
        self.cb_request = QCheckBox("🔴 Request 입력 모드 (빨간색)")
        self.cb_request.toggled.connect(lambda checked: setattr(self, 'request_mode', checked))
        
        self.btn_run = QPushButton("🚀 RUN (자동 완성)")
        self.btn_save = QPushButton("💾 저장 및 이월")
        
        top_bar.addWidget(QLabel("📅 설정:"))
        top_bar.addWidget(self.year_sel)
        top_bar.addWidget(QLabel("년"))
        top_bar.addWidget(self.month_sel)
        top_bar.addWidget(QLabel("월"))
        top_bar.addStretch()
        top_bar.addWidget(self.cb_request)
        top_bar.addWidget(self.btn_run)
        top_bar.addWidget(self.btn_save)
        layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # 테이블 생성
        self.setup_table1()
        self.setup_table2()
        self.setup_table3()

        # --- 하단 직원 명부 푸터 (요청하신 모든 번호와 이름 표시) ---
        footer = QFrame()
        footer.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        footer_layout = QVBoxLayout(footer)
        
        nurse_names = " | ".join([f"{n[0]} {n[1]}" for n in NURSES])
        aide_names = " | ".join([f"{a[0]} {a[1]}" for a in AIDES])
        
        f_label1 = QLabel(f"<b>[간호사 명단]</b> {nurse_names}")
        f_label2 = QLabel(f"<b>[보호사 명단]</b> {aide_names}")
        footer_layout.addWidget(f_label1)
        footer_layout.addWidget(f_label2)
        layout.addWidget(footer)

    def refresh_all(self):
        self.setup_table2()
        self.setup_table3()

    def get_weekday(self, day):
        year = self.year_sel.value()
        month = int(self.month_sel.currentText())
        days = ["월", "화", "수", "목", "금", "토", "일"]
        return days[calendar.weekday(year, month, day)]

    def setup_table1(self):
        staff = NURSES + AIDES
        self.table1 = QTableWidget(len(staff), 10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "12/31 막근", "연속일", "D", "E", "N", "O", "M"])
        for i, (num, name) in enumerate(staff):
            self.table1.setItem(i, 0, QTableWidgetItem(str(num)))
            self.table1.setItem(i, 1, QTableWidgetItem(name))
            role = "간호사" if i < len(NURSES) else "보호사"
            self.table1.setItem(i, 2, QTableWidgetItem(role))
        self.tabs.addTab(self.table1, "테이블 1 (설정)")

    def setup_table2(self):
        year = self.year_sel.value()
        month = int(self.month_sel.currentText())
        days_in_month = calendar.monthrange(year, month)[1]
        staff = NURSES + AIDES
        
        self.table2 = QTableWidget(len(staff), days_in_month + 2)
        # 헤더에 날짜와 요일 병기
        headers = ["번호", "성함"]
        for d in range(1, days_in_month + 1):
            headers.append(f"{d}\n({self.get_weekday(d)})")
        self.table2.setHorizontalHeaderLabels(headers)
        
        for r in range(len(staff)):
            color = QColor("#FFFFE0") if r < len(NURSES) else QColor("#E0FFFF")
            self.table2.setItem(r, 0, QTableWidgetItem(str(staff[r][0])))
            self.table2.setItem(r, 1, QTableWidgetItem(staff[r][1]))
            for c in range(days_in_month + 2):
                if c >= 2:
                    item = QTableWidgetItem("")
                    self.table2.setItem(r, c, item)
                self.table2.item(r, c).setBackground(color)
        
        self.table2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table2.cellChanged.connect(self.handle_table2_input)
        
        if self.tabs.count() > 1: self.tabs.removeTab(1)
        self.tabs.insertTab(1, self.table2, "테이블 2 (개인별)")

    def handle_table2_input(self, r, c):
        if c < 2: return
        item = self.table2.item(r, c)
        if item and self.request_mode and "[R]" not in item.text():
            self.table2.blockSignals(True)
            item.setText(f"[R]{item.text()}")
            item.setForeground(QColor("red"))
            self.table2.blockSignals(False)

    def setup_table3(self):
        year = self.year_sel.value()
        month = int(self.month_sel.currentText())
        days = calendar.monthrange(year, month)[1]
        
        # 간호사(D,E,N) 3열, 보호사(D,N) 2열 -> 한 날짜당 총 5열
        self.table3 = QTableWidget(12, days * 5 + 1)
        self.table3.setItemDelegate(VerticalTextDelegate())
        
        nurse_w = 30 # 간호사 열 너비
        aide_w = 45  # 보호사 열 너비 (1.5배)

        for d in range(1, days + 1):
            col_start = (d - 1) * 5 + 1
            # 날짜 병합 (5열)
            self.table3.setSpan(0, col_start, 1, 5)
            self.table3.setItem(0, col_start, QTableWidgetItem(str(d)))
            # 요일 병합 (5열)
            self.table3.setSpan(1, col_start, 1, 5)
            wd = self.get_weekday(d)
            wd_item = QTableWidgetItem(wd)
            if wd == "토": wd_item.setForeground(QColor("blue"))
            if wd == "일": wd_item.setForeground(QColor("red"))
            self.table3.setItem(1, col_start, wd_item)

            # 간호사 D,E,N 칼럼 (폭 30)
            for i, shift in enumerate(["D", "E", "N"]):
                self.table3.setItem(2, col_start + i, QTableWidgetItem(shift))
                self.table3.setColumnWidth(col_start + i, nurse_w)
            
            # 보호사 D,N 칼럼 (폭 45, 1.5배)
            for i, shift in enumerate(["D", "N"]):
                self.table3.setItem(7, col_start + 3 + i, QTableWidgetItem(shift))
                self.table3.setColumnWidth(col_start + 3 + i, aide_w)

        # 행 이름 및 색상/높이 설정
        row_names = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "구분", "3W", "4W", "5W"]
        for i, name in enumerate(row_names):
            self.table3.setItem(i, 0, QTableWidgetItem(name))
            bg = QColor("#FFFFE0") if i < 6 else QColor("#E0FFFF")
            self.table3.item(i, 0).setBackground(bg)
            # 이름이 들어가는 행(3,4,5,8,9,10)은 높이를 크게 설정
            if i in [3, 4, 5, 8, 9, 10]:
                self.table3.setRowHeight(i, 90)
            else:
                self.table3.setRowHeight(i, 30)

        if self.tabs.count() > 2: self.tabs.removeTab(2)
        self.tabs.insertTab(2, self.table3, "테이블 3 (출력용)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = DutyAppFinal()
    win.show()
=======
import sys
import calendar
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# 1. 전체 직원 명단 (요청하신 번호와 이름 그대로 반영)
NURSES = [
    (31, "최민애"), (32, "김유하"), (33, "김민경"), (34, "김다인"), (35, "김다솜"),
    (41, "이미경"), (42, "권수진"), (43, "정지우"), (44, "송선아"),
    (51, "김도연"), (52, "김나은"), (53, "허예리"), (54, "박수진"), (55, "김민영")
]
AIDES = [
    (36, "전치구"), (37, "김재호"), (38, "송재웅"), (39, "지정우"),
    (46, "송현찬"), (47, "김두현"), (48, "하영기"),
    (56, "서현도"), (57, "김두현(주)"), (58, "제상수")
]

class VerticalTextDelegate(QStyledItemDelegate):
    """이름을 세로로 쓰고 빨간색 Request를 처리하는 데리게이트"""
    def paint(self, painter, option, index):
        text = str(index.data() or "")
        if text:
            painter.save()
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

class DutyAppFinal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 관리 시스템 v4.1")
        self.setGeometry(20, 20, 1700, 980)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 상단 제어바
        top_bar = QHBoxLayout()
        self.year_sel = QSpinBox()
        self.year_sel.setRange(2024, 2030)
        self.year_sel.setValue(2025)
        self.month_sel = QComboBox()
        self.month_sel.addItems([f"{i:02d}" for i in range(1, 13)])
        self.month_sel.setCurrentText("12")
        self.month_sel.currentTextChanged.connect(self.refresh_all)
        
        self.cb_request = QCheckBox("🔴 Request 입력 모드 (빨간색)")
        self.cb_request.toggled.connect(lambda checked: setattr(self, 'request_mode', checked))
        
        self.btn_run = QPushButton("🚀 RUN (자동 완성)")
        self.btn_save = QPushButton("💾 저장 및 이월")
        
        top_bar.addWidget(QLabel("📅 설정:"))
        top_bar.addWidget(self.year_sel)
        top_bar.addWidget(QLabel("년"))
        top_bar.addWidget(self.month_sel)
        top_bar.addWidget(QLabel("월"))
        top_bar.addStretch()
        top_bar.addWidget(self.cb_request)
        top_bar.addWidget(self.btn_run)
        top_bar.addWidget(self.btn_save)
        layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # 테이블 생성
        self.setup_table1()
        self.setup_table2()
        self.setup_table3()

        # --- 하단 직원 명부 푸터 (요청하신 모든 번호와 이름 표시) ---
        footer = QFrame()
        footer.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        footer_layout = QVBoxLayout(footer)
        
        nurse_names = " | ".join([f"{n[0]} {n[1]}" for n in NURSES])
        aide_names = " | ".join([f"{a[0]} {a[1]}" for a in AIDES])
        
        f_label1 = QLabel(f"<b>[간호사 명단]</b> {nurse_names}")
        f_label2 = QLabel(f"<b>[보호사 명단]</b> {aide_names}")
        footer_layout.addWidget(f_label1)
        footer_layout.addWidget(f_label2)
        layout.addWidget(footer)

    def refresh_all(self):
        self.setup_table2()
        self.setup_table3()

    def get_weekday(self, day):
        year = self.year_sel.value()
        month = int(self.month_sel.currentText())
        days = ["월", "화", "수", "목", "금", "토", "일"]
        return days[calendar.weekday(year, month, day)]

    def setup_table1(self):
        staff = NURSES + AIDES
        self.table1 = QTableWidget(len(staff), 10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "12/31 막근", "연속일", "D", "E", "N", "O", "M"])
        for i, (num, name) in enumerate(staff):
            self.table1.setItem(i, 0, QTableWidgetItem(str(num)))
            self.table1.setItem(i, 1, QTableWidgetItem(name))
            role = "간호사" if i < len(NURSES) else "보호사"
            self.table1.setItem(i, 2, QTableWidgetItem(role))
        self.tabs.addTab(self.table1, "테이블 1 (설정)")

    def setup_table2(self):
        year = self.year_sel.value()
        month = int(self.month_sel.currentText())
        days_in_month = calendar.monthrange(year, month)[1]
        staff = NURSES + AIDES
        
        self.table2 = QTableWidget(len(staff), days_in_month + 2)
        # 헤더에 날짜와 요일 병기
        headers = ["번호", "성함"]
        for d in range(1, days_in_month + 1):
            headers.append(f"{d}\n({self.get_weekday(d)})")
        self.table2.setHorizontalHeaderLabels(headers)
        
        for r in range(len(staff)):
            color = QColor("#FFFFE0") if r < len(NURSES) else QColor("#E0FFFF")
            self.table2.setItem(r, 0, QTableWidgetItem(str(staff[r][0])))
            self.table2.setItem(r, 1, QTableWidgetItem(staff[r][1]))
            for c in range(days_in_month + 2):
                if c >= 2:
                    item = QTableWidgetItem("")
                    self.table2.setItem(r, c, item)
                self.table2.item(r, c).setBackground(color)
        
        self.table2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table2.cellChanged.connect(self.handle_table2_input)
        
        if self.tabs.count() > 1: self.tabs.removeTab(1)
        self.tabs.insertTab(1, self.table2, "테이블 2 (개인별)")

    def handle_table2_input(self, r, c):
        if c < 2: return
        item = self.table2.item(r, c)
        if item and self.request_mode and "[R]" not in item.text():
            self.table2.blockSignals(True)
            item.setText(f"[R]{item.text()}")
            item.setForeground(QColor("red"))
            self.table2.blockSignals(False)

    def setup_table3(self):
        year = self.year_sel.value()
        month = int(self.month_sel.currentText())
        days = calendar.monthrange(year, month)[1]
        
        # 간호사(D,E,N) 3열, 보호사(D,N) 2열 -> 한 날짜당 총 5열
        self.table3 = QTableWidget(12, days * 5 + 1)
        self.table3.setItemDelegate(VerticalTextDelegate())
        
        nurse_w = 30 # 간호사 열 너비
        aide_w = 45  # 보호사 열 너비 (1.5배)

        for d in range(1, days + 1):
            col_start = (d - 1) * 5 + 1
            # 날짜 병합 (5열)
            self.table3.setSpan(0, col_start, 1, 5)
            self.table3.setItem(0, col_start, QTableWidgetItem(str(d)))
            # 요일 병합 (5열)
            self.table3.setSpan(1, col_start, 1, 5)
            wd = self.get_weekday(d)
            wd_item = QTableWidgetItem(wd)
            if wd == "토": wd_item.setForeground(QColor("blue"))
            if wd == "일": wd_item.setForeground(QColor("red"))
            self.table3.setItem(1, col_start, wd_item)

            # 간호사 D,E,N 칼럼 (폭 30)
            for i, shift in enumerate(["D", "E", "N"]):
                self.table3.setItem(2, col_start + i, QTableWidgetItem(shift))
                self.table3.setColumnWidth(col_start + i, nurse_w)
            
            # 보호사 D,N 칼럼 (폭 45, 1.5배)
            for i, shift in enumerate(["D", "N"]):
                self.table3.setItem(7, col_start + 3 + i, QTableWidgetItem(shift))
                self.table3.setColumnWidth(col_start + 3 + i, aide_w)

        # 행 이름 및 색상/높이 설정
        row_names = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "구분", "3W", "4W", "5W"]
        for i, name in enumerate(row_names):
            self.table3.setItem(i, 0, QTableWidgetItem(name))
            bg = QColor("#FFFFE0") if i < 6 else QColor("#E0FFFF")
            self.table3.item(i, 0).setBackground(bg)
            # 이름이 들어가는 행(3,4,5,8,9,10)은 높이를 크게 설정
            if i in [3, 4, 5, 8, 9, 10]:
                self.table3.setRowHeight(i, 90)
            else:
                self.table3.setRowHeight(i, 30)

        if self.tabs.count() > 2: self.tabs.removeTab(2)
        self.tabs.insertTab(2, self.table3, "테이블 3 (출력용)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = DutyAppFinal()
    win.show()
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    sys.exit(app.exec())