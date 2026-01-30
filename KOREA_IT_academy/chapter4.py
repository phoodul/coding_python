# ''' 제언문(조건문) '''
# print("조건 전")
# money = True
# if money:
#     print("버스를 타라")
#     print("집 도착")
#
# if not money:
#     print("걸어가라")
#
# print("조건 후")
# print()
# print("조건 전")
# money = False
# if money:
#     print("버스를 타라")
#     print("집 도착")
# else:
#     print("걸어가라")
#
# print("조건 후")
#
# # 비교 연산자
# print(10 > 4)
# print(4 < 10)
# floor = 10
# ### 무조건 기준은 왼쪽!!!!!!!!!!!!!!
# print(floor < 15)
# print(15 > floor)
# print(floor != 15)
#
# '''
# 실습
# ele1 = {floor: 10,
#         status: up}
# myfloor = 6
# 조건문
#
# 대기 시간:
# 도착까지의 시간:
#
# * 1층당 2초 소요
# * 건물 총 14층까지 있음
# '''
# ele1 = {"floor": 5, "status" : "up"}
# myfloor = 6
#
# # # 엘리베이터 나보다 무조건 위에 있다는 가정
# # # if ele1["status"] == "up":
# # #     time = (14 - ele1["floor"]) * 2 + (14 - myfloor) * 2
# # #     print("대기시간:", time)
# # #     print("도착까지의 시간:", (time + (myfloor - 1) * 2))
# # # else:
# # #     time = (ele1["floor"] - myfloor) * 2
# # #     print("대기시간:", time)
# # #     print("도착까지의 시간:", (time + (myfloor - 1) * 2))
#
# # 2. 엘리베이터 위치 상관없음
# if ele1["status"] == "up":
#     if myfloor < ele1['floor']:
#         time = (14 - ele1["floor"]) * 2 + (14 - myfloor) * 2
#         myTime = time + (myfloor - 1) * 2
#     else:
#         time = (myfloor - ele1["floor"]) * 2
#         myTime = time + (myfloor - 1) * 2
# else:
#     if myfloor < ele1['floor'] :
#         time = (ele1["floor"] - myfloor) * 2
#         myTime = time + (myfloor - 1) * 2
#     else:
#         time = (ele1["floor"] - 1) * 2 + (myfloor - 1) * 2
#         myTime = time + (myfloor - 1) * 2
# print("대기시간:", time)
# print("도착까지의 시간:", myTime)
#
# if ele1["status"] == "up" and myfloor < ele1['floor']:
#     time = (14 - ele1["floor"]) * 2 + (14 - myfloor) * 2
#     myTime = time + (myfloor - 1) * 2
# elif ele1["status"] == "up" and myfloor > ele1['floor']:
#     time = (myfloor - ele1["floor"]) * 2
#     myTime = time + (myfloor - 1) * 2
# elif ele1["status"] == "down" and myfloor < ele1['floor']:
#     time = (ele1["floor"] - myfloor) * 2
#     myTime = time + (myfloor - 1) * 2
# else:
#     time = (ele1["floor"] - 1) * 2 + (myfloor - 1) * 2
#     myTime = time + (myfloor - 1) * 2
# print("대기시간:", time)
# print("도착까지의 시간:", myTime)
#
# '''
# <회원가입>
# *아이디:
# *비밀번호(숫자 4자리):
# *나이:
# 주소:
# 연락처:
#
# 단, 비밀번호에 숫자가 아닌 값이 있으면 회원가입x
#     나이가 34세 초과일 시 회원가입 불가
# '''
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

