#!/usr/bin/env python3

import socket
from decouple import config
from tkinter import filedialog
import os
import pathlib
import time
import sys
import hashlib
from pathlib import Path


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
        print(client.recv(1024).decode())
        clientConnection(client)
        while True:
            handleOptions(client)
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


def signUpConnection(client):
    user = input("Enter username: ")
    passwd = input("Enter password: ")
    passwdConfirm = input("Comfirm password: ")
    while passwd != passwdConfirm:
        passwd = input("Enter password: ")
        passwdConfirm = input("Comfirm password: ")
    client.send(user.encode())
    time.sleep(0.1)
    hash_pwd = hashlib.sha256(passwd.encode()).hexdigest()
    client.send(hash_pwd.encode())
    result = client.recv(1024).decode()
    if result != "true":
        print("Sign up impossible")
        clientConnection(client)
    else:
        print("User authenticated")


def signInConnection(client):
    user = input("Enter username: ")
    passwd = input("Enter password: ")
    client.send(user.encode())
    time.sleep(0.1)
    hash_pwd = hashlib.sha256(passwd.encode()).hexdigest()
    client.send(hash_pwd.encode())
    result = client.recv(1024).decode()
    if result != "true":
        print("Incorrect username or password")
        clientConnection(client)
    else:
        print("User authenticated")


def handleOptions(client):
    option = input("Choose between (save/restore/settings/exit): ")
    while option != "save" and option != "restore" and option != "settings" and option != "exit":
        option = input("Choose between (save/restore/settings/exit): ")
    match option:
        case "save":
            save(client)
        case "restore":
            restore(client)
        case "settings":
            # Bonus : setSettings(client)
            print("Settings option not implemented yet")
        case "exit":
            raise KeyboardInterrupt


def save(client): #TODO: implement directory  in directory backup
    client.send("save".encode())
    saveOption = input("Choose between save (directory/files): ")
    while saveOption != "directory" and saveOption != "files":
        saveOption = input("Choose between save (directory/files): ")
    match saveOption:
        case "directory":
            directory = filedialog.askdirectory(title="Select Directory to Save")
            if directory != "":
                files = [f for f in pathlib.Path(directory).iterdir() if f.is_file()]
                for f in files:
                    sendFile(client, f)
        case "files":
            files = filedialog.askopenfilenames(title="Select Files to Save")
            for f in files:
                sendFile(client, f)
    client.send("stop".encode())
    

def sendFile(client, f):
    file = open(str(f), "rb")
    file_size = os.path.getsize(str(f))
    client.send(str(f).encode())
    time.sleep(1)
    size_str = str(file_size).zfill(10) # Taille fixe de 10 octets, complétée par des zéros
    client.send(size_str.encode())
    data = file.read()
    client.sendall(data)
    client.send("end".encode())
    file.close()


def restore(client):
    client.send("restore".encode())
    tree = client.recv(1024).decode()
    print("Available files/directories:\n" + tree) #TODO: pretty print for the tree ?
    restoreOption = input("Choose between restore (all/file/directory): ")
    while restoreOption != "all" and restoreOption != "file" and restoreOption != "directory":
        restoreOption = input("Choose between restore (all/file/directory): ")
    match restoreOption:
        
        case "all":
            client.send("all".encode())
            path = filedialog.askdirectory(title="Select Directory where to Restore the files")
            while path == "":
                path = filedialog.askdirectory(title="Select Directory where to Restore the files")
            restore_file(client, path)

        case "file":
            client.send("file".encode())
            filenames = []
            name = input("Enter the filename to restore (stop to finish): ") #TODO: handle non-existing file in the server tree
            while name != "stop":
                filenames.append(name)
                name = input("Enter the filename to restore (stop to finish): ")
            path = filedialog.askdirectory(title="Select Directory where to Restore the files")
            while path == "":
                path = filedialog.askdirectory(title="Select Directory where to Restore the files")
            for filename in filenames:
                client.send(filename.encode())
            client.send("stop".encode())
            restore_file(client, path)
            
        case "directory":
            client.send("directory".encode())
            directory = input("Enter the directory to restore: ") #TODO: handle non-existing directory in the server tree
            client.send(directory.encode())
            path = filedialog.askdirectory(title="Select Directory where to Restore the files")
            while path == "":
                path = filedialog.askdirectory(title="Select Directory where to Restore the files")
            restore_file(client, path)
            
    client.send("stop".encode())
    
    
def restore_file(client, path):
    name = client.recv(1024).decode()
    while (name != "stop") :
        result = recv_file(client, path, name)
        if result != "" :
            name = result
        else:
            name = client.recv(1024).decode()
    
    
def recv_file(client, path, name):
        size = int(client.recv(10).decode())
        name = path + "/" + name
        output_file = Path(name)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open('wb') as file:
            file_bytes = b""
            done = False
            while not done:
                data = client.recv(1024)
                if not data:
                    break
                file_bytes += data

                if len(file_bytes) >= size + 3 and file_bytes[size:size + 3] == b"end":
                    done = True

            file.write(file_bytes[ : size])

        file.close()
        return file_bytes[size + 3 : ].decode(errors='ignore')


if __name__ == "__main__":
    main()