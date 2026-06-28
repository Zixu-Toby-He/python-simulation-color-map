import abc
import typing

import numpy
import cv2

class 模拟迭代器(abc.ABC):
	'''
	该迭代器假设初速度均为 0
	'''
	def __init__(self, 结束时刻: float, 分割精细度:int = 512, fps:int = 30, *args, **kwargs):
		self.时间坐标:float          = 0
		self.时刻迭代器:numpy.nditer = numpy.nditer(numpy.linspace(0, 结束时刻, int(结束时刻 * fps + 1)))
		self.下一时刻:numpy.float64  = numpy.float64(next(self.时刻迭代器))

		x1下限, x1上限 = self.x1范围
		x2下限, x2上限 = self.x2范围
		self.x1: numpy.ndarray = numpy.linspace(x1下限, x1上限, 分割精细度 + 1)
		self.x2: numpy.ndarray = numpy.linspace(x2下限, x2上限, 分割精细度 + 1)
		self.x1, self.x2 = numpy.meshgrid(self.x1, self.x2)

	@abc.abstractmethod
	def 演进(self):
		'''
		不是演化一步，而是直接演化到下一时刻
		'''
		if(self.下一时刻 != self.时间坐标):
			# 演化逻辑
			self.时间坐标 = self.下一时刻

	@property
	@abc.abstractmethod
	def x1范围(self):
		return (0, 1)
	@property
	@abc.abstractmethod
	def x2范围(self):
		return (0, 1)

	def __next__(self):
		self.演进()
		try:
			self.下一时刻 = numpy.float64(next(self.时刻迭代器))
		except StopIteration:
			raise StopIteration
		return self.时间坐标, self.x1, self.x2
	def __iter__(self):
		return self

sqrt3 = numpy.sqrt(3)
class 弹簧链模拟迭代器(模拟迭代器):
	"""
	物理系统：三根完全相同的弹簧链接着刚体边界与两个完全相同的质点
		|     1     2     |   K = 1/2 * m * (d/dt(x1))^2 + 1/2 * m * (d/dt(x2))^2
		|~~~~~O~~~~~O~~~~~|
		|  k  m  k  m  k  |   V = 1/2 * k * x1^2 + 1/2 * x2^2 + 1/2 * (x1 - x2)^2
	精确解：（其中k = m * omege^2）
		x1 + x2 = Const_1c * cos(    omege * t) + Const_1s * sin(    omege * t)
		x1 - x2 = Const_3c * cos(3 * omege * t) + Const_3s * sin(3 * omege * t)
	此处取 omega 恒为1
	"""
	def __init__(self, 结束时刻, 分割精细度 = 512, fps = 30, *args, **kwargs):
		super().__init__(结束时刻 = 结束时刻, 分割精细度 = 分割精细度, fps = fps)
		self.Const_1c = self.x1 + self.x2
		self.Const_3c = self.x1 - self.x2
		self.Const_1s = 0
		self.Const_3s = 0

	@property
	def x1范围(self):
		return (-1, 1)
	@property
	def x2范围(self):
		return (-1, 1)

	def 演进(self):
		if (self.时间坐标 != self.下一时刻):
			和 = self.Const_1c * numpy.cos(        self.下一时刻) + self.Const_1s * numpy.sin(        self.下一时刻)
			差 = self.Const_3c * numpy.cos(sqrt3 * self.下一时刻) + self.Const_3s * numpy.sin(sqrt3 * self.下一时刻)
			self.x1 = (和 + 差) / 2
			self.x2 = (和 - 差) / 2
			self.时间坐标 = self.下一时刻

class 双摆模拟迭代器(模拟迭代器):
	"""
	物理系统：两根长度相同的绳子系着相同的质点
	---------
	    |
	    |  l     K = 1/2 * m * l^2 * (2 * (d/dt(theta_1))^2 + (d/dt(theta_2))^2 + 2 * cos(theta_1 - theta_2) * (d/dt(theta_1)) * (d/dt(theta_2)))
	    |
	    O  M
	    |
	    |  l     V = - m * g * l * (2 * cos(theta_1) + cos(theta_2))
	    |
	    O  M
	动力学方程： g = l * omega^2，D = d/dt
		2 * D^2(theta_1) + cos(theta_1 - theta_2) * D^2(theta_2) + sin(theta_1 - theta_2) * (D(theta_2))^2 + 2 * omega^2 sin(theta_1) = 0
		    D^2(theta_2) + cos(theta_1 - theta_2) * D^2(theta_1) - sin(theta_1 - theta_2) * (D(theta_1))^2 +     omega^2 sin(theta_1) = 0
	精确解：无
	数值计算方法：

	此处取 omega 恒为1
	"""
	def __init__(self, 结束时刻, 分割精细度 = 512, fps = 30, *args, **kwargs):
		super().__init__(结束时刻 = 结束时刻, 分割精细度 = 分割精细度, fps = fps)
		self.x1_prev = 0
		self.x2_prev = 0

	@property
	def x1范围(self):
		return (0, 2 * numpy.pi)
	@property
	def x2范围(self):
		return (0, 2 * numpy.pi)

	def 演进(self):
		if (self.时间坐标 != self.下一时刻):

			# 归一化
			self.x1 %= (2 * numpy.pi)
			self.x2 %= (2 * numpy.pi)
			
			self.时间坐标 = self.下一时刻