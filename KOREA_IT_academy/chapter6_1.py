class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, num):
        self.result += num
        return self.result

cal1 = Calculator() # 생성
cal2 = Calculator()
print(cal1.add(10))
print(cal1.add(20))

print(cal1)
print(cal2)
print(cal2.add(30))

'''
메가커피 클래스
클래스명: MegaCoffee
함수:
1. 지점 등록 makeMege("전포점")
2. 판매 갯수, 가격 countSale(2, 5700)
* 판매 갯수, 가격이 계속 더해지면서 일 판매량, 금액 확인할 용도

서면점
전포점
광안리점 메가커피를 만드시오
각각 음료 갯수와 가격을 넣은 후
값을 확인 하시오

'''

class MegaCoffee:
    def __init__(self):
        self.name = None
        self.count = 0
        self.totalMoney = 0

    def makeMega(self, inputName):
        self.name = inputName

    def countSale(self, count, totalMoney):
        self.count += count
        self.totalMoney += totalMoney

mega1 = MegaCoffee()
mega1.makeMega("전포점")
mega1.countSale(2, 10000)
print(mega1.name)
print(mega1.count)

mega2 = MegaCoffee()
mega2.makeMega("서면점")
print(mega2.name)
[mega1, mega2]
'''
메가 본사 프로그램
1. 점포 등록
2. 점포 판매 등록
3. 점포 매출 현황
입력: 1
점포명을 입력하십시오: 동래점
입력: 1
점포명을 입력하십시오: 수안점

입력: 2
지점: 동래점
갯수: 2
금액: 20000

입력: 3
지점: 동래점
매출: 100000(출력)
'''

# megaList = []
# while True:
#     for i in range(len(megaList)):
#         print(megaList[i].name)
#     print("메가 본사 프로그램")
#     print("1. 점포 등록")
#     print("2. 점포 판매 등록")
#     print("3. 점포 매출 현황")
#     select = input("입력: ")
#
#     if select == "1":
#         name = input("지점명: ")
#         megaCoffee = MegaCoffee()
#         megaCoffee.makeMega(name)
#         megaList.append(megaCoffee)
#     elif select == "2":
#         name = input("지점명: ")
#         count = int(input("갯수: "))
#         money = int(input("금액: "))
#         flag = False
#         for i in megaList:
#             if i.name == name:
#                 i.countSale(count, money)
#                 print("저장 완료")
#                 flag = True
#         if not flag:
#             print("지점이 존재하지 않습니다.")
#     elif select == "3":
#         name = input("지점명: ")
#         flag = False
#         for i in megaList:
#             if i.name == name:
#                 print("매출:", i.totalMoney)
#                 flag = True
#         if not flag:
#             print("지점이 존재하지 않습니다.")

class MyInfo:
    def __init__(self, name, age, hegiht, weight):
        self.name = name
        self.age = age
        self.height = hegiht
        self.weight = weight

myInfo1 = MyInfo("gildong", 18, 180, 70) # 생성
print(myInfo1.name)
print(myInfo1.weight)


class Animal:
    def __init__(self):
        print("Animal 생성")
    def walk(self):
        print("동물이 걷습니다.")

# class Tiger:
#     def __init__(self):
#         pass
#     def walk(self):
#         print("동물이 걷습니다.")
#
# class Dog:
#     def __init__(self):
#         pass
#     def walk(self):
#         print("동물이 걷습니다.")
class Tiger(Animal):
    pass
class Dog(Animal):
    def __init__(self):
        super().__init__()
        print("Dog 생성")

    def walk(self): # Overriding -> 재정의
        print("hi")

    def smile(self):
        print("강아지가 웃습니다.")
# animal = Animal()
# tiger = Tiger()
dog = Dog()
# animal.walk()
# tiger.walk()
dog.walk()
dog.smile()
print(isinstance(dog, Dog))
print(isinstance(dog, Tiger))

class SignUP:
    def __init__(self, id, pw, email):
        self.id = id
        self.pw = pw
        self.email = email

    def showInfo(self):
        print("id:", self.id)
        print("pw:", self.pw)
        print("email:", self.email)
# 화면에서 전달된 정보
signUpInfo = {
    "id" : "gildong",
    "pw" : "1q2w3e4r!!",
    "email" : "gildong@gmail.com"
}

newInfo1 = SignUP(signUpInfo["id"], signUpInfo["pw"], signUpInfo["email"])

newInfo1.showInfo()






