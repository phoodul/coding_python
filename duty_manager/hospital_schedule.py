<<<<<<< HEAD
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import calendar
import random
import csv

# ==========================================
# 1. 기초 데이터 및 설정
# ==========================================

YEAR = 2025
MONTH = 12
DAYS_IN_MONTH = 31

# 직원 데이터 매핑 (번호: [이름, 병동, 직종])
# 30~35: 3병동 간호사 / 36~39: 3병동 보호사
# 40~45: 4병동 간호사 / 46~49: 4병동 보호사
# 50~55: 5병동 간호사 / 56~59: 5병동 보호사

EMPLOYEES = {}

# 이름 생성 도우미 (임시 이름)
def generate_name(idx, role):
    last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]
    first_names = ["서연", "민준", "지우", "서현", "민재", "하윤", "건우", "예준", "현우", "지민"]
    return f"{random.choice(last_names)}{random.choice(first_names)}"

# 3병동
for i in range(30, 36): EMPLOYEES[i] = {"name": generate_name(i, "간호"), "ward": "3W", "job": "RN"}
for i in range(36, 40): EMPLOYEES[i] = {"name": generate_name(i, "보호"), "ward": "3W", "job": "AN"} # Caregiver
# 4병동
for i in range(40, 46): EMPLOYEES[i] = {"name": generate_name(i, "간호"), "ward": "4W", "job": "RN"}
for i in range(46, 50): EMPLOYEES[i] = {"name": generate_name(i, "보호"), "ward": "4W", "job": "AN"}
# 5병동
for i in range(50, 56): EMPLOYEES[i] = {"name": generate_name(i, "간호"), "ward": "5W", "job": "RN"}
for i in range(56, 60): EMPLOYEES[i] = {"name": generate_name(i, "보호"), "ward": "5W", "job": "AN"}

# 근무 타입 정의
SHIFTS_RN = ["D", "E", "N", "M", "O", "D5", "n5"]
SHIFTS_AN = ["D", "N", "O"]

# ==========================================
# 2. 로직 클래스 (알고리즘)
# ==========================================

class SchedulerLogic:
    def __init__(self):
        # 데이터 저장소
        # self.schedule[emp_id] = [prev_5_days..., day1, day2, ..., day31]
        self.schedule = {} 
        self.targets = {} # {emp_id: {'D': 5, 'E': 5, ...}}
        
        # 초기화
        for eid in EMPLOYEES:
            # 전월 5일 + 당월 31일 = 총 36개 슬롯
            self.schedule[eid] = [""] * (5 + DAYS_IN_MONTH)
            # 전월 데이터는 랜덤하게 채움 (실제로는 입력받아야 함)
            for k in range(5):
                self.schedule[eid][k] = random.choice(["D", "E", "N", "O"])
            
            # 목표 개수 초기화 (기본값 0: 제한 없음 의미)
            self.targets[eid] = {"D": 0, "E": 0, "N": 0, "M": 0, "O": 0}

    def check_validity(self, schedule_list, day_idx, shift_type, job_type):
        """특정 날짜에 특정 근무를 넣을 때 규칙 위반 여부 확인"""
        # 인덱스 보정 (0~4는 전월, 5가 1일)
        current_idx = day_idx
        
        # 1. 근무 타입 유효성
        if job_type == "AN" and shift_type not in ["D", "N", "O"]:
            return False

        # 2. N 근무 연속 3일 초과 불가
        if shift_type == "N":
            consecutive_n = 0
            for k in range(1, 4):
                if current_idx - k >= 0 and schedule_list[current_idx - k] == "N":
                    consecutive_n += 1
                else:
                    break
            if consecutive_n >= 3:
                return False

        # 3. 연속 근무 5일 초과 불가 (6일째는 반드시 O)
        if shift_type != "O":
            consecutive_work = 0
            for k in range(1, 6):
                if current_idx - k >= 0 and schedule_list[current_idx - k] != "O":
                    consecutive_work += 1
                else:
                    break
            if consecutive_work >= 5:
                return False

        # 4. N -> D/E 전환 시 반드시 O 필요 (N 다음날 D/E/M 불가)
        prev_shift = schedule_list[current_idx - 1] if current_idx > 0 else "O"
        if "N" in prev_shift and shift_type in ["D", "E", "M", "D5"]:
            return False

        return True

    def auto_fill(self):
        """자동 완성 알고리즘 (백트래킹/그리디 혼합)"""
        # 간단한 전략: 빈칸인 날짜에 대해 가능한 근무 중 하나를 선택
        # 공정성을 위해 타겟 카운트 고려
        
        for eid, info in EMPLOYEES.items():
            current_schedule = self.schedule[eid]
            job = info['job']
            possible_shifts = SHIFTS_RN if job == "RN" else SHIFTS_AN
            
            # 당월 1일부터 말일까지 순회 (인덱스 5 ~ 35)
            for day in range(5, 5 + DAYS_IN_MONTH):
                if current_schedule[day].strip() != "":
                    continue # 이미 입력된 값은 패스

                valid_options = []
                for s in possible_shifts:
                    if self.check_validity(current_schedule, day, s, job):
                        valid_options.append(s)
                
                if not valid_options:
                    current_schedule[day] = "O" # 갈 곳 없으면 오프
                else:
                    # 타겟 카운트를 고려하여 가중치 부여 (간단 구현: 랜덤)
                    # 실제로는 부족한 근무를 우선 배정하는 로직이 들어감
                    
                    # 2-5일 연속 근무 선호 로직
                    prev = current_schedule[day-1]
                    if prev in valid_options and prev != "O":
                        # 연속 근무 확률 높임
                        if random.random() < 0.7: 
                            current_schedule[day] = prev
                            continue

                    current_schedule[day] = random.choice(valid_options)

    def count_shifts(self, eid):
        """특정 직원의 당월 근무 개수 집계"""
        counts = {"D": 0, "E": 0, "N": 0, "M": 0, "O": 0, "Total": 0}
        # 인덱스 5부터 끝까지 (당월)
        month_schedule = self.schedule[eid][5:]
        
        for s in month_schedule:
            base_s = s[0] if len(s) > 0 else "" # D5 -> D, n5 -> n
            if "D" in s: counts["D"] += 1
            elif "E" in s: counts["E"] += 1
            elif "N" in s or "n" in s: counts["N"] += 1
            elif "M" in s: counts["M"] += 1
            elif "O" in s: counts["O"] += 1
        
        counts["Total"] = counts["D"] + counts["E"] + counts["N"] + counts["M"]
        return counts

