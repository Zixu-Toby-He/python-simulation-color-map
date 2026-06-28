import os
import traceback

import numpy
import cv2

import 模拟
import 二维颜色映射

def 生成弹簧链模拟视频():
	fps = 30
	结束时刻 = 8 * numpy.pi
	# 生成视频
	模拟迭代器 = 模拟.弹簧链模拟迭代器(结束时刻 = 结束时刻, fps = fps)
	四字代码 = cv2.VideoWriter.fourcc(*"mp4v")
	单帧大小 = 模拟迭代器.x1.shape[::-1]
	视频对象   = cv2.VideoWriter(
		"弹簧系统模拟.mp4",
		四字代码,
		fps,
		单帧大小
	)
	
	for t, x1, x2 in 模拟迭代器:
		B, G, R = 二维颜色映射.效果增强.平方渲染(二维颜色映射.二维颜色映射.HSV极坐标映射(x1, x2))
		当前帧 = cv2.merge([B, G, R])
		print("当前进度：{} %".format(t / 结束时刻 * 100))
		视频对象.write(当前帧)
	视频对象.release()

try:
	生成弹簧链模拟视频()
except:
	traceback.print_exc()
	print()
	print()
	print()
	os.system("pause")
