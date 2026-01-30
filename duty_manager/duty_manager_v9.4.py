<<<<<<< HEAD
import sys
import calendar
import json
import os
import random
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

# --- [1. 세로쓰기 전용 델리게이트] ---
class VerticalTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 0 or index.row() < 3: 
            return super().paint(painter, option, index)
        
        text = str(index.data() or "")
        if text:
            painter.save()
            # 빨간색 글씨 처리 (Request)
            fg_color = index.data(Qt.ItemDataRole.ForegroundRole)
            if isinstance(fg_color, QColor) and fg_color == QColor("red"):
                painter.setPen(QColor("red"))
            
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            names = text.split('\n')
            rect = option.rect
            total_names = len(names)
            name_width = rect.width() // max(1, total_names)
            
            for i, name in enumerate(names):
                name_rect = QRect(rect.x() + (i * name_width), rect.y(), name_width, rect.height())
                char_y = name_rect.y() + 5
                for char in name:
                    painter.drawText(name_rect.x(), char_y, name_width, 15, 
                                     Qt.AlignmentFlag.AlignCenter, char)
                    char_y += 13
            painter.restore()

# --- [2. 메인 애플리케이션] ---
class DutyAppV94(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나눔과행복병원 근무표 통합 관리기 v9.4")
        self.resize(1650, 950)
        
        self.current_year = 2025
        self.current_month = 12
        self.request_mode = False
        self.staff_list = []
        self.duty_records = {} 
        self.request_records = {} 
        
        self.init_initial_data() 
        self.init_ui()
        self.refresh_tables()

    def init_initial_data(self):
        # 기본 명단 설정
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
        key = "2025-12"
        # 초기 데이터 로드 (v9.3과 동일한 데이터 구조)
        raw_12 = {"31": "D,O,D,D,D,O,O,D,D,N,N,N,O,O,D,D,N,N,N,O,O,D,D,D,O,N,N,O,O,D,D", "32": "E,O,O,E,E,O,N,N,N,O,O,E,O,O,E,E,E,E,E,O,O,E,N,N,O,E,E,N,N,O,O", "33": "O,E,E,O,O,D,D,N4,N4,N4,O,O,D,D,O,E,N4,N4,O,O,D,E,O,O,D,D,D,O,O,N4,N4", "34": "O,D,N,N,O,E,E,E,O,D,D,D,E,O,D,N,N,O,E,N,N,O,O,N,N,O,O,O,E,O,E", "35": "N,N,O,O,N,N,O,O,E,E,E,O,N,N,N,O,O,D,D,D,O,O,E,E,E,O,O,D,D,E,N", "41": "O,D,D,N,N,O,O,D,D,D,D,D,O,O,D,D,D,D,O,O,N,N,N,O,D,N,N,N,O,O,O", "42": "N,O,O,D,D,N,N,O,E,E,O,E,O,N,N,N,O,O,E,E,O,E,E,O,N,N,O,O,D,D,D", "43": "E,E,E,E,O,E,E,O,O,O,E,O,D,D,D,O,O,D,E,O,E,O,D,D,D,O,O,D,E,E,E", "44": "D,N,N,O,O,D,D,E,O,O,O,N,N,N,O,E,E,E,O,N,N,N,O,O,E,E,E,E,E,O,E", "51": "O,O,D,D,N,N,N,O,O,E,E,E,N,N,O,E,E,O,D,D,N,N,O,O,D,D,D,O,O,E,O", "52": "D,D,O,O,E4,E,E,O,E,O,O,O,E4,E4,N,N,O,O,O,D4,D4,D4,O,N,N,N,O,O,N,N,N", "53": "E,O,E,E,E,O,O,E,O,D,D,D,E,O,D,D,D,O,E,E,O,D,D,E,O,O,O,E,E,O,O", "54": "O,E,N,N,O,O,D,D,D,O,N,N,O,E,E,E,O,D,D,N,N,O,O,D,D,O,N,N,O,O,E", "55": "N,N,O,O,O,D,O,N,N,N,O,O,D,D,O,N,N,N,O,E,E,E,O,E,E,O,O,D,D,D,O", "36": "D4,D4,D,O,D4,O,O,N,N,O,O,D,O,O,N,N,O,O,D5,D5,O,D,D5,O,O,D,D,O,N4,N4,N4", "37": "N,N,O,O,D,D5,O,D,D5,O,D5,O,N,N,O,O,D,N,N,N,O,O,O,D,D,N5,N5,N,O,O,O", "38": "D,D,O,O,N,N,N,O,O,D,D,O,O,O,O,O,N,N,O,O,D,O,D,N,N,O,D,N,N,O,O", "39": "O,O,N,N,O,D,D,D,O,N,N,N,O,O,D,D,D,O,D,D,O,N,N,O,O,N,N,O,O,D,N", "46": "O,O,N,N,O,D,D,D,O,N,N,N,O,D,D,O,D,D,D,O,N,N,O,D,N,N,O,O,D,D,D3", "47": "N,N,O,O,N,N,O,O,D,D,D,O,N,N,O,D,N,N,N,O,O,D,D,D,O,D,O,D,D,O,O", "48": "O,O,D,D,O,O,N,N,N,O,O,D,O,O,D,N,O,O,D,D,O,N,N,N,O,O,D,N,N,O,O", "56": "N,N,O,D,D,D,O,O,N,N,N,O,O,D,D,O,D,O,O,D,D,O,N,N,O,O,N,N,N,O,O", "57": "O,O,N,N,N,O,O,D,D,O,D,N,N,N,O,D,D,N,N,O,O,N,N,O,D,O,D,D,O,D,D", "58": "D,D,D,O,O,N,N,N,O,O,O,D,D,O,N,N,N,O,O,N,N,O,O,D,O,D,D,O,O,D,N"}
        self.duty_records[key] = {k: v.split(",") for k, v in raw_12.items()}
        self.request_records[key] = {k: [False]*31 for k in raw_12.keys()}
        self.request_records[key]["31"][1] = True # 예시: 최민애 12/2 빨간색

    def get_ward_color(self, sid):
        if 31 <= sid <= 35: return QColor("#FFF9C4") # 3W 간호
        if 41 <= sid <= 45: return QColor("#FFF176") # 4W 간호
        if 51 <= sid <= 55: return QColor("#FBC02D") # 5W 간호
        if 36 <= sid <= 39: return QColor("#E1F5FE") # 3W 보호
        if 46 <= sid <= 49: return QColor("#81D4FA") # 4W 보호
        if 56 <= sid <= 59: return QColor("#29B6F6") # 5W 보호
        return QColor("white")

    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central); main_lay = QVBoxLayout(central)
        self.tabs = QTabWidget(); main_lay.addWidget(self.tabs)
        
        # --- 테이블 1 ---
        t1_page = QWidget(); t1_lay = QVBoxLayout(t1_page)
        self.title_t1 = QLabel(); self.title_t1.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        t1_lay.addWidget(self.title_t1)
        t1_top = QHBoxLayout()
        self.btn_load = QPushButton("📂 불러오기"); self.btn_load.clicked.connect(self.load_dialog)
        self.btn_save = QPushButton("💾 저장"); self.btn_save.clicked.connect(self.save_to_file)
        self.btn_next1 = QPushButton("다음 달 ▶"); self.btn_next1.clicked.connect(self.go_next)
        t1_top.addStretch(); t1_top.addWidget(self.btn_load); t1_top.addWidget(self.btn_save); t1_top.addWidget(self.btn_next1)
        t1_lay.addLayout(t1_top)
        self.table1 = QTableWidget(); self.table1.setColumnCount(10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "전월막근", "연속일", "D", "E", "N", "O", "M"])
        self.table1.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table1.customContextMenuRequested.connect(self.show_context_menu)
        self.table1.itemChanged.connect(self.on_table1_changed)
        t1_lay.addWidget(self.table1); self.tabs.addTab(t1_page, "테이블 1 (설정)")

        # --- 테이블 2 ---
        t2_page = QWidget(); t2_lay = QVBoxLayout(t2_page)
        self.title_t2 = QLabel(); self.title_t2.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        t2_lay.addWidget(self.title_t2)
        t2_top = QHBoxLayout()
        self.cb_req = QCheckBox("🔴 Request 모드"); self.cb_req.toggled.connect(lambda v: setattr(self, 'request_mode', v))
        self.btn_run = QPushButton("🚀 RUN (자동완성)"); self.btn_run.clicked.connect(self.run_algo)
        self.btn_print2 = QPushButton("🖨️ 인쇄"); self.btn_print2.clicked.connect(lambda: self.print_preview(self.table2))
        self.btn_next2 = QPushButton("다음 달 ▶"); self.btn_next2.clicked.connect(self.go_next)
        t2_top.addWidget(self.cb_req); t2_top.addStretch(); t2_top.addWidget(self.btn_run); t2_top.addWidget(self.btn_print2); t2_top.addWidget(self.btn_next2)
        t2_lay.addLayout(t2_top)
        self.table2 = QTableWidget(); self.table2.cellClicked.connect(self.on_table2_click)
        self.table2.itemChanged.connect(self.on_table2_changed)
        t2_lay.addWidget(self.table2); self.tabs.addTab(t2_page, "테이블 2 (개인별)")

        # --- 테이블 3 ---
        t3_page = QWidget(); t3_lay = QVBoxLayout(t3_page)
        self.title_t3 = QLabel(); self.title_t3.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        t3_lay.addWidget(self.title_t3)
        t3_top = QHBoxLayout()
        self.btn_print3 = QPushButton("🖨️ 인쇄 (A4 가로)"); self.btn_print3.clicked.connect(lambda: self.print_preview(self.table3))
        self.btn_next3 = QPushButton("다음 달 ▶"); self.btn_next3.clicked.connect(self.go_next)
        t3_top.addStretch(); t3_top.addWidget(self.btn_print3); t3_top.addWidget(self.btn_next3)
        t3_lay.addLayout(t3_top)
        self.table3 = QTableWidget(); self.table3.setItemDelegate(VerticalTextDelegate())
        t3_lay.addWidget(self.table3)
        self.footer = QLabel(); self.footer.setFont(QFont("Malgun Gothic", 9))
        t3_lay.addWidget(self.footer); self.tabs.addTab(t3_page, "테이블 3 (배치표)")

    def refresh_tables(self):
        self.table1.blockSignals(True); self.table2.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        date_str = f"📅 {self.current_year}년 {self.current_month}월 근무표"
        self.title_t1.setText(date_str); self.title_t2.setText(date_str); self.title_t3.setText(date_str)
        
        key = f"{self.current_year}-{self.current_month:02d}"
        month_data = self.duty_records.get(key, {})
        req_data = self.request_records.get(key, {})

        self.table1.setRowCount(len(self.staff_list))
        self.table2.setRowCount(len(self.staff_list) + 1)
        self.table2.setColumnCount(days + 2)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(d) for d in range(1, days+1)])
        self.table2.setColumnWidth(0, 30); self.table1.setColumnWidth(0, 30)

        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            wd_idx = calendar.weekday(self.current_year, self.current_month, d)
            it = QTableWidgetItem(weekdays[wd_idx]); it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if wd_idx == 5: it.setForeground(QColor("blue"))
            elif wd_idx == 6: it.setForeground(QColor("red"))
            self.table2.setItem(0, d+1, it)

        for r, s in enumerate(self.staff_list):
            sid, name, role = s; color = self.get_ward_color(sid)
            for c, v in enumerate([sid, name, role]):
                it = QTableWidgetItem(str(v)); it.setBackground(color); self.table1.setItem(r, c, it)
            it0 = QTableWidgetItem(str(sid)); it0.setBackground(color); self.table2.setItem(r+1, 0, it0)
            it1 = QTableWidgetItem(name); it1.setBackground(color); self.table2.setItem(r+1, 1, it1)
            duties = month_data.get(str(sid), [""] * days)
            reqs = req_data.get(str(sid), [False] * days)
            for d in range(days):
                val = duties[d] if d < len(duties) else ""
                it = QTableWidgetItem(val); it.setBackground(color)
                if d < len(reqs) and reqs[d]: it.setForeground(QColor("red"))
                self.table2.setItem(r+1, d+2, it); self.table2.setColumnWidth(d+2, 28)

        self.table1.blockSignals(False); self.table2.blockSignals(False); self.table3.blockSignals(False)
        self.setup_table3_layout(days); self.sync_logic()

    def setup_table3_layout(self, days):
        self.table3.blockSignals(True)
        self.table3.setColumnCount(days * 3 + 1); self.table3.setRowCount(10); self.table3.setColumnWidth(0, 30)
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            c = (d-1)*3 + 1
            self.table3.setSpan(0, c, 1, 3); self.table3.setItem(0, c, QTableWidgetItem(str(d)))
            wd_i = calendar.weekday(self.current_year, self.current_month, d)
            self.table3.setSpan(1, c, 1, 3); it_wd = QTableWidgetItem(weekdays[wd_i])
            if wd_i == 5: it_wd.setForeground(QColor("blue"))
            elif wd_i == 6: it_wd.setForeground(QColor("red"))
            self.table3.setItem(1, c, it_wd)
            for i, s in enumerate(["D", "E", "N"]): self.table3.setItem(2, c+i, QTableWidgetItem(s))
            self.table3.setItem(6, c, QTableWidgetItem("D")); self.table3.setItem(6, c+2, QTableWidgetItem("N"))
            it_gray = QTableWidgetItem(""); it_gray.setBackground(QColor("gray")); self.table3.setItem(6, c+1, it_gray)
            for i in range(3): self.table3.setColumnWidth(c+i, 25)
        titles = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, t in enumerate(titles): 
            self.table3.setItem(i, 0, QTableWidgetItem(t))
            if i in [3,4,5,7,8,9]: self.table3.setRowHeight(i, 80) # 줄 높이 줄임
            else: self.table3.setRowHeight(i, 30)
        # 병동별 색상 적용
        for d in range(1, days*3+1):
            self.table3.item(3, d).setBackground(QColor("#FFF9C4")) # 3W 간호
            self.table3.item(4, d).setBackground(QColor("#FFF176")) # 4W 간호
            self.table3.item(5, d).setBackground(QColor("#FBC02D")) # 5W 간호
            self.table3.item(7, d).setBackground(QColor("#E1F5FE")) # 3W 보호
            self.table3.item(8, d).setBackground(QColor("#81D4FA")) # 4W 보호
            self.table3.item(9, d).setBackground(QColor("#29B6F6")) # 5W 보호
        self.table3.blockSignals(False)

    def sync_logic(self):
        self.table1.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        for r in [3,4,5,7,8,9]:
            for c in range(1, self.table3.columnCount()):
                old_val = self.table3.item(r,c).text() if self.table3.item(r,c) else ""
                if old_val != "X": self.table3.setItem(r, c, QTableWidgetItem(""))
        for r, s in enumerate(self.staff_list):
            sid, name, role = s; stats = {"D":0, "E":0, "N":0, "O":0, "M":0}
            for d in range(days):
                cell = self.table2.item(r+1, d+2)
                if not cell: continue
                duty = cell.text().strip()
                if not duty: continue
                d_type = duty[0].upper()
                if d_type in stats: stats[d_type] += 1
                if d_type == "O": continue 
                is_nurse = "간호사" in role; col_base = d*3 + 1
                t_ward = "3W" if (31 <= sid <= 39) else "4W" if (41 <= sid <= 49) else "5W"
                if "3" in duty: t_ward = "3W"; 
                elif "4" in duty: t_ward = "4W"; 
                elif "5" in duty: t_ward = "5W"
                if "n" in duty: is_nurse = False
                tr = (3 if t_ward=="3W" else 4 if t_ward=="4W" else 5) if is_nurse else (7 if t_ward=="3W" else 8 if t_ward=="4W" else 9)
                tc = col_base + (1 if "E" in duty.upper() else 2 if "N" in duty.upper() else 0)
                if tr != -1:
                    prev = self.table3.item(tr, tc).text() if self.table3.item(tr, tc) else ""
                    if prev == "X": continue
                    it = QTableWidgetItem((prev + "\n" + name).strip())
                    if cell.foreground().color() == QColor("red"): it.setForeground(QColor("red"))
                    self.table3.setItem(tr, tc, it)
        for r, s in enumerate(self.staff_list):
            for i, k in enumerate(["D", "E", "N", "O", "M"]): 
                self.table1.setItem(r, 5+i, QTableWidgetItem(str(stats[k])))
        n_names = [f"{s[0]}{s[1]}" for s in self.staff_list if "간호사" in s[2]]
        a_names = [f"{s[0]}{s[1]}" for s in self.staff_list if "보호사" in s[2]]
        self.footer.setText(f"<b>[간호사]</b> {' | '.join(n_names)}<br><b>[보호사]</b> {' | '.join(a_names)}")
        self.table1.blockSignals(False); self.table3.blockSignals(False)

    def on_table2_click(self, r, c):
        if not self.request_mode or r == 0 or c < 2: return
        it = self.table2.item(r, c)
        if it.foreground().color() == QColor("red"): it.setForeground(QColor("black"))
        else: it.setForeground(QColor("red"))
        self.sync_logic()

    def on_table2_changed(self, it):
        if self.request_mode: it.setForeground(QColor("red"))
        self.sync_logic()

    def run_algo(self):
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        self.table2.blockSignals(True)
        for d in range(1, days + 1):
            col_base = (d-1)*3 + 1
            # 간호사 배정 (3W, 4W, 5W)
            for ward_idx, ward_name in enumerate(["3W", "4W", "5W"]):
                tr = 3 + ward_idx
                for shift_idx, shift_code in enumerate(["D", "E", "N"]):
                    if self.table3.item(tr, col_base + shift_idx).text() == "X": continue
                    if self.table3.item(tr, col_base + shift_idx).text().strip() != "": continue
                    eligible = [s for s in self.staff_list if "간호사" in s[2] and (31+ward_idx*10 <= s[0] <= 35+ward_idx*10)]
                    random.shuffle(eligible)
                    for staff in eligible:
                        r_idx = next(i for i, x in enumerate(self.staff_list) if x[0] == staff[0])
                        if self.table2.item(r_idx+1, d+1).text().strip() == "":
                            self.table2.item(r_idx+1, d+1).setText(shift_code)
                            break
            # 보호사 배정 (3W, 4W)
            for ward_idx, ward_name in enumerate(["3W", "4W"]):
                tr = 7 + ward_idx
                for shift_idx, shift_code in enumerate(["D", "N"]):
                    tc = col_base + (0 if shift_code == "D" else 2)
                    if self.table3.item(tr, tc).text() == "X": continue
                    if self.table3.item(tr, tc).text().strip() != "": continue
                    eligible = [s for s in self.staff_list if "보호사" in s[2] and (36+ward_idx*10 <= s[0] <= 39+ward_idx*10)]
                    random.shuffle(eligible)
                    for staff in eligible:
                        r_idx = next(i for i, x in enumerate(self.staff_list) if x[0] == staff[0])
                        if self.table2.item(r_idx+1, d+1).text().strip() == "":
                            self.table2.item(r_idx+1, d+1).setText(shift_code)
                            break
        self.table2.blockSignals(False); self.sync_logic()

    def show_context_menu(self, pos):
        menu = QMenu(); a1 = menu.addAction("위에 행 추가"); a2 = menu.addAction("아래에 행 추가"); a3 = menu.addAction("행 삭제")
        action = menu.exec(self.table1.mapToGlobal(pos)); row = self.table1.currentRow()
        if action == a1: self.staff_list.insert(row, [0, "신규", "간호사"]); self.refresh_tables()
        elif action == a2: self.staff_list.insert(row+1, [0, "신규", "간호사"]); self.refresh_tables()
        elif action == a3: self.staff_list.pop(row); self.refresh_tables()

    def on_table1_changed(self, it):
        r, c = it.row(), it.column()
        if c < 3:
            val = it.text()
            if c == 0: self.staff_list[r][0] = int(val) if val.isdigit() else 0
            elif c == 1: self.staff_list[r][1] = val
            elif c == 2: self.staff_list[r][2] = val
            self.refresh_tables()

    def save_to_file(self):
        key = f"{self.current_year}-{self.current_month:02d}"
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        cur_d = {}; cur_r = {}
        for r in range(len(self.staff_list)):
            sid = str(self.staff_list[r][0])
            cur_d[sid] = [self.table2.item(r+1, d+2).text() for d in range(days)]
            cur_r[sid] = [self.table2.item(r+1, d+2).foreground().color() == QColor("red") for d in range(days)]
        self.duty_records[key] = cur_d; self.request_records[key] = cur_r
        with open("duty_data.json", "w", encoding="utf-8") as f:
            json.dump({"staff": self.staff_list, "duty": self.duty_records, "req": self.request_records}, f, ensure_ascii=False)
        QMessageBox.information(self, "저장", "성공적으로 저장되었습니다.")

    def load_dialog(self):
        text, ok = QInputDialog.getText(self, "불러오기", "년-월 (예: 2025-12):")
        if ok and text:
            try:
                y, m = map(int, text.split("-")); self.current_year, self.current_month = y, m
                self.refresh_tables()
            except: QMessageBox.warning(self, "에러", "형식이 잘못되었습니다.")

    def go_next(self):
        self.current_month += 1
        if self.current_month > 12: self.current_month = 1; self.current_year += 1
        self.refresh_tables()

    def print_preview(self, table):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.handle_print(p, table))
        preview.exec()

    def handle_print(self, p, table):
        painter = QPainter(p); page = p.pageRect(QPrinter.Unit.DevicePixel)
        tw = sum([table.columnWidth(c) for c in range(table.columnCount())])
        th = sum([table.rowHeight(r) for r in range(table.rowCount())])
        scale = min(page.width() / (tw + 100), (page.height() - 150) / (th + 100), 1.0)
        painter.scale(scale, scale); x, y = 50, 80
        painter.setFont(QFont("Malgun Gothic", 12, QFont.Weight.Bold))
        painter.drawText(x, y-20, f"{self.current_year}년 {self.current_month}월 근무표")
        painter.setFont(QFont("Malgun Gothic", 7))
        for r in range(table.rowCount()):
            curr_x = x; rh = table.rowHeight(r)
            for c in range(table.columnCount()):
                cw = table.columnWidth(c); rect = QRect(curr_x, y, cw, rh)
                it = table.item(r, c)
                if it:
                    painter.fillRect(rect, it.background())
                    painter.drawRect(rect); painter.setPen(it.foreground().color())
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, it.text())
                    painter.setPen(QColor("black"))
                else: painter.drawRect(rect)
                curr_x += cw
            y += rh
        painter.end()