# '''
# 주제를 잡아서 만들기
# 1) 2주차
# 2) 3주차(+반복)
# 3) 4주차(+함수)
# '''
# '''
# 실습
# leftShoulder
# rightShoulder
# RightHip
# LeftHip
# ex) rightShoulder = [0, 0]
# 위 4곳의 x,y 좌표를 받으시오
# leftShoulder-x : 100
# leftShoulder-y : 300
# 단계(보통(80점)(3% 이내), 경고(50점)(5%이내), 위험(10점)(그 외))
# 어깨 좌우축 상태: 보통
# 골반 좌우축 상태: 경고
# 척추 곧음 정도: 경고
# 종합 점수: 60점
# '''
# leftShoulder = [103, 301]
# rightShoulder = [3, 300]
# RightHip = [30, 220]
# LeftHip = [70, 208]
#
# shoulderDegree = (leftShoulder[1] - rightShoulder[1]) / (leftShoulder[0] - rightShoulder[0])
#
# if shoulderDegree > -0.03  and shoulderDegree < 0.03:
#     shoulderResult = "보통"
#     shoulderScore = 80
# elif shoulderDegree > -0.05  and shoulderDegree < 0.05:
#     shoulderResult = "경고"
#     shoulderScore = 50
# else:
#     shoulderResult = "위험"
#     shoulderScore = 10
#
# HipDegree = (LeftHip[1] - RightHip[1]) / (LeftHip[0] - RightHip[0])
#
# if HipDegree > -0.03  and HipDegree < 0.03:
#     hipResult = "보통"
#     hipScore = 80
# elif HipDegree > -0.05  and HipDegree < 0.05:
#     hipResult = "경고"
#     hipScore = 50
# else:
#     hipResult = "위험"
#     hipScore = 10
#
# shoulderCenter = [(leftShoulder[0] + rightShoulder[0]) / 2, (leftShoulder[1] + rightShoulder[1]) / 2]
#
# hipCenter = [(LeftHip[0] + RightHip[0]) / 2, (LeftHip[1] + RightHip[1]) / 2]
#
# spineDegree = (shoulderCenter[0] - hipCenter[0]) / (shoulderCenter[1] - hipCenter[1])
#
# if spineDegree > -0.03  and spineDegree < 0.03:
#     spineResult = "보통"
#     spineScore = 80
# elif spineDegree > -0.05  and spineDegree < 0.05:
#     spineResult = "경고"
#     spineScore = 50
# else:
#     spineResult = "위험"
#     spineScore = 10
#
# print("어깨:", shoulderResult)
# print("골반:", hipResult)
# print("척추:", spineResult)
# print("종합점수:", (shoulderScore + hipScore + spineScore) / 3)
# '''
# 학점 계산기
# 점수: 70(입력)
# 학점: C학점
#
# 89점 초과 A학점
# 79점 초과 B학점
# 69점 초과 C학점
# 59점 초과 D학점
# 나머지는 F학점
# * 점수 0보다 작거나 100보다 "계산불가" 출력
#
# 59 < score < 69
# 59 < score and score < 69
# '''
# # score = int(input("점수: "))
# # if score < 0 or score > 100:
# #     result = "계산 불가"
# # elif score > 89:
# #     result = "A 학점"
# # elif score > 79:
# #     result = "i 학점"
# # elif score > 69:
# #     result = "C 학점"
# # elif score > 59:
# #     result = "D 학점"
# # else:
# #     result = "F 학점"
# # print("학점:", result)
#
# num = 10
# num = num + 1
# print(num)
#
# num += 1
# print(num)
#
# num += 10
# print(num)
#
# print("반복 전")
# human = 0
# while human < 20:
#     human = human + 1
#     print("%d 번째 학생입니다." %human)
# print("반복 후")
#
# '''
# 1월 17일
# 1월 18일
# 1월 19일
# ...
# 1월 31일
# '''

# day = 0 # 초기문
# while day < 15: # 조건식(문) * 반복횟수!!!
#     realDay = day + 17
#     print("1월 %d일" %realDay) # 실행문
#     day += 1 # 후처리문
#
#
# coffee = 500
# milk = 3000
# print("어서오세요 코리아카페입니다.")
# select = input("주문할 음료를 선택해주세요(1.아메리카노, 2.라떼, 3.패션후르츠):")
# num = int(input("주문할 음료의 갯수를 입력하십시오: "))
#
# if select == "1":
#     menu = "아메리카노"
# elif select == "2":
#     menu = "라떼"
# elif select == "3":
#     menu = "패션후르츠"
#
# i = 0
# while i < num:
#     if select == "1":
#         coffee -= 45
#     elif select == "2":
#         coffee -= 45
#         milk -= 400
#     print(menu + " 한잔 나왔습니다.")
#     i += 1
# print("[재고]")
# print("우유:", milk, "ml")
# print("원두:", coffee, "g")
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
# '''
# '''
# print("반복 전")
# i = 0
# num = 100
# while i < num:
#     print(i)
#     i += 1
#     if i == 8:
#         break
#
# print("반복 후")
#
# '''
# 지폐 최소갯수 프로그램
# 금액: 127000 #입력
# 최소 갯수: 7 (출력)
# '''

# money = int(input("금액: "))
# i = 0
# while money >= 50000:
#     money -= 50000
#     i += 1
# while money >= 10000:
#     money -= 10000
#     i += 1
# while money >= 5000:
#     money -= 5000
#     i += 1
# while money >= 1000:
#     money -= 1000
#     i += 1
# print("최소 갯수:", i)

