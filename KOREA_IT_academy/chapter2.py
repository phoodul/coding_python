''' 리스트 '''
a = []
b = [1, 2, 3]
c = ["apple", "banana", "cherry"]
d = [1, "apple", 2, "banana"]
e = [1, 2, ["apple", "banana"]]

print(e)
print(e[0])
subList = e[2]
print(subList)
print(subList[0])
print(e[2][0])
print(e[1:])

# 리스트 연산하기
a = [1, 2, 3]
b = [4, 5, 6]
print (a + b)
# 리스트 반복
print (a * 3)

# 수정과 삭제
a = [1, 2, 3]
print (a)
a[1] = 10

print (a)
del a[1]
print (a)

''' 리스트 관련 함수들 '''
a = [1, 2, 3]
print (a)
a.append(8)
print (a)
a.append([10, 20])
print (a)

# 정렬
a = [1, 4, 2, 7, 6, 5]
print (a)
a.sort()
print (a)
a.reverse()
print (a)

b = ["b", "c", "k", "a", "d"]
b.sort()
print (b)

# 인덱스 반환

a = ['a', 'b', 'c']
print(a.index('a'))
print(a.index('b'))

# 리스트 요소 삽입
a = ['a', 'b', 'c']
a.insert(1, 'k')
print(a)
del a[1]
print(a)
a.insert(1, ['apple', 'banana'])
print(a)
a.insert(1, 'k')
# 요소 삭제
a.remove('k')
print(a)
a = [1, 1, 1, 3, 3, 2, 1, 3]
print(a)
a.remove(1)
print(a)

''' 값을 모두 삭제하려는 방법 '''
# 예시: 리스트에서 20을 모두 제거하고 싶을 때
numbers = [10, 20, 30, 20, 40, 20, 50]

# "x가 20이 아닌 것들만 모아서 리스트를 만들어라"
numbers = [x for x in numbers if x != 20]
''' x가 아닌 다른 문자를 사용해도 됨 '''
print(numbers)  # 출력: [10, 30, 40, 50]

# 요소 확인 후 삭제
a = ["a", "b", "c"]
print(a.pop(1))
print(a)

# 요소 x 의 갯수
a = [1, 2, 3, 4, 1]
print(a.count(1))

a = [1, 2, 3]
b = [4, 5, 6]
a.extend(b)
print(a)
'''
a = [1, 2, 3]
a.append(4, 5, 6)
print(a)
error가 나온다. 이유는 append 뒤에는 하나의 요소만 추가할 수 있기 때문이다. 
'''

''' append는 요소값 추가 vs. extend는 확장 '''



