print("hellow world")

#주석입니다.
'''
주석: 코드 실행결과에 아무런 영향을 주지 않는 부분

-> 단문 주석: #
-> 장문 주석: ''' '''
-> 주석 단축키: ctrl + /
'''
''' 숫자형 자료형 '''
a=10
b=20

print(a + b)
c = a + b
print(c)

print(b - a)
print(a - b)
print(a * b)
a = 2
b = 3
print(a ** b)
#  ** -> 제곱

a = 100
b = 5
print(a / b)
a = 10
b = 3
print(a // b)
# // -> 몫
print(a % b)
# %  -> 나머지

''' 문자열 자료형 '''
'''
문자열: 문자, 단어 등으로 구성된 문자들의 집합
문자열을 만드는 방법
- ""
- ''
- """"""
- ''''''
'''
name = "gildong"
print(name)

name2 = "gilseo"
#  자동완성 단축키: ctrl + space
print(name2)

print(name + name2)
# stringNum = "100"
# intNum = 200
# print(stringNum + intNum)

''' 질문: 동시에 드래그 해서 주석을 표시하는 방법? 
    답: 드래그 후  ctrl + / 단축키를 사용하면 됨 '''

print('gildong says "hellow"')
print('gildong says "hellow"')
gildongStr = 'gildong says "hellow"'
print(gildongStr)

strEX = """gildong
kakao
naver
daum"""
print(strEX)

strEx = "hellow \npython"
print(strEx)
''' \n escape 문자, 더 많은 escpape 문자를 사용하기 위해서는 구글에서 검색 '''
gildong = 'gildong\'s apple'
print(gildong)

Newton = 'Newton\'s gravity \tis great finding '
print(Newton)

print()
''' 문자열 인덱싱과 슬라이싱 '''
a = "Life is too short, You need Python"

#  인덱스는 0부터 시작
print(a[0])
print(a[1])
print(a[-1])

#  실습 short 를 인덱싱하여 출력하시오
''' 인덱싱은 a[] '''

print(a[12:17])
print(a[12] + a[13] + a[14] + a[15] + a[16])

print(a)
print(a[12 :])
print(a[: 17])
print(a[:])

print(a.find("i"))
print(a.rfind("i"))

url = "https://news.naver.com/section/102"

'''
category 변수에 section 을 대입하시오
cateroryNum 변수에 102를 대입하시오
아래와 같이 출력하시오

카테고리: section
카테고리번호: 102

'''

print(url.rfind("s"))
print(url.rfind("n"))
print(url.rfind("/"))
print(url.find("2"))

category = print(url[23:30])
categoryNum = print(url[31:])

print("카테고리: "+url[23:30])
print("카테고리번호: "+url[31:])

print("카테고리: ", url[23:30])
print("카테고리 번호: ", url[31:])
''' 문자열과 슬라이싱한 것을 섞어서 표시할 때 문자열에만 ""를 사용하고 
    이후에는 인덱싱한 것을 그대로 표현하라
    콤마를 찍어서 표현하거나 +를 사용해서 표현할 수 있다'''

url = "https://news.naver.com/section/102"

# 1. 가장 마지막 '/'의 인덱스 찾기
last_index = url.rfind('/')

# 2. 처음부터 last_index 직전까지의 범위에서 다시 뒤에서부터 찾기
# rfind(찾을문자, 시작인덱스, 끝인덱스)
second_last_index = url.rfind('/', 0, last_index)

print(second_last_index)

searchNum = url.rfind("/")
categoryNum = url[searchNum +1 :]
url2 = url[: searchNum]
searchNum2 = url2.rfind("/")
category = url2[searchNum2 + 1 :]

print("카테고리:", category)
print("카테고리 번호:", categoryNum)

nameList = '[홍길동, 홍길서, 홍길남, 무하마드 알리, 강군]'
'''
학생부의 제일 뒤 학생이 반장
제일 뒤의 앞이 부반장
아래와 같이 출력하시오
반장: 강군
부반장: 무하마드 알리
'''

SearchNum = nameList.rfind(",")
President = nameList[SearchNum+2: -1]
nameList2 = nameList[:SearchNum]
SearchNum2 = nameList2.rfind(",")
VicePresident = nameList2[SearchNum2+2 :]
print("반장:",President)
print("부반장:",VicePresident)

''' ml kit : 구글에 사전에 저장된 이용가능한 자료들 '''

''' 포맷팅 '''
# 문자열 포매팅: 문자열 안에 어떤 값을 삽입하는 방법
# 숫자 대입
a = "I eat %d apples" %3
print(a)

# 문자 대입
b = "I eat %s apples" %"five"
print(b)

name = "홍길동"
strEx = "%s님 합격을 진심으로 축하드립니다."%name
print(strEx)

# 2개 이상의 값 넣기
number = 10
day = "three"
d = "I ate %d apples. so I was sick for %s days" %(number, day)
print(d)

# format 함수를 사용한 포맷팅
a = "I eat {0} apples".format(3)
print(a)
b = "I eat {0} apples".format("five")
print(b)


number = 10
day = "three"
d = "I ate {0} apples. so I was sick for {1} days".format(number, day)
print(d)

'''
홍길동님 진료 완료되었습니다.
금일(2026-01-10) 진료 항목은 기관지염입니다. 
진료비는 7,600원 입니다.

'''
name = "홍길동"
date = "2026-01-10"
diag = "기관지염"
price = 7600

dstr = """
{0}님 진료 완료되었습니다. 
금일("{1}") 진료 항목은 {2}입니다.
진료비는 {3}원 입니다."""
str = dstr.format(name, date, diag, price)
print(str)


#%%
import random
a = random.random()
print(a)

#%%
options = ['사과', '포도', '딸기']

while True:
    choice = input(f"좋아하는 과일을 고르세요 ({', '.join(options)}): ")
    if choice in options:
        break
    print(f"❌ 목록에 없는 과일입니다. {options} 중에서 골라주세요.")

print(f"선택하신 과일: {choice}")



