[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# [Clientes.Chat](https://clientes.chat)

* [Sobre o serviço](#sobre-o-serviço)
* [Configuração](#configuração)
  * [Banco de Dados](#banco-de-dados)
  * [Variáveis de Ambiente](#variáveis-de-ambiente)
  * [Docker](#docker)
  * [Python](#python)
  * [Heroku](#heroku)
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

### Heroku

O bot está pronto para funcionar também em modo *webhook*, facilitando que seja executado no site [Heroku](https://heroku.com). Para isto, defina as mesmas [variáveis de ambiente](#variáveis-de-ambiente) explicadas anteriormente e acrescente a variável:

```
WEBHOOK = https://SEU_APP.herokuapp.com/
```

## Contribuição

**Toda contribuição é bem vinda!**
