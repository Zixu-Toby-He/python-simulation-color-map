import os
import traceback

import numpy
import cv2

def 线性重整(数组:numpy.ndarray, 目标最小值: float | int = -1, 目标最大值: float | int = 1):
	"""
	将参数通过线性的方式将数组映射到对应区间范围内
	数组：numpy.ndarray
		需要整备的数组
	目标最小值、目标最大值：需要调整的范围
	"""
	目标最小值, 目标最大值 = min([目标最大值, 目标最小值]),max([目标最大值, 目标最小值])
	最大值   = numpy.max(数组.flatten())
	最小值   = numpy.min(数组.flatten())
	返回数组1 = (数组 - 最小值) * (目标最大值 - 目标最小值) / (最大值 - 最小值) + 目标最小值
	返回数组2 = (数组 - 最大值) * (目标最大值 - 目标最小值) / (最大值 - 最小值) + 目标最大值
	return (返回数组1 + 返回数组2) / 2

class 二维颜色映射:
	"""
	该模块函数参数设置
	参数：
		x1、x2：numpy.ndarray 或 数值类型
			需要二者维度信息相同，均为二维数组(m, n)
			数值范围：-1 ~ 1
	返回值：
		图片：numpy.ndarray
			若 x1、x2 为 数值类型       则返回值 size 为 (3,)
			若 x1、x2 为 numpy.ndarray 则返回值 size = (3,m,n)
			分别对应蓝、绿、红通道
	"""
	@staticmethod
	def 平面映射(x1: numpy.ndarray | float | int, x2: numpy.ndarray | float | int):
		x1 = (x1 + 1) / 2 + ((x1 - 1) / 2 + 1)
		x2 = (x2 + 1) / 2 + ((x2 - 1) / 2 + 1)
		x3 = (2 - x1 - x2) / 2
		return numpy.uint8([255 * x1, 255 * x2, 255 * x3]) # pyright: ignore[reportArgumentType]
	@staticmethod
	def 球面映射(x1:numpy.ndarray | float, x2: numpy.ndarray | float):
		x1 = ((x1 + 1) / 2) + ((x1 - 1) / 2 + 1)
		x2 = ((x2 + 1) / 2) + ((x2 - 1) / 2 + 1)
		x3 = (1 - 0.5 * (x1**2) - 0.5 * (x2**2))**(1/2)
		return numpy.uint8([255 * x1, 255 * x2, 255 * x3]) # pyright: ignore[reportArgumentType]
	@staticmethod
	def HSV极坐标映射(x1:numpy.ndarray, x2:numpy.ndarray):
		x1 /= 2
		x2 /= 2
		色相   = numpy.arctan2(x1, x2) % (2 * numpy.pi)
		饱和度 = numpy.sqrt(x1**2 + x2**2)
		明度   = 1.0
		
		def hsv2rgb(h: numpy.ndarray, s: numpy.ndarray, v: numpy.ndarray| float):
			c = v * s
			x = c * (1 - numpy.abs((h / 60) % 2 - 1))
			m = v - c
			
			r = numpy.zeros_like(h)
			b = numpy.zeros_like(h)
			g = numpy.zeros_like(h)
			
			掩膜 = (h >=   0) & (h <  60)
			r[掩膜] = c[掩膜]
			g[掩膜] = x[掩膜]
			b[掩膜] = 0
			
			掩膜 = (h >=  60) & (h < 120)
			r[掩膜] = x[掩膜]
			g[掩膜] = c[掩膜]
			b[掩膜] = 0
			
			掩膜 = (h >= 120) & (h < 180)
			r[掩膜] = 0
			g[掩膜] = c[掩膜]
			b[掩膜] = x[掩膜]
			
			掩膜 = (h >= 180) & (h < 240)
			r[掩膜] = 0
			g[掩膜] = x[掩膜]
			b[掩膜] = c[掩膜]
			
			掩膜 = (h >= 240) & (h < 300)
			r[掩膜] = x[掩膜]
			g[掩膜] = 0
			b[掩膜] = c[掩膜]
			
			掩膜 = (h >= 300) & (h < 360)
			r[掩膜] = c[掩膜]
			g[掩膜] = 0
			b[掩膜] = x[掩膜]
			
			b, g, r = (b + m) * 255, (g + m) * 255, (r + m) * 255
			
			return numpy.uint8([b, g, r]) # pyright: ignore[reportArgumentType]
		
		return hsv2rgb(色相 * 180 / numpy.pi, 饱和度, 明度)

class 效果增强:
	"""
	将参数通过重整 bgr 数值实现对图像效果的增强
	数组：numpy.ndarray
		既可以是(3,m,n)，也可以是(m,n,3)
	"""

	@staticmethod
	def 平方渲染(bgr):
		return numpy.uint8(bgr * (bgr / 255.0))

	@staticmethod
	def exp渲染(bgr):
		return numpy.uint8(255 * (numpy.exp(1.0 * bgr / 255.0) - 1) / (numpy.e - 1))

	@staticmethod
	def cos渲染(bgr):
		return numpy.uint8(255 * (1 - numpy.cos(bgr / 510.0 * numpy.pi)))

	@staticmethod
	def sin渲染(bgr):
		return numpy.uint8(255 * (numpy.sin(bgr / 510.0 * numpy.pi)))

	@staticmethod
	def 无渲染(bgr):
		return bgr

def 生成色卡(颜色生成函数):
	色卡宽度 = 512
	横坐标 = numpy.linspace(-1, 1, 色卡宽度 + 1)
	纵坐标 = numpy.linspace(-1, 1, 色卡宽度 + 1)
	横坐标, 纵坐标 = numpy.meshgrid(横坐标, 纵坐标)

	色卡 = numpy.empty([513, 513, 3], dtype = numpy.uint8)
	B,G,R = 颜色生成函数(横坐标, 纵坐标)
	色卡[:,:,0] = B
	色卡[:,:,1] = G
	色卡[:,:,2] = R
	return 色卡


# 测试函数
if __name__ == "__main__":
	try:
		色卡宽度 = 512
		x1 = numpy.linspace(-1, 1, 色卡宽度 + 1)
		x2 = numpy.linspace(-1, 1, 色卡宽度 + 1)
		x1,x2 = numpy.meshgrid(x1,x2)
		色卡 = 生成色卡(lambda x ,y : 效果增强.无渲染(二维颜色映射.HSV极坐标映射(x,y)))
		cv2.imshow("hsv non", 色卡)
		cv2.waitKey(1)
		色卡 = 生成色卡(lambda x ,y : 效果增强.无渲染(二维颜色映射.HSV极坐标映射(x,y)))
		cv2.imshow("hsv sqr", 色卡)
		cv2.waitKey(1)
		色卡 = 生成色卡(lambda x ,y : 效果增强.exp渲染(二维颜色映射.HSV极坐标映射(x,y)))
		cv2.imshow("pic exp", 色卡)
		cv2.waitKey(1)
		色卡 = 生成色卡(lambda x ,y : 效果增强.cos渲染(二维颜色映射.HSV极坐标映射(x,y)))
		cv2.imshow("pic cos", 色卡)
		cv2.waitKey(1)

		cv2.waitKey()
		cv2.destroyAllWindows()
	except:
		traceback.print_exc()
		print()
		print()
	finally:
		os.system("pause")

