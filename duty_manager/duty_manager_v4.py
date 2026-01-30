<<<<<<< HEAD
import sys
import calendar
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# 이름 세로 쓰기를 위한 처리
class VerticalTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        text = str(index.data() or "")
        if text:
            painter.save()
            # Request 모드([R] 태그)일 경우 빨간색 처리
            if "[R]" in text:
                painter.setPen(QColor("red"))
                text = text.replace("[R]", "")
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            v_text = "\n".join(list(text))
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, v_text)
            painter.restore()
        else:
            super().paint(painter, option, index)

class DutyAppFinal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 관리 시스템 v4.0")
        self.setGeometry(30, 30, 1600, 950)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # --- 상단 컨트롤 영역 ---
        top_bar = QHBoxLayout()
        self.year_sel = QSpinBox()
        self.year_sel.setRange(2024, 2030)
        self.year_sel.setValue(2025)
        self.month_sel = QComboBox()
        self.month_sel.addItems([f"{i:02d}" for i in range(1, 13)])
        self.month_sel.setCurrentText("12")
        
        self.cb_request = QCheckBox("🔴 Request 입력 모드 (빨간색)")
        self.cb_request.toggled.connect(lambda checked: setattr(self, 'request_mode', checked))
        
        self.btn_run = QPushButton("🚀 RUN (자동 완성)")
        self.btn_save = QPushButton("💾 저장 및 이월")
        
        top_bar.addWidget(QLabel("📅 년도:"))
        top_bar.addWidget(self.year_sel)
        top_bar.addWidget(QLabel("월:"))
        top_bar.addWidget(self.month_sel)
        top_bar.addStretch()
        top_bar.addWidget(self.cb_request)
        top_bar.addWidget(self.btn_run)
        top_bar.addWidget(self.btn_save)
        layout.addLayout(top_bar)

        # --- 메인 탭 영역 ---
        self.tabs = QTabWidget()
        self.setup_table1() # 설정
        self.setup_table2() # 개인별
        self.setup_table3() # 병동별(엑셀형)
        layout.addWidget(self.tabs)

        # --- 하단 직원 명부 (테이블 3 아래 상시 표시) ---
        footer = QLabel(
            "<b>[간호사]</b> 31 최민애 | 32 김유하 | 33 김민경 | 34 김다인 | 35 김다솜 | 41 이미경 | 42 권수진 | 43 정지우 | 44 송선아 | 51 김도연 | 52 김나은 | 53 허예리 | 54 박수진 | 55 김민영<br>"
            "<b>[보호사]</b> 36 전치구 | 37 김재호 | 38 송재웅 | 39 지정우 | 46 송현찬 | 47 김두현 | 48 하영기 | 56 서현도 | 57 김두현(주) | 58 제상수"
        )
        footer.setStyleSheet("background: #f8f9fa; padding: 10px; border: 1px solid #ddd; font-family: 'Malgun Gothic';")
        layout.addWidget(footer)

    def setup_table1(self):
        # D, E, N, O, M 순서 조정
        self.table1 = QTableWidget(24, 8)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "D", "E", "N", "O", "M", "비고"])
        self.tabs.addTab(self.table1, "테이블 1 (설정)")

    def setup_table2(self):
        self.table2 = QTableWidget(24, 33)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(i) for i in range(1, 32)])
        for r in range(24):
            color = QColor("#FFFFE0") if r < 14 else QColor("#E0FFFF")
            for c in range(33):
                item = QTableWidgetItem("")
                item.setBackground(color)
                self.table2.setItem(r, c, item)
        self.table2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table2.cellChanged.connect(self.handle_input)
        self.tabs.addTab(self.table2, "테이블 2 (개인별)")

    def handle_input(self, r, c):
        if c < 2: return
        item = self.table2.item(r, c)
        if item and self.request_mode and "[R]" not in item.text():
            self.table2.blockSignals(True)
            text = item.text()
            item.setText(f"[R]{text}")
            item.setForeground(QColor("red"))
            self.table2.blockSignals(False)

    def setup_table3(self, days=31):
        self.table3 = QTableWidget(12, days * 3 + 1)
        self.table3.setItemDelegate(VerticalTextDelegate())
        # 헤더 그리기
        for d in range(1, days + 1):
            col = (d - 1) * 3 + 1
            self.table3.setSpan(0, col, 1, 3) # 날짜
            self.table3.setItem(0, col, QTableWidgetItem(str(d)))
            self.table3.setSpan(1, col, 1, 3) # 요일
            self.table3.setItem(2, col, QTableWidgetItem("D"))
            self.table3.setItem(2, col+1, QTableWidgetItem("E"))
            self.table3.setItem(2, col+2, QTableWidgetItem("N"))
            self.table3.setItem(7, col, QTableWidgetItem("D"))
            self.table3.setItem(7, col+1, QTableWidgetItem("N"))
        
        row_names = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "구분", "3W", "4W", "5W"]
        for i, name in enumerate(row_names):
            self.table3.setItem(i, 0, QTableWidgetItem(name))
            color = QColor("#FFFFE0") if i < 6 else QColor("#E0FFFF")
            self.table3.item(i, 0).setBackground(color)
        self.tabs.addTab(self.table3, "테이블 3 (병동별)")

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

