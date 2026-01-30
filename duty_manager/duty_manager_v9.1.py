<<<<<<< HEAD
import sys
import calendar
import json
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

class DutyAppV91(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나눔과행복병원 근무표 생성기 v9.1 (복구판)")
        self.resize(1600, 950)
        
        self.current_year = 2025
        self.current_month = 12
        self.request_mode = False
        self.staff_list = []
        self.duty_records = {}
        
        self.init_initial_data() # 2025-12 이미지 분석 데이터 로드
        self.init_ui()
        self.refresh_tables()

    def init_initial_data(self):
        # 1. 기본 명단 설정
        self.staff_list = [
            [31, "최민애", "간호사", "3W"], [32, "김유하", "간호사", "3W"], [33, "김민경", "간호사", "3W"],
            [34, "김다인", "간호사", "3W"], [35, "김다솜", "간호사", "3W"], [41, "이미경", "간호사", "4W"],
            [42, "권수진", "간호사", "4W"], [43, "정지우", "간호사", "4W"], [44, "송선아", "간호사", "4W"],
            [51, "김도연", "간호사", "5W"], [52, "김나은", "간호사", "5W"], [53, "허예리", "간호사", "5W"],
            [54, "박수진", "간호사", "5W"], [55, "김민영", "간호사", "5W"], [36, "전치구", "보호사", "3W"],
            [37, "김재호", "보호사", "3W"], [38, "송재웅", "보호사", "3W"], [39, "지정우", "보호사", "3W"],
            [46, "송현찬", "보호사", "4W"], [47, "김두현", "보호사", "4W"], [48, "하영기", "보호사", "4W"],
            [56, "서현도", "보호사", "5W"], [57, "김두현(주)", "보호사", "5W"], [58, "제상수", "보호사", "5W"]
        ]

        # 2. 이미지 분석 기반 2025년 12월 데이터 (하트=O, 빨간색=[R])
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
        
        formatted_duty = {}
        for k, v in raw_12.items():
            formatted_duty[k] = v.split(",")
        self.duty_records["2025-12"] = formatted_duty

    def get_ward_color(self, sid, role, ward):
        try: sid_int = int(sid)
        except: sid_int = 0
        if "간호사" in role:
            if "3W" in ward or (30 <= sid_int <= 35): return QColor("#FFF9C4")
            if "4W" in ward or (40 <= sid_int <= 45): return QColor("#FFF176")
            if "5W" in ward or (50 <= sid_int <= 55): return QColor("#FBC02D")
        else: # 보호사
            if "3W" in ward or (36 <= sid_int <= 39): return QColor("#E1F5FE")
            if "4W" in ward or (46 <= sid_int <= 49): return QColor("#81D4FA")
            if "5W" in ward or (56 <= sid_int <= 59): return QColor("#29B6F6")
        return QColor("white")

    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        lay = QVBoxLayout(central)

        # Top Bar
        top = QHBoxLayout()
        self.title = QLabel(f"📅 {self.current_year}년 {self.current_month}월")
        self.title.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        
        self.btn_load = QPushButton("📂 불러오기"); self.btn_load.clicked.connect(self.load_dialog)
        self.btn_save = QPushButton("💾 전체 저장"); self.btn_save.clicked.connect(self.save_to_file)
        self.btn_run = QPushButton("🚀 RUN (자동완성)"); self.btn_run.clicked.connect(self.run_algo)
        self.cb_req = QCheckBox("🔴 Request 모드"); self.cb_req.toggled.connect(lambda v: setattr(self, 'request_mode', v))
        
        top.addWidget(self.title); top.addStretch(); top.addWidget(self.cb_req); top.addWidget(self.btn_run); top.addWidget(self.btn_load); top.addWidget(self.btn_save)
        lay.addLayout(top)

        self.tabs = QTabWidget(); lay.addWidget(self.tabs)
        
        # Table 1
        self.table1 = QTableWidget(); self.table1.setColumnCount(10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "병동", "전월막근", "D", "E", "N", "O", "M"])
        self.table1.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table1.customContextMenuRequested.connect(self.show_context_menu)
        self.table1.itemChanged.connect(self.on_table1_changed)
        self.tabs.addTab(self.table1, "1. 인원 설정")

        # Table 2
        self.table2 = QTableWidget()
        self.table2.cellClicked.connect(self.on_table2_click)
        self.table2.itemChanged.connect(self.on_table2_changed)
        t2p = QWidget(); t2l = QVBoxLayout(t2p)
        t2b = QHBoxLayout(); t2pr = QPushButton("🖨️ 인쇄"); t2pr.clicked.connect(lambda: self.print_p(self.table2))
        t2b.addStretch(); t2b.addWidget(t2pr); t2l.addLayout(t2b); t2l.addWidget(self.table2)
        self.tabs.addTab(t2p, "2. 개인별 근무표")

        # Table 3 (복구된 v8 레이아웃)
        self.table3 = QTableWidget()
        t3p = QWidget(); t3l = QVBoxLayout(t3p)
        t3b = QHBoxLayout(); t3pr = QPushButton("🖨️ 인쇄 (A4 가로)"); t3pr.clicked.connect(lambda: self.print_p(self.table3))
        t3b.addStretch(); t3b.addWidget(t3pr); t3l.addLayout(t3b); t3l.addWidget(self.table3)
        self.footer = QLabel(); t3l.addWidget(self.footer)
        self.tabs.addTab(t3p, "3. 병동별 배치표")

    def refresh_tables(self):
        self.table1.blockSignals(True); self.table2.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        key = f"{self.current_year}-{self.current_month:02d}"
        month_data = self.duty_records.get(key, {})

        # Table 1 & 2
        self.table1.setRowCount(len(self.staff_list))
        self.table2.setRowCount(len(self.staff_list))
        self.table2.setColumnCount(days + 2)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(d) for d in range(1, days+1)])
        self.table2.setColumnWidth(0, 35)

        for r, s in enumerate(self.staff_list):
            sid, name, role, ward = s
            color = self.get_ward_color(sid, role, ward)
            
            # T1
            for c, v in enumerate([sid, name, role, ward]):
                it = QTableWidgetItem(str(v)); it.setBackground(color); self.table1.setItem(r, c, it)
            
            # T2
            it0 = QTableWidgetItem(str(sid)); it0.setBackground(color); self.table2.setItem(r, 0, it0)
            it1 = QTableWidgetItem(name); it1.setBackground(color); self.table2.setItem(r, 1, it1)
            
            duties = month_data.get(str(sid), [""] * days)
            for d in range(days):
                val = duties[d] if d < len(duties) else ""
                it = QTableWidgetItem(val)
                if "[R]" in val: it.setForeground(QColor("red"))
                
                wd = calendar.weekday(self.current_year, self.current_month, d+1)
                if wd == 5: it.setBackground(QColor("#E8EAF6")) # 토
                elif wd == 6: it.setBackground(QColor("#FFEBEE")) # 일
                else: it.setBackground(color)
                
                self.table2.setItem(r, d+2, it); self.table2.setColumnWidth(d+2, 28)

        self.table1.blockSignals(False); self.table2.blockSignals(False); self.table3.blockSignals(False)
        self.setup_table3_v8(days)
        self.sync_logic()

    def setup_table3_v8(self, days):
        """v8 스크린샷 구조 재현 (3열 1일)"""
        self.table3.blockSignals(True)
        self.table3.setColumnCount(days * 3 + 1)
        self.table3.setRowCount(10)
        self.table3.setColumnWidth(0, 70)
        
        # 날짜/요일 행
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            c = (d-1)*3 + 1
            self.table3.setSpan(0, c, 1, 3); self.table3.setItem(0, c, QTableWidgetItem(str(d)))
            self.table3.item(0, c).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            wd_i = calendar.weekday(self.current_year, self.current_month, d)
            self.table3.setSpan(1, c, 1, 3); it_wd = QTableWidgetItem(weekdays[wd_i])
            it_wd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if wd_i == 5: it_wd.setForeground(QColor("blue"))
            elif wd_i == 6: it_wd.setForeground(QColor("red"))
            self.table3.setItem(1, c, it_wd)

            # 간호사 D/E/N 구분선
            self.table3.setItem(2, c, QTableWidgetItem("D")); self.table3.setItem(2, c+1, QTableWidgetItem("E")); self.table3.setItem(2, c+2, QTableWidgetItem("N"))
            # 보호사 D/N 구분선 (E칸 회색)
            self.table3.setItem(6, c, QTableWidgetItem("D")); self.table3.setItem(6, c+2, QTableWidgetItem("N"))
            it_gray = QTableWidgetItem(""); it_gray.setBackground(QColor("gray")); self.table3.setItem(6, c+1, it_gray)
            
            for i in range(3): self.table3.setColumnWidth(c+i, 25)

        titles = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, t in enumerate(titles):
            self.table3.setItem(i, 0, QTableWidgetItem(t))
            if i in [3,4,5,7,8,9]: self.table3.setRowHeight(i, 110)
            else: self.table3.setRowHeight(i, 30)
        self.table3.blockSignals(False)

    def sync_logic(self):
        self.table1.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        
        # T3 내용 청소
        for r in [3,4,5,7,8,9]:
            for c in range(1, self.table3.columnCount()):
                if r >= 7 and (c-1)%3 == 1: continue 
                self.table3.setItem(r, c, QTableWidgetItem(""))

        for r, s in enumerate(self.staff_list):
            sid, name, role, ward = s
            cnt = {"D":0, "E":0, "N":0, "O":0, "M":0}
            for d in range(days):
                duty = self.table2.item(r, d+2).text().replace("[R]", "").strip()
                if not duty: continue
                
                # 통계 계산
                d_type = duty[0].upper()
                if d_type in cnt: cnt[d_type] += 1

                # 배치표 맵핑
                col_base = d*3 + 1
                tr, tc = -1, -1
                is_nurse = "간호사" in role
                t_ward = ward
                if "3" in duty: t_ward = "3W"
                elif "4" in duty: t_ward = "4W"
                elif "5" in duty: t_ward = "5W"
                if "n" in duty: is_nurse = False

                if is_nurse:
                    tr = 3 if "3W" in t_ward else 4 if "4W" in t_ward else 5
                    tc = col_base + (1 if "E" in duty.upper() else 2 if "N" in duty.upper() else 0)
                else:
                    tr = 7 if "3W" in t_ward else 8 if "4W" in t_ward else 9
                    tc = col_base + (2 if "N" in duty.upper() else 0)
                
                if tr != -1:
                    prev = self.table3.item(tr, tc).text() if self.table3.item(tr, tc) else ""
                    self.table3.setItem(tr, tc, QTableWidgetItem((prev + "\n" + name).strip()))

            for i, k in enumerate(["D", "E", "N", "O", "M"]):
                self.table1.setItem(r, 5+i, QTableWidgetItem(str(cnt[k])))

        # Footer
        n_names = [s[1] for s in self.staff_list if "간호사" in s[2]]
        a_names = [s[1] for s in self.staff_list if "보호사" in s[2]]
        self.footer.setText(f"<b>[간호사]</b> {', '.join(n_names)}  |  <b>[보호사]</b> {', '.join(a_names)}")
        self.table1.blockSignals(False); self.table3.blockSignals(False)

    def on_table2_click(self, r, c):
        if not self.request_mode or c < 2: return
        it = self.table2.item(r, c)
        if "[R]" in it.text(): it.setText(it.text().replace("[R]", "")); it.setForeground(QColor("black"))
        else: it.setText(f"[R]{it.text()}"); it.setForeground(QColor("red"))

    def show_context_menu(self, pos):
        menu = QMenu(); a1 = menu.addAction("위에 행 추가"); a2 = menu.addAction("아래에 행 추가"); a3 = menu.addAction("행 삭제")
        action = menu.exec(self.table1.mapToGlobal(pos)); row = self.table1.currentRow()
        if action == a1: self.staff_list.insert(row, [0, "신규", "간호사", "3W"]); self.refresh_tables()
        elif action == a2: self.staff_list.insert(row+1, [0, "신규", "간호사", "3W"]); self.refresh_tables()
        elif action == a3: self.staff_list.pop(row); self.refresh_tables()

    def on_table1_changed(self, it):
        r, c = it.row(), it.column()
        if c < 4:
            self.staff_list[r][c] = it.text() if c != 0 else int(it.text() if it.text().isdigit() else 0)
            self.refresh_tables()

    def on_table2_changed(self, it): self.sync_logic()

    def save_to_file(self):
        key = f"{self.current_year}-{self.current_month:02d}"
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        cur_m_data = {}
        for r in range(len(self.staff_list)):
            sid = str(self.staff_list[r][0])
            cur_m_data[sid] = [self.table2.item(r, d+2).text() for d in range(days)]
        self.duty_records[key] = cur_m_data
        with open("duty_data.json", "w", encoding="utf-8") as f:
            json.dump({"staff_list": self.staff_list, "duty_records": self.duty_records}, f, ensure_ascii=False, indent=4)
        QMessageBox.information(self, "저장", "성공적으로 저장되었습니다.")

    def load_dialog(self):
        text, ok = QInputDialog.getText(self, "불러오기", "년-월 (예: 2025-12):")
        if ok and text:
            try:
                y, m = map(int, text.split("-")); self.current_year, self.current_month = y, m
                self.title.setText(f"📅 {y}년 {m}월"); self.refresh_tables()
            except: QMessageBox.warning(self, "에러", "형식이 잘못되었습니다.")

    def run_algo(self):
        import random
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        self.table2.blockSignals(True)
        for r in range(len(self.staff_list)):
            role = self.staff_list[r][2]; opts = ["D", "E", "N", "O"] if "간호사" in role else ["D", "N", "O"]
            for d in range(days):
                if not self.table2.item(r, d+2).text(): self.table2.item(r, d+2).setText(random.choice(opts))
        self.table2.blockSignals(False); self.sync_logic()

    def print_p(self, table):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.handle_print(p, table))
        preview.exec()

    def handle_print(self, p, table):
        painter = QPainter(p); page = p.pageRect(QPrinter.Unit.DevicePixel)
        tw = sum([table.columnWidth(c) for c in range(table.columnCount())])
        th = sum([table.rowHeight(r) for r in range(table.rowCount())])
        scale = min(page.width() / (tw + 100), (page.height() - 100) / (th + 100), 1.0)
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
                    painter.drawRect(rect); painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, it.text())
                else: painter.drawRect(rect)
                curr_x += cw
            y += rh
        if table == self.table3: painter.drawText(x, y + 30, self.footer.text().replace("<b>","").replace("</b>",""))
        painter.end()

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

