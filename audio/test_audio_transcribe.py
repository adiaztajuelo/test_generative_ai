import whisper
from whisper.utils import get_writer
from config import short_audio_mp3, temp_wave_1min
import os

model = whisper.load_model("base")
audio = short_audio_mp3
print(audio)
audio_data = whisper.load_audio(temp_wave_1min)
result = model.transcribe(temp_wave_1min)
output_directory = "./"


# Save as a TXT file without any line breaks
with open("transcription_whisper.txt", "w", encoding="utf-8") as txt:
    txt.write(result["text"])


# Save as a TXT file with hard line breaks
txt_writer = get_writer("txt", output_directory)
txt_writer(result, audio)