# ==========================================
# 3. GUI 클래스
# ==========================================

class HospitalScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("나눔과행복병원 간호부 근무표 생성기 v9.8")
        self.root.geometry("1600x900")
        
        self.logic = SchedulerLogic()
        self.entries_table2 = {} # (eid, day) -> Entry Widget
        self.entries_table1 = {} # (eid, type) -> Entry Widget
        
        # 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", tabposition='n')
        
        # 메인 탭 컨테이너
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 탭 생성
        self.tab1 = ttk.Frame(self.notebook) # 설정 (Table 1)
        self.tab2 = ttk.Frame(self.notebook) # 캘린더 (Table 2)
        self.tab3 = ttk.Frame(self.notebook) # 일별 명단 (Table 3)
        
        self.notebook.add(self.tab2, text=" [Table 2] 월간 근무표 (메인) ")
        self.notebook.add(self.tab1, text=" [Table 1] 근무 개수 설정 ")
        self.notebook.add(self.tab3, text=" [Table 3] 일별 근무자 명단 ")
        
        # UI 구축
        self.setup_table2() # 메인이 먼저 보이도록
        self.setup_table1()
        self.setup_table3()
        
        # 하단 버튼 프레임
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="자동 완성 (Auto Fill)", bg="#ffcccc", command=self.run_auto_fill).pack(side='right', padx=10)
        tk.Button(btn_frame, text="새로고침 & 통계 업데이트", command=self.refresh_all).pack(side='right', padx=10)
        tk.Button(btn_frame, text="CSV 저장 (A4 출력용)", command=self.save_csv).pack(side='right', padx=10)

    def get_day_color(self, day):
        """날짜별 색상 반환 (2025년 12월)"""
        # calendar.weekday(year, month, day) -> 0:Mon, ... 5:Sat, 6:Sun
        try:
            wd = calendar.weekday(YEAR, MONTH, day)
            if wd == 5: return "blue"
            if wd == 6: return "red"
        except:
            pass
        return "black"

    # ------------------------------------------------
    # Table 2: 메인 캘린더
    # ------------------------------------------------
    def setup_table2(self):
        canvas = tk.Canvas(self.tab2)
        scrollbar_y = ttk.Scrollbar(self.tab2, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(self.tab2, orient="horizontal", command=canvas.xview)
        
        self.scrollable_frame2 = ttk.Frame(canvas)
        self.scrollable_frame2.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame2, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        # 헤더 그리기
        # (이름) (전월5일) (1~31일)
        tk.Label(self.scrollable_frame2, text="이름/직급", width=15, relief="ridge", bg="lightgray").grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        # 전월 헤더
        tk.Label(self.scrollable_frame2, text="전월", width=20, relief="ridge", bg="#dddddd").grid(row=0, column=1, columnspan=5, sticky="nsew")
        
        # 당월 헤더
        for d in range(1, DAYS_IN_MONTH + 1):
            fg_color = self.get_day_color(d)
            tk.Label(self.scrollable_frame2, text=f"{d}", width=3, relief="ridge", fg=fg_color).grid(row=0, column=5+d, sticky="nsew")
            # 요일 표시
            day_name = ["월", "화", "수", "목", "금", "토", "일"][calendar.weekday(YEAR, MONTH, d)]
            tk.Label(self.scrollable_frame2, text=day_name, width=3, relief="ridge", fg=fg_color).grid(row=1, column=5+d, sticky="nsew")

        # 내용 그리기
        r = 2
        for eid in sorted(EMPLOYEES.keys()):
            emp = EMPLOYEES[eid]
            # 이름 표시
            label_text = f"{emp['ward']} {emp['name']}"
            tk.Label(self.scrollable_frame2, text=label_text, relief="ridge", anchor="w").grid(row=r, column=0, sticky="nsew")
            
            # 전월 5일 (회색 배경, 수정 가능하지만 시각적 구분)
            for i in range(5):
                val = self.logic.schedule[eid][i]
                e = tk.Entry(self.scrollable_frame2, width=3, justify="center", bg="#eeeeee")
                e.insert(0, val)
                e.grid(row=r, column=1+i, padx=1, pady=1)
                self.entries_table2[(eid, i)] = e # key: (eid, index_0_to_35)
            
            # 당월 1~31일
            for i in range(5, 5 + DAYS_IN_MONTH):
                val = self.logic.schedule[eid][i]
                # 날짜에 따른 배경색 (토/일 약간의 틴트?) -> 텍스트 색으로 구분
                # 입력창 생성
                e = tk.Entry(self.scrollable_frame2, width=3, justify="center")
                e.insert(0, val)
                e.grid(row=r, column=1+i, padx=1, pady=1)
                
                # 데이터 바인딩을 위해 딕셔너리에 저장
                self.entries_table2[(eid, i)] = e
            
            r += 1

    # ------------------------------------------------
    # Table 1: 근무 개수 설정 및 통계
    # ------------------------------------------------
    def setup_table1(self):
        # Treeview 대신 Grid 사용 (입력 가능해야 하므로)
        frame = ttk.Frame(self.tab1)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        headers = ["ID", "이름", "병동", "D (목표/현재)", "E (목표/현재)", "N (목표/현재)", "M (목표/현재)", "O (목표/현재)"]
        for col, text in enumerate(headers):
            tk.Label(frame, text=text, font=("Arial", 10, "bold"), relief="ridge", width=15).grid(row=0, column=col, sticky="nsew")

        r = 1
        for eid in sorted(EMPLOYEES.keys()):
            emp = EMPLOYEES[eid]
            tk.Label(frame, text=str(eid)).grid(row=r, column=0)
            tk.Label(frame, text=emp['name']).grid(row=r, column=1)
            tk.Label(frame, text=emp['ward']).grid(row=r, column=2)
            
            # 각 근무 형태별 목표 입력창 및 현재 개수 라벨
            types = ["D", "E", "N", "M", "O"]
            for c_idx, t in enumerate(types):
                sub_frame = tk.Frame(frame)
                sub_frame.grid(row=r, column=3+c_idx)
                
                # 목표 입력
                entry = tk.Entry(sub_frame, width=3)
                entry.insert(0, "0") # 0은 제한 없음
                entry.pack(side="left")
                self.entries_table1[(eid, t)] = entry
                
                # 현재 상태 (라벨) -> 추후 업데이트
                lbl = tk.Label(sub_frame, text="/ 0", fg="blue")
                lbl.pack(side="left")
                self.entries_table1[(eid, f"{t}_lbl")] = lbl
            
            r += 1

    # ------------------------------------------------
    # Table 3: 일별 근무자 명단 (세로쓰기)
    # ------------------------------------------------
    def setup_table3(self):
        canvas = tk.Canvas(self.tab3)
        scroll_x = ttk.Scrollbar(self.tab3, orient="horizontal", command=canvas.xview)
        scroll_y = ttk.Scrollbar(self.tab3, orient="vertical", command=canvas.yview)
        
        self.frame3 = ttk.Frame(canvas)
        self.frame3.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0,0), window=self.frame3, anchor="nw")
        canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        
        canvas.pack(side="top", fill="both", expand=True)
        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")
        
        # 구조: 행(병동/직군) x 열(날짜)
        # 헤더
        tk.Label(self.frame3, text="구분", width=10, relief="raised", bg="lightgray").grid(row=0, column=0, sticky="nsew")
        for d in range(1, DAYS_IN_MONTH + 1):
            fg = self.get_day_color(d)
            tk.Label(self.frame3, text=f"{d}일", width=4, relief="raised", fg=fg).grid(row=0, column=d, sticky="nsew")

        # 행 라벨
        groups = [
            "3W 간호사", "3W 보호사",
            "4W 간호사", "4W 보호사",
            "5W 간호사", "5W 보호사"
        ]
        
        self.table3_labels = {} # (group_idx, day) -> Label

        for i, group in enumerate(groups):
            tk.Label(self.frame3, text=group, width=10, height=10, relief="solid").grid(row=i+1, column=0, sticky="nsew")
            for d in range(1, DAYS_IN_MONTH + 1):
                lbl = tk.Label(self.frame3, text="", width=4, height=10, relief="solid", anchor="n", font=("Arial", 8))
                lbl.grid(row=i+1, column=d, sticky="nsew")
                self.table3_labels[(i, d)] = lbl

    # ------------------------------------------------
    # Actions
    # ------------------------------------------------
    def sync_data_from_ui(self):
        """Table 2의 UI 값을 Logic 메모리로 저장"""
        for (eid, idx), entry in self.entries_table2.items():
            val = entry.get().upper().strip()
            self.logic.schedule[eid][idx] = val

        # Table 1의 목표치도 저장
        for (eid, t), entry in self.entries_table1.items():
            if "lbl" in str(t): continue
            try:
                self.logic.targets[eid][t] = int(entry.get())
            except:
                pass

    def update_ui_from_data(self):
        """Logic 메모리 값을 UI에 반영 (Table 1, 2, 3 전체)"""
        
        # 1. Table 2 (Calendar) 업데이트
        for (eid, idx), entry in self.entries_table2.items():
            val = self.logic.schedule[eid][idx]
            if entry.get() != val:
                entry.delete(0, tk.END)
                entry.insert(0, val)

        # 2. Table 1 (Stats) 업데이트
        for eid in EMPLOYEES:
            counts = self.logic.count_shifts(eid)
            for t in ["D", "E", "N", "M", "O"]:
                lbl = self.entries_table1[(eid, f"{t}_lbl")]
                lbl.config(text=f"/ {counts[t]}")

        # 3. Table 3 (Roster) 업데이트
        # 데이터를 뒤집어서 날짜별/그룹별 명단 생성
        # 그룹 인덱스: 0:3W간, 1:3W보, 2:4W간, 3:4W보, 4:5W간, 5:5W보
        roster = {g: {d: [] for d in range(1, 32)} for g in range(6)}
        
        for eid, info in EMPLOYEES.items():
            # 그룹 결정
            w = info['ward']
            j = info['job']
            g_idx = 0
            if w == "3W": g_idx = 0 if j == "RN" else 1
            elif w == "4W": g_idx = 2 if j == "RN" else 3
            elif w == "5W": g_idx = 4 if j == "RN" else 5
            
            # 스케줄 순회 (인덱스 5 -> 1일)
            for d in range(1, DAYS_IN_MONTH + 1):
                shift = self.logic.schedule[eid][d + 4] # 인덱스 보정
                if shift in ["D", "E", "N", "M", "D5", "n5"]: # 근무자만 표시 (Off 제외)
                    # 세로쓰기용 이름 포맷팅 (김\n철\n수)
                    vert_name = "\n".join(list(info['name']))
                    # 근무 표시 추가 (예: 김철수(N))
                    display_text = f"{vert_name}\n({shift})"
                    roster[g_idx][d].append(display_text)
        
        # 라벨에 텍스트 적용
        for g in range(6):
            for d in range(1, DAYS_IN_MONTH + 1):
                names = roster[g][d]
                text = "\n---\n".join(names) # 구분선
                self.table3_labels[(g, d)].config(text=text)

    def run_auto_fill(self):
        self.sync_data_from_ui() # 현재 수동 입력값 저장
        self.logic.auto_fill()   # 빈칸 채우기
        self.update_ui_from_data() # 결과 보여주기
        messagebox.showinfo("완료", "빈 칸에 대한 근무표 자동 완성이 끝났습니다.\n규칙에 위배되는 경우 수동 수정이 필요할 수 있습니다.")

    def refresh_all(self):
        self.sync_data_from_ui()
        self.update_ui_from_data()

    def save_csv(self):
        self.sync_data_from_ui()
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path: return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # Title
                writer.writerow(["2025년 12월 간호부 근무표"])
                writer.writerow([])
                
                # Header
                header = ["이름", "직급"] + [f"11/{26+i}" for i in range(5)] + [f"12/{i}" for i in range(1, 32)]
                writer.writerow(header)
                
                # Rows
                for eid in sorted(EMPLOYEES.keys()):
                    row = [EMPLOYEES[eid]['name'], EMPLOYEES[eid]['ward']]
                    row += self.logic.schedule[eid]
                    writer.writerow(row)
            
            messagebox.showinfo("저장 성공", f"파일이 저장되었습니다:\n{path}")
        except Exception as e:
            messagebox.showerror("에러", f"저장 중 오류가 발생했습니다: {e}")

