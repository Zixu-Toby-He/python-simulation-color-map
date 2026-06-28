import numpy
import pydub
import pydub.playback
import cv2

def 获取播放时长(视频路径):
	视频对象 = cv2.VideoCapture(视频路径)
	每秒帧数 = 视频对象.get(cv2.CAP_PROP_FPS)
	总帧数量 = 视频对象.get(cv2.CAP_PROP_FRAME_COUNT)
	视频时长 = 总帧数量 / 每秒帧数
	视频对象.release()
	return 视频时长

视频时长 = 获取播放时长("弹簧系统模拟（4周期）.mp4")


sqrt3 = numpy.sqrt(3)

采样率     = 96000  # 示例采样率：96 kHz
时间轴     = numpy.arange(0, 视频时长, 1 / 采样率)  # 10秒的时间坐标
def 生成左声道音频(时间轴, 基频 = 440):
	基角频 = 2 * numpy.pi * 基频
	return numpy.sin(基角频 * 时间轴) + 0.25 * numpy.sin(sqrt3 * 基角频 * 时间轴)
def 生成右声道音频(时间轴, 基频 = 440):
	基角频 = 2 * numpy.pi * 基频
	return numpy.sin(基角频 * 时间轴) + 0.25 * numpy.sin(sqrt3 * 基角频 * 时间轴)

左声道数据 = 生成左声道音频(时间轴, 基频 = 440) # 440 Hz的正弦波
右声道数据 = 生成右声道音频(时间轴, 基频 = 440) # 220 Hz的正弦波


print(左声道数据)
print(右声道数据)
# 音频文件中振幅为 int16 数字
def 声道归一化(位移):
	位移极大值 = numpy.max(numpy.abs(位移))
	return numpy.int16(0x7FFF * 位移 / 位移极大值)

左声道数据 = 声道归一化(左声道数据)
右声道数据 = 声道归一化(右声道数据)

左声道音频 = pydub.AudioSegment(左声道数据.tobytes(), frame_rate=采样率, sample_width=2, channels=1)
右声道音频 = pydub.AudioSegment(右声道数据.tobytes(), frame_rate=采样率, sample_width=2, channels=1)

合并音频 = pydub.AudioSegment.from_mono_audiosegments(左声道音频, 右声道音频)

# 指定一个可写入的文件路径
音频文件路径 = "音频文件.wav"
合并音频.export(音频文件路径, format="wav")

# 播放（不成功）
# pydub.playback.play(音频)