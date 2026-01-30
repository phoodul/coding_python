# 데이터 교환
x = 10
y = 20

# 교환 전 출력
print("교환 전 : x =", x, "y =", y)

# = 연산자를 활용하여 데이터 교환
(x, y) = (y, x)

# 교환 후 출력
print("교환 후 : x =", x, "y =", y)

# 다양한 자료형을 세트로 변환하기
str = "apple"
list1 = [1, 2, 3]
tuple = (1, 2, 3)

print("<각자의 형태를 가진 자료형들>")
print("str : ", str)
print("list : ", list1)
print("tuple : ", tuple)

# set으로 변환
set_str = set(str)
set_list = set(list1)
set_tuple = set(tuple)
print()
print("set_str : ", set_str)
print("set_list : ", set_list)
print("set_tuple : ", set_tuple)


# 예제 n번째로 작은 알파벳 출력하기

str_random = "apbdhwoernzhd"
str_random = set(str_random)

print(str_random)

# 다시 리스트로 변환
list_str = list(str_random)
print(list_str)

list_str.sort()
print(list_str)

# 특정 순서의 알파벳 출력
print("3번째로 작은 알파벳은", list_str[2], "입니다.")
print(f"7번째로 작은 알파벳은 {list_str[6]} 입니다.")
print(f"5번째로 작은 알파벳은 {list_str[4]} 입니다.")

set_a = {2, 4, 6}
set_b = {3, 6, 9}

union_AandB = set_a.union(set_b)
print(union_AandB)

union_AandB = set_a | set_b
print(union_AandB)

# 함수 선언
def hello():
    print("hello")
    print("제 이름은 김파이입니다.")
print("만나서 반갑습니다.")
print()
hello()

num = 49

if num % 2 == 0:
    print("{0}은 짝수입니다.".format(num))
else:
    print("{0}은 홀수입니다.".format(num))