# ==========================================
# 4. 실행
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalScheduleApp(root)
=======
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import calendar
import random
import csv

# ==========================================
# 1. 기초 데이터 및 설정
# ==========================================

YEAR = 2025
MONTH = 12
DAYS_IN_MONTH = 31

# 직원 데이터 매핑 (번호: [이름, 병동, 직종])
# 30~35: 3병동 간호사 / 36~39: 3병동 보호사
# 40~45: 4병동 간호사 / 46~49: 4병동 보호사
# 50~55: 5병동 간호사 / 56~59: 5병동 보호사

EMPLOYEES = {}

# 이름 생성 도우미 (임시 이름)
def generate_name(idx, role):
    last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]
    first_names = ["서연", "민준", "지우", "서현", "민재", "하윤", "건우", "예준", "현우", "지민"]
    return f"{random.choice(last_names)}{random.choice(first_names)}"

# 3병동
for i in range(30, 36): EMPLOYEES[i] = {"name": generate_name(i, "간호"), "ward": "3W", "job": "RN"}
for i in range(36, 40): EMPLOYEES[i] = {"name": generate_name(i, "보호"), "ward": "3W", "job": "AN"} # Caregiver
# 4병동
for i in range(40, 46): EMPLOYEES[i] = {"name": generate_name(i, "간호"), "ward": "4W", "job": "RN"}
for i in range(46, 50): EMPLOYEES[i] = {"name": generate_name(i, "보호"), "ward": "4W", "job": "AN"}
# 5병동
for i in range(50, 56): EMPLOYEES[i] = {"name": generate_name(i, "간호"), "ward": "5W", "job": "RN"}
for i in range(56, 60): EMPLOYEES[i] = {"name": generate_name(i, "보호"), "ward": "5W", "job": "AN"}

