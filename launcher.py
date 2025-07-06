# launcher.py

import subprocess
import time
import qrcode
import webbrowser
import os
import shutil
import re
import requests

PUERTO_STREAMLIT = 8501

def iniciar_servidor_broker():
    print("🟢 Iniciando servidor broker (TCP)...")
    return subprocess.Popen(["python", "server.py"])

def iniciar_cliente_streamlit():
    print("🟢 Iniciando cliente Streamlit...")
    return subprocess.Popen(
        ["streamlit", "run", "client_str.py", "--server.headless=true", "--browser.gatherUsageStats=false"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

def obtener_comando_cloudflared():
    path = shutil.which("cloudflared")
    if not path:
        print("❌ cloudflared no está instalado.")
        exit(1)
    return path

def iniciar_cloudflare_tunnel(puerto=8501):
    print("🚀 Iniciando Cloudflare Tunnel...")
    cf_cmd = obtener_comando_cloudflared()
    proceso = subprocess.Popen(
        [cf_cmd, "tunnel", "--url", f"http://localhost:{puerto}"],
        stderr=subprocess.PIPE, text=True, encoding='utf-8'
    )
    for linea in iter(proceso.stderr.readline, ''):
        if ".trycloudflare.com" in linea:
            match = re.search(r'(https?://\S+\.trycloudflare\.com)', linea)
            if match:
                url = match.group(0)
                print(f"✅ URL pública generada: {url}")
                return proceso, url
    print("❌ No se pudo obtener la URL de Cloudflare Tunnel.")
    proceso.terminate()
    return None, None

def esperar_disponibilidad(url, timeout=30):
    print(f"⏳ Esperando que {url} esté disponible...")
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                print("✅ El sitio está disponible.")
                return True
        except:
            pass
        time.sleep(1)
    print("⚠️ Tiempo de espera agotado. El sitio aún no responde.")
    return False

def mostrar_qr(link):
    qr = qrcode.QRCode()
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save("qr_chat.png")
    print("🖨️  QR generado en 'qr_chat.png'.")

def main():
    broker = iniciar_servidor_broker()
    time.sleep(1)
    
    cliente_ui = iniciar_cliente_streamlit()
    time.sleep(3)
    
    cf_proceso, url_publica = iniciar_cloudflare_tunnel(PUERTO_STREAMLIT)
    
    if url_publica and esperar_disponibilidad(url_publica):
        print(f"\n🌍 Tu cliente Streamlit está disponible en:\n👉 {url_publica}")
        mostrar_qr(url_publica)
        webbrowser.open(url_publica)
    else:
        print("❌ No fue posible acceder al túnel de Cloudflare.")
        broker.terminate()
        cliente_ui.terminate()
        if cf_proceso: cf_proceso.terminate()
        exit(1)

    print("\n⏹️  Pulsa Ctrl+C para cerrar todo.")
    try:
        cf_proceso.wait()
    except KeyboardInterrupt:
        print("\n⏹️  Cerrando procesos...")
    finally:
        if broker.poll() is None: broker.terminate()
        if cliente_ui.poll() is None: cliente_ui.terminate()
        if cf_proceso.poll() is None: cf_proceso.terminate()
        print("✅ Todo cerrado.")

if __name__ == "__main__":
    main()

