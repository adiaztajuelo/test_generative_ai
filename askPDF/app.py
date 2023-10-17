import os
import streamlit as st
import databutton as db
import io
import re
import sys
from typing import Any, Callable
from dotenv import load_dotenv
from PIL import Image
from PyPDF2 import PdfReader
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import SystemMessage, HumanMessage 
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks import get_openai_callback
from langchain.memory import ConversationBufferWindowMemory

# Load OpenAI API Key from .env
load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

# Set the context for the LLM
LLM_CONTEXT = """
    Eres un guía turístico de Santa Cruz de Tenerife y San Cristóbal de La Laguna. Los usuarios
    te preguntan cuestiones sobre estos municipios y, en base a un contexto que se te proporciona,
    debes responder de forma muy útil para los usuarios.
    
    En el contexto es posible que se te incluyan links. Estos links son muy importantes y útiles
    para los usuarios, por lo que siempre debes incluirlos. La estructura de los links vendrá dada
    de la siguiente forma:
    
    - Ejemplo link ubicación: ::link::::"Ubicación de <nombre_de_sitio>"(<link_ubicación>)::
    
    - Ejemplo link vídeo: ::link::::"Vídeo de <nombre_de_sitio>"(<link_vídeo>)::
    
    - Ejemplo link imagen: ::image::::"<image_description>"(<image_path>)::
    
    Los links que se te proporcionen siempre debes darle un formato adecuado, EXCEPTO LAS IMÁGENES.
    LAS IMÁGENES NO PROPORCIONES NUNCA EL LINK O IMAGE_PATH. En caso de haber imágenes en el contexto
    proporcionado, debes generar al final del mensaje lo siguiente:
    
    images = {'image_1':{'path':<path_a_la_imagen>, 'description':<descripcion_imagen>},
    'image_2':{'path':<path_a_la_imagen>, 'description':<descripcion_imagen>}}
    
    Esto debes respetarlo siempre para las imágenes, y siempre con el mismo tipo de estructura."""


# Set the header of the webapp
st.header("guacimAIra💬🍌")

# Define the function to load the data and create the knowledge base
@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text=("Chiquita pachorra tengo muchacho... Dame un fisquito tiempo pa' "
                              "ver el par de sitios guapos que decirte anda...")):
        pdf_reader = PdfReader("./inputs/TENERIFE.pdf")
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        knowledge_base = FAISS.from_texts(chunks, embeddings)
        
        retriever = knowledge_base.as_retriever()
        retriever.search_kwargs["distance_metric"] = "cos"
        retriever.search_kwargs["fetch_k"] = 5
        retriever.search_kwargs["maximal_marginal_relevance"] = True
        retriever.search_kwargs["k"] = 5

        return retriever

# Define the chatbot's memory
@st.cache_resource(show_spinner=False)
def load_memory():
    memory=ConversationBufferWindowMemory(
        k=3,
        memory_key="chat_history",
        return_messages=True,
        output_key='answer'
    )
    return memory

def clear_cache_and_session():
    for key in st.session_state.keys():
        st.session_state.pop(key)

def chat_ui(qa, memory):
    # Accept user input
    if prompt:= st.chat_input("Échate un palique"):
        # Add user message to chat history
        st.session_state.messages.append({"role":"user", "content":prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # Load the memory variables, which include the chat history
            memory_variables = memory.load_memory_variables({})

            # Predict the AI's response in the conversation
            with st.spinner("Deja preguntarle a la viejita y te digo..."):
                response = capture_and_display_output(
                    qa, ({"question": prompt, "chat_history": memory_variables})
                )

            # Display chat response
            full_response += response["answer"]
            message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        # Append message to session state
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

def capture_and_display_output(func: Callable[..., Any], args, **kwargs) -> Any:
    # Capture the standard output
    original_stdout = sys.stdout
    sys.stdout = output_catcher = io.StringIO()

    # Run the given function and capture its output
    response = func(args, **kwargs)

    # Reset the standard output to its original value
    sys.stdout = original_stdout

    # Clean the captured output
    output_text = output_catcher.getvalue()
    clean_text = re.sub(r"\x1b[.?[@-~]", "", output_text)

    # Custom CSS for the response box
    st.markdown("""
    <style>
        .response-value {
            border: 2px solid #6c757d;
            border-radius: 5px;
            padding: 20px;
            background-color: #f8f9fa;
            color: #3d3d3d;
            font-size: 20px;  # Change this value to adjust the text size
            font-family: monospace;
        }
    </style>
    """, unsafe_allow_html=True)

    # Create an expander titled "See Verbose"
    with st.expander("See Langchain Thought Process"):
        # Display the cleaned text in Streamlit as code
        st.code(clean_text)

    return response

def main():

    retriever = load_data()
    memory = load_memory()
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k",
                     temperature=0.3,
                     streaming=True,
                     verbose=True,
                     top_p=0.95)

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        verbose=True,
        chain_type="stuff",
        return_source_documents=True
    )

    # Create a button to trigger the clearing of cache and session states
    st.sidebar.button("Empieza un nuevo palique", on_click=clear_cache_and_session)

    # Initialize chat history
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {'role': "system",
             'content': LLM_CONTEXT},
            {'role': "assistant",
             'content': "¡Oh, qué pasó! Aquí GuacimAIra, ¿de qué quieres que paliquemos hoy?"}
        ]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Run chat_ui function passing the ConversationalRetrievalChain
    chat_ui(qa, memory)

            

if __name__ == '__main__':
    main()