if __name__ == "__main__":
=======
import sys
import calendar
import json
import os
import random
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

# --- [1. 세로쓰기 전용 델리게이트] ---
class VerticalTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 0 or index.row() < 3: 
            return super().paint(painter, option, index)
        
        text = str(index.data() or "")
        if text:
            painter.save()
            # 빨간색 글씨 처리 (Request)
            fg_color = index.data(Qt.ItemDataRole.ForegroundRole)
            if isinstance(fg_color, QColor) and fg_color == QColor("red"):
                painter.setPen(QColor("red"))
            
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            names = text.split('\n')
            rect = option.rect
            total_names = len(names)
            name_width = rect.width() // max(1, total_names)
            
            for i, name in enumerate(names):
                name_rect = QRect(rect.x() + (i * name_width), rect.y(), name_width, rect.height())
                char_y = name_rect.y() + 5
                for char in name:
                    painter.drawText(name_rect.x(), char_y, name_width, 15, 
                                     Qt.AlignmentFlag.AlignCenter, char)
                    char_y += 13
            painter.restore()

# --- [2. 메인 애플리케이션] ---
class DutyAppV94(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나눔과행복병원 근무표 통합 관리기 v9.4")
        self.resize(1650, 950)
        
        self.current_year = 2025
        self.current_month = 12
        self.request_mode = False
        self.staff_list = []
        self.duty_records = {} 
        self.request_records = {} 
        
        self.init_initial_data() 
        self.init_ui()
        self.refresh_tables()

    def init_initial_data(self):
        # 기본 명단 설정
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
        key = "2025-12"
        # 초기 데이터 로드 (v9.3과 동일한 데이터 구조)
        raw_12 = {"31": "D,O,D,D,D,O,O,D,D,N,N,N,O,O,D,D,N,N,N,O,O,D,D,D,O,N,N,O,O,D,D", "32": "E,O,O,E,E,O,N,N,N,O,O,E,O,O,E,E,E,E,E,O,O,E,N,N,O,E,E,N,N,O,O", "33": "O,E,E,O,O,D,D,N4,N4,N4,O,O,D,D,O,E,N4,N4,O,O,D,E,O,O,D,D,D,O,O,N4,N4", "34": "O,D,N,N,O,E,E,E,O,D,D,D,E,O,D,N,N,O,E,N,N,O,O,N,N,O,O,O,E,O,E", "35": "N,N,O,O,N,N,O,O,E,E,E,O,N,N,N,O,O,D,D,D,O,O,E,E,E,O,O,D,D,E,N", "41": "O,D,D,N,N,O,O,D,D,D,D,D,O,O,D,D,D,D,O,O,N,N,N,O,D,N,N,N,O,O,O", "42": "N,O,O,D,D,N,N,O,E,E,O,E,O,N,N,N,O,O,E,E,O,E,E,O,N,N,O,O,D,D,D", "43": "E,E,E,E,O,E,E,O,O,O,E,O,D,D,D,O,O,D,E,O,E,O,D,D,D,O,O,D,E,E,E", "44": "D,N,N,O,O,D,D,E,O,O,O,N,N,N,O,E,E,E,O,N,N,N,O,O,E,E,E,E,E,O,E", "51": "O,O,D,D,N,N,N,O,O,E,E,E,N,N,O,E,E,O,D,D,N,N,O,O,D,D,D,O,O,E,O", "52": "D,D,O,O,E4,E,E,O,E,O,O,O,E4,E4,N,N,O,O,O,D4,D4,D4,O,N,N,N,O,O,N,N,N", "53": "E,O,E,E,E,O,O,E,O,D,D,D,E,O,D,D,D,O,E,E,O,D,D,E,O,O,O,E,E,O,O", "54": "O,E,N,N,O,O,D,D,D,O,N,N,O,E,E,E,O,D,D,N,N,O,O,D,D,O,N,N,O,O,E", "55": "N,N,O,O,O,D,O,N,N,N,O,O,D,D,O,N,N,N,O,E,E,E,O,E,E,O,O,D,D,D,O", "36": "D4,D4,D,O,D4,O,O,N,N,O,O,D,O,O,N,N,O,O,D5,D5,O,D,D5,O,O,D,D,O,N4,N4,N4", "37": "N,N,O,O,D,D5,O,D,D5,O,D5,O,N,N,O,O,D,N,N,N,O,O,O,D,D,N5,N5,N,O,O,O", "38": "D,D,O,O,N,N,N,O,O,D,D,O,O,O,O,O,N,N,O,O,D,O,D,N,N,O,D,N,N,O,O", "39": "O,O,N,N,O,D,D,D,O,N,N,N,O,O,D,D,D,O,D,D,O,N,N,O,O,N,N,O,O,D,N", "46": "O,O,N,N,O,D,D,D,O,N,N,N,O,D,D,O,D,D,D,O,N,N,O,D,N,N,O,O,D,D,D3", "47": "N,N,O,O,N,N,O,O,D,D,D,O,N,N,O,D,N,N,N,O,O,D,D,D,O,D,O,D,D,O,O", "48": "O,O,D,D,O,O,N,N,N,O,O,D,O,O,D,N,O,O,D,D,O,N,N,N,O,O,D,N,N,O,O", "56": "N,N,O,D,D,D,O,O,N,N,N,O,O,D,D,O,D,O,O,D,D,O,N,N,O,O,N,N,N,O,O", "57": "O,O,N,N,N,O,O,D,D,O,D,N,N,N,O,D,D,N,N,O,O,N,N,O,D,O,D,D,O,D,D", "58": "D,D,D,O,O,N,N,N,O,O,O,D,D,O,N,N,N,O,O,N,N,O,O,D,O,D,D,O,O,D,N"}
        self.duty_records[key] = {k: v.split(",") for k, v in raw_12.items()}
        self.request_records[key] = {k: [False]*31 for k in raw_12.keys()}
        self.request_records[key]["31"][1] = True # 예시: 최민애 12/2 빨간색

    def get_ward_color(self, sid):
        if 31 <= sid <= 35: return QColor("#FFF9C4") # 3W 간호
        if 41 <= sid <= 45: return QColor("#FFF176") # 4W 간호
        if 51 <= sid <= 55: return QColor("#FBC02D") # 5W 간호
        if 36 <= sid <= 39: return QColor("#E1F5FE") # 3W 보호
        if 46 <= sid <= 49: return QColor("#81D4FA") # 4W 보호
        if 56 <= sid <= 59: return QColor("#29B6F6") # 5W 보호
        return QColor("white")

    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central); main_lay = QVBoxLayout(central)
        self.tabs = QTabWidget(); main_lay.addWidget(self.tabs)
        
        # --- 테이블 1 ---
        t1_page = QWidget(); t1_lay = QVBoxLayout(t1_page)
        self.title_t1 = QLabel(); self.title_t1.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        t1_lay.addWidget(self.title_t1)
        t1_top = QHBoxLayout()
        self.btn_load = QPushButton("📂 불러오기"); self.btn_load.clicked.connect(self.load_dialog)
        self.btn_save = QPushButton("💾 저장"); self.btn_save.clicked.connect(self.save_to_file)
        self.btn_next1 = QPushButton("다음 달 ▶"); self.btn_next1.clicked.connect(self.go_next)
        t1_top.addStretch(); t1_top.addWidget(self.btn_load); t1_top.addWidget(self.btn_save); t1_top.addWidget(self.btn_next1)
        t1_lay.addLayout(t1_top)
        self.table1 = QTableWidget(); self.table1.setColumnCount(10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "전월막근", "연속일", "D", "E", "N", "O", "M"])
        self.table1.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table1.customContextMenuRequested.connect(self.show_context_menu)
        self.table1.itemChanged.connect(self.on_table1_changed)
        t1_lay.addWidget(self.table1); self.tabs.addTab(t1_page, "테이블 1 (설정)")

        # --- 테이블 2 ---
        t2_page = QWidget(); t2_lay = QVBoxLayout(t2_page)
        self.title_t2 = QLabel(); self.title_t2.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        t2_lay.addWidget(self.title_t2)
        t2_top = QHBoxLayout()
        self.cb_req = QCheckBox("🔴 Request 모드"); self.cb_req.toggled.connect(lambda v: setattr(self, 'request_mode', v))
        self.btn_run = QPushButton("🚀 RUN (자동완성)"); self.btn_run.clicked.connect(self.run_algo)
        self.btn_print2 = QPushButton("🖨️ 인쇄"); self.btn_print2.clicked.connect(lambda: self.print_preview(self.table2))
        self.btn_next2 = QPushButton("다음 달 ▶"); self.btn_next2.clicked.connect(self.go_next)
        t2_top.addWidget(self.cb_req); t2_top.addStretch(); t2_top.addWidget(self.btn_run); t2_top.addWidget(self.btn_print2); t2_top.addWidget(self.btn_next2)
        t2_lay.addLayout(t2_top)
        self.table2 = QTableWidget(); self.table2.cellClicked.connect(self.on_table2_click)
        self.table2.itemChanged.connect(self.on_table2_changed)
        t2_lay.addWidget(self.table2); self.tabs.addTab(t2_page, "테이블 2 (개인별)")

        # --- 테이블 3 ---
        t3_page = QWidget(); t3_lay = QVBoxLayout(t3_page)
        self.title_t3 = QLabel(); self.title_t3.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        t3_lay.addWidget(self.title_t3)
        t3_top = QHBoxLayout()
        self.btn_print3 = QPushButton("🖨️ 인쇄 (A4 가로)"); self.btn_print3.clicked.connect(lambda: self.print_preview(self.table3))
        self.btn_next3 = QPushButton("다음 달 ▶"); self.btn_next3.clicked.connect(self.go_next)
        t3_top.addStretch(); t3_top.addWidget(self.btn_print3); t3_top.addWidget(self.btn_next3)
        t3_lay.addLayout(t3_top)
        self.table3 = QTableWidget(); self.table3.setItemDelegate(VerticalTextDelegate())
        t3_lay.addWidget(self.table3)
        self.footer = QLabel(); self.footer.setFont(QFont("Malgun Gothic", 9))
        t3_lay.addWidget(self.footer); self.tabs.addTab(t3_page, "테이블 3 (배치표)")

    def refresh_tables(self):
        self.table1.blockSignals(True); self.table2.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        date_str = f"📅 {self.current_year}년 {self.current_month}월 근무표"
        self.title_t1.setText(date_str); self.title_t2.setText(date_str); self.title_t3.setText(date_str)
        
        key = f"{self.current_year}-{self.current_month:02d}"
        month_data = self.duty_records.get(key, {})
        req_data = self.request_records.get(key, {})

        self.table1.setRowCount(len(self.staff_list))
        self.table2.setRowCount(len(self.staff_list) + 1)
        self.table2.setColumnCount(days + 2)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(d) for d in range(1, days+1)])
        self.table2.setColumnWidth(0, 30); self.table1.setColumnWidth(0, 30)

        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            wd_idx = calendar.weekday(self.current_year, self.current_month, d)
            it = QTableWidgetItem(weekdays[wd_idx]); it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if wd_idx == 5: it.setForeground(QColor("blue"))
            elif wd_idx == 6: it.setForeground(QColor("red"))
            self.table2.setItem(0, d+1, it)

        for r, s in enumerate(self.staff_list):
            sid, name, role = s; color = self.get_ward_color(sid)
            for c, v in enumerate([sid, name, role]):
                it = QTableWidgetItem(str(v)); it.setBackground(color); self.table1.setItem(r, c, it)
            it0 = QTableWidgetItem(str(sid)); it0.setBackground(color); self.table2.setItem(r+1, 0, it0)
            it1 = QTableWidgetItem(name); it1.setBackground(color); self.table2.setItem(r+1, 1, it1)
            duties = month_data.get(str(sid), [""] * days)
            reqs = req_data.get(str(sid), [False] * days)
            for d in range(days):
                val = duties[d] if d < len(duties) else ""
                it = QTableWidgetItem(val); it.setBackground(color)
                if d < len(reqs) and reqs[d]: it.setForeground(QColor("red"))
                self.table2.setItem(r+1, d+2, it); self.table2.setColumnWidth(d+2, 28)

        self.table1.blockSignals(False); self.table2.blockSignals(False); self.table3.blockSignals(False)
        self.setup_table3_layout(days); self.sync_logic()

    def setup_table3_layout(self, days):
        self.table3.blockSignals(True)
        self.table3.setColumnCount(days * 3 + 1); self.table3.setRowCount(10); self.table3.setColumnWidth(0, 30)
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            c = (d-1)*3 + 1
            self.table3.setSpan(0, c, 1, 3); self.table3.setItem(0, c, QTableWidgetItem(str(d)))
            wd_i = calendar.weekday(self.current_year, self.current_month, d)
            self.table3.setSpan(1, c, 1, 3); it_wd = QTableWidgetItem(weekdays[wd_i])
            if wd_i == 5: it_wd.setForeground(QColor("blue"))
            elif wd_i == 6: it_wd.setForeground(QColor("red"))
            self.table3.setItem(1, c, it_wd)
            for i, s in enumerate(["D", "E", "N"]): self.table3.setItem(2, c+i, QTableWidgetItem(s))
            self.table3.setItem(6, c, QTableWidgetItem("D")); self.table3.setItem(6, c+2, QTableWidgetItem("N"))
            it_gray = QTableWidgetItem(""); it_gray.setBackground(QColor("gray")); self.table3.setItem(6, c+1, it_gray)
            for i in range(3): self.table3.setColumnWidth(c+i, 25)
        titles = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, t in enumerate(titles): 
            self.table3.setItem(i, 0, QTableWidgetItem(t))
            if i in [3,4,5,7,8,9]: self.table3.setRowHeight(i, 80) # 줄 높이 줄임
            else: self.table3.setRowHeight(i, 30)
        # 병동별 색상 적용
        for d in range(1, days*3+1):
            self.table3.item(3, d).setBackground(QColor("#FFF9C4")) # 3W 간호
            self.table3.item(4, d).setBackground(QColor("#FFF176")) # 4W 간호
            self.table3.item(5, d).setBackground(QColor("#FBC02D")) # 5W 간호
            self.table3.item(7, d).setBackground(QColor("#E1F5FE")) # 3W 보호
            self.table3.item(8, d).setBackground(QColor("#81D4FA")) # 4W 보호
            self.table3.item(9, d).setBackground(QColor("#29B6F6")) # 5W 보호
        self.table3.blockSignals(False)

    def sync_logic(self):
        self.table1.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        for r in [3,4,5,7,8,9]:
            for c in range(1, self.table3.columnCount()):
                old_val = self.table3.item(r,c).text() if self.table3.item(r,c) else ""
                if old_val != "X": self.table3.setItem(r, c, QTableWidgetItem(""))
        for r, s in enumerate(self.staff_list):
            sid, name, role = s; stats = {"D":0, "E":0, "N":0, "O":0, "M":0}
            for d in range(days):
                cell = self.table2.item(r+1, d+2)
                if not cell: continue
                duty = cell.text().strip()
                if not duty: continue
                d_type = duty[0].upper()
                if d_type in stats: stats[d_type] += 1
                if d_type == "O": continue 
                is_nurse = "간호사" in role; col_base = d*3 + 1
                t_ward = "3W" if (31 <= sid <= 39) else "4W" if (41 <= sid <= 49) else "5W"
                if "3" in duty: t_ward = "3W"; 
                elif "4" in duty: t_ward = "4W"; 
                elif "5" in duty: t_ward = "5W"
                if "n" in duty: is_nurse = False
                tr = (3 if t_ward=="3W" else 4 if t_ward=="4W" else 5) if is_nurse else (7 if t_ward=="3W" else 8 if t_ward=="4W" else 9)
                tc = col_base + (1 if "E" in duty.upper() else 2 if "N" in duty.upper() else 0)
                if tr != -1:
                    prev = self.table3.item(tr, tc).text() if self.table3.item(tr, tc) else ""
                    if prev == "X": continue
                    it = QTableWidgetItem((prev + "\n" + name).strip())
                    if cell.foreground().color() == QColor("red"): it.setForeground(QColor("red"))
                    self.table3.setItem(tr, tc, it)
        for r, s in enumerate(self.staff_list):
            for i, k in enumerate(["D", "E", "N", "O", "M"]): 
                self.table1.setItem(r, 5+i, QTableWidgetItem(str(stats[k])))
        n_names = [f"{s[0]}{s[1]}" for s in self.staff_list if "간호사" in s[2]]
        a_names = [f"{s[0]}{s[1]}" for s in self.staff_list if "보호사" in s[2]]
        self.footer.setText(f"<b>[간호사]</b> {' | '.join(n_names)}<br><b>[보호사]</b> {' | '.join(a_names)}")
        self.table1.blockSignals(False); self.table3.blockSignals(False)

    def on_table2_click(self, r, c):
        if not self.request_mode or r == 0 or c < 2: return
        it = self.table2.item(r, c)
        if it.foreground().color() == QColor("red"): it.setForeground(QColor("black"))
        else: it.setForeground(QColor("red"))
        self.sync_logic()

    def on_table2_changed(self, it):
        if self.request_mode: it.setForeground(QColor("red"))
        self.sync_logic()

    def run_algo(self):
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        self.table2.blockSignals(True)
        for d in range(1, days + 1):
            col_base = (d-1)*3 + 1
            # 간호사 배정 (3W, 4W, 5W)
            for ward_idx, ward_name in enumerate(["3W", "4W", "5W"]):
                tr = 3 + ward_idx
                for shift_idx, shift_code in enumerate(["D", "E", "N"]):
                    if self.table3.item(tr, col_base + shift_idx).text() == "X": continue
                    if self.table3.item(tr, col_base + shift_idx).text().strip() != "": continue
                    eligible = [s for s in self.staff_list if "간호사" in s[2] and (31+ward_idx*10 <= s[0] <= 35+ward_idx*10)]
                    random.shuffle(eligible)
                    for staff in eligible:
                        r_idx = next(i for i, x in enumerate(self.staff_list) if x[0] == staff[0])
                        if self.table2.item(r_idx+1, d+1).text().strip() == "":
                            self.table2.item(r_idx+1, d+1).setText(shift_code)
                            break
            # 보호사 배정 (3W, 4W)
            for ward_idx, ward_name in enumerate(["3W", "4W"]):
                tr = 7 + ward_idx
                for shift_idx, shift_code in enumerate(["D", "N"]):
                    tc = col_base + (0 if shift_code == "D" else 2)
                    if self.table3.item(tr, tc).text() == "X": continue
                    if self.table3.item(tr, tc).text().strip() != "": continue
                    eligible = [s for s in self.staff_list if "보호사" in s[2] and (36+ward_idx*10 <= s[0] <= 39+ward_idx*10)]
                    random.shuffle(eligible)
                    for staff in eligible:
                        r_idx = next(i for i, x in enumerate(self.staff_list) if x[0] == staff[0])
                        if self.table2.item(r_idx+1, d+1).text().strip() == "":
                            self.table2.item(r_idx+1, d+1).setText(shift_code)
                            break
        self.table2.blockSignals(False); self.sync_logic()

    def show_context_menu(self, pos):
        menu = QMenu(); a1 = menu.addAction("위에 행 추가"); a2 = menu.addAction("아래에 행 추가"); a3 = menu.addAction("행 삭제")
        action = menu.exec(self.table1.mapToGlobal(pos)); row = self.table1.currentRow()
        if action == a1: self.staff_list.insert(row, [0, "신규", "간호사"]); self.refresh_tables()
        elif action == a2: self.staff_list.insert(row+1, [0, "신규", "간호사"]); self.refresh_tables()
        elif action == a3: self.staff_list.pop(row); self.refresh_tables()

    def on_table1_changed(self, it):
        r, c = it.row(), it.column()
        if c < 3:
            val = it.text()
            if c == 0: self.staff_list[r][0] = int(val) if val.isdigit() else 0
            elif c == 1: self.staff_list[r][1] = val
            elif c == 2: self.staff_list[r][2] = val
            self.refresh_tables()

    def save_to_file(self):
        key = f"{self.current_year}-{self.current_month:02d}"
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        cur_d = {}; cur_r = {}
        for r in range(len(self.staff_list)):
            sid = str(self.staff_list[r][0])
            cur_d[sid] = [self.table2.item(r+1, d+2).text() for d in range(days)]
            cur_r[sid] = [self.table2.item(r+1, d+2).foreground().color() == QColor("red") for d in range(days)]
        self.duty_records[key] = cur_d; self.request_records[key] = cur_r
        with open("duty_data.json", "w", encoding="utf-8") as f:
            json.dump({"staff": self.staff_list, "duty": self.duty_records, "req": self.request_records}, f, ensure_ascii=False)
        QMessageBox.information(self, "저장", "성공적으로 저장되었습니다.")

    def load_dialog(self):
        text, ok = QInputDialog.getText(self, "불러오기", "년-월 (예: 2025-12):")
        if ok and text:
            try:
                y, m = map(int, text.split("-")); self.current_year, self.current_month = y, m
                self.refresh_tables()
            except: QMessageBox.warning(self, "에러", "형식이 잘못되었습니다.")

    def go_next(self):
        self.current_month += 1
        if self.current_month > 12: self.current_month = 1; self.current_year += 1
        self.refresh_tables()

    def print_preview(self, table):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.handle_print(p, table))
        preview.exec()

    def handle_print(self, p, table):
        painter = QPainter(p); page = p.pageRect(QPrinter.Unit.DevicePixel)
        tw = sum([table.columnWidth(c) for c in range(table.columnCount())])
        th = sum([table.rowHeight(r) for r in range(table.rowCount())])
        scale = min(page.width() / (tw + 100), (page.height() - 150) / (th + 100), 1.0)
        painter.scale(scale, scale); x, y = 50, 80
        painter.setFont(QFont("Malgun Gothic", 12, QFont.Weight.Bold))
        painter.drawText(x, y-20, f"{self.current_year}년 {self.current_month}월 근무표")
        painter.setFont(QFont("Malgun Gothic", 7))
        for r in range(table.rowCount()):
            curr_x = x; rh = table.rowHeight(r)
            for c in range(table.columnCount()):
                cw = table.columnWidth(c); rect = QRect(curr_x, y, cw, rh)
                it = table.item(r, c)
                if it:
                    painter.fillRect(rect, it.background())
                    painter.drawRect(rect); painter.setPen(it.foreground().color())
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, it.text())
                    painter.setPen(QColor("black"))
                else: painter.drawRect(rect)
                curr_x += cw
            y += rh
        painter.end()

if __name__ == "__main__":
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    app = QApplication(sys.argv); app.setStyle("Fusion"); win = DutyAppV94(); win.show(); sys.exit(app.exec())