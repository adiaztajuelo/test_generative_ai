import streamlit as st
import whisper
from pydub import AudioSegment
#
from paths_input_output import audio_lince_iberico_wave, short_audio_wave, temp_wave_1min, output_file, short_audio_mp3, output_transcription




st.header("Knowledge base extracted from audio")
audio_file_path = st.file_uploader("Audio file path (wav)", type="wav")
max_duration_per_segment = st.text_input("Duration per segment", value=60000, type="default")

audio_file_text = st.file_uploader("Audio file text (Knowledge base)", type="txt")

@st.cache_resource
def split_audio_and_transcribe(file_path, max_duration):
    sound = AudioSegment.from_wav(file_path)
    # sound = AudioSegment.from_mp3(file_path)
    start_time = 0
    model = whisper.load_model("base")

    while start_time < len(sound):
        end_time = min(start_time + int(max_duration), len(sound))
        segment = sound[start_time:end_time]

        # Guarda el segmento como archivo temporal
        segment.export(temp_wave_1min, format="wav")

        # transcribe
        transcribe_result = model.transcribe(temp_wave_1min)

        with open(output_transcription, "a", encoding="utf-8") as txt:
            txt.write(transcribe_result["text"])

        transcription_data = transcribe_result["text"]
        print(transcription_data)

        # Actualiza el inicio para el próximo segmento
        start_time = end_time
    txt.close()

@st.cache_resource
def create_embeddings(pdf):
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    knowledge_base = FAISS.from_texts(chunks, embeddings)

    return knowledge_base


def main():
    if audio_file_path:
        split_audio_and_transcribe(audio_file_path, max_duration_per_segment)
        # knowledge_base = create_embeddings(pdf_object)
        # user_question = st.text_input("Ask anything about the PDF file...")

if __name__ == '__main__':
    main()