import sys, calendar, json, os, random
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

class VerticalTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 0 or index.row() < 3: return super().paint(painter, option, index)
        text = str(index.data() or "")
        if text:
            painter.save()
            if index.data(Qt.ItemDataRole.ForegroundRole) == QColor("red"): painter.setPen(QColor("red"))
            painter.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            names = text.split('\n')
            rect, total = option.rect, len(names)
            w = rect.width() // max(1, total)
            for i, name in enumerate(names):
                nx = rect.x() + (i * w)
                ny = rect.y() + 5
                for char in name:
                    painter.drawText(nx, ny, w, 15, Qt.AlignmentFlag.AlignCenter, char)
                    ny += 13
            painter.restore()

class DutyAppV97(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나눔과행복병원 근무표 통합 관리기 v9.7")
        self.resize(1650, 950)
        self.current_year, self.current_month, self.request_mode = 2025, 12, False
        self.staff_list, self.duty_records, self.request_records = [], {}, {}
        self.init_initial_data()
        self.init_ui()
        self.refresh_tables()

    def init_initial_data(self):
        self.staff_list = [[31,"최민애","간호사"],[32,"김유하","간호사"],[33,"김민경","간호사"],[34,"김다인","간호사"],[35,"김다솜","간호사"],[41,"이미경","간호사"],[42,"권수진","간호사"],[43,"정지우","간호사"],[44,"송선아","간호사"],[51,"김도연","간호사"],[52,"김나은","간호사"],[53,"허예리","간호사"],[54,"박수진","간호사"],[55,"김민영","간호사"],[36,"전치구","보호사"],[37,"김재호","보호사"],[38,"송재웅","보호사"],[39,"지정우","보호사"],[46,"송현찬","보호사"],[47,"김두현","보호사"],[48,"하영기","보호사"],[56,"서현도","보호사"],[57,"김두현(주)","보호사"],[58,"제상수","보호사"]]
        key, raw_12 = "2025-12", {"31":"D,O,D,D,D,O,O,D,D,N,N,N,O,O,D,D,N,N,N,O,O,D,D,D,O,N,N,O,O,D,D","32":"E,O,O,E,E,O,N,N,N,O,O,E,O,O,E,E,E,E,E,O,O,E,N,N,O,E,E,N,N,O,O","33":"O,E,E,O,O,D,D,N4,N4,N4,O,O,D,D,O,E,N4,N4,O,O,D,E,O,O,D,D,D,O,O,N4,N4","34":"O,D,N,N,O,E,E,E,O,D,D,D,E,O,D,N,N,O,E,N,N,O,O,N,N,O,O,O,E,O,E","35":"N,N,O,O,N,N,O,O,E,E,E,O,N,N,N,O,O,D,D,D,O,O,E,E,E,O,O,D,D,E,N","41":"O,D,D,N,N,O,O,D,D,D,D,D,O,O,D,D,D,D,O,O,N,N,N,O,D,N,N,N,O,O,O","42":"N,O,O,D,D,N,N,O,E,E,O,E,O,N,N,N,O,O,E,E,O,E,E,O,N,N,O,O,D,D,D","43":"E,E,E,E,O,E,E,O,O,O,E,O,D,D,D,O,O,D,E,O,E,O,D,D,D,O,O,D,E,E,E","44":"D,N,N,O,O,D,D,E,O,O,O,N,N,N,O,E,E,E,O,N,N,N,O,O,E,E,E,E,E,O,E","51":"O,O,D,D,N,N,N,O,O,E,E,E,N,N,O,E,E,O,D,D,N,N,O,O,D,D,D,O,O,E,O","52":"D,D,O,O,E4,E,E,O,E,O,O,O,E4,E4,N,N,O,O,O,D4,D4,D4,O,N,N,N,O,O,N,N,N","53":"E,O,E,E,E,O,O,E,O,D,D,D,E,O,D,D,D,O,E,E,O,D,D,E,O,O,O,E,E,O,O","54":"O,E,N,N,O,O,D,D,D,O,N,N,O,E,E,E,O,D,D,N,N,O,O,D,D,O,N,N,O,O,E","55":"N,N,O,O,O,D,O,N,N,N,O,O,D,D,O,N,N,N,O,E,E,E,O,E,E,O,O,D,D,D,O","36":"D4,D4,D,O,D4,O,O,N,N,O,O,D,O,O,N,N,O,O,D5,D5,O,D,D5,O,O,D,D,O,N4,N4,N4","37":"N,N,O,O,D,D5,O,D,D5,O,D5,O,N,N,O,O,D,N,N,N,O,O,O,D,D,N5,N5,N,O,O,O","38":"D,D,O,O,N,N,N,O,O,D,D,O,O,O,O,O,N,N,O,O,D,O,D,N,N,O,D,N,N,O,O","39":"O,O,N,N,O,D,D,D,O,N,N,N,O,O,D,D,D,O,D,D,O,N,N,O,O,N,N,O,O,D,N","46":"O,O,N,N,O,D,D,D,O,N,N,N,O,D,D,O,D,D,D,O,N,N,O,D,N,N,O,O,D,D,D3","47":"N,N,O,O,N,N,O,O,D,D,D,O,N,N,O,D,N,N,N,O,O,D,D,D,O,D,O,D,D,O,O","48":"O,O,D,D,O,O,N,N,N,O,O,D,O,O,D,N,O,O,D,D,O,N,N,N,O,O,D,N,N,O,O","56":"N,N,O,D,D,D,O,O,N,N,N,O,O,D,D,O,D,O,O,D,D,O,N,N,O,O,N,N,N,O,O","57":"O,O,N,N,N,O,O,D,D,O,D,N,N,N,O,D,D,N,N,O,O,N,N,O,D,O,D,D,O,D,D","58":"D,D,D,O,O,N,N,N,O,O,O,D,D,O,N,N,N,O,O,N,N,O,O,D,O,D,D,O,O,D,N"}
        self.duty_records[key] = {k: v.split(",") for k, v in raw_12.items()}
        self.request_records[key] = {k: [False]*31 for k in raw_12.keys()}
        self.request_records[key]["31"][1] = True

    def get_ward_color(self, sid):
        if 31 <= sid <= 35: return QColor("#FFF9C4")
        if 41 <= sid <= 45: return QColor("#FFF176")
        if 51 <= sid <= 55: return QColor("#FBC02D")
        if 36 <= sid <= 39: return QColor("#E1F5FE")
        if 46 <= sid <= 49: return QColor("#81D4FA")
        if 56 <= sid <= 59: return QColor("#29B6F6")
        return QColor("white")

    def init_ui(self):
        c = QWidget(); self.setCentralWidget(c); l = QVBoxLayout(c); self.tabs = QTabWidget(); l.addWidget(self.tabs)
        # T1
        p1 = QWidget(); l1 = QVBoxLayout(p1); self.title_t1 = QLabel(); self.title_t1.setFont(QFont("Malgun Gothic",16,QFont.Weight.Bold)); l1.addWidget(self.title_t1)
        h1 = QHBoxLayout(); self.btn_load = QPushButton("📂 불러오기"); self.btn_load.clicked.connect(self.load_dialog); self.btn_save = QPushButton("💾 저장"); self.btn_save.clicked.connect(self.save_to_file); self.btn_next1 = QPushButton("다음 달 ▶"); self.btn_next1.clicked.connect(self.go_next)
        h1.addStretch(); h1.addWidget(self.btn_load); h1.addWidget(self.btn_save); h1.addWidget(self.btn_next1); l1.addLayout(h1)
        self.table1 = QTableWidget(0,10); self.table1.setHorizontalHeaderLabels(["번호","이름","구분","전월막근","연속일","D","E","N","O","M"]); self.table1.setColumnWidth(0,30); self.table1.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu); self.table1.customContextMenuRequested.connect(self.show_context_menu); self.table1.itemChanged.connect(self.on_table1_changed); l1.addWidget(self.table1); self.tabs.addTab(p1,"인원 관리")
        # T2
        p2 = QWidget(); l2 = QVBoxLayout(p2); self.title_t2 = QLabel(); self.title_t2.setFont(QFont("Malgun Gothic",16,QFont.Weight.Bold)); l2.addWidget(self.title_t2)
        h2 = QHBoxLayout(); self.cb_req = QCheckBox("🔴 Request 모드"); self.cb_req.toggled.connect(lambda v: setattr(self, 'request_mode', v)); self.btn_run = QPushButton("🚀 자동배정"); self.btn_run.clicked.connect(self.run_algo); self.btn_pr2 = QPushButton("🖨️ 인쇄"); self.btn_pr2.clicked.connect(lambda: self.print_preview(self.table2)); self.btn_next2 = QPushButton("다음 달 ▶"); self.btn_next2.clicked.connect(self.go_next)
        h2.addWidget(self.cb_req); h2.addStretch(); h2.addWidget(self.btn_run); h2.addWidget(self.btn_pr2); h2.addWidget(self.btn_next2); l2.addLayout(h2)
        self.table2 = QTableWidget(); self.table2.cellClicked.connect(self.on_table2_click); self.table2.itemChanged.connect(self.on_table2_changed); l2.addWidget(self.table2); self.tabs.addTab(p2,"근무표 편집")
        # T3
        p3 = QWidget(); l3 = QVBoxLayout(p3); self.title_t3 = QLabel(); self.title_t3.setFont(QFont("Malgun Gothic",16,QFont.Weight.Bold)); l3.addWidget(self.title_t3)
        h3 = QHBoxLayout(); self.btn_pr3 = QPushButton("🖨️ 인쇄 (A4)"); self.btn_pr3.clicked.connect(lambda: self.print_preview(self.table3)); self.btn_next3 = QPushButton("다음 달 ▶"); self.btn_next3.clicked.connect(self.go_next)
        h3.addStretch(); h3.addWidget(self.btn_pr3); h3.addWidget(self.btn_next3); l3.addLayout(h3)
        self.table3 = QTableWidget(); self.table3.setItemDelegate(VerticalTextDelegate()); l3.addWidget(self.table3); self.footer = QLabel(); self.footer.setFont(QFont("Malgun Gothic",9)); l3.addWidget(self.footer); self.tabs.addTab(p3,"출력 미리보기")

    def refresh_tables(self):
        self.table1.blockSignals(True); self.table2.blockSignals(True); self.table3.blockSignals(True)
        days = calendar.monthrange(self.current_year, self.current_month)[1]
        dt = f"📅 {self.current_year}년 {self.current_month}월 근무표"
        self.title_t1.setText(dt); self.title_t2.setText(dt); self.title_t3.setText(dt)
        key = f"{self.current_year}-{self.current_month:02d}"
        m_d = self.duty_records.get(key, {}); r_d = self.request_records.get(key, {})
        self.table1.setRowCount(len(self.staff_list)); self.table2.setRowCount(len(self.staff_list)+1); self.table2.setColumnCount(days+2)
        self.table2.setHorizontalHeaderLabels(["번호","성함"]+[str(d) for d in range(1, days+1)])
        self.table2.setColumnWidth(0,30); self.table1.setColumnWidth(0,30)
        wks = ["월","화","수","목","금","토","일"]
        for d in range(1, days+1):
            wd = calendar.weekday(self.current_year, self.current_month, d)
            it = QTableWidgetItem(wks[wd]); it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if wd==5: it.setForeground(QColor("blue"))
            elif wd==6: it.setForeground(QColor("red"))
            self.table2.setItem(0, d+1, it)
        for r, s in enumerate(self.staff_list):
            sid, name, role = s; color = self.get_ward_color(sid)
            for c, v in enumerate([sid, name, role]):
                it = QTableWidgetItem(str(v)); it.setBackground(color); self.table1.setItem(r, c, it)
            it0 = QTableWidgetItem(str(sid)); it0.setBackground(color); self.table2.setItem(r+1, 0, it0)
            it1 = QTableWidgetItem(name); it1.setBackground(color); self.table2.setItem(r+1, 1, it1)
            ds = m_d.get(str(sid), [""]*days); rqs = r_d.get(str(sid), [False]*days)
            for d in range(days):
                v = ds[d] if d<len(ds) else ""; it = QTableWidgetItem(v); it.setBackground(color)
                if d<len(rqs) and rqs[d]: it.setForeground(QColor("red"))
                self.table2.setItem(r+1, d+2, it); self.table2.setColumnWidth(d+2, 28)
        self.table1.blockSignals(False); self.table2.blockSignals(False); self.table3.blockSignals(False)
        self.setup_table3_layout(days); self.sync_logic()

    def setup_table3_layout(self, days):
        self.table3.blockSignals(True); self.table3.setColumnCount(days*3+1); self.table3.setRowCount(10); self.table3.setColumnWidth(0, 30)
        for r in range(10):
            for c in range(days*3+1): self.table3.setItem(r, c, QTableWidgetItem(""))
        wks = ["월","화","수","목","금","토","일"]
        for d in range(1, days+1):
            c = (d-1)*3+1; self.table3.setSpan(0,c,1,3); self.table3.item(0,c).setText(str(d))
            wd = calendar.weekday(self.current_year, self.current_month, d)
            self.table3.setSpan(1,c,1,3); self.table3.item(1,c).setText(wks[wd])
            if wd==5: self.table3.item(1,c).setForeground(QColor("blue"))
            elif wd==6: self.table3.item(1,c).setForeground(QColor("red"))
            for i, s in enumerate(["D","E","N"]): self.table3.item(2, c+i).setText(s)
            self.table3.item(6, c).setText("D"); self.table3.item(6, c+2).setText("N"); self.table3.item(6, c+1).setBackground(QColor("gray"))
            for i in range(3): self.table3.setColumnWidth(c+i, 25)
        ts = ["날짜","요일","간호사","3W","4W","5W","보호사","3W","4W","5W"]
        for i, t in enumerate(ts):
            self.table3.item(i,0).setText(t); self.table3.setRowHeight(i, 80 if i in [3,4,5,7,8,9] else 30)
        for dc in range(1, days*3+1):
            self.table3.item(3,dc).setBackground(QColor("#FFF9C4")); self.table3.item(4,dc).setBackground(QColor("#FFF176")); self.table3.item(5,dc).setBackground(QColor("#FBC02D"))
            self.table3.item(7,dc).setBackground(QColor("#E1F5FE")); self.table3.item(8,dc).setBackground(QColor("#81D4FA")); self.table3.item(9,dc).setBackground(QColor("#29B6F6"))
        self.table3.blockSignals(False)

    def sync_logic(self):
        self.table1.blockSignals(True); self.table3.blockSignals(True); days = calendar.monthrange(self.current_year, self.current_month)[1]
        for r in [3,4,5,7,8,9]:
            for c in range(1, self.table3.columnCount()):
                it = self.table3.item(r, c); 
                if it and it.text() != "X": it.setText("")
        for r, s in enumerate(self.staff_list):
            sid, name, role = s; stats = {"D":0,"E":0,"N":0,"O":0,"M":0}
            for d in range(days):
                cell = self.table2.item(r+1, d+2)
                if not cell: continue
                dt = cell.text().strip(); 
                if not dt: continue
                tp = dt[0].upper(); 
                if tp in stats: stats[tp] += 1
                if tp == "O": continue
                is_n = "간호사" in role; cb = d*3+1; wd = "3W" if (31<=sid<=39) else "4W" if (41<=sid<=49) else "5W"
                if "3" in dt: wd = "3W"
                elif "4" in dt: wd = "4W"
                elif "5" in dt: wd = "5W"
                if "n" in dt: is_n = False
                tr = (3 if wd=="3W" else 4 if wd=="4W" else 5) if is_n else (7 if wd=="3W" else 8 if wd=="4W" else 9)
                tc = cb + (1 if "E" in dt.upper() else 2 if "N" in dt.upper() else 0)
                tg = self.table3.item(tr, tc)
                if tg and tg.text() != "X": tg.setText((tg.text()+"\n"+name).strip()); 
                if cell.foreground().color() == QColor("red"): tg.setForeground(QColor("red"))
            for i, k in enumerate(["D","E","N","O","M"]): self.table1.setItem(r, 5+i, QTableWidgetItem(str(stats[k])))
        ns = [f"{s[0]}{s[1]}" for s in self.staff_list if "간호사" in s[2]]; as_ = [f"{s[0]}{s[1]}" for s in self.staff_list if "보호사" in s[2]]
        self.footer.setText(f"<b>[간호사]</b> {' | '.join(ns)}<br><b>[보호사]</b> {' | '.join(as_)}")
        self.table1.blockSignals(False); self.table3.blockSignals(False)

    def on_table2_click(self, r, c):
        if not self.request_mode or r==0 or c<2: return
        it = self.table2.item(r, c)
        if it.foreground().color() == QColor("red"): it.setForeground(QColor("black"))
        else: it.setForeground(QColor("red"))
        self.sync_logic()

    def on_table2_changed(self, it):
        if self.request_mode: it.setForeground(QColor("red"))
        self.sync_logic()

    def run_algo(self):
        days = calendar.monthrange(self.current_year, self.current_month)[1]; self.table2.blockSignals(True)
        for d in range(1, days+1):
            cb = (d-1)*3+1
            for w_i in range(3):
                tr = 3 + w_i
                for s_i, sc in enumerate(["D","E","N"]):
                    tg = self.table3.item(tr, cb+s_i)
                    if tg and (tg.text()=="X" or tg.text().strip()!=""): continue
                    el = [s for s in self.staff_list if "간호사" in s[2] and (31+w_i*10<=s[0]<=35+w_i*10)]; random.shuffle(el)
                    for st in el:
                        ri = next(i for i,x in enumerate(self.staff_list) if x[0]==st[0])
                        if self.table2.item(ri+1, d+1).text().strip()=="": self.table2.item(ri+1, d+1).setText(sc); break
            for w_i in range(2):
                tr = 7 + w_i
                for s_i, sc in enumerate(["D","N"]):
                    tc = cb + (0 if sc=="D" else 2); tg = self.table3.item(tr, tc)
                    if tg and (tg.text()=="X" or tg.text().strip()!=""): continue
                    el = [s for s in self.staff_list if "보호사" in s[2] and (36+w_i*10<=s[0]<=39+w_i*10)]; random.shuffle(el)
                    for st in el:
                        ri = next(i for i,x in enumerate(self.staff_list) if x[0]==st[0])
                        if self.table2.item(ri+1, d+1).text().strip()=="": self.table2.item(ri+1, d+1).setText(sc); break
        self.table2.blockSignals(False); self.sync_logic()

    def show_context_menu(self, pos):
        m = QMenu(); a1 = m.addAction("위에 행 추가"); a2 = m.addAction("아래에 행 추가"); a3 = m.addAction("행 삭제")
        ac = m.exec(self.table1.mapToGlobal(pos)); r = self.table1.currentRow()
        if ac==a1: self.staff_list.insert(r,[0,"신규","간호사"]); self.refresh_tables()
        elif ac==a2: self.staff_list.insert(r+1,[0,"신규","간호사"]); self.refresh_tables()
        elif ac==a3: self.staff_list.pop(r); self.refresh_tables()

    def on_table1_changed(self, it):
        r, c = it.row(), it.column()
        if c<3:
            v = it.text(); 
            if c==0: self.staff_list[r][0] = int(v) if v.isdigit() else 0
            elif c==1: self.staff_list[r][1] = v
            elif c==2: self.staff_list[r][2] = v
            self.refresh_tables()

    def save_to_file(self):
        k = f"{self.current_year}-{self.current_month:02d}"; days = calendar.monthrange(self.current_year, self.current_month)[1]; cd, cr = {}, {}
        for r in range(len(self.staff_list)):
            sid = str(self.staff_list[r][0]); cd[sid] = [self.table2.item(r+1, d+2).text() for d in range(days)]
            cr[sid] = [self.table2.item(r+1, d+2).foreground().color() == QColor("red") for d in range(days)]
        with open("duty_data.json", "w", encoding="utf-8") as f: json.dump({"staff": self.staff_list, "duty": {k:cd}, "req": {k:cr}}, f, ensure_ascii=False)
        QMessageBox.information(self, "저장", "저장되었습니다.")

    def load_dialog(self):
        t, ok = QInputDialog.getText(self, "불러오기", "년-월 (예: 2025-12):")
        if ok and t:
            try: y, m = map(int, t.split("-")); self.current_year, self.current_month = y, m; self.refresh_tables()
            except: QMessageBox.warning(self, "에러", "형식이 잘못되었습니다.")

    def go_next(self):
        self.current_month += 1
        if self.current_month > 12: self.current_month = 1; self.current_year += 1
        self.refresh_tables()

    def print_preview(self, t):
        p = QPrinter(QPrinter.PrinterMode.HighResolution); p.setPageOrientation(QPageLayout.Orientation.Landscape)
        pv = QPrintPreviewDialog(p, self); pv.paintRequested.connect(lambda pr: self.handle_print(pr, t)); pv.exec()

    def handle_print(self, pr, t):
        pnt = QPainter(pr); pg = pr.pageRect(QPrinter.Unit.DevicePixel)
        tw = sum([t.columnWidth(c) for c in range(t.columnCount())]); th = sum([t.rowHeight(r) for r in range(t.rowCount())])
        s = min(pg.width() / (tw+100), (pg.height()-150) / (th+100), 1.0); pnt.scale(s, s); x, y = 50, 80
        pnt.setFont(QFont("Malgun Gothic", 12, QFont.Weight.Bold)); pnt.drawText(x, y-20, f"{self.current_year}년 {self.current_month}월 근무표")
        pnt.setFont(QFont("Malgun Gothic", 7))
        for r in range(t.rowCount()):
            cx = x; rh = t.rowHeight(r)
            for c in range(t.columnCount()):
                cw = t.columnWidth(c); rect = QRect(cx, y, cw, rh); it = t.item(r, c)
                if it: pnt.fillRect(rect, it.background()); pnt.drawRect(rect); pnt.setPen(it.foreground().color()); pnt.drawText(rect, Qt.AlignmentFlag.AlignCenter, it.text()); pnt.setPen(QColor("black"))
                else: pnt.drawRect(rect)
                cx += cw
            y += rh
        pnt.end()

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion"); win = DutyAppV97(); win.show(); sys.exit(app.exec())