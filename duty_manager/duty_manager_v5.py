<<<<<<< HEAD
import sys
import calendar
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# 직원 명단 데이터
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
    def paint(self, painter, option, index):
        # 첫 번째 열(라벨)은 가로쓰기, 나머지는 세로쓰기
        if index.column() == 0:
            super().paint(painter, option, index)
            return
            
        text = str(index.data() or "")
        if text:
            painter.save()
            if "[R]" in text:
                painter.setPen(QColor("red"))
                text = text.replace("[R]", "")
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            v_text = "\n".join(list(text))
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, v_text)
            painter.restore()
        else:
            super().paint(painter, option, index)

class DutyAppV5(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 관리 시스템 v5.0")
        self.setGeometry(50, 50, 1600, 900)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 상단 컨트롤
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
        self.btn_save = QPushButton("💾 저장")
        
        top_bar.addWidget(QLabel("📅 년/월:"))
        top_bar.addWidget(self.year_sel)
        top_bar.addWidget(self.month_sel)
        top_bar.addStretch()
        top_bar.addWidget(self.cb_request)
        top_bar.addWidget(self.btn_run)
        top_bar.addWidget(self.btn_save)
        layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.setup_table1()
        self.setup_table2()
        self.setup_table3_tab() # 테이블 3은 푸터를 포함한 탭으로 구성

    def setup_table1(self):
        staff = NURSES + AIDES
        self.table1 = QTableWidget(len(staff), 10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "전월막근", "연속일", "D", "E", "N", "O", "M"])
        for i, (num, name) in enumerate(staff):
            bg = QColor("#FFFFE0") if i < len(NURSES) else QColor("#E0FFFF")
            self.table1.setItem(i, 0, QTableWidgetItem(str(num)))
            self.table1.setItem(i, 1, QTableWidgetItem(name))
            role = "간호사" if i < len(NURSES) else "보호사"
            self.table1.setItem(i, 2, QTableWidgetItem(role))
            for c in range(10):
                if self.table1.item(i, c):
                    self.table1.item(i, c).setBackground(bg)
        self.tabs.addTab(self.table1, "테이블 1 (설정)")

    def setup_table2(self):
        year = self.year_sel.value()
        month = int(self.month_sel.currentText())
        days = calendar.monthrange(year, month)[1]
        staff = NURSES + AIDES
        
        self.table2 = QTableWidget(len(staff), days + 2)
        headers = ["번호", "성함"]
        for d in range(1, days + 1):
            wd = ["월", "화", "수", "목", "금", "토", "일"][calendar.weekday(year, month, d)]
            headers.append(f"{d}\n({wd})")
        self.table2.setHorizontalHeaderLabels(headers)
        
        for r in range(len(staff)):
            bg = QColor("#FFFFE0") if r < len(NURSES) else QColor("#E0FFFF")
            self.table2.setItem(r, 0, QTableWidgetItem(str(staff[r][0])))
            self.table2.setItem(r, 1, QTableWidgetItem(staff[r][1]))
            for c in range(days + 2):
                if c >= 2: self.table2.setItem(r, c, QTableWidgetItem(""))
                self.table2.item(r, c).setBackground(bg)
        
        self.table2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabs.addTab(self.table2, "테이블 2 (개인별)")

    def setup_table3_tab(self):
        # 테이블 3과 푸터를 담을 별도 탭 레이아웃
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        
        year = self.year_sel.value()
        month = int(self.month_sel.currentText())
        days = calendar.monthrange(year, month)[1]
        
        # 10행 구성: 날짜, 요일, 간호사(D/E/N), 3W, 4W, 5W, 보호사(D/E_gray/N), 3W, 4W, 5W
        self.table3 = QTableWidget(10, days * 3 + 1)
        self.table3.setItemDelegate(VerticalTextDelegate())
        
        for d in range(1, days + 1):
            col = (d - 1) * 3 + 1
            # 날짜/요일 병합
            self.table3.setSpan(0, col, 1, 3)
            self.table3.setItem(0, col, QTableWidgetItem(str(d)))
            self.table3.setSpan(1, col, 1, 3)
            wd = ["월", "화", "수", "목", "금", "토", "일"][calendar.weekday(year, month, d)]
            wd_item = QTableWidgetItem(wd)
            if wd == "토": wd_item.setForeground(QColor("blue"))
            if wd == "일": wd_item.setForeground(QColor("red"))
            self.table3.setItem(1, col, wd_item)

            # 간호사 헤더 (D,E,N)
            self.table3.setItem(2, col, QTableWidgetItem("D"))
            self.table3.setItem(2, col+1, QTableWidgetItem("E"))
            self.table3.setItem(2, col+2, QTableWidgetItem("N"))
            # 보호사 헤더 (D, Gray, N)
            self.table3.setItem(6, col, QTableWidgetItem("D"))
            e_gray = QTableWidgetItem("")
            e_gray.setBackground(QColor("#D3D3D3"))
            e_gray.setFlags(e_gray.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table3.setItem(6, col+1, e_gray)
            self.table3.setItem(6, col+2, QTableWidgetItem("N"))

            # 보호사 근무 행의 E열(col+1) 회색 처리
            for r in [7, 8, 9]:
                gray_cell = QTableWidgetItem("")
                gray_cell.setBackground(QColor("#D3D3D3"))
                gray_cell.setFlags(gray_cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table3.setItem(r, col+1, gray_cell)

        # 라벨 및 색상 설정
        row_names = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, name in enumerate(row_names):
            self.table3.setItem(i, 0, QTableWidgetItem(name))
            bg = QColor("#FFFFE0") if i < 6 else QColor("#E0FFFF")
            self.table3.item(i, 0).setBackground(bg)
            # 이름 행 높이 조정
            if i in [3, 4, 5, 7, 8, 9]: self.table3.setRowHeight(i, 100)
            else: self.table3.setRowHeight(i, 35)

        tab_layout.addWidget(self.table3)
        
        # 푸터 (테이블 3 탭 하단에만 배치)
        footer = QFrame()
        footer.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        f_lay = QVBoxLayout(footer)
        n_names = " | ".join([f"{n[0]} {n[1]}" for n in NURSES])
        a_names = " | ".join([f"{a[0]} {a[1]}" for a in AIDES])
        f_lay.addWidget(QLabel(f"<b>[간호사]</b> {n_names}"))
        f_lay.addWidget(QLabel(f"<b>[보호사]</b> {a_names}"))
        tab_layout.addWidget(footer)
        
        self.tabs.addTab(tab_widget, "테이블 3 (출력용)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = DutyAppV5()
    win.show()
=======
import sys
import calendar
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# 직원 명단 데이터
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
    def paint(self, painter, option, index):
        # 첫 번째 열(라벨)은 가로쓰기, 나머지는 세로쓰기
        if index.column() == 0:
            super().paint(painter, option, index)
            return
            
        text = str(index.data() or "")
        if text:
            painter.save()
            if "[R]" in text:
                painter.setPen(QColor("red"))
                text = text.replace("[R]", "")
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            v_text = "\n".join(list(text))
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, v_text)
            painter.restore()
        else:
            super().paint(painter, option, index)

class DutyAppV5(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 관리 시스템 v5.0")
        self.setGeometry(50, 50, 1600, 900)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 상단 컨트롤
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
        self.btn_save = QPushButton("💾 저장")
        
        top_bar.addWidget(QLabel("📅 년/월:"))
        top_bar.addWidget(self.year_sel)
        top_bar.addWidget(self.month_sel)
        top_bar.addStretch()
        top_bar.addWidget(self.cb_request)
        top_bar.addWidget(self.btn_run)
        top_bar.addWidget(self.btn_save)
        layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.setup_table1()
        self.setup_table2()
        self.setup_table3_tab() # 테이블 3은 푸터를 포함한 탭으로 구성

    def setup_table1(self):
        staff = NURSES + AIDES
        self.table1 = QTableWidget(len(staff), 10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "전월막근", "연속일", "D", "E", "N", "O", "M"])
        for i, (num, name) in enumerate(staff):
            bg = QColor("#FFFFE0") if i < len(NURSES) else QColor("#E0FFFF")
            self.table1.setItem(i, 0, QTableWidgetItem(str(num)))
            self.table1.setItem(i, 1, QTableWidgetItem(name))
            role = "간호사" if i < len(NURSES) else "보호사"
            self.table1.setItem(i, 2, QTableWidgetItem(role))
            for c in range(10):
                if self.table1.item(i, c):
                    self.table1.item(i, c).setBackground(bg)
        self.tabs.addTab(self.table1, "테이블 1 (설정)")

    def setup_table2(self):
        year = self.year_sel.value()
        month = int(self.month_sel.currentText())
        days = calendar.monthrange(year, month)[1]
        staff = NURSES + AIDES
        
        self.table2 = QTableWidget(len(staff), days + 2)
        headers = ["번호", "성함"]
        for d in range(1, days + 1):
            wd = ["월", "화", "수", "목", "금", "토", "일"][calendar.weekday(year, month, d)]
            headers.append(f"{d}\n({wd})")
        self.table2.setHorizontalHeaderLabels(headers)
        
        for r in range(len(staff)):
            bg = QColor("#FFFFE0") if r < len(NURSES) else QColor("#E0FFFF")
            self.table2.setItem(r, 0, QTableWidgetItem(str(staff[r][0])))
            self.table2.setItem(r, 1, QTableWidgetItem(staff[r][1]))
            for c in range(days + 2):
                if c >= 2: self.table2.setItem(r, c, QTableWidgetItem(""))
                self.table2.item(r, c).setBackground(bg)
        
        self.table2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabs.addTab(self.table2, "테이블 2 (개인별)")

    def setup_table3_tab(self):
        # 테이블 3과 푸터를 담을 별도 탭 레이아웃
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        
        year = self.year_sel.value()
        month = int(self.month_sel.currentText())
        days = calendar.monthrange(year, month)[1]
        
        # 10행 구성: 날짜, 요일, 간호사(D/E/N), 3W, 4W, 5W, 보호사(D/E_gray/N), 3W, 4W, 5W
        self.table3 = QTableWidget(10, days * 3 + 1)
        self.table3.setItemDelegate(VerticalTextDelegate())
        
        for d in range(1, days + 1):
            col = (d - 1) * 3 + 1
            # 날짜/요일 병합
            self.table3.setSpan(0, col, 1, 3)
            self.table3.setItem(0, col, QTableWidgetItem(str(d)))
            self.table3.setSpan(1, col, 1, 3)
            wd = ["월", "화", "수", "목", "금", "토", "일"][calendar.weekday(year, month, d)]
            wd_item = QTableWidgetItem(wd)
            if wd == "토": wd_item.setForeground(QColor("blue"))
            if wd == "일": wd_item.setForeground(QColor("red"))
            self.table3.setItem(1, col, wd_item)

            # 간호사 헤더 (D,E,N)
            self.table3.setItem(2, col, QTableWidgetItem("D"))
            self.table3.setItem(2, col+1, QTableWidgetItem("E"))
            self.table3.setItem(2, col+2, QTableWidgetItem("N"))
            # 보호사 헤더 (D, Gray, N)
            self.table3.setItem(6, col, QTableWidgetItem("D"))
            e_gray = QTableWidgetItem("")
            e_gray.setBackground(QColor("#D3D3D3"))
            e_gray.setFlags(e_gray.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table3.setItem(6, col+1, e_gray)
            self.table3.setItem(6, col+2, QTableWidgetItem("N"))

            # 보호사 근무 행의 E열(col+1) 회색 처리
            for r in [7, 8, 9]:
                gray_cell = QTableWidgetItem("")
                gray_cell.setBackground(QColor("#D3D3D3"))
                gray_cell.setFlags(gray_cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table3.setItem(r, col+1, gray_cell)

        # 라벨 및 색상 설정
        row_names = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, name in enumerate(row_names):
            self.table3.setItem(i, 0, QTableWidgetItem(name))
            bg = QColor("#FFFFE0") if i < 6 else QColor("#E0FFFF")
            self.table3.item(i, 0).setBackground(bg)
            # 이름 행 높이 조정
            if i in [3, 4, 5, 7, 8, 9]: self.table3.setRowHeight(i, 100)
            else: self.table3.setRowHeight(i, 35)

        tab_layout.addWidget(self.table3)
        
        # 푸터 (테이블 3 탭 하단에만 배치)
        footer = QFrame()
        footer.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        f_lay = QVBoxLayout(footer)
        n_names = " | ".join([f"{n[0]} {n[1]}" for n in NURSES])
        a_names = " | ".join([f"{a[0]} {a[1]}" for a in AIDES])
        f_lay.addWidget(QLabel(f"<b>[간호사]</b> {n_names}"))
        f_lay.addWidget(QLabel(f"<b>[보호사]</b> {a_names}"))
        tab_layout.addWidget(footer)
        
        self.tabs.addTab(tab_widget, "테이블 3 (출력용)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = DutyAppV5()
    win.show()
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    sys.exit(app.exec())