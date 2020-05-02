from google.cloud import storage
from google.cloud import speech_v1p1beta1 as speech
import os
import io
import subprocess
import datetime
import math

# Settings
filepath = os.path.expanduser(os.sep.join(["~", "Downloads/for-transcript/"]))         # all files from this folder will be transcribed
output_filepath = os.path.expanduser(os.sep.join(["~", "Downloads/transcripts/"]))     # ready text files will be in this folder
bucketname = "for-text-converting"  # your name here
language_code = 'en'    # https://cloud.google.com/speech-to-text/docs/languages
alternative_language_codes = [
    "ru",
]   # up to 6 codes here
enable_speaker_diarization = True   # set True if there are multiple speakers in audio files


def prepare_audio(filepath, audio_file_name):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + ' Converting audio…    ', end="", flush=True)
    current_file = filepath + audio_file_name
    destination_file = current_file.split('.')[0] + '.opus'
    subprocess.run(['ffmpeg', '-y', '-i', current_file, '-vn', '-acodec', 'libopus', '-ac', '1',
                    '-b:a', '128k', '-ar', '48000', destination_file, '-loglevel', 'warning'])
    print('Done')
    audio_file_name = audio_file_name.split('.')[0] + '.opus'
    return audio_file_name


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + ' Uploading, might take a while…    ', end="", flush=True)
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print('Done')


def delete_blob(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

def get_transcribing_time(file_name):
    p = subprocess.run(['ffprobe', '-v', "error", "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1", file_name], capture_output=True)
    length = float(p.stdout)
    transcribing_time = math.ceil(length / 2 / 60)      # on average, transcribing speed is 2x from duration
    return transcribing_time

def google_transcribe(audio_file_name):

    audio_file_name = prepare_audio(filepath, audio_file_name)
    file_name = filepath + audio_file_name
    audio_format = speech.enums.RecognitionConfig.AudioEncoding.OGG_OPUS
    sample_rate = 48000
    bucket_name = bucketname

    upload_blob(bucket_name, file_name, audio_file_name)

    gcs_uri = 'gs://' + bucketname + '/' + audio_file_name
    transcript = ''

    client = speech.SpeechClient()
    audio = speech.types.cloud_speech_pb2.RecognitionAudio(uri=gcs_uri)

    config = {
        "enable_speaker_diarization": enable_speaker_diarization,
        "language_code": language_code,
        "alternative_language_codes": alternative_language_codes,
        "encoding": audio_format,
        "sample_rate_hertz": sample_rate,
    }

    transcribing_time = get_transcribing_time(file_name)
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + ' Transcribing, estimate waiting time is ' + str(transcribing_time) + ' min…    ', end="", flush=True)

    # Detects speech in the audio file
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)
    result = response.results[-1]
    words_info = result.alternatives[0].words

    tag = 1
    speaker = ""

    for word_info in words_info:
        if word_info.speaker_tag == tag:
            speaker = speaker+" "+word_info.word
        else:
            transcript += "speaker {}: {}".format(tag, speaker) + "\n"
            tag = word_info.speaker_tag
            speaker = ""+word_info.word

    transcript += "speaker {}: {}".format(tag, speaker)

    delete_blob(bucket_name, audio_file_name)
    os.remove(file_name)
    return transcript


def write_transcript(transcript_filename, transcript):
    f = open(output_filepath + transcript_filename,
             "w+", encoding="utf-8", errors="ignore")
    f.write(transcript)
    f.close()
    print('Done.')


if __name__ == "__main__":
    for audio_file_name in os.listdir(filepath):
        exists = os.path.isfile(
            output_filepath + audio_file_name.split('.')[0] + '.txt')
        if exists:
            pass
        else:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                + " Starting file " + audio_file_name)
            transcript = google_transcribe(audio_file_name)
            transcript_filename = audio_file_name.split('.')[0] + '.txt'
            write_transcript(transcript_filename, transcript)
