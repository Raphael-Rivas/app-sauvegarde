#!/usr/bin/env python3

import pathlib
import socket
import threading
import signal
import sys

from decouple import config
from pathlib import Path
import os


HOST = config("HOST")
PORT = int(config("PORT"))
SERVER_PATH = config("SERVER_PATH")

running = True
socket_ecoute = None


class SocketClient:

    def __init__(self, socket):
        self.socket = socket
        self.path = ""

    def send(self, message):
        self.socket.send(message.encode())

    def recv(self):
        return self.socket.recv(1024).decode()

    def recv_file(self, name):
        size = int(self.socket.recv(10).decode())
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
        return file_bytes[size + 3 : ].decode(errors='ignore')

    def sendFile(self, f, name=None):
        file = open(str(f), "rb")
        file_size = os.path.getsize(str(f))
        if name is None:
            name = str(f)
        self.send(name)
        self.recv()
        size_str = str(file_size).zfill(10)
        self.send(size_str)
        data = file.read()
        self.socket.sendall(data)
        self.send("end")
        file.close()
        self.recv()

    def save(self):
        name = self.recv()
        while (name != "stop") :
            result = self.recv_file(name)
            if result != "" :
                name = result
            else:
                name = self.recv()

    def log(self):
        name = self.recv()
        password = self.recv()
        path = SERVER_PATH + name
        if Path(path + "/password.txt").is_file():
            with open(path + "/password.txt", "r") as f:
                hash_pwd = f.read().strip()
                if hash_pwd == password:
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
            Path(path).mkdir(parents=True, exist_ok=True)
            with open(path + "/password.txt", "w") as f:
                f.write(password)
            return "true"

    def restore(self):
        tree = list_files(self.path)
        tree_bytes = tree.encode()
        size_str = str(len(tree_bytes)).zfill(10)
        self.socket.send(size_str.encode())
        self.socket.sendall(tree_bytes)
        data = self.recv()
        match data:
            case "all":
                confirmation = self.recv()
                if confirmation == "cancel":
                    return
                for f in pathlib.Path(self.path).rglob("*"):
                    if f.is_file() and f.name != "password.txt":
                        relative_path = str(f).replace(self.path, "")
                        if relative_path.startswith("/"):
                            relative_path = relative_path[1:]
                        self.sendFile(f, relative_path)
                self.send("stop")
            case "file":
                filename = self.recv()
                if filename == "cancel":
                    return
                while filename != "stop" and filename != "" and filename != "cancel":
                    found = False
                    req_norm = filename.replace("\\", "/").lstrip("/")
                    for f in pathlib.Path(self.path).rglob("*"):
                        if f.is_file() and f.name != "password.txt":
                            rel_norm = f.relative_to(self.path).as_posix()
                            if rel_norm == req_norm:
                                self.sendFile(f, f.name)
                                found = True
                                break
                    if not found:
                        self.send("notfound")
                    filename = self.recv()
            case "directory":
                directory = self.recv()
                if directory and directory != "cancel":
                    dir_path = pathlib.Path(self.path) / directory
                    if dir_path.is_dir():
                        for f in dir_path.rglob("*"):
                            if f.is_file() and f.name != "password.txt":
                                relative_path = str(f).replace(str(dir_path) + "/", "")
                                self.sendFile(f, relative_path)
                self.send("stop")


    def close(self):
        try:
            self.socket.close()
        except:
            pass


def main():
    global socket_ecoute
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    socket_ecoute = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_ecoute.bind(('', PORT))
    socket_ecoute.listen()
    socket_ecoute.settimeout(1.0)

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
        
        
def signal_handler(sig, frame):
    global running, socket_ecoute
    print("\nArrêt du serveur...")
    running = False
    if socket_ecoute:
        try:
            socket_ecoute.close()
        except:
            pass
    sys.exit(0)


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
                    print("Settings requested - not implemented")
            data = s_client.recv()
    except (ConnectionResetError, BrokenPipeError, OSError):
        print("Client déconnecté brusquement")
    except Exception as e:
        print(f"Erreur client: {e}")
    finally:
        s_client.close()
        print("Client fermé")


def list_files(startpath):
    result = ""
    startpath = os.path.normpath(startpath)
    for root, dirs, files in os.walk(startpath):
        rel = os.path.relpath(root, startpath)
        if rel == ".":
            subindent = ' ' * 4 * 0
            for f in files:
                if f != "password.txt":
                    result += f"{subindent}{f}\n"
            continue
        level = rel.count(os.sep)
        indent = ' ' * 4 * level
        result += f"{indent}{os.path.basename(root)}/\n"
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f != "password.txt":
                result += f"{subindent}{f}\n"
    return result

        
if __name__ == "__main__":
    main()