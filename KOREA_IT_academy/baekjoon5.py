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

# S = input()
# alphabet_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
# for i in alphabet_list:
#     if i in S:
#         print(S.index(i), end=' ')
#     else:
#         print(-1, end=' ')

# T = int(input())
# for _ in range(T):
#     A, B = input().split()
#     a = int(A)
#     list_char = []
#     for i in B:
#         list_char.append(i * a)
#     print(''.join(list_char))

# sentence = input()
# count = 0
# if len(sentence) < 3:
#     if all(sentence[i] == ' ' for i in range(len(sentence))):
#         word_count = 0
#     else:
#         word_count = 1
# else:
#     for i in range(len(sentence)-2):
#         if (sentence[i] != ' ') and (sentence[i+1] == ' ') and (sentence[i+2] != ' '):
#             count += 1
#     word_count = count + 1
# print(word_count)

# 정답
sentence = input().strip()
if sentence == "":
    print(0)
else:
    print(len(sentence.split()))
