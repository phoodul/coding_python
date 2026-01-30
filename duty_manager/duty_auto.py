<<<<<<< HEAD
import pandas as pd
import numpy as np
import calendar
from collections import defaultdict

class NurseScheduleManager:
    def __init__(self, year, month, raw_data, requests=None):
        self.year = year
        self.month = month
        self.raw_data = raw_data
        self.requests = requests if requests else {} # {'이름': [1, 5, ...]} 형태
        self.days_in_month = calendar.monthrange(year, month)[1]
        self.weekdays = ['월', '화', '수', '목', '금', '토', '일']
        
        # 1. 데이터 파싱 및 초기화
        self.df = self._parse_data()
        
    def _get_role(self, num_str):
        n = int(num_str)
        if 30 <= n <= 35: return '3병동 간호사'
        if 36 <= n <= 39: return '3병동 보호사'
        if 40 <= n <= 45: return '4병동 간호사'
        if 46 <= n <= 49: return '4병동 보호사'
        if 50 <= n <= 55: return '5병동 간호사'
        if 56 <= n <= 59: return '5병동 보호사'
        return '기타'

    def _parse_data(self):
        """텍스트 데이터를 DataFrame으로 변환"""
        rows = []
        for line in self.raw_data.strip().split('\n'):
            parts = line.split()
            if not parts: continue
            
            num = parts[0]
            name = parts[1]
            shifts = parts[2].split(',')
            
            # 딕셔너리 생성
            row_data = {'번호': num, '이름': name, '직종': self._get_role(num)}
            
            # 날짜별 근무 할당 (데이터가 31일보다 적으면 빈칸, 많으면 자름)
            for day in range(1, self.days_in_month + 1):
                shift_val = shifts[day-1] if (day-1) < len(shifts) else 'O'
                row_data[str(day)] = shift_val.strip()
            
            rows.append(row_data)
        
        return pd.DataFrame(rows)

    def _classify_shift(self, shift_code):
        """근무 코드를 통계용(D, E, N, O)으로 분류"""
        code = str(shift_code).upper()
        if 'O' in code: return 'OFF'
        if code.startswith('D'): return 'D' # D3, D4, D5 -> D
        if code.startswith('E'): return 'E' # E4 -> E
        if code.startswith('N'): return 'N' # N4, N5 -> N
        if code.startswith('M'): return 'M'
        return 'ETC'

    def get_table1_stats(self):
        """[테이블 1] 개인별 근무 개수 집계"""
        stats_rows = []
        
        for _, row in self.df.iterrows():
            counts = defaultdict(int)
            for day in range(1, self.days_in_month + 1):
                s_type = self._classify_shift(row[str(day)])
                counts[s_type] += 1
            
            stats_rows.append({
                '번호': row['번호'],
                '이름': row['이름'],
                '직종': row['직종'],
                'D': counts['D'],
                'E': counts['E'],
                'N': counts['N'],
                'M': counts['M'],
                'O': counts['OFF']
            })
            
        return pd.DataFrame(stats_rows)

    def get_table2_calendar(self):
        """[테이블 2] 전체 스케줄 (하트 로직 적용)"""
        view_df = self.df.copy()
        
        for day in range(1, self.days_in_month + 1):
            col = str(day)
            
            # 각 직원에 대해 순회하며 표시 변경
            for idx, row in view_df.iterrows():
                shift = row[col]
                name = row['이름']
                
                # OFF 처리 로직
                if 'O' in shift:
                    # Request 목록에 해당 날짜가 있는지 확인
                    user_reqs = self.requests.get(name, [])
                    if day in user_reqs:
                        view_df.at[idx, col] = '❤️' # 신청 오프 (빨강)
                    else:
                        view_df.at[idx, col] = '🖤' # 기본 오프 (검정)
                else:
                    view_df.at[idx, col] = shift

        return view_df[['이름'] + [str(d) for d in range(1, self.days_in_month + 1)]]

    def get_table3_daily_roster(self):
        """[테이블 3] 병동별 일별 근무자 명단"""
        # 결과 저장용 딕셔너리 구조 초기화
        roster = {
            '3병동 간호사': [], '3병동 보호사': [],
            '4병동 간호사': [], '4병동 보호사': [],
            '5병동 간호사': [], '5병동 보호사': []
        }
        
        # 각 날짜별로 스트링 빌드
        for row_label in roster.keys():
            # 해당 직종인 직원들 필터링
            sub_df = self.df[self.df['직종'] == row_label]
            
            row_data = {'구분': row_label}
            for day in range(1, self.days_in_month + 1):
                day_str = str(day)
                workers = []
                
                for _, worker in sub_df.iterrows():
                    shift = worker[day_str]
                    if 'O' not in shift: # 오프가 아닌 경우만 추가
                        workers.append(f"{worker['이름']}({shift})")
                
                # 세로쓰기 느낌을 위해 리스트를 줄바꿈 문자열로 연결 (출력 시 가독성)
                row_data[day_str] = ", ".join(workers) if workers else "-"
            
            # DataFrame 변환을 위해 리스트에 append하지 않고 나중에 한꺼번에 처리
            # 여기서는 편의상 최종 데이터프레임 구조를 맞춥니다.
        
        # 판다스로 변환하기 쉽게 구조 재조정
        final_rows = []
        target_order = ['3병동 간호사', '3병동 보호사', '4병동 간호사', '4병동 보호사', '5병동 간호사', '5병동 보호사']
        
        for role in target_order:
            sub_df = self.df[self.df['직종'] == role]
            row_dict = {'구분': role}
            
            for day in range(1, self.days_in_month + 1):
                d_str = str(day)
                # 해당 날짜에 근무하는 사람들 수집
                on_duty = sub_df[~sub_df[d_str].str.contains('O')]
                # 이름(근무) 형태 문자열 생성
                entries = [f"{r['이름']}({r[d_str]})" for _, r in on_duty.iterrows()]
                row_dict[d_str] = "\n".join(entries) # 줄바꿈으로 구분
            
            final_rows.append(row_dict)
            
        return pd.DataFrame(final_rows)

    def update_shift(self, name, day, new_shift):
        """사용자가 테이블2에서 근무를 수정하면 전체 데이터에 반영"""
        # 이름으로 인덱스 찾기
        idx_list = self.df.index[self.df['이름'] == name].tolist()
        if not idx_list:
            print(f"⚠️ 오류: '{name}' 직원을 찾을 수 없습니다.")
            return
        
        idx = idx_list[0]
        self.df.at[idx, str(day)] = new_shift
        print(f"✅ 수정 완료: {name}님의 {day}일 근무가 '{new_shift}'(으)로 변경되었습니다.")
        
    def check_constraints(self):
        """제약 조건 위반 여부 검사 (N 3연속 초과, 5일 근무 후 휴무 등)"""
        print("\n🔍 [근무 규칙 검사 보고서]")
        violation_found = False
        
        for _, row in self.df.iterrows():
            shifts = [row[str(d)] for d in range(1, self.days_in_month + 1)]
            name = row['이름']
            
            # 1. N 근무 연속 3일 초과 체크
            n_streak = 0
            for i, s in enumerate(shifts):
                if 'N' in s: n_streak += 1
                else: n_streak = 0
                
                if n_streak > 3:
                    print(f"  - ⚠️ {name}: {i+1}일 경 N근무 3일 초과 ({n_streak}일째)")
                    violation_found = True
            
            # 2. 연속 5일 근무 후 OFF 체크
            work_streak = 0
            for i, s in enumerate(shifts):
                if 'O' not in s: work_streak += 1
                else: work_streak = 0
                
                if work_streak > 5:
                    print(f"  - ⚠️ {name}: {i+1}일 시점, 5일 초과 연속 근무 중 ({work_streak}일째)")
                    violation_found = True

            # 3. N -> D/E 전환 시 OFF 필수
            for i in range(len(shifts) - 1):
                curr = shifts[i]
                nxt = shifts[i+1]
                if 'N' in curr and ('D' in nxt or 'E' in nxt):
                     print(f"  - ⚠️ {name}: {i+1}일(N) -> {i+2}일({nxt}) 사이에 OFF가 없습니다.")
                     violation_found = True

        if not violation_found:
            print("  - ✅ 위반 사항이 없습니다. 완벽합니다!")

