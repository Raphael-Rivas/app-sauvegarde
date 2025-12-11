import socket
import threading
from decouple import config

HOST = config("HOST")
PORT = int(config("PORT"))

class SocketClient:

    def __init__(self, socket):
        self.socket = socket

    def send(self, message):
        self.socket.send(message.encode())

    def recv(self):
        return self.socket.recv(1024).decode()

    def recv_file(self, name):
        size = self.recv()
        file = open(name, "wb")

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


    """
    def restore(self):


    def settings(self):

    """

    def close(self):
        self.socket.close()


def handle_client(s_client):
    s_client.send("Connexion réussie")
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
socket_ecoute.bind(('', PORT))
socket_ecoute.listen()

threads = []

print("Début de l'écoute")

while True:
    try:
        socket_client, adresse_client = socket_ecoute.accept()
        print("Connexion réussie")
        client_thread = threading.Thread(target=handle_client, args=(SocketClient(socket_client),))
        client_thread.start()

        threads.append(client_thread)
    finally:
        socket_ecoute.close()
        for t in threads:
            t.join()