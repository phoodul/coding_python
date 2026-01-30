# '''구구단'''
# n = int(input())
# for i in range(1, 10):
#     print(f"{n} * {i} = {n*i}")

# '''A + i '''
# T = int(input())
# for i in range(T):
#     A, i = map(int, input().split())
#     print(A + i)

# ''' 합 '''
# n = int(input())
# sum = 0
# for i in range(1, n+1):
#     sum += i
# print(sum)

# ''' 영수증 '''
# X = int(input())
# N = int(input())
# sum = 0
# for i in range(N):
#     a, b = map(int, input().split())
#     sum += a * b
# if sum == X:
#     print("Yes")
# else:
#     print("No")

# 
# # 15552 '''빠른 A + i'''
# T = int(input())
# for i in range(T):
#     A, i = map(int, input().split())
#     print(A + i)

# # ''' A + i - 7'''
# T = int(input())
# for i in range(T):
#     A, i = map(int, input().split())
#     print(f"Case #{i+1}: {A + i}")

# ''' A + i - 8'''
# T = int(input())
# for i in range(T):
#     A, i = map(int, input().split())
#     print(f"Case #{i + 1}: {A} + {i} = {A + i}")

# 별 찍기 -1
# N = int(input())
# for i in range(N):
#     for j in range(i+1):
#         print("*", end="")
#     print()

# # 별 찍기 -2
# N = int(input())
# for i in range(1, N+1):
#     for j in range(N-i):
#         print(" ", end="")
#     for j in range(i):
#         print("*", end="")
#     print()

#10952 A + i - 5
# while True:
#     A, i = map(int, input().split())
#     if A ==0 and i ==0:
#         break
#     else:
#         print(A + i)

# while True:
#     A, i = map(int, input().split())
#     if (A > 0 and A < 10) and (i > 0 and i < 10):
#         print(A + i)
#     else:
#         break

# import sys
# T = int(sys.stdin.readline())
# for i in range(T):
#     A, i = map(int, sys.stdin.readline().split())
#     print(A + i)

# N = int(input()) 
# list_num = list (map(int, input().split()))
# V = int(input())
# count = 0
# for i in list_num:
#     if i == V:
#         count += 1
# print(count)

# 10871 ''' X보다 작은 수'''
# N, X = map(int, input().split())
# list_num = list(map(int, input().split()))
# newListNum = []
# for i in list_num:
#     if X > i:
#         newListNum.append(i)
# print(" ".join(map(str, newListNum)))

# 10818 ''' 최소, 최대'''
# N = int(input())
# list_num = list(map(int, input().split()))
# max_num = max(list_num)
# min_num = min(list_num)
# print(f"{min_num} {max_num}")


# a = int(input())
# b = int(input())
# c = int(input())
# d = int(input())
# e = int(input())
# f = int(input())
# g = int(input())
# h = int(input())
# i = int(input())
# list_num = [a, b, c, d, e, f, g, h, i]
# max_num = max(list_num)
# x = list_num.index(max_num) + 1
# print(max_num)
# print(x)

# N , M = map(int, input().split())
# list = []
# for x in range(N):
#     list.append(0)
# for a in range(M):
#     i, j, k = map(int, input().split())
#     for x in range(i-1, j):
#         list[x] = k
    
# print(" ".join(map(str, list)))

# N, M = map(int, input().split())
# list_num = [i + 1 for i in range(N)]
# for a in range(M):
#     i, j = map(int, input().split())
#     list_num[i - 1], list_num[j - 1] = list_num[j - 1], list_num[i - 1]
# print(" ".join(map(str, list_num)))


# N, M = map(int, input().split())
# bucket_list = [i + 1 for i in range(N)]
# for k in range(M):
#     i, j = map(int, input().split())
#     bucket_list[i - 1 : j] = reversed(bucket_list[i - 1 : j])
# print(" ".join(map(str, bucket_list)))

N = int(input())
score = list(map(int, input().split()))
max_score = max(score)
new_score = []
for i in score:
    new_score.append(i / max_score * 100)
average = sum(new_score) / N
print(average)