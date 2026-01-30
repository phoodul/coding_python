<<<<<<< HEAD
import sys
import calendar
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# --- [기본 데이터 및 12월 근무표 탑재] ---
STAFF_INFO = [
    (31, "최민애", "간호사", "3W"), (32, "김유하", "간호사", "3W"), (33, "김민경", "간호사", "3W"),
    (34, "김다인", "간호사", "3W"), (35, "김다솜", "간호사", "3W"), (41, "이미경", "간호사", "4W"),
    (42, "권수진", "간호사", "4W"), (43, "정지우", "간호사", "4W"), (44, "송선아", "간호사", "4W"),
    (51, "김도연", "간호사", "5W"), (52, "김나은", "간호사", "5W"), (53, "허예리", "간호사", "5W"),
    (54, "박수진", "간호사", "5W"), (55, "김민영", "간호사", "5W"), (36, "전치구", "보호사", "3W"),
    (37, "김재호", "보호사", "3W"), (38, "송재웅", "보호사", "3W"), (39, "지정우", "보호사", "3W"),
    (46, "송현찬", "보호사", "4W"), (47, "김두현", "보호사", "4W"), (48, "하영기", "보호사", "4W"),
    (56, "서현도", "보호사", "5W"), (57, "김두현(주)", "보호사", "5W"), (58, "제상수", "보호사", "5W")
]

# 12월 실제 데이터 (Choi Min-ae 등 일부 예시 데이터 탑재)
DUTY_DATA_12 = {
    "31": ["D", "O", "D", "D", "D", "O", "O", "D", "D", "N", "N", "N", "O", "O", "D", "D", "N", "N", "N", "O", "O", "D", "D", "D", "O", "N", "N", "O", "O", "D", "D"],
    "36": ["D4", "D4", "D", "O", "D4", "O", "O", "N", "N", "O", "O", "D", "O", "O", "N", "N", "O", "O", "D5", "D5", "O", "O", "D", "D5", "O", "O", "D", "O", "N4", "N4", "N4"]
}

class VerticalTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 0: return super().paint(painter, option, index)
        text = str(index.data() or "")
        if text:
            painter.save()
            if "[R]" in text: painter.setPen(QColor("red")); text = text.replace("[R]", "")
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            v_text = "\n".join(list(text))
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, v_text)
            painter.restore()
        else: super().paint(painter, option, index)

