<<<<<<< HEAD
import requests
import json
import time
import datetime
import schedule # pip install schedule 필요

# ==========================================
# [설정] 아래 두 가지 정보를 입력해주세요
# ==========================================

# 1. 카카오톡 액세스 토큰 (Kakao Developers에서 발급)
# 주의: 기본 토큰은 수명(6시간)이 짧습니다. 장기 사용시 '리프레시 토큰' 로직이 필요합니다.
KAKAO_TOKEN = "jVEzB2jXs_r12o74tidYYN7yUGm2DheBAAAAAQoXC9cAAAGbIq-NtR7SOb8w2j0_"

# 2. 씨젠 로그인 쿠키 (cURL에서 복사한 'Cookie' 전체)
COOKIE_STRING = "visid_incap_2839813=4tA2B+1IQgCzRr5wRfbJF1I9PGkAAAAAQUIPAAAAAAAAgIY31+5zygrvXWTMX4Xh; _ga=GA1.1.2040753655.1765555540; WMONID=QfjBSdpABVQ; visid_incap_3209525=avc6JaUsQLSUdYHbZJ4tEls9PGkAAAAAQUIPAAAAAAB07wTx70oz9io+oXeYVduP; visid_incap_2845396=7DVo7wiUTdOjadEyc5zaK1w9PGkAAAAAQUIPAAAAAAAUYNDJG8k6ZRVCK+u7aWGT; ROUTEID=route.was2; incap_ses_950_3209525=eSwaI3uyVSL9xQhDbhQvDVMfQGkAAAAArQtAxPJsJNAmTyN1kHrmoQ==; incap_ses_950_2845396=VEJmVW07mz9exghDbhQvDVMfQGkAAAAAOgOMhDSJexww7gkdHHugEg=="

# ==========================================

def send_kakao_msg(text):
    """카카오톡으로 나에게 메시지를 보냅니다."""
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {KAKAO_TOKEN}"}
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": "https://srms.seegenemedical.com",
                "mobile_web_url": "https://srms.seegenemedical.com"
            }
        })
    }
    res = requests.post(url, headers=headers, data=data)
    if res.status_code == 200:
        print("✅ 카카오톡 전송 성공!")
    else:
        print(f"❌ 카톡 전송 실패: {res.status_code} (토큰 만료 확인 필요)")

