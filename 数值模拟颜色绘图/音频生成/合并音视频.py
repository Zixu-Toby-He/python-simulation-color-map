import moviepy

视频数据 = moviepy.VideoFileClip("无声视频.mp4")
音频数据 = moviepy.AudioFileClip("音频文件.wav")

if   (视频数据.duration < 音频数据.duration):
	音频数据 = 音频数据.subclipped(0, 视频数据.duration)
elif (视频数据.duration > 音频数据.duration):
	视频数据 = 视频数据.subclipped(0, 音频数据.duration)
else:
	pass

视频数据.audio = 音频数据

视频数据.write_videofile(
	"有声视频.mp4",
	codec       = "libx264",
	audio_codec = "aac",
	threads     = 4,
	#verbose     = False,
	logger      = None
)

视频数据.close()
音频数据.close()