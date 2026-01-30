fruitDic = {
    "id" : "gildong",
    "pw" : "1234",
    "fruitList": [
        {"name": "apple",
         "price": 3000,
         "count": 200},
        {"name": "banana",
         "price": 5000,
         "count": 100},
        {"name": "tomato",
         "price": 500,
         "count": 100},
        {"name": "tangerine",
         "price": 10000,
         "count": 50},
        {"name": "gam",
         "price": 10000,
         "count": 0}
    ]
}


'''
1. 금일 과일 가격 리스트 조회
2. 과일 재고 조회
3. 과일 구매
4. 과일 추가
입력: 
'''


fruit_all_list = fruitDic["fruitList"]
print(fruit_all_list)


# 문제 1을 풀기 위한 함수 정의
# def fruitPriceList():
#     fruitList = []
#     for i in fruit_all_list:
#         dicNamePrice = {}
#         dicNamePrice["name"] = i["name"]
#         dicNamePrice["price"] = i["price"]
#         fruitList.append(dicNamePrice)
#     return fruitList
#
# print(fruitPriceList())
# def fruitPriceListService():
#     return fruitPriceList()
#
# print(fruitPriceListService())
#
# def fruitPriceCountList():
#     fruitPriceCountList = []
#     for fruit in fruitDic["fruitList"]:
#         dicNamePrice = {}
#         dicNamePrice["name"] = fruit["name"]
#         dicNamePrice["price"] = fruit["price"]
#         dicNamePrice["count"] = fruit["count"]
#         fruitPriceCountList.append(dicNamePrice)
#     return fruitPriceCountList
#
# 2번 문제를 풀기 위한 함수
def fruit_count_service():
    fruit_count_list = []
    for m in fruit_all_list:
        if m["count"] == 0:
            m["count"] = "재고 없음"
        fruit_count_list.append(m)
    return fruit_count_list

# 3번 문제를 풀기 위한 함수
def fruit_buy_service():
    dic_fruit_count = {}
    for x in fruit_all_list:
        dic_fruit_count[x["name"]] = x["count"]
    return dic_fruit_count

# # 3번 문제를 풀기 위한 함수
# def fruit_name_list():
#     fruit_name_list = []
#     for i in fruit_all_list:
#         fruit_name_list.append(i["name"])
#     return fruit_name_list

print("1. 금일 과일 가격 리스트 조회")
'''
이름: apple 가격: 3000
이름: banana 가격: 2000
'''

print("2. 과일 재고 조회")
'''
이름: apple 가격: 3000 재고: 100
이름: banana 가격: 2000 재고: 200
이름: gam 가격: 10000 재고: 재고 없음
'''
print("3. 과일 구매")
print("4. 과일 추가")
select = input("입력: ")
if select == "1":
    for i in fruit_all_list:
        print(f"이름: {i['name']}, 가격: {i['price']}")

elif select == "2":
    a = fruit_count_service()
    for i in a:
        print(f"이름: {i['name']}, 가격: {i['price']}, 재고: {i['count']}")
##
elif select == "3":
    d = fruit_buy_service()
    while True:
        buy_fruit = input("과일명: ")
        if buy_fruit not in d.keys():
            print("목록에 없는 과일입니다. 다시 입력해주십시오.")
            continue
        while True:
            buy_count = int(input("갯수: "))
            if buy_count > d[buy_fruit]:
                print(f"{buy_fruit}의 재고가 부족합니다.")
                continue
            else: 
                print(f"{buy_fruit}의 구매가 완료되었습니다.")
                d[buy_fruit] -= buy_count
                break
        break

'''질문: 반복문을 두 번을 돌릴 때 break를 두번 사용할 수 없는가? 
   가령 위에서 과일명이 목록에 없다면 과일명만 다시 입력 받게 하고 
   갯수가 재고보다 많다면 갯수만 다시 입력 받게 하려면 어떻게 해야 하나요?
   현재는 과일명이 목록에 없으면 과일명과 갯수 모두 다시 입력 받게 됩니다. '''