def check_results():
    """어제 날짜 검사 결과를 조회하고 이상 수치를 찾습니다."""
    print(f"\n[{datetime.datetime.now()}] 검사 결과 조회를 시작합니다...")

    # 1. 날짜 계산 (어제 날짜)
    today = datetime.date.today()
    yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_nodash = yesterday.replace("-", "")
    
    print(f"🔎 검색 대상일: {yesterday}")

    # 2. 헤더 설정
    headers = {
        "accept": "application/json, */*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://srms.seegenemedical.com",
        "referer": "https://srms.seegenemedical.com/rstUser.do",
        "cookie": COOKIE_STRING,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    # 3. 환자 목록 조회 (rstUserList.do)
    list_url = "https://srms.seegenemedical.com/rstUserList.do"
    list_payload = {
        "I_LOGMNU": "RSTUSER",
        "I_FDT": yesterday, # 어제
        "I_TDT": yesterday, # 어제
        "I_FNM": "동래나눔과행복병원",
        "I_PHOS": "29114",
        "I_CNT": "100",     # 최대 100명까지
        "I_LNG": "KOR"
    }

    try:
        res = requests.post(list_url, headers=headers, data=list_payload)
        patients = res.json()
        
        # 로그인 세션 체크
        if isinstance(patients, dict) and "strMessage" in patients:
             print("⚠️ 로그인 세션이 만료되었습니다. 쿠키를 갱신해주세요.")
             return

        abnormal_cases = [] # 이상 수치 모음

        print(f"총 {len(patients)}명의 수진자 발견. 상세 분석 시작...")

        # 4. 각 환자별 상세 조회
        for p in patients:
            p_name = p.get('NAM', '이름없음')
            p_jno = p.get('JNO') # 접수번호
            p_dat = p.get('DAT') # 접수일자
            
            # 상세 조회 요청 (rstUserDtl.do)
            dtl_url = "https://srms.seegenemedical.com/rstUserDtl.do"
            dtl_payload = {
                "I_LOGMNU": "RSTUSER",
                "I_DAT": p_dat,
                "I_JNO": p_jno,
                "I_DTLDAT": p_dat,
                "I_DTLJNO": p_jno,
                "I_HOS": "29114",
                "I_ECF": "N"
            }
            
            res_dtl = requests.post(dtl_url, headers=headers, data=dtl_payload)
            dtl_data = res_dtl.json()

            # 상세 데이터 파싱
            if isinstance(dtl_data, dict):
                # 일반 검사 결과 리스트
                results = dtl_data.get('rstUserDtl', [])
                # 이상 소견 리스트 (redTxtList)
                red_list = dtl_data.get('redTxtList', [])
                red_codes = [item.get('R003GCD') for item in red_list]

                for item in results:
                    # 항목 코드, 이름, 결과, 판정
                    t_code = item.get('GCD', '')   # 검사코드
                    t_name = item.get('TNM', '')   # 검사항목명
                    t_rslt = item.get('RSLT', '')  # 결과값
                    t_judge = item.get('JUDGE', '') # 판정 (H, L 등)

                    # [조건] 1. 판정(JUDGE)에 H, L 등이 있거나
                    # [조건] 2. redTxtList에 포함된 코드라면 이상 수치로 간주
                    is_abnormal = False
                    
                    if t_judge in ['H', 'L', 'P', 'Pos', '+']:
                        is_abnormal = True
                    elif t_code in red_codes:
                        is_abnormal = True
                    # 결과값에 'High' 등의 텍스트가 포함된 경우 체크
                    elif "High" in str(t_rslt) or "Low" in str(t_rslt):
                        is_abnormal = True

                    if is_abnormal:
                        case_str = f"[{p_name}] {t_name}: {t_rslt} ({t_judge})"
                        abnormal_cases.append(case_str)
                        print(f"  🚨 발견: {case_str}")

        # 5. 결과 종합 및 카톡 전송
        if abnormal_cases:
            msg = f"📢 [이상 수치 알림]\n기준일: {yesterday}\n\n" + "\n".join(abnormal_cases)
            print("카톡 전송 중...")
            send_kakao_msg(msg)
        else:
            print("특이사항이 없습니다.")

    except Exception as e:
        print(f"에러 발생: {e}")

# ==========================================
# [스케줄러] 매일 아침 07:00에 실행
# ==========================================
print("🚀 자동 알림 봇이 시작되었습니다. (매일 07:00 실행)")

# 테스트를 위해 지금 즉시 한번 실행해보고 싶으면 아래 주석(#)을 지우세요
check_results()

schedule.every().day.at("07:00").do(check_results)

while True:
    schedule.run_pending()
=======
import requests
import json
import time
import datetime
import schedule # pip install schedule 필요

# ==========================================
# [설정] 아래 두 가지 정보를 입력해주세요
# ==========================================

# 1. 카카오톡 액세스 토큰 (Kakao Developers에서 발급)
# 주의: 기본 토큰은 수명(6시간)이 짧습니다. 장기 사용시 '리프레시 토큰' 로직이 필요합니다.
KAKAO_TOKEN = "jVEzB2jXs_r12o74tidYYN7yUGm2DheBAAAAAQoXC9cAAAGbIq-NtR7SOb8w2j0_"

# 2. 씨젠 로그인 쿠키 (cURL에서 복사한 'Cookie' 전체)
COOKIE_STRING = "visid_incap_2839813=4tA2B+1IQgCzRr5wRfbJF1I9PGkAAAAAQUIPAAAAAAAAgIY31+5zygrvXWTMX4Xh; _ga=GA1.1.2040753655.1765555540; WMONID=QfjBSdpABVQ; visid_incap_3209525=avc6JaUsQLSUdYHbZJ4tEls9PGkAAAAAQUIPAAAAAAB07wTx70oz9io+oXeYVduP; visid_incap_2845396=7DVo7wiUTdOjadEyc5zaK1w9PGkAAAAAQUIPAAAAAAAUYNDJG8k6ZRVCK+u7aWGT; ROUTEID=route.was2; incap_ses_950_3209525=eSwaI3uyVSL9xQhDbhQvDVMfQGkAAAAArQtAxPJsJNAmTyN1kHrmoQ==; incap_ses_950_2845396=VEJmVW07mz9exghDbhQvDVMfQGkAAAAAOgOMhDSJexww7gkdHHugEg=="

# ==========================================

def send_kakao_msg(text):
    """카카오톡으로 나에게 메시지를 보냅니다."""
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {KAKAO_TOKEN}"}
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": "https://srms.seegenemedical.com",
                "mobile_web_url": "https://srms.seegenemedical.com"
            }
        })
    }
    res = requests.post(url, headers=headers, data=data)
    if res.status_code == 200:
        print("✅ 카카오톡 전송 성공!")
    else:
        print(f"❌ 카톡 전송 실패: {res.status_code} (토큰 만료 확인 필요)")

