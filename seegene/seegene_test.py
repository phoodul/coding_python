<<<<<<< HEAD
import requests
import json
import datetime

# --- 설정 구간 ---
# 어제 날짜를 자동으로 구합니다 (검사일 기준)
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
print(f"검색 기준일: {yesterday}")

# 1. 헤더 및 쿠키 (방금 주신 최신 정보 적용)
headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "origin": "https://srms.seegenemedical.com",
    "referer": "https://srms.seegenemedical.com/rstUser.do",
    "ajax": "true",
    # JSESSIONID가 바뀌었다면 아래 Cookie를 수정해야 합니다.
    "Cookie": "visid_incap_2839813=4tA2B+1IQgCzRr5wRfbJF1I9PGkAAAAAQUIPAAAAAAAAgIY31+5zygrvXWTMX4Xh; _ga=GA1.1.2040753655.1765555540; WMONID=QfjBSdpABVQ; visid_incap_3209525=avc6JaUsQLSUdYHbZJ4tEls9PGkAAAAAQUIPAAAAAAB07wTx70oz9io+oXeYVduP; visid_incap_2845396=7DVo7wiUTdOjadEyc5zaK1w9PGkAAAAAQUIPAAAAAAAUYNDJG8k6ZRVCK+u7aWGT; JSESSIONID=F95177E4E5B711F12BB40478E27884CC.was2; ROUTEID=route.was2; incap_ses_950_2839813=CXAkGua2ilM8wwhDbhQvDU0fQGkAAAAA87i49vjit7F/8J0xMK3MMg==; incap_ses_950_3209525=eSwaI3uyVSL9xQhDbhQvDVMfQGkAAAAArQtAxPJsJNAmTyN1kHrmoQ==; _ga_61EJYGRKLW=GS2.1.s1765809998$o4$g0$t1765810003$j55$l0$h0; incap_ses_950_2845396=VEJmVW07mz9exghDbhQvDVMfQGkAAAAAOgOMhDSJexww7gkdHHugEg=="
}

# 2. 수진자 목록 가져오기 (rstUserList.do)
list_url = "https://srms.seegenemedical.com/rstUserList.do"
# 테스트를 위해 날짜를 12월 13일~15일로 고정 (나중에 자동화 시 yesterday 변수 사용)
list_payload = {
    "I_LOGMNU": "RSTUSER",
    "I_LOGMNM": "수진자별 결과관리",
    "I_FDT": "2025-12-13",
    "I_TDT": "2025-12-15",
    "I_FNM": "동래나눔과행복병원",
    "I_PHOS": "29114",
    "I_CNT": "40",
    "I_ROW": "0",
    "I_LNG": "KOR"
}

try:
    print("1. 환자 목록을 조회합니다...")
    res_list = requests.post(list_url, headers=headers, data=list_payload)
    data_list = res_list.json()

    if len(data_list) > 0:
        target_patient = data_list[0] # 첫 번째 환자 선택
        name = target_patient.get('NAM')
        # 목록에서 필요한 정보 추출 (상세조회용)
        p_dat = target_patient.get('DAT') # 접수일자
        p_jno = target_patient.get('JNO') # 접수번호
        p_hos = target_patient.get('HOS') # 병원코드
        
        print(f"--> 환자 발견: {name} (접수번호: {p_jno})")
        print("2. 상세 결과(rstUserDtl.do)를 조회합니다...")

        # 3. 상세 결과 가져오기 (rstUserDtl.do)
        dtl_url = "https://srms.seegenemedical.com/rstUserDtl.do"
        dtl_payload = {
            "I_DAT": p_dat,  # 목록에서 가져온 값
            "I_JNO": p_jno,  # 목록에서 가져온 값
            "I_HOS": p_hos,  # 목록에서 가져온 값
            "I_LOGMNU": "RSTUSER",
            "I_ECF": "N"
        }
        
        res_dtl = requests.post(dtl_url, headers=headers, data=dtl_payload)
        data_dtl = res_dtl.json()
        
        print("\n[중요] 아래 데이터를 복사해서 알려주세요!\n")
        # 보기 좋게 출력 (한글 깨짐 방지)
        print(json.dumps(data_dtl[0:2], indent=4, ensure_ascii=False)) 

    else:
        print("조회된 환자가 없습니다. 날짜나 쿠키를 확인해주세요.")

except Exception as e:
=======
import requests
import json
import datetime

