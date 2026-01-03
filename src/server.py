import socket
import threading
from decouple import config
from pathlib import Path

HOST = config("HOST")
PORT = int(config("PORT"))
SERVER_PATH = config("SERVER_PATH")

class SocketClient:

    def __init__(self, socket):
        self.socket = socket
        self.path = ""

    def send(self, message):
        self.socket.send(message.encode())

    def recv(self):
        return self.socket.recv(1024).decode()

    def recv_file(self, name):
        size = self.recv()
        name = self.path + name
        output_file = Path(name)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open('wb') as file:
            file_bytes = b""
            done = False
            while not done:
                data = self.socket.recv(1024)
                if file_bytes[-5:] == b"<END>":
                    done = True
                else:
                    file_bytes += data

            file.write(file_bytes)

        return file

    def save(self):
        name = self.recv()
        while (name != "stop") :
            file = self.recv_file(name)
            file.close()
            name = self.recv()

    def log(self):
        name = self.recv()
        password = self.recv()
        path = SERVER_PATH  + name
        if Path(path).is_dir():
            self.path = path
            return "true"
        return "false"

    def sign(self):
        name = self.recv()
        password = self.recv()
        path = SERVER_PATH  + name
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
        self.socket.close()


def handle_client(s_client):
    s_client.send("Connexion réussie")
    res_con = "false"
    while res_con == "false":
        data = s_client.recv()
        if data == "sign":
            res_con = s_client.sign()
        elif data == "log":
            res_con = s_client.log()
        s_client.send(res_con)

    data = s_client.recv()
    while data != "exit":
        print("Message reçu : " + data)
        match data:
            case "save":
                s_client.save()
            case "restore":
                s_client.restore()
            case "settings":
                s_client.settings()
        data = s_client.recv()
    s_client.close()

socket_ecoute = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket_ecoute.bind(('', PORT))
socket_ecoute.listen()

threads = []

print("Début de l'écoute")

try:
    while True:
        socket_client, adresse_client = socket_ecoute.accept()
        print("Connexion réussie")
        client_thread = threading.Thread(target=handle_client, args=(SocketClient(socket_client),))
        client_thread.start()
        threads.append(client_thread)
finally:
    socket_ecoute.close()
    for t in threads:
        t.join()