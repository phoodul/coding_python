''' 문자열 관련 함수들 '''
# 문자 갯수 세기(count)
a = "hobby"
print(len(a))
print(a.count("b"))
#shift + F10 -> 실행 단축키
# ctrl + shift + F10 -> 해당 프로젝트 실행 단축키

#  위치 알려주기(find)
a = "gildong is good"
print(a.find("g"))
print(a[1:].find("g"))

# %%위치 알려주기2(index)
a = "gildong is good"
print(a.ndex("d"))

# 문자열 삽입(join)
a = ",".join("abcd")
print(a)
a = "-"
b = "abcd"
c = a.join(b)
print(c)

# 소문자 -> 대문자(upper)
a = "hellow"
print(a.upper())

# 여권 예시
print(1 == 1)
name = "gildong"
print(name == name.upper())
name2 = "GILDONG"
print(name2 == name2.upper())

# 대문자 -> 소문자(lower)
name2 = "GILDONG"
print(name2.lower())

name = "sungsoo"
newName = name[0].upper() + name[1:]
print(newName)

'''
'''