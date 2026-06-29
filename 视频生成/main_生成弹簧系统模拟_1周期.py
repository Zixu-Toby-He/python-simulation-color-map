import os
import traceback
import pathlib

import cv2
import numpy
import moviepy


import 视频模拟
import 音频模拟

结束时刻 = 2 * numpy.pi

def 生成弹簧链模拟视频(视频路径 = "弹簧系统模拟.mp4"):
	fps = 30
	# 生成视频
	模拟迭代器 = 视频模拟.弹簧链模拟迭代器(结束时刻 = 结束时刻, fps = fps)
	四字代码 = cv2.VideoWriter.fourcc(*"mp4v")
	单帧大小 = 模拟迭代器.x1.shape[::-1]
	视频对象   = cv2.VideoWriter(
		视频路径,
		四字代码,
		fps,
		单帧大小
	)
	
	for t, x1, x2 in 模拟迭代器:
		B, G, R = 视频模拟.效果增强.平方渲染(视频模拟.二维颜色映射.HSV极坐标映射(x1, x2))
		当前帧 = cv2.merge([B, G, R])
		print("视频进度：{} %".format(t / 结束时刻 * 100))
		视频对象.write(当前帧)
	视频对象.release()

def 生成弹簧链模拟音频(音频路径 = "弹簧系统模拟.wav"):
	音频生成器 = 音频模拟.弹簧链模拟生成器(
		结束时刻 = 结束时刻,
		基频系数 = 220,
		初始参数 = (0.5, 0.5)
	)
	音频生成器.生成数据()
	音频生成器.写入音频文件(音频路径)

def 合并音频与视频(音频路径, 视频路径, 结果路径):
	视频数据 = moviepy.VideoFileClip(str(视频路径))
	音频数据 = moviepy.AudioFileClip(str(音频路径))
	if   (视频数据.duration < 音频数据.duration):
		音频数据 = 音频数据.subclipped(0, 视频数据.duration)
	elif (视频数据.duration > 音频数据.duration):
		视频数据 = 视频数据.subclipped(0, 音频数据.duration)
	else:
		pass

	视频数据.audio = 音频数据

	视频数据.write_videofile(
		str(结果路径),
		codec       = "libx264",
		audio_codec = "aac",
		threads     = 4,
		#verbose     = False,
		logger      = None
	)

	视频数据.close()
	音频数据.close()

try:
	当前路径 = pathlib.Path(__file__).parent
	(当前路径 / "output").mkdir(parents=True, exist_ok=True)
	生成弹簧链模拟视频(当前路径 / "output" / "弹簧系统模拟_无声.mp4")
	生成弹簧链模拟音频(当前路径 / "output" / "弹簧系统模拟_音频.wav")
	合并音频与视频(
		当前路径 / "output" / "弹簧系统模拟_音频.wav",
		当前路径 / "output" / "弹簧系统模拟_无声.mp4",
		当前路径 / "output" / "弹簧系统模拟.mp4"
	)

except:
	traceback.print_exc()
	print()
	print()
	print()
	os.system("pause")
