import socket
from decouple import config

HOST = config("HOST")
PORT = config("PORT")

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))
