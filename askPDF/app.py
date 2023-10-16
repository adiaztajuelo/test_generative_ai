import os
import streamlit as st

from PIL import Image
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import SystemMessage, HumanMessage 
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback

st.header("askPDF")
OPENAI_API_KEY = st.text_input("OpenAI API Key", type="password")
pdf_object = st.file_uploader("Upload file", type="pdf")

@st.cache_resource
def create_embeddings(pdf):
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=100,
        length_function=len
    )    
    chunks = text_splitter.split_text(text)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2") # sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
    knowledge_base = FAISS.from_texts(chunks, embeddings)

    return knowledge_base

def main():
    if pdf_object:
        knowledge_base = create_embeddings(pdf_object)
        user_question = st.text_input("Ask anything about the PDF file...")

        if user_question:
            os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
            docs = knowledge_base.similarity_search(user_question, 5)
            llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k")
            chain = load_qa_chain(llm, chain_type="stuff")
            messages = [
                SystemMessage(
                    content="""Eres un guía turístico súper útil. Se te pasa un contexto sobre el sitio en concreto
                    sobre el que te está preguntando el usuario y tú debes responder de manera muy útil.
                    
                    Asimismo, en el contexto es posible que se te incluyan hipervínculos. Estos son enlace de
                    mucho interés para lo que pregunta el usuario. La estructura de estos hipervínculos vendrá
                    siempre dada con la forma que se muestra a continuación.
                    
                    Ejemplos hipervínculos:
                    
                    Ejemplo 1 - [nombre_hipervinculo: "Ubicación de <nombre_de_sitio>"](<hipervinculo_ubicacion_del_sitio_en_cuestión>)
                    
                    Ejemplo 2 - [nombre_hipervinculo: "Vídeo de <nombre_de_sitio>"](<hipervinculo_a_un_video_del_sitio_en_cuestión>)
                    
                    Como ves, pueden haber hipervínculos de ubicaciones o de vídeos informativos. Debes mostrar todos los hipervínculos,
                    en caso de haberlos.
                    
                    Asimismo, en el contexto es posible que también se te proporcione información sobre imágenes
                    relevantes para lo que te está preguntando el usuario. Cuando generes la respuesta, la información
                    de las imágenes debes añadirla SIEMPRE AL FINAL DE TU RESPUESTA, pero como si fuera información de sistema
                    y NO COMO RESPUESTA AL USUARIO.
                    
                    Ejemplos imágenes:
                    
                    Ejemplo 1 - Supongamos que en el contexto proporcionado hay dos imágenes relevantes. Vendrán dadas como:
                    
                    [nombre_imagen: "<nombre_de_imagen>"](<path_a_la_imagen>)[descripcion_imagen: <descripcion_imagen>]
                    
                    En ese caso, generarás AL FINAL DEL TEXTO LO SIGUIENTE:
                    
                    images = {'image_1':{'path':<path_a_la_imagen>, 'description':<descripcion_imagen>},
                    'image_2':{'path':<path_a_la_imagen>, 'description':<descripcion_imagen>}}
                    
                    Por otro lado, SI NO HAY IMÁGENES RELEVANTES EN EL CONTEXTO, NO GENERES NADA, LIMÍTATE 
                    A RESPONDER EN BASE AL CONTEXTO PROPORCIONADO."""
                ),

                HumanMessage(content=user_question)
            ]
            
            with get_openai_callback() as cb:
                answer = chain.run(input_documents=docs, question=messages)
                print(cb)

            images_info = None
            if "images = {'imag" in answer:
                images_info = answer[answer.find("images"):]
                answer = answer.replace(images_info, "")
                images_info = images_info.split("\n")
                images_info = [chunk.strip() for chunk in images_info]
                images_info = "".join(images_info)
                images_info = eval(images_info.replace("images = ", "").replace("`",""))
            elif "images = None" in answer:
                answer.replace("images = None", "")

            st.write(answer)

            if images_info:
                for image, image_info in images_info.items():
                    try:
                        image = Image.open(image_info['path'])
                        st.image(image, caption=image_info["description"])
                    except:
                        pass
            else:
                print("No images.")

            

if __name__ == '__main__':
    main()
