import socket
import threading

HOST = '0.0.0.0'
PORT = 5000
clientes = []
aliases = {}
lock = threading.Lock()

def manejar_cliente(conn, addr):
    print(f"[+] Cliente conectado desde {addr}")
    alias = ""
    try:
        while True:
            mensaje = conn.recv(1024)
            if not mensaje:
                break
            texto = mensaje.decode()
            if texto.startswith("ALIAS:"):
                alias = texto.split(":", 1)[1].strip()
                with lock:
                    aliases[conn] = alias
                enviar_lista_usuarios()
                continue
            print(f"[📨] {addr}: {texto}")
            reenviar(texto.encode(), conn)
    except Exception as e:
        print(f"⚠️ Error con {addr}: {e}")
    finally:
        with lock:
            if conn in clientes:
                clientes.remove(conn)
            if conn in aliases:
                del aliases[conn]
        conn.close()
        print(f"[-] Cliente desconectado: {addr}")
        enviar_lista_usuarios()

def reenviar(mensaje, origen):
    with lock:
        for cliente in clientes:
            if cliente != origen:
                try:
                    cliente.send(mensaje)
                except:
                    cliente.close()
                    clientes.remove(cliente)
                    aliases.pop(cliente, None)

def enviar_lista_usuarios():
    with lock:
        lista = list(aliases.values())
        mensaje = f"__USERS__|{','.join(lista)}".encode()
        for cliente in clientes:
            try:
                cliente.send(mensaje)
            except:
                pass

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"🟢 Servidor activo en {HOST}:{PORT}")
    while True:
        conn, addr = servidor.accept()
        with lock:
            clientes.append(conn)
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
        hilo.start()

if __name__ == "__main__":
    iniciar_servidor()

