import socket
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# === CONFIGURACIÓN ===
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

# === INICIALIZACIÓN DE ESTADOS ===
if "conectado" not in st.session_state:
    st.session_state.conectado = False
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "socket" not in st.session_state:
    st.session_state.socket = None
if "alias" not in st.session_state:
    st.session_state.alias = ""

# === AUTOREFRESH ===
st_autorefresh(interval=500, key="autorefresh")

st.title("💬 Chat Distribuido")

def conectar_a_servidor():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_HOST, SERVER_PORT))
        sock.setblocking(False)
        return sock
    except Exception as e:
        st.error(f"No se pudo conectar al servidor: {e}")
        st.stop()

def recibir_mensajes():
    try:
        sock = st.session_state.socket
        while True:
            try:
                msg = sock.recv(1024).decode()
                if msg and msg not in st.session_state.mensajes:
                    st.session_state.mensajes.append(msg)
            except BlockingIOError:
                break
    except:
        pass

if not st.session_state.conectado:
    alias = st.text_input("Ingresa tu nombre o apodo:")
    if st.button("Conectarse"):
        if alias.strip() == "":
            st.warning("Debes ingresar un nombre.")
        else:
            st.session_state.alias = alias.strip()
            st.session_state.socket = conectar_a_servidor()
            st.session_state.conectado = True
else:
    st.success(f"Conectado como: {st.session_state.alias}")

    recibir_mensajes()

    st.subheader("Chat en tiempo real")

    for msg in st.session_state.mensajes[-30:]:
        st.markdown(f"📨 {msg}")

    # NO tocar st.session_state.input_msg aquí
    mensaje_usuario = st.text_input("Escribe un mensaje:", key="input_msg")

    if st.button("Enviar"):
        if mensaje_usuario.strip():
            mensaje = f"{st.session_state.alias}: {mensaje_usuario}"
            try:
                st.session_state.socket.send(mensaje.encode())
                st.session_state.mensajes.append(mensaje)
            except Exception as e:
                st.error(f"❌ Error al enviar mensaje: {e}")


