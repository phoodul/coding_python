<<<<<<< HEAD
import sys
import calendar
import json
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

class DutyAppV9(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나눔과행복병원 근무표 생성기 v9.0")
        self.resize(1600, 900)
        
        # 데이터 초기화
        self.current_year = 2025
        self.current_month = 12
        self.request_mode = False
        self.staff_list = []  # [[번호, 이름, 직종, 병동], ...]
        self.duty_records = {} # {"YYYY-MM": { "SID": [근무리스트] }}
        
        # 초기 명단 설정 (v8.0 기준)
        self.init_staff_data()
        
        self.init_ui()
        self.load_from_file() # 파일에서 기존 데이터 로드
        self.refresh_tables()

    def init_staff_data(self):
        # 기본 명단 셋업
        initial_data = [
            (31, "최민애", "간호사", "3W"), (32, "김유하", "간호사", "3W"), (33, "김민경", "간호사", "3W"),
            (34, "김다인", "간호사", "3W"), (35, "김다솜", "간호사", "3W"), (36, "전치구", "보호사", "3W"),
            (37, "김재호", "보호사", "3W"), (38, "송재웅", "보호사", "3W"), (39, "지정우", "보호사", "3W"),
            (41, "이미경", "간호사", "4W"), (42, "권수진", "간호사", "4W"), (43, "정지우", "간호사", "4W"),
            (44, "송선아", "간호사", "4W"), (46, "송현찬", "보호사", "4W"), (47, "김두현", "보호사", "4W"),
            (48, "하영기", "보호사", "4W"), (51, "김도연", "간호사", "5W"), (52, "김나은", "간호사", "5W"),
            (53, "허예리", "간호사", "5W"), (54, "박수진", "간호사", "5W"), (55, "김민영", "간호사", "5W"),
            (56, "서현도", "보호사", "5W"), (57, "김두현(주)", "보호사", "5W"), (58, "제상수", "보호사", "5W")
        ]
        for d in initial_data:
            self.staff_list.append(list(d))

    def get_ward_color(self, sid, role, ward):
        # 병동 및 직종별 색상 지정
        try:
            sid_int = int(sid)
        except: sid_int = 0

        if "간호사" in role:
            if "3W" in ward or (30 <= sid_int <= 35): return QColor("#FFF9C4") # 연노랑
            if "4W" in ward or (40 <= sid_int <= 45): return QColor("#FFF176") # 중간노랑
            if "5W" in ward or (50 <= sid_int <= 55): return QColor("#FBC02D") # 진노랑
        else: # 보호사
            if "3W" in ward or (36 <= sid_int <= 39): return QColor("#E1F5FE") # 연하늘
            if "4W" in ward or (46 <= sid_int <= 49): return QColor("#81D4FA") # 중간하늘
            if "5W" in ward or (56 <= sid_int <= 59): return QColor("#29B6F6") # 진하늘
        return QColor("white")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 상단 컨트롤바
        top_bar = QHBoxLayout()
        self.label_title = QLabel(f"📅 {self.current_year}년 {self.current_month}월 근무표")
        self.label_title.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        
        self.btn_load = QPushButton("📂 불러오기"); self.btn_load.clicked.connect(self.load_dialog)
        self.btn_save = QPushButton("💾 전체 저장"); self.btn_save.clicked.connect(self.save_to_file)
        self.btn_run = QPushButton("🚀 RUN (자동완성)"); self.btn_run.clicked.connect(self.run_algo)
        self.cb_request = QCheckBox("🔴 Request 모드"); self.cb_request.toggled.connect(self.set_request_mode)
        
        top_bar.addWidget(self.label_title)
        top_bar.addStretch()
        top_bar.addWidget(self.cb_request)
        top_bar.addWidget(self.btn_run)
        top_bar.addWidget(self.btn_load)
        top_bar.addWidget(self.btn_save)
        main_layout.addLayout(top_bar)

        # 탭 구성
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # 테이블 1: 명단 및 설정
        self.table1 = QTableWidget()
        self.table1.setColumnCount(10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "병동", "전월막근", "D", "E", "N", "O", "M"])
        self.table1.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table1.customContextMenuRequested.connect(self.show_context_menu)
        self.table1.itemChanged.connect(self.on_table1_item_changed)
        self.tabs.addTab(self.table1, "1. 인원 관리 (우클릭: 행추가)")

        # 테이블 2: 개인 근무표
        self.table2 = QTableWidget()
        self.table2.cellClicked.connect(self.on_table2_cell_clicked)
        self.table2.itemChanged.connect(self.on_table2_item_changed)
        
        t2_page = QWidget(); t2_lay = QVBoxLayout(t2_page)
        t2_btn_lay = QHBoxLayout()
        t2_btn_print = QPushButton("🖨️ 개인 근무표 인쇄"); t2_btn_print.clicked.connect(lambda: self.print_preview(self.table2))
        t2_btn_lay.addStretch(); t2_btn_lay.addWidget(t2_btn_print)
        t2_lay.addLayout(t2_btn_lay); t2_lay.addWidget(self.table2)
        self.tabs.addTab(t2_page, "2. 근무 입력")

        # 테이블 3: 병동 배치표
        self.table3 = QTableWidget()
        from PyQt6.QtWidgets import QStyledItemDelegate
        # 세로쓰기 Delegate는 생략(표준 텍스트로 가독성 확보)
        
        t3_page = QWidget(); t3_lay = QVBoxLayout(t3_page)
        t3_btn_lay = QHBoxLayout()
        t3_btn_print = QPushButton("🖨️ 병동 배치표 인쇄"); t3_btn_print.clicked.connect(lambda: self.print_preview(self.table3))
        t3_btn_lay.addStretch(); t3_btn_lay.addWidget(t3_btn_print)
        t3_lay.addLayout(t3_btn_lay); t3_lay.addWidget(self.table3)
        self.footer_label = QLabel()
        t3_lay.addWidget(self.footer_label)
        self.tabs.addTab(t3_page, "3. 병동별 배치표")

    def refresh_tables(self):
        """명단 기반으로 모든 테이블 다시 그리기"""
        self.table1.blockSignals(True); self.table2.blockSignals(True); self.table3.blockSignals(True)
        
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        key = f"{self.current_year}-{self.current_month:02d}"
        month_data = self.duty_records.get(key, {})

        # Table 1 & 2 행수 설정
        self.table1.setRowCount(len(self.staff_list))
        self.table2.setRowCount(len(self.staff_list))
        self.table2.setColumnCount(days + 2)
        
        # Table 2 헤더
        headers = ["번호", "이름"] + [str(d) for d in range(1, days+1)]
        self.table2.setHorizontalHeaderLabels(headers)
        self.table2.setColumnWidth(0, 40) # 번호열 축소

        for r, staff in enumerate(self.staff_list):
            sid, name, role, ward = staff
            color = self.get_ward_color(sid, role, ward)

            # Table 1 채우기
            for c, val in enumerate([sid, name, role, ward]):
                item = QTableWidgetItem(str(val))
                item.setBackground(color)
                self.table1.setItem(r, c, item)

            # Table 2 채우기
            self.table2.setItem(r, 0, QTableWidgetItem(str(sid)))
            self.table2.setItem(r, 1, QTableWidgetItem(name))
            self.table2.item(r,0).setBackground(color); self.table2.item(r,1).setBackground(color)
            
            duties = month_data.get(str(sid), [""] * days)
            for d in range(days):
                duty_val = duties[d] if d < len(duties) else ""
                item = QTableWidgetItem(duty_val)
                if "[R]" in duty_val: item.setForeground(QColor("red"))
                
                # 주말 배경색
                wd = calendar.weekday(self.current_year, self.current_month, d+1)
                if wd == 5: item.setBackground(QColor("#E3F2FD")) # 토
                elif wd == 6: item.setBackground(QColor("#FFEBEE")) # 일
                else: item.setBackground(color)
                
                self.table2.setItem(r, d+2, item)
                self.table2.setColumnWidth(d+2, 30)

        self.table1.blockSignals(False); self.table2.blockSignals(False); self.table3.blockSignals(False)
        self.setup_table3_layout()
        self.sync_logic()

    def setup_table3_layout(self):
        """배치표 레이아웃 설정"""
        self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        self.table3.setColumnCount(days + 1)
        self.table3.setRowCount(9) # 날짜, 요일, 3W간호, 4W간호, 5W간호, 3W보호, 4W보호, 5W보호, 구분
        
        headers = ["병동"] + [str(d) for d in range(1, days+1)]
        self.table3.setHorizontalHeaderLabels(headers)
        
        row_titles = ["날짜", "요일", "3W 간호", "4W 간호", "5W 간호", "3W 보호", "4W 보호", "5W 보호"]
        for i, title in enumerate(row_titles):
            self.table3.setItem(i, 0, QTableWidgetItem(title))
            if i >= 2: self.table3.setRowHeight(i, 100)

        # 요일 채우기
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            wd_idx = calendar.weekday(self.current_year, self.current_month, d)
            item = QTableWidgetItem(weekdays[wd_idx])
            if wd_idx == 5: item.setForeground(QColor("blue"))
            if wd_idx == 6: item.setForeground(QColor("red"))
            self.table3.setItem(1, d, item)
            self.table3.setColumnWidth(d, 45)

        self.table3.blockSignals(False)

    def sync_logic(self):
        """모든 테이블 데이터 연동 및 통계 계산"""
        if not self.staff_list: return
        self.table1.blockSignals(True); self.table3.blockSignals(True)
        
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        
        # 배치표 초기화
        for r in range(2, 8):
            for c in range(1, days + 1):
                self.table3.setItem(r, c, QTableWidgetItem(""))

        # 통계 및 배치
        for r in range(len(self.staff_list)):
            sid, name, role, ward = self.staff_list[r]
            cnt = {"D":0, "E":0, "N":0, "O":0, "M":0}
            
            for d in range(days):
                duty = self.table2.item(r, d+2).text().replace("[R]", "").strip()
                if not duty: continue
                
                # 통계
                d_key = duty[0].upper()
                if d_key in cnt: cnt[d_key] += 1
                
                # 배치표 행 찾기
                t3_row = -1
                is_nurse = "간호사" in role
                # 특수근무(n5, D5 등) 처리
                target_ward = ward
                if "3" in duty: target_ward = "3W"
                elif "4" in duty: target_ward = "4W"
                elif "5" in duty: target_ward = "5W"
                
                if "n" in duty: is_nurse = False # 간호사가 보호사 근무

                if is_nurse:
                    t3_row = 2 if "3W" in target_ward else 3 if "4W" in target_ward else 4
                else:
                    t3_row = 5 if "3W" in target_ward else 6 if "4W" in target_ward else 7
                
                if t3_row != -1:
                    prev = self.table3.item(t3_row, d+1).text()
                    new_text = (prev + "\n" + f"{duty[0]}{name}").strip()
                    self.table3.setItem(t3_row, d+1, QTableWidgetItem(new_text))

            # Table 1 통계 업데이트
            for i, k in enumerate(["D", "E", "N", "O", "M"]):
                self.table1.setItem(r, 5+i, QTableWidgetItem(str(cnt[k])))

        # Footer 업데이트
        n_list = [f"{s[1]}" for s in self.staff_list if "간호사" in s[2]]
        a_list = [f"{s[1]}" for s in self.staff_list if "보호사" in s[2]]
        self.footer_label.setText(f"<b>[간호사]</b> {', '.join(n_list)}  |  <b>[보호사]</b> {', '.join(a_list)}")

        self.table1.blockSignals(False); self.table3.blockSignals(False)

    # --- 이벤트 핸들러 ---
    def show_context_menu(self, pos):
        menu = QMenu()
        act_add_up = menu.addAction("위에 행 추가")
        act_add_down = menu.addAction("아래에 행 추가")
        act_del = menu.addAction("행 삭제")
        
        action = menu.exec(self.table1.mapToGlobal(pos))
        row = self.table1.currentRow()
        
        if action == act_add_up: self.add_staff(row)
        elif action == act_add_down: self.add_staff(row + 1)
        elif action == act_del: self.delete_staff(row)

    def add_staff(self, row_idx):
        new_staff = [0, "신규", "간호사", "3W"]
        self.staff_list.insert(row_idx, new_staff)
        self.refresh_tables()

    def delete_staff(self, row_idx):
        if 0 <= row_idx < len(self.staff_list):
            self.staff_list.pop(row_idx)
            self.refresh_tables()

    def on_table1_item_changed(self, item):
        r, c = item.row(), item.column()
        if c < 4: # 정보 변경 시
            val = item.text()
            if c == 0: self.staff_list[r][0] = val
            elif c == 1: self.staff_list[r][1] = val
            elif c == 2: self.staff_list[r][2] = val
            elif c == 3: self.staff_list[r][3] = val
            self.refresh_tables()

    def on_table2_item_changed(self, item):
        self.sync_logic()

    def on_table2_cell_clicked(self, r, c):
        if not self.request_mode or c < 2: return
        item = self.table2.item(r, c)
        txt = item.text()
        if "[R]" in txt:
            item.setText(txt.replace("[R]", ""))
            item.setForeground(QColor("black"))
        else:
            item.setText(f"[R]{txt}")
            item.setForeground(QColor("red"))

    def set_request_mode(self, val):
        self.request_mode = val

    # --- 파일 입출력 (엑셀 스타일 저장/불러오기) ---
    def save_to_file(self):
        # 현재 화면의 데이터를 duty_records에 반영
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        key = f"{self.current_year}-{self.current_month:02d}"
        current_month_duties = {}
        
        for r in range(len(self.staff_list)):
            sid = str(self.staff_list[r][0])
            duties = []
            for d in range(days):
                duties.append(self.table2.item(r, d+2).text())
            current_month_duties[sid] = duties
        
        self.duty_records[key] = current_month_duties

        data = {
            "staff_list": self.staff_list,
            "duty_records": self.duty_records
        }
        with open("duty_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        QMessageBox.information(self, "저장", "성공적으로 저장되었습니다 (duty_data.json)")

    def load_from_file(self):
        if os.path.exists("duty_data.json"):
            with open("duty_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.staff_list = data.get("staff_list", self.staff_list)
                self.duty_records = data.get("duty_records", {})

    def load_dialog(self):
        text, ok = QInputDialog.getText(self, "불러오기", "년-월을 입력하세요 (예: 2025-12):")
        if ok and text:
            try:
                y, m = map(int, text.split("-"))
                self.current_year, self.current_month = y, m
                self.label_title.setText(f"📅 {y}년 {m}월 근무표")
                self.refresh_tables()
            except:
                QMessageBox.warning(self, "에러", "형식이 잘못되었습니다 (YYYY-MM)")

    # --- 인쇄 및 자동완성 (v8.0 기능 유지) ---
    def run_algo(self):
        import random
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        self.table2.blockSignals(True)
        for r in range(len(self.staff_list)):
            role = self.staff_list[r][2]
            possible = ["D", "E", "N", "O"] if "간호사" in role else ["D", "N", "O"]
            for d in range(days):
                item = self.table2.item(r, d+2)
                if not item.text():
                    item.setText(random.choice(possible))
        self.table2.blockSignals(False)
        self.sync_logic()

    def print_preview(self, table):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.handle_print(p, table))
        preview.exec()

    def handle_print(self, printer, table):
        painter = QPainter(printer)
        page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        
        # 1. 테이블 전체 크기 계산
        total_width = 0
        for c in range(table.columnCount()): total_width += table.columnWidth(c)
        total_height = 0
        for r in range(table.rowCount()): total_height += table.rowHeight(r)
        
        # 2. 배율 계산 (A4 가로 한 장에 맞춤)
        scale_x = page_rect.width() / (total_width + 100)
        scale_y = (page_rect.height() - 100) / (total_height + 100)
        scale = min(scale_x, scale_y, 1.0) # 너무 커지지 않게 제한
        
        painter.scale(scale, scale)
        
        # 3. 그리기
        x, y = 50, 50
        # 제목 그리기
        painter.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        painter.drawText(x, y-10, f"{self.current_year}년 {self.current_month}월 근무표")
        
        painter.setFont(QFont("Malgun Gothic", 7))
        for r in range(table.rowCount()):
            curr_x = x
            row_h = table.rowHeight(r)
            for c in range(table.columnCount()):
                col_w = table.columnWidth(c)
                rect = QRect(curr_x, y, col_w, row_h)
                
                # 배경색
                item = table.item(r, c)
                if item:
                    painter.fillRect(rect, item.background())
                    painter.drawRect(rect)
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, item.text())
                else:
                    painter.drawRect(rect)
                curr_x += col_w
            y += row_h
        
        # 푸터 (배치표인 경우만)
        if table == self.table3:
            painter.drawText(x, y + 20, self.footer_label.text().replace("<b>","").replace("</b>",""))
            
        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = DutyAppV9()
    win.show()
