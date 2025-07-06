import socket
import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# === CONFIG ===
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

# === ESTADOS DE SESIÓN ===
estados = ["conectado", "mensajes", "socket", "alias", "usuarios"]
for estado in estados:
    if estado not in st.session_state:
        if estado in ["mensajes", "usuarios"]:
            st.session_state[estado] = []
        elif estado == "conectado":
            st.session_state[estado] = False
        else:
            st.session_state[estado] = None

# === AUTOREFRESH ===
st_autorefresh(interval=500, key="autorefresh")

# === FUNCIONES AUXILIARES ===
def conectar():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_HOST, SERVER_PORT))
        sock.setblocking(False)
        return sock
    except Exception as e:
        st.error(f"Error al conectar con el servidor: {e}")
        st.stop()

def recibir():
    try:
        sock = st.session_state.socket
        while True:
            try:
                msg = sock.recv(1024).decode()
                if msg.startswith("__USERS__|"):
                    st.session_state.usuarios = msg.split("|", 1)[1].split(",")
                elif msg and msg not in st.session_state.mensajes:
                    st.session_state.mensajes.append(msg)
            except BlockingIOError:
                break
    except:
        pass

def extraer_datos_mensaje(msg):
    """Extrae autor, contenido y hora de un mensaje"""
    if msg.startswith("[") and "]" in msg:
        hora_raw, resto = msg.split("]", 1)
        hora_str = hora_raw.strip("[").split(" ")[1][:5]
        if ": " in resto:
            autor, contenido = resto.split(": ", 1)
            autor = autor.strip()
            contenido = contenido.strip()
            return autor, contenido, hora_str
    return None, None, None

def render_mensajes(mensajes):
    """Renderiza todos los mensajes usando st.chat_message(), agrupando por autor consecutivo"""
    autor_anterior = None
    
    for msg in mensajes:
        autor, contenido, hora_str = extraer_datos_mensaje(msg)
        
        if autor and contenido and hora_str:
            es_usuario = autor == st.session_state.alias
            mostrar_autor = autor != autor_anterior
            
            tipo = "user" if es_usuario else "assistant"
            with st.chat_message(tipo):
                if mostrar_autor:
                    st.markdown(f"**{autor}**")
                st.markdown(contenido)
                st.caption(hora_str)
            
            autor_anterior = autor
        else:
            # Mensaje del sistema o formato no reconocido
            st.markdown(f"📨 {msg}")
            autor_anterior = None  # Resetear para mensajes del sistema

# === SIDEBAR ===
with st.sidebar:
    st.markdown("# :material/group: Usuarios Conectados")

    if st.session_state.usuarios:
        for user in st.session_state.usuarios:
            cols = st.columns([1, 2, 1])
            with cols[0]:
                if user == st.session_state.alias:
                    st.header(f":green[:material/priority:] {user}")
                else:
                    st.header(f":blue[:material/for_you:] {user}")
        st.markdown("---")
    else:
        st.header(f":orange[:material/sentiment_dissatisfied:] No estas conectado al servidor")

    if st.button("Salir", icon = ":material/logout:", type="primary", use_container_width=True):
        if st.session_state.socket:
            try:
                st.session_state.socket.close()
            except:
                pass
        st.session_state.conectado = False
        st.session_state.socket = None
        st.session_state.mensajes = []
        st.session_state.usuarios = []
        st.experimental_rerun()

# === UI PRINCIPAL ===
st.title(":material/desktop_cloud_stack: CHAT ECSD")

if not st.session_state.conectado:
    alias = st.text_input("Ingresa tu nombre o apodo:")
    if st.button(":green[Conectarse]", icon = ":material/logout:", type="tertiary", use_container_width=True):
        if alias.strip() == "":
            st.warning("Debes ingresar un nombre.")
        else:
            st.session_state.alias = alias.strip()
            st.session_state.socket = conectar()
            st.session_state.socket.send(f"ALIAS:{st.session_state.alias}".encode())
            st.session_state.conectado = True
else:
    recibir()
    render_mensajes(st.session_state.mensajes[-30:])

    mensaje = st.chat_input("Escribe tu mensaje...")

    if mensaje:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mensaje_formateado = f"[{timestamp}] {st.session_state.alias}: {mensaje}"
        try:
            st.session_state.socket.send(mensaje_formateado.encode())
            st.session_state.mensajes.append(mensaje_formateado)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al enviar mensaje: {e}")