def check_results():
    """어제 날짜 검사 결과를 조회하고 이상 수치를 찾습니다."""
    print(f"\n[{datetime.datetime.now()}] 검사 결과 조회를 시작합니다...")

    # 1. 날짜 계산 (어제 날짜)
    today = datetime.date.today()
    yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_nodash = yesterday.replace("-", "")
    
    print(f"🔎 검색 대상일: {yesterday}")

    # 2. 헤더 설정
    headers = {
        "accept": "application/json, */*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://srms.seegenemedical.com",
        "referer": "https://srms.seegenemedical.com/rstUser.do",
        "cookie": COOKIE_STRING,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    # 3. 환자 목록 조회 (rstUserList.do)
    list_url = "https://srms.seegenemedical.com/rstUserList.do"
    list_payload = {
        "I_LOGMNU": "RSTUSER",
        "I_FDT": yesterday, # 어제
        "I_TDT": yesterday, # 어제
        "I_FNM": "동래나눔과행복병원",
        "I_PHOS": "29114",
        "I_CNT": "100",     # 최대 100명까지
        "I_LNG": "KOR"
    }

    try:
        res = requests.post(list_url, headers=headers, data=list_payload)
        patients = res.json()
        
        # 로그인 세션 체크
        if isinstance(patients, dict) and "strMessage" in patients:
             print("⚠️ 로그인 세션이 만료되었습니다. 쿠키를 갱신해주세요.")
             return

        abnormal_cases = [] # 이상 수치 모음

        print(f"총 {len(patients)}명의 수진자 발견. 상세 분석 시작...")

        # 4. 각 환자별 상세 조회
        for p in patients:
            p_name = p.get('NAM', '이름없음')
            p_jno = p.get('JNO') # 접수번호
            p_dat = p.get('DAT') # 접수일자
            
            # 상세 조회 요청 (rstUserDtl.do)
            dtl_url = "https://srms.seegenemedical.com/rstUserDtl.do"
            dtl_payload = {
                "I_LOGMNU": "RSTUSER",
                "I_DAT": p_dat,
                "I_JNO": p_jno,
                "I_DTLDAT": p_dat,
                "I_DTLJNO": p_jno,
                "I_HOS": "29114",
                "I_ECF": "N"
            }
            
            res_dtl = requests.post(dtl_url, headers=headers, data=dtl_payload)
            dtl_data = res_dtl.json()

            # 상세 데이터 파싱
            if isinstance(dtl_data, dict):
                # 일반 검사 결과 리스트
                results = dtl_data.get('rstUserDtl', [])
                # 이상 소견 리스트 (redTxtList)
                red_list = dtl_data.get('redTxtList', [])
                red_codes = [item.get('R003GCD') for item in red_list]

                for item in results:
                    # 항목 코드, 이름, 결과, 판정
                    t_code = item.get('GCD', '')   # 검사코드
                    t_name = item.get('TNM', '')   # 검사항목명
                    t_rslt = item.get('RSLT', '')  # 결과값
                    t_judge = item.get('JUDGE', '') # 판정 (H, L 등)

                    # [조건] 1. 판정(JUDGE)에 H, L 등이 있거나
                    # [조건] 2. redTxtList에 포함된 코드라면 이상 수치로 간주
                    is_abnormal = False
                    
                    if t_judge in ['H', 'L', 'P', 'Pos', '+']:
                        is_abnormal = True
                    elif t_code in red_codes:
                        is_abnormal = True
                    # 결과값에 'High' 등의 텍스트가 포함된 경우 체크
                    elif "High" in str(t_rslt) or "Low" in str(t_rslt):
                        is_abnormal = True

                    if is_abnormal:
                        case_str = f"[{p_name}] {t_name}: {t_rslt} ({t_judge})"
                        abnormal_cases.append(case_str)
                        print(f"  🚨 발견: {case_str}")

        # 5. 결과 종합 및 카톡 전송
        if abnormal_cases:
            msg = f"📢 [이상 수치 알림]\n기준일: {yesterday}\n\n" + "\n".join(abnormal_cases)
            print("카톡 전송 중...")
            send_kakao_msg(msg)
        else:
            print("특이사항이 없습니다.")

    except Exception as e:
        print(f"에러 발생: {e}")

# ==========================================
# [스케줄러] 매일 아침 07:00에 실행
# ==========================================
print("🚀 자동 알림 봇이 시작되었습니다. (매일 07:00 실행)")

# 테스트를 위해 지금 즉시 한번 실행해보고 싶으면 아래 주석(#)을 지우세요
check_results()

schedule.every().day.at("07:00").do(check_results)

while True:
    schedule.run_pending()
>>>>>>> 6443ad1f5814a89c02d447b962b17928fe70af00
    time.sleep(60)