# ==========================================
# 실행 데이터 및 설정
# ==========================================

# 1. 확정된 초기 데이터 (수정 금지)
fixed_raw_data = """
31 최민애 D,O,D,D,D,O,O,D,D,N,N,N,O,O,O,D,D,N,N,O,O,D,D,D,O,N,N,O,O,D,D
32 김유하 E,O,O,E,E,O,N,N,N,O,O,E,O,E,E,O,E,E,O,E,E,N,N,O,O,E,E,N,N,N,O
33 김민경 O,E,E,O,O,D,D,N4,N4,N4,O,O,D,D,O,E,N4,N4,O,O,D,E,O,O,D,D,D,E,O,N4,N4
34 김다인 O,D,N,N,O,E,E,E,O,D,D,D,E,O,D,N,N,O,E,N,N,O,O,N,N,O,O,O,E,O,E
35 김다솜 N,N,O,O,N,N,O,O,E,E,E,O,N,N,N,O,O,D,D,D,O,O,E,E,E,O,O,D,D,E,N
41 이미경 O,D,D,N,N,O,O,D,D,D,D,D,O,O,O,D,D,D,D,O,O,N,N,N,O,D,N,N,N,O,O
42 권수진 N,O,O,D,D,N,N,O,E,E,O,E,O,N,N,N,O,O,E,E,O,E,E,O,N,N,O,O,D,D,D
43 정지우 E,E,E,E,O,E,E,O,O,O,E,O,D,D,D,O,O,E,O,O,E,O,D,D,O,O,D,D,E,E,E
44 송선아 D,N,N,O,O,D,D,E,O,O,N,N,N,O,E,E,E,O,N,N,N,O,O,E,E,E,E,E,O,O,O
51 김도연 O,O,D,D,N,N,N,O,O,E,E,E,N,N,O,O,E,E,O,D,D,N,N,O,O,D,D,D,O,E,O
52 김나은 D,D,O,O,E4,E,E,O,E,O,O,O,E4,E4,N,N,O,O,O,D4,D4,D4,O,N,N,N,O,O,N,N,N
53 허예리 E,O,E,E,E,O,O,E,O,D,D,D,E,O,D,D,D,O,E,E,O,D,D,E,O,O,E,E,E,O,O
54 박수진 O,E,N,N,O,O,D,D,D,O,N,N,O,E,E,E,O,D,D,N,N,O,O,D,D,O,N,N,O,O,E
55 김민영 N,N,O,O,D,D,O,N,N,N,O,O,D,D,O,O,N,N,N,O,E,E,E,O,E,E,O,O,D,D,D
36 전치구 D4,D4,D,O,D4,O,O,N,N,O,O,D,O,O,N,N,O,O,D5,D5,O,D,D5,O,O,D,D,O,N4,N4,N4
37 김재호 N,N,O,D,D,O,D5,O,D,D5,O,O,N,N,O,O,O,D,N,N,N,O,O,D,D,N5,N5,N,O,O,O
38 송재웅 D,D,O,O,N,N,N,O,O,D,D,O,D,D,O,O,N,N,O,O,D,O,D,N,N,O,O,D,N,N,O
39 지정우 O,O,N,N,O,D,D,O,D,N,N,N,O,O,D,D,D,O,D,D,O,N,N,O,O,N,N,O,D,D,N
46 송현찬 O,O,N,N,O,D,D,D,O,N,N,N,O,D,D,O,D,D,O,N,N,O,O,D,N,N,O,O,D,D,D3
47 김두현B N,N,O,O,N,N,O,O,D,D,D,O,N,N,O,D,N,N,N,O,D,D,D,O,D,O,D,D,O,O,O
48 하영기 O,O,D,D,O,O,N,N,N,O,O,D,D,O,N,N,O,O,D,D,O,N,N,N,O,D,N,N,O,O,D
56 서현도 N,N,O,D,D,D,O,O,N,N,N,O,O,D,D,O,O,D,O,O,D,D,O,N,N,O,O,N,N,N,O
57 김두현 O,O,N,N,N,O,O,D,D,O,D,N,N,N,O,D,D,N,N,O,O,N,N,O,D,O,O,D,D,O,D
58 제상수 D,D,D,O,O,N,N,N,O,O,O,D,D,O,N,N,N,O,O,N,N,O,O,D,O,D,D,O,O,D,N
"""

