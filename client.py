import socket
import threading

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

            print(dados, end="\n")  

        except:
            break


# Thread 2 - enviar comandos
def enviar_comandos():
    while True:
        try:
            comando = input(">> ")
            client.send((comando + "\n").encode())

            if comando == "exit":
                client.close()
                break
        except:
            break


thread_receber = threading.Thread(target=receber_mensagens)
thread_enviar = threading.Thread(target=enviar_comandos)

thread_receber.start()
thread_enviar.start()

thread_receber.join()
thread_enviar.join()