class DutyAppV91(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나눔과행복병원 근무표 생성기 v9.1 (복구판)")
        self.resize(1600, 950)
        
        self.current_year = 2025
        self.current_month = 12
        self.request_mode = False
        self.staff_list = []
        self.duty_records = {}
        
        self.init_initial_data() # 2025-12 이미지 분석 데이터 로드
        self.init_ui()
        self.refresh_tables()

    def init_initial_data(self):
        # 1. 기본 명단 설정
        self.staff_list = [
            [31, "최민애", "간호사", "3W"], [32, "김유하", "간호사", "3W"], [33, "김민경", "간호사", "3W"],
            [34, "김다인", "간호사", "3W"], [35, "김다솜", "간호사", "3W"], [41, "이미경", "간호사", "4W"],
            [42, "권수진", "간호사", "4W"], [43, "정지우", "간호사", "4W"], [44, "송선아", "간호사", "4W"],
            [51, "김도연", "간호사", "5W"], [52, "김나은", "간호사", "5W"], [53, "허예리", "간호사", "5W"],
            [54, "박수진", "간호사", "5W"], [55, "김민영", "간호사", "5W"], [36, "전치구", "보호사", "3W"],
            [37, "김재호", "보호사", "3W"], [38, "송재웅", "보호사", "3W"], [39, "지정우", "보호사", "3W"],
            [46, "송현찬", "보호사", "4W"], [47, "김두현", "보호사", "4W"], [48, "하영기", "보호사", "4W"],
            [56, "서현도", "보호사", "5W"], [57, "김두현(주)", "보호사", "5W"], [58, "제상수", "보호사", "5W"]
        ]

        # 2. 이미지 분석 기반 2025년 12월 데이터 (하트=O, 빨간색=[R])
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
        
        formatted_duty = {}
        for k, v in raw_12.items():
            formatted_duty[k] = v.split(",")
        self.duty_records["2025-12"] = formatted_duty

    def get_ward_color(self, sid, role, ward):
        try: sid_int = int(sid)
        except: sid_int = 0
        if "간호사" in role:
            if "3W" in ward or (30 <= sid_int <= 35): return QColor("#FFF9C4")
            if "4W" in ward or (40 <= sid_int <= 45): return QColor("#FFF176")
            if "5W" in ward or (50 <= sid_int <= 55): return QColor("#FBC02D")
        else: # 보호사
            if "3W" in ward or (36 <= sid_int <= 39): return QColor("#E1F5FE")
            if "4W" in ward or (46 <= sid_int <= 49): return QColor("#81D4FA")
            if "5W" in ward or (56 <= sid_int <= 59): return QColor("#29B6F6")
        return QColor("white")

    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        lay = QVBoxLayout(central)

        # Top Bar
        top = QHBoxLayout()
        self.title = QLabel(f"📅 {self.current_year}년 {self.current_month}월")
        self.title.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        
        self.btn_load = QPushButton("📂 불러오기"); self.btn_load.clicked.connect(self.load_dialog)
        self.btn_save = QPushButton("💾 전체 저장"); self.btn_save.clicked.connect(self.save_to_file)
        self.btn_run = QPushButton("🚀 RUN (자동완성)"); self.btn_run.clicked.connect(self.run_algo)
        self.cb_req = QCheckBox("🔴 Request 모드"); self.cb_req.toggled.connect(lambda v: setattr(self, 'request_mode', v))
        
        top.addWidget(self.title); top.addStretch(); top.addWidget(self.cb_req); top.addWidget(self.btn_run); top.addWidget(self.btn_load); top.addWidget(self.btn_save)
        lay.addLayout(top)

        self.tabs = QTabWidget(); lay.addWidget(self.tabs)
        
        # Table 1
        self.table1 = QTableWidget(); self.table1.setColumnCount(10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "병동", "전월막근", "D", "E", "N", "O", "M"])
        self.table1.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table1.customContextMenuRequested.connect(self.show_context_menu)
        self.table1.itemChanged.connect(self.on_table1_changed)
        self.tabs.addTab(self.table1, "1. 인원 설정")

        # Table 2
        self.table2 = QTableWidget()
        self.table2.cellClicked.connect(self.on_table2_click)
        self.table2.itemChanged.connect(self.on_table2_changed)
        t2p = QWidget(); t2l = QVBoxLayout(t2p)
        t2b = QHBoxLayout(); t2pr = QPushButton("🖨️ 인쇄"); t2pr.clicked.connect(lambda: self.print_p(self.table2))
        t2b.addStretch(); t2b.addWidget(t2pr); t2l.addLayout(t2b); t2l.addWidget(self.table2)
        self.tabs.addTab(t2p, "2. 개인별 근무표")

        # Table 3 (복구된 v8 레이아웃)
        self.table3 = QTableWidget()
        t3p = QWidget(); t3l = QVBoxLayout(t3p)
        t3b = QHBoxLayout(); t3pr = QPushButton("🖨️ 인쇄 (A4 가로)"); t3pr.clicked.connect(lambda: self.print_p(self.table3))
        t3b.addStretch(); t3b.addWidget(t3pr); t3l.addLayout(t3b); t3l.addWidget(self.table3)
        self.footer = QLabel(); t3l.addWidget(self.footer)
        self.tabs.addTab(t3p, "3. 병동별 배치표")

    def refresh_tables(self):
        self.table1.blockSignals(True); self.table2.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        key = f"{self.current_year}-{self.current_month:02d}"
        month_data = self.duty_records.get(key, {})

        # Table 1 & 2
        self.table1.setRowCount(len(self.staff_list))
        self.table2.setRowCount(len(self.staff_list))
        self.table2.setColumnCount(days + 2)
        self.table2.setHorizontalHeaderLabels(["번호", "성함"] + [str(d) for d in range(1, days+1)])
        self.table2.setColumnWidth(0, 35)

        for r, s in enumerate(self.staff_list):
            sid, name, role, ward = s
            color = self.get_ward_color(sid, role, ward)
            
            # T1
            for c, v in enumerate([sid, name, role, ward]):
                it = QTableWidgetItem(str(v)); it.setBackground(color); self.table1.setItem(r, c, it)
            
            # T2
            it0 = QTableWidgetItem(str(sid)); it0.setBackground(color); self.table2.setItem(r, 0, it0)
            it1 = QTableWidgetItem(name); it1.setBackground(color); self.table2.setItem(r, 1, it1)
            
            duties = month_data.get(str(sid), [""] * days)
            for d in range(days):
                val = duties[d] if d < len(duties) else ""
                it = QTableWidgetItem(val)
                if "[R]" in val: it.setForeground(QColor("red"))
                
                wd = calendar.weekday(self.current_year, self.current_month, d+1)
                if wd == 5: it.setBackground(QColor("#E8EAF6")) # 토
                elif wd == 6: it.setBackground(QColor("#FFEBEE")) # 일
                else: it.setBackground(color)
                
                self.table2.setItem(r, d+2, it); self.table2.setColumnWidth(d+2, 28)

        self.table1.blockSignals(False); self.table2.blockSignals(False); self.table3.blockSignals(False)
        self.setup_table3_v8(days)
        self.sync_logic()

    def setup_table3_v8(self, days):
        """v8 스크린샷 구조 재현 (3열 1일)"""
        self.table3.blockSignals(True)
        self.table3.setColumnCount(days * 3 + 1)
        self.table3.setRowCount(10)
        self.table3.setColumnWidth(0, 70)
        
        # 날짜/요일 행
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            c = (d-1)*3 + 1
            self.table3.setSpan(0, c, 1, 3); self.table3.setItem(0, c, QTableWidgetItem(str(d)))
            self.table3.item(0, c).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            wd_i = calendar.weekday(self.current_year, self.current_month, d)
            self.table3.setSpan(1, c, 1, 3); it_wd = QTableWidgetItem(weekdays[wd_i])
            it_wd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if wd_i == 5: it_wd.setForeground(QColor("blue"))
            elif wd_i == 6: it_wd.setForeground(QColor("red"))
            self.table3.setItem(1, c, it_wd)

            # 간호사 D/E/N 구분선
            self.table3.setItem(2, c, QTableWidgetItem("D")); self.table3.setItem(2, c+1, QTableWidgetItem("E")); self.table3.setItem(2, c+2, QTableWidgetItem("N"))
            # 보호사 D/N 구분선 (E칸 회색)
            self.table3.setItem(6, c, QTableWidgetItem("D")); self.table3.setItem(6, c+2, QTableWidgetItem("N"))
            it_gray = QTableWidgetItem(""); it_gray.setBackground(QColor("gray")); self.table3.setItem(6, c+1, it_gray)
            
            for i in range(3): self.table3.setColumnWidth(c+i, 25)

        titles = ["날짜", "요일", "간호사", "3W", "4W", "5W", "보호사", "3W", "4W", "5W"]
        for i, t in enumerate(titles):
            self.table3.setItem(i, 0, QTableWidgetItem(t))
            if i in [3,4,5,7,8,9]: self.table3.setRowHeight(i, 110)
            else: self.table3.setRowHeight(i, 30)
        self.table3.blockSignals(False)

    def sync_logic(self):
        self.table1.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        
        # T3 내용 청소
        for r in [3,4,5,7,8,9]:
            for c in range(1, self.table3.columnCount()):
                if r >= 7 and (c-1)%3 == 1: continue 
                self.table3.setItem(r, c, QTableWidgetItem(""))

        for r, s in enumerate(self.staff_list):
            sid, name, role, ward = s
            cnt = {"D":0, "E":0, "N":0, "O":0, "M":0}
            for d in range(days):
                duty = self.table2.item(r, d+2).text().replace("[R]", "").strip()
                if not duty: continue
                
                # 통계 계산
                d_type = duty[0].upper()
                if d_type in cnt: cnt[d_type] += 1

                # 배치표 맵핑
                col_base = d*3 + 1
                tr, tc = -1, -1
                is_nurse = "간호사" in role
                t_ward = ward
                if "3" in duty: t_ward = "3W"
                elif "4" in duty: t_ward = "4W"
                elif "5" in duty: t_ward = "5W"
                if "n" in duty: is_nurse = False

                if is_nurse:
                    tr = 3 if "3W" in t_ward else 4 if "4W" in t_ward else 5
                    tc = col_base + (1 if "E" in duty.upper() else 2 if "N" in duty.upper() else 0)
                else:
                    tr = 7 if "3W" in t_ward else 8 if "4W" in t_ward else 9
                    tc = col_base + (2 if "N" in duty.upper() else 0)
                
                if tr != -1:
                    prev = self.table3.item(tr, tc).text() if self.table3.item(tr, tc) else ""
                    self.table3.setItem(tr, tc, QTableWidgetItem((prev + "\n" + name).strip()))

            for i, k in enumerate(["D", "E", "N", "O", "M"]):
                self.table1.setItem(r, 5+i, QTableWidgetItem(str(cnt[k])))

        # Footer
        n_names = [s[1] for s in self.staff_list if "간호사" in s[2]]
        a_names = [s[1] for s in self.staff_list if "보호사" in s[2]]
        self.footer.setText(f"<b>[간호사]</b> {', '.join(n_names)}  |  <b>[보호사]</b> {', '.join(a_names)}")
        self.table1.blockSignals(False); self.table3.blockSignals(False)

    def on_table2_click(self, r, c):
        if not self.request_mode or c < 2: return
        it = self.table2.item(r, c)
        if "[R]" in it.text(): it.setText(it.text().replace("[R]", "")); it.setForeground(QColor("black"))
        else: it.setText(f"[R]{it.text()}"); it.setForeground(QColor("red"))

    def show_context_menu(self, pos):
        menu = QMenu(); a1 = menu.addAction("위에 행 추가"); a2 = menu.addAction("아래에 행 추가"); a3 = menu.addAction("행 삭제")
        action = menu.exec(self.table1.mapToGlobal(pos)); row = self.table1.currentRow()
        if action == a1: self.staff_list.insert(row, [0, "신규", "간호사", "3W"]); self.refresh_tables()
        elif action == a2: self.staff_list.insert(row+1, [0, "신규", "간호사", "3W"]); self.refresh_tables()
        elif action == a3: self.staff_list.pop(row); self.refresh_tables()

    def on_table1_changed(self, it):
        r, c = it.row(), it.column()
        if c < 4:
            self.staff_list[r][c] = it.text() if c != 0 else int(it.text() if it.text().isdigit() else 0)
            self.refresh_tables()

    def on_table2_changed(self, it): self.sync_logic()

    def save_to_file(self):
        key = f"{self.current_year}-{self.current_month:02d}"
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        cur_m_data = {}
        for r in range(len(self.staff_list)):
            sid = str(self.staff_list[r][0])
            cur_m_data[sid] = [self.table2.item(r, d+2).text() for d in range(days)]
        self.duty_records[key] = cur_m_data
        with open("duty_data.json", "w", encoding="utf-8") as f:
            json.dump({"staff_list": self.staff_list, "duty_records": self.duty_records}, f, ensure_ascii=False, indent=4)
        QMessageBox.information(self, "저장", "성공적으로 저장되었습니다.")

    def load_dialog(self):
        text, ok = QInputDialog.getText(self, "불러오기", "년-월 (예: 2025-12):")
        if ok and text:
            try:
                y, m = map(int, text.split("-")); self.current_year, self.current_month = y, m
                self.title.setText(f"📅 {y}년 {m}월"); self.refresh_tables()
            except: QMessageBox.warning(self, "에러", "형식이 잘못되었습니다.")

    def run_algo(self):
        import random
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        self.table2.blockSignals(True)
        for r in range(len(self.staff_list)):
            role = self.staff_list[r][2]; opts = ["D", "E", "N", "O"] if "간호사" in role else ["D", "N", "O"]
            for d in range(days):
                if not self.table2.item(r, d+2).text(): self.table2.item(r, d+2).setText(random.choice(opts))
        self.table2.blockSignals(False); self.sync_logic()

    def print_p(self, table):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.handle_print(p, table))
        preview.exec()

    def handle_print(self, p, table):
        painter = QPainter(p); page = p.pageRect(QPrinter.Unit.DevicePixel)
        tw = sum([table.columnWidth(c) for c in range(table.columnCount())])
        th = sum([table.rowHeight(r) for r in range(table.rowCount())])
        scale = min(page.width() / (tw + 100), (page.height() - 100) / (th + 100), 1.0)
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
                    painter.drawRect(rect); painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, it.text())
                else: painter.drawRect(rect)
                curr_x += cw
            y += rh
        if table == self.table3: painter.drawText(x, y + 30, self.footer.text().replace("<b>","").replace("</b>",""))
        painter.end()

if __name__ == "__main__":
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    app = QApplication(sys.argv); app.setStyle("Fusion"); win = DutyAppV91(); win.show(); sys.exit(app.exec())