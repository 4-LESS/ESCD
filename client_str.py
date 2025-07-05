import socket
import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

# Inicialización de estados
if "conectado" not in st.session_state:
    st.session_state.conectado = False
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "socket" not in st.session_state:
    st.session_state.socket = None
if "alias" not in st.session_state:
    st.session_state.alias = ""

st_autorefresh(interval=500, key="autorefresh")

st.title("💬 Chat Distribuido")

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
            st.session_state.socket = conectar()
            st.session_state.conectado = True
else:
    st.success(f"Conectado como: {st.session_state.alias}")
    recibir()

    st.subheader("Chat")

    for msg in st.session_state.mensajes[-30:]:
        if msg.startswith("[") and "]" in msg:
            hora_raw, resto = msg.split("]", 1)
            resto = resto.strip()
            hora_str = hora_raw.strip("[").split(" ")[1][:5]
            if ": " in resto:
                autor, contenido = resto.split(": ", 1)
                autor = autor.strip()
                contenido = contenido.strip()
                es_usuario = autor == st.session_state.alias

                align = "right" if es_usuario else "left"
                bubble_color = "rgba(255,255,255,0.1)" if es_usuario else "rgba(255,255,255,0.05)"
                text_color = "inherit"

                # Nombre fuera de la burbuja para todos
                nombre_html = f"<div style='font-weight:bold; margin-bottom: 2px; text-align: {align};'>{autor}</div>"

                st.markdown(
                    f"""
                    <div style='margin-bottom: 8px; text-align: {align};'>
                        {nombre_html}
                        <div style='
                            display: inline-block;
                            background-color: {bubble_color};
                            color: {text_color};
                            border-radius: 10px;
                            padding: 8px 12px;
                            max-width: 80%;
                            box-shadow: 0 0 3px rgba(0,0,0,0.05);
                            word-wrap: break-word;
                        '>
                            {contenido}
                            <div style='font-size: 10px; color: gray; text-align: right; margin-top: 4px;'>{hora_str}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(f"📨 {msg}")
        else:
            st.markdown(f"📨 {msg}")

    with st.form("form_chat", clear_on_submit=True):
        col1, col2 = st.columns([1, 5])
        with col1:
            enviado = st.form_submit_button("📤")
        with col2:
            texto = st.text_input("Mensaje", key="input_msg", label_visibility="collapsed")

        if enviado and texto.strip():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            mensaje = f"[{timestamp}] {st.session_state.alias}: {texto}"
            try:
                st.session_state.socket.send(mensaje.encode())
                st.session_state.mensajes.append(mensaje)  # Guardar solo texto plano
            except Exception as e:
                st.error(f"❌ Error al enviar mensaje: {e}")


