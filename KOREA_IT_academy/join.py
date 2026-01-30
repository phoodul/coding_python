'''
<회원가입>
*아이디
*비밀번호(숫자 4자리)
*나이
주소
연락처

단, 비밀번호에 숫자가 아닌 값이 있으면 회원가입X
    나이가 34세 초과일 시 회원가입 불가
'''


"<Membership Join>"
id = input("아이디: ")
pw = input("비밀번호(숫자네자리): ")
age = input("나이: ")
address = input("주소: ")
phone = input("연락처: ")
num_list = ["0","1","2","3","4","5","6","7","8","9"]
# if id == "":
#     print("아이디가 정상적으로 입력되지 않았습니다.")
# elif pw[0] not in num_list or pw[1] not in num_list or pw[2] not in num_list or pw[3] not in num_list :
#     print("비밀번호가 숫자네자리로 입력되지 않았습니다.")
# elif int(age) not in range(35):
#     print("34세 이하의 청년만 가입 가능합니다.")
# else:
#     print("회원가입이 정상적으로 완료되었습니다.")

# 2번째 방법
list_pw = list(pw)
if id == "":
    print("아이디가 정상적으로 입력되지 않았습니다.")
elif [x for x in list_pw] not in num_list :
    print("비밀번호가 숫자네자리로 입력되지 않았습니다.")
elif int(age) not in range(35):
    print("34세 이하의 청년만 가입 가능합니다.")
else:
    print("회원가입이 정상적으로 완료되었습니다.")