# 2. 직원 Request 샘플 (테스트용)
# 만약 '최민애'가 2일과 13일에 '신청 오프'를 냈다고 가정 (빨간 하트 확인용)
sample_requests = {
    '최민애': [2, 13], 
    '김유하': [3] 
}

# ==========================================
# 시스템 구동
# ==========================================
if __name__ == "__main__":
    # 매니저 생성 (12월)
    manager = NurseScheduleManager(2025, 12, fixed_raw_data, requests=sample_requests)
    
    # --------------------------------------
    # [시나리오] 근무표 수정 및 자동 반영 테스트
    # --------------------------------------
    # 예: 김유하의 1일 근무를 'E' -> 'D'로 변경
    # manager.update_shift('김유하', 1, 'D') 

    # 1. 규칙 검사 (N 3일 연속 등)
    manager.check_constraints()

    # 2. 테이블 출력
    print("\n" + "="*60)
    print("📋 [테이블 1] 근무 개수 통계 (자동 집계)")
    print("="*60)
    print(manager.get_table1_stats().to_markdown(index=False))

    print("\n" + "="*60)
    print("🗓️ [테이블 2] 전체 스케줄 (Request=❤️, 기본=🖤)")
    print("   * 날짜 색상 시뮬레이션: (토)=파랑, (일)=빨강")
    print("="*60)
    # 가독성을 위해 상위 15일만 먼저 출력
    t2 = manager.get_table2_calendar()
    print(t2.iloc[:, :16].to_markdown(index=False)) # 이름 + 1~15일

    print("\n" + "="*60)
    print("👥 [테이블 3] 병동별 일별 근무자 명단 (세로쓰기)")
    print("="*60)
    t3 = manager.get_table3_daily_roster()
    # 지면상 1일~5일치만 출력
