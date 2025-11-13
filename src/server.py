import socket
import threading
from decouple import config

HOST = config("HOST")
PORT = int(config("PORT"))

def handle_client(s_client):
    s_client.send("Hello")
    data = s_client.recv(1024)
    print(data.decode()[0])
    s_client.close()

socket_ecoute = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_ecoute.bind(('', PORT))
socket_ecoute.listen()

threads = []

print("Début de l'écoute")

while True:
    try:
        socket_client, adresse_client = socket_ecoute.accept()
        client_thread = threading.Thread(target=handle_client, args=(socket_client,))
        client_thread.start()

        threads.append(client_thread)
    finally:
        socket_ecoute.close()
        for t in threads:
            t.join()