# 근무 타입 정의
SHIFTS_RN = ["D", "E", "N", "M", "O", "D5", "n5"]
SHIFTS_AN = ["D", "N", "O"]

# ==========================================
# 2. 로직 클래스 (알고리즘)
# ==========================================

class SchedulerLogic:
    def __init__(self):
        # 데이터 저장소
        # self.schedule[emp_id] = [prev_5_days..., day1, day2, ..., day31]
        self.schedule = {} 
        self.targets = {} # {emp_id: {'D': 5, 'E': 5, ...}}
        
        # 초기화
        for eid in EMPLOYEES:
            # 전월 5일 + 당월 31일 = 총 36개 슬롯
            self.schedule[eid] = [""] * (5 + DAYS_IN_MONTH)
            # 전월 데이터는 랜덤하게 채움 (실제로는 입력받아야 함)
            for k in range(5):
                self.schedule[eid][k] = random.choice(["D", "E", "N", "O"])
            
            # 목표 개수 초기화 (기본값 0: 제한 없음 의미)
            self.targets[eid] = {"D": 0, "E": 0, "N": 0, "M": 0, "O": 0}

    def check_validity(self, schedule_list, day_idx, shift_type, job_type):
        """특정 날짜에 특정 근무를 넣을 때 규칙 위반 여부 확인"""
        # 인덱스 보정 (0~4는 전월, 5가 1일)
        current_idx = day_idx
        
        # 1. 근무 타입 유효성
        if job_type == "AN" and shift_type not in ["D", "N", "O"]:
            return False

        # 2. N 근무 연속 3일 초과 불가
        if shift_type == "N":
            consecutive_n = 0
            for k in range(1, 4):
                if current_idx - k >= 0 and schedule_list[current_idx - k] == "N":
                    consecutive_n += 1
                else:
                    break
            if consecutive_n >= 3:
                return False

        # 3. 연속 근무 5일 초과 불가 (6일째는 반드시 O)
        if shift_type != "O":
            consecutive_work = 0
            for k in range(1, 6):
                if current_idx - k >= 0 and schedule_list[current_idx - k] != "O":
                    consecutive_work += 1
                else:
                    break
            if consecutive_work >= 5:
                return False

        # 4. N -> D/E 전환 시 반드시 O 필요 (N 다음날 D/E/M 불가)
        prev_shift = schedule_list[current_idx - 1] if current_idx > 0 else "O"
        if "N" in prev_shift and shift_type in ["D", "E", "M", "D5"]:
            return False

        return True

    def auto_fill(self):
        """자동 완성 알고리즘 (백트래킹/그리디 혼합)"""
        # 간단한 전략: 빈칸인 날짜에 대해 가능한 근무 중 하나를 선택
        # 공정성을 위해 타겟 카운트 고려
        
        for eid, info in EMPLOYEES.items():
            current_schedule = self.schedule[eid]
            job = info['job']
            possible_shifts = SHIFTS_RN if job == "RN" else SHIFTS_AN
            
            # 당월 1일부터 말일까지 순회 (인덱스 5 ~ 35)
            for day in range(5, 5 + DAYS_IN_MONTH):
                if current_schedule[day].strip() != "":
                    continue # 이미 입력된 값은 패스

                valid_options = []
                for s in possible_shifts:
                    if self.check_validity(current_schedule, day, s, job):
                        valid_options.append(s)
                
                if not valid_options:
                    current_schedule[day] = "O" # 갈 곳 없으면 오프
                else:
                    # 타겟 카운트를 고려하여 가중치 부여 (간단 구현: 랜덤)
                    # 실제로는 부족한 근무를 우선 배정하는 로직이 들어감
                    
                    # 2-5일 연속 근무 선호 로직
                    prev = current_schedule[day-1]
                    if prev in valid_options and prev != "O":
                        # 연속 근무 확률 높임
                        if random.random() < 0.7: 
                            current_schedule[day] = prev
                            continue

                    current_schedule[day] = random.choice(valid_options)

    def count_shifts(self, eid):
        """특정 직원의 당월 근무 개수 집계"""
        counts = {"D": 0, "E": 0, "N": 0, "M": 0, "O": 0, "Total": 0}
        # 인덱스 5부터 끝까지 (당월)
        month_schedule = self.schedule[eid][5:]
        
        for s in month_schedule:
            base_s = s[0] if len(s) > 0 else "" # D5 -> D, n5 -> n
            if "D" in s: counts["D"] += 1
            elif "E" in s: counts["E"] += 1
            elif "N" in s or "n" in s: counts["N"] += 1
            elif "M" in s: counts["M"] += 1
            elif "O" in s: counts["O"] += 1
        
        counts["Total"] = counts["D"] + counts["E"] + counts["N"] + counts["M"]
        return counts