=======
import sys
import calendar
import json
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

class DutyAppV9(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나눔과행복병원 근무표 생성기 v9.0")
        self.resize(1600, 900)
        
        # 데이터 초기화
        self.current_year = 2025
        self.current_month = 12
        self.request_mode = False
        self.staff_list = []  # [[번호, 이름, 직종, 병동], ...]
        self.duty_records = {} # {"YYYY-MM": { "SID": [근무리스트] }}
        
        # 초기 명단 설정 (v8.0 기준)
        self.init_staff_data()
        
        self.init_ui()
        self.load_from_file() # 파일에서 기존 데이터 로드
        self.refresh_tables()

    def init_staff_data(self):
        # 기본 명단 셋업
        initial_data = [
            (31, "최민애", "간호사", "3W"), (32, "김유하", "간호사", "3W"), (33, "김민경", "간호사", "3W"),
            (34, "김다인", "간호사", "3W"), (35, "김다솜", "간호사", "3W"), (36, "전치구", "보호사", "3W"),
            (37, "김재호", "보호사", "3W"), (38, "송재웅", "보호사", "3W"), (39, "지정우", "보호사", "3W"),
            (41, "이미경", "간호사", "4W"), (42, "권수진", "간호사", "4W"), (43, "정지우", "간호사", "4W"),
            (44, "송선아", "간호사", "4W"), (46, "송현찬", "보호사", "4W"), (47, "김두현", "보호사", "4W"),
            (48, "하영기", "보호사", "4W"), (51, "김도연", "간호사", "5W"), (52, "김나은", "간호사", "5W"),
            (53, "허예리", "간호사", "5W"), (54, "박수진", "간호사", "5W"), (55, "김민영", "간호사", "5W"),
            (56, "서현도", "보호사", "5W"), (57, "김두현(주)", "보호사", "5W"), (58, "제상수", "보호사", "5W")
        ]
        for d in initial_data:
            self.staff_list.append(list(d))

    def get_ward_color(self, sid, role, ward):
        # 병동 및 직종별 색상 지정
        try:
            sid_int = int(sid)
        except: sid_int = 0

        if "간호사" in role:
            if "3W" in ward or (30 <= sid_int <= 35): return QColor("#FFF9C4") # 연노랑
            if "4W" in ward or (40 <= sid_int <= 45): return QColor("#FFF176") # 중간노랑
            if "5W" in ward or (50 <= sid_int <= 55): return QColor("#FBC02D") # 진노랑
        else: # 보호사
            if "3W" in ward or (36 <= sid_int <= 39): return QColor("#E1F5FE") # 연하늘
            if "4W" in ward or (46 <= sid_int <= 49): return QColor("#81D4FA") # 중간하늘
            if "5W" in ward or (56 <= sid_int <= 59): return QColor("#29B6F6") # 진하늘
        return QColor("white")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 상단 컨트롤바
        top_bar = QHBoxLayout()
        self.label_title = QLabel(f"📅 {self.current_year}년 {self.current_month}월 근무표")
        self.label_title.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        
        self.btn_load = QPushButton("📂 불러오기"); self.btn_load.clicked.connect(self.load_dialog)
        self.btn_save = QPushButton("💾 전체 저장"); self.btn_save.clicked.connect(self.save_to_file)
        self.btn_run = QPushButton("🚀 RUN (자동완성)"); self.btn_run.clicked.connect(self.run_algo)
        self.cb_request = QCheckBox("🔴 Request 모드"); self.cb_request.toggled.connect(self.set_request_mode)
        
        top_bar.addWidget(self.label_title)
        top_bar.addStretch()
        top_bar.addWidget(self.cb_request)
        top_bar.addWidget(self.btn_run)
        top_bar.addWidget(self.btn_load)
        top_bar.addWidget(self.btn_save)
        main_layout.addLayout(top_bar)

        # 탭 구성
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # 테이블 1: 명단 및 설정
        self.table1 = QTableWidget()
        self.table1.setColumnCount(10)
        self.table1.setHorizontalHeaderLabels(["번호", "이름", "구분", "병동", "전월막근", "D", "E", "N", "O", "M"])
        self.table1.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table1.customContextMenuRequested.connect(self.show_context_menu)
        self.table1.itemChanged.connect(self.on_table1_item_changed)
        self.tabs.addTab(self.table1, "1. 인원 관리 (우클릭: 행추가)")

        # 테이블 2: 개인 근무표
        self.table2 = QTableWidget()
        self.table2.cellClicked.connect(self.on_table2_cell_clicked)
        self.table2.itemChanged.connect(self.on_table2_item_changed)
        
        t2_page = QWidget(); t2_lay = QVBoxLayout(t2_page)
        t2_btn_lay = QHBoxLayout()
        t2_btn_print = QPushButton("🖨️ 개인 근무표 인쇄"); t2_btn_print.clicked.connect(lambda: self.print_preview(self.table2))
        t2_btn_lay.addStretch(); t2_btn_lay.addWidget(t2_btn_print)
        t2_lay.addLayout(t2_btn_lay); t2_lay.addWidget(self.table2)
        self.tabs.addTab(t2_page, "2. 근무 입력")

        # 테이블 3: 병동 배치표
        self.table3 = QTableWidget()
        from PyQt6.QtWidgets import QStyledItemDelegate
        # 세로쓰기 Delegate는 생략(표준 텍스트로 가독성 확보)
        
        t3_page = QWidget(); t3_lay = QVBoxLayout(t3_page)
        t3_btn_lay = QHBoxLayout()
        t3_btn_print = QPushButton("🖨️ 병동 배치표 인쇄"); t3_btn_print.clicked.connect(lambda: self.print_preview(self.table3))
        t3_btn_lay.addStretch(); t3_btn_lay.addWidget(t3_btn_print)
        t3_lay.addLayout(t3_btn_lay); t3_lay.addWidget(self.table3)
        self.footer_label = QLabel()
        t3_lay.addWidget(self.footer_label)
        self.tabs.addTab(t3_page, "3. 병동별 배치표")

    def refresh_tables(self):
        """명단 기반으로 모든 테이블 다시 그리기"""
        self.table1.blockSignals(True); self.table2.blockSignals(True); self.table3.blockSignals(True)
        
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        key = f"{self.current_year}-{self.current_month:02d}"
        month_data = self.duty_records.get(key, {})

        # Table 1 & 2 행수 설정
        self.table1.setRowCount(len(self.staff_list))
        self.table2.setRowCount(len(self.staff_list))
        self.table2.setColumnCount(days + 2)
        
        # Table 2 헤더
        headers = ["번호", "이름"] + [str(d) for d in range(1, days+1)]
        self.table2.setHorizontalHeaderLabels(headers)
        self.table2.setColumnWidth(0, 40) # 번호열 축소

        for r, staff in enumerate(self.staff_list):
            sid, name, role, ward = staff
            color = self.get_ward_color(sid, role, ward)

            # Table 1 채우기
            for c, val in enumerate([sid, name, role, ward]):
                item = QTableWidgetItem(str(val))
                item.setBackground(color)
                self.table1.setItem(r, c, item)

            # Table 2 채우기
            self.table2.setItem(r, 0, QTableWidgetItem(str(sid)))
            self.table2.setItem(r, 1, QTableWidgetItem(name))
            self.table2.item(r,0).setBackground(color); self.table2.item(r,1).setBackground(color)
            
            duties = month_data.get(str(sid), [""] * days)
            for d in range(days):
                duty_val = duties[d] if d < len(duties) else ""
                item = QTableWidgetItem(duty_val)
                if "[R]" in duty_val: item.setForeground(QColor("red"))
                
                # 주말 배경색
                wd = calendar.weekday(self.current_year, self.current_month, d+1)
                if wd == 5: item.setBackground(QColor("#E3F2FD")) # 토
                elif wd == 6: item.setBackground(QColor("#FFEBEE")) # 일
                else: item.setBackground(color)
                
                self.table2.setItem(r, d+2, item)
                self.table2.setColumnWidth(d+2, 30)

        self.table1.blockSignals(False); self.table2.blockSignals(False); self.table3.blockSignals(False)
        self.setup_table3_layout()
        self.sync_logic()

    def setup_table3_layout(self):
        """배치표 레이아웃 설정"""
        self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        self.table3.setColumnCount(days + 1)
        self.table3.setRowCount(9) # 날짜, 요일, 3W간호, 4W간호, 5W간호, 3W보호, 4W보호, 5W보호, 구분
        
        headers = ["병동"] + [str(d) for d in range(1, days+1)]
        self.table3.setHorizontalHeaderLabels(headers)
        
        row_titles = ["날짜", "요일", "3W 간호", "4W 간호", "5W 간호", "3W 보호", "4W 보호", "5W 보호"]
        for i, title in enumerate(row_titles):
            self.table3.setItem(i, 0, QTableWidgetItem(title))
            if i >= 2: self.table3.setRowHeight(i, 100)

        # 요일 채우기
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in range(1, days + 1):
            wd_idx = calendar.weekday(self.current_year, self.current_month, d)
            item = QTableWidgetItem(weekdays[wd_idx])
            if wd_idx == 5: item.setForeground(QColor("blue"))
            if wd_idx == 6: item.setForeground(QColor("red"))
            self.table3.setItem(1, d, item)
            self.table3.setColumnWidth(d, 45)

        self.table3.blockSignals(False)

    def sync_logic(self):
        """모든 테이블 데이터 연동 및 통계 계산"""
        if not self.staff_list: return
        self.table1.blockSignals(True); self.table3.blockSignals(True)
        
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        
        # 배치표 초기화
        for r in range(2, 8):
            for c in range(1, days + 1):
                self.table3.setItem(r, c, QTableWidgetItem(""))

        # 통계 및 배치
        for r in range(len(self.staff_list)):
            sid, name, role, ward = self.staff_list[r]
            cnt = {"D":0, "E":0, "N":0, "O":0, "M":0}
            
            for d in range(days):
                duty = self.table2.item(r, d+2).text().replace("[R]", "").strip()
                if not duty: continue
                
                # 통계
                d_key = duty[0].upper()
                if d_key in cnt: cnt[d_key] += 1
                
                # 배치표 행 찾기
                t3_row = -1
                is_nurse = "간호사" in role
                # 특수근무(n5, D5 등) 처리
                target_ward = ward
                if "3" in duty: target_ward = "3W"
                elif "4" in duty: target_ward = "4W"
                elif "5" in duty: target_ward = "5W"
                
                if "n" in duty: is_nurse = False # 간호사가 보호사 근무

                if is_nurse:
                    t3_row = 2 if "3W" in target_ward else 3 if "4W" in target_ward else 4
                else:
                    t3_row = 5 if "3W" in target_ward else 6 if "4W" in target_ward else 7
                
                if t3_row != -1:
                    prev = self.table3.item(t3_row, d+1).text()
                    new_text = (prev + "\n" + f"{duty[0]}{name}").strip()
                    self.table3.setItem(t3_row, d+1, QTableWidgetItem(new_text))

            # Table 1 통계 업데이트
            for i, k in enumerate(["D", "E", "N", "O", "M"]):
                self.table1.setItem(r, 5+i, QTableWidgetItem(str(cnt[k])))

        # Footer 업데이트
        n_list = [f"{s[1]}" for s in self.staff_list if "간호사" in s[2]]
        a_list = [f"{s[1]}" for s in self.staff_list if "보호사" in s[2]]
        self.footer_label.setText(f"<b>[간호사]</b> {', '.join(n_list)}  |  <b>[보호사]</b> {', '.join(a_list)}")

        self.table1.blockSignals(False); self.table3.blockSignals(False)

    # --- 이벤트 핸들러 ---
    def show_context_menu(self, pos):
        menu = QMenu()
        act_add_up = menu.addAction("위에 행 추가")
        act_add_down = menu.addAction("아래에 행 추가")
        act_del = menu.addAction("행 삭제")
        
        action = menu.exec(self.table1.mapToGlobal(pos))
        row = self.table1.currentRow()
        
        if action == act_add_up: self.add_staff(row)
        elif action == act_add_down: self.add_staff(row + 1)
        elif action == act_del: self.delete_staff(row)

    def add_staff(self, row_idx):
        new_staff = [0, "신규", "간호사", "3W"]
        self.staff_list.insert(row_idx, new_staff)
        self.refresh_tables()

    def delete_staff(self, row_idx):
        if 0 <= row_idx < len(self.staff_list):
            self.staff_list.pop(row_idx)
            self.refresh_tables()

    def on_table1_item_changed(self, item):
        r, c = item.row(), item.column()
        if c < 4: # 정보 변경 시
            val = item.text()
            if c == 0: self.staff_list[r][0] = val
            elif c == 1: self.staff_list[r][1] = val
            elif c == 2: self.staff_list[r][2] = val
            elif c == 3: self.staff_list[r][3] = val
            self.refresh_tables()

    def on_table2_item_changed(self, item):
        self.sync_logic()

    def on_table2_cell_clicked(self, r, c):
        if not self.request_mode or c < 2: return
        item = self.table2.item(r, c)
        txt = item.text()
        if "[R]" in txt:
            item.setText(txt.replace("[R]", ""))
            item.setForeground(QColor("black"))
        else:
            item.setText(f"[R]{txt}")
            item.setForeground(QColor("red"))

    def set_request_mode(self, val):
        self.request_mode = val

    # --- 파일 입출력 (엑셀 스타일 저장/불러오기) ---
    def save_to_file(self):
        # 현재 화면의 데이터를 duty_records에 반영
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        key = f"{self.current_year}-{self.current_month:02d}"
        current_month_duties = {}
        
        for r in range(len(self.staff_list)):
            sid = str(self.staff_list[r][0])
            duties = []
            for d in range(days):
                duties.append(self.table2.item(r, d+2).text())
            current_month_duties[sid] = duties
        
        self.duty_records[key] = current_month_duties

        data = {
            "staff_list": self.staff_list,
            "duty_records": self.duty_records
        }
        with open("duty_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        QMessageBox.information(self, "저장", "성공적으로 저장되었습니다 (duty_data.json)")

    def load_from_file(self):
        if os.path.exists("duty_data.json"):
            with open("duty_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.staff_list = data.get("staff_list", self.staff_list)
                self.duty_records = data.get("duty_records", {})

    def load_dialog(self):
        text, ok = QInputDialog.getText(self, "불러오기", "년-월을 입력하세요 (예: 2025-12):")
        if ok and text:
            try:
                y, m = map(int, text.split("-"))
                self.current_year, self.current_month = y, m
                self.label_title.setText(f"📅 {y}년 {m}월 근무표")
                self.refresh_tables()
            except:
                QMessageBox.warning(self, "에러", "형식이 잘못되었습니다 (YYYY-MM)")

    # --- 인쇄 및 자동완성 (v8.0 기능 유지) ---
    def run_algo(self):
        import random
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        self.table2.blockSignals(True)
        for r in range(len(self.staff_list)):
            role = self.staff_list[r][2]
            possible = ["D", "E", "N", "O"] if "간호사" in role else ["D", "N", "O"]
            for d in range(days):
                item = self.table2.item(r, d+2)
                if not item.text():
                    item.setText(random.choice(possible))
        self.table2.blockSignals(False)
        self.sync_logic()

    def print_preview(self, table):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.handle_print(p, table))
        preview.exec()

    def handle_print(self, printer, table):
        painter = QPainter(printer)
        page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        
        # 1. 테이블 전체 크기 계산
        total_width = 0
        for c in range(table.columnCount()): total_width += table.columnWidth(c)
        total_height = 0
        for r in range(table.rowCount()): total_height += table.rowHeight(r)
        
        # 2. 배율 계산 (A4 가로 한 장에 맞춤)
        scale_x = page_rect.width() / (total_width + 100)
        scale_y = (page_rect.height() - 100) / (total_height + 100)
        scale = min(scale_x, scale_y, 1.0) # 너무 커지지 않게 제한
        
        painter.scale(scale, scale)
        
        # 3. 그리기
        x, y = 50, 50
        # 제목 그리기
        painter.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        painter.drawText(x, y-10, f"{self.current_year}년 {self.current_month}월 근무표")
        
        painter.setFont(QFont("Malgun Gothic", 7))
        for r in range(table.rowCount()):
            curr_x = x
            row_h = table.rowHeight(r)
            for c in range(table.columnCount()):
                col_w = table.columnWidth(c)
                rect = QRect(curr_x, y, col_w, row_h)
                
                # 배경색
                item = table.item(r, c)
                if item:
                    painter.fillRect(rect, item.background())
                    painter.drawRect(rect)
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, item.text())
                else:
                    painter.drawRect(rect)
                curr_x += col_w
            y += row_h
        
        # 푸터 (배치표인 경우만)
        if table == self.table3:
            painter.drawText(x, y + 20, self.footer_label.text().replace("<b>","").replace("</b>",""))
            
        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = DutyAppV9()
    win.show()
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    sys.exit(app.exec())