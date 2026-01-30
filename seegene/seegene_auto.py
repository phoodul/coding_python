<<<<<<< HEAD
import time
import schedule
import json
import requests
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================
# [설정] 선생님의 정보를 입력해주세요
# ==========================================
USER_ID = "29114"       
USER_PW = "29114"     
KAKAO_TOKEN = "jVEzB2jXs_r12o74tidYYN7yUGm2DheBAAAAAQoXC9cAAAGbIq-NtR7SOb8w2j0_"
# ==========================================

def send_kakao_msg(text):
    """카카오톡 전송 함수"""
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
    requests.post(url, headers=headers, data=data)

def job():
    print(f"\n[{datetime.datetime.now()}] 🤖 로봇이 작업을 시작합니다...")
    
    # 1. 크롬 브라우저 열기
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # 나중에 잘 되면 이 주석을 푸세요 (화면 없이 실행)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 2. 로그인 페이지 접속
        driver.get("https://srms.seegenemedical.com")
        
        # 3. 아이디/비번 입력 (수정된 부분!)
        print("🔑 로그인을 시도합니다...")
        wait = WebDriverWait(driver, 10)
        
        # (1) 아이디 입력칸 찾기 (찾아주신 headerId 사용)
        id_box = wait.until(EC.presence_of_element_located((By.ID, "headerId")))
        id_box.clear()
        id_box.send_keys(USER_ID)
        
        # (2) 비밀번호 입력칸 찾기 (만능키: type='password'인 칸을 찾음)
        pw_box = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        pw_box.clear()
        pw_box.send_keys(USER_PW)
        
        # (3) 엔터키로 로그인
        pw_box.submit()
        
        # 로그인 후 페이지 전환 대기
        time.sleep(5) 
        print("✅ 로그인 성공! 데이터를 조회합니다.")

        # 4. 브라우저의 로그인 정보(쿠키)를 가져옴
        session = requests.Session()
        cookies = driver.get_cookies()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
            
        # 5. 데이터 조회 (날짜: 어제)
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        # (API 요청시 브라우저인 척 속이기 위한 헤더)
        headers = {
            "User-Agent": driver.execute_script("return navigator.userAgent;"),
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://srms.seegenemedical.com/rstUser.do"
        }
        
        # 환자 목록 요청
        list_url = "https://srms.seegenemedical.com/rstUserList.do"
        payload = {
            "I_LOGMNU": "RSTUSER",
            "I_FDT": yesterday,
            "I_TDT": yesterday,
            "I_FNM": "동래나눔과행복병원", 
            "I_PHOS": "29114",
            "I_CNT": "100",
            "I_LNG": "KOR"
        }
        
        res = session.post(list_url, headers=headers, data=payload)
        patients = res.json()

        if isinstance(patients, list) and len(patients) > 0:
            print(f"총 {len(patients)}명의 환자 발견. 상세 분석 중...")
            abnormal_cases = []

            for p in patients:
                # 상세 결과 요청
                dtl_url = "https://srms.seegenemedical.com/rstUserDtl.do"
                dtl_payload = {
                    "I_DAT": p.get('DAT'),
                    "I_JNO": p.get('JNO'),
                    "I_HOS": p.get('HOS'),
                    "I_LOGMNU": "RSTUSER",
                    "I_ECF": "N"
                }
                res_dtl = session.post(dtl_url, headers=headers, data=dtl_payload)
                dtl_data = res_dtl.json()
                
                # 이상 수치 필터링
                results = dtl_data.get('rstUserDtl', [])
                red_list = dtl_data.get('redTxtList', [])
                red_codes = [r.get('R003GCD') for r in red_list]

                for item in results:
                    is_abnormal = False
                    judge = item.get('JUDGE', '')
                    code = item.get('GCD', '')
                    rslt = item.get('RSLT', '')
                    
                    if judge in ['H', 'L', 'P', 'Pos', '+']: is_abnormal = True
                    if code in red_codes: is_abnormal = True
                    if "High" in str(rslt) or "Low" in str(rslt): is_abnormal = True
                    
                    if is_abnormal:
                        msg = f"[{p.get('NAM')}] {item.get('TNM')}: {rslt} ({judge})"
                        abnormal_cases.append(msg)
                        print(f"  🚨 {msg}")

            if abnormal_cases:
                # 카톡 내용이 너무 길면 잘릴 수 있으므로 나누거나 요약
                full_msg = f"📢 [이상 수치 알림]\n{yesterday} 결과 ({len(abnormal_cases)}건)\n\n" + "\n".join(abnormal_cases)
                send_kakao_msg(full_msg)
                print("📩 카카오톡 전송 완료!")
            else:
                print("👍 특이사항(이상 수치)이 없습니다.")
        else:
            print(ℹ️ 조회된 환자가 없거나 아직 결과가 나오지 않았습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
    finally:
        driver.quit() # 작업 끝난 브라우저 닫기

# --- 스케줄러 실행 ---
print("🚀 자동 로그인 봇 시작! (매일 07:00 실행)")

# 테스트를 위해 '지금 당장' 한번 실행합니다.
job() 

# 매일 아침 7시 예약
schedule.every().day.at("07:00").do(job)

while True:
    schedule.run_pending()
=======
import time
import schedule
import json
import requests
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================
# [설정] 선생님의 정보를 입력해주세요
# ==========================================
USER_ID = "29114"       
USER_PW = "29114"     
KAKAO_TOKEN = "jVEzB2jXs_r12o74tidYYN7yUGm2DheBAAAAAQoXC9cAAAGbIq-NtR7SOb8w2j0_"
# ==========================================

def send_kakao_msg(text):
    """카카오톡 전송 함수"""
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
    requests.post(url, headers=headers, data=data)

def job():
    print(f"\n[{datetime.datetime.now()}] 🤖 로봇이 작업을 시작합니다...")
    
    # 1. 크롬 브라우저 열기
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # 나중에 잘 되면 이 주석을 푸세요 (화면 없이 실행)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 2. 로그인 페이지 접속
        driver.get("https://srms.seegenemedical.com")
        
        # 3. 아이디/비번 입력 (수정된 부분!)
        print("🔑 로그인을 시도합니다...")
        wait = WebDriverWait(driver, 10)
        
        # (1) 아이디 입력칸 찾기 (찾아주신 headerId 사용)
        id_box = wait.until(EC.presence_of_element_located((By.ID, "headerId")))
        id_box.clear()
        id_box.send_keys(USER_ID)
        
        # (2) 비밀번호 입력칸 찾기 (만능키: type='password'인 칸을 찾음)
        pw_box = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        pw_box.clear()
        pw_box.send_keys(USER_PW)
        
        # (3) 엔터키로 로그인
        pw_box.submit()
        
        # 로그인 후 페이지 전환 대기
        time.sleep(5) 
        print("✅ 로그인 성공! 데이터를 조회합니다.")

        # 4. 브라우저의 로그인 정보(쿠키)를 가져옴
        session = requests.Session()
        cookies = driver.get_cookies()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
            
        # 5. 데이터 조회 (날짜: 어제)
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        # (API 요청시 브라우저인 척 속이기 위한 헤더)
        headers = {
            "User-Agent": driver.execute_script("return navigator.userAgent;"),
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://srms.seegenemedical.com/rstUser.do"
        }
        
        # 환자 목록 요청
        list_url = "https://srms.seegenemedical.com/rstUserList.do"
        payload = {
            "I_LOGMNU": "RSTUSER",
            "I_FDT": yesterday,
            "I_TDT": yesterday,
            "I_FNM": "동래나눔과행복병원", 
            "I_PHOS": "29114",
            "I_CNT": "100",
            "I_LNG": "KOR"
        }
        
        res = session.post(list_url, headers=headers, data=payload)
        patients = res.json()

        if isinstance(patients, list) and len(patients) > 0:
            print(f"총 {len(patients)}명의 환자 발견. 상세 분석 중...")
            abnormal_cases = []

            for p in patients:
                # 상세 결과 요청
                dtl_url = "https://srms.seegenemedical.com/rstUserDtl.do"
                dtl_payload = {
                    "I_DAT": p.get('DAT'),
                    "I_JNO": p.get('JNO'),
                    "I_HOS": p.get('HOS'),
                    "I_LOGMNU": "RSTUSER",
                    "I_ECF": "N"
                }
                res_dtl = session.post(dtl_url, headers=headers, data=dtl_payload)
                dtl_data = res_dtl.json()
                
                # 이상 수치 필터링
                results = dtl_data.get('rstUserDtl', [])
                red_list = dtl_data.get('redTxtList', [])
                red_codes = [r.get('R003GCD') for r in red_list]

                for item in results:
                    is_abnormal = False
                    judge = item.get('JUDGE', '')
                    code = item.get('GCD', '')
                    rslt = item.get('RSLT', '')
                    
                    if judge in ['H', 'L', 'P', 'Pos', '+']: is_abnormal = True
                    if code in red_codes: is_abnormal = True
                    if "High" in str(rslt) or "Low" in str(rslt): is_abnormal = True
                    
                    if is_abnormal:
                        msg = f"[{p.get('NAM')}] {item.get('TNM')}: {rslt} ({judge})"
                        abnormal_cases.append(msg)
                        print(f"  🚨 {msg}")

            if abnormal_cases:
                # 카톡 내용이 너무 길면 잘릴 수 있으므로 나누거나 요약
                full_msg = f"📢 [이상 수치 알림]\n{yesterday} 결과 ({len(abnormal_cases)}건)\n\n" + "\n".join(abnormal_cases)
                send_kakao_msg(full_msg)
                print("📩 카카오톡 전송 완료!")
            else:
                print("👍 특이사항(이상 수치)이 없습니다.")
        else:
            print(ℹ️ 조회된 환자가 없거나 아직 결과가 나오지 않았습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
    finally:
        driver.quit() # 작업 끝난 브라우저 닫기

# --- 스케줄러 실행 ---
print("🚀 자동 로그인 봇 시작! (매일 07:00 실행)")

# 테스트를 위해 '지금 당장' 한번 실행합니다.
job() 

# 매일 아침 7시 예약
schedule.every().day.at("07:00").do(job)

while True:
    schedule.run_pending()
>>>>>>> 6443ad1f5814a89c02d447b962b17928fe70af00
    time.sleep(60)