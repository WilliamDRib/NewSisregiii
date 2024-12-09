#Imports Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


#Outros imports
import re
import pandas as pd
import time
import random
from datetime import datetime,timedelta

#Import das funções do DB
import mysql.connector
from db import db_create, db_read, db_readall, db_update, db_delete, db_read_send

#Variaveis de ambiente
import os
from dotenv import load_dotenv
load_dotenv('config.env')

#Criando Conexão com o DB
conexao = mysql.connector.connect (
    host= 'localhost',
    database= 'db_saude',
    user= os.getenv('USER_DB'),
    password= os.getenv('PASS_DB'),
    auth_plugin= 'mysql_native_password'
)

#Valida Conexao do DB
if conexao.is_connected():
    print("Conectado ao DB!")
    cursor = conexao.cursor()
else:
    print("Não foi possivel criar comunicação com o DB")
    quit()


#Configurando o WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service = service, options=chrome_options)

# ------------------- Login -------------------

# URL da página de login
url_login = 'https://sisregiii.saude.gov.br/'
driver.get(url_login)  

# Esperar a página de login carregar e encontrar os campos
try:
    username_field = WebDriverWait(driver, 1000).until(
        EC.presence_of_element_located((By.ID, 'usuario'))
    )
    password_field = driver.find_element(By.ID, 'senha')

except Exception as e:
    print("Erro ao encontrar os campos de login: ", e)
    driver.quit()

# Inserir credenciais e fazer login
username_field.send_keys(os.getenv('USER_SIS'))
password_field.send_keys(os.getenv('PASS_SIS'))
password_field.send_keys(Keys.RETURN)

print("Logado")


# ------------------- Formulario Inicial -------------------


# Redireciona para a pagina de consulta
url_table = "https://sisregiii.saude.gov.br/cgi-bin/cons_marcados_reg"
driver.get(url_table)

# Esperar a página de login carregar e encontrar os campos
try:
    autorizacao = WebDriverWait(driver, 1000).until(
        EC.presence_of_element_located((By.ID, 'tp_periodo_aut'))
    )
    inicio_periodo = driver.find_element(By.ID, 'dataInicial')
    final_periodo  = driver.find_element(By.ID, 'dataFinal')
    pesquisar = driver.find_element(By.NAME, 'pesquisar')

except Exception as e:
    print("Erro ao encontrar os campos solicitados:", e)
    driver.quit()

# Preenche o formulario e busca
autorizacao.click()

# Salva a data do dia atual
hoje = datetime.today()
data = hoje.strftime('%d-%m-%Y')

# Preenche o formulário com a data atual
inicio_periodo.send_keys(data)
final_periodo.send_keys(data)
# pesquisar.click()

print("Fomulario preenchido")

# ------------------- Coleta -------------------

# Importa as funções usadas para Coleta de dados
from dados import loading_table, collect_data, anonimizar

df = pd.DataFrame()
contador_tela = 1
next_button = None

while(1):
    print("Carregando tela ", contador_tela)
    loading_table(driver)
    print("Coletando da tela ", contador_tela)

    # Coleta todos os dados da table
    templist = collect_data(driver)

    # Adiciona os dados coletados ao DataFrame principal
    df = pd.concat([df, pd.DataFrame(templist)], ignore_index=True)
    templist = []

    # Verifica se há mais páginas
    next_button = driver.find_element(By.XPATH, '//*[@id="main_page"]/form/center[3]/table/tbody/tr/td/a[last()]')
    img_button = next_button.find_element(By.TAG_NAME, 'img')

    if img_button.get_attribute('alt') == "Anterior":
        break

    next_button.click()
    contador_tela += 1

# ------------------- Salvar DB -------------------

# Iterando o Dataframe
for index, row in df.iterrows():

    numero_valido = False
    if row['NUMBER']:
        numero_valido = True

    # Salvando no DB (Verifica se vai ser salvo anonimo ou os dados)
    if os.getenv('NUMBER_ANONIMO') in (None, ""):
        print(db_create(cursor, conexao, row['CODIGO'], row['NAME'], row['CNS'], row['NUMBER'], True, numero_valido, row['COLETA_TEMPO'], row['DATA_COLETA']))
    else:
        # Anonimizando os dados
        codigo, nome, cns, numero = anonimizar(os.getenv('NUMBER_ANONIMO'))
        print(db_create(cursor, conexao, codigo, nome, cns, numero, True, numero_valido, row['COLETA_TEMPO'], row['DATA_COLETA']))

df = pd.DataFrame() #Limpa os valores salvos

# ------------------- Envio -------------------

from twilio.rest import Client as Client_Twilio

twilio = Client_Twilio(
    os.getenv('TWILIO_ACCOUNT'),
    os.getenv('TWILIO_TOKEN')
)

twilio_number = 'whatsapp:'+str(os.getenv('TWILIO_NUMBER'))

# Lendo os dados do DB que precisam ser enviados
result = db_read_send(cursor, conexao)

for row in result:
    try:
        start_time = time.time()

        numero = 'whatsapp:+'+str(row[4])
        mensagem = f'''
            Olá paciente {row[2]}, voce teve seu procedimento liberado, por favor comparecer ao Setor Responsavel.        
        '''

        # Enviar a mensagem via WhatsApp pelo Twilio
        message = twilio.messages.create(
            from_ = twilio_number,
            to = numero,
            body = mensagem
        )
        
        tentativas = 0
        max_tentativas = 10
        status = message.status

        print(f'Tentativa de envio de mensagem, ID {row[0]}')

        # Espera a mensagem ser enviada
        while status not in ['delivered', 'undelivered', 'failed', 'read'] and tentativas < max_tentativas:
            time.sleep(1) 
            message = twilio.messages(message.sid).fetch()
            status = message.status
            tentativas += 1

        # Verifica se a mensagem foi enviada
        if status not in ['delivered', 'read']:
            raise Exception(f"Mensagem não entregue. Status final: {status}")
            
        tempo_para_enviar = time.time() - start_time
        date_now = datetime.now().strftime("%Y%m%d%H%M%S")

        # Registrando sobre o envio
        print(db_update(cursor, conexao, 1, 0, tempo_para_enviar, None, row[0], date_now))
        
    except Exception as e:
        # Se der erro no envio, registrar no status
        date_now = datetime.now().strftime("%Y%m%d%H%M%S")
        print(db_update(cursor, conexao, 0, 1, 0, str(e), row[0], date_now))
        print(str(e))

# ------------------- End -------------------

driver.close()
cursor.close()
conexao.close()

print("Fim!")