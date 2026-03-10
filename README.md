# Pregão da Bolsa de Valores

Projeto desenvolvido na disciplina de Redes e Comunicação da PUC-Campinas.

## Descrição
Este projeto simula um ambiente simples de negociação de ativos da bolsa de valores

O sistema possui um **servidor** que controla os ativos e um **cliente** que permite ao usuário enviar ordens de compra e venda.

## Etapa 1 

---

## Funcionamento

- O **servidor** mantém uma lista de ativos e seus preços.
- Os preços variam automaticamente com valores aleatórios.
- O **cliente** recebe atualizações periódicas dos preços.
- O usuário pode comprar, vender e consultar sua carteira.

---

## Threads

### Servidor
- **Thread 1:** processa ordens de compra e venda.
- **Thread 2:** simula a variação de preços e envia o feed ao cliente.

### Cliente
- **Thread 1:** envia comandos digitados pelo usuário.
- **Thread 2:** recebe atualizações do servidor.

---

## Ativos Simulados

- PETR4
- VALE3
- ITUB4
- BBDC4
- MGLU3
- WEGE3

---