''' 강사님 답변 '''
# money = int(input("금액: "))
# count = 0
# while True:
#     if money >= 50000:
#         money -= 50000
#         count += 1
#     elif money >= 10000:
#         money -= 10000
#         count += 1
#     elif money >= 5000:
#         money -= 5000
#         count += 1
#     elif money >= 1000:
#         money -= 1000
#         count += 1
#     if money < 1000:
#         break
# print("최소 갯수:", count)

# money = int(input("금액: "))
# if money >= 50000:
#     a = money // 50000
#     money -= 50000 * a
# else:
#     a = 0
# if money >= 10000:
#     b = money // 10000
#     money -= 10000 * b
# else:
#     b = 0
# if money >= 5000:
#     c = money // 5000
#     money -= 5000 * c
# else:
#     c = 0
# if money >= 1000:
#     d = money // 1000
#     money -= 1000 * d
# else:
#     d = 0
# x = a + b + c + d
# print("최소 갯수:", x)
#
# a = 0
# while a < 10:
#     a += 1
#     if a % 2 == 0:
#         continue
#     print("a:", a)

# %%

'''
짝수들의 합 구하기
입력: 8 (입력)
짝수들의 합: 20 (출력)
'''

# num = int(input("입력: "))
#
# a = 0
# total = 0
# while a <= num:
#     if a % 2 != 0:
#         continue
#     a += 1
#     total += a
# print("짝수들의 합:", total)

# ''' for 반복문 '''
# print()
# test_list = ["one", "two", "three"]
# for i in test_list:
#     print(i)
#
# print()
# marks = [90, 25, 45, 67, 80, 33]
# number = 0
# for mark in marks:
#     number = number + 1
#     if mark > 60:
#         print("%d번 학생 합격입니다."%number)
#     else:
#         print("%d번 학생 불합격입니다."%number)
# #%%
#
testResult = [
    {"name" : "gildong",
     "phone" : "01012345678",
     "score" : {"math": 100,
                "science": 30,
                "english": 45}},
    {"name": "gilseo",
     "phone": "01011112222",
     "score": {"math": 40,
               "science": 70,
                "english": 92}},
    {"name": "gilnam",
     "phone": "01033334444",
     "score": {"math": 50,
               "science": 80,
               "english": 75}}
]

'''
출력(평균 60점 이상)
01011112222 으로 문자 발송
gilseo님 합격을 진심으로 축하합니다.
'''

for i in testResult:
    sum = i["score"]["math"]+ i["score"]["english"]+ i["score"]["science"]
    average = sum / 3
    if average > 60:
        print(i["phone"], "으로 문자 발송")
        print(i["name"]+ "님 합격을 진심으로 축하합니다.")


print()
for i in range(1, 11):
    print(i)

print()
for i in range(10):
    print(i)

# for i in range(len(testResult)):
#     print(testResult[i]["name"])

# print(type(1))
# num_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
# calStr = input("수식 입력: ")
# sum = 0
# a = 0
# y = 0
# for i in range(len(calStr)):
#     if calStr[i] not in num_list:
#         x = int(calStr[a : i])
#         sum += x
#         a = i + 1
# y = int(calStr[a : ])
# sum1 = sum + y
# print (sum1)
#
# calStr = input("수식 입력: ")
# noSpaceStr = ""
# # 공백 제거
#
# for i in range(len(calStr)):
#     if calStr[i] == " ":
#         continue
#     noSpaceStr += calStr[i]
# print(noSpaceStr)
# numList = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
# flagNum = 0
# int1 = ""
# int2 = ""
# flagSearch = 0
# for i in range(len(noSpaceStr)):
#     if flagSearch == 0 and noSpaceStr[i] in numList:
#         int1 += noSpaceStr[i]
#     elif noSpaceStr[i] == "+":
#         flagSearch = 1
#     elif flagSearch == 1 and noSpaceStr[i] in numList:
#         int2 += noSpaceStr[i]
#
# print(int(int1) + int(int2))

# '''
# 별찍기
#
# 줄 수 입력: 5
#
# *
# **
# ***
# ****
# *****
# '''
#
# a = int(input("줄 수 입력: "))
# for i in range(a):
#     x = "*" * (i + 1)
#     print(x)
#
# starLine = int(input("별 찍기(줄 수): "))
# for i in range(starLine):
#     for j in range(i + 1):
#         print("*", end="")
#     print()

# for i in range(a):

'''
트리만들기: 5
    *
   ***
  *****
 *******
*********
'''

a = int(input("트리만들기: "))
for i in range(a):
    x = i + 1
    for j in range(a - x):
        print(" ", end="")
    for k in range(x * 2 - 1):
        print("*", end="")
    print()
