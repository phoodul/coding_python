<<<<<<< HEAD
import tkinter as tk
from tkinter import ttk, messagebox
import calendar
import datetime
import json
import os
import threading
from win10toast import ToastNotifier # 알림 기능을 위해 필요 (pip install win10toast)

# 데이터 저장 파일명
DATA_FILE = "lai_schedule_data.json"

class LAI_Scheduler_App:
    def __init__(self, root):
        self.root = root
        self.root.title("LAI 처방 스케줄러 (Dr. Ver.)")
        self.root.geometry("1000x800") # 화면 크기를 넉넉하게 잡았습니다.

        # 현재 날짜 기준 설정
        self.current_date = datetime.date.today()
        self.year = self.current_date.year
        self.month = self.current_date.month

        # 데이터 로드
        self.schedule_data = self.load_data()

        # UI 구성
        self.create_widgets()
        
        # 캘린더 그리기
        self.draw_calendar()
        
        # 프로그램 시작 시 알림 체크 (백그라운드 실행)
        self.check_notifications()

    def load_data(self):
        """저장된 JSON 데이터를 불러옵니다."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_data(self):
        """데이터를 JSON 파일로 저장합니다."""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.schedule_data, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        """상단 네비게이션과 요일 헤더를 만듭니다."""
        # 상단 년/월 표시 및 이동 버튼 프레임
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10)

        prev_btn = tk.Button(nav_frame, text="< 이전 달", command=self.prev_month)
        prev_btn.pack(side=tk.LEFT, padx=20)

        self.header_label = tk.Label(nav_frame, text=f"{self.year}년 {self.month}월", font=("Arial", 18, "bold"))
        self.header_label.pack(side=tk.LEFT, padx=20)

        next_btn = tk.Button(nav_frame, text="다음 달 >", command=self.next_month)
        next_btn.pack(side=tk.LEFT, padx=20)

        # 요일 표시 (일 ~ 토)
        days_frame = tk.Frame(self.root)
        days_frame.pack(fill=tk.X, padx=10)
        days = ["일", "월", "화", "수", "목", "금", "토"]
        for i, day in enumerate(days):
            color = "red" if i == 0 else "blue" if i == 6 else "black"
            lbl = tk.Label(days_frame, text=day, font=("Arial", 12, "bold"), fg=color, width=14)
            lbl.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # 캘린더 날짜들이 들어갈 메인 프레임
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

    def draw_calendar(self):
        """현재 년/월에 맞는 달력을 그립니다."""
        # 기존 캘린더 버튼들 지우기
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.header_label.config(text=f"{self.year}년 {self.month}월")

        # 달력 매트릭스 가져오기 (해당 월의 날짜 배열)
        cal = calendar.monthcalendar(self.year, self.month)

        # 그리드 설정 (7열)
        for col in range(7):
            self.calendar_frame.columnconfigure(col, weight=1)

        row = 0
        for week in cal:
            self.calendar_frame.rowconfigure(row, weight=1)
            for col, day in enumerate(week):
                if day != 0:
                    # 날짜 키 생성 (YYYY-MM-DD)
                    date_key = f"{self.year}-{self.month:02d}-{self.day_str(day)}"
                    
                    # 해당 날짜에 예약된 환자 찾기
                    patients_text = f"{day}" # 기본은 날짜 숫자만
                    bg_color = "white"
                    
                    if date_key in self.schedule_data:
                        # 데이터가 있으면 환자 이름을 버튼 텍스트에 추가
                        names = [item['name'] for item in self.schedule_data[date_key]]
                        # 칸이 좁으니 최대 3명까지만 보여주고 ... 처리
                        display_names = "\n".join(names[:3]) 
                        if len(names) > 3: display_names += "\n..."
                        patients_text += f"\n\n{display_names}"
                        bg_color = "#E0F7FA" # 예약 있는 날은 연하늘색 배경

                    # 오늘 날짜 강조
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    if date_key == today_str:
                        bg_color = "#FFEBEE" # 오늘은 연분홍색

                    # 버튼 생성 (여기서 날짜별 버튼을 만듭니다)
                    btn = tk.Button(
                        self.calendar_frame, 
                        text=patients_text, 
                        bg=bg_color, 
                        justify=tk.LEFT, 
                        anchor="nw", # 텍스트 왼쪽 상단 정렬
                        font=("Arial", 10),
                        relief="ridge",
                        borderwidth=2
                    )
                    btn.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

                    # [핵심 수정 1] 마우스 좌측 더블클릭 이벤트 바인딩
                    # lambda를 사용하여 클릭된 날짜 정보를 전달
                    btn.bind("<Double-Button-1>", lambda event, d=day: self.open_input_dialog(d))
                
                else:
                    # 날짜가 없는 빈 칸 (이전달/다음달 여백)
                    lbl = tk.Label(self.calendar_frame, bg="#f0f0f0")
                    lbl.grid(row=row, column=col, sticky="nsew")
            
            row += 1

    def day_str(self, day):
        """숫자 날짜를 두 자리 문자열로 변환 (예: 5 -> '05')"""
        return f"{day:02d}"

    def prev_month(self):
        """이전 달로 이동"""
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.draw_calendar()

    def next_month(self):
        """다음 달로 이동"""
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.draw_calendar()

    def open_input_dialog(self, day):
        """입력 팝업창을 엽니다."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{self.year}-{self.month}-{day} 처방 입력")
        dialog.geometry("400x450")

        # 입력 필드 구성
        tk.Label(dialog, text="환자명:").pack(pady=5)
        name_entry = tk.Entry(dialog)
        name_entry.pack(pady=5)
        name_entry.focus_set() # 창 열리면 바로 이름 입력 가능하게 포커스

        tk.Label(dialog, text="약품명:").pack(pady=5)
        # 약품 리스트 (필요에 따라 수정하세요)
        drug_list = ["Invega Trinza", "Xeplion", "Abilify Maintena", "Risperdal Consta"]
        drug_combobox = ttk.Combobox(dialog, values=drug_list)
        drug_combobox.pack(pady=5)
        drug_combobox.current(0)

        tk.Label(dialog, text="용량:").pack(pady=5)
        dosage_list = ["50mg", "75mg", "100mg", "150mg", "200mg", "300mg", "400mg", "525mg"]
        dosage_combobox = ttk.Combobox(dialog, values=dosage_list)
        dosage_combobox.pack(pady=5)

        tk.Label(dialog, text="주사 간격 (일 단위):").pack(pady=5)
        interval_entry = tk.Entry(dialog)
        interval_entry.insert(0, "28") # 기본값 4주
        interval_entry.pack(pady=5)

        # [저장 버튼 로직]
        def save():
            name = name_entry.get()
            if not name:
                messagebox.showwarning("경고", "환자명을 입력해주세요.")
                return
            
            try:
                interval = int(interval_entry.get())
            except ValueError:
                messagebox.showerror("오류", "주사 간격은 숫자만 입력해주세요.")
                return

            # 처방일(선택한 날짜)
            prescribed_date = datetime.date(self.year, self.month, day)
            # 다음 예정일 계산 (핵심 로직)
            next_date = prescribed_date + datetime.timedelta(days=interval)
            next_date_str = next_date.strftime("%Y-%m-%d")

            # 데이터 구조: { "2023-12-20": [ {정보1}, {정보2} ], ... }
            if next_date_str not in self.schedule_data:
                self.schedule_data[next_date_str] = []
            
            record = {
                "name": name,
                "drug": drug_combobox.get(),
                "dosage": dosage_combobox.get(),
                "prescribed_date": prescribed_date.strftime("%Y-%m-%d"),
                "interval": interval
            }
            
            self.schedule_data[next_date_str].append(record)
            self.save_data()
            
            messagebox.showinfo("저장 완료", f"다음 주사 예정일({next_date_str})에 등록되었습니다.")
            dialog.destroy()
            
            # 캘린더 새로고침 (이름이 화면에 즉시 반영되도록)
            self.draw_calendar()

        tk.Button(dialog, text="저장", command=save, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20, fill=tk.X, padx=20)
        
        # [해당 날짜 예약 확인 기능] - 팝업 하단에 리스트 표시
        selected_date_key = f"{self.year}-{self.month:02d}-{self.day_str(day)}"
        if selected_date_key in self.schedule_data:
            tk.Label(dialog, text="[금일 예약 명단]", fg="blue", font=("bold")).pack(pady=10)
            for item in self.schedule_data[selected_date_key]:
                info = f"- {item['name']} ({item['drug']} {item['dosage']})"
                tk.Label(dialog, text=info).pack()

    def check_notifications(self):
        """알림 로직: 오늘 기준으로 D-Day, D-1, D-2 환자 찾기"""
        today = datetime.date.today()
        alert_messages = []

        # 0일(당일), 1일전, 2일전 체크
        for days_left in [0, 1, 2]:
            target_date = today + datetime.timedelta(days=days_left)
            target_str = target_date.strftime("%Y-%m-%d")
            
            if target_str in self.schedule_data:
                for item in self.schedule_data[target_str]:
                    msg = ""
                    if days_left == 0: msg = f"[오늘] {item['name']}님 주사 예정"
                    elif days_left == 1: msg = f"[내일] {item['name']}님 주사 예정"
                    elif days_left == 2: msg = f"[모레] {item['name']}님 주사 예정"
                    alert_messages.append(msg)
        
        # 알림이 있다면 윈도우 토스트 메시지 띄우기
        if alert_messages:
            toaster = ToastNotifier()
            full_msg = "\n".join(alert_messages)
            # 스레드로 실행하여 UI 멈춤 방지
            t = threading.Thread(target=toaster.show_toast, args=("LAI 처방 알림", full_msg, None, 10))
            t.start()
        else:
            print("오늘 예정된 알림이 없습니다.")

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
from win10toast import ToastNotifier # 알림 기능을 위해 필요 (pip install win10toast)

