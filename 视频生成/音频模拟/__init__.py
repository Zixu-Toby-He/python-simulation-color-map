import abc
import pydub
import numpy


# 音频文件中振幅为 int16 数字
def 声道归一化(位移):
	位移极大值 = numpy.max(位移)
	位移极小值 = numpy.min(位移)
	if (位移极大值 == 位移极小值):
		return numpy.zeros(len(位移), dtype = numpy.int16)
	# 归一化到 [-32767, 32767]
	return numpy.int16(0x7FFF * (2 * 位移 - 位移极大值 - 位移极小值) / (位移极大值 - 位移极小值))

# 音频文件数据小，不需要利用迭代器直接生成即可
class 音频模拟生成器(abc.ABC):
	def __init__(
		self,
		结束时刻: float | int,
		采样率:   int               = 96000,
		基频系数: float | int       = 220,
		初始参数: tuple[int] | None = None
	):
		self.所有时刻 = numpy.linspace(
			0,
			2 * numpy.pi * 基频系数 * 结束时刻,
			int(结束时刻 * 采样率 + 1),
			dtype = "float64"
		)
		self.采样率 = 采样率
		if (初始参数 == None):
			self.x1初值 = 0
			self.x2初值 = 0
		else:
			self.x1初值, self.x2初值 = 初始参数[:2]

		if (((self.x1范围[0] <= self.x1初值) and (self.x1初值 <= self.x1范围[1])) and (((self.x2范围[0] <= self.x2初值) and (self.x2初值 <= self.x2范围[1])))):
			pass
		else:
			raise ValueError("初始参数错误：其各值取值范围为\n\t[0] -- ({})\n\t[1] -- ({})".format(self.x1范围, self.x2范围))
		self.已生成数据 = False

	@abc.abstractmethod
	def _演进(self, i):
		'''
		根据索引 i 计算第 i 个时刻的 x1, x2
		'''
		raise NotImplementedError

	@property
	@abc.abstractmethod
	def x1范围(self):
		return (0, 1)

	@property
	@abc.abstractmethod
	def x2范围(self):
		return (0, 1)

	def 生成数据(self):
		self.x1 = numpy.empty_like(self.所有时刻)
		self.x2 = numpy.empty_like(self.所有时刻)
		for i in range(len(self.所有时刻)):
			x1, x2 = self._演进(i)
			self.x1[i] = x1
			self.x2[i] = x2
		self.已生成数据 = True

	@property
	@abc.abstractmethod
	def _左通道数据(self):
		return self.x1

	@property
	@abc.abstractmethod
	def _右通道数据(self):
		return self.x2

	@property
	def 左通道数据(self):
		if (self.已生成数据):
			return 声道归一化(self._左通道数据)
		else:
			raise ValueError("尚未生成数据")

	@property
	def 右通道数据(self):
		if (self.已生成数据):
			return 声道归一化(self._右通道数据)
		else:
			raise ValueError("尚未生成数据")

	def 写入音频文件(self, 输出文件路径):
		左声道音频 = pydub.AudioSegment(self.左通道数据.tobytes(), frame_rate=self.采样率, sample_width=2, channels=1)
		右声道音频 = pydub.AudioSegment(self.右通道数据.tobytes(), frame_rate=self.采样率, sample_width=2, channels=1)
		合并音频 = pydub.AudioSegment.from_mono_audiosegments(左声道音频, 右声道音频)
		合并音频.export(输出文件路径, format="wav")

sqrt3 = numpy.sqrt(3)
class 弹簧链模拟生成器(音频模拟生成器):
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
	def __init__(self, 结束时刻, 采样率 = 96000, 基频系数 = 440, 初始参数 = None):
		super().__init__(结束时刻, 采样率, 基频系数, 初始参数)
		self.Const_1c = self.x1初值 + self.x2初值
		self.Const_3c = self.x1初值 - self.x2初值
		self.Const_1s = 0
		self.Const_3s = 0

	def _演进(self, i):
		'''
		根据索引 i 计算第 i 个时刻的 x1, x2
		'''
		和 = self.Const_1c * numpy.cos(        self.所有时刻[i]) + self.Const_1s * numpy.sin(        self.所有时刻[i])
		差 = self.Const_3c * numpy.cos(sqrt3 * self.所有时刻[i]) + self.Const_3s * numpy.sin(sqrt3 * self.所有时刻[i])
		x1 = (和 + 差) / 2
		x2 = (和 - 差) / 2
	
		return x1, x2

	@property
	def _左通道数据(self):
		return self.x1

	@property
	def _右通道数据(self):
		return self.x2

	@property
	def x1范围(self):
		return (0, 1)

	@property
	def x2范围(self):
		return (0, 1)