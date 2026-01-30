''' Section03 응용문제 '''
# 문제 1
num1 = 100
num2 = 4

print(num1 / num2)
print(num1 // num2)
print(num1 % num2)
print(num1 ** num2)

# 문제 2
str1 = "abc"
str2 = "ab"

print(str1 == str2)
str2 += "c"

print(str1 == str2)

#문제 3
x = 10
x *= 7
print(x)

#문제 4
officeNum = 1255
last_num = officeNum % 10
if last_num >= 5:
    print("근무시간은 오전입니다.")
else:
    print("근무시간은 오후입니다.")

#문제 5
korean_score = 85
english_score = 83
math_score = 81
mean_score = (korean_score + english_score + math_score) / 3
if mean_score >= 80:
    result = "합격"
else:
    result = "불합격"
d = mean_score
s = result
announcement = "평균은 %d점이고, 결과는 %s입니다."
print(announcement % (d, s))

''' section 5 응용문제 '''
# 3.

count =5

while count < 10:
    print(count)
    count += 1
#5 정수를 입력받아서 그 횟수만큼 'Hello'를 출력하는 프로그램을 구현하기.

num = int(input('정수를 입력하세요>>> '))
if num >= 0:
    initial = 1
    while initial <= num:
        print(initial, "번째 Hello")
        initial += 1
else:
    print("잘못된 입력입니다.")

#6번
(""" 커피 1잔을 300원에 판매하는 커피자판기가 있습니다.
 이 커피자판기에 돈을 넣으면 자판기에서 뽑을 수 있는 커피가
 몇 잔이며 잔돈은 얼마인지를 함께 출력하는 프로그램을 구현하세요.
 HINT: 잔돈이 300원 이상이면 계속 실행할 수 있도록 반복문을 구성합니다.""")

mon = int(input("자판기에 얼마를 넣을까요?>>> "))
glass = 1
while mon >= 300:
    mon = mon - 300
    print("커피", glass,"잔, 잔돈", mon,"원")
    glass += 1

#문제 7
eva = int(input("이번 영화의 평점을 입력하세요>>> "))
if eva not in range (1, 6):
    print("평점을 1~5점 사이만 입력할 수 있습니다.")
while eva in range(1,6):
    print("\u2605", end="")
    eva -= 1
