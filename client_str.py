import socket
import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from PIL import Image
import os
import streamlit.components.v1 as components

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
    if msg.startswith("[") and "]" in msg:
        hora_raw, resto = msg.split("]", 1)
        hora_str = hora_raw.strip("[").split(" ")[1][:5]
        if ": " in resto:
            autor, contenido = resto.split(": ", 1)
            return autor.strip(), contenido.strip(), hora_str
    return None, None, None

def render_mensajes(mensajes):
    autor_anterior = None
    mensajes_grupo = []
    hora_ultimo = None
    es_usuario = False

    def mostrar_grupo(autor, grupo, es_user, hora):
        tipo = "user" if es_user else "assistant"
        if es_user:
            col1, col2 = st.columns([1, 4])
            with col2:
                with st.chat_message(tipo):
                    st.markdown(f"**{autor}**")
                    for m in grupo:
                        st.markdown(m)
                    st.caption(hora)
        else:
            col1, col2 = st.columns([4, 1])
            with col1:
                with st.chat_message(tipo):
                    st.markdown(f"**{autor}**")
                    for m in grupo:
                        st.markdown(m)
                    st.caption(hora)

    for msg in mensajes:
        autor, contenido, hora_str = extraer_datos_mensaje(msg)
        if autor and contenido and hora_str:
            es_user_actual = autor == st.session_state.alias

            if autor != autor_anterior:
                if autor_anterior is not None:
                    mostrar_grupo(autor_anterior, mensajes_grupo, es_usuario, hora_ultimo)
                autor_anterior = autor
                mensajes_grupo = [contenido]
                es_usuario = es_user_actual
                hora_ultimo = hora_str
            else:
                mensajes_grupo.append(contenido)
                hora_ultimo = hora_str
        else:
            if autor_anterior:
                mostrar_grupo(autor_anterior, mensajes_grupo, es_usuario, hora_ultimo)
                autor_anterior = None
                mensajes_grupo = []
            st.markdown(f"📨 {msg}")

    if autor_anterior and mensajes_grupo:
        mostrar_grupo(autor_anterior, mensajes_grupo, es_usuario, hora_ultimo)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("# :material/group: Usuarios Conectados")

    if st.session_state.conectado:
        recibir()

    if st.session_state.usuarios:
        for user in st.session_state.usuarios:
            cols = st.columns([1, 2, 1])
            with cols[0]:
                if user == st.session_state.alias:
                    st.subheader(f":green[:material/priority:] {user}")
                else:
                    st.subheader(f":blue[:material/for_you:] {user}")
        st.markdown("---")
    else:
        st.header(f":orange[:material/sentiment_dissatisfied:] No estás conectado al servidor")

    with st.expander(":material/qr_code_scanner: Escanea el QR"):
        qr_path = "qr_chat.png"
        if os.path.exists(qr_path):
            st.image(qr_path)
        else:
            st.write("QR no disponible")

    if st.button("Salir", icon=":material/logout:", type="primary", use_container_width=True):
        if st.session_state.socket:
            try:
                st.session_state.socket.close()
            except:
                pass
        st.session_state.conectado = False
        st.session_state.socket = None
        st.session_state.mensajes = []
        st.session_state.usuarios = []
        st.rerun()

# === UI PRINCIPAL ===
st.title(":material/desktop_cloud_stack: CHAT ECSD")

if not st.session_state.conectado:
    alias = st.text_input("Ingresa tu nombre o apodo:")
    if st.button(":green[Conectarse]", icon=":material/logout:", type="tertiary", use_container_width=True):
        if alias.strip() == "":
            st.warning("Debes ingresar un nombre.")
        else:
            st.session_state.alias = alias.strip()
            st.session_state.socket = conectar()
            st.session_state.socket.send(f"ALIAS:{st.session_state.alias}".encode())
            st.session_state.conectado = True
else:
    render_mensajes(st.session_state.mensajes[-30:])

    with st.container():
        mensaje = st.chat_input("Escribe tu mensaje...")
        if mensaje:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            mensaje_formateado = f"[{timestamp}] {st.session_state.alias}: {mensaje}"
            try:
                st.session_state.socket.send(mensaje_formateado.encode())
                st.session_state.mensajes.append(mensaje_formateado)
                st.rerun()
            except Exception as e:
                st.error(f"Error al enviar mensaje: {e}")






