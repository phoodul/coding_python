# def add(a, b):
#     c = a + b
#     return a + b
#
# print(add(10, 20)) # 함수 호출
#
# '''
# 파이썬 함수
# def 함수명(매개변수 or 파라미터):
#     실행문
#     실행문2
#     return 리턴값
# '''
#
# inputOrderMenu = [
#     {"name": "아메리카노",
#      "num": 10,
#      "price": 2000},
#     {"name": "라떼",
#      "num": 5,
#      "price": 3400},
#     {"name": "아이스티",
#      "num": 1,
#      "price": 3000}
# ]
#
# # 아메리카노 2000원, 라떼 3400원
# def calMenu(inputOrderMenu):
#     sumPrice = 0
#     for i in range(len(inputOrderMenu)):
#         if inputOrderMenu[i]["name"] == "아메리카노":
#             sumPrice += inputOrderMenu[i]["num"] * 2000
#         elif inputOrderMenu[i]["name"] == "라떼":
#             sumPrice += inputOrderMenu[i]["num"] * 3400
#         elif inputOrderMenu[i]["name"] == "아이스티":
#             sumPrice += inputOrderMenu[i]["num"] * 3000
#         elif inputOrderMenu[i]["name"] == "카페모카":
#             sumPrice += inputOrderMenu[i]["num"] * 4000
#     return sumPrice
#
# print(calMenu(inputOrderMenu))

# def calMenu(orderMenu):
#     total = 0
#     for i in orderMenu:
#         sum = i["num"] * i["price"]
#         total += sum
#     return total
# print(calMenu(orderMenu), "원")

print()
def say():
    print("안녕")
    return "hi"

print(say())

def bankUpdate():
    print("확인용 출력")
    print("금일 은행 거래 내역 디비에서 업데이트 하는 함수 호출")
    return True

def plusPrint(a, b):
    print("입력1:", a)
    print("입력2:", b)
    print("합:", (a + b))

print(plusPrint(10, 20))

# 입력값이 몇개가 될지 모르는 경우

def add_many(*args): #arguments 파라미터들
    print(args)
    result = 0
    for i in args:
        result += i
    return result

print(add_many(1, 2, 3))
print(add_many(10, 20, 3, 4))

def printHobby(name, *hobbys):
    print(name)
    for i in hobbys:
        print(i, end=" ")
    print()
printHobby("gildong", "soccer", "baseball", "swimming")

a = 1
def varTest(k):
    global a
    a = k + 1

print(varTest(a))
print(a)