=======
import pandas as pd
import numpy as np
import calendar
from collections import defaultdict

class NurseScheduleManager:
    def __init__(self, year, month, raw_data, requests=None):
        self.year = year
        self.month = month
        self.raw_data = raw_data
        self.requests = requests if requests else {} # {'이름': [1, 5, ...]} 형태
        self.days_in_month = calendar.monthrange(year, month)[1]
        self.weekdays = ['월', '화', '수', '목', '금', '토', '일']
        
        # 1. 데이터 파싱 및 초기화
        self.df = self._parse_data()
        
    def _get_role(self, num_str):
        n = int(num_str)
        if 30 <= n <= 35: return '3병동 간호사'
        if 36 <= n <= 39: return '3병동 보호사'
        if 40 <= n <= 45: return '4병동 간호사'
        if 46 <= n <= 49: return '4병동 보호사'
        if 50 <= n <= 55: return '5병동 간호사'
        if 56 <= n <= 59: return '5병동 보호사'
        return '기타'

    def _parse_data(self):
        """텍스트 데이터를 DataFrame으로 변환"""
        rows = []
        for line in self.raw_data.strip().split('\n'):
            parts = line.split()
            if not parts: continue
            
            num = parts[0]
            name = parts[1]
            shifts = parts[2].split(',')
            
            # 딕셔너리 생성
            row_data = {'번호': num, '이름': name, '직종': self._get_role(num)}
            
            # 날짜별 근무 할당 (데이터가 31일보다 적으면 빈칸, 많으면 자름)
            for day in range(1, self.days_in_month + 1):
                shift_val = shifts[day-1] if (day-1) < len(shifts) else 'O'
                row_data[str(day)] = shift_val.strip()
            
            rows.append(row_data)
        
        return pd.DataFrame(rows)

    def _classify_shift(self, shift_code):
        """근무 코드를 통계용(D, E, N, O)으로 분류"""
        code = str(shift_code).upper()
        if 'O' in code: return 'OFF'
        if code.startswith('D'): return 'D' # D3, D4, D5 -> D
        if code.startswith('E'): return 'E' # E4 -> E
        if code.startswith('N'): return 'N' # N4, N5 -> N
        if code.startswith('M'): return 'M'
        return 'ETC'

    def get_table1_stats(self):
        """[테이블 1] 개인별 근무 개수 집계"""
        stats_rows = []
        
        for _, row in self.df.iterrows():
            counts = defaultdict(int)
            for day in range(1, self.days_in_month + 1):
                s_type = self._classify_shift(row[str(day)])
                counts[s_type] += 1
            
            stats_rows.append({
                '번호': row['번호'],
                '이름': row['이름'],
                '직종': row['직종'],
                'D': counts['D'],
                'E': counts['E'],
                'N': counts['N'],
                'M': counts['M'],
                'O': counts['OFF']
            })
            
        return pd.DataFrame(stats_rows)

    def get_table2_calendar(self):
        """[테이블 2] 전체 스케줄 (하트 로직 적용)"""
        view_df = self.df.copy()
        
        for day in range(1, self.days_in_month + 1):
            col = str(day)
            
            # 각 직원에 대해 순회하며 표시 변경
            for idx, row in view_df.iterrows():
                shift = row[col]
                name = row['이름']
                
                # OFF 처리 로직
                if 'O' in shift:
                    # Request 목록에 해당 날짜가 있는지 확인
                    user_reqs = self.requests.get(name, [])
                    if day in user_reqs:
                        view_df.at[idx, col] = '❤️' # 신청 오프 (빨강)
                    else:
                        view_df.at[idx, col] = '🖤' # 기본 오프 (검정)
                else:
                    view_df.at[idx, col] = shift

        return view_df[['이름'] + [str(d) for d in range(1, self.days_in_month + 1)]]

    def get_table3_daily_roster(self):
        """[테이블 3] 병동별 일별 근무자 명단"""
        # 결과 저장용 딕셔너리 구조 초기화
        roster = {
            '3병동 간호사': [], '3병동 보호사': [],
            '4병동 간호사': [], '4병동 보호사': [],
            '5병동 간호사': [], '5병동 보호사': []
        }
        
        # 각 날짜별로 스트링 빌드
        for row_label in roster.keys():
            # 해당 직종인 직원들 필터링
            sub_df = self.df[self.df['직종'] == row_label]
            
            row_data = {'구분': row_label}
            for day in range(1, self.days_in_month + 1):
                day_str = str(day)
                workers = []
                
                for _, worker in sub_df.iterrows():
                    shift = worker[day_str]
                    if 'O' not in shift: # 오프가 아닌 경우만 추가
                        workers.append(f"{worker['이름']}({shift})")
                
                # 세로쓰기 느낌을 위해 리스트를 줄바꿈 문자열로 연결 (출력 시 가독성)
                row_data[day_str] = ", ".join(workers) if workers else "-"
            
            # DataFrame 변환을 위해 리스트에 append하지 않고 나중에 한꺼번에 처리
            # 여기서는 편의상 최종 데이터프레임 구조를 맞춥니다.
        
        # 판다스로 변환하기 쉽게 구조 재조정
        final_rows = []
        target_order = ['3병동 간호사', '3병동 보호사', '4병동 간호사', '4병동 보호사', '5병동 간호사', '5병동 보호사']
        
        for role in target_order:
            sub_df = self.df[self.df['직종'] == role]
            row_dict = {'구분': role}
            
            for day in range(1, self.days_in_month + 1):
                d_str = str(day)
                # 해당 날짜에 근무하는 사람들 수집
                on_duty = sub_df[~sub_df[d_str].str.contains('O')]
                # 이름(근무) 형태 문자열 생성
                entries = [f"{r['이름']}({r[d_str]})" for _, r in on_duty.iterrows()]
                row_dict[d_str] = "\n".join(entries) # 줄바꿈으로 구분
            
            final_rows.append(row_dict)
            
        return pd.DataFrame(final_rows)

    def update_shift(self, name, day, new_shift):
        """사용자가 테이블2에서 근무를 수정하면 전체 데이터에 반영"""
        # 이름으로 인덱스 찾기
        idx_list = self.df.index[self.df['이름'] == name].tolist()
        if not idx_list:
            print(f"⚠️ 오류: '{name}' 직원을 찾을 수 없습니다.")
            return
        
        idx = idx_list[0]
        self.df.at[idx, str(day)] = new_shift
        print(f"✅ 수정 완료: {name}님의 {day}일 근무가 '{new_shift}'(으)로 변경되었습니다.")
        
    def check_constraints(self):
        """제약 조건 위반 여부 검사 (N 3연속 초과, 5일 근무 후 휴무 등)"""
        print("\n🔍 [근무 규칙 검사 보고서]")
        violation_found = False
        
        for _, row in self.df.iterrows():
            shifts = [row[str(d)] for d in range(1, self.days_in_month + 1)]
            name = row['이름']
            
            # 1. N 근무 연속 3일 초과 체크
            n_streak = 0
            for i, s in enumerate(shifts):
                if 'N' in s: n_streak += 1
                else: n_streak = 0
                
                if n_streak > 3:
                    print(f"  - ⚠️ {name}: {i+1}일 경 N근무 3일 초과 ({n_streak}일째)")
                    violation_found = True
            
            # 2. 연속 5일 근무 후 OFF 체크
            work_streak = 0
            for i, s in enumerate(shifts):
                if 'O' not in s: work_streak += 1
                else: work_streak = 0
                
                if work_streak > 5:
                    print(f"  - ⚠️ {name}: {i+1}일 시점, 5일 초과 연속 근무 중 ({work_streak}일째)")
                    violation_found = True

            # 3. N -> D/E 전환 시 OFF 필수
            for i in range(len(shifts) - 1):
                curr = shifts[i]
                nxt = shifts[i+1]
                if 'N' in curr and ('D' in nxt or 'E' in nxt):
                     print(f"  - ⚠️ {name}: {i+1}일(N) -> {i+2}일({nxt}) 사이에 OFF가 없습니다.")
                     violation_found = True

        if not violation_found:
            print("  - ✅ 위반 사항이 없습니다. 완벽합니다!")

