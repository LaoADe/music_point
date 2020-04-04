# -*- coding: utf-8 -*-

import cv2
import librosa
import numpy as np
from PIL import Image
from moviepy.editor import *
from natsort import natsorted
from pydub import AudioSegment


def main():
    # 音频路径
    music_path = 'music/Danny Avila - End Of The Night (Explicit).mp3'
    # 音频开始截取时间
    start_time = 67
    # 截取时长
    duration = 15
    # 采样率
    sr=44100
    # 加载音频文件
    y ,sr= librosa.load(music_path, offset=start_time, duration=duration,sr=sr)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr,
                                             hop_length=512,
                                             aggregate=np.median)
    # 获取信号中的峰值
    # delta参数对取值影响较大
    # 这个方法参数较为重要，可以写一个公式计算出部分参数的取值
    peaks = librosa.util.peak_pick(onset_env, 1, 1, 1, 1, 0.8, 5)
    # 使用beat_track函数得到速度和节拍点
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    # # 使用plp函数得到脉冲曲线
    # pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr)
    # # 得到局部脉冲的最大值
    # beats_plp = np.flatnonzero(librosa.util.localmax(pulse))
    # 创建一个节拍值1/4、2/4、3/4、4/4的数组
    M = beats * [[1 / 4], [2 / 4], [3 / 4]]
    M = M.flatten()
    M = np.sort(M)
    # # 将节拍索引转换为时间点
    # beats_times = librosa.frames_to_time(np.arange(len(beats)),
    #                                      sr=sr, hop_length=512)
    # 局部脉冲与节拍点做10%的去误差，得到节奏点
    L = []
    for i in M:
        for j in peaks:
            if i * 0.9 < j < i * 1.1:
                L.append(j)
    L = list(set(L))
    L.sort()
    # 节奏点转化为时间
    # 取前30个点，不够30个则全取
    if len(L) > 30:
        point_list = librosa.frames_to_time(L[:30], sr=sr)
    else:
        point_list = librosa.frames_to_time(L[:len(L)], sr=sr)
    # 音乐裁剪，设置开始结束时间
    end_time = point_list[len(point_list) - 1] + start_time
    start_time = start_time * 1000
    end_time = end_time * 1000
    sound = AudioSegment.from_mp3(music_path)
    word = sound[start_time:end_time]
    # 音乐储存路径
    word.export('movie/music.wav', format="wav")
    movie_cut(point_list)


def movie_cut(point_list):
    # 该方法将图片制作成规定时长的短片
    fps_list = point_list
    size = (1080, 1920)
    name = 0
    # 设置视频写出格式
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # 图片储存路径
    picture_path = 'picture/'
    # 视频写出路径
    movie_path = 'movie/'
    num = 0
    # 图片加黑边后写出路径
    picture_o = 'picture1/'
    # 图片统一加黑边，将图片制成1080，1920大小
    for i in os.listdir(picture_path):
        image1 = Image.new("RGBA", (1080, 1920))
        img = Image.open(picture_path + i)
        if img.size[0] / img.size[1] == 1080 / 1920:
            img = img
            img.save(picture_o + str(num) + '.png', 'PNG')
        elif img.size[0] / img.size[1] > 1080 / 1920:
            # 过宽，高度不够
            img = img.resize((1080, int(1080 * img.size[1] / img.size[0])), )
            image1.paste(img, (0, int((1920 - img.size[1]) / 2)))
            img = image1
            img.save(picture_o + str(num) + '.png', 'PNG')
        else:
            # 过高，宽度不够
            img = img.resize((int(1920 * img.size[0] / img.size[1]), 1920), )
            image1.paste(img, (int((1080 - img.size[0]) / 2), 0))
            img = image1
            img.save(picture_o + str(num) + '.png', 'PNG')
        num += 1
    # 将图片制作成规定时长的短片
    for i in os.listdir(picture_o):
        if name == len(fps_list):
            break
        if name == 0:
            fps = 1 / fps_list[name]
        else:
            fps = 1 / (fps_list[name] - fps_list[name - 1])
        videowriter = cv2.VideoWriter(movie_path + str(name) + ".avi", fourcc, fps, size)
        img = cv2.imread(picture_o + i)
        crop_size = (1080, 1920)
        img_new = cv2.resize(img, crop_size, interpolation=cv2.INTER_CUBIC)
        videowriter.write(img_new)
        videowriter.release()
        name += 1
        num += 1


def com_movie():
    # 该方法将视频短片拼接
    L = []
    # 访问 video 文件夹
    for root, dirs, files in os.walk("./movie"):
        # 按文件名排序
        files = natsorted(files)
        # 遍历所有文件
        for file in files:
            # 如果后缀名为 .avi
            if os.path.splitext(file)[1] == '.avi':
                # 拼接成完整路径
                filePath = os.path.join(root, file)
                # 载入视频
                video = VideoFileClip(filePath)
                # 添加到数组
                L.append(video)
    audioclip = AudioFileClip('movie/music.wav')
    # 拼接视频
    final_clip = concatenate_videoclips(L)
    final_clip = final_clip.set_audio(audioclip)
    # 生成目标视频文件
    final_clip.to_videofile("movie/target.avi", fps=24, codec="mpeg4", remove_temp=True)


if __name__ == '__main__':
    main()
    com_movie()
