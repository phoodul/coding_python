class Factory:
    def __init__(self, factoryNumber):
        self.factoryNumber = factoryNumber

    def factoryStart(self):
        print(self.factoryNumber, "공장을 가동합니다.")

    def factoryStop(self):
        print(self.factoryNumber, "공장을 중지합니다.")

class SamsungFactory(Factory):
    def __init__(self, factoryNumber):
        super().__init__(factoryNumber)

    def factoryStart(self):
        print("삼성 ", end="")
        super().factoryStart()

    def factoryStop(self):
        print("삼성 ", end="")
        super().factoryStop()

    def makeSmartPhone(self):
        print("삼성 스마트폰을 제작합니다.")

class LGFactory(Factory):
    def __init__(self, factoryNumber):
        super().__init__(factoryNumber)

    def factoryStart(self):
        print("엘지 ", end="")
        super().factoryStart()

    def factoryStop(self):
        print("엘지 ", end="")
        super().factoryStop()

    def makeSmartTV(self):
        print("엘지 스마트TV를 제작합니다.")


samsungFactory1 = SamsungFactory(1)
samsungFactory1.factoryStart()

'''
삼성 1, 2, 3, 4, 5 공장을 만드시오
모든 공장을 가동하십시오
모든 공장을 중지하십시오
'''
samsungFactoryList = []
for i in range(5):
    samsungFactory = SamsungFactory(i + 1)
    samsungFactoryList.append(samsungFactory)

for i in samsungFactoryList:
    i.factoryStart()



for i in samsungFactoryList:
    i.factoryStop()

print()
factoryList = []
'''
삼성1, 삼성2, 엘지1, 엘지2, 엘지3, 삼성3

6개의 공장을 모두 가동하십시오
1 공장을 가동합니다.
2 공장을 가동합니다.
1 공장을 가동합니다.
'''
samsungFactory11 = SamsungFactory(1)
samsungFactory2 = SamsungFactory(2)
samsungFactory3 = SamsungFactory(3)

LGFactory1 = LGFactory(1)
LGFactory2 = LGFactory(2)
LGFactory3 = LGFactory(3)
factoryList.append(samsungFactory11)
factoryList.append(samsungFactory2)
factoryList.append(LGFactory1)
factoryList.append(LGFactory2)
factoryList.append(LGFactory3)
factoryList.append(samsungFactory3)

for i in factoryList:
    i.factoryStart()

'''
각 공장별 제품을 생산하시오
'''
for i in factoryList:
    if isinstance(i, SamsungFactory):
        i.makeSmartPhone()
    elif isinstance(i, LGFactory):
        i.makeSmartTV()


for i in factoryList:
    i.factoryStop()








