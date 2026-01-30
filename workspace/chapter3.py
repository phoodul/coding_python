
'''
튜플: 리스트와 비슷한 집합
-리스트는 요소값의 변화가 가능하고 튜플은 요소값의 변화가 불가능하다.
'''

t1 = (1, 2, 3)
print(t1)
''' 튜플은 소괄호 생략 가능 '''
t2 = 1, 2, 3
print(t2)

# 아래는 요소가 아니다
t3 = 1
print(t3)
# 요소값이 하나일 때 표기법
t4 = (1, )
print(t4)

# 인덱싱과 슬라이싱은 가능
print(t2[2])


''' 딕셔너리
    {key : value} '''

a = {1 : "a"}
print(a)

b = {1 : "a", 2 : "b"}
print(b)
# 키의 중복을 허용하지 않는다.
c = {1 : "a", 2 : "b", 1 : "c"}
print(c)

# 밸류의 중복 가능
d = {1: 'a', 2: 'b', 3: 'b'}
print(d)

# 쌍 추가
d[4] = "hi"
print(d)

# 키값을 통해 값 찾기
''' list나 tuple에서는 slicing으로 값을 찾는데, 
    dictionary에서는 key로 value 값을 찾는다.'''
info = {"name" : "gildong", "age" : 18, "hobby" : ["soccer", "golf"]}
print(info["name"])

# 키 값은 변하지 않는 (immutable)한 값을 써야함
# list는 변하는(mutable) 값이다.
#info2 = {["soccer", "golf"]: "hobby"}
#print(info2)
# 아래처럼 튜플 immutable한 값이어서 가능하다.
info2 = {("soccer", "golf"): "hobby"}
print(info2)

''' 불(Boolean) 자료형 '''
a = True
print(a)
print(type(a))

print(4 < 10)
info = {"name" : "gildong", "age" : 18, "hobby" : ["soccer", "golf"]}
print("soccer" in info["hobby"])
