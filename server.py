import socket
import threading
import time
import random
import sys
import json
from datetime import datetime

#definir o número máximo de conexões simultâneas caso o servidor seja executado sem argumentos
if len(sys.argv) > 1:
    LIMITE = int(sys.argv[1])
else:
    LIMITE = 5


#precisamos dizer ao nosso SO que desejamos criar um socket com determinadas características (TCP, IPv4)
HOST = "127.0.0.1"
PORT = 5000

#ativos disponíveis
ativos = {
    "PETR4": 30.0,
    "VALE3": 60.0,
    "ITUB4": 28.0,
    "BBDC4": 15.0,
    "MGLU3": 3.5,
    "WEGE3": 40.0
}

arq = "usuarios.json"

def carregar():
    try:
        with open(arq, "r") as f:
            return json.load(f)
    except:
        return {}
    
def salvar(usuarios):
    with open(arq, "w") as f:
        json.dump(usuarios, f)

usuarios = carregar()

clientes = []
lock = threading.Lock()

#AF_INET para endereços de rede IPv4
#SOCK_STREAM protoclo TCP na camada de transporte
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #criando socket

server.bind((HOST, PORT)) #ligar IP + porta

server.listen(LIMITE) #servidor começa a escutar conexões 

print("Servidor aguardando conexão...")

#acitando mais de um cliente
def aceitar_clientes(conn, addr):
    print("Cliente conectado:", addr)

    with lock:
        clientes.append(conn)

    #login
    conn.send("Digite seu nome:\n".encode())
    nome = conn.recv(1024).decode().strip()

    if nome not in usuarios:
        usuarios[nome] = {"saldo":1000, "carteira": {}}
        salvar(usuarios)
    
    #manda ativos iniciais
    hora = datetime.now().strftime("%H:%M:%S")
    mensagem = f"{hora}: CONECTADO!\n"
    conn.send(mensagem.encode())

    for ativo, preco in ativos.items():
        conn.send(f"{ativo} - R$ {preco}\n".encode())

    t1 = threading.Thread(target=processar_ordem, args=(conn, addr, nome))
    t2 = threading.Thread(target=enviar_precos_cliente, args=(conn,))

    t1.start()
    t2.start()


def processar_ordem(conn, addr, nome):

    carteira = usuarios[nome]["carteira"]
    
    while True:
        try:
            dados = conn.recv(1024).decode()

            if not dados:
                break

            linhas = dados.split("\n")

            for linha in linhas:

                if not linha.strip():
                    continue

                comando = linha.strip().split()

                if not comando:
                    continue

                # buy
                if comando[0] == "buy":

                    if len(comando) != 3:
                        conn.send("Uso: buy ATIVO QUANTIDADE\n".encode())
                        continue

                    ativo = comando[1]
                    qtd = int(comando[2])

                    if ativo in ativos:
                        preco = ativos[ativo]
                        custo = preco * qtd

                        if usuarios[nome]["saldo"] >= custo:

                            usuarios[nome]["saldo"] -= custo

                            if ativo in carteira:
                                carteira[ativo] += qtd
                            else:
                                carteira[ativo] = qtd

                            salvar(usuarios)

                            resposta = f"Comprou {qtd} de {ativo}\n"

                        else:
                            resposta = "Saldo insuficiente.\n"

                    else:
                        resposta = "Ativo não existe.\n"

                    conn.send(resposta.encode())

                # sell
                elif comando[0] == "sell":

                    if len(comando) != 3:
                        conn.send("Uso: sell ATIVO QUANTIDADE\n".encode())
                        continue

                    ativo = comando[1]
                    qtd = int(comando[2])

                    if ativo in carteira and carteira[ativo] >= qtd:

                        preco = ativos[ativo]
                        valor = preco * qtd

                        carteira[ativo] -= qtd
                        usuarios[nome]["saldo"] += valor

                        salvar(usuarios)

                        resposta = f"Vendeu {qtd} de {ativo}.\n"

                    else:
                        resposta = "Você não tem esse ativo.\n"

                    conn.send(resposta.encode())

                # carteira
                elif comando[0] == "carteira":

                    texto = f"Saldo: R$ {round(usuarios[nome]['saldo'], 2)}\n"

                    if not carteira:
                        texto += "Carteira vazia.\n"
                    else:
                        for ativo, qtd in carteira.items():
                            texto += f"{ativo}: {qtd}\n"

                    conn.send(texto.encode())

                # sair
                elif comando[0] == "exit":
                    print("Cliente desconectou:", addr)
                    conn.send("Encerrando conexão\n".encode())

                    with lock:
                        if conn in clientes:
                            clientes.remove(conn)
                    conn.close()
                    return

                else:
                    conn.send("Comando inválido.\n".encode())

        except Exception:
            with lock:
                if conn in clientes:
                    clientes.remove(conn)
            break

def enviar_precos_cliente(conn):
    while True:
        try:
            texto = "Atualização de preços:\n"

            for ativo, preco in ativos.items():
                texto += f"{ativo}: R$ {round(preco,2)}\n"

            conn.send(texto.encode())
            time.sleep(20)

        except:
            break

#THREAD 2 -  simular a variação dos preços dos ativos
def atualizar_precos():
    while True:
        for ativo in ativos:
            variacao = random.uniform(-0.1, 0.1)
            ativos[ativo] += variacao

        time.sleep(20) #atualiza a cada x seg.

thread_precos = threading.Thread(target=atualizar_precos, daemon=True)
thread_precos.start()

while True:
    conn, addr = server.accept()

    with lock:
        if len(clientes) >= LIMITE:
            conn.send("Servidor lotado. Tente novamente mais tarde.\n".encode())
            conn.close()
            continue

    thread = threading.Thread(target=aceitar_clientes, args=(conn, addr))
    thread.start()