class DutyAppV6(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 통합 관리기 v6.0")
        self.setGeometry(50, 50, 1600, 950)
        self.init_ui()
        self.load_december_data() # 데이터 로드 및 초기 연동 실행

    def init_ui(self):
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        self.setCentralWidget(main_scroll)
        container = QWidget(); main_scroll.setWidget(container); layout = QVBoxLayout(container)

        # 상단 컨트롤
        top_bar = QHBoxLayout()
        self.cb_request = QCheckBox("🔴 Request 모드")
        self.btn_run = QPushButton("🚀 RUN (자동 완성)"); self.btn_save = QPushButton("💾 저장")
        top_bar.addWidget(QLabel("📅 2025년 12월 데이터 기반")); top_bar.addStretch()
        top_bar.addWidget(self.cb_request); top_bar.addWidget(self.btn_run); top_bar.addWidget(self.btn_save)
        layout.addLayout(top_bar)

        self.tabs = QTabWidget(); layout.addWidget(self.tabs)
        self.setup_table1(); self.setup_table2(); self.setup_table3_tab()

        # 연동 시그널 연결
        self.table1.cellChanged.connect(self.on_table1_changed)
        self.table2.cellChanged.connect(self.on_table2_changed)
        self.table3.cellChanged.connect(self.on_table3_changed)

    def setup_table1(self):
        self.table1 = QTableWidget(len(STAFF_INFO), 10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "전월막근", "연속일", "D", "E", "N", "O", "M"])
        for i, info in enumerate(STAFF_INFO):
            self.table1.setItem(i, 0, QTableWidgetItem(str(info[0])))
            self.table1.setItem(i, 1, QTableWidgetItem(info[1]))
            self.table1.setItem(i, 2, QTableWidgetItem(info[2]))
            color = QColor("#FFFFE0") if info[2] == "간호사" else QColor("#E0FFFF")
            for c in range(10): 
                if not self.table1.item(i, c): self.table1.setItem(i, c, QTableWidgetItem(""))
                self.table1.item(i, c).setBackground(color)
        self.tabs.addTab(self.table1, "테이블 1 (설정)")

    def setup_table2(self, days=31):
        self.table2 = QTableWidget(len(STAFF_INFO), days + 2)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(i) for i in range(1, days + 1)])
        for r, info in enumerate(STAFF_INFO):
            self.table2.setItem(r, 0, QTableWidgetItem(str(info[0])))
            self.table2.setItem(r, 1, QTableWidgetItem(info[1]))
            color = QColor("#FFFFE0") if info[2] == "간호사" else QColor("#E0FFFF")
            for c in range(days + 2):
                if c >= 2: self.table2.setItem(r, c, QTableWidgetItem(""))
                self.table2.item(r, c).setBackground(color)
        self.table2.horizontalHeader().setDefaultSectionSize(35)
        self.tabs.addTab(self.table2, "테이블 2 (개인별 Duty)")

    def setup_table3_tab(self, days=31):
        tab_widget = QWidget(); tab_layout = QVBoxLayout(tab_widget)
        self.table3 = QTableWidget(10, days * 3 + 1); self.table3.setItemDelegate(VerticalTextDelegate())
        self.table3.setColumnWidth(0, 55)
        for d in range(1, days + 1):
            col = (d - 1) * 3 + 1
            for c in range(3): self.table3.setColumnWidth(col + c, 28)
            self.table3.setSpan(0, col, 1, 3); self.table3.setItem(0, col, QTableWidgetItem(str(d)))
            self.table3.setSpan(1, col, 1, 3); self.table3.setItem(1, col, QTableWidgetItem("일" if d % 7 == 0 else "토" if d % 7 == 6 else "평"))
        
        row_names = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, name in enumerate(row_names):
            self.table3.setItem(i, 0, QTableWidgetItem(name))
            bg = QColor("#FFFFE0") if i < 6 else QColor("#E0FFFF")
            self.table3.item(i, 0).setBackground(bg)
            if i in [3, 4, 5, 7, 8, 9]: self.table3.setRowHeight(i, 95)
        
        tab_layout.addWidget(self.table3)
        footer = QLabel(f"<b>[간호사]</b> {' | '.join([n[1] for n in STAFF_INFO if n[2]=='간호사'])}<br><b>[보호사]</b> {' | '.join([a[1] for a in STAFF_INFO if a[2]=='보호사'])}")
        tab_layout.addWidget(footer)
        self.tabs.addTab(tab_widget, "테이블 3 (출력용)")

    def load_december_data(self):
        self.table2.blockSignals(True)
        for r in range(self.table2.rowCount()):
            staff_id = self.table2.item(r, 0).text()
            if staff_id in DUTY_DATA_12:
                for d, duty in enumerate(DUTY_DATA_12[staff_id]):
                    self.table2.setItem(r, d + 2, QTableWidgetItem(duty))
        self.table2.blockSignals(False)
        self.sync_all_from_table2()

    def sync_all_from_table2(self):
        self.on_table2_changed(0, 2) # 전체 강제 업데이트 트리거

    def on_table1_changed(self, r, c):
        if c == 1: # 이름 변경 시
            new_name = self.table1.item(r, c).text()
            self.table2.item(r, 1).setText(new_name)

    def on_table2_changed(self, r, c):
        if c < 2: return
        self.update_table1_counts(r)
        self.update_table3_layout()

    def update_table1_counts(self, r):
        counts = {"D": 0, "E": 0, "N": 0, "O": 0, "M": 0}
        for c in range(2, self.table2.columnCount()):
            val = self.table2.item(r, c).text().upper()
            if "D" in val: counts["D"] += 1
            elif "E" in val: counts["E"] += 1
            elif "N" in val: counts["N"] += 1
            elif "O" in val or "♥" in val: counts["O"] += 1
            elif "M" in val: counts["M"] += 1
        
        self.table1.blockSignals(True)
        for i, key in enumerate(["D", "E", "N", "O", "M"]):
            self.table1.setItem(r, i + 5, QTableWidgetItem(str(counts[key])))
        self.table1.blockSignals(False)

    def update_table3_layout(self):
        self.table3.blockSignals(True)
        # 테이블 3 청소 후 재배치
        for r in [3, 4, 5, 7, 8, 9]:
            for c in range(1, self.table3.columnCount()): self.table3.setItem(r, c, QTableWidgetItem(""))
            
        for r in range(self.table2.rowCount()):
            name = self.table2.item(r, 1).text()
            ward = STAFF_INFO[r][3]
            role = STAFF_INFO[r][2]
            for d in range(2, self.table2.columnCount()):
                duty = self.table2.item(r, d).text().upper()
                col_offset = (d - 2) * 3 + 1
                if role == "간호사":
                    row = 3 if ward == "3W" else 4 if ward == "4W" else 5
                    if "D" in duty: self.table3.setItem(row, col_offset, QTableWidgetItem(name))
                    elif "E" in duty: self.table3.setItem(row, col_offset + 1, QTableWidgetItem(name))
                    elif "N" in duty: self.table3.setItem(row, col_offset + 2, QTableWidgetItem(name))
                else:
                    row = 7 if ward == "3W" else 8 if ward == "4W" else 9
                    if "D" in duty: self.table3.setItem(row, col_offset, QTableWidgetItem(name))
                    elif "N" in duty: self.table3.setItem(row, col_offset + 2, QTableWidgetItem(name))
        self.table3.blockSignals(False)

    def on_table3_changed(self, r, c):
        # 테이블 3에서 'X' 입력 시 테이블 2 연동 등 역방향 로직 구현 가능
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
=======
import sys
import calendar
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# --- [기본 데이터 및 12월 근무표 탑재] ---
STAFF_INFO = [
    (31, "최민애", "간호사", "3W"), (32, "김유하", "간호사", "3W"), (33, "김민경", "간호사", "3W"),
    (34, "김다인", "간호사", "3W"), (35, "김다솜", "간호사", "3W"), (41, "이미경", "간호사", "4W"),
    (42, "권수진", "간호사", "4W"), (43, "정지우", "간호사", "4W"), (44, "송선아", "간호사", "4W"),
    (51, "김도연", "간호사", "5W"), (52, "김나은", "간호사", "5W"), (53, "허예리", "간호사", "5W"),
    (54, "박수진", "간호사", "5W"), (55, "김민영", "간호사", "5W"), (36, "전치구", "보호사", "3W"),
    (37, "김재호", "보호사", "3W"), (38, "송재웅", "보호사", "3W"), (39, "지정우", "보호사", "3W"),
    (46, "송현찬", "보호사", "4W"), (47, "김두현", "보호사", "4W"), (48, "하영기", "보호사", "4W"),
    (56, "서현도", "보호사", "5W"), (57, "김두현(주)", "보호사", "5W"), (58, "제상수", "보호사", "5W")
]

