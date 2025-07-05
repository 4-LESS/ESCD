import socket
import threading

HOST = '0.0.0.0'  # Acepta conexiones externas
PORT = 5000
clientes = []
lock = threading.Lock()

def manejar_cliente(conn, addr):
    print(f"[+] Cliente conectado desde {addr}")
    try:
        while True:
            mensaje = conn.recv(1024)
            if not mensaje:
                break
            texto = mensaje.decode()
            print(f"📩 Recibido de {addr}: {texto}")
            reenviar(mensaje, conn)
    except Exception as e:
        print(f"⚠️ Error con {addr}: {e}")
    finally:
        with lock:
            if conn in clientes:
                clientes.remove(conn)
        conn.close()
        print(f"[-] Cliente desconectado: {addr}")

def reenviar(mensaje, origen):
    with lock:
        for cliente in clientes[:]:  # Copia de la lista para evitar errores
            if cliente != origen:
                try:
                    cliente.send(mensaje)
                except Exception as e:
                    print(f"❌ Error al reenviar a un cliente: {e}")
                    cliente.close()
                    clientes.remove(cliente)

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"🟢 Servidor TCP activo en {HOST}:{PORT}")
    while True:
        conn, addr = servidor.accept()
        with lock:
            clientes.append(conn)
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
        hilo.start()

if __name__ == "__main__":
    iniciar_servidor()
