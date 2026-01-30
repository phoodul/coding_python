<<<<<<< HEAD
import sys
import calendar
import json
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# --- [1. 전직원 명단 및 12월 전체 데이터] ---
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

# 2025년 12월 전체 데이터 (하트=O 처리)
RAW_DATA_12 = {
    "31": "D,O,D,D,D,O,O,D,D,N,N,N,O,O,D,D,N,N,N,O,O,D,D,D,O,N,N,O,O,D,D",
    "32": "E,O,O,E,E,O,N,N,N,O,O,E,O,O,E,E,E,E,E,O,O,E,N,N,O,E,E,N,N,O,O",
    "33": "O,E,E,O,O,D,D,N4,N4,N4,O,O,D,D,O,E,N4,N4,O,O,D,E,O,O,D,D,D,O,O,N4,N4",
    "34": "O,D,N,N,O,E,E,E,O,D,D,D,E,O,D,N,N,O,E,N,N,O,O,N,N,O,O,O,E,O,E",
    "35": "N,N,O,O,N,N,O,O,E,E,E,O,N,N,N,O,O,D,D,D,O,O,E,E,E,O,O,D,D,E,N",
    "41": "O,D,D,N,N,O,O,D,D,D,D,D,O,O,D,D,D,D,O,O,N,N,N,O,D,N,N,N,O,O,O",
    "42": "N,O,O,D,D,N,N,O,E,E,O,E,O,N,N,N,O,O,E,E,O,E,E,O,N,N,O,O,D,D,D",
    "43": "E,E,E,E,O,E,E,O,O,O,E,O,D,D,D,O,O,D,E,O,E,O,D,D,D,O,O,D,E,E,E",
    "44": "D,N,N,O,O,D,D,E,O,O,O,N,N,N,O,E,E,E,O,N,N,N,O,O,E,E,E,E,E,O,E",
    "51": "O,O,D,D,N,N,N,O,O,E,E,E,N,N,O,E,E,O,D,D,N,N,O,O,D,D,D,O,O,E,O",
    "52": "D,D,O,O,E4,E,E,O,E,O,O,O,E4,E4,N,N,O,O,O,D4,D4,D4,O,N,N,N,O,O,N,N,N",
    "53": "E,O,E,E,E,O,O,E,O,D,D,D,E,O,D,D,D,O,E,E,O,D,D,E,O,O,O,E,E,O,O",
    "54": "O,E,N,N,O,O,D,D,D,O,N,N,O,E,E,E,O,D,D,N,N,O,O,D,D,O,N,N,O,O,E",
    "55": "N,N,O,O,O,D,O,N,N,N,O,O,D,D,O,N,N,N,O,E,E,E,O,E,E,O,O,D,D,D,O",
    "36": "D4,D4,D,O,D4,O,O,N,N,O,O,D,O,O,N,N,O,O,D5,D5,O,D,D5,O,O,D,D,O,N4,N4,N4",
    "37": "N,N,O,O,D,D,O,D,D5,O,D5,O,N,N,O,O,D,N,N,N,O,O,O,D,D,N5,N5,N,O,O,O",
    "38": "D,D,O,O,N,N,N,O,O,D,D,O,O,O,O,O,N,N,O,O,D,O,D,N,N,O,D,N,N,O,O",
    "39": "O,O,N,N,O,D,D,D,O,N,N,N,O,O,D,D,D,O,D,D,O,N,N,O,O,N,N,O,O,D,N",
    "46": "O,O,N,N,O,D,D,D,O,N,N,N,O,D,D,O,D,D,D,O,N,N,O,D,N,N,O,O,D,D,D3",
    "47": "N,N,O,O,N,N,O,O,D,D,D,O,N,N,O,D,N,N,N,O,O,D,D,D,O,D,O,D,D,O,O",
    "48": "O,O,D,D,O,O,N,N,N,O,O,D,O,O,D,N,O,O,D,D,O,N,N,N,O,O,D,N,N,O,O",
    "56": "N,N,O,D,D,D,O,O,N,N,N,O,O,D,D,O,D,O,O,D,D,O,N,N,O,O,N,N,N,O,O",
    "57": "O,O,N,N,N,O,O,D,D,O,D,N,N,N,O,D,D,N,N,O,O,N,N,O,D,O,D,D,O,D,D",
    "58": "D,D,D,O,O,N,N,N,O,O,O,D,D,O,N,N,N,O,O,N,N,O,O,D,O,D,D,O,O,D,N"
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

class DutyAppV8(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 통합 관리기 v8.0")
        self.setGeometry(30, 30, 1650, 950)
        self.current_year = 2025
        self.current_month = 12
        self.all_data = {} # 저장된 모든 월 데이터
        self.init_ui()
        self.load_month_data(2025, 12) # 초기 로드: 12월

    def init_ui(self):
        main_scroll = QScrollArea(); main_scroll.setWidgetResizable(True)
        self.setCentralWidget(main_scroll)
        container = QWidget(); main_scroll.setWidget(container); layout = QVBoxLayout(container)

        # 상단 컨트롤
        top_bar = QHBoxLayout()
        self.label_date = QLabel("📅 2025년 12월")
        self.label_date.setFont(QFont("Malgun Gothic", 12, QFont.Weight.Bold))
        
        self.btn_prev = QPushButton("◀ 이전 달"); self.btn_prev.clicked.connect(self.go_prev)
        self.btn_next = QPushButton("다음 달 ▶"); self.btn_next.clicked.connect(self.go_next)
        self.btn_run = QPushButton("🚀 RUN (자동 완성)"); self.btn_run.clicked.connect(self.run_algo)
        self.btn_save = QPushButton("💾 저장"); self.btn_save.clicked.connect(self.save_data)
        self.cb_request = QCheckBox("🔴 Request 모드")
        self.cb_request.toggled.connect(lambda c: setattr(self, 'request_mode', c))

        top_bar.addWidget(self.label_date); top_bar.addWidget(self.btn_prev); top_bar.addWidget(self.btn_next)
        top_bar.addStretch(); top_bar.addWidget(self.cb_request); top_bar.addWidget(self.btn_run); top_bar.addWidget(self.btn_save)
        layout.addLayout(top_bar)

        self.tabs = QTabWidget(); layout.addWidget(self.tabs)
        self.setup_tables()

    def setup_tables(self):
        # 테이블 1
        self.table1 = QTableWidget(len(STAFF_INFO), 10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "전월막근", "연속일", "D", "E", "N", "O", "M"])
        self.table1.cellChanged.connect(self.on_table1_name_changed)
        self.tabs.addTab(self.table1, "테이블 1 (설정)")

        # 테이블 2
        self.table2 = QTableWidget(len(STAFF_INFO), 33)
        self.table2.cellChanged.connect(self.on_table2_changed)
        self.tabs.addTab(self.table2, "테이블 2 (개인별)")

        # 테이블 3 (푸터 포함)
        t3_container = QWidget(); t3_lay = QVBoxLayout(t3_container)
        self.table3 = QTableWidget(10, 31*3 + 1); self.table3.setItemDelegate(VerticalTextDelegate())
        t3_lay.addWidget(self.table3)
        self.footer = QLabel()
        t3_lay.addWidget(self.footer)
        self.tabs.addTab(t3_container, "테이블 3 (배치표)")

    def load_month_data(self, year, month):
        self.current_year, self.current_month = year, month
        self.label_date.setText(f"📅 {year}년 {month}월")
        days = calendar.monthrange(year, month)[1]
        
        # 테이블 초기화 및 헤더 세팅
        self.table2.setColumnCount(days + 2)
        headers = ["번호", "성함"] + [f"{d}\n{['월','화','수','목','금','토','일'][calendar.weekday(year, month, d)]}" for d in range(1, days+1)]
        self.table2.setHorizontalHeaderLabels(headers)
        
        # 데이터 불러오기
        key = f"{year}-{month:02d}"
        month_data = self.all_data.get(key, {})
        if not month_data and key == "2025-12":
            for sid, dstr in RAW_DATA_12.items(): month_data[sid] = dstr.split(",")

        # UI 업데이트
        self.table1.blockSignals(True); self.table2.blockSignals(True)
        for r, info in enumerate(STAFF_INFO):
            sid = str(info[0]); name = info[1]
            bg = QColor("#FFFFE0") if info[2] == "간호사" else QColor("#E0FFFF")
            
            # Table 1
            self.table1.setItem(r, 0, QTableWidgetItem(sid)); self.table1.item(r, 0).setBackground(bg)
            self.table1.setItem(r, 1, QTableWidgetItem(name)); self.table1.item(r, 1).setBackground(bg)
            self.table1.setItem(r, 2, QTableWidgetItem(info[2])); self.table1.item(r, 2).setBackground(bg)

            # Table 2
            self.table2.setItem(r, 0, QTableWidgetItem(sid)); self.table2.item(r, 0).setBackground(bg)
            self.table2.setItem(r, 1, QTableWidgetItem(name)); self.table2.item(r, 1).setBackground(bg)
            self.table2.setColumnWidth(1, 60)
            
            duty_list = month_data.get(sid, [""] * days)
            for d in range(days):
                val = duty_list[d] if d < len(duty_list) else ""
                item = QTableWidgetItem(val)
                item.setBackground(bg)
                self.table2.setItem(r, d + 2, item)
                self.table2.setColumnWidth(d + 2, 28)
        
        self.table1.blockSignals(False); self.table2.blockSignals(False)
        self.setup_table3_layout(days)
        self.sync_all()

    def setup_table3_layout(self, days):
        self.table3.setColumnCount(days * 3 + 1); self.table3.setColumnWidth(0, 60)
        for d in range(1, days + 1):
            col = (d - 1) * 3 + 1
            self.table3.setSpan(0, col, 1, 3); self.table3.setItem(0, col, QTableWidgetItem(str(d)))
            self.table3.setSpan(1, col, 1, 3)
            wd = ["월", "화", "수", "목", "금", "토", "일"][calendar.weekday(self.current_year, self.current_month, d)]
            wd_i = QTableWidgetItem(wd); wd_i.setForeground(QColor("blue") if wd=="토" else QColor("red") if wd=="일" else QColor("black"))
            self.table3.setItem(1, col, wd_i)
            for i, s in enumerate(["D", "E", "N"]): self.table3.setItem(2, col+i, QTableWidgetItem(s)); self.table3.setColumnWidth(col+i, 28)
            self.table3.setItem(6, col, QTableWidgetItem("D")); self.table3.setItem(6, col+2, QTableWidgetItem("N"))
            e_g = QTableWidgetItem(""); e_g.setBackground(QColor("lightgray")); self.table3.setItem(6, col+1, e_g)

        rows = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, r in enumerate(rows):
            self.table3.setItem(i, 0, QTableWidgetItem(r)); bg = QColor("#FFFFE0") if i < 6 else QColor("#E0FFFF")
            self.table3.item(i, 0).setBackground(bg)
            self.table3.setRowHeight(i, 100 if i in [3,4,5,7,8,9] else 35)
        
        n_footer = " | ".join([f"{n[0]}{n[1]}" for n in STAFF_INFO if n[2]=="간호사"])
        a_footer = " | ".join([f"{a[0]}{a[1]}" for a in STAFF_INFO if a[2]=="보호사"])
        self.footer.setText(f"<b>[간호사]</b> {n_footer}<br><b>[보호사]</b> {a_footer}")

    def on_table2_changed(self, r, c):
        if c < 2: return
        item = self.table2.item(r, c)
        if item and self.request_mode and "[R]" not in item.text():
            self.table2.blockSignals(True); item.setText(f"[R]{item.text()}"); item.setForeground(QColor("red")); self.table2.blockSignals(False)
        self.sync_all()

    def on_table1_name_changed(self, r, c):
        if c == 1: # 이름 연동
            name = self.table1.item(r, c).text()
            self.table2.blockSignals(True); self.table2.item(r, 1).setText(name); self.table2.blockSignals(False)
            self.sync_all()

    def sync_all(self):
        # 1. 월간 개수 계산 (Table 1)
        self.table1.blockSignals(True)
        for r in range(len(STAFF_INFO)):
            cnt = {"D":0, "E":0, "N":0, "O":0, "M":0}
            for c in range(2, self.table2.columnCount()):
                v = self.table2.item(r, c).text().upper()
                if "D" in v: cnt["D"]+=1
                elif "E" in v: cnt["E"]+=1
                elif "N" in v: cnt["N"]+=1
                elif "O" in v or "♥" in v: cnt["O"]+=1
                elif "M" in v: cnt["M"]+=1
            for i, k in enumerate(["D", "E", "N", "O", "M"]):
                self.table1.setItem(r, i+5, QTableWidgetItem(str(cnt[k])))
        self.table1.blockSignals(False)

        # 2. 배치표 업데이트 (Table 3)
        self.table3.blockSignals(True)
        for r in [3,4,5,7,8,9]:
            for c in range(1, self.table3.columnCount()): self.table3.setItem(r, c, QTableWidgetItem(""))
        for r in range(len(STAFF_INFO)):
            name = self.table2.item(r, 1).text(); role = STAFF_INFO[r][2]; ward = STAFF_INFO[r][3]
            for d in range(2, self.table2.columnCount()):
                duty = self.table2.item(r, d).text().upper(); col = (d-2)*3 + 1
                if role == "간호사":
                    t3_r = 3 if ward=="3W" else 4 if ward=="4W" else 5
                    if "D" in duty: self.append_t3(t3_r, col, name)
                    elif "E" in duty: self.append_t3(t3_r, col+1, name)
                    elif "N" in duty: self.append_t3(t3_r, col+2, name)
                else:
                    t3_r = 7 if ward=="3W" else 8 if ward=="4W" else 9
                    if "D" in duty: self.append_t3(t3_r, col, name)
                    elif "N" in duty: self.append_t3(t3_r, col+2, name)
        self.table3.blockSignals(False)

    def append_t3(self, r, c, name):
        curr = self.table3.item(r, c).text()
        self.table3.setItem(r, c, QTableWidgetItem(f"{curr}\n{name}".strip()))

    def go_prev(self): self.save_data(); m = self.current_month - 1; y = self.current_year
    def go_next(self):
        self.save_data()
        m = self.current_month + 1; y = self.current_year
        if m > 12: m = 1; y += 1
        
        # 이월 로직
        prev_key = f"{self.current_year}-{self.current_month:02d}"
        prev_data = self.all_data.get(prev_key, {})
        self.load_month_data(y, m)
        
        # 전월막근 및 연속일 계산
        self.table1.blockSignals(True)
        for r in range(len(STAFF_INFO)):
            p_duties = prev_data.get(str(STAFF_INFO[r][0]), [])
            last = p_duties[-1] if p_duties else "O"
            count = 0
            for d in reversed(p_duties):
                if d == last and last != "O": count += 1
                else: break
            self.table1.setItem(r, 3, QTableWidgetItem(last))
            self.table1.setItem(r, 4, QTableWidgetItem(str(count)))
        self.table1.blockSignals(False)

    def save_data(self):
        key = f"{self.current_year}-{self.current_month:02d}"
        month_dict = {}
        for r in range(self.table2.rowCount()):
            month_dict[self.table2.item(r, 0).text()] = [self.table2.item(r, c).text() for c in range(2, self.table2.columnCount())]
        self.all_data[key] = month_dict

    def run_algo(self): QMessageBox.information(self, "RUN", "설정된 8가지 규칙에 따라 빈칸을 자동 완성합니다.")

if __name__ == "__main__":
=======
import sys
import calendar
import json
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# --- [1. 전직원 명단 및 12월 전체 데이터] ---
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

# 2025년 12월 전체 데이터 (하트=O 처리)
RAW_DATA_12 = {
    "31": "D,O,D,D,D,O,O,D,D,N,N,N,O,O,D,D,N,N,N,O,O,D,D,D,O,N,N,O,O,D,D",
    "32": "E,O,O,E,E,O,N,N,N,O,O,E,O,O,E,E,E,E,E,O,O,E,N,N,O,E,E,N,N,O,O",
    "33": "O,E,E,O,O,D,D,N4,N4,N4,O,O,D,D,O,E,N4,N4,O,O,D,E,O,O,D,D,D,O,O,N4,N4",
    "34": "O,D,N,N,O,E,E,E,O,D,D,D,E,O,D,N,N,O,E,N,N,O,O,N,N,O,O,O,E,O,E",
    "35": "N,N,O,O,N,N,O,O,E,E,E,O,N,N,N,O,O,D,D,D,O,O,E,E,E,O,O,D,D,E,N",
    "41": "O,D,D,N,N,O,O,D,D,D,D,D,O,O,D,D,D,D,O,O,N,N,N,O,D,N,N,N,O,O,O",
    "42": "N,O,O,D,D,N,N,O,E,E,O,E,O,N,N,N,O,O,E,E,O,E,E,O,N,N,O,O,D,D,D",
    "43": "E,E,E,E,O,E,E,O,O,O,E,O,D,D,D,O,O,D,E,O,E,O,D,D,D,O,O,D,E,E,E",
    "44": "D,N,N,O,O,D,D,E,O,O,O,N,N,N,O,E,E,E,O,N,N,N,O,O,E,E,E,E,E,O,E",
    "51": "O,O,D,D,N,N,N,O,O,E,E,E,N,N,O,E,E,O,D,D,N,N,O,O,D,D,D,O,O,E,O",
    "52": "D,D,O,O,E4,E,E,O,E,O,O,O,E4,E4,N,N,O,O,O,D4,D4,D4,O,N,N,N,O,O,N,N,N",
    "53": "E,O,E,E,E,O,O,E,O,D,D,D,E,O,D,D,D,O,E,E,O,D,D,E,O,O,O,E,E,O,O",
    "54": "O,E,N,N,O,O,D,D,D,O,N,N,O,E,E,E,O,D,D,N,N,O,O,D,D,O,N,N,O,O,E",
    "55": "N,N,O,O,O,D,O,N,N,N,O,O,D,D,O,N,N,N,O,E,E,E,O,E,E,O,O,D,D,D,O",
    "36": "D4,D4,D,O,D4,O,O,N,N,O,O,D,O,O,N,N,O,O,D5,D5,O,D,D5,O,O,D,D,O,N4,N4,N4",
    "37": "N,N,O,O,D,D,O,D,D5,O,D5,O,N,N,O,O,D,N,N,N,O,O,O,D,D,N5,N5,N,O,O,O",
    "38": "D,D,O,O,N,N,N,O,O,D,D,O,O,O,O,O,N,N,O,O,D,O,D,N,N,O,D,N,N,O,O",
    "39": "O,O,N,N,O,D,D,D,O,N,N,N,O,O,D,D,D,O,D,D,O,N,N,O,O,N,N,O,O,D,N",
    "46": "O,O,N,N,O,D,D,D,O,N,N,N,O,D,D,O,D,D,D,O,N,N,O,D,N,N,O,O,D,D,D3",
    "47": "N,N,O,O,N,N,O,O,D,D,D,O,N,N,O,D,N,N,N,O,O,D,D,D,O,D,O,D,D,O,O",
    "48": "O,O,D,D,O,O,N,N,N,O,O,D,O,O,D,N,O,O,D,D,O,N,N,N,O,O,D,N,N,O,O",
    "56": "N,N,O,D,D,D,O,O,N,N,N,O,O,D,D,O,D,O,O,D,D,O,N,N,O,O,N,N,N,O,O",
    "57": "O,O,N,N,N,O,O,D,D,O,D,N,N,N,O,D,D,N,N,O,O,N,N,O,D,O,D,D,O,D,D",
    "58": "D,D,D,O,O,N,N,N,O,O,O,D,D,O,N,N,N,O,O,N,N,O,O,D,O,D,D,O,O,D,N"
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

class DutyAppV8(QMainWindow):
    def __init__(self):
        super().__init__()
        self.request_mode = False
        self.setWindowTitle("나눔과행복병원 근무표 통합 관리기 v8.0")
        self.setGeometry(30, 30, 1650, 950)
        self.current_year = 2025
        self.current_month = 12
        self.all_data = {} # 저장된 모든 월 데이터
        self.init_ui()
        self.load_month_data(2025, 12) # 초기 로드: 12월

    def init_ui(self):
        main_scroll = QScrollArea(); main_scroll.setWidgetResizable(True)
        self.setCentralWidget(main_scroll)
        container = QWidget(); main_scroll.setWidget(container); layout = QVBoxLayout(container)

        # 상단 컨트롤
        top_bar = QHBoxLayout()
        self.label_date = QLabel("📅 2025년 12월")
        self.label_date.setFont(QFont("Malgun Gothic", 12, QFont.Weight.Bold))
        
        self.btn_prev = QPushButton("◀ 이전 달"); self.btn_prev.clicked.connect(self.go_prev)
        self.btn_next = QPushButton("다음 달 ▶"); self.btn_next.clicked.connect(self.go_next)
        self.btn_run = QPushButton("🚀 RUN (자동 완성)"); self.btn_run.clicked.connect(self.run_algo)
        self.btn_save = QPushButton("💾 저장"); self.btn_save.clicked.connect(self.save_data)
        self.cb_request = QCheckBox("🔴 Request 모드")
        self.cb_request.toggled.connect(lambda c: setattr(self, 'request_mode', c))

        top_bar.addWidget(self.label_date); top_bar.addWidget(self.btn_prev); top_bar.addWidget(self.btn_next)
        top_bar.addStretch(); top_bar.addWidget(self.cb_request); top_bar.addWidget(self.btn_run); top_bar.addWidget(self.btn_save)
        layout.addLayout(top_bar)

        self.tabs = QTabWidget(); layout.addWidget(self.tabs)
        self.setup_tables()

    def setup_tables(self):
        # 테이블 1
        self.table1 = QTableWidget(len(STAFF_INFO), 10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "전월막근", "연속일", "D", "E", "N", "O", "M"])
        self.table1.cellChanged.connect(self.on_table1_name_changed)
        self.tabs.addTab(self.table1, "테이블 1 (설정)")

        # 테이블 2
        self.table2 = QTableWidget(len(STAFF_INFO), 33)
        self.table2.cellChanged.connect(self.on_table2_changed)
        self.tabs.addTab(self.table2, "테이블 2 (개인별)")

        # 테이블 3 (푸터 포함)
        t3_container = QWidget(); t3_lay = QVBoxLayout(t3_container)
        self.table3 = QTableWidget(10, 31*3 + 1); self.table3.setItemDelegate(VerticalTextDelegate())
        t3_lay.addWidget(self.table3)
        self.footer = QLabel()
        t3_lay.addWidget(self.footer)
        self.tabs.addTab(t3_container, "테이블 3 (배치표)")

    def load_month_data(self, year, month):
        self.current_year, self.current_month = year, month
        self.label_date.setText(f"📅 {year}년 {month}월")
        days = calendar.monthrange(year, month)[1]
        
        # 테이블 초기화 및 헤더 세팅
        self.table2.setColumnCount(days + 2)
        headers = ["번호", "성함"] + [f"{d}\n{['월','화','수','목','금','토','일'][calendar.weekday(year, month, d)]}" for d in range(1, days+1)]
        self.table2.setHorizontalHeaderLabels(headers)
        
        # 데이터 불러오기
        key = f"{year}-{month:02d}"
        month_data = self.all_data.get(key, {})
        if not month_data and key == "2025-12":
            for sid, dstr in RAW_DATA_12.items(): month_data[sid] = dstr.split(",")

        # UI 업데이트
        self.table1.blockSignals(True); self.table2.blockSignals(True)
        for r, info in enumerate(STAFF_INFO):
            sid = str(info[0]); name = info[1]
            bg = QColor("#FFFFE0") if info[2] == "간호사" else QColor("#E0FFFF")
            
            # Table 1
            self.table1.setItem(r, 0, QTableWidgetItem(sid)); self.table1.item(r, 0).setBackground(bg)
            self.table1.setItem(r, 1, QTableWidgetItem(name)); self.table1.item(r, 1).setBackground(bg)
            self.table1.setItem(r, 2, QTableWidgetItem(info[2])); self.table1.item(r, 2).setBackground(bg)

            # Table 2
            self.table2.setItem(r, 0, QTableWidgetItem(sid)); self.table2.item(r, 0).setBackground(bg)
            self.table2.setItem(r, 1, QTableWidgetItem(name)); self.table2.item(r, 1).setBackground(bg)
            self.table2.setColumnWidth(1, 60)
            
            duty_list = month_data.get(sid, [""] * days)
            for d in range(days):
                val = duty_list[d] if d < len(duty_list) else ""
                item = QTableWidgetItem(val)
                item.setBackground(bg)
                self.table2.setItem(r, d + 2, item)
                self.table2.setColumnWidth(d + 2, 28)
        
        self.table1.blockSignals(False); self.table2.blockSignals(False)
        self.setup_table3_layout(days)
        self.sync_all()

    def setup_table3_layout(self, days):
        self.table3.setColumnCount(days * 3 + 1); self.table3.setColumnWidth(0, 60)
        for d in range(1, days + 1):
            col = (d - 1) * 3 + 1
            self.table3.setSpan(0, col, 1, 3); self.table3.setItem(0, col, QTableWidgetItem(str(d)))
            self.table3.setSpan(1, col, 1, 3)
            wd = ["월", "화", "수", "목", "금", "토", "일"][calendar.weekday(self.current_year, self.current_month, d)]
            wd_i = QTableWidgetItem(wd); wd_i.setForeground(QColor("blue") if wd=="토" else QColor("red") if wd=="일" else QColor("black"))
            self.table3.setItem(1, col, wd_i)
            for i, s in enumerate(["D", "E", "N"]): self.table3.setItem(2, col+i, QTableWidgetItem(s)); self.table3.setColumnWidth(col+i, 28)
            self.table3.setItem(6, col, QTableWidgetItem("D")); self.table3.setItem(6, col+2, QTableWidgetItem("N"))
            e_g = QTableWidgetItem(""); e_g.setBackground(QColor("lightgray")); self.table3.setItem(6, col+1, e_g)

        rows = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, r in enumerate(rows):
            self.table3.setItem(i, 0, QTableWidgetItem(r)); bg = QColor("#FFFFE0") if i < 6 else QColor("#E0FFFF")
            self.table3.item(i, 0).setBackground(bg)
            self.table3.setRowHeight(i, 100 if i in [3,4,5,7,8,9] else 35)
        
        n_footer = " | ".join([f"{n[0]}{n[1]}" for n in STAFF_INFO if n[2]=="간호사"])
        a_footer = " | ".join([f"{a[0]}{a[1]}" for a in STAFF_INFO if a[2]=="보호사"])
        self.footer.setText(f"<b>[간호사]</b> {n_footer}<br><b>[보호사]</b> {a_footer}")

    def on_table2_changed(self, r, c):
        if c < 2: return
        item = self.table2.item(r, c)
        if item and self.request_mode and "[R]" not in item.text():
            self.table2.blockSignals(True); item.setText(f"[R]{item.text()}"); item.setForeground(QColor("red")); self.table2.blockSignals(False)
        self.sync_all()

    def on_table1_name_changed(self, r, c):
        if c == 1: # 이름 연동
            name = self.table1.item(r, c).text()
            self.table2.blockSignals(True); self.table2.item(r, 1).setText(name); self.table2.blockSignals(False)
            self.sync_all()

    def sync_all(self):
        # 1. 월간 개수 계산 (Table 1)
        self.table1.blockSignals(True)
        for r in range(len(STAFF_INFO)):
            cnt = {"D":0, "E":0, "N":0, "O":0, "M":0}
            for c in range(2, self.table2.columnCount()):
                v = self.table2.item(r, c).text().upper()
                if "D" in v: cnt["D"]+=1
                elif "E" in v: cnt["E"]+=1
                elif "N" in v: cnt["N"]+=1
                elif "O" in v or "♥" in v: cnt["O"]+=1
                elif "M" in v: cnt["M"]+=1
            for i, k in enumerate(["D", "E", "N", "O", "M"]):
                self.table1.setItem(r, i+5, QTableWidgetItem(str(cnt[k])))
        self.table1.blockSignals(False)

        # 2. 배치표 업데이트 (Table 3)
        self.table3.blockSignals(True)
        for r in [3,4,5,7,8,9]:
            for c in range(1, self.table3.columnCount()): self.table3.setItem(r, c, QTableWidgetItem(""))
        for r in range(len(STAFF_INFO)):
            name = self.table2.item(r, 1).text(); role = STAFF_INFO[r][2]; ward = STAFF_INFO[r][3]
            for d in range(2, self.table2.columnCount()):
                duty = self.table2.item(r, d).text().upper(); col = (d-2)*3 + 1
                if role == "간호사":
                    t3_r = 3 if ward=="3W" else 4 if ward=="4W" else 5
                    if "D" in duty: self.append_t3(t3_r, col, name)
                    elif "E" in duty: self.append_t3(t3_r, col+1, name)
                    elif "N" in duty: self.append_t3(t3_r, col+2, name)
                else:
                    t3_r = 7 if ward=="3W" else 8 if ward=="4W" else 9
                    if "D" in duty: self.append_t3(t3_r, col, name)
                    elif "N" in duty: self.append_t3(t3_r, col+2, name)
        self.table3.blockSignals(False)

    def append_t3(self, r, c, name):
        curr = self.table3.item(r, c).text()
        self.table3.setItem(r, c, QTableWidgetItem(f"{curr}\n{name}".strip()))

    def go_prev(self): self.save_data(); m = self.current_month - 1; y = self.current_year
    def go_next(self):
        self.save_data()
        m = self.current_month + 1; y = self.current_year
        if m > 12: m = 1; y += 1
        
        # 이월 로직
        prev_key = f"{self.current_year}-{self.current_month:02d}"
        prev_data = self.all_data.get(prev_key, {})
        self.load_month_data(y, m)
        
        # 전월막근 및 연속일 계산
        self.table1.blockSignals(True)
        for r in range(len(STAFF_INFO)):
            p_duties = prev_data.get(str(STAFF_INFO[r][0]), [])
            last = p_duties[-1] if p_duties else "O"
            count = 0
            for d in reversed(p_duties):
                if d == last and last != "O": count += 1
                else: break
            self.table1.setItem(r, 3, QTableWidgetItem(last))
            self.table1.setItem(r, 4, QTableWidgetItem(str(count)))
        self.table1.blockSignals(False)

    def save_data(self):
        key = f"{self.current_year}-{self.current_month:02d}"
        month_dict = {}
        for r in range(self.table2.rowCount()):
            month_dict[self.table2.item(r, 0).text()] = [self.table2.item(r, c).text() for c in range(2, self.table2.columnCount())]
        self.all_data[key] = month_dict

    def run_algo(self): QMessageBox.information(self, "RUN", "설정된 8가지 규칙에 따라 빈칸을 자동 완성합니다.")

if __name__ == "__main__":
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    app = QApplication(sys.argv); app.setStyle("Fusion"); win = DutyAppV8(); win.show(); sys.exit(app.exec())