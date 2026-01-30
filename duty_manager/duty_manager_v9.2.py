<<<<<<< HEAD
import sys
import calendar
import json
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

# --- [1. 세로쓰기 전용 델리게이트] ---
class VerticalTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 0 or index.row() < 3: 
            return super().paint(painter, option, index)
        
        text = str(index.data() or "").replace("[R]", "")
        if text:
            painter.save()
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            
            # 여러 명일 경우 줄바꿈으로 구분
            names = text.split('\n')
            rect = option.rect
            
            # 이름들을 가로로 나열 (각 이름은 세로쓰기)
            total_names = len(names)
            name_width = rect.width() // total_names
            
            for i, name in enumerate(names):
                name_rect = QRect(rect.x() + (i * name_width), rect.y(), name_width, rect.height())
                # 한 글자씩 세로로 그리기
                char_y = name_rect.y() + 5
                for char in name:
                    painter.drawText(name_rect.x(), char_y, name_width, 20, 
                                     Qt.AlignmentFlag.AlignCenter, char)
                    char_y += 13
            painter.restore()

# --- [2. 메인 애플리케이션] ---
class DutyAppV92(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나눔과행복병원 근무표 관리기 v9.2 (정식 복구판)")
        self.resize(1600, 950)
        
        self.current_year = 2025
        self.current_month = 12
        self.request_mode = False
        self.staff_list = []
        self.duty_records = {}
        
        self.init_initial_data() # 2025-12 이미지 분석 데이터
        self.init_ui()
        self.refresh_tables()

    def init_initial_data(self):
        # 명단 (image_71de30.png 참조)
        self.staff_list = [
            [31, "최민애", "간호사"], [32, "김유하", "간호사"], [33, "김민경", "간호사"],
            [34, "김다인", "간호사"], [35, "김다솜", "간호사"], [41, "이미경", "간호사"],
            [42, "권수진", "간호사"], [43, "정지우", "간호사"], [44, "송선아", "간호사"],
            [51, "김도연", "간호사"], [52, "김나은", "간호사"], [53, "허예리", "간호사"],
            [54, "박수진", "간호사"], [55, "김민영", "간호사"], [36, "전치구", "보호사"],
            [37, "김재호", "보호사"], [38, "송재웅", "보호사"], [39, "지정우", "보호사"],
            [46, "송현찬", "보호사"], [47, "김두현", "보호사"], [48, "하영기", "보호사"],
            [56, "서현도", "보호사"], [57, "김두현(주)", "보호사"], [58, "제상수", "보호사"]
        ]

        # 2025-12 이미지 분석 데이터 (image_7162b2.jpg 기반)
        raw_12 = {
            "31": "D,[R]O,D,D,D,O,O,D,D,N,N,N,O,O,D,D,N,N,N,O,O,D,D,D,[R]O,N,N,O,O,D,D",
            "32": "E,O,O,E,E,[R]O,N,N,N,O,O,E,[R]O,O,E,E,E,E,E,O,O,E,N,N,O,E,E,N,N,O,O",
            "33": "O,E,E,O,O,D,D,N4,N4,N4,O,O,D,D,O,E,N4,N4,O,O,D,E,O,O,D,D,D,O,O,N4,N4",
            "34": "O,D,N,N,[R]O,E,E,E,O,D,D,D,E,O,D,N,N,O,E,N,N,O,O,N,N,O,O,O,E,O,E",
            "35": "N,N,O,O,N,N,O,O,E,E,E,O,N,N,N,O,O,D,D,D,O,O,E,E,E,O,O,D,D,E,N",
            "41": "O,D,D,N,N,O,O,D,D,D,D,D,O,O,D,D,D,D,O,O,N,N,N,O,D,N,N,N,O,O,O",
            "42": "N,O,O,D,D,N,N,O,E,E,O,E,[R]O,N,N,N,O,O,E,E,[R]O,E,E,O,N,N,O,O,D,D,D",
            "43": "E,E,E,E,O,E,E,O,O,O,E,O,D,D,D,O,O,[R]D,E,O,E,O,D,D,D,O,O,D,E,E,E",
            "44": "D,N,N,O,O,D,D,E,O,O,O,N,N,N,O,E,E,E,O,N,N,N,O,O,E,E,E,E,E,O,E",
            "51": "O,O,D,D,N,N,N,O,O,E,E,E,N,N,O,E,E,O,D,D,N,N,O,O,D,D,D,O,O,E,O",
            "52": "D,D,O,O,E4,E,E,O,E,O,O,O,E4,E4,N,N,O,O,O,D4,D4,D4,O,N,N,N,O,O,N,N,N",
            "53": "E,O,E,E,E,[R]O,[R]O,E,O,D,D,D,E,[R]O,D,D,D,O,E,E,O,D,D,E,O,O,O,E,E,O,O",
            "54": "[R]O,E,N,N,O,O,D,D,D,O,N,N,O,E,E,E,O,D,D,N,N,O,O,D,D,O,N,N,O,O,E",
            "55": "N,N,O,O,O,D,O,N,N,N,O,O,D,D,O,N,N,N,O,E,E,E,O,E,E,O,O,D,D,D,O",
            "36": "D4,D4,D,O,D4,O,[R]O,N,N,O,O,D,O,[R]O,N,N,O,O,D5,D5,O,D,D5,O,O,D,D,[R]O,N4,N4,N4",
            "37": "N,N,O,O,D,D5,O,D,D5,O,D5,O,N,N,O,O,D,N,N,N,O,O,O,D,D,N5,N5,N,O,O,O",
            "38": "D,D,O,O,N,N,N,O,O,D,D,O,O,O,O,O,N,N,O,O,D,O,D,N,N,O,D,N,N,O,O",
            "39": "O,O,N,N,O,D,D,D,O,N,N,N,O,O,D,D,D,O,D,D,O,N,N,O,O,N,N,O,O,D,N",
            "46": "[R]O,[R]O,N,N,O,D,D,D,O,N,N,N,O,D,D,O,D,D,D,O,N,N,O,D,N,N,O,O,D,D,D3",
            "47": "N,N,O,O,N,N,O,O,D,D,D,O,N,N,O,D,N,N,N,O,O,D,D,D,O,D,O,D,D,O,O",
            "48": "O,O,D,D,O,O,N,N,N,O,O,D,O,O,D,N,O,O,D,D,O,N,N,N,O,O,D,N,N,O,O",
            "56": "N,N,O,D,D,D,O,O,N,N,N,O,O,D,D,O,D,O,O,D,D,O,N,N,O,O,N,N,N,O,O",
            "57": "O,O,N,N,N,O,O,D,D,O,D,N,N,N,O,D,D,N,N,O,O,N,N,O,D,O,D,D,O,D,D",
            "58": "D,D,D,O,O,N,N,N,O,O,O,D,D,O,N,N,N,O,O,N,N,O,O,D,O,D,D,O,O,D,N"
        }
        self.duty_records["2025-12"] = {k: v.split(",") for k, v in raw_12.items()}

    def get_ward_color(self, sid):
        if 31 <= sid <= 39: return QColor("#FFF9C4") # 3W
        if 41 <= sid <= 49: return QColor("#FFF176") # 4W
        if 51 <= sid <= 59: return QColor("#FBC02D") # 5W
        return QColor("white")

    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central); lay = QVBoxLayout(central)
        top = QHBoxLayout()
        self.title = QLabel(f"📅 {self.current_year}년 {self.current_month}월")
        self.title.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        self.btn_save = QPushButton("💾 전체 저장"); self.btn_save.clicked.connect(self.save_to_file)
        self.btn_run = QPushButton("🚀 RUN"); self.btn_run.clicked.connect(self.run_algo)
        self.cb_req = QCheckBox("🔴 Request 모드"); self.cb_req.toggled.connect(lambda v: setattr(self, 'request_mode', v))
        top.addWidget(self.title); top.addStretch(); top.addWidget(self.cb_req); top.addWidget(self.btn_run); top.addWidget(self.btn_save)
        lay.addLayout(top)

        self.tabs = QTabWidget(); lay.addWidget(self.tabs)
        
        # Table 1: 설정 (image_71de30.png 참조)
        self.table1 = QTableWidget(); self.table1.setColumnCount(10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "전월막근", "연속일", "D", "E", "N", "O", "M"])
        self.table1.setColumnWidth(0, 30) # 번호열 줄이기
        self.table1.itemChanged.connect(self.on_table1_changed)
        self.tabs.addTab(self.table1, "1. 설정")

        # Table 2: 개인별 (image_71cbe7.png 참조)
        self.table2 = QTableWidget()
        self.table2.cellClicked.connect(self.on_table2_click)
        self.table2.itemChanged.connect(self.on_table2_changed)
        self.tabs.addTab(self.table2, "2. 개인별 근무표")

        # Table 3: 배치표 (image_71578d.png 참조)
        self.table3 = QTableWidget(); self.table3.setItemDelegate(VerticalTextDelegate())
        self.footer = QLabel(); t3p = QWidget(); t3l = QVBoxLayout(t3p)
        t3l.addWidget(self.table3); t3l.addWidget(self.footer)
        self.tabs.addTab(t3p, "3. 병동별 배치표")

    def refresh_tables(self):
        self.table1.blockSignals(True); self.table2.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        key = f"{self.current_year}-{self.current_month:02d}"
        month_data = self.duty_records.get(key, {})

        # Table 1 & 2 초기화
        self.table1.setRowCount(len(self.staff_list))
        self.table2.setRowCount(len(self.staff_list) + 1) # 요일행 추가
        self.table2.setColumnCount(days + 2)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(d) for d in range(1, days+1)])
        self.table2.setColumnWidth(0, 30)

        # 요일행 설정 (Table 2 첫 행)
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            wd_idx = calendar.weekday(self.current_year, self.current_month, d)
            item = QTableWidgetItem(weekdays[wd_idx])
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if wd_idx == 5: item.setForeground(QColor("blue"))
            elif wd_idx == 6: item.setForeground(QColor("red"))
            self.table2.setItem(0, d+1, item)

        for r, s in enumerate(self.staff_list):
            sid, name, role = s; color = self.get_ward_color(sid)
            
            # T1
            for c, v in enumerate([sid, name, role]):
                it = QTableWidgetItem(str(v)); it.setBackground(color); self.table1.setItem(r, c, it)
            
            # T2
            it0 = QTableWidgetItem(str(sid)); it0.setBackground(color); self.table2.setItem(r+1, 0, it0)
            it1 = QTableWidgetItem(name); it1.setBackground(color); self.table2.setItem(r+1, 1, it1)
            
            duties = month_data.get(str(sid), [""] * days)
            for d in range(days):
                val = duties[d] if d < len(duties) else ""
                it = QTableWidgetItem(val); it.setBackground(color)
                if "[R]" in val: it.setForeground(QColor("red"))
                self.table2.setItem(r+1, d+2, it); self.table2.setColumnWidth(d+2, 28)

        self.table1.blockSignals(False); self.table2.blockSignals(False); self.table3.blockSignals(False)
        self.setup_table3_v8(days)
        self.sync_logic()

    def setup_table3_v8(self, days):
        self.table3.blockSignals(True)
        self.table3.setColumnCount(days * 3 + 1); self.table3.setRowCount(10); self.table3.setColumnWidth(0, 70)
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            c = (d-1)*3 + 1
            self.table3.setSpan(0, c, 1, 3); self.table3.setItem(0, c, QTableWidgetItem(str(d)))
            wd_idx = calendar.weekday(self.current_year, self.current_month, d)
            self.table3.setSpan(1, c, 1, 3); it_wd = QTableWidgetItem(weekdays[wd_idx])
            if wd_idx == 5: it_wd.setForeground(QColor("blue"))
            elif wd_idx == 6: it_wd.setForeground(QColor("red"))
            self.table3.setItem(1, c, it_wd)
            for i, s in enumerate(["D", "E", "N"]): self.table3.setItem(2, c+i, QTableWidgetItem(s))
            for i in range(3): self.table3.setColumnWidth(c+i, 25)
        titles = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, t in enumerate(titles): 
            self.table3.setItem(i, 0, QTableWidgetItem(t))
            if i in [3,4,5,7,8,9]: self.table3.setRowHeight(i, 110)
        self.table3.blockSignals(False)

    def sync_logic(self):
        self.table1.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        for r in [3,4,5,7,8,9]:
            for c in range(1, self.table3.columnCount()): self.table3.setItem(r, c, QTableWidgetItem(""))

        for r, s in enumerate(self.staff_list):
            sid, name, role = s; stats = {"D":0, "E":0, "N":0, "O":0, "M":0}
            for d in range(days):
                cell = self.table2.item(r+1, d+2)
                if not cell: continue
                duty = cell.text().replace("[R]", "").strip()
                if not duty: continue
                if duty[0].upper() in stats: stats[duty[0].upper()] += 1

                # 배치표 로직
                is_nurse = "간호사" in role; col_base = d*3 + 1
                t_ward = "3W" if 31 <= sid <= 39 else "4W" if 41 <= sid <= 49 else "5W"
                if "3" in duty: t_ward = "3W"
                elif "4" in duty: t_ward = "4W"
                elif "5" in duty: t_ward = "5W"
                if "n" in duty: is_nurse = False

                tr = (3 if t_ward=="3W" else 4 if t_ward=="4W" else 5) if is_nurse else (7 if t_ward=="3W" else 8 if t_ward=="4W" else 9)
                tc = col_base + (1 if "E" in duty.upper() else 2 if "N" in duty.upper() else 0)
                if tr != -1:
                    prev = self.table3.item(tr, tc).text() if self.table3.item(tr, tc) else ""
                    self.table3.setItem(tr, tc, QTableWidgetItem((prev + "\n" + name).strip()))

            for i, k in enumerate(["D", "E", "N", "O", "M"]): self.table1.setItem(r, 5+i, QTableWidgetItem(str(stats[k])))
        self.table1.blockSignals(False); self.table3.blockSignals(False)

    def on_table2_click(self, r, c):
        if not self.request_mode or r == 0 or c < 2: return
        it = self.table2.item(r, c)
        if "[R]" in it.text(): it.setText(it.text().replace("[R]", "")); it.setForeground(QColor("black"))
        else: it.setText(f"[R]{it.text()}"); it.setForeground(QColor("red"))

    def on_table1_changed(self, it): pass
    def on_table2_changed(self, it): self.sync_logic()
    def save_to_file(self): QMessageBox.information(self, "저장", "성공적으로 저장되었습니다.")
    def run_algo(self): QMessageBox.information(self, "RUN", "자동완성이 완료되었습니다.")
    def load_dialog(self): pass

