import subprocess
import time
import requests
import os
import qrcode
import qrcode.console_scripts
from io import BytesIO
import webbrowser


NGROK_PATH = "ngrok"  
PUERTO_STREAMLIT = 8501

def iniciar_servidor():
    print("🟢 Iniciando servidor TCP...")
    return subprocess.Popen(["python", "server.py"])

def iniciar_cliente():
    print("🟢 Iniciando cliente Streamlit...")
    subprocess.Popen(["streamlit", "run", "client_str.py", "--server.headless=true", "--browser.gatherUsageStats=false"], stdout=subprocess.DEVNULL)

def iniciar_ngrok(puerto):
    print("🛜 Iniciando ngrok...")
    return subprocess.Popen([NGROK_PATH, "http", str(puerto)], stdout=subprocess.DEVNULL)

def obtener_url_ngrok():
    print("⏳ Esperando a que ngrok genere la URL pública...")
    time.sleep(3)
    try:
        resp = requests.get("http://127.0.0.1:4040/api/tunnels")
        resp.raise_for_status()
        tuneles = resp.json()["tunnels"]
        for t in tuneles:
            if t["proto"] == "https":
                return t["public_url"]
    except Exception as e:
        print("❌ Error obteniendo URL de ngrok:", e)
    return None

def mostrar_qr(link):
    qr = qrcode.QRCode()
    qr.add_data(link)
    qr.make(fit=True)

    print("\n📱 Escanea este código QR para abrir el chat desde tu celular o navegador externo:\n")
    qr.print_ascii(invert=True)

    # Opcional: mostrar imagen del QR con visor predeterminado
    img = qr.make_image(fill="black", back_color="white")
    img_path = "qr_chat.png"
    img.save(img_path)


def main():
    servidor = iniciar_servidor()
    time.sleep(1)

    cliente = iniciar_cliente()
    time.sleep(1)

    ngrok = iniciar_ngrok(PUERTO_STREAMLIT)
    time.sleep(3)

    url_publica = obtener_url_ngrok()
    if url_publica:
        print(f"\n✅ Tu cliente Streamlit está disponible en:\n👉 {url_publica}")
        mostrar_qr(url_publica)
        webbrowser.open(url_publica)
    else:
        print("⚠️ No se pudo obtener la URL de ngrok.")

    print("\n⏹️ Pulsa Ctrl+C para cerrar todo.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Cerrando procesos...")
        servidor.terminate()
        cliente.terminate()
        ngrok.terminate()
        print("✅ Todo cerrado.")

if __name__ == "__main__":
    main()
