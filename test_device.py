import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import time

matplotlib.use('TkAgg')

# how many audio samples per frame
CHUNK = 1024*4
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
DIVISOR = 4

print('Here')
p = pyaudio.PyAudio()

print(p.get_default_input_device_info())

print('HEre')
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK,
    input_device_index = 8
)

fig, ax = plt.subplots()
x = np.arange(0, 2*CHUNK,DIVISOR)
line, = ax.plot(x, np.random.rand(2*CHUNK//DIVISOR))
ax.set_ylim(-255//2, 255//2)
ax.set_xlim(0, CHUNK*2//DIVISOR)
plt.show(block=False)

while True:
    data = stream.read(CHUNK)
    data_int = np.array(struct.unpack(str(2*CHUNK) + 'b', data)[::DIVISOR], dtype=np.int8)
    # print('Type:', type(data_int))
    # print('Dtype', data_int.dtype)
    
    line.set_ydata(data_int)
    fig.canvas.draw()
    fig.canvas.flush_events()
    # input()

# ax.plot(data_int, '-')
# plt.show()