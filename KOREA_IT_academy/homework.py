
'''
실습
leftShoulder
rightShoulder
leftHip
rightHip
위 4곳의 x, y 좌표를 받으시오
leftShoulder-x : 100
leftShoulder-y : 300

rightShoulder
leftHip
rightHip
단계(보통(80점)(3%이내), 경고(50점)(5%이내), 위험(10점)(그 외))
어깨 좌우축 상태: 보통
골반 좌우축 상태: 경고
척추 곧음 정도: 경고
종합 점수: 60점

'''
lt_shoulder = [100 ,300]
rt_shoulder = [200 ,305]
lt_hip = [120 ,150]
rt_hip = [180 ,155]

axis_shoulder = (rt_shoulder[1] - lt_shoulder[1])/(rt_shoulder[0] - lt_shoulder[0])
abs_axis_shoulder = abs(axis_shoulder)
axis_hip = (rt_hip[1] - lt_hip[1])/(rt_hip[0] - lt_hip[0])
abs_axis_hip = abs(axis_hip)
axisdev_x = (lt_shoulder[0] + rt_shoulder[0]- lt_hip[0] - rt_hip[0])/(rt_shoulder[0] + rt_hip[0] - lt_shoulder[0] - lt_hip[0])
axisdev_y = (lt_shoulder[1] + rt_shoulder[1]- lt_hip[1] - rt_hip[1])/(rt_shoulder[1] - rt_hip[1] + lt_shoulder[1] - lt_hip[1])
dev_axis = abs(axisdev_x) + abs(axisdev_y)
list1 = [abs_axis_shoulder, abs_axis_hip, dev_axis]
if list1[0] <= 0.03 :
    shoulder_level = ["보통", 80]
elif list1[0] <= 0.05 :
    shoulder_level = ["경고", 50]
else :
    shoulder_level = ["위험", 10]

if list1[1] <= 0.03 :
    hip_level = ["보통", 80]
elif list1[1] <= 0.05 :
    hip_level = ["경고", 50]
else :
    hip_level = ["위험", 10]

if list1[2] <= 0.03 :
    axis_level = ["보통", 80]
elif list1[1] <= 0.05:
    axis_level = ["경고", 50]
else:
    axis_level = ["위험", 10]
overall_point = (shoulder_level[1] + hip_level[1] + axis_level[1]) / 3
print("어깨 좌우축 상태: ", shoulder_level[0])
print("골반 좌우축 상태: ", hip_level[0])
print("척추 곧음 정도: ", axis_level[0])
print("종합점수: ", int(overall_point))
