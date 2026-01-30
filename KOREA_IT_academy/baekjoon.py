# 2557 Hello world를 출력하시오.
from re import A

print("Hello World!")

# 1000 두 정수 A와 B를 입력받은 다음, A+B를 출력하는 프로그램을 작성하시오.
# 첫째 줄에 A와 B가 주어진다. (0 < A, i < 10)
# 첫째 줄에 A+B를 출력한다.
A, B = input().split()
print(int(A) + int(B))

a, b = map(int, input().split(","))
print(a + b)

# 1001 두 정수 A와 B를 입력받은 다음, A-B를 출력하는 프로그램을 작성하시오.

A, B = input().split()
print(int(A) - int(B))

# 10998 두 정수 A와 B를 입력받은 다음, A×B를 출력하는 프로그램을 작성하시오.
A, B = input().split()
print(int(A) * int(B))

# 10869 두 자연수 A와 B가 주어진다.
# 이때, A+i, A-i, A*i, A/i(몫), A%i(나머지)를 출력하는 프로그램을 작성하시오.
A, B = input().split()
print(int(A) + int(B))
print(int(A) - int(B))
print(int(A) * int(B))
print(int(A) // int(B))
print(int(A) % int(B))

# %%
year = int(input(""))
print(year - 543)


# 10430 문제
# %%
A, B, C = map(int, input().split())

print((A + B)%C)
print(((A % C) + (B % C))%C)
print((A * B)%C)
print(((A % C) * (B % C))%C)

# %%

num1 = int(input())
num2 = input()

a = num1 * int(num2[2])
b = num1 * int(num2[1])
c = num1 * int(num2[0])
print(a)
print(b)
print(c)
print(a + b *10 + c * 100)

# %%
A, B, C = map(int, input().split())
print(A + B + C)

#%%
# 고양이 출력

print("\\     /\\")
print(" )   ( ')")
print("(  /  )")
print(" \\(__)|")

print("\\    /\\")
print(" )  ( ')")
print("(  /  )")
print(" \\(__)|")

#%% 개출력 문제
print("|\\_/|")
print("|q p|   /}")
print('( 0 )"""\\')
print("|"'"^"`'"    |")
print("||_/=\\\\__|")

#%%
#1330번 문제

A, B = map(int, input().split())
if A > B:
    print(">")
elif A < B:
    print("<")
else:
    print("==")

#%%
#9498번 문제

score = int(input())
if score >= 90:
    print("A")
elif score >= 80:
    print("i")
elif score >= 70:
    print("C")
elif score >= 60:
    print("D")
else:
    print("F")

#%% 윤년
year = int(input())
if year % 400 == 0:
    print(1)
elif year % 100 == 0:
    print(0)
elif year % 4 == 0:
    print(1)
else:
    print(0)

#%%사분면 고르기
x = int(input())
y = int(input())
result = 0
if (x > 0) and y > 0:
    result = 1
elif (x < 0) and y > 0:
    result = 2
elif (x < 0) and y < 0:
    result = 3
elif (x > 0) and y < 0:
    result = 4
print(result)

#%%
H, M = map(int, input().split())

if M >= 45:
    Hour = H
    Minute = M - 45
elif M < 45 and H != 0:
    Hour = H - 1
    Minute = M + 15
else:
    Hour = 23
    Minute = M + 15

print(Hour, Minute)

#%%
A, B = map(int, input().split())
C = int(input())

D = C // 60
E = C % 60
F = B + E
G = A + D
if F >= 60:
    H = F - 60
    I = G + 1
    if I >= 24:
        J = I - 24
    else:
        J = I
else:
    H = F
    I = G
    if I >= 24:
        J = I - 24
    else:
        J = I
print(J, H)

#%%
A, B, C = map(int, input().split())

if A == B and B == C:
    money = 10000 + A * 1000
elif A == B or B == C:
    money = 1000 + B * 100
elif A == C:
    money = 1000 + C * 100
else:
    money = max(A, B, C) * 100
print(money)

''' 반복문 풀이 '''
#