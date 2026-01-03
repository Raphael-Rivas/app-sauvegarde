#!/usr/bin/env python3

import socket
from decouple import config
from tkinter import filedialog
import os
import pathlib
import time
import sys


HOST = config("HOST")
PORT = int(config("PORT"))


def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Impossible de se connecter au serveur")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        sys.exit(1)

    try:
        print(client.recv(1024).decode('utf-8'))
        clientConnection(client)
        
        while True:
            sendMsg(client)
    except (ConnectionResetError, BrokenPipeError):
        print("Connexion perdue avec le serveur")
    except KeyboardInterrupt:
        print("Déconnexion...")
    finally:
        try:
            client.send("exit".encode())
        except:
            pass
        client.close()
        print("Client fermé")
        sys.exit(0)


def clientConnection(client):
    connectionMethode = input("Log in / Sign up (log/sign): ")
    while connectionMethode != "log" and connectionMethode != "sign":
        connectionMethode = input("Log in / Sign up (log/sign): ")
    match connectionMethode:
        case "log":
            client.send("log".encode())
            signInConnection(client)
        case "sign":
            client.send("sign".encode())
            signUpConnection(client)
    print("User authenticated")


def signUpConnection(client):
    user = input("Enter username: ")
    passwd = input("Enter password: ")
    passwdConfirm = input("Comfirm password: ")
    while passwd != passwdConfirm:
        passwd = input("Enter password: ")
        passwdConfirm = input("Comfirm password: ")
    client.send(user.encode())
    time.sleep(0.01)
    client.send(passwd.encode())
    result = client.recv(1024).decode('utf-8')
    if result != "true":
        print("Sign up impossible")
        clientConnection(client)


def signInConnection(client):
    user = input("Enter username: ")
    passwd = input("Enter password: ")
    client.send(user.encode())
    time.sleep(0.01)
    client.send(passwd.encode())
    result = client.recv(1024).decode('utf-8')
    if result != "true":
        print("Incorrect username or password")
        clientConnection(client)


def sendMsg(client):
    option = input("Choose between (save/restore/settings/exit): ")
    while option != "save" and option != "restore" and option != "settings" and option != "exit":
        option = input("Choose between (save/restore/settings/exit): ")
    match option:
        case "save":
            save(client)
        case "restore":
            restore()
        case "settings":
            setSettings()
        case "exit":
            raise KeyboardInterrupt  # Will be caught in main() for clean exit


def save(client):
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


def restore():
    path = input()


def setSettings():
    suffix = input()


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