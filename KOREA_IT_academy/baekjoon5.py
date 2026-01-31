# S= input()
# i = int(input())
# print(S[(i - 1)])

# user_input = input()
# print(len(user_input))

# T = int(input())
# input_list = [input() for _ in range(T)]
# for item in input_list:
#     print(item[0] + item[-1])

# a = input()
# print(ord(a))

# N = int(input())
# input_num = input()
# list_num = [int(x) for x in input_num]
# sum = 0
# for _ in range(len(list_num)):
#     sum += list_num[_]
# print(sum)

S = input()
alphabet_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
for i in alphabet_list:
    if i in S:
        print(S.index(i), end=' ')
    else:
        print(-1, end=' ')
        