# 12월 실제 데이터 (Choi Min-ae 등 일부 예시 데이터 탑재)
DUTY_DATA_12 = {
    "31": ["D", "O", "D", "D", "D", "O", "O", "D", "D", "N", "N", "N", "O", "O", "D", "D", "N", "N", "N", "O", "O", "D", "D", "D", "O", "N", "N", "O", "O", "D", "D"],
    "36": ["D4", "D4", "D", "O", "D4", "O", "O", "N", "N", "O", "O", "D", "O", "O", "N", "N", "O", "O", "D5", "D5", "O", "O", "D", "D5", "O", "O", "D", "O", "N4", "N4", "N4"]
}

class VerticalTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 0: return super().paint(painter, option, index)
        text = str(index.data() or "")
        if text:
            painter.save()
            if "[R]" in text: painter.setPen(QColor("red")); text = text.replace("[R]", "")
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            v_text = "\n".join(list(text))
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, v_text)
            painter.restore()
        else: super().paint(painter, option, index)

class DutyAppV6(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 통합 관리기 v6.0")
        self.setGeometry(50, 50, 1600, 950)
        self.init_ui()
        self.load_december_data() # 데이터 로드 및 초기 연동 실행

    def init_ui(self):
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        self.setCentralWidget(main_scroll)
        container = QWidget(); main_scroll.setWidget(container); layout = QVBoxLayout(container)

        # 상단 컨트롤
        top_bar = QHBoxLayout()
        self.cb_request = QCheckBox("🔴 Request 모드")
        self.btn_run = QPushButton("🚀 RUN (자동 완성)"); self.btn_save = QPushButton("💾 저장")
        top_bar.addWidget(QLabel("📅 2025년 12월 데이터 기반")); top_bar.addStretch()
        top_bar.addWidget(self.cb_request); top_bar.addWidget(self.btn_run); top_bar.addWidget(self.btn_save)
        layout.addLayout(top_bar)

        self.tabs = QTabWidget(); layout.addWidget(self.tabs)
        self.setup_table1(); self.setup_table2(); self.setup_table3_tab()

        # 연동 시그널 연결
        self.table1.cellChanged.connect(self.on_table1_changed)
        self.table2.cellChanged.connect(self.on_table2_changed)
        self.table3.cellChanged.connect(self.on_table3_changed)

    def setup_table1(self):
        self.table1 = QTableWidget(len(STAFF_INFO), 10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "전월막근", "연속일", "D", "E", "N", "O", "M"])
        for i, info in enumerate(STAFF_INFO):
            self.table1.setItem(i, 0, QTableWidgetItem(str(info[0])))
            self.table1.setItem(i, 1, QTableWidgetItem(info[1]))
            self.table1.setItem(i, 2, QTableWidgetItem(info[2]))
            color = QColor("#FFFFE0") if info[2] == "간호사" else QColor("#E0FFFF")
            for c in range(10): 
                if not self.table1.item(i, c): self.table1.setItem(i, c, QTableWidgetItem(""))
                self.table1.item(i, c).setBackground(color)
        self.tabs.addTab(self.table1, "테이블 1 (설정)")

    def setup_table2(self, days=31):
        self.table2 = QTableWidget(len(STAFF_INFO), days + 2)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(i) for i in range(1, days + 1)])
        for r, info in enumerate(STAFF_INFO):
            self.table2.setItem(r, 0, QTableWidgetItem(str(info[0])))
            self.table2.setItem(r, 1, QTableWidgetItem(info[1]))
            color = QColor("#FFFFE0") if info[2] == "간호사" else QColor("#E0FFFF")
            for c in range(days + 2):
                if c >= 2: self.table2.setItem(r, c, QTableWidgetItem(""))
                self.table2.item(r, c).setBackground(color)
        self.table2.horizontalHeader().setDefaultSectionSize(35)
        self.tabs.addTab(self.table2, "테이블 2 (개인별 Duty)")

    def setup_table3_tab(self, days=31):
        tab_widget = QWidget(); tab_layout = QVBoxLayout(tab_widget)
        self.table3 = QTableWidget(10, days * 3 + 1); self.table3.setItemDelegate(VerticalTextDelegate())
        self.table3.setColumnWidth(0, 55)
        for d in range(1, days + 1):
            col = (d - 1) * 3 + 1
            for c in range(3): self.table3.setColumnWidth(col + c, 28)
            self.table3.setSpan(0, col, 1, 3); self.table3.setItem(0, col, QTableWidgetItem(str(d)))
            self.table3.setSpan(1, col, 1, 3); self.table3.setItem(1, col, QTableWidgetItem("일" if d % 7 == 0 else "토" if d % 7 == 6 else "평"))
        
        row_names = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, name in enumerate(row_names):
            self.table3.setItem(i, 0, QTableWidgetItem(name))
            bg = QColor("#FFFFE0") if i < 6 else QColor("#E0FFFF")
            self.table3.item(i, 0).setBackground(bg)
            if i in [3, 4, 5, 7, 8, 9]: self.table3.setRowHeight(i, 95)
        
        tab_layout.addWidget(self.table3)
        footer = QLabel(f"<b>[간호사]</b> {' | '.join([n[1] for n in STAFF_INFO if n[2]=='간호사'])}<br><b>[보호사]</b> {' | '.join([a[1] for a in STAFF_INFO if a[2]=='보호사'])}")
        tab_layout.addWidget(footer)
        self.tabs.addTab(tab_widget, "테이블 3 (출력용)")

    def load_december_data(self):
        self.table2.blockSignals(True)
        for r in range(self.table2.rowCount()):
            staff_id = self.table2.item(r, 0).text()
            if staff_id in DUTY_DATA_12:
                for d, duty in enumerate(DUTY_DATA_12[staff_id]):
                    self.table2.setItem(r, d + 2, QTableWidgetItem(duty))
        self.table2.blockSignals(False)
        self.sync_all_from_table2()

    def sync_all_from_table2(self):
        self.on_table2_changed(0, 2) # 전체 강제 업데이트 트리거

    def on_table1_changed(self, r, c):
        if c == 1: # 이름 변경 시
            new_name = self.table1.item(r, c).text()
            self.table2.item(r, 1).setText(new_name)

    def on_table2_changed(self, r, c):
        if c < 2: return
        self.update_table1_counts(r)
        self.update_table3_layout()

    def update_table1_counts(self, r):
        counts = {"D": 0, "E": 0, "N": 0, "O": 0, "M": 0}
        for c in range(2, self.table2.columnCount()):
            val = self.table2.item(r, c).text().upper()
            if "D" in val: counts["D"] += 1
            elif "E" in val: counts["E"] += 1
            elif "N" in val: counts["N"] += 1
            elif "O" in val or "♥" in val: counts["O"] += 1
            elif "M" in val: counts["M"] += 1
        
        self.table1.blockSignals(True)
        for i, key in enumerate(["D", "E", "N", "O", "M"]):
            self.table1.setItem(r, i + 5, QTableWidgetItem(str(counts[key])))
        self.table1.blockSignals(False)

    def update_table3_layout(self):
        self.table3.blockSignals(True)
        # 테이블 3 청소 후 재배치
        for r in [3, 4, 5, 7, 8, 9]:
            for c in range(1, self.table3.columnCount()): self.table3.setItem(r, c, QTableWidgetItem(""))
            
        for r in range(self.table2.rowCount()):
            name = self.table2.item(r, 1).text()
            ward = STAFF_INFO[r][3]
            role = STAFF_INFO[r][2]
            for d in range(2, self.table2.columnCount()):
                duty = self.table2.item(r, d).text().upper()
                col_offset = (d - 2) * 3 + 1
                if role == "간호사":
                    row = 3 if ward == "3W" else 4 if ward == "4W" else 5
                    if "D" in duty: self.table3.setItem(row, col_offset, QTableWidgetItem(name))
                    elif "E" in duty: self.table3.setItem(row, col_offset + 1, QTableWidgetItem(name))
                    elif "N" in duty: self.table3.setItem(row, col_offset + 2, QTableWidgetItem(name))
                else:
                    row = 7 if ward == "3W" else 8 if ward == "4W" else 9
                    if "D" in duty: self.table3.setItem(row, col_offset, QTableWidgetItem(name))
                    elif "N" in duty: self.table3.setItem(row, col_offset + 2, QTableWidgetItem(name))
        self.table3.blockSignals(False)

    def on_table3_changed(self, r, c):
        # 테이블 3에서 'X' 입력 시 테이블 2 연동 등 역방향 로직 구현 가능
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    win = DutyAppV6(); win.show(); sys.exit(app.exec())