# ==========================================
# 3. GUI 클래스
# ==========================================

class HospitalScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("나눔과행복병원 간호부 근무표 생성기 v9.8")
        self.root.geometry("1600x900")
        
        self.logic = SchedulerLogic()
        self.entries_table2 = {} # (eid, day) -> Entry Widget
        self.entries_table1 = {} # (eid, type) -> Entry Widget
        
        # 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", tabposition='n')
        
        # 메인 탭 컨테이너
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 탭 생성
        self.tab1 = ttk.Frame(self.notebook) # 설정 (Table 1)
        self.tab2 = ttk.Frame(self.notebook) # 캘린더 (Table 2)
        self.tab3 = ttk.Frame(self.notebook) # 일별 명단 (Table 3)
        
        self.notebook.add(self.tab2, text=" [Table 2] 월간 근무표 (메인) ")
        self.notebook.add(self.tab1, text=" [Table 1] 근무 개수 설정 ")
        self.notebook.add(self.tab3, text=" [Table 3] 일별 근무자 명단 ")
        
        # UI 구축
        self.setup_table2() # 메인이 먼저 보이도록
        self.setup_table1()
        self.setup_table3()
        
        # 하단 버튼 프레임
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="자동 완성 (Auto Fill)", bg="#ffcccc", command=self.run_auto_fill).pack(side='right', padx=10)
        tk.Button(btn_frame, text="새로고침 & 통계 업데이트", command=self.refresh_all).pack(side='right', padx=10)
        tk.Button(btn_frame, text="CSV 저장 (A4 출력용)", command=self.save_csv).pack(side='right', padx=10)

    def get_day_color(self, day):
        """날짜별 색상 반환 (2025년 12월)"""
        # calendar.weekday(year, month, day) -> 0:Mon, ... 5:Sat, 6:Sun
        try:
            wd = calendar.weekday(YEAR, MONTH, day)
            if wd == 5: return "blue"
            if wd == 6: return "red"
        except:
            pass
        return "black"

    # ------------------------------------------------
    # Table 2: 메인 캘린더
    # ------------------------------------------------
    def setup_table2(self):
        canvas = tk.Canvas(self.tab2)
        scrollbar_y = ttk.Scrollbar(self.tab2, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(self.tab2, orient="horizontal", command=canvas.xview)
        
        self.scrollable_frame2 = ttk.Frame(canvas)
        self.scrollable_frame2.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame2, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        # 헤더 그리기
        # (이름) (전월5일) (1~31일)
        tk.Label(self.scrollable_frame2, text="이름/직급", width=15, relief="ridge", bg="lightgray").grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        # 전월 헤더
        tk.Label(self.scrollable_frame2, text="전월", width=20, relief="ridge", bg="#dddddd").grid(row=0, column=1, columnspan=5, sticky="nsew")
        
        # 당월 헤더
        for d in range(1, DAYS_IN_MONTH + 1):
            fg_color = self.get_day_color(d)
            tk.Label(self.scrollable_frame2, text=f"{d}", width=3, relief="ridge", fg=fg_color).grid(row=0, column=5+d, sticky="nsew")
            # 요일 표시
            day_name = ["월", "화", "수", "목", "금", "토", "일"][calendar.weekday(YEAR, MONTH, d)]
            tk.Label(self.scrollable_frame2, text=day_name, width=3, relief="ridge", fg=fg_color).grid(row=1, column=5+d, sticky="nsew")

        # 내용 그리기
        r = 2
        for eid in sorted(EMPLOYEES.keys()):
            emp = EMPLOYEES[eid]
            # 이름 표시
            label_text = f"{emp['ward']} {emp['name']}"
            tk.Label(self.scrollable_frame2, text=label_text, relief="ridge", anchor="w").grid(row=r, column=0, sticky="nsew")
            
            # 전월 5일 (회색 배경, 수정 가능하지만 시각적 구분)
            for i in range(5):
                val = self.logic.schedule[eid][i]
                e = tk.Entry(self.scrollable_frame2, width=3, justify="center", bg="#eeeeee")
                e.insert(0, val)
                e.grid(row=r, column=1+i, padx=1, pady=1)
                self.entries_table2[(eid, i)] = e # key: (eid, index_0_to_35)
            
            # 당월 1~31일
            for i in range(5, 5 + DAYS_IN_MONTH):
                val = self.logic.schedule[eid][i]
                # 날짜에 따른 배경색 (토/일 약간의 틴트?) -> 텍스트 색으로 구분
                # 입력창 생성
                e = tk.Entry(self.scrollable_frame2, width=3, justify="center")
                e.insert(0, val)
                e.grid(row=r, column=1+i, padx=1, pady=1)
                
                # 데이터 바인딩을 위해 딕셔너리에 저장
                self.entries_table2[(eid, i)] = e
            
            r += 1

    # ------------------------------------------------
    # Table 1: 근무 개수 설정 및 통계
    # ------------------------------------------------
    def setup_table1(self):
        # Treeview 대신 Grid 사용 (입력 가능해야 하므로)
        frame = ttk.Frame(self.tab1)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        headers = ["ID", "이름", "병동", "D (목표/현재)", "E (목표/현재)", "N (목표/현재)", "M (목표/현재)", "O (목표/현재)"]
        for col, text in enumerate(headers):
            tk.Label(frame, text=text, font=("Arial", 10, "bold"), relief="ridge", width=15).grid(row=0, column=col, sticky="nsew")

        r = 1
        for eid in sorted(EMPLOYEES.keys()):
            emp = EMPLOYEES[eid]
            tk.Label(frame, text=str(eid)).grid(row=r, column=0)
            tk.Label(frame, text=emp['name']).grid(row=r, column=1)
            tk.Label(frame, text=emp['ward']).grid(row=r, column=2)
            
            # 각 근무 형태별 목표 입력창 및 현재 개수 라벨
            types = ["D", "E", "N", "M", "O"]
            for c_idx, t in enumerate(types):
                sub_frame = tk.Frame(frame)
                sub_frame.grid(row=r, column=3+c_idx)
                
                # 목표 입력
                entry = tk.Entry(sub_frame, width=3)
                entry.insert(0, "0") # 0은 제한 없음
                entry.pack(side="left")
                self.entries_table1[(eid, t)] = entry
                
                # 현재 상태 (라벨) -> 추후 업데이트
                lbl = tk.Label(sub_frame, text="/ 0", fg="blue")
                lbl.pack(side="left")
                self.entries_table1[(eid, f"{t}_lbl")] = lbl
            
            r += 1

    # ------------------------------------------------
    # Table 3: 일별 근무자 명단 (세로쓰기)
    # ------------------------------------------------
    def setup_table3(self):
        canvas = tk.Canvas(self.tab3)
        scroll_x = ttk.Scrollbar(self.tab3, orient="horizontal", command=canvas.xview)
        scroll_y = ttk.Scrollbar(self.tab3, orient="vertical", command=canvas.yview)
        
        self.frame3 = ttk.Frame(canvas)
        self.frame3.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0,0), window=self.frame3, anchor="nw")
        canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        
        canvas.pack(side="top", fill="both", expand=True)
        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")
        
        # 구조: 행(병동/직군) x 열(날짜)
        # 헤더
        tk.Label(self.frame3, text="구분", width=10, relief="raised", bg="lightgray").grid(row=0, column=0, sticky="nsew")
        for d in range(1, DAYS_IN_MONTH + 1):
            fg = self.get_day_color(d)
            tk.Label(self.frame3, text=f"{d}일", width=4, relief="raised", fg=fg).grid(row=0, column=d, sticky="nsew")

        # 행 라벨
        groups = [
            "3W 간호사", "3W 보호사",
            "4W 간호사", "4W 보호사",
            "5W 간호사", "5W 보호사"
        ]
        
        self.table3_labels = {} # (group_idx, day) -> Label

        for i, group in enumerate(groups):
            tk.Label(self.frame3, text=group, width=10, height=10, relief="solid").grid(row=i+1, column=0, sticky="nsew")
            for d in range(1, DAYS_IN_MONTH + 1):
                lbl = tk.Label(self.frame3, text="", width=4, height=10, relief="solid", anchor="n", font=("Arial", 8))
                lbl.grid(row=i+1, column=d, sticky="nsew")
                self.table3_labels[(i, d)] = lbl

    # ------------------------------------------------
    # Actions
    # ------------------------------------------------
    def sync_data_from_ui(self):
        """Table 2의 UI 값을 Logic 메모리로 저장"""
        for (eid, idx), entry in self.entries_table2.items():
            val = entry.get().upper().strip()
            self.logic.schedule[eid][idx] = val

        # Table 1의 목표치도 저장
        for (eid, t), entry in self.entries_table1.items():
            if "lbl" in str(t): continue
            try:
                self.logic.targets[eid][t] = int(entry.get())
            except:
                pass

    def update_ui_from_data(self):
        """Logic 메모리 값을 UI에 반영 (Table 1, 2, 3 전체)"""
        
        # 1. Table 2 (Calendar) 업데이트
        for (eid, idx), entry in self.entries_table2.items():
            val = self.logic.schedule[eid][idx]
            if entry.get() != val:
                entry.delete(0, tk.END)
                entry.insert(0, val)

        # 2. Table 1 (Stats) 업데이트
        for eid in EMPLOYEES:
            counts = self.logic.count_shifts(eid)
            for t in ["D", "E", "N", "M", "O"]:
                lbl = self.entries_table1[(eid, f"{t}_lbl")]
                lbl.config(text=f"/ {counts[t]}")

        # 3. Table 3 (Roster) 업데이트
        # 데이터를 뒤집어서 날짜별/그룹별 명단 생성
        # 그룹 인덱스: 0:3W간, 1:3W보, 2:4W간, 3:4W보, 4:5W간, 5:5W보
        roster = {g: {d: [] for d in range(1, 32)} for g in range(6)}
        
        for eid, info in EMPLOYEES.items():
            # 그룹 결정
            w = info['ward']
            j = info['job']
            g_idx = 0
            if w == "3W": g_idx = 0 if j == "RN" else 1
            elif w == "4W": g_idx = 2 if j == "RN" else 3
            elif w == "5W": g_idx = 4 if j == "RN" else 5
            
            # 스케줄 순회 (인덱스 5 -> 1일)
            for d in range(1, DAYS_IN_MONTH + 1):
                shift = self.logic.schedule[eid][d + 4] # 인덱스 보정
                if shift in ["D", "E", "N", "M", "D5", "n5"]: # 근무자만 표시 (Off 제외)
                    # 세로쓰기용 이름 포맷팅 (김\n철\n수)
                    vert_name = "\n".join(list(info['name']))
                    # 근무 표시 추가 (예: 김철수(N))
                    display_text = f"{vert_name}\n({shift})"
                    roster[g_idx][d].append(display_text)
        
        # 라벨에 텍스트 적용
        for g in range(6):
            for d in range(1, DAYS_IN_MONTH + 1):
                names = roster[g][d]
                text = "\n---\n".join(names) # 구분선
                self.table3_labels[(g, d)].config(text=text)

    def run_auto_fill(self):
        self.sync_data_from_ui() # 현재 수동 입력값 저장
        self.logic.auto_fill()   # 빈칸 채우기
        self.update_ui_from_data() # 결과 보여주기
        messagebox.showinfo("완료", "빈 칸에 대한 근무표 자동 완성이 끝났습니다.\n규칙에 위배되는 경우 수동 수정이 필요할 수 있습니다.")

    def refresh_all(self):
        self.sync_data_from_ui()
        self.update_ui_from_data()

    def save_csv(self):
        self.sync_data_from_ui()
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path: return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # Title
                writer.writerow(["2025년 12월 간호부 근무표"])
                writer.writerow([])
                
                # Header
                header = ["이름", "직급"] + [f"11/{26+i}" for i in range(5)] + [f"12/{i}" for i in range(1, 32)]
                writer.writerow(header)
                
                # Rows
                for eid in sorted(EMPLOYEES.keys()):
                    row = [EMPLOYEES[eid]['name'], EMPLOYEES[eid]['ward']]
                    row += self.logic.schedule[eid]
                    writer.writerow(row)
            
            messagebox.showinfo("저장 성공", f"파일이 저장되었습니다:\n{path}")
        except Exception as e:
            messagebox.showerror("에러", f"저장 중 오류가 발생했습니다: {e}")

# ==========================================
# 4. 실행
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalScheduleApp(root)
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    root.mainloop()