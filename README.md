# [Clientes.Chat](https://clientes.chat)

* [Sobre o serviço](sobre_o_serviço)
* [Configuração](#configuração)
  * [Docker](#docker)
  * [Python](#python)
* [Contribuição](#contribuição)

## Sobre o serviço

A maneira mais organizada de atender seus clientes no Telegram!

Para mais informações, [visite o site](https://clientes.chat).

## Configuração

### Docker

Clone o repositório, renomeie o arquivo `docker-compose_sample.yml` para `docker-compose.yml` e ajuste as variáveis.

#### Variáveis de ambiente

`TOKEN`: Token do bot gerado no [@BotFather](https://t.me/BotFather);

`SAC_CHANNEL`: ID do canal em que serão feitos os atendimentos;

`SAC_GROUP`: ID do grupo que será vinculado ao canal para atendimentos;

`BOT_USERNAME`: Nome de usuário do bot que será exibido na mensagem inline;

`MONGO_SERVER`: Servidor de banco de dados;

`MONGO_PORT`: Porta de conexão ao banco de dados;

`LOG_DAYS`: Tempo de retenção do histórico das mensagens no banco. Útil para que as respostas à mensagens funcionem adequadamente;

`NOTIFY_ADMINS`: `1` para notificar administradores em caso de novas mensagens. `0` para não notificar;

`START_MSG`: Mensagem de resposta ao comando de `/start`. Utilize `<br>` para quebras de linhas;

`RESTART_MSG`: Mensagem de resposta quando um atendimento é reaberto. Utilize `<br>` para quebras de linhas;

`END_MSG`: Mensagem enviada quando um atendimento é finalizado. Utilize `<br>` para quebras de linhas.

#### Deploy

`docker-compose up -d` para rodar o bot e o banco de dados.

### Python

Clone o repositório e edite as variáveis do arquivo `bot.py` conforme a explicação das variáveis de ambiente do docker.

## Contribuição

Toda contribuição é bem vinda! Sem exceção.