# 이름 세로 쓰기를 위한 처리
class VerticalTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        text = str(index.data() or "")
        if text:
            painter.save()
            # Request 모드([R] 태그)일 경우 빨간색 처리
            if "[R]" in text:
                painter.setPen(QColor("red"))
                text = text.replace("[R]", "")
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            v_text = "\n".join(list(text))
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, v_text)
            painter.restore()
        else:
            super().paint(painter, option, index)

class DutyAppFinal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 관리 시스템 v4.0")
        self.setGeometry(30, 30, 1600, 950)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # --- 상단 컨트롤 영역 ---
        top_bar = QHBoxLayout()
        self.year_sel = QSpinBox()
        self.year_sel.setRange(2024, 2030)
        self.year_sel.setValue(2025)
        self.month_sel = QComboBox()
        self.month_sel.addItems([f"{i:02d}" for i in range(1, 13)])
        self.month_sel.setCurrentText("12")
        
        self.cb_request = QCheckBox("🔴 Request 입력 모드 (빨간색)")
        self.cb_request.toggled.connect(lambda checked: setattr(self, 'request_mode', checked))
        
        self.btn_run = QPushButton("🚀 RUN (자동 완성)")
        self.btn_save = QPushButton("💾 저장 및 이월")
        
        top_bar.addWidget(QLabel("📅 년도:"))
        top_bar.addWidget(self.year_sel)
        top_bar.addWidget(QLabel("월:"))
        top_bar.addWidget(self.month_sel)
        top_bar.addStretch()
        top_bar.addWidget(self.cb_request)
        top_bar.addWidget(self.btn_run)
        top_bar.addWidget(self.btn_save)
        layout.addLayout(top_bar)

        # --- 메인 탭 영역 ---
        self.tabs = QTabWidget()
        self.setup_table1() # 설정
        self.setup_table2() # 개인별
        self.setup_table3() # 병동별(엑셀형)
        layout.addWidget(self.tabs)

        # --- 하단 직원 명부 (테이블 3 아래 상시 표시) ---
        footer = QLabel(
            "<b>[간호사]</b> 31 최민애 | 32 김유하 | 33 김민경 | 34 김다인 | 35 김다솜 | 41 이미경 | 42 권수진 | 43 정지우 | 44 송선아 | 51 김도연 | 52 김나은 | 53 허예리 | 54 박수진 | 55 김민영<br>"
            "<b>[보호사]</b> 36 전치구 | 37 김재호 | 38 송재웅 | 39 지정우 | 46 송현찬 | 47 김두현 | 48 하영기 | 56 서현도 | 57 김두현(주) | 58 제상수"
        )
        footer.setStyleSheet("background: #f8f9fa; padding: 10px; border: 1px solid #ddd; font-family: 'Malgun Gothic';")
        layout.addWidget(footer)

    def setup_table1(self):
        # D, E, N, O, M 순서 조정
        self.table1 = QTableWidget(24, 8)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "D", "E", "N", "O", "M", "비고"])
        self.tabs.addTab(self.table1, "테이블 1 (설정)")

    def setup_table2(self):
        self.table2 = QTableWidget(24, 33)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(i) for i in range(1, 32)])
        for r in range(24):
            color = QColor("#FFFFE0") if r < 14 else QColor("#E0FFFF")
            for c in range(33):
                item = QTableWidgetItem("")
                item.setBackground(color)
                self.table2.setItem(r, c, item)
        self.table2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table2.cellChanged.connect(self.handle_input)
        self.tabs.addTab(self.table2, "테이블 2 (개인별)")

    def handle_input(self, r, c):
        if c < 2: return
        item = self.table2.item(r, c)
        if item and self.request_mode and "[R]" not in item.text():
            self.table2.blockSignals(True)
            text = item.text()
            item.setText(f"[R]{text}")
            item.setForeground(QColor("red"))
            self.table2.blockSignals(False)

    def setup_table3(self, days=31):
        self.table3 = QTableWidget(12, days * 3 + 1)
        self.table3.setItemDelegate(VerticalTextDelegate())
        # 헤더 그리기
        for d in range(1, days + 1):
            col = (d - 1) * 3 + 1
            self.table3.setSpan(0, col, 1, 3) # 날짜
            self.table3.setItem(0, col, QTableWidgetItem(str(d)))
            self.table3.setSpan(1, col, 1, 3) # 요일
            self.table3.setItem(2, col, QTableWidgetItem("D"))
            self.table3.setItem(2, col+1, QTableWidgetItem("E"))
            self.table3.setItem(2, col+2, QTableWidgetItem("N"))
            self.table3.setItem(7, col, QTableWidgetItem("D"))
            self.table3.setItem(7, col+1, QTableWidgetItem("N"))
        
        row_names = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "구분", "3W", "4W", "5W"]
        for i, name in enumerate(row_names):
            self.table3.setItem(i, 0, QTableWidgetItem(name))
            color = QColor("#FFFFE0") if i < 6 else QColor("#E0FFFF")
            self.table3.item(i, 0).setBackground(color)
        self.tabs.addTab(self.table3, "테이블 3 (병동별)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = DutyAppFinal()
    win.show()
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    sys.exit(app.exec())