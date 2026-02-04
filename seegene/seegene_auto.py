import time
import schedule
import json
import tempfile
import shutil
import requests
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================
# [설정] 아래 정보를 입력해주세요
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

def wait_and_dismiss_popup(driver, label, timeout=10):
    """사이트 팝업의 '확인' 버튼을 polling하여 클릭 (delayed render에 대응)"""
    for attempt in range(timeout):
        result = driver.execute_script("""
            // 1단계: button/a/input 중 텍스트가 정확히 '확인'인 것
            var clickables = document.querySelectorAll('button, a, input');
            for (var i = 0; i < clickables.length; i++) {
                if (clickables[i].offsetParent !== null) {
                    var t = (clickables[i].value || clickables[i].textContent || '').trim();
                    if (t === '확인') { clickables[i].click(); return 'clicked:' + clickables[i].tagName; }
                }
            }
            // 2단계: 모든 leaf 요소 중 텍스트가 '확인'인 것 → 클릭
            var all = document.querySelectorAll('*');
            for (var i = 0; i < all.length; i++) {
                if (all[i].children.length === 0 && all[i].offsetParent !== null && all[i].textContent.trim() === '확인') {
                    all[i].click();
                    return 'clicked_leaf:' + all[i].tagName + '.' + all[i].className;
                }
            }
            return 'not_found';
        """)
        if result != 'not_found':
            print(f"[DEBUG] [{label}] popup dismiss: {result} ({attempt}초 후)")
            return True
        time.sleep(1)
    print(f"[DEBUG] [{label}] '확인' 버튼 {timeout}초 내 발견 안됨")
    return False

