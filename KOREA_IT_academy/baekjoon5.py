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

# # 정답
# sentence = input().strip()
# if sentence == "":
#     print(0)
# else:
#     print(len(sentence.split()))

# A, B = input().split()
# list_A = [x for x in A]
# list_B = [x for x in B]
# list_a = [list_A[2], list_A[1], list_A[0]]
# list_b = [list_B[2], list_B[1], list_B[0]]
# num_A = ''.join(list_a)
# num_B = ''.join(list_b)
# if num_A > num_B:
#     print(num_A)
# else:
#     print(num_B)

# # 정답
# a, b = input().split()
# # 문자열 슬라이싱으로 뒤집기: '734' -> '437'
# a = int(a[::-1])
# b = int(b[::-1])

# # 더 큰 수 출력
# print(max(a, b))

word = input()
num_dict = {
    ('A', 'B', 'C') : 3,
    ('D', 'E', 'F') : 4,
    ('G', 'H', 'I') : 5,
    ('J', 'K', 'L') : 6,
    ('M', 'N', 'O') : 7,
    ('P', 'Q', 'R', 'S') : 8,
    ('T', 'U', 'V') : 9,
    ('W', 'X', 'Y', 'Z') : 10
}
num = 0
for char in word:
    for key in num_dict.keys():
        if char in key:
            num += num_dict[key]
print(num)