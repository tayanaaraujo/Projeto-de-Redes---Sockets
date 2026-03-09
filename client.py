import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


# Thread 1 - receber feed do servidor
def receber_mensagens():
    while True:
        try:
            dados = client.recv(1024).decode()

            if not dados:
                break

            mensagens = dados.split("\n")

            for msg in mensagens:
                if msg.strip() != "":
                    print("\n" + msg)

            print(flush=True)

        except:
            break


# Thread 2 - enviar comandos
def enviar_comandos():
    while True:
        try:
            comando = input(">>")

            if comando.strip() == "":
                continue

            client.send((comando + "\n").encode())

            if comando.lower() == "exit":
                client.close()

        except:
            break


thread_receber = threading.Thread(target=receber_mensagens)
thread_enviar = threading.Thread(target=enviar_comandos)

thread_receber.start()
thread_enviar.start()

thread_receber.join()
thread_enviar.join()