# Chat Streamlit / Cloudflare Tunnel

Este proyecto implementa un sistema de chat simple utilizando sockets TCP y Streamlit como interfaz web. Los mensajes se transmiten a través de un servidor central accesible desde internet mediante **Cloudflare Tunnel**.

## Requisitos

Antes de ejecutar el programa, asegúrate de tener instalado lo siguiente:

* Python 3.8 o superior
* Streamlit
* Cloudflared

Instalación de dependencias:

```bash
pip install streamlit streamlit-autorefresh qrcode pillow
```

## Instalación de Cloudflared

Puedes instalar Cloudflared usando la herramienta Winget:

```bash
winget install --id Cloudflare.cloudflared
```

Verifica la instalación con:

```bash
cloudflared --version
```

## Ejecución del sistema

Para lanzar todo el sistema, ejecuta:

```bash
python launcher.py
```

Este script realizará lo siguiente:

* Iniciará el servidor de chat (broker TCP)
* Ejecutará la interfaz gráfica de cliente con Streamlit
* Activará un túnel de Cloudflare para hacer público el frontend
* Mostrará la URL generada
* Generará un código QR para facilitar el acceso desde dispositivos móviles


