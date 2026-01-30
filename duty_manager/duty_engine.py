<<<<<<< HEAD
# -*- coding: utf-8 -*-
import random

class DutyEngine:
    def __init__(self, staff_list, days_in_month, prev_history=None):
        """
        prev_history: { sid: [day-5, day-4, day-3, day-2, day-1] }
        """
        self.staff_list = staff_list
        self.days = days_in_month
        self.prev_history = prev_history or {}

    def check_rule_violation(self, sid, day_idx, shift_type, current_schedule, current_counts, quotas):
        if not shift_type or shift_type in ["♥", "O", ""]: return True, ""
        base = shift_type[0].upper()
        sid_str = str(sid)

        # [추가] 테이블 1의 목표 근무 개수(Quota) 확인
        target_quota = int(quotas.get(sid_str, {}).get(base, 99))
        if current_counts.get(sid_str, {}).get(base, 0) >= target_quota:
            return False, f"{base} 근무 개수 초과"

        # 이전 근무 데이터 파악 (전월 5일 데이터 포함)
        full_history = self.prev_history.get(sid_str, ["♥"]*5) + current_schedule[sid]
        adj_idx = day_idx + 5 

        prev_raw = full_history[adj_idx-1]
        prev_duty = "O" if (not prev_raw or prev_raw == "♥") else prev_raw[0].upper()

        # 연속 근무 일수 계산
        con_days = 0
        is_prev_off = (prev_duty == "O")
        for i in range(adj_idx-1, -1, -1):
            val = full_history[i]
            curr_is_off = (not val or val == "♥")
            if curr_is_off == is_prev_off: con_days += 1
            else: break

        # 연속 N 근무 계산
        con_n = 0
        for i in range(adj_idx-1, -1, -1):
            val = full_history[i]
            if val and val[0].upper() == "N": con_n += 1
            else: break

        # [핵심 규칙]
        if prev_duty == "N" and base in ["D", "E", "M"]: 
            return False, "N 다음날은 반드시 휴무"
        if prev_duty == "E" and base == "D": 
            return False, "E 다음날 D 불가"
        
        # [규칙 3] N 근무 3개 제한 / 5연근 제한
        if base == "N" and con_n >= 3: return False, "N 3개 초과 불가"
        if base != "O" and prev_duty != "O" and con_days >= 5: return False, "5일 연근 제한"

        # [회복 기간] N-O-N 방지
        if base == "N":
            lookback = 5
            n_count = 0
            for i in range(adj_idx-1, max(-1, adj_idx-lookback), -1):
                val = full_history[i]
                if val and val[0].upper() == "N": n_count += 1
            if n_count >= 2 and prev_duty == "O":
                return False, "N 근무 후 충분한 휴식 필요"

        return True, ""

    def run_auto_complete(self, request_data, table1_quotas, table3_pre):
        schedule = {s[0]: [None]*self.days for s in self.staff_list}
        current_counts = {str(s[0]): {"D":0, "E":0, "N":0, "M":0} for s in self.staff_list}
        
        # 1. 수동 입력값(Request) 우선 반영
        for sid, days in request_data.items():
            for d_idx, val in enumerate(days):
                if val and val.strip() and val != "♥": 
                    schedule[sid][d_idx] = val
                    base = val[0].upper()
                    if base in current_counts[str(sid)]:
                        current_counts[str(sid)][base] += 1

        # 2. 날짜별 배정
        for d in range(self.days):
            for ward in ["3W", "4W", "5W"]:
                for r_type in ["Nurse", "Caregiver"]:
                    shifts = ["D", "E", "N"] if r_type == "Nurse" else ["D", "N"]
                    for s_type in shifts:
                        key = f"{ward}_{r_type}_{s_type}"
                        assigned_names = table3_pre.get(d+1, {}).get(key, "")
                        
                        # 테이블 3에 'X'가 있으면 배정 건너뜀
                        if "X" in assigned_names: continue
                        
                        if assigned_names:
                            self._assign_name(assigned_names, d, s_type, ward, schedule, current_counts)
                        else:
                            role_limit = "간호사" if r_type == "Nurse" else "보호사"
                            self._fill_best(d, s_type, ward, role_limit, schedule, current_counts, table1_quotas)
        
        for sid in schedule:
            for d in range(self.days):
                if not schedule[sid][d]: schedule[sid][d] = "♥"
        return schedule

    def _assign_name(self, names, d, stype, ward, schedule, current_counts):
        for name in names.split('\n'):
            name = name.strip()
            if not name: continue
            for s in self.staff_list:
                if s[1] == name:
                    sid = s[0]
                    if schedule[sid][d]: continue 
                    s_ward = str(sid)[0] + "W"
                    code = stype if s_ward == ward else f"{stype}{ward[0]}"
                    schedule[sid][d] = code
                    if stype[0].upper() in current_counts[str(sid)]:
                        current_counts[str(sid)][stype[0].upper()] += 1

    def _fill_best(self, d, stype, ward, role_req, schedule, current_counts, quotas):
        cands = []
        for s in self.staff_list:
            sid, s_name, s_role = s
            if role_req not in s_role: continue
            if schedule[sid][d]: continue
            
            is_ok, _ = self.check_rule_violation(sid, d, stype, schedule, current_counts, quotas)
            if not is_ok: continue
            
            score = 0
            s_ward = str(sid)[0] + "W"
            if s_ward != ward: score += 100000 # 타병동 파견 억제

            # 공정성 및 목표량(Quota) 기반 점수화
            q = int(quotas.get(str(sid), {}).get(stype[0].upper(), 0))
            curr = current_counts.get(str(sid), {}).get(stype[0].upper(), 0)
            remaining = q - curr
            score -= remaining * 5000 
            
            total_work = sum(current_counts[str(sid)].values())
            score += total_work * 1000
            
            # 연속성 (동일 근무 블록)
            full_history = self.prev_history.get(str(sid), ["♥"]*5) + schedule[sid]
            adj_idx = d + 5
            prev_val = full_history[adj_idx-1]
            if prev_val and prev_val[0].upper() == stype[0].upper():
                score -= 2000 
            
            score += random.random() * 100
            cands.append((sid, score))
        
        if cands:
            best_sid = min(cands, key=lambda x: x[1])[0]
            s_ward = str(best_sid)[0] + "W"
            code = stype if s_ward == ward else f"{stype}{ward[0]}"
            schedule[best_sid][d] = code
            if stype[0].upper() in current_counts[str(best_sid)]:
