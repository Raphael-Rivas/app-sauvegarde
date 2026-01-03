import socket
import threading
import signal
import sys
from decouple import config
from pathlib import Path

HOST = config("HOST")
PORT = int(config("PORT"))
SERVER_PATH = config("SERVER_PATH")

running = True


class SocketClient:

    def __init__(self, socket):
        self.socket = socket
        self.path = ""

    def send(self, message):
        self.socket.send(message.encode())

    def recv(self):
        return self.socket.recv(1024).decode()

    def recv_file(self, name):
        size = int(self.recv())
        name = self.path + name
        output_file = Path(name)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open('wb') as file:
            file_bytes = b""
            done = False
            while not done:
                data = self.socket.recv(1024)
                if not data:
                    break
                file_bytes += data

                if len(file_bytes) >= size + 3 and file_bytes[size:size + 3] == b"end":
                    done = True

            file.write(file_bytes[ : size])

        file.close()
        return file_bytes[size + 3 : ].decode()

    def save(self):
        name = self.recv()
        while (name != "stop") :
            name = self.recv_file(name)
            print("Name : " + name)
            if name != "stop" :
                name = self.recv()

    def log(self):
        name = self.recv()
        password = self.recv()
        path = SERVER_PATH + name
        if Path(path).is_dir():
            self.path = path
            return "true"
        return "false"

    def sign(self):
        name = self.recv()
        password = self.recv()
        path = SERVER_PATH + name
        if Path(path).is_dir():
            return "false"
        else:
            self.path = path
            return "true"

    """
    def restore(self):


    def settings(self):

    """

    def close(self):
        try:
            self.socket.close()
        except:
            pass


def handle_client(s_client):
    try:
        s_client.send("Connexion réussie")
        res_con = "false"
        while res_con == "false" and running:
            data = s_client.recv()
            if not data:
                return
            if data == "sign":
                res_con = s_client.sign()
            elif data == "log":
                res_con = s_client.log()
            s_client.send(res_con)

        data = s_client.recv()
        while data != "exit" and data and running:
            print("Message reçu : " + data)
            match data:
                case "save":
                    s_client.save()
                case "restore":
                    s_client.restore()
                case "settings":
                    s_client.settings()
            data = s_client.recv()
    except (ConnectionResetError, BrokenPipeError, OSError):
        print("Client déconnecté brusquement")
    except Exception as e:
        print(f"Erreur client: {e}")
    finally:
        s_client.close()
        print("Client fermé")


def signal_handler(sig, frame):
    global running
    print("Arrêt du serveur...")
    running = False
    socket_ecoute.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

socket_ecoute = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket_ecoute.bind(('', PORT))
socket_ecoute.listen()
socket_ecoute.settimeout(1.0)  # Timeout pour permettre l'arrêt propre

threads = []

print("Début de l'écoute")

try:
    while running:
        try:
            socket_client, adresse_client = socket_ecoute.accept()
            print("Connexion réussie")
            client_thread = threading.Thread(target=handle_client, args=(SocketClient(socket_client),))
            client_thread.start()
            threads.append(client_thread)
        except socket.timeout:
            continue
        except OSError:
            break
finally:
    socket_ecoute.close()
    for t in threads:
        t.join(timeout=2.0)
    print("Serveur fermé")