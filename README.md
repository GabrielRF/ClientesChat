# [Clientes.Chat](https://clientes.chat)

* [Sobre o serviço](#sobre-o-serviço)
* [Configuração](#configuração)
  * [Banco de Dados](#banco-de-dados)
  * [Variáveis de Ambiente](#variáveis-de-ambiente)
  * [Docker](#docker)
  * [Python](#python)
  * [AWS Lambda](#aws-lambda)
* [Contribuição](#contribuição)

## Sobre o serviço

A maneira mais organizada de atender seus clientes no Telegram!

Para mais informações e ajuda, [visite o site](https://clientes.chat).

## Configuração

### Banco de Dados

O bot exige um banco de dados MongoDB em funcionamento.

#### Container com banco de dados local

O arquivo `docker_compose_local_mongodb.yml` mostra como seria o deploy de um conteiner com o bot e outro com o banco de dados, já com a comunicação entre eles funcionando corretamente. 

#### Container com baco de dados remoto

Para este caso, utilize o arquivo `docker_compose_remote_mongodb.yml`.

### Variáveis de ambiente

`TOKEN`: Token do bot gerado no [@BotFather](https://t.me/BotFather);

`SAC_CHANNEL`: ID do canal em que serão feitos os atendimentos;

`SAC_GROUP`: ID do grupo que será vinculado ao canal para atendimentos;

`BOT_USERNAME`: Nome de usuário do bot que será exibido na mensagem inline;

`MONGO_CON`: String de conexão ao banco de dados;

`LOG_DAYS`: Tempo de retenção do histórico das mensagens no banco. Útil para que as respostas à mensagens funcionem adequadamente;

`NOTIFY_ADMINS`: `1` para notificar administradores em caso de novas mensagens. `0` para não notificar;

`START_MSG`: Mensagem de resposta ao comando de `/start`. Utilize `<br>` para quebras de linhas;

`RESTART_MSG`: Mensagem de resposta quando um atendimento é reaberto. Utilize `<br>` para quebras de linhas;

`END_MSG`: Mensagem enviada quando um atendimento é finalizado. Utilize `<br>` para quebras de linhas.

### Docker

![Docker Pulls](https://img.shields.io/docker/pulls/gabrielrf/clienteschat)

Escolhido o arquivo ideal para seu banco de dados e feitas as configurações das [variáveis de ambiente](#variáveis-de-ambiente), renomeie o arquivo para `docker-compose.yml` execute o comando:

`docker-compose up -d`

### Python

> Para usar este método é necessário ter um banco de dados MongoDB já em funcionamento.

Clone o repositório e edite as variáveis do arquivo `bot.py` conforme a explicação das [variáveis de ambiente usadas em docker](#variáveis-de-ambiente).

Instale as dependências:

```
pip install -r requirements.txt
```

Execute o bot:

```
python bot.py
```

### AWS Lambda

Para mais informações, visite: [https://www.serverless.com/framework/docs/getting-started](https://www.serverless.com/framework/docs/getting-started)

O bot está pronto para funcionar também em modo *webhook*, facilitando que seja executado em uma função AWS Lambda. Para isto, edite o arquivo `serverless_sample.yml` seguindo as [variáveis de ambiente](#variáveis-de-ambiente) explicadas anteriormente. Renomeie o arquivo para `serverless.yml` e execute:

```
serverless deploy
```

Isto irá criar a função e demais componentes necessários para o funcionamento do serviço. Copie a URL exibida no passo anterior, salve-a no arquivo `serverless.yml` e também como uma variável de ambiente local executando:

```
export WEBHOOK=https://SEU_APP.amazonaws.com/
python3 set_webhook.py
```

## Contribuição

**Toda contribuição é bem vinda!**
