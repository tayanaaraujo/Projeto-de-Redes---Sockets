import socket
import threading
import time
import random
from datetime import datetime

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

saldo = 1000
carteira = {}

#AF_INET para endereços de rede IPv4
#SOCK_STREAM protoclo TCP na camada de transporte
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #criando socket

server.bind((HOST, PORT)) #ligar IP + porta

server.listen(1) #servidor começa a escutar conexões (por enquanto apenas com 1 cliente)

print("Servidor aguardando conexão...")

conn, addr = server.accept() #conn → conexão com cliente, addr → endereço do cliente

print("Cliente conectado:", addr)

#mensagem de conexão
hora = datetime.now().strftime("%H:%M:%S")
mensagem = f"{hora}: CONECTADO!\n"
conn.send(mensagem.encode())

#envia ativos iniciais
for ativo, preco in ativos.items():
    msg = f"{ativo} - R$ {preco}\n"
    conn.send(msg.encode())

# THEREAD 1 - processar ordem de compra/venda
def processar_ordem():
    global saldo

    while True:
        try:
            dados = conn.recv(1024).decode()
            if not dados:
                break

            comando = dados.strip().split()

            #ordem de compra
            if comando[0] == ":buy":

                ativo = comando[1]
                qtd = int(comando[2])

                if ativo in ativos:
                    preco = ativos[ativo]
                    custo = preco * qtd

                    if saldo >= custo:
                        saldo -= custo
                        if ativo in carteira:
                            carteira[ativo] += qtd
                        else:
                            carteira[ativo] = qtd

                        resposta = f"Comprou {qtd} de {ativo}\n"

                    else:
                        resposta = "Saldo insuficiente\n"
                else:
                    resposta = "Ativo não existe\n"

                conn.send(resposta.encode())

            #ordem de venda
            elif comando[0] == ":sell":
                ativo = comando[1]
                qtd = int(comando[2])

                if ativo in carteira and carteira[ativo] >= qtd:
                    preco = ativos[ativo]
                    valor = preco * qtd
                    carteira[ativo] -= qtd
                    saldo += valor
                    resposta = f"Vendeu {qtd} de {ativo}\n"
                else:
                    resposta = "Você não tem esse ativo\n"
                
                conn.send(resposta.encode())

            elif comando[0] == ":carteira":
                texto = f"Saldo: R$ {round(saldo, 2)}\n"
                for ativo, qtd in carteira.items():
                    texto += f"{ativo}: {qtd}\n"
                conn.send(texto.encode())

            elif comando[0] == ":exit":
                conn.send("Encerrando conexão\n".encode())
                conn.close()
                break

        except:
            break

#THREAD 2 -  simular a variação dos preços dos ativos
def atualizar_precos():
    while True:
        for ativo in ativos:
            #variação aleatória entre -5% e +5%
            variacao = ativos[ativo] * random.uniform(-0.05, 0.05)
            ativos[ativo] += variacao

        texto = "\nAtualização de preços:\n"

        for ativo, preco in ativos.items():
            texto += f"{ativo}: {round(preco,2)}\n"

        try:
            conn.send(texto.encode())
        except:
            break

        time.sleep(5) #atualiza a cada 5 seg.


#Criando threads para processar ordens e atualizar preços
thread1 = threading.Thread(target=processar_ordem)
thread2 = threading.Thread(target=atualizar_precos)

thread1.start()
thread2.start()

thread1.join()
thread2.join()
