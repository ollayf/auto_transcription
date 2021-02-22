import time, logging
from datetime import datetime
import threading, collections, queue, os, os.path
import deepspeech
import numpy as np

import soundfile as sf
import glob

MODEL = 'models/deepspeech-0.9.3-models.pbmm'
SCORER = 'models/deepspeech-0.9.3-models.scorer'
FILE = 'data/OpenSLR/LibriSpeech/test-clean/121/121726/121-121726-0001.flac'
AUDIO_EXTS = ['.wav', '.mp3', '.flac']

# now = time.strftime('%Y%m%d_%H%M%S')
# logging.basicConfig(filename=f'logs/dir_prediction_{now}.txt', level=logging.INFO)



def predict_audio(filepath, model, intermediate=False):

    soundf = sf.SoundFile(filepath, 'r')
    model_stream = model.createStream()
    while True:
        chunk = (soundf.read(320)*32767).astype(np.int16)
        if chunk.size == 0:
            print('Ending Stream')
            result = model_stream.finishStream()
            break
        model_stream.feedAudioContent(chunk)
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
    model = deepspeech.Model(MODEL)
    model.enableExternalScorer(SCORER)
    for folder in glob.glob('data/OpenSLR/LibriSpeech/test-clean/*/*/'):
        print('Predicting:', folder)
        predict_folder(folder, 'predictions.txt', model)