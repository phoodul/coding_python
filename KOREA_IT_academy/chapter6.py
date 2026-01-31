class Calculator: # class 선언 대문자로 이름 시작 이후 :
    def __init__(self): # 생성자 함수
        self.result = 0 # 변수 초기화

    def add(self, num):
        self.result += num #함수 정의
        return self.result #return 값 반환

cal1 = Calculator()
# 생성인데, cal1은 Calculator로 만든 저장소에 입력된 변수를 가리킨다는 의미다.
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

class MegaCoffee(): # class 선언
    def __init__(self):
        self.name = None
        self.count = 0
        self.totalMoney = 0

    def makeMega(self, name):
        self.name = name

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
#         #megaCoffee는 MegaCoffee로 만들어진 주소에 저장된 변수를 말한다.
#         megaCoffee.makeMega(name)
#         #megaCoffee라는 object에 makeMega로 만든 name 값을 담는다.
#         #이 때, name은 그저 인스턴스에 담긴 하나의 변수일 뿐,
#         # dictionary나 list의 형태로 저장되는 것이 아니다.
#         megaList.append(megaCoffee)
#         # 여기서 인스턴스 자체를 하나의 list로 만든다.
#     elif select == "2":
#         name = input("지점명: ")
#         count = int(input("갯수: "))
#         totalMoney = int(input("금액: "))
#         flag = False
#         for i in megaList: # 이 때의 i는 megaList에 담긴 각각의 인스턴스를 의미한다.
#             if i.name == name:
#                 i.countSale(count, totalMoney)
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
    def __init__(self, name, age, height, weight):
        self.name = name
        self.age = age
        self.height = height
        self.weight = weight

myInfo1 = MyInfo("gildong", 18, 180, 70) # 생성
print(myInfo1.name)
print(myInfo1.weight)







