names = ["jennie", "hani", "kelly"]

for name in names:
    print("안녕하세요, 제 이름은 %s 입니다. \n만나서 반갑습니다." %name)
for name in names:
    print("안녕하세요, 제 이름은 {0} 입니다. \n만나서 반갑습니다.".format(name))

def greet_hospital(hospital_name, *staff_names):
    print(f"[{hospital_name}] 소속 직원 명단:")
    for name in staff_names:
        print(f"- {name}")

greet_hospital("나눔 병원", "김철수", "이영희", "박지민")

pi = 3.141592
dosage = 1250000

print(f"결과값: {pi:.2f}")        # 소수점 둘째 자리까지 표시 (3.14)
print(f"누적 환자수: {dosage:,}")  # 천 단위 콤마 추가 (1,250,000)

foods = ["pizza", "pasta", "bibimbap"]

for food in foods:
    print(f"제가 좋아하는 음식은 {food}입니다")

for ch in 'Hello':
    print(ch)

nums = range(1, 6)

sum = 0
for num in nums:
    sum += num
print(sum)

for n in range(1, 10):
    print(f"2 X {n} = {2 * n}")

list = [1, 2, 3, 4, 5, 6]
list1 = ["a", "b"]
list = list + list1
print(list)

print(["a", "b", "c"][0].upper())

colors = ["red", "green", "blue"]
colors.pop()
print(colors)