# ==========================================
# 실행 데이터 및 설정
# ==========================================

# 1. 확정된 초기 데이터 (수정 금지)
fixed_raw_data = """
31 최민애 D,O,D,D,D,O,O,D,D,N,N,N,O,O,O,D,D,N,N,O,O,D,D,D,O,N,N,O,O,D,D
32 김유하 E,O,O,E,E,O,N,N,N,O,O,E,O,E,E,O,E,E,O,E,E,N,N,O,O,E,E,N,N,N,O
33 김민경 O,E,E,O,O,D,D,N4,N4,N4,O,O,D,D,O,E,N4,N4,O,O,D,E,O,O,D,D,D,E,O,N4,N4
34 김다인 O,D,N,N,O,E,E,E,O,D,D,D,E,O,D,N,N,O,E,N,N,O,O,N,N,O,O,O,E,O,E
35 김다솜 N,N,O,O,N,N,O,O,E,E,E,O,N,N,N,O,O,D,D,D,O,O,E,E,E,O,O,D,D,E,N
41 이미경 O,D,D,N,N,O,O,D,D,D,D,D,O,O,O,D,D,D,D,O,O,N,N,N,O,D,N,N,N,O,O
42 권수진 N,O,O,D,D,N,N,O,E,E,O,E,O,N,N,N,O,O,E,E,O,E,E,O,N,N,O,O,D,D,D
43 정지우 E,E,E,E,O,E,E,O,O,O,E,O,D,D,D,O,O,E,O,O,E,O,D,D,O,O,D,D,E,E,E
44 송선아 D,N,N,O,O,D,D,E,O,O,N,N,N,O,E,E,E,O,N,N,N,O,O,E,E,E,E,E,O,O,O
51 김도연 O,O,D,D,N,N,N,O,O,E,E,E,N,N,O,O,E,E,O,D,D,N,N,O,O,D,D,D,O,E,O
52 김나은 D,D,O,O,E4,E,E,O,E,O,O,O,E4,E4,N,N,O,O,O,D4,D4,D4,O,N,N,N,O,O,N,N,N
53 허예리 E,O,E,E,E,O,O,E,O,D,D,D,E,O,D,D,D,O,E,E,O,D,D,E,O,O,E,E,E,O,O
54 박수진 O,E,N,N,O,O,D,D,D,O,N,N,O,E,E,E,O,D,D,N,N,O,O,D,D,O,N,N,O,O,E
55 김민영 N,N,O,O,D,D,O,N,N,N,O,O,D,D,O,O,N,N,N,O,E,E,E,O,E,E,O,O,D,D,D
36 전치구 D4,D4,D,O,D4,O,O,N,N,O,O,D,O,O,N,N,O,O,D5,D5,O,D,D5,O,O,D,D,O,N4,N4,N4
37 김재호 N,N,O,D,D,O,D5,O,D,D5,O,O,N,N,O,O,O,D,N,N,N,O,O,D,D,N5,N5,N,O,O,O
38 송재웅 D,D,O,O,N,N,N,O,O,D,D,O,D,D,O,O,N,N,O,O,D,O,D,N,N,O,O,D,N,N,O
39 지정우 O,O,N,N,O,D,D,O,D,N,N,N,O,O,D,D,D,O,D,D,O,N,N,O,O,N,N,O,D,D,N
46 송현찬 O,O,N,N,O,D,D,D,O,N,N,N,O,D,D,O,D,D,O,N,N,O,O,D,N,N,O,O,D,D,D3
47 김두현B N,N,O,O,N,N,O,O,D,D,D,O,N,N,O,D,N,N,N,O,D,D,D,O,D,O,D,D,O,O,O
48 하영기 O,O,D,D,O,O,N,N,N,O,O,D,D,O,N,N,O,O,D,D,O,N,N,N,O,D,N,N,O,O,D
56 서현도 N,N,O,D,D,D,O,O,N,N,N,O,O,D,D,O,O,D,O,O,D,D,O,N,N,O,O,N,N,N,O
57 김두현 O,O,N,N,N,O,O,D,D,O,D,N,N,N,O,D,D,N,N,O,O,N,N,O,D,O,O,D,D,O,D
58 제상수 D,D,D,O,O,N,N,N,O,O,O,D,D,O,N,N,N,O,O,N,N,O,O,D,O,D,D,O,O,D,N
"""

