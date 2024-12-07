
# Projeto sobre o SISREG³

Este projeto é uma aplicação automatizada para coleta e envio de dados do sistema SISREG³. Utilizando Selenium para acessar e extrair informações diretamente da interface web do SISREG, e o Twilio para enviar mensagens via WhatsApp, este projeto visa otimizar processos manuais e reduzir erros operacionais, especialmente em contextos que envolvem grande volume de dados e notificações.
Embora o sistema esteja em fase de simulação, ele analisa tempos de execução e valida números de telefone, oferecendo um relatório detalhado do status do envio.

## Para executar

Para executar o projeto, segue abaixo os requisitos e como executa-lo:

### Requisitos básicos

Antes de iniciar, você precisará dos seguintes componentes instalados:

- Python 3.1 ou superior
- Gerenciador de pacotes pip
- Navegador Google Chrome
- Banco de dados: MYsql ou outro SGBD campatível com o SQL básico

### Clonando o repositório

Clone o repositório para sua máquina local:

- git clone https://github.com/WilliamDRib/NewSisregiii.git
- cd NewSisregiii

### Instalando dependencias

Observação: Recomenda-se o uso de ambiente virtual (venv).

- Criação do venv: python -m venv venv
- Utilizar o venv: \venv\Script\activate.bat

Você pode instalar todas as bibliotecas necessárias de duas formas:

- Utilizando o requirements.txt com o seguinte comando:

    - pip install -r requirements.txt

- Caso desejar pode instalar as bibliotecas individualmente:

    - selenium 
    - webdriver_manager
    - pandas 
    - mysql.connector 
    - twilio

### Criando o Banco de Dados

- Certifique que o servido do banco de dados esteja ativo.
- execute o scipt create_db.sql para criar as tabelas necessárias.

Comando para executar o script: mysql -u <usuario> -p < create_db.sql

Substitua <usuario> pelo seru nome de usuário no MySQL.

### Configuração inicial

Para executar o codigo precisa primeiro configura-lo:

Dentro do arquivo config.env.sample tem o modelo das variaveis de ambiente necesários. Crie um arquivo config.env seguindo o config.env.sample como exemplo.

Configurar o config.env da seguinte forma:
- USER_SIS: Usuario de login no SISREG³
- PASS_SIS: Senha de login no SISREG³
- USER_DB: Usuario para comunicar com o DB
- PASS_DB: Senha para comunicar com o BD
- TWILIO_ACCOUNT: Codigo SID da conta do Twilio
- TWILIO_TOKEN: Token de autenticação do Twilio
- NUMBER_ANONIMO: Telefone para envio de teste na anonimização (Deixar vazio caso não deseje anonimizar os dados)

### Executando

python main.py

## Estrutura do projeto

A estrutura do projeto está organizado da seguinte forma:

- main.py: Arquivo principal que executa o sistema.
- requirements.txt: Arquivo com as dependencias necessárias.
- db_create.sql: Arquivo com o SQL para criação do DataBase.
- db.py: Arquivo com as funções de Query ao DataBase.
- dados.py: Arquivo com as principais funções utilizadas para coletar os dados do SISREG³.