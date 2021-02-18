'''
Creates a Spectrum display of sound coming from the microphone
'''

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import time

matplotlib.use('TkAgg')

# how many audio samples per frame
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 2000

p = pyaudio.PyAudio()
print(p.get_default_input_device_info())

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

# Setup plots
fig, ax = plt.subplots()

# placeholder values for matplotlib optimisation
x = np.arange(0, CHUNK)
line, = ax.plot(x, np.random.rand(CHUNK))

# Formatting for the Analyser
ax.set_ylim(-2**15, 2**15-1)
ax.set_xlim(0, CHUNK)
ax.set_ylabel('Amplitude')
ax.set_xlabel('time')
plt.show(block=False)
i=0

# streams in data
while True:
    data = stream.read(CHUNK)
    data_int = np.frombuffer(data, dtype=np.int16) * 10
    line.set_ydata(data_int)
    fig.suptitle(f'Sound From -- {time.strftime("%H:%M:%S")}')
    fig.canvas.draw()
    fig.canvas.flush_events()