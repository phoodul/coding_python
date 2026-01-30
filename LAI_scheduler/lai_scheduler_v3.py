<<<<<<< HEAD
import tkinter as tk
from tkinter import ttk, messagebox
import calendar
import datetime
import json
import os
import threading
import time
from win10toast import ToastNotifier

# 데이터 저장 파일명
DATA_FILE = "lai_schedule_data_final.json"

# 약품 및 용량 데이터베이스
DRUG_DATABASE = {
    "아빌리파이 메인테나": ["300mg", "400mg"],
    "아빌리파이 아심투파이": ["720mg", "960mg"],
    "인베가 서스티나": ["78mg", "117mg", "156mg", "234mg"],
    "인베가 트린자": ["273mg", "410mg", "546mg", "819mg"],
    "인베가 하피에라": ["1092mg", "1560mg"]
}

class LAI_Scheduler_App:
    def __init__(self, root):
        self.root = root
        self.root.title("LAI 처방 스케줄러 (Dr. Final Ver.)")
        self.root.geometry("1100x900") # 화면을 조금 더 길게 늘렸습니다 (삭제 목록 공간 확보)

        # 현재 날짜 기준 설정
        self.current_date = datetime.date.today()
        self.year = self.current_date.year
        self.month = self.current_date.month

        # 데이터 로드
        self.schedule_data = self.load_data()

        # UI 구성
        self.create_header()
        self.create_calendar_frame()
        self.draw_calendar()
        
        # 단축키 바인딩 (F1 누르면 오늘 날짜 입력)
        self.root.bind("<F1>", lambda event: self.open_input_dialog(self.current_date.day))

        # 백그라운드 알림 스레드 시작
        self.start_notification_thread()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.schedule_data, f, ensure_ascii=False, indent=4)

    def create_header(self):
        nav_frame = tk.Frame(self.root, pady=10)
        nav_frame.pack(fill=tk.X)

        prev_btn = tk.Button(nav_frame, text="◀ 이전 달", command=self.prev_month, font=("맑은 고딕", 10))
        prev_btn.pack(side=tk.LEFT, padx=20)

        self.header_label = tk.Label(nav_frame, text=f"{self.year}년 {self.month}월", font=("맑은 고딕", 20, "bold"))
        self.header_label.pack(side=tk.LEFT, expand=True)

        next_btn = tk.Button(nav_frame, text="다음 달 ▶", command=self.next_month, font=("맑은 고딕", 10))
        next_btn.pack(side=tk.LEFT, padx=20)

        days_frame = tk.Frame(self.root)
        days_frame.pack(fill=tk.X, padx=10)
        days = ["일", "월", "화", "수", "목", "금", "토"]
        for i, day in enumerate(days):
            color = "red" if i == 0 else "blue" if i == 6 else "black"
            lbl = tk.Label(days_frame, text=day, font=("맑은 고딕", 11, "bold"), fg=color, width=14, relief="flat")
            lbl.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def create_calendar_frame(self):
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.header_label.config(text=f"{self.year}년 {self.month}월")
        cal = calendar.monthcalendar(self.year, self.month)

        for col in range(7):
            self.calendar_frame.columnconfigure(col, weight=1)

        row = 0
        today = datetime.date.today()

        for week in cal:
            self.calendar_frame.rowconfigure(row, weight=1)
            for col, day in enumerate(week):
                if day != 0:
                    date_key = f"{self.year}-{self.month:02d}-{day:02d}"
                    
                    display_text = f"{day}"
                    bg_color = "white"
                    fg_color = "black"
                    
                    if col == 0: fg_color = "red"
                    elif col == 6: fg_color = "blue"

                    if self.year == today.year and self.month == today.month and day == today.day:
                        bg_color = "#FFF59D" 
                        display_text += " [오늘]"

                    if date_key in self.schedule_data:
                        items = self.schedule_data[date_key]
                        count = 0
                        for item in items:
                            if count >= 3:
                                display_text += "\n..."
                                break
                            tag = "(주사)" if item.get('type') == 'injection' else "(예정)"
                            if item.get('type') == 'due':
                                bg_color = "#E1F5FE" if bg_color == "white" or bg_color == "#FFF59D" else bg_color

                            display_text += f"\n• {item['name']} {tag}"
                            count += 1

                    btn = tk.Button(
                        self.calendar_frame,
                        text=display_text,
                        bg=bg_color,
                        fg=fg_color,
                        justify=tk.LEFT,
                        anchor="nw",
                        font=("맑은 고딕", 9),
                        relief="solid",
                        borderwidth=1
                    )
                    btn.grid(row=row, column=col, sticky="nsew", padx=0, pady=0)
                    btn.bind("<Double-Button-1>", lambda event, d=day: self.open_input_dialog(d))

                else:
                    lbl = tk.Label(self.calendar_frame, bg="#F2F2F2")
                    lbl.grid(row=row, column=col, sticky="nsew")
            row += 1

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.draw_calendar()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.draw_calendar()

    def open_input_dialog(self, day):
        target_date = datetime.date(self.year, self.month, day)
        date_key = target_date.strftime("%Y-%m-%d")
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"기록 관리: {date_key}")
        dialog.geometry("450x650") # 높이를 늘림

        # === [섹션 1] 신규 입력 ===
        input_frame = tk.LabelFrame(dialog, text=" [신규 처방 입력] ", font=("맑은 고딕", 11, "bold"), padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text="환자명:", font=("맑은 고딕", 9)).grid(row=0, column=0, sticky="e", pady=5)
        name_entry = tk.Entry(input_frame, width=20)
        name_entry.grid(row=0, column=1, sticky="w", pady=5)
        name_entry.focus_set()

        tk.Label(input_frame, text="약품명:", font=("맑은 고딕", 9)).grid(row=1, column=0, sticky="e", pady=5)
        drug_names = list(DRUG_DATABASE.keys())
        drug_combo = ttk.Combobox(input_frame, values=drug_names, state="readonly", width=25)
        drug_combo.grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(input_frame, text="용량:", font=("맑은 고딕", 9)).grid(row=2, column=0, sticky="e", pady=5)
        dosage_combo = ttk.Combobox(input_frame, state="readonly", width=15)
        dosage_combo.grid(row=2, column=1, sticky="w", pady=5)

        def on_drug_select(event):
            selected_drug = drug_combo.get()
            dosages = DRUG_DATABASE.get(selected_drug, [])
            dosage_combo['values'] = dosages
            if dosages: dosage_combo.current(0)
            else: dosage_combo.set('')
        
        drug_combo.bind("<<ComboboxSelected>>", on_drug_select)
        drug_combo.current(0)
        on_drug_select(None)

        tk.Label(input_frame, text="간격(일):", font=("맑은 고딕", 9)).grid(row=3, column=0, sticky="e", pady=5)
        interval_entry = tk.Entry(input_frame, width=10)
        interval_entry.insert(0, "28")
        interval_entry.grid(row=3, column=1, sticky="w", pady=5)

        def save_action():
            name = name_entry.get().strip()
            drug = drug_combo.get()
            dosage = dosage_combo.get()
            
            if not name:
                messagebox.showwarning("오류", "환자명을 입력해주세요.")
                return
            try:
                interval = int(interval_entry.get())
            except ValueError:
                messagebox.showerror("오류", "간격은 숫자만 입력해주세요.")
                return

            start_date_str = date_key
            next_date = target_date + datetime.timedelta(days=interval)
            next_date_str = next_date.strftime("%Y-%m-%d")

            record_base = {
                "name": name,
                "drug": drug,
                "dosage": dosage,
                "interval": interval,
                "prescribed_date": start_date_str,
                "next_date": next_date_str
            }

            # 1. 오늘 주사 기록
            if start_date_str not in self.schedule_data: self.schedule_data[start_date_str] = []
            rec_inj = record_base.copy()
            rec_inj['type'] = 'injection'
            self.schedule_data[start_date_str].append(rec_inj)

            # 2. 다음 예정 기록
            if next_date_str not in self.schedule_data: self.schedule_data[next_date_str] = []
            rec_due = record_base.copy()
            rec_due['type'] = 'due'
            self.schedule_data[next_date_str].append(rec_due)

            self.save_data()
            messagebox.showinfo("성공", f"저장되었습니다.\n다음 예정일: {next_date_str}")
            dialog.destroy()
            self.draw_calendar()

        save_btn = tk.Button(input_frame, text="등록하기", command=save_action, bg="#4CAF50", fg="white", font=("맑은 고딕", 10, "bold"))
        save_btn.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)


        # === [섹션 2] 기록 확인 및 삭제 ===
        list_frame = tk.LabelFrame(dialog, text=f" [ {date_key} 기록 목록 ] ", font=("맑은 고딕", 11, "bold"), padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 스크롤바가 있는 리스트 영역
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 해당 날짜의 데이터 로드
        current_items = self.schedule_data.get(date_key, [])

        if not current_items:
            tk.Label(scrollable_frame, text="기록된 내역이 없습니다.", fg="gray").pack(pady=20)
        else:
            for idx, item in enumerate(current_items):
                # 개별 아이템 프레임
                item_frame = tk.Frame(scrollable_frame, relief="groove", borderwidth=1, pady=5)
                item_frame.pack(fill=tk.X, pady=2, padx=2)

                # 정보 표시 텍스트
                type_text = "[주사]" if item.get('type') == 'injection' else "[예정]"
                type_color = "blue" if item.get('type') == 'injection' else "red"
                
                info_text = f"{type_text} {item['name']}\n{item['drug']} ({item['dosage']})"
                
                lbl = tk.Label(item_frame, text=info_text, justify=tk.LEFT, fg=type_color, font=("맑은 고딕", 9))
                lbl.pack(side=tk.LEFT, padx=5)

                # 삭제 로직 함수
                def delete_item(index=idx):
                    if messagebox.askyesno("삭제 확인", "정말 이 기록을 삭제하시겠습니까?"):
                        # 데이터 삭제
                        del self.schedule_data[date_key][index]
                        # 리스트가 비었으면 키 자체를 제거
                        if not self.schedule_data[date_key]:
                            del self.schedule_data[date_key]
                        
                        self.save_data() # 저장
                        dialog.destroy() # 창 닫기 (새로고침 위해)
                        self.draw_calendar() # 캘린더 새로고침
                        self.open_input_dialog(day) # 창 다시 열기 (갱신된 목록 표시)

                # 삭제 버튼
                del_btn = tk.Button(item_frame, text="삭제", bg="#FFCDD2", command=delete_item)
                del_btn.pack(side=tk.RIGHT, padx=5)

    def start_notification_thread(self):
        t = threading.Thread(target=self.notification_loop, daemon=True)
        t.start()

    def notification_loop(self):
        self.check_and_notify()
        while True:
            now = datetime.datetime.now()
            if now.hour == 8 and now.minute == 30:
                self.check_and_notify()
                time.sleep(61)
            time.sleep(10)

    def check_and_notify(self):
        today = datetime.date.today()
        msgs = []
        for d in [0, 1, 2]:
            target_date = today + datetime.timedelta(days=d)
            target_str = target_date.strftime("%Y-%m-%d")
            
            if target_str in self.schedule_data:
                for item in self.schedule_data[target_str]:
                    if item.get('type') == 'due':
                        prefix = "[오늘]" if d == 0 else f"[{d}일 뒤]"
                        msgs.append(f"{prefix} {item['name']} ({item['drug']})")
        
        if msgs:
            toaster = ToastNotifier()
            full_msg = "\n".join(msgs)
            toaster.show_toast("LAI 주사 예정 알림", full_msg, duration=10, threaded=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = LAI_Scheduler_App(root)
=======
import tkinter as tk
from tkinter import ttk, messagebox
import calendar
import datetime
import json
import os
import threading
import time
from win10toast import ToastNotifier

# 데이터 저장 파일명
DATA_FILE = "lai_schedule_data_final.json"

# 약품 및 용량 데이터베이스
DRUG_DATABASE = {
    "아빌리파이 메인테나": ["300mg", "400mg"],
    "아빌리파이 아심투파이": ["720mg", "960mg"],
    "인베가 서스티나": ["78mg", "117mg", "156mg", "234mg"],
    "인베가 트린자": ["273mg", "410mg", "546mg", "819mg"],
    "인베가 하피에라": ["1092mg", "1560mg"]
}

class LAI_Scheduler_App:
    def __init__(self, root):
        self.root = root
        self.root.title("LAI 처방 스케줄러 (Dr. Final Ver.)")
        self.root.geometry("1100x900") # 화면을 조금 더 길게 늘렸습니다 (삭제 목록 공간 확보)

        # 현재 날짜 기준 설정
        self.current_date = datetime.date.today()
        self.year = self.current_date.year
        self.month = self.current_date.month

        # 데이터 로드
        self.schedule_data = self.load_data()

        # UI 구성
        self.create_header()
        self.create_calendar_frame()
        self.draw_calendar()
        
        # 단축키 바인딩 (F1 누르면 오늘 날짜 입력)
        self.root.bind("<F1>", lambda event: self.open_input_dialog(self.current_date.day))

        # 백그라운드 알림 스레드 시작
        self.start_notification_thread()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.schedule_data, f, ensure_ascii=False, indent=4)

    def create_header(self):
        nav_frame = tk.Frame(self.root, pady=10)
        nav_frame.pack(fill=tk.X)

        prev_btn = tk.Button(nav_frame, text="◀ 이전 달", command=self.prev_month, font=("맑은 고딕", 10))
        prev_btn.pack(side=tk.LEFT, padx=20)

        self.header_label = tk.Label(nav_frame, text=f"{self.year}년 {self.month}월", font=("맑은 고딕", 20, "bold"))
        self.header_label.pack(side=tk.LEFT, expand=True)

        next_btn = tk.Button(nav_frame, text="다음 달 ▶", command=self.next_month, font=("맑은 고딕", 10))
        next_btn.pack(side=tk.LEFT, padx=20)

        days_frame = tk.Frame(self.root)
        days_frame.pack(fill=tk.X, padx=10)
        days = ["일", "월", "화", "수", "목", "금", "토"]
        for i, day in enumerate(days):
            color = "red" if i == 0 else "blue" if i == 6 else "black"
            lbl = tk.Label(days_frame, text=day, font=("맑은 고딕", 11, "bold"), fg=color, width=14, relief="flat")
            lbl.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def create_calendar_frame(self):
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.header_label.config(text=f"{self.year}년 {self.month}월")
        cal = calendar.monthcalendar(self.year, self.month)

        for col in range(7):
            self.calendar_frame.columnconfigure(col, weight=1)

        row = 0
        today = datetime.date.today()

        for week in cal:
            self.calendar_frame.rowconfigure(row, weight=1)
            for col, day in enumerate(week):
                if day != 0:
                    date_key = f"{self.year}-{self.month:02d}-{day:02d}"
                    
                    display_text = f"{day}"
                    bg_color = "white"
                    fg_color = "black"
                    
                    if col == 0: fg_color = "red"
                    elif col == 6: fg_color = "blue"

                    if self.year == today.year and self.month == today.month and day == today.day:
                        bg_color = "#FFF59D" 
                        display_text += " [오늘]"

                    if date_key in self.schedule_data:
                        items = self.schedule_data[date_key]
                        count = 0
                        for item in items:
                            if count >= 3:
                                display_text += "\n..."
                                break
                            tag = "(주사)" if item.get('type') == 'injection' else "(예정)"
                            if item.get('type') == 'due':
                                bg_color = "#E1F5FE" if bg_color == "white" or bg_color == "#FFF59D" else bg_color

                            display_text += f"\n• {item['name']} {tag}"
                            count += 1

                    btn = tk.Button(
                        self.calendar_frame,
                        text=display_text,
                        bg=bg_color,
                        fg=fg_color,
                        justify=tk.LEFT,
                        anchor="nw",
                        font=("맑은 고딕", 9),
                        relief="solid",
                        borderwidth=1
                    )
                    btn.grid(row=row, column=col, sticky="nsew", padx=0, pady=0)
                    btn.bind("<Double-Button-1>", lambda event, d=day: self.open_input_dialog(d))

                else:
                    lbl = tk.Label(self.calendar_frame, bg="#F2F2F2")
                    lbl.grid(row=row, column=col, sticky="nsew")
            row += 1

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.draw_calendar()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.draw_calendar()

    def open_input_dialog(self, day):
        target_date = datetime.date(self.year, self.month, day)
        date_key = target_date.strftime("%Y-%m-%d")
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"기록 관리: {date_key}")
        dialog.geometry("450x650") # 높이를 늘림

        # === [섹션 1] 신규 입력 ===
        input_frame = tk.LabelFrame(dialog, text=" [신규 처방 입력] ", font=("맑은 고딕", 11, "bold"), padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text="환자명:", font=("맑은 고딕", 9)).grid(row=0, column=0, sticky="e", pady=5)
        name_entry = tk.Entry(input_frame, width=20)
        name_entry.grid(row=0, column=1, sticky="w", pady=5)
        name_entry.focus_set()

        tk.Label(input_frame, text="약품명:", font=("맑은 고딕", 9)).grid(row=1, column=0, sticky="e", pady=5)
        drug_names = list(DRUG_DATABASE.keys())
        drug_combo = ttk.Combobox(input_frame, values=drug_names, state="readonly", width=25)
        drug_combo.grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(input_frame, text="용량:", font=("맑은 고딕", 9)).grid(row=2, column=0, sticky="e", pady=5)
        dosage_combo = ttk.Combobox(input_frame, state="readonly", width=15)
        dosage_combo.grid(row=2, column=1, sticky="w", pady=5)

        def on_drug_select(event):
            selected_drug = drug_combo.get()
            dosages = DRUG_DATABASE.get(selected_drug, [])
            dosage_combo['values'] = dosages
            if dosages: dosage_combo.current(0)
            else: dosage_combo.set('')
        
        drug_combo.bind("<<ComboboxSelected>>", on_drug_select)
        drug_combo.current(0)
        on_drug_select(None)

        tk.Label(input_frame, text="간격(일):", font=("맑은 고딕", 9)).grid(row=3, column=0, sticky="e", pady=5)
        interval_entry = tk.Entry(input_frame, width=10)
        interval_entry.insert(0, "28")
        interval_entry.grid(row=3, column=1, sticky="w", pady=5)

        def save_action():
            name = name_entry.get().strip()
            drug = drug_combo.get()
            dosage = dosage_combo.get()
            
            if not name:
                messagebox.showwarning("오류", "환자명을 입력해주세요.")
                return
            try:
                interval = int(interval_entry.get())
            except ValueError:
                messagebox.showerror("오류", "간격은 숫자만 입력해주세요.")
                return

            start_date_str = date_key
            next_date = target_date + datetime.timedelta(days=interval)
            next_date_str = next_date.strftime("%Y-%m-%d")

            record_base = {
                "name": name,
                "drug": drug,
                "dosage": dosage,
                "interval": interval,
                "prescribed_date": start_date_str,
                "next_date": next_date_str
            }

            # 1. 오늘 주사 기록
            if start_date_str not in self.schedule_data: self.schedule_data[start_date_str] = []
            rec_inj = record_base.copy()
            rec_inj['type'] = 'injection'
            self.schedule_data[start_date_str].append(rec_inj)

            # 2. 다음 예정 기록
            if next_date_str not in self.schedule_data: self.schedule_data[next_date_str] = []
            rec_due = record_base.copy()
            rec_due['type'] = 'due'
            self.schedule_data[next_date_str].append(rec_due)

            self.save_data()
            messagebox.showinfo("성공", f"저장되었습니다.\n다음 예정일: {next_date_str}")
            dialog.destroy()
            self.draw_calendar()

        save_btn = tk.Button(input_frame, text="등록하기", command=save_action, bg="#4CAF50", fg="white", font=("맑은 고딕", 10, "bold"))
        save_btn.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)


        # === [섹션 2] 기록 확인 및 삭제 ===
        list_frame = tk.LabelFrame(dialog, text=f" [ {date_key} 기록 목록 ] ", font=("맑은 고딕", 11, "bold"), padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 스크롤바가 있는 리스트 영역
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 해당 날짜의 데이터 로드
        current_items = self.schedule_data.get(date_key, [])

        if not current_items:
            tk.Label(scrollable_frame, text="기록된 내역이 없습니다.", fg="gray").pack(pady=20)
        else:
            for idx, item in enumerate(current_items):
                # 개별 아이템 프레임
                item_frame = tk.Frame(scrollable_frame, relief="groove", borderwidth=1, pady=5)
                item_frame.pack(fill=tk.X, pady=2, padx=2)

                # 정보 표시 텍스트
                type_text = "[주사]" if item.get('type') == 'injection' else "[예정]"
                type_color = "blue" if item.get('type') == 'injection' else "red"
                
                info_text = f"{type_text} {item['name']}\n{item['drug']} ({item['dosage']})"
                
                lbl = tk.Label(item_frame, text=info_text, justify=tk.LEFT, fg=type_color, font=("맑은 고딕", 9))
                lbl.pack(side=tk.LEFT, padx=5)

                # 삭제 로직 함수
                def delete_item(index=idx):
                    if messagebox.askyesno("삭제 확인", "정말 이 기록을 삭제하시겠습니까?"):
                        # 데이터 삭제
                        del self.schedule_data[date_key][index]
                        # 리스트가 비었으면 키 자체를 제거
                        if not self.schedule_data[date_key]:
                            del self.schedule_data[date_key]
                        
                        self.save_data() # 저장
                        dialog.destroy() # 창 닫기 (새로고침 위해)
                        self.draw_calendar() # 캘린더 새로고침
                        self.open_input_dialog(day) # 창 다시 열기 (갱신된 목록 표시)

                # 삭제 버튼
                del_btn = tk.Button(item_frame, text="삭제", bg="#FFCDD2", command=delete_item)
                del_btn.pack(side=tk.RIGHT, padx=5)

    def start_notification_thread(self):
        t = threading.Thread(target=self.notification_loop, daemon=True)
        t.start()

    def notification_loop(self):
        self.check_and_notify()
        while True:
            now = datetime.datetime.now()
            if now.hour == 8 and now.minute == 30:
                self.check_and_notify()
                time.sleep(61)
            time.sleep(10)

    def check_and_notify(self):
        today = datetime.date.today()
        msgs = []
        for d in [0, 1, 2]:
            target_date = today + datetime.timedelta(days=d)
            target_str = target_date.strftime("%Y-%m-%d")
            
            if target_str in self.schedule_data:
                for item in self.schedule_data[target_str]:
                    if item.get('type') == 'due':
                        prefix = "[오늘]" if d == 0 else f"[{d}일 뒤]"
                        msgs.append(f"{prefix} {item['name']} ({item['drug']})")
        
        if msgs:
            toaster = ToastNotifier()
            full_msg = "\n".join(msgs)
            toaster.show_toast("LAI 주사 예정 알림", full_msg, duration=10, threaded=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = LAI_Scheduler_App(root)
>>>>>>> dfa05a198f5cb127863523e0f9695e87d86e3324
    root.mainloop()