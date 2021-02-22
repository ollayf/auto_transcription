import wave
import pyaudio
import logging
from env import *
import queue
from pynput import keyboard
import time
import pyaudio
import wave

keys_pressed = []
def on_press(key):
    keys_pressed.append(key.char)
    return True
    
def on_release(key):
    keys_pressed.remove(key.char)
    return True

def write_wav(filename, data, channels, sampwidth, rate):
    logging.info("write wav %s", filename)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        # wf.setsampwidth(self.pa.get_sample_size(FORMAT))
        assert FORMAT == pyaudio.paInt16
        wf.setsampwidth(sampwidth)
        wf.setframerate(rate)
        wf.writeframes(data)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "./recordings/output.wav"
BLOCKS_PER_SECOND = 50
CHUNK = int(RATE/BLOCKS_PER_SECOND)

p = pyaudio.PyAudio()
frames = []
buffer_data = bytearray()
buffer_queue = queue.Queue()

def callback(in_data, frame_count, time_info, status):
    buffer_queue.put(in_data)
    return (in_data, pyaudio.paContinue)

kwargs = {
    'format': pyaudio.paInt16,
    'channels': CHANNELS,
    'rate': RATE,
    'input': True,
    'frames_per_buffer': CHUNK,
    'stream_callback': callback
}

stream = p.open(**kwargs)
key_events = keyboard.Listener(on_press=on_press, on_release=on_release)
key_events.start()

while True:
    if 'w' in keys_pressed:
        print('W pressed')
        stream.start_stream()
        print("start Stream")

    elif 'q' in keys_pressed:
        print("Something coocked")
        input()
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Saving recording into ", WAVE_OUTPUT_FILENAME)
        write_wav(WAVE_OUTPUT_FILENAME, buffer_data, CHANNELS, 2, RATE)

    elif 's' in keys_pressed:
        print("Saving recording into ", WAVE_OUTPUT_FILENAME)
        write_wav(WAVE_OUTPUT_FILENAME, buffer_data, CHANNELS, 2, RATE)

    print('Adding New data to buffer')
    frame = buffer_queue.get()
    buffer_data.extend(frame)
    print("Added new frame into data")