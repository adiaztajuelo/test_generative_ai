from config import audio_lince_iberico_wave, temp_wave_1min, output_file, short_audio_mp3, output_transcription_complete
from pydub import AudioSegment
import whisper




# Función para dividir el archivo de data_audio en segmentos
def split_audio_and_transcribe(file_path, max_duration):
    sound = AudioSegment.from_wav(file_path)
    # sound = AudioSegment.from_mp3(file_path)
    start_time = 0
    model = whisper.load_model("base")

    while start_time < len(sound):
        end_time = min(start_time + max_duration, len(sound))
        segment = sound[start_time:end_time]

        # Guarda el segmento como archivo temporal
        segment.export(temp_wave_1min, format="wav")

        # transcribe
        transcribe_result = model.transcribe(temp_wave_1min)

        with open(output_transcription_complete, "a", encoding="utf-8") as txt:
            txt.write(transcribe_result["text"])

        transcription_data = transcribe_result["text"]
        print(transcription_data)

        # Actualiza el inicio para el próximo segmento
        start_time = end_time



audio_file_path = audio_lince_iberico_wave

# Duración máxima de cada parte en milisegundos
max_duration_per_segment = 60000  # 60 segundos
# Llama a la función para transcribir el archivo de data_audio por partes
split_audio_and_transcribe(audio_file_path, max_duration_per_segment)

