import socket
from decouple import config

HOST = config("HOST")
PORT = int(config("PORT"))

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))

def sendMsg():
    option = input("Choose between (save/restore/settings)")
    while option != "save" or option != "restore" or option != "settings":
        option = input("Choose between (save/restore/settings)")
    match option:
        case "save":
            directory = input("Give the path of the directory you want to save")
        case "restore":
            path = input()
        case "settings":
            suffix = input()
