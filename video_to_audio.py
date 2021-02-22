from os.path import splitext
import moviepy.editor as mp
from numpy import quantile
import deepspeech
import numpy as np
import os

def transcribe_video(video_path, output_path, model, max_succ=10):
    # if output path is just a filename, put it into the folder with the video
    if output_path == os.path.basename(output_path):
        output_path = os.path.join(os.path.dirname(video_path), output_path)
    
    # check if the output path exists
    if os.path.exists(output_path):
        input('Transcription already exists, Ctrl-C to cancel process\n or the previous transcription will be deleted')
        os.remove(output_path)
        
    video = mp.VideoFileClip(video_path)
    chunks = video.audio.iter_chunks(5000, quantize=True)
    succ = 0
    model_stream = model.createStream()
    for chunk in chunks:
        succ += 1
        chunk = chunk[:, 0] // 2 + chunk[:, 1]//2
        model_stream.feedAudioContent(chunk)
        if not succ % max_succ:
            result = model_stream.finishStream()
            model_stream = model.createStream()
            with open(output_path, 'a+') as t:
                t.write(result + ' ')
                print(result)

def extract_audio(ext, vid_path):
    audio_path = os.path.splitext(vid_path)[0] + ext
    video = mp.VideoFileClip(vid_path)
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')


if __name__ == '__main__':
    vid_path = 'data/youtube/videos/English Pronunciation Training _ Improve Your Accent & Speak Clearly.mp4'
    output_path = 'data/youtube/videos/EPT_transcription1'
    MODEL = 'models/deepspeech-0.9.3-models.pbmm'
    SCORER = 'models/deepspeech-0.9.3-models.scorer'
    model = deepspeech.Model(MODEL)
    model.enableExternalScorer(SCORER)

    transcribe_video(vid_path, output_path, model)