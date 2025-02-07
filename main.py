from os import getenv
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from custom_tools import generate_routine_pdf
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
import gradio as gr
import ast
from functions import subir_pdf_a_supabase
import time
# cargar las variables de entorno
load_dotenv()

# Crear una instancia del modelo de lenguaje
llm = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base=getenv("OPENROUTER_BASE_URL"),
  model_name="google/gemini-flash-1.5",
  model_kwargs={
    "extra_headers":{
        "Helicone-Auth": f"Bearer "+getenv("HELICONE_API_KEY")
      }
  },
)

# AGENTE
memory = MemorySaver()
tools = [generate_routine_pdf]
agent_executor = create_react_agent(llm, tools, checkpointer=memory)

# documento de manual de calistenia
pdf_path = './c.pdf'

#cargar pdf
loader = PyPDFLoader(pdf_path)
docs = loader.load()

# Dividir el texto en fragmentos
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
splits = text_splitter.split_documents(docs)

# embedding de la respuest
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
 
# Crear un vector store
vectorstore = InMemoryVectorStore(embedding=embeddings)
vectorstore.add_documents(docs)

# Función principal del chatbot
def chatbot(message, history):
    yield "🤔 Analizando el contexto y preparando respuesta..."

    # Verificar si el mensaje está relacionado con la generación de rutina
    if "generar rutina" in message.lower() or "crear rutina" in message.lower():
        yield "🏋️ Generando rutina de entrenamiento..."

        messages_for_agent = []
        for msg in history:
            if msg["role"] == "user":
                messages_for_agent.append(HumanMessage(content=msg["content"]))
            else:
                messages_for_agent.append(AIMessage(content=msg["content"]))
                
        # mensaje actual del usuario
        messages_for_agent.append(HumanMessage(content=message))
        
        prompt = (
            "Por favor, genera un diccionario de rutinas de calistenia que contenga diferentes categorías de ejercicios.\n\n"
            "La estructura del diccionario debe ser la siguiente:\n\n"
            "No generes una variable de Python, simplemente escribe el diccionario en texto plano.\n"
            "Las claves del diccionario deben ser números (por ejemplo, 1, 2, 3).\n"
            "Cada valor debe ser una lista de ejercicios dentro de cada categoría.\n"
            "Los ejercicios deben ser para entrenamiento de fuerza y calistenia, como flexiones, sentadillas, dominadas, etc.\n"
            "El diccionario debe verse así:\n\n"
            "{1: ['Ejercicio 1: 3x9', 'Ejercicio 2: 3x6', 'Ejercicio 3: 2x10'],\n"
            "Cada número corresponde a un día de la semana, No generes el Domingo \n"
            "Asegúrate de que las categorías de ejercicios estén equilibradas, es decir, que tengan una mezcla de ejercicios de distintas partes del cuerpo (pecho, piernas, espalda, etc.)."
        )
        # Definir el mensaje para el agente
        messages_for_agent = [{"role": "user", "content": prompt}]
        response = llm.stream(messages_for_agent)
        exercises_dic_str = ""

        for chunk in response:
            if chunk and hasattr(chunk, 'content'):
                content = chunk.content
                if content: 
                    exercises_dic_str += content     

        yield "🏋️ Generando rutina de entrenamiento..."

        try:
            exercises_dict = ast.literal_eval(exercises_dic_str)
            print(exercises_dict)
            fig = generate_routine_pdf.invoke({"exercises_dict": exercises_dict})
            pdf_name = f"rutina_{time.time()}.pdf"
            fig.savefig(f"./files/{pdf_name}")
        except Exception as e:
            yield "❌ Error al procesar el diccionario de ejercicios. Por favor, inténtalo de nuevo."
        
        try:
            # Subir el archivo a Supabase
            subir_pdf_a_supabase(pdf_name)
            yield "Rutina generada y subida a supabase con éxito 🎉"
        except Exception as e:
            yield "❌ Error al subir el archivo a Supabase. Por favor, inténtalo de nuevo."
                 
    else:
        # Búsqueda de contexto en el vectorstore (RAG)
        relevant_docs = vectorstore.similarity_search(message)

        print("\n=== Fragmentos de documento utilizados para la respuesta ===")
        for i, doc in enumerate(relevant_docs, 1):
            texto = doc.page_content.replace("\n", " ")
            print(f"\nFragmento {i}:\n{texto[:300]}...")

        context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

        final_prompt = (
            "Eres un asistente experto en Calistenia y Street Workout. "
            "Utiliza el siguiente contexto para responder de forma breve y concisa. "
            "Si no encuentras la información, responde que no la conoces.\n\n"
            f"Contexto:\n{context_text}\n\n"
            f"Pregunta: {message}\n"
            "Respuesta:"
        )

        # Construcción del historial de mensajes
        messages = [{"role": "user", "content": final_prompt}] + history

        # Generación de la respuesta del LLM
        response = llm.stream(messages)
        partial_response = ""

        for chunk in response:
            if chunk and hasattr(chunk, 'content'):
                content = chunk.content
                if content:
                    partial_response += content
                    yield partial_response

# 7. Interfaz de Gradio
demo = gr.ChatInterface(
    chatbot,
    chatbot=gr.Chatbot(height=400, type="messages"),
    textbox=gr.Textbox(placeholder="Escribe tu mensaje aquí...", container=False, scale=7),
    title="ChatBot RAG - Calistenia y Street Workout",
    description="Asistente virtual para responder preguntas sobre Calistenia y Street Workout",
    theme="ocean",
    examples=[
        "¿Qué ejercicio es bueno para principiantes?",
        "¿qué es mejor entrenar por la mañana o por la tarde?",
        "Realiza una rutina para principiantes"
    ],
    type="messages",
    editable=True,
    save_history=True,
)

if __name__ == "__main__":
    demo.queue().launch()
