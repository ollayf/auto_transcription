import wave
import pyaudio
import logging
from env import *

def write_wav(self, filename, data):
    logging.info("write wav %s", filename)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        # wf.setsampwidth(self.pa.get_sample_size(FORMAT))
        assert FORMAT == pyaudio.paInt16
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(data)