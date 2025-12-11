#!/usr/bin/env python3

import socket
from decouple import config
from tkinter import filedialog
import os
import pathlib

HOST = config("HOST")
PORT = int(config("PORT"))

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    print(client.recv(1024).decode('utf-8'))

    while True:
        sendMsg(client)


def sendMsg(client):
    option = input("Choose between (save/restore/settings/exit): ")
    while option != "save" and option != "restore" and option != "settings" and option != "exit":
        option = input("Choose between (save/restore/settings/exit): ")
    match option:
        case "save":
            client.send("save".encode())
            
            saveOption = input("Choose between save (directory/files): ")
            while saveOption != "directory" and saveOption != "files":
                saveOption = input("Choose between save (directory/files): ")
            match saveOption:
                case "directory":
                    directory = filedialog.askdirectory()
                    if directory != "":
                        files = [f for f in pathlib.Path().iterdir() if f.is_file()] #files = [f for f in pathlib.Path().glob("/sys/*.log")]
                        for f in files:
                            sendFile(client, f)
                case "files":
                    files = filedialog.askopenfilenames()
                    for f in files:
                        sendFile(client, f)
            client.send("stop".encode())
                    
        case "restore":
            path = input()
        case "settings":
            suffix = input()
        case "exit":
            client.send("exit".encode())
            client.close()
            exit()

def sendFile(client, f):
    file = open(str(f), "rb")
    file_size = os.path.getsize(str(f))
    client.send(str(f).encode())
    client.send(str(file_size).encode())
    data = file.read()
    client.sendall(data)
    client.send("end".encode())
    file.close()


if __name__ == "__main__":
    main()