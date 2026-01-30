''' 제언문(조건문) '''
print("조건 전")
money = True
if money:
    print("버스를 타라")
    print("집 도착")

if not money:
    print("걸어가라")

print("조건 후")
print()
print("조건 전")
money = False
if money:
    print("버스를 타라")
    print("집 도착")
else:
    print("걸어가라")

print("조건 후")

# 비교 연산자
print(10 > 4)
print(4 < 10)
floor = 10
### 무조건 기준은 왼쪽!!!!!!!!!!!!!!
print(floor < 15)
print(15 > floor)
print(floor != 15)

'''
실습
ele1 = {floor: 10,
        status: up}
myfloor = 6
조건문

대기 시간: 
도착까지의 시간:

* 1층당 2초 소요
* 건물 총 14층까지 있음
'''
ele1 = {"floor": 5, "status" : "up"}
myfloor = 6

# # 엘리베이터 나보다 무조건 위에 있다는 가정
# # if ele1["status"] == "up":
# #     time = (14 - ele1["floor"]) * 2 + (14 - myfloor) * 2
# #     print("대기시간:", time)
# #     print("도착까지의 시간:", (time + (myfloor - 1) * 2))
# # else:
# #     time = (ele1["floor"] - myfloor) * 2
# #     print("대기시간:", time)
# #     print("도착까지의 시간:", (time + (myfloor - 1) * 2))

# 2. 엘리베이터 위치 상관없음
if ele1["status"] == "up":
    if myfloor < ele1['floor']:
        time = (14 - ele1["floor"]) * 2 + (14 - myfloor) * 2
        myTime = time + (myfloor - 1) * 2
    else:
        time = (myfloor - ele1["floor"]) * 2
        myTime = time + (myfloor - 1) * 2
else:
    if myfloor < ele1['floor'] :
        time = (ele1["floor"] - myfloor) * 2
        myTime = time + (myfloor - 1) * 2
    else:
        time = (ele1["floor"] - 1) * 2 + (myfloor - 1) * 2
        myTime = time + (myfloor - 1) * 2
print("대기시간:", time)
print("도착까지의 시간:", myTime)

if ele1["status"] == "up" and myfloor < ele1['floor']:
    time = (14 - ele1["floor"]) * 2 + (14 - myfloor) * 2
    myTime = time + (myfloor - 1) * 2
elif ele1["status"] == "up" and myfloor > ele1['floor']:
    time = (myfloor - ele1["floor"]) * 2
    myTime = time + (myfloor - 1) * 2
elif ele1["status"] == "down" and myfloor < ele1['floor']:
    time = (ele1["floor"] - myfloor) * 2
    myTime = time + (myfloor - 1) * 2
else:
    time = (ele1["floor"] - 1) * 2 + (myfloor - 1) * 2
    myTime = time + (myfloor - 1) * 2
print("대기시간:", time)
print("도착까지의 시간:", myTime)

'''
<회원가입>
*아이디:
*비밀번호(숫자 4자리):
*나이:
주소:
연락처:

단, 비밀번호에 숫자가 아닌 값이 있으면 회원가입x
    나이가 34세 초과일 시 회원가입 불가
'''
# print(input("이름: "))
# num1 = input("숫자1: ")
# num2 = input("숫자2: ")
# print(type(num2))
# print("num1 + num2:", (int(num1) + int(num2)))
#
# idFlag = False
# pwFlag = False
# addressFlag = False
# idFlag = True
# addressFlag = True
# (idFlag and pwFlag) or addressFlag

# inputId = input("아이디: ")
# inputPw = input("비밀번호(4자리): ")
# inputAge = input("나이: ")
# inputAddress = input("주소: ")
# inputPhone = input("연락처: ")
# idFlag = False
# pwFlag = False
# ageFlag = False
# numList = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
# if not inputId == "":
#     idFlag = True
#
# if len(inputPw) == 4 and inputPw[0] in numList and inputPw[1] in numList and inputPw[2] in numList and inputPw[3] in numList:
#     pwFlag = True
#
# if int(inputAge) <= 34:
#     ageFlag = True
#
# if idFlag and pwFlag and ageFlag:
#     print("회원가입 완료")
# elif not idFlag:
#     print("아이디 미충족")
#     print("회원가입 불가")
# elif not pwFlag:
#     print("비밀번호 미충족")
#     print("회원가입 불가")
# elif not ageFlag:
#     print("나이 미충족")
#     print("회원가입 불가")

