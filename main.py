import streamlit as st
from groq import Groq


st.set_page_config(page_title="Chat IA", page_icon="🤖", layout="wide")


MODELOS = ['llama3-8b-8192', 'llama3-70b-8192', 'mixtral-8x7b-32768']



def inicializar_estado():
    """Inicializa el estado global de la aplicación."""
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []


def actualizar_historial(rol, contenido, avatar):
    """Agrega un mensaje al historial."""
    st.session_state.mensajes.append({
        "role": rol,
        "content": str(contenido),  
        "avatar": avatar
    })


def mostrar_historial():
    """Muestra el historial de mensajes en el chat."""
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"], avatar=mensaje["avatar"]):
            st.markdown(mensaje["content"])


def crear_cliente_groq():
    """Crea y retorna un cliente de Groq."""
    try:
        clave_secreta = st.secrets["CLAVE_API"]
        return Groq(api_key=clave_secreta)
    except KeyError:
        st.error("⚠️ No se encontró la clave API. Configúrala en `st.secrets`.")
        return None


def configurar_modelo(cliente, modelo, mensaje_usuario):
    """Configura y ejecuta el modelo de IA con un mensaje de entrada."""
    try:
        return cliente.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": mensaje_usuario}],
            stream=True
        )
    except Exception as e:
        st.error(f"⚠️ Error al configurar el modelo: {e}")
        return None


def generar_respuestas(chat_completo):
    """Genera respuestas de manera incremental desde el modelo."""
    respuesta_completa = ""
    try:
        for fragmento in chat_completo:
            if fragmento.choices[0].delta.content:
                texto_fragmento = str(fragmento.choices[0].delta.content)
                respuesta_completa += texto_fragmento
                yield texto_fragmento
    except Exception as e:
        st.error(f"⚠️ Error al generar la respuesta: {e}")
    return respuesta_completa




def configurar_pagina():
    """Configura la interfaz lateral para la selección de modelo."""
    st.sidebar.title("Configuración del Chat")
    modelo_seleccionado = st.sidebar.selectbox("Selecciona un modelo", MODELOS, index=0)
    return modelo_seleccionado


def area_chat():
    """Área principal donde se muestra el chat."""
    st.subheader("Chat de IA")
    contenedor_chat = st.container()
    with contenedor_chat:
        mostrar_historial()



def main():
    inicializar_estado()

    modelo = configurar_pagina()

    cliente = crear_cliente_groq()
    if not cliente:
        return  

    area_chat()

    mensaje_usuario = st.chat_input("Escribe tu mensaje aquí...")
    if mensaje_usuario:

        actualizar_historial("user", mensaje_usuario, "😆")

        chat_completo = configurar_modelo(cliente, modelo, mensaje_usuario)
        if chat_completo:
            with st.chat_message("assistant", avatar="🤖"):
                respuesta_generada = st.empty() 
                respuesta_completa = ""
                for fragmento in generar_respuestas(chat_completo):
                    respuesta_completa += fragmento
                    respuesta_generada.markdown(respuesta_completa) 

                actualizar_historial("assistant", respuesta_completa, "🤖")
            st.rerun() 


if __name__ == "__main__":
    main()
