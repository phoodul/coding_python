# S= input()
# i = int(input())
# print(S[(i - 1)])

# user_input = input()
# print(len(user_input))

T = int(input())
input_list = [input() for _ in range(T)]
for item in input_list:
    print(item[0] + item[-1])