=======
# -*- coding: utf-8 -*-
import random

class DutyEngine:
    def __init__(self, staff_list, days_in_month, prev_history=None):
        """
        prev_history: { sid: [day-5, day-4, day-3, day-2, day-1] }
        """
        self.staff_list = staff_list
        self.days = days_in_month
        self.prev_history = prev_history or {}

    def check_rule_violation(self, sid, day_idx, shift_type, current_schedule, current_counts, quotas):
        if not shift_type or shift_type in ["♥", "O", ""]: return True, ""
        base = shift_type[0].upper()
        sid_str = str(sid)

        # [추가] 테이블 1의 목표 근무 개수(Quota) 확인
        target_quota = int(quotas.get(sid_str, {}).get(base, 99))
        if current_counts.get(sid_str, {}).get(base, 0) >= target_quota:
            return False, f"{base} 근무 개수 초과"

        # 이전 근무 데이터 파악 (전월 5일 데이터 포함)
        full_history = self.prev_history.get(sid_str, ["♥"]*5) + current_schedule[sid]
        adj_idx = day_idx + 5 

        prev_raw = full_history[adj_idx-1]
        prev_duty = "O" if (not prev_raw or prev_raw == "♥") else prev_raw[0].upper()

        # 연속 근무 일수 계산
        con_days = 0
        is_prev_off = (prev_duty == "O")
        for i in range(adj_idx-1, -1, -1):
            val = full_history[i]
            curr_is_off = (not val or val == "♥")
            if curr_is_off == is_prev_off: con_days += 1
            else: break

        # 연속 N 근무 계산
        con_n = 0
        for i in range(adj_idx-1, -1, -1):
            val = full_history[i]
            if val and val[0].upper() == "N": con_n += 1
            else: break

        # [핵심 규칙]
        if prev_duty == "N" and base in ["D", "E", "M"]: 
            return False, "N 다음날은 반드시 휴무"
        if prev_duty == "E" and base == "D": 
            return False, "E 다음날 D 불가"
        
        # [규칙 3] N 근무 3개 제한 / 5연근 제한
        if base == "N" and con_n >= 3: return False, "N 3개 초과 불가"
        if base != "O" and prev_duty != "O" and con_days >= 5: return False, "5일 연근 제한"

        # [회복 기간] N-O-N 방지
        if base == "N":
            lookback = 5
            n_count = 0
            for i in range(adj_idx-1, max(-1, adj_idx-lookback), -1):
                val = full_history[i]
                if val and val[0].upper() == "N": n_count += 1
            if n_count >= 2 and prev_duty == "O":
                return False, "N 근무 후 충분한 휴식 필요"

        return True, ""

    def run_auto_complete(self, request_data, table1_quotas, table3_pre):
        schedule = {s[0]: [None]*self.days for s in self.staff_list}
        current_counts = {str(s[0]): {"D":0, "E":0, "N":0, "M":0} for s in self.staff_list}
        
        # 1. 수동 입력값(Request) 우선 반영
        for sid, days in request_data.items():
            for d_idx, val in enumerate(days):
                if val and val.strip() and val != "♥": 
                    schedule[sid][d_idx] = val
                    base = val[0].upper()
                    if base in current_counts[str(sid)]:
                        current_counts[str(sid)][base] += 1

        # 2. 날짜별 배정
        for d in range(self.days):
            for ward in ["3W", "4W", "5W"]:
                for r_type in ["Nurse", "Caregiver"]:
                    shifts = ["D", "E", "N"] if r_type == "Nurse" else ["D", "N"]
                    for s_type in shifts:
                        key = f"{ward}_{r_type}_{s_type}"
                        assigned_names = table3_pre.get(d+1, {}).get(key, "")
                        
                        # 테이블 3에 'X'가 있으면 배정 건너뜀
                        if "X" in assigned_names: continue
                        
                        if assigned_names:
                            self._assign_name(assigned_names, d, s_type, ward, schedule, current_counts)
                        else:
                            role_limit = "간호사" if r_type == "Nurse" else "보호사"
                            self._fill_best(d, s_type, ward, role_limit, schedule, current_counts, table1_quotas)
        
        for sid in schedule:
            for d in range(self.days):
                if not schedule[sid][d]: schedule[sid][d] = "♥"
        return schedule

    def _assign_name(self, names, d, stype, ward, schedule, current_counts):
        for name in names.split('\n'):
            name = name.strip()
            if not name: continue
            for s in self.staff_list:
                if s[1] == name:
                    sid = s[0]
                    if schedule[sid][d]: continue 
                    s_ward = str(sid)[0] + "W"
                    code = stype if s_ward == ward else f"{stype}{ward[0]}"
                    schedule[sid][d] = code
                    if stype[0].upper() in current_counts[str(sid)]:
                        current_counts[str(sid)][stype[0].upper()] += 1

    def _fill_best(self, d, stype, ward, role_req, schedule, current_counts, quotas):
        cands = []
        for s in self.staff_list:
            sid, s_name, s_role = s
            if role_req not in s_role: continue
            if schedule[sid][d]: continue
            
            is_ok, _ = self.check_rule_violation(sid, d, stype, schedule, current_counts, quotas)
            if not is_ok: continue
            
            score = 0
            s_ward = str(sid)[0] + "W"
            if s_ward != ward: score += 100000 # 타병동 파견 억제

            # 공정성 및 목표량(Quota) 기반 점수화
            q = int(quotas.get(str(sid), {}).get(stype[0].upper(), 0))
            curr = current_counts.get(str(sid), {}).get(stype[0].upper(), 0)
            remaining = q - curr
            score -= remaining * 5000 
            
            total_work = sum(current_counts[str(sid)].values())
            score += total_work * 1000
            
            # 연속성 (동일 근무 블록)
            full_history = self.prev_history.get(str(sid), ["♥"]*5) + schedule[sid]
            adj_idx = d + 5
            prev_val = full_history[adj_idx-1]
            if prev_val and prev_val[0].upper() == stype[0].upper():
                score -= 2000 
            
            score += random.random() * 100
            cands.append((sid, score))
        
        if cands:
            best_sid = min(cands, key=lambda x: x[1])[0]
            s_ward = str(best_sid)[0] + "W"
            code = stype if s_ward == ward else f"{stype}{ward[0]}"
            schedule[best_sid][d] = code
            if stype[0].upper() in current_counts[str(best_sid)]:
>>>>>>> 4d16b35fa97b7af3588c8ad918749e5735e40ba1
                current_counts[str(best_sid)][stype[0].upper()] += 1