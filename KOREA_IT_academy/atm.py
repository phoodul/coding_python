bankPW = "1q2w3e4r!"
atmList = [
    {"name" : "서면1", "money": 30000000, "inputList": [], "outputList" : []},
    {"name" : "서면2", "money": 30000000, "inputList": [], "outputList" : []},
    {"name" : "서면3", "money": 30000000, "inputList": [], "outputList" : []},
    {"name" : "서면4", "money": 30000000, "inputList": [], "outputList" : []},
]
'''
어서오세요 코리아 은행입니다.
1. 고객
2. 관리자
q. 종료
입력: 1
print("1. 서면1")
1. 서면1
2. 서면2
3. 서면3
4. 서면4
창구 선택: 3
카테고리(1. 입금, 2.출금): 1
입금자 성명: 홍길동
금액: 1000000
입금이 완료 되었습니다.
출금 동일(*단, atm 금액이 부족할 시 출금 X)



입력: 2
관리자 패스워드: 1234
패스워드가 일치 하지 않습니다. 다시 입력하십시오
관리자 패스워드: 1q2w3e4r!
카테고리(1. 지점금액, 2. 입출금 내역 확인): 1
atm명: 서면1
금액: 30000000
atm명: 서면2
금액: 30000000
...
총 금액: 120000000

'''

while True:
    print("어서오세요 코리아 은행입니다.")
    print("1. 고객")
    print("2. 관리자")
    print("q. 종료")
    select = input("입력: ")
    if select == "1":
        # atm 기기들 출력
        i = 0
        while i < len(atmList):
            i += 1
            print(i, end="")
            print(". ", end="")
            print(atmList[i -1]["name"])

        selectATM = int(input("창구선택: "))
        atmCategory = input("카테고리(1.입금, 2.출금)")
        if atmCategory == "1":
            name = input("입금자 성명: ")
            inputMoney = int(input("금액: "))
            inputDic = {"name" : name, "inputMoney": inputMoney}
            atmList[selectATM - 1]["inputList"].append(inputDic)
            atmList[selectATM - 1]["money"] += inputMoney
            print(atmList[selectATM - 1]["inputList"])
            print(atmList[selectATM - 1]["money"])
        elif atmCategory == "2":
            name = input("출금자 성명: ")
            outputMoney = int(input("금액: "))
            outputDic = {"name": name, "outputMoney": outputMoney}
            if atmList[selectATM - 1]["money"] < outputMoney:
                print("atm 잔고 부족")
                print("출금 실패")
            else:
                atmList[selectATM - 1]["outputList"].append(outputDic)
                atmList[selectATM - 1]["money"] -= outputMoney
                print("출금 성공")
            print(atmList[selectATM - 1]["outputList"])
            print(atmList[selectATM - 1]["money"])
    elif select == "2":
        while True:
            inputPW = input("관리자 패스워드: ")
            if bankPW == inputPW:
                break
            print("비밀번호가 일치하지 않습니다.")
            print("다시 입력하십시오")

        adminInputCategory = input("카테고리(1. 지점금액, 2. 입출금 내역 확인): ")
        if adminInputCategory == "1":
            i = 0
            while i < len(atmList):
                print("atm명:", atmList[i]["name"])
                print("금액:", atmList[i]["money"])
                i += 1
            sum = 0
            k = 0
            while k < len(atmList):
                sum += atmList[k]['money']
                k += 1
            print("총 금액:", sum)

    elif select == "q":
        break









