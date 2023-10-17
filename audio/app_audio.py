import streamlit as st
import whisper
import os
from pydub import AudioSegment
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import SystemMessage, HumanMessage
from langchain.callbacks import get_openai_callback
#
from paths_input_output import audio_lince_iberico_wave, short_audio_wave, temp_wave_1min, output_file, short_audio_mp3, output_transcription


OPENAI_API_KEY = ''

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
def create_embeddings(text_raw):
    print(f"[DEBUG] create_embeddings->  {type(text_raw)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(text_raw)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    knowledge_base = FAISS.from_texts(chunks, embeddings)

    return knowledge_base


def main():
    if audio_file_path:
        split_audio_and_transcribe(audio_file_path, max_duration_per_segment)
        print(f"[INFO] Audio file transcribed")
    if audio_file_text:
        print(f"[DEBUG] main -> inicio primer if audio_file_text")
        bytes_data = audio_file_text.read()
        try:
            encoding = 'utf-8'
            decoded_text_data = str(bytes_data, encoding)

        except:
            decoded_text_data = bytes_data
        #st.write(decoded_text_data)
        #print(f"{decoded_text_data}")
        print(f"[DEBUG] main -> fin primer if audio_file_text")

    if audio_file_text:
        print(f"[DEBUG] main -> inicio segundo if audio_file_text")
        print(f"[DEBUG] main -> {type(audio_file_text)}")
        print(f"[DEBUG] main -> {type(decoded_text_data)}")
        knowledge_base = create_embeddings(decoded_text_data)
        print(f"[INFO] Knowledge_base created")
        print(f"[DEBUG] main -> fin segundo if audio_file_text")
        user_question = st.text_input("Ask anything about the PDF file...")
        if user_question:
            os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
            docs = knowledge_base.similarity_search(user_question, 5)
            llm = ChatOpenAI(model_name="gpt-3.5-turbo")
            chain = load_qa_chain(llm, chain_type="stuff")
            messages = [
                SystemMessage(
                    content="""
                            Eres un experto en animales, concretamente en el lince ibérico. 
                            """
                ),

                HumanMessage(content=user_question)
            ]

            with get_openai_callback() as cb:
                answer = chain.run(input_documents=docs, question=messages)
                print(cb)

            st.write(answer)


if __name__ == '__main__':
    main()