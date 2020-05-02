# Speech-to-text

Python script for converting speech to text. Uses [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text). Suitable for long audio/video files.

Originally based on [Sundar Krishnan’s work](https://towardsdatascience.com/how-to-use-google-speech-to-text-api-to-transcribe-long-audio-files-1c886f4eb3e9).

## Improvements
- The code actually works now
- Detects language automatically (from up to 6 predefined options)
- Supports any audio or video format as a source, not just MP3
- Converts to Opus format, which takes less space → faster upload
- Supports source files of any length (previously was up to 100 MB)
- Removes temporary files from disk after transcribing
- Provides succinct verbose output for every stage of the process
- Works on Windows, too

## Installation
1. Set up Google Cloud stuff: do the [6 steps](https://medium.com/@sundarstyles89/create-your-own-google-assistant-voice-based-assistant-using-python-94b577d724f9)
1. Create a [storage bucket](https://console.cloud.google.com/storage/)
1. Install [ffmpeg](https://ffmpeg.org/download.html)
1. Install all the dependencies for the .py
1. Change the settings in the top of the .py for your needs

## Usage
1. Put your audio or video files to a specified folder
1. Run .py
1. Do your stuff (the whole process will take about 50–80% of your files duration)
1. Gather your transcripts from another folder