# 2. 직원 Request 샘플 (테스트용)
# 만약 '최민애'가 2일과 13일에 '신청 오프'를 냈다고 가정 (빨간 하트 확인용)
sample_requests = {
    '최민애': [2, 13], 
    '김유하': [3] 
}

# ==========================================
# 시스템 구동
# ==========================================
if __name__ == "__main__":
    # 매니저 생성 (12월)
    manager = NurseScheduleManager(2025, 12, fixed_raw_data, requests=sample_requests)
    
    # --------------------------------------
    # [시나리오] 근무표 수정 및 자동 반영 테스트
    # --------------------------------------
    # 예: 김유하의 1일 근무를 'E' -> 'D'로 변경
    # manager.update_shift('김유하', 1, 'D') 

    # 1. 규칙 검사 (N 3일 연속 등)
    manager.check_constraints()

    # 2. 테이블 출력
    print("\n" + "="*60)
    print("📋 [테이블 1] 근무 개수 통계 (자동 집계)")
    print("="*60)
    print(manager.get_table1_stats().to_markdown(index=False))

    print("\n" + "="*60)
    print("🗓️ [테이블 2] 전체 스케줄 (Request=❤️, 기본=🖤)")
    print("   * 날짜 색상 시뮬레이션: (토)=파랑, (일)=빨강")
    print("="*60)
    # 가독성을 위해 상위 15일만 먼저 출력
    t2 = manager.get_table2_calendar()
    print(t2.iloc[:, :16].to_markdown(index=False)) # 이름 + 1~15일

    print("\n" + "="*60)
    print("👥 [테이블 3] 병동별 일별 근무자 명단 (세로쓰기)")
    print("="*60)
    t3 = manager.get_table3_daily_roster()
    # 지면상 1일~5일치만 출력
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
    print(t3[['구분', '1', '2', '3', '4', '5']].to_markdown(index=False))