# 데이터 저장 파일명
DATA_FILE = "lai_schedule_data.json"

class LAI_Scheduler_App:
    def __init__(self, root):
        self.root = root
        self.root.title("LAI 처방 스케줄러 (Dr. Ver.)")
        self.root.geometry("1000x800") # 화면 크기를 넉넉하게 잡았습니다.

        # 현재 날짜 기준 설정
        self.current_date = datetime.date.today()
        self.year = self.current_date.year
        self.month = self.current_date.month

        # 데이터 로드
        self.schedule_data = self.load_data()

        # UI 구성
        self.create_widgets()
        
        # 캘린더 그리기
        self.draw_calendar()
        
        # 프로그램 시작 시 알림 체크 (백그라운드 실행)
        self.check_notifications()

    def load_data(self):
        """저장된 JSON 데이터를 불러옵니다."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_data(self):
        """데이터를 JSON 파일로 저장합니다."""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.schedule_data, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        """상단 네비게이션과 요일 헤더를 만듭니다."""
        # 상단 년/월 표시 및 이동 버튼 프레임
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10)

        prev_btn = tk.Button(nav_frame, text="< 이전 달", command=self.prev_month)
        prev_btn.pack(side=tk.LEFT, padx=20)

        self.header_label = tk.Label(nav_frame, text=f"{self.year}년 {self.month}월", font=("Arial", 18, "bold"))
        self.header_label.pack(side=tk.LEFT, padx=20)

        next_btn = tk.Button(nav_frame, text="다음 달 >", command=self.next_month)
        next_btn.pack(side=tk.LEFT, padx=20)

        # 요일 표시 (일 ~ 토)
        days_frame = tk.Frame(self.root)
        days_frame.pack(fill=tk.X, padx=10)
        days = ["일", "월", "화", "수", "목", "금", "토"]
        for i, day in enumerate(days):
            color = "red" if i == 0 else "blue" if i == 6 else "black"
            lbl = tk.Label(days_frame, text=day, font=("Arial", 12, "bold"), fg=color, width=14)
            lbl.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # 캘린더 날짜들이 들어갈 메인 프레임
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

    def draw_calendar(self):
        """현재 년/월에 맞는 달력을 그립니다."""
        # 기존 캘린더 버튼들 지우기
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.header_label.config(text=f"{self.year}년 {self.month}월")

        # 달력 매트릭스 가져오기 (해당 월의 날짜 배열)
        cal = calendar.monthcalendar(self.year, self.month)

        # 그리드 설정 (7열)
        for col in range(7):
            self.calendar_frame.columnconfigure(col, weight=1)

        row = 0
        for week in cal:
            self.calendar_frame.rowconfigure(row, weight=1)
            for col, day in enumerate(week):
                if day != 0:
                    # 날짜 키 생성 (YYYY-MM-DD)
                    date_key = f"{self.year}-{self.month:02d}-{self.day_str(day)}"
                    
                    # 해당 날짜에 예약된 환자 찾기
                    patients_text = f"{day}" # 기본은 날짜 숫자만
                    bg_color = "white"
                    
                    if date_key in self.schedule_data:
                        # 데이터가 있으면 환자 이름을 버튼 텍스트에 추가
                        names = [item['name'] for item in self.schedule_data[date_key]]
                        # 칸이 좁으니 최대 3명까지만 보여주고 ... 처리
                        display_names = "\n".join(names[:3]) 
                        if len(names) > 3: display_names += "\n..."
                        patients_text += f"\n\n{display_names}"
                        bg_color = "#E0F7FA" # 예약 있는 날은 연하늘색 배경

                    # 오늘 날짜 강조
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    if date_key == today_str:
                        bg_color = "#FFEBEE" # 오늘은 연분홍색

                    # 버튼 생성 (여기서 날짜별 버튼을 만듭니다)
                    btn = tk.Button(
                        self.calendar_frame, 
                        text=patients_text, 
                        bg=bg_color, 
                        justify=tk.LEFT, 
                        anchor="nw", # 텍스트 왼쪽 상단 정렬
                        font=("Arial", 10),
                        relief="ridge",
                        borderwidth=2
                    )
                    btn.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

                    # [핵심 수정 1] 마우스 좌측 더블클릭 이벤트 바인딩
                    # lambda를 사용하여 클릭된 날짜 정보를 전달
                    btn.bind("<Double-Button-1>", lambda event, d=day: self.open_input_dialog(d))
                
                else:
                    # 날짜가 없는 빈 칸 (이전달/다음달 여백)
                    lbl = tk.Label(self.calendar_frame, bg="#f0f0f0")
                    lbl.grid(row=row, column=col, sticky="nsew")
            
            row += 1

    def day_str(self, day):
        """숫자 날짜를 두 자리 문자열로 변환 (예: 5 -> '05')"""
        return f"{day:02d}"

    def prev_month(self):
        """이전 달로 이동"""
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.draw_calendar()

    def next_month(self):
        """다음 달로 이동"""
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.draw_calendar()

    def open_input_dialog(self, day):
        """입력 팝업창을 엽니다."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{self.year}-{self.month}-{day} 처방 입력")
        dialog.geometry("400x450")

        # 입력 필드 구성
        tk.Label(dialog, text="환자명:").pack(pady=5)
        name_entry = tk.Entry(dialog)
        name_entry.pack(pady=5)
        name_entry.focus_set() # 창 열리면 바로 이름 입력 가능하게 포커스

        tk.Label(dialog, text="약품명:").pack(pady=5)
        # 약품 리스트 (필요에 따라 수정하세요)
        drug_list = ["Invega Trinza", "Xeplion", "Abilify Maintena", "Risperdal Consta"]
        drug_combobox = ttk.Combobox(dialog, values=drug_list)
        drug_combobox.pack(pady=5)
        drug_combobox.current(0)

        tk.Label(dialog, text="용량:").pack(pady=5)
        dosage_list = ["50mg", "75mg", "100mg", "150mg", "200mg", "300mg", "400mg", "525mg"]
        dosage_combobox = ttk.Combobox(dialog, values=dosage_list)
        dosage_combobox.pack(pady=5)

        tk.Label(dialog, text="주사 간격 (일 단위):").pack(pady=5)
        interval_entry = tk.Entry(dialog)
        interval_entry.insert(0, "28") # 기본값 4주
        interval_entry.pack(pady=5)

        # [저장 버튼 로직]
        def save():
            name = name_entry.get()
            if not name:
                messagebox.showwarning("경고", "환자명을 입력해주세요.")
                return
            
            try:
                interval = int(interval_entry.get())
            except ValueError:
                messagebox.showerror("오류", "주사 간격은 숫자만 입력해주세요.")
                return

            # 처방일(선택한 날짜)
            prescribed_date = datetime.date(self.year, self.month, day)
            # 다음 예정일 계산 (핵심 로직)
            next_date = prescribed_date + datetime.timedelta(days=interval)
            next_date_str = next_date.strftime("%Y-%m-%d")

            # 데이터 구조: { "2023-12-20": [ {정보1}, {정보2} ], ... }
            if next_date_str not in self.schedule_data:
                self.schedule_data[next_date_str] = []
            
            record = {
                "name": name,
                "drug": drug_combobox.get(),
                "dosage": dosage_combobox.get(),
                "prescribed_date": prescribed_date.strftime("%Y-%m-%d"),
                "interval": interval
            }
            
            self.schedule_data[next_date_str].append(record)
            self.save_data()
            
            messagebox.showinfo("저장 완료", f"다음 주사 예정일({next_date_str})에 등록되었습니다.")
            dialog.destroy()
            
            # 캘린더 새로고침 (이름이 화면에 즉시 반영되도록)
            self.draw_calendar()

        tk.Button(dialog, text="저장", command=save, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20, fill=tk.X, padx=20)
        
        # [해당 날짜 예약 확인 기능] - 팝업 하단에 리스트 표시
        selected_date_key = f"{self.year}-{self.month:02d}-{self.day_str(day)}"
        if selected_date_key in self.schedule_data:
            tk.Label(dialog, text="[금일 예약 명단]", fg="blue", font=("bold")).pack(pady=10)
            for item in self.schedule_data[selected_date_key]:
                info = f"- {item['name']} ({item['drug']} {item['dosage']})"
                tk.Label(dialog, text=info).pack()

    def check_notifications(self):
        """알림 로직: 오늘 기준으로 D-Day, D-1, D-2 환자 찾기"""
        today = datetime.date.today()
        alert_messages = []

        # 0일(당일), 1일전, 2일전 체크
        for days_left in [0, 1, 2]:
            target_date = today + datetime.timedelta(days=days_left)
            target_str = target_date.strftime("%Y-%m-%d")
            
            if target_str in self.schedule_data:
                for item in self.schedule_data[target_str]:
                    msg = ""
                    if days_left == 0: msg = f"[오늘] {item['name']}님 주사 예정"
                    elif days_left == 1: msg = f"[내일] {item['name']}님 주사 예정"
                    elif days_left == 2: msg = f"[모레] {item['name']}님 주사 예정"
                    alert_messages.append(msg)
        
        # 알림이 있다면 윈도우 토스트 메시지 띄우기
        if alert_messages:
            toaster = ToastNotifier()
            full_msg = "\n".join(alert_messages)
            # 스레드로 실행하여 UI 멈춤 방지
            t = threading.Thread(target=toaster.show_toast, args=("LAI 처방 알림", full_msg, None, 10))
            t.start()
        else:
            print("오늘 예정된 알림이 없습니다.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LAI_Scheduler_App(root)
>>>>>>> dfa05a198f5cb127863523e0f9695e87d86e3324
    root.mainloop()