# --- 설정 구간 ---
# 어제 날짜를 자동으로 구합니다 (검사일 기준)
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
print(f"검색 기준일: {yesterday}")

# 1. 헤더 및 쿠키 (방금 주신 최신 정보 적용)
headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "origin": "https://srms.seegenemedical.com",
    "referer": "https://srms.seegenemedical.com/rstUser.do",
    "ajax": "true",
    # JSESSIONID가 바뀌었다면 아래 Cookie를 수정해야 합니다.
    "Cookie": "visid_incap_2839813=4tA2B+1IQgCzRr5wRfbJF1I9PGkAAAAAQUIPAAAAAAAAgIY31+5zygrvXWTMX4Xh; _ga=GA1.1.2040753655.1765555540; WMONID=QfjBSdpABVQ; visid_incap_3209525=avc6JaUsQLSUdYHbZJ4tEls9PGkAAAAAQUIPAAAAAAB07wTx70oz9io+oXeYVduP; visid_incap_2845396=7DVo7wiUTdOjadEyc5zaK1w9PGkAAAAAQUIPAAAAAAAUYNDJG8k6ZRVCK+u7aWGT; JSESSIONID=F95177E4E5B711F12BB40478E27884CC.was2; ROUTEID=route.was2; incap_ses_950_2839813=CXAkGua2ilM8wwhDbhQvDU0fQGkAAAAA87i49vjit7F/8J0xMK3MMg==; incap_ses_950_3209525=eSwaI3uyVSL9xQhDbhQvDVMfQGkAAAAArQtAxPJsJNAmTyN1kHrmoQ==; _ga_61EJYGRKLW=GS2.1.s1765809998$o4$g0$t1765810003$j55$l0$h0; incap_ses_950_2845396=VEJmVW07mz9exghDbhQvDVMfQGkAAAAAOgOMhDSJexww7gkdHHugEg=="
}

# 2. 수진자 목록 가져오기 (rstUserList.do)
list_url = "https://srms.seegenemedical.com/rstUserList.do"
# 테스트를 위해 날짜를 12월 13일~15일로 고정 (나중에 자동화 시 yesterday 변수 사용)
list_payload = {
    "I_LOGMNU": "RSTUSER",
    "I_LOGMNM": "수진자별 결과관리",
    "I_FDT": "2025-12-13",
    "I_TDT": "2025-12-15",
    "I_FNM": "동래나눔과행복병원",
    "I_PHOS": "29114",
    "I_CNT": "40",
    "I_ROW": "0",
    "I_LNG": "KOR"
}

try:
    print("1. 환자 목록을 조회합니다...")
    res_list = requests.post(list_url, headers=headers, data=list_payload)
    data_list = res_list.json()

    if len(data_list) > 0:
        target_patient = data_list[0] # 첫 번째 환자 선택
        name = target_patient.get('NAM')
        # 목록에서 필요한 정보 추출 (상세조회용)
        p_dat = target_patient.get('DAT') # 접수일자
        p_jno = target_patient.get('JNO') # 접수번호
        p_hos = target_patient.get('HOS') # 병원코드
        
        print(f"--> 환자 발견: {name} (접수번호: {p_jno})")
        print("2. 상세 결과(rstUserDtl.do)를 조회합니다...")

        # 3. 상세 결과 가져오기 (rstUserDtl.do)
        dtl_url = "https://srms.seegenemedical.com/rstUserDtl.do"
        dtl_payload = {
            "I_DAT": p_dat,  # 목록에서 가져온 값
            "I_JNO": p_jno,  # 목록에서 가져온 값
            "I_HOS": p_hos,  # 목록에서 가져온 값
            "I_LOGMNU": "RSTUSER",
            "I_ECF": "N"
        }
        
        res_dtl = requests.post(dtl_url, headers=headers, data=dtl_payload)
        data_dtl = res_dtl.json()
        
        print("\n[중요] 아래 데이터를 복사해서 알려주세요!\n")
        # 보기 좋게 출력 (한글 깨짐 방지)
        print(json.dumps(data_dtl[0:2], indent=4, ensure_ascii=False)) 

    else:
        print("조회된 환자가 없습니다. 날짜나 쿠키를 확인해주세요.")

except Exception as e:
>>>>>>> 6443ad1f5814a89c02d447b962b17928fe70af00
    print(f"에러 발생: {e}")