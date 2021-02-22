import time, logging
from datetime import datetime
import threading, collections, queue, os, os.path
from types import new_class
import deepspeech
import numpy as np
from scipy.signal.signaltools import resample
import webrtcvad
import soundfile as sf
import glob
from scipy import signal
import struct

# now = time.strftime('%Y%m%d_%H%M%S')
# logging.basicConfig(filename=f'logs/dir_prediction_{now}.txt', level=logging.INFO)



def predict_audio(filepath, model, vad_aggro=0, intermediate=False, max_succ=500, chunk_factor=1):

    soundf = sf.SoundFile(filepath, 'r')
    samp_rate = soundf.samplerate
    chunk_size = samp_rate// 100 * chunk_factor

    if vad_aggro:
        vad = webrtcvad.Vad(vad_aggro)
        if samp_rate not in [800, 1600, 32000]:
            # adapts to the current samp rate
            if samp_rate < 8000:
            # will have problems upsampling
                samp_rate = 0
            elif samp_rate < 16000:
                samp_rate = 8000
            elif samp_rate < 32000:
                samp_rate = 16000
            else:
                samp_rate = 32000
            samp_changed = True
            new_chunk_size = samp_rate// 100 * chunk_factor


    print('Sampler rate is', samp_rate)
    model_stream = model.createStream()
    result = ''
    succ = 0
    last = False
    while True:
        chunk = (soundf.read(chunk_size)*32767).astype(np.int16)        
        # breaks when the audio clip is over
        if chunk.size == 0:
            print('Ending Stream')
            result += model_stream.finishStream()
            result == ' '
            break

        # only resample if samp rate is wrong
        if vad_aggro:
            if samp_changed:
                chunk = signal.resample(chunk, new_chunk_size)
                chunk = np.array(chunk, dtype=np.int16)


            chunk_bi = struct.pack("%dh" % chunk.size, *chunk)
            if not vad.is_speech(chunk_bi, samp_rate):
                print('Skipping, not speech')
                if last:
                    stream_result = model_stream.finishStream()
                    model_stream = model.createStream()
                    last = False
                    if stream_result:
                        result += stream_result
                        result += ' '
                continue

        succ += 1
        model_stream.feedAudioContent(chunk)
        last = True
        # Don't bother processing if it is not speech
        # converting to  binary for vad
        if not succ % max_succ:
            print('Skipping', succ)
            stream_result = model_stream.finishStream()
            if stream_result:
                result += stream_result
                result += ' '
            model_stream = model.createStream()
            continue

        if intermediate:
            print('Best Guess:', model_stream.intermediateDecode())
        


    print(f'Final Result for {filepath}', result)
    return result

def predict_folder(folder_path, output_path, model):
    for file in sorted(os.listdir(folder_path)):
        basefile, ext = os.path.splitext(file)
        if ext in AUDIO_EXTS:
            file_path = os.path.join(folder_path, file)
            result = predict_audio(file_path, model)
            # for logging the detections
            if output_path == os.path.basename(output_path):
                output_path = os.path.join(folder_path, output_path)
            with open(output_path, 'a+') as t:
                t.write(f'{basefile} {result.upper()}\n')
        else:
            print(file, 'not in audio format')

if __name__ == '__main__':
    MODEL = 'models/deepspeech-0.9.3-models.pbmm'
    SCORER = 'models/deepspeech-0.9.3-models.scorer'
    FILE = 'data/youtube/videos/mono_EPT.wav'
    AUDIO_EXTS = ['.wav', '.mp3', '.flac']
    model = deepspeech.Model(MODEL)
    model.enableExternalScorer(SCORER)
    # for folder in glob.glob('data/OpenSLR/LibriSpeech/test-clean/*/*/'):
    #     print('Predicting:', folder)
    #     predict_folder(folder, 'predictions.txt', model)

    predict_audio(FILE, model, 1, intermediate=True, chunk_factor=3)