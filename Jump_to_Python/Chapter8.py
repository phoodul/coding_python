'''08-1 정규 표현식 살펴보기 '''

data = """
park 800905-1049118
kim 700905-1059119 
"""

result = []

for line in data.split("\n"):
    word_result = []
    for word in line.split(" "):
        if len(word) == 14 and word[:6].isdigit() and word[7:].isdigit():
            word = word[:6] + "-" + "*"*7
        word_result.append(word)
    result.append(" ".join(word_result))
print("\n".join(result))

import re

data = """
park 800905-1049118
kim 700905-1059119 
 """
pat = re.compile(r"(\d{6})[-]\d{7}")
print(pat.sub(r"\g<1>-*******", data))

k = re.compile(r"[\w]+")
p = k.match("abc")
print(p)

import re
p = re.compile(r'[a-z]+')

m = p.match("python")
print(m)