def job():
    print(f"\n[{datetime.datetime.now()}] 🤖 로봇이 작업을 시작합니다...")

    # 1. 크롬 브라우저 열기 (임시 프로필 → 저장된 비밀번호 없음 → breach 팝업 불가)
    temp_dir = tempfile.mkdtemp(prefix="seegene_chrome_")
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={temp_dir}")
    # options.add_argument("--headless") # 나중에 잘 되면 이 주석을 푸세요 (화면 없이 실행)
    options.add_argument("--disable-password-manager")
    options.add_argument("--password-store=none")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-features=SafeBrowsing,PasswordLeakDetection,SafeBrowsingPasswordLeakDetection,PasswordReuse,AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "safe_browsing.enabled": False,
        "profile.password_leak_detection_enabled": False,
        "password_manager.leak_detection_enabled": False,
    })

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 2. 로그인 페이지 접속
        driver.get("https://srms.seegenemedical.com")

        # 3. 아이디/비번 입력 (수정된 부분!)
        print("🔑 로그인을 시도합니다...")
        wait = WebDriverWait(driver, 10)

        # (1) 아이디 입력칸 찾기 (찾아주신 headerId 사용)
        # [DEBUG] 페이지 상태 확인
        print(f"[DEBUG] page title: {driver.title}")
        print(f"[DEBUG] current URL: {driver.current_url}")
        driver.save_screenshot(r"C:\Users\JSS\coding_python\seegene\seegene_debug.png")
        print("[DEBUG] 스크린샷 저장완료")

        # (1) JS로 아이디/비번 값 설정 + 이벤트 발생
        wait.until(EC.presence_of_element_located((By.ID, "headerId")))

        # headerId 주변 폼 구조 확인 (비밀번호 필드 ID 파악)
        form_info = driver.execute_script("""
            var idEl = document.getElementById('headerId');
            var form = idEl.closest('form') || idEl.closest('table');
            var inputs = form ? form.querySelectorAll('input') : [];
            var result = [];
            inputs.forEach(function(el) { result.push({id: el.id, name: el.name, type: el.type}); });
            return result;
        """)
        print(f"[DEBUG] headerId 폼 내 input 목록: {form_info}")

        driver.execute_script("""
            function setNativeValue(element, value) {
                var valueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                valueSetter.call(element, value);
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }
            setNativeValue(document.getElementById('headerId'), arguments[0]);
            // 비밀번호 필드는 headerId와 같은 폼/테이블 안의 password 타입
            var idEl = document.getElementById('headerId');
            var container = idEl.closest('form') || idEl.closest('table');
            var pwField = container ? container.querySelector("input[type='password']") : document.querySelector("input[type='password']");
            if (pwField) setNativeValue(pwField, arguments[1]);
        """, USER_ID, USER_PW)
        print("[DEBUG] 아이디/비번 값 설정완료 (native setter + event)")

        # (2) btnLogin 클릭 (headerId 폼과 매칭되는 버튼)
        driver.execute_script("document.getElementById('btnLogin').click();")
        print("[DEBUG] btnLogin 클릭완료")

        # (3) Alert 처리
        time.sleep(2)
        try:
            alert = driver.switch_to.alert
            print(f"[DEBUG] Alert 메시지: {alert.text}")
            alert.accept()
        except:
            pass

        # 로그인 후 페이지 전환 대기
        time.sleep(5)
        driver.save_screenshot(r"C:\Users\JSS\coding_python\seegene\seegene_after_login.png")
        print(f"[DEBUG] 로그인후 URL: {driver.current_url}")
        print("[DEBUG] 로그인후 스크린샷 저장: seegene_after_login.png")
        print("✅ 로그인 성공! 데이터를 조회합니다.")

        # 4. 팝업 dismiss — polling (delayed render에 대응, "비밀번호 변경" 등)
        wait_and_dismiss_popup(driver, "main.do", timeout=8)

        # 5. rstUser.do 페이지로 이동 (세션 상태 안정화)
        driver.get("https://srms.seegenemedical.com/rstUser.do")
        time.sleep(3)

        # rstUser.do 팝업 dismiss — polling
        wait_and_dismiss_popup(driver, "rstUser.do", timeout=10)

        driver.save_screenshot(r"C:\Users\JSS\coding_python\seegene\seegene_rstUser.png")
        print("[DEBUG] rstUser.do 스크린샷 저장완료")

        # 6. 데이터 조회 (날짜: 어제)
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # [진단] 사이트 자체 "조회" 클릭 시 실제 XHR 캡처 → body/응답 비교용
        page_info = driver.execute_script("""
            var inputs = document.querySelectorAll('input, select');
            var r = [];
            for (var i = 0; i < inputs.length; i++) {
                var n = inputs[i].name || inputs[i].id;
                if (n) r.push(inputs[i].tagName + '[' + n + ']=' + inputs[i].value);
            }
            return r;
        """)
        print(f"[DEBUG] 페이지 inputs: {page_info}")

        # 날짜 필드를 어제로 세팅 (사이트 폼 기준: I_FDT, I_TDT 등 공통 패턴)
        date_set_res = driver.execute_script("""
            var yesterday = arguments[0]; // "YYYY-MM-DD"
            var set = [];
            var dateFields = ['I_FDT','I_TDT','sFDT','sTDT','sDate','eDate','fromDate','toDate'];
            dateFields.forEach(function(name) {
                var el = document.querySelector('input[name="'+name+'"]') || document.getElementById(name);
                if (el) { el.value = yesterday; set.push(name); }
            });
            // 날짜 필드 이름이 다를 경우 date/text 타입 input 전체를 어제로 세팅
            if (set.length === 0) {
                document.querySelectorAll('input').forEach(function(el) {
                    if ((el.type === 'date' || el.type === 'text') && /\\d{4}[-\\/.]\\d{2}/.test(el.value)) {
                        el.value = yesterday; set.push(el.name || el.id || 'unnamed');
                    }
                });
            }
            return set;
        """, yesterday)
        print(f"[DEBUG] 날짜 세팅: {date_set_res}")

        # XHR + fetch 인터셉터 주입 (응답 50KB 캡처, rstUserList body 템플릿 저장)
        driver.execute_script("""
            window._xlog = [];
            window._xbody = null; // rstUserList 요청 body 템플릿 저장용
            // --- XHR 인터셉 ---
            var _oO = XMLHttpRequest.prototype.open;
            var _oS = XMLHttpRequest.prototype.send;
            XMLHttpRequest.prototype.open = function(method, url) {
                this._xUrl = url; this._xMethod = method;
                return _oO.apply(this, arguments);
            };
            XMLHttpRequest.prototype.send = function(body) {
                var self = this;
                var sendBody = body ? body.toString() : null;
                // rstUserList 첫 번째 요청의 body를 템플릿으로 저장
                if (!window._xbody && self._xUrl && self._xUrl.indexOf('rstUserList') !== -1 && sendBody) {
                    window._xbody = sendBody;
                }
                self.addEventListener('load', function() {
                    window._xlog.push({ url: self._xUrl, method: self._xMethod, body: sendBody, status: self.status, response: self.responseText ? self.responseText.substring(0, 50000) : null, src: 'xhr' });
                });
                return _oS.apply(this, [body]);
            };
            // --- fetch 인터셉 ---
            var _oF = window.fetch;
            window.fetch = function(url, opts) {
                var method = (opts && opts.method) || 'GET';
                var body = (opts && opts.body) || null;
                return _oF.apply(this, arguments).then(function(resp) {
                    resp.clone().text().then(function(text) {
                        window._xlog.push({ url: (typeof url === 'string' ? url : url.url), method: method, body: body ? body.toString() : null, status: resp.status, response: text ? text.substring(0, 50000) : null, src: 'fetch' });
                    });
                    return resp;
                });
            };
            // --- jQuery hook ---
            if (window.jQuery) {
                jQuery(document).ajaxComplete(function(e, xhr, s) {
                    window._xlog.push({ url: s.url, method: s.type, body: s.data || null, status: xhr.status, response: xhr.responseText ? xhr.responseText.substring(0, 50000) : null, src: 'jquery' });
                });
            }
        """)

        # "조회" 버튼 클릭 → 사이트가 자체 API 호출 (button, input[type=button], input[type=submit] 모두 탐색)
        click_res = driver.execute_script("""
            var clickables = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
            for (var i = 0; i < clickables.length; i++) {
                var t = (clickables[i].value || clickables[i].textContent || '').trim();
                if (t === '조회') { clickables[i].click(); return 'clicked:' + clickables[i].tagName + (clickables[i].id ? '#'+clickables[i].id : ''); }
            }
            return 'not_found';
        """)
        print(f"[DEBUG] 조회 클릭: {click_res}")
        time.sleep(3)

        # 캡처된 XHR 로그 출력
        xhr_log = json.loads(driver.execute_script("return JSON.stringify(window._xlog);"))
        print(f"[DEBUG] XHR Log ({len(xhr_log)}건):")
        for entry in xhr_log:
            print(f"  [{entry.get('method','?')}] {entry.get('url','?')}")
            if entry.get('body'): print(f"    body: {entry['body']}")
            if entry.get('response'): print(f"    resp: {entry['response'][:500]}")

        # body 템플릿 회수 (rstUserDtl 호출 시 사용)
        body_template = driver.execute_script("return window._xbody;")
        print(f"[DEBUG] Body 템플릿: {len(body_template)}자" if body_template else "[DEBUG] Body 템플릿: 캡처 안됨")

        # rstUserList 응답에서 환자 목록 추출 (배열 키 동적 탐색)
        patients = []
        for entry in xhr_log:
            if 'rstUserList' in str(entry.get('url', '')) and entry.get('response'):
                try:
                    resp = json.loads(entry['response'])
                    if isinstance(resp, dict):
                        if 'strMessage' in resp:
                            print(f"[DEBUG] 사이트 API 메시지: {resp['strMessage']}")
                        # 배열 값 중 환자 객체(DAT/JNO/NAM 포함)를 포함하는 키 탐색
                        for key, value in resp.items():
                            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                                if any(k in value[0] for k in ['DAT', 'JNO', 'NAM']):
                                    patients = value
                                    print(f"[DEBUG] 환자 목록 키: '{key}', {len(patients)}명")
                                    break
                        if not patients:
                            print(f"[DEBUG] 환자 배열 키 미발견. 응답 최상위 키: {list(resp.keys())}")
                    elif isinstance(resp, list):
                        patients = resp
                except Exception as e:
                    print(f"[DEBUG] 응답 파싱 실패: {e}")
                break
        if not patients:
            print("[DEBUG] rstUserList 캡처 안됨 또는 결과 없음")

        if isinstance(patients, list) and len(patients) > 0:
            print(f"총 {len(patients)}명의 환자 발견. 상세 분석 중...")
            abnormal_cases = []

            for p in patients:
                # 상세 결과 요청 — body 템플릿에서 I_DAT/I_JNO만 교체
                dtl_response = driver.execute_script("""
                    var body = new URLSearchParams(arguments[3]);
                    body.set('I_DAT', arguments[0] || '');
                    body.set('I_JNO', arguments[1] || '');
                    body.set('I_HOS', arguments[2] || '');
                    body.set('I_ECF', 'N');
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', '/rstUserDtl.do', false);
                    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
                    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
                    xhr.send(body.toString());
                    return xhr.responseText;
                """, p.get('DAT'), p.get('JNO'), USER_ID, body_template)
                dtl_data = json.loads(dtl_response)

                # 동적 래퍼 키 처리 (예: {"param_rstUserMw106rm3": {...}})
                if isinstance(dtl_data, dict):
                    wrapper_keys = [k for k in dtl_data if k.startswith('param_')]
                    if wrapper_keys:
                        dtl_data = dtl_data[wrapper_keys[0]]

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
                full_msg = f"📢 [이상 수치 알림]\n{yesterday} 결과 ({len(abnormal_cases)}건)\n\n" + "\n".join(abnormal_cases)
                send_kakao_msg(full_msg)
                print("📩 카카오톡 전송 완료!")
            else:
                print("👍 특이사항(이상 수치)이 없습니다.")
        else:
            print("ℹ️ 조회된 환자가 없거나 아직 결과가 나오지 않았습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
    finally:
        driver.quit() # 작업 끝난 브라우저 닫기
        shutil.rmtree(temp_dir, ignore_errors=True) # 임시 프로필 정리

# --- 스케줄러 실행 ---
print("🚀 자동 로그인 봇 시작! (매일 07:00 실행)")

# 테스트를 위해 '지금 당장' 한번 실행합니다.
job()

# 매일 아침 7시 예약
schedule.every().day.at("07:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