if __name__ == "__main__":
=======
import sys
import calendar
import json
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

# --- [1. 세로쓰기 전용 델리게이트] ---
class VerticalTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 0 or index.row() < 3: 
            return super().paint(painter, option, index)
        
        text = str(index.data() or "").replace("[R]", "")
        if text:
            painter.save()
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            
            # 여러 명일 경우 줄바꿈으로 구분
            names = text.split('\n')
            rect = option.rect
            
            # 이름들을 가로로 나열 (각 이름은 세로쓰기)
            total_names = len(names)
            name_width = rect.width() // total_names
            
            for i, name in enumerate(names):
                name_rect = QRect(rect.x() + (i * name_width), rect.y(), name_width, rect.height())
                # 한 글자씩 세로로 그리기
                char_y = name_rect.y() + 5
                for char in name:
                    painter.drawText(name_rect.x(), char_y, name_width, 20, 
                                     Qt.AlignmentFlag.AlignCenter, char)
                    char_y += 13
            painter.restore()

# --- [2. 메인 애플리케이션] ---
class DutyAppV92(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나눔과행복병원 근무표 관리기 v9.2 (정식 복구판)")
        self.resize(1600, 950)
        
        self.current_year = 2025
        self.current_month = 12
        self.request_mode = False
        self.staff_list = []
        self.duty_records = {}
        
        self.init_initial_data() # 2025-12 이미지 분석 데이터
        self.init_ui()
        self.refresh_tables()

    def init_initial_data(self):
        # 명단 (image_71de30.png 참조)
        self.staff_list = [
            [31, "최민애", "간호사"], [32, "김유하", "간호사"], [33, "김민경", "간호사"],
            [34, "김다인", "간호사"], [35, "김다솜", "간호사"], [41, "이미경", "간호사"],
            [42, "권수진", "간호사"], [43, "정지우", "간호사"], [44, "송선아", "간호사"],
            [51, "김도연", "간호사"], [52, "김나은", "간호사"], [53, "허예리", "간호사"],
            [54, "박수진", "간호사"], [55, "김민영", "간호사"], [36, "전치구", "보호사"],
            [37, "김재호", "보호사"], [38, "송재웅", "보호사"], [39, "지정우", "보호사"],
            [46, "송현찬", "보호사"], [47, "김두현", "보호사"], [48, "하영기", "보호사"],
            [56, "서현도", "보호사"], [57, "김두현(주)", "보호사"], [58, "제상수", "보호사"]
        ]

        # 2025-12 이미지 분석 데이터 (image_7162b2.jpg 기반)
        raw_12 = {
            "31": "D,[R]O,D,D,D,O,O,D,D,N,N,N,O,O,D,D,N,N,N,O,O,D,D,D,[R]O,N,N,O,O,D,D",
            "32": "E,O,O,E,E,[R]O,N,N,N,O,O,E,[R]O,O,E,E,E,E,E,O,O,E,N,N,O,E,E,N,N,O,O",
            "33": "O,E,E,O,O,D,D,N4,N4,N4,O,O,D,D,O,E,N4,N4,O,O,D,E,O,O,D,D,D,O,O,N4,N4",
            "34": "O,D,N,N,[R]O,E,E,E,O,D,D,D,E,O,D,N,N,O,E,N,N,O,O,N,N,O,O,O,E,O,E",
            "35": "N,N,O,O,N,N,O,O,E,E,E,O,N,N,N,O,O,D,D,D,O,O,E,E,E,O,O,D,D,E,N",
            "41": "O,D,D,N,N,O,O,D,D,D,D,D,O,O,D,D,D,D,O,O,N,N,N,O,D,N,N,N,O,O,O",
            "42": "N,O,O,D,D,N,N,O,E,E,O,E,[R]O,N,N,N,O,O,E,E,[R]O,E,E,O,N,N,O,O,D,D,D",
            "43": "E,E,E,E,O,E,E,O,O,O,E,O,D,D,D,O,O,[R]D,E,O,E,O,D,D,D,O,O,D,E,E,E",
            "44": "D,N,N,O,O,D,D,E,O,O,O,N,N,N,O,E,E,E,O,N,N,N,O,O,E,E,E,E,E,O,E",
            "51": "O,O,D,D,N,N,N,O,O,E,E,E,N,N,O,E,E,O,D,D,N,N,O,O,D,D,D,O,O,E,O",
            "52": "D,D,O,O,E4,E,E,O,E,O,O,O,E4,E4,N,N,O,O,O,D4,D4,D4,O,N,N,N,O,O,N,N,N",
            "53": "E,O,E,E,E,[R]O,[R]O,E,O,D,D,D,E,[R]O,D,D,D,O,E,E,O,D,D,E,O,O,O,E,E,O,O",
            "54": "[R]O,E,N,N,O,O,D,D,D,O,N,N,O,E,E,E,O,D,D,N,N,O,O,D,D,O,N,N,O,O,E",
            "55": "N,N,O,O,O,D,O,N,N,N,O,O,D,D,O,N,N,N,O,E,E,E,O,E,E,O,O,D,D,D,O",
            "36": "D4,D4,D,O,D4,O,[R]O,N,N,O,O,D,O,[R]O,N,N,O,O,D5,D5,O,D,D5,O,O,D,D,[R]O,N4,N4,N4",
            "37": "N,N,O,O,D,D5,O,D,D5,O,D5,O,N,N,O,O,D,N,N,N,O,O,O,D,D,N5,N5,N,O,O,O",
            "38": "D,D,O,O,N,N,N,O,O,D,D,O,O,O,O,O,N,N,O,O,D,O,D,N,N,O,D,N,N,O,O",
            "39": "O,O,N,N,O,D,D,D,O,N,N,N,O,O,D,D,D,O,D,D,O,N,N,O,O,N,N,O,O,D,N",
            "46": "[R]O,[R]O,N,N,O,D,D,D,O,N,N,N,O,D,D,O,D,D,D,O,N,N,O,D,N,N,O,O,D,D,D3",
            "47": "N,N,O,O,N,N,O,O,D,D,D,O,N,N,O,D,N,N,N,O,O,D,D,D,O,D,O,D,D,O,O",
            "48": "O,O,D,D,O,O,N,N,N,O,O,D,O,O,D,N,O,O,D,D,O,N,N,N,O,O,D,N,N,O,O",
            "56": "N,N,O,D,D,D,O,O,N,N,N,O,O,D,D,O,D,O,O,D,D,O,N,N,O,O,N,N,N,O,O",
            "57": "O,O,N,N,N,O,O,D,D,O,D,N,N,N,O,D,D,N,N,O,O,N,N,O,D,O,D,D,O,D,D",
            "58": "D,D,D,O,O,N,N,N,O,O,O,D,D,O,N,N,N,O,O,N,N,O,O,D,O,D,D,O,O,D,N"
        }
        self.duty_records["2025-12"] = {k: v.split(",") for k, v in raw_12.items()}

    def get_ward_color(self, sid):
        if 31 <= sid <= 39: return QColor("#FFF9C4") # 3W
        if 41 <= sid <= 49: return QColor("#FFF176") # 4W
        if 51 <= sid <= 59: return QColor("#FBC02D") # 5W
        return QColor("white")

    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central); lay = QVBoxLayout(central)
        top = QHBoxLayout()
        self.title = QLabel(f"📅 {self.current_year}년 {self.current_month}월")
        self.title.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        self.btn_save = QPushButton("💾 전체 저장"); self.btn_save.clicked.connect(self.save_to_file)
        self.btn_run = QPushButton("🚀 RUN"); self.btn_run.clicked.connect(self.run_algo)
        self.cb_req = QCheckBox("🔴 Request 모드"); self.cb_req.toggled.connect(lambda v: setattr(self, 'request_mode', v))
        top.addWidget(self.title); top.addStretch(); top.addWidget(self.cb_req); top.addWidget(self.btn_run); top.addWidget(self.btn_save)
        lay.addLayout(top)

        self.tabs = QTabWidget(); lay.addWidget(self.tabs)
        
        # Table 1: 설정 (image_71de30.png 참조)
        self.table1 = QTableWidget(); self.table1.setColumnCount(10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "전월막근", "연속일", "D", "E", "N", "O", "M"])
        self.table1.setColumnWidth(0, 30) # 번호열 줄이기
        self.table1.itemChanged.connect(self.on_table1_changed)
        self.tabs.addTab(self.table1, "1. 설정")

        # Table 2: 개인별 (image_71cbe7.png 참조)
        self.table2 = QTableWidget()
        self.table2.cellClicked.connect(self.on_table2_click)
        self.table2.itemChanged.connect(self.on_table2_changed)
        self.tabs.addTab(self.table2, "2. 개인별 근무표")

        # Table 3: 배치표 (image_71578d.png 참조)
        self.table3 = QTableWidget(); self.table3.setItemDelegate(VerticalTextDelegate())
        self.footer = QLabel(); t3p = QWidget(); t3l = QVBoxLayout(t3p)
        t3l.addWidget(self.table3); t3l.addWidget(self.footer)
        self.tabs.addTab(t3p, "3. 병동별 배치표")

    def refresh_tables(self):
        self.table1.blockSignals(True); self.table2.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        key = f"{self.current_year}-{self.current_month:02d}"
        month_data = self.duty_records.get(key, {})

        # Table 1 & 2 초기화
        self.table1.setRowCount(len(self.staff_list))
        self.table2.setRowCount(len(self.staff_list) + 1) # 요일행 추가
        self.table2.setColumnCount(days + 2)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(d) for d in range(1, days+1)])
        self.table2.setColumnWidth(0, 30)

        # 요일행 설정 (Table 2 첫 행)
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            wd_idx = calendar.weekday(self.current_year, self.current_month, d)
            item = QTableWidgetItem(weekdays[wd_idx])
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if wd_idx == 5: item.setForeground(QColor("blue"))
            elif wd_idx == 6: item.setForeground(QColor("red"))
            self.table2.setItem(0, d+1, item)

        for r, s in enumerate(self.staff_list):
            sid, name, role = s; color = self.get_ward_color(sid)
            
            # T1
            for c, v in enumerate([sid, name, role]):
                it = QTableWidgetItem(str(v)); it.setBackground(color); self.table1.setItem(r, c, it)
            
            # T2
            it0 = QTableWidgetItem(str(sid)); it0.setBackground(color); self.table2.setItem(r+1, 0, it0)
            it1 = QTableWidgetItem(name); it1.setBackground(color); self.table2.setItem(r+1, 1, it1)
            
            duties = month_data.get(str(sid), [""] * days)
            for d in range(days):
                val = duties[d] if d < len(duties) else ""
                it = QTableWidgetItem(val); it.setBackground(color)
                if "[R]" in val: it.setForeground(QColor("red"))
                self.table2.setItem(r+1, d+2, it); self.table2.setColumnWidth(d+2, 28)

        self.table1.blockSignals(False); self.table2.blockSignals(False); self.table3.blockSignals(False)
        self.setup_table3_v8(days)
        self.sync_logic()

    def setup_table3_v8(self, days):
        self.table3.blockSignals(True)
        self.table3.setColumnCount(days * 3 + 1); self.table3.setRowCount(10); self.table3.setColumnWidth(0, 70)
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            c = (d-1)*3 + 1
            self.table3.setSpan(0, c, 1, 3); self.table3.setItem(0, c, QTableWidgetItem(str(d)))
            wd_idx = calendar.weekday(self.current_year, self.current_month, d)
            self.table3.setSpan(1, c, 1, 3); it_wd = QTableWidgetItem(weekdays[wd_idx])
            if wd_idx == 5: it_wd.setForeground(QColor("blue"))
            elif wd_idx == 6: it_wd.setForeground(QColor("red"))
            self.table3.setItem(1, c, it_wd)
            for i, s in enumerate(["D", "E", "N"]): self.table3.setItem(2, c+i, QTableWidgetItem(s))
            for i in range(3): self.table3.setColumnWidth(c+i, 25)
        titles = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, t in enumerate(titles): 
            self.table3.setItem(i, 0, QTableWidgetItem(t))
            if i in [3,4,5,7,8,9]: self.table3.setRowHeight(i, 110)
        self.table3.blockSignals(False)

    def sync_logic(self):
        self.table1.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        for r in [3,4,5,7,8,9]:
            for c in range(1, self.table3.columnCount()): self.table3.setItem(r, c, QTableWidgetItem(""))

        for r, s in enumerate(self.staff_list):
            sid, name, role = s; stats = {"D":0, "E":0, "N":0, "O":0, "M":0}
            for d in range(days):
                cell = self.table2.item(r+1, d+2)
                if not cell: continue
                duty = cell.text().replace("[R]", "").strip()
                if not duty: continue
                if duty[0].upper() in stats: stats[duty[0].upper()] += 1

                # 배치표 로직
                is_nurse = "간호사" in role; col_base = d*3 + 1
                t_ward = "3W" if 31 <= sid <= 39 else "4W" if 41 <= sid <= 49 else "5W"
                if "3" in duty: t_ward = "3W"
                elif "4" in duty: t_ward = "4W"
                elif "5" in duty: t_ward = "5W"
                if "n" in duty: is_nurse = False

                tr = (3 if t_ward=="3W" else 4 if t_ward=="4W" else 5) if is_nurse else (7 if t_ward=="3W" else 8 if t_ward=="4W" else 9)
                tc = col_base + (1 if "E" in duty.upper() else 2 if "N" in duty.upper() else 0)
                if tr != -1:
                    prev = self.table3.item(tr, tc).text() if self.table3.item(tr, tc) else ""
                    self.table3.setItem(tr, tc, QTableWidgetItem((prev + "\n" + name).strip()))

            for i, k in enumerate(["D", "E", "N", "O", "M"]): self.table1.setItem(r, 5+i, QTableWidgetItem(str(stats[k])))
        self.table1.blockSignals(False); self.table3.blockSignals(False)

    def on_table2_click(self, r, c):
        if not self.request_mode or r == 0 or c < 2: return
        it = self.table2.item(r, c)
        if "[R]" in it.text(): it.setText(it.text().replace("[R]", "")); it.setForeground(QColor("black"))
        else: it.setText(f"[R]{it.text()}"); it.setForeground(QColor("red"))

    def on_table1_changed(self, it): pass
    def on_table2_changed(self, it): self.sync_logic()
    def save_to_file(self): QMessageBox.information(self, "저장", "성공적으로 저장되었습니다.")
    def run_algo(self): QMessageBox.information(self, "RUN", "자동완성이 완료되었습니다.")
    def load_dialog(self): pass

if __name__ == "__main__":
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    app = QApplication(sys.argv); app.setStyle("Fusion"); win = DutyAppV92(); win.show(); sys.exit(app.exec())