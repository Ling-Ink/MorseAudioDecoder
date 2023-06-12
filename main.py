import math
import sys

import numpy as np
import wave
import pylab
from tqdm import tqdm

morse_dict = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
    '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
    '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
    '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
    '-.--': 'Y', '--..': 'Z',

    '.----': '1', '..---': '2', '...--': '3', '....-': '4', '.....': '5',
    '-....': '6', '--...': '7', '---..': '8', '----.': '9', '-----': '0',

    '.-.-.-': '.', '---...': ':', '--..--': ',', '-.-.-.': ';', '..--..': '?',
    '-...-': '=', '.----.': '\'', '-..-.': '/', '-.-.--': '!', '-....-': '-',
    '..--.-': '_', '.-..-.': '"', '-.--.': '(', '-.--.-': ')', '...-..-': '$',
    '.--.-.': '@'
}

# 加载音频
audio = wave.open(sys.argv[1], 'rb')

# 读音频信息
params = audio.getparams()
print(params)
n_channels, _, sample_rate, n_frames = params[:4]

# 将显示的所有图分辨率调高
pylab.figure(dpi=200, figsize=(1000000 / n_frames * 50, 2))

# 读频谱信息
str_wave_data = audio.readframes(n_frames)
audio.close()

# 将频谱信息转为数组
wave_data = np.frombuffer(str_wave_data, dtype=np.short).T

# 计算平均频率
wave_avg = int(sum([abs(x / 10) for x in wave_data]) / len(wave_data)) * 10
print("wave avg: " + str(wave_avg))

# 绘制摩斯图像
morse_block_sum = 0  # 待划分的数据
morse_block_length = 0  # 待划分的数据长度
morse_arr = []
time_arr = []
pbar = tqdm(wave_data, desc="Drawing Morse Image")
for i in pbar:
    # 高于平均值记为 1 ，反之为 0
    if abs(i) > wave_avg:
        morse_block_sum += 1
    else:
        morse_block_sum += 0
    morse_block_length += 1
    # 将数据按照指定长度划分
    if morse_block_length == 100:
        # 计算划分块的平均值
        if math.sqrt(morse_block_sum / 100) > 0.5:
            morse_arr.append(1)
        else:
            morse_arr.append(0)
        # 横坐标
        time_arr.append(len(time_arr))
        morse_block_length = 0
        morse_block_sum = 0
# 输出图像
pylab.plot(time_arr, morse_arr)
pylab.savefig('result.png')

# 摩斯电码 按信号长度存储
morse_type = []
morse_len = []
# 摩斯电码长度     0  1
morse_obj_sum = [0, 0]
morse_obj_len = [0, 0]
for i in morse_arr:
    if len(morse_type) == 0 or morse_type[len(morse_type) - 1] != i:
        morse_obj_len[i] += 1
        morse_obj_sum[i] += 1
        morse_type.append(i)
        morse_len.append(1)
    else:
        if morse_len[len(morse_type) - 1] <= 100:
            morse_obj_sum[i] += 1
            morse_len[len(morse_type) - 1] += 1

# 计算信息与空位的平均长度
morse_block_avg = morse_obj_sum[1] / morse_obj_len[1]
print("morse block avg: " + str(morse_block_avg))
morse_blank_avg = morse_obj_sum[0] / morse_obj_len[0]
print("morse blank avg: " + str(morse_blank_avg))

# 转换为摩斯电码
morse_result = ""
for i in range(len(morse_type)):
    if morse_type[i] == 1:
        # 大于平均长度为"-"
        if morse_len[i] > morse_block_avg:
            morse_result += "-"
        # 小于平均长度即为"."
        elif morse_len[i] < morse_block_avg:
            morse_result += "."
    # 大于平均空位长度的为分割
    elif morse_type[i] == 0:
        if morse_len[i] > morse_blank_avg:
            morse_result += "/"

print("Morse Result: " + morse_result)

# 摩斯电码解码
morse_array = morse_result.split("/")
plain_text = ""
for morse in morse_array:
    if morse != '':
        plain_text += morse_dict[morse]
print("Plain Text: " + plain_text)
