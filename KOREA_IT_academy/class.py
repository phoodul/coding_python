# class Monster:
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age
#     def say(self):
#         print(f"나는 {self.name} {self.age}살임")

# shark = Monster("상어", 7)
# wolf = Monster("늑대", 3)

# shark.say()
# wolf.say()


# class Animal:
#     def cry(self, sound):
#         print("저의 울음소리는", sound, "입니다.")

# cat = Animal()
# cat.cry("야옹")

# dog = Animal()
# dog.cry("멍멍")

# class Person:
#     def introduce(self, name):
#         print(f"안녕하세요. 저는 {name}입니다.")
#         self.name = name
# minsu = Person()
# minsu.introduce("민수")

# print(minsu.name)

# class Person:
#     def __init__(self, name):
#         self.name = name

#     def introduce(self):
#         print(f"안녕하세요. 저는 {self.name}입니다.")

# minsu = Person("민수")
# minsu.introduce()

# younghee = Person("영희")
# younghee.introduce()

# soohyun = Person("수현")
# soohyun.introduce()

# class Cup: 
#     def __init__(self, color, brand):
#         self.color = color
#         self.brand = brand
    
# #객체 생성 및 속성 출력
# starCafeCup = Cup('green', 'Starbucks')


# class Student:
#     def __init__(self, name, ban, subject):
#         self.name = name
#         self.ban = ban
#         self.subject = subject

#     def introduce(self):
#         print(f"안녕하세요. 제 이름은 {self.name} 입니다.")
#         print(f"저는 {self.ban}반 입니다.")
#         print(f"1교시 수업은 {self.subject} 입니다.")
#         print()

#     def talk_about_subject(self):
#         print(f"저는 {self.ban}반 {self.name}입니다.")

#         if (self.subject == "Art"):
#             print(f"1교시 수업은 그대로 {self.subject}입니다.")
#             print()
#         else:
#             print(f"1교시 수업은 변경되어 {self.subject}입니다.")
#             print()

# kelly = Student("Kelly", 1, "Art")
# jason = Student("Jason", 2, "Art")
# tom = Student("Tom", 1, "Art")

# #자기 소개와 1교시 과목 안내
# kelly.introduce()
# jason.introduce()
# tom.introduce()

# #kelly, jason 객체의 1교시 과목 변경
# kelly.subject = "Korean"
# jason.subject = "Korean"

# kelly.talk_about_subject()
# jason.talk_about_subject()
# tom.talk_about_subject()

# class Student:
#     subject = "Art"
#     def __init__(self, name, ban):
#         self.name = name
#         self.ban = ban


#     def introduce(self):
#         print(f"안녕하세요. 제 이름은 {self.name} 입니다.")
#         print(f"저는 {self.ban}반 입니다.")
#         print(f"1교시 수업은 {self.subject} 입니다.")
#         print()

#     def talk_about_subject(self):
#         print(f"저는 {self.ban}반 {self.name}입니다.")

#         if (self.subject == "Art"):
#             print(f"1교시 수업은 그대로 {self.subject}입니다.")
#             print()
#         else:
#             print(f"1교시 수업은 변경되어 {self.subject}입니다.")
#             print()
# Student.subject = "Math"

# kelly = Student("Kelly", 1)
# jason = Student("Jason", 2)
# tom = Student("Tom", 1)

# #자기 소개와 1교시 과목 안내
# kelly.introduce()
# jason.introduce()
# tom.introduce()

# kelly.talk_about_subject()
# jason.talk_about_subject()
# tom.talk_about_subject()

# class Parent:

#     def hello(self): 
#         print("안녕하세요")

# class Child(Parent):

#     def bye(self):
#         print("안녕히 가세요")

# class GrandChild:
#     pass

# parent = Parent()
# child = Child()
# grandchild = GrandChild()

# print(parent)
# print(child)
# print(grandchild)

# class Person: 

#     def introduce(self, name):
#         self.name = name
#         print(f"안녕하세요. 저는 {self.name}입니다.")

# minsu = Person()
# minsu.introduce("민수")
# print(minsu.name)

# class Book: 

#     def set_info(self, title, author):
#         self.title = title
#         self.author = author
#         print(f"책 제목: {self.title}")
#         print(f"책 저자: {self.author}")

# book1 = Book()
# book2 = Book()

# book1.set_info('어린왕자', '생텍쥐페리')
# book2.set_info('꽃을 보듯 너를 본다', '나태주')

# from collections import namedtuple
# from collections import defaultdict
# Grade = namedtuple('Grade', ('score', 'weight'))
# class Subject:
#     def __init__(self):
#         self._grade = []

#     def report_grade(self, score, weight):
#             self._grade.append(Grade(score, weight))

#     def average_grade(self):
#         total, total_weight = 0, 0
#         for grade in self._grade:
#             total += grade.score * grade.weight
#             total_weight += grade.weight
#         return total / total_weight
    
# class Student:
#     def __init__(self):
#         self._subjects = defaultdict(Subject)
#     def get_subject(self, name):
#         return self._subjects[name]
    
#     def average_grade(self):
#         total, count = 0, 0
#         for subject in self._subjects.values():
#             total += subject.average_grade()
#             count += 1
#         return total / count
    
# class GradeBook:
#     def __init__(self):
#         self._students = defaultdict(Student)
#     def get_student(self, name):
#         return self._students[name]
    
import json

# 1. 기능을 제공할 믹스인 클래스 정의
class JsonMixin:
    def to_json(self):
        # 객체의 어트리뷰트(__dict__)를 JSON 문자열로 변환
        return json.dumps(self.__dict__)

# 2. 일반 클래스에 믹스인을 조립
class Student(JsonMixin):  # 믹스인을 상속받음
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

class Point(JsonMixin):    # 전혀 다른 클래스에도 조립 가능
    def __init__(self, x, y):
        self.x = x
        self.y = y

# 3. 사용
s = Student("철수", 3)
p = Point(10, 20)

print(s.to_json())  # {"name": "\ucd2c\uc218", "grade": 3}
print(p.rstrip().to_json()) if hasattr(p, 'rstrip') else print(p.to_json()) 
# {"x": 10, "y": 20}
    