'''
주제를 잡아서 만들기
1) 2주차
2) 3주차(+반복)
3) 4주차(+함수)
'''
'''
실습
leftShoulder
rightShoulder
RightHip
LeftHip
ex) rightShoulder = [0, 0]
위 4곳의 x,y 좌표를 받으시오
leftShoulder-x : 100
leftShoulder-y : 300
단계(보통(80점)(3% 이내), 경고(50점)(5%이내), 위험(10점)(그 외))
어깨 좌우축 상태: 보통
골반 좌우축 상태: 경고
척추 곧음 정도: 경고
종합 점수: 60점
'''
leftShoulder = [103, 301]
rightShoulder = [3, 300]
RightHip = [30, 220]
LeftHip = [70, 208]

shoulderDegree = (leftShoulder[1] - rightShoulder[1]) / (leftShoulder[0] - rightShoulder[0])

if shoulderDegree > -0.03  and shoulderDegree < 0.03:
    shoulderResult = "보통"
    shoulderScore = 80
elif shoulderDegree > -0.05  and shoulderDegree < 0.05:
    shoulderResult = "경고"
    shoulderScore = 50
else:
    shoulderResult = "위험"
    shoulderScore = 10

HipDegree = (LeftHip[1] - RightHip[1]) / (LeftHip[0] - RightHip[0])

if HipDegree > -0.03  and HipDegree < 0.03:
    hipResult = "보통"
    hipScore = 80
elif HipDegree > -0.05  and HipDegree < 0.05:
    hipResult = "경고"
    hipScore = 50
else:
    hipResult = "위험"
    hipScore = 10

shoulderCenter = [(leftShoulder[0] + rightShoulder[0]) / 2, (leftShoulder[1] + rightShoulder[1]) / 2]

hipCenter = [(LeftHip[0] + RightHip[0]) / 2, (LeftHip[1] + RightHip[1]) / 2]

spineDegree = (shoulderCenter[0] - hipCenter[0]) / (shoulderCenter[1] - hipCenter[1])

if spineDegree > -0.03  and spineDegree < 0.03:
    spineResult = "보통"
    spineScore = 80
elif spineDegree > -0.05  and spineDegree < 0.05:
    spineResult = "경고"
    spineScore = 50
else:
    spineResult = "위험"
    spineScore = 10

print("어깨:", shoulderResult)
print("골반:", hipResult)
print("척추:", spineResult)
print("종합점수:", (shoulderScore + hipScore + spineScore) / 3)
'''
학점 계산기
점수: 70(입력)
학점: C학점

89점 초과 A학점
79점 초과 B학점
69점 초과 C학점
59점 초과 D학점
나머지는 F학점
* 점수 0보다 작거나 100보다 "계산불가" 출력

59 < score < 69
59 < score and score < 69
'''
# score = int(input("점수: "))
# if score < 0 or score > 100:
#     result = "계산 불가"
# elif score > 89:
#     result = "A 학점"
# elif score > 79:
#     result = "i 학점"
# elif score > 69:
#     result = "C 학점"
# elif score > 59:
#     result = "D 학점"
# else:
#     result = "F 학점"
# print("학점:", result)

num = 10
num = num + 1
print(num)

num += 1
print(num)

num += 10
print(num)

print("반복 전")
human = 0
while human < 20:
    human = human + 1
    print("%d 번째 학생입니다." %human)
print("반복 후")

'''
1월 17일
1월 18일
1월 19일
...
1월 31일
'''

day = 0 # 초기문
while day < 15: # 조건식(문) * 반복횟수!!!
    realDay = day + 17
    print("1월 %d일" %realDay) # 실행문
    day += 1 # 후처리문


coffee = 500
milk = 3000
print("어서오세요 코리아카페입니다.")
select = input("주문할 음료를 선택해주세요(1.아메리카노, 2.라떼, 3.패션후르츠):")
num = int(input("주문할 음료의 갯수를 입력하십시오: "))

if select == "1":
    menu = "아메리카노"
elif select == "2":
    menu = "라떼"
elif select == "3":
    menu = "패션후르츠"

i = 0
while i < num:
    if select == "1":
        coffee -= 45
    elif select == "2":
        coffee -= 45
        milk -= 400
    print(menu + " 한잔 나왔습니다.")
    i += 1
print("[재고]")
print("우유:", milk, "ml")
print("원두:", coffee, "g")
'''
[재고]
우유: 3000ml
원두: 500g
[소비량]
아메리카노: 원두 45g
라떼: 원두 45g, 우유 400ml
어서오세요 코리아카페입니다.
주문할 음료를 선택해주세요(1.아메리카노, 2.라떼, 3.패션후르츠): 2
주문할 음료의 갯수를 입력하십시오: 2
라떼 한잔 나왔습니다.
라떼 한잔 나왔습니다.
[재고]
우유: 2200ml
원두: 410g
'''
'''
'''
print("반복 전")
i = 0
num = 100
while i < num:
    print(i)
    i += 1
    if i == 8:
        break

print("반복 후")















