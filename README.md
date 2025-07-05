# Chat Streamlit / Ngrok

Este proyecto implementa un sistema de chat simple utilizando sockets TCP y Streamlit como interfaz web. Los mensajes se transmiten a través de un servidor central accesible desde internet mediante Ngrok.

## Requisitos

Antes de ejecutar el programa, asegúrate de tener instalado lo siguiente:

- Python 3.8 o superior
- Streamlit
- Ngrok (con cuenta gratuita verificada)

Instalación de dependencias:  
```bash
pip install streamlit
```
## Configuración de Ngrok:

- Crea una cuenta gratuita en https://ngrok.com
- Descarga e instala Ngrok según tu sistema operativo.
- Autentica tu cuenta ejecutando:
```bash
ngrok config add-authtoken TU_TOKEN_AQUI
```
##  Ejecución del sistema

Para ejecutar el sistema completo, simplemente corre:
```bash
python launcher.py
```

Este script realizará lo siguiente:

- Iniciará el servidor TCP
- Abrirá Ngrok para publicar el frontend de Streamlit
- Ejecutará el cliente web
- Mostrará la URL pública generada por Ngrok
- Generará un código QR con acceso directo al chat
