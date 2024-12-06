from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import datetime
import time
import re

#Função para esperar carregar
def loading_table(driver):
    try:
        table = WebDriverWait(driver, 1000).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main_page"]/form/center[2]/table/tbody'))
        )

    except Exception as e:
        print("Erro ao encontrar os campos solicitados:", e)
        driver.quit()

#Função que ajusta o telefone
def validar_telefone(telefone):
    # 1. Remover caracteres indesejados
    telefone_limpo = re.sub(r'[^\d]', '', telefone)  # Remove tudo que não for dígito
    
    # 2. Verificar se o número já possui o DDD (considerando números com 8 ou 9 dígitos)
    if len(telefone_limpo) == 8 or len(telefone_limpo) == 9:  # Telefone sem DDD
        telefone_limpo = '049' + telefone_limpo  # Adiciona o DDD padrão
    
    # 3. Retornar o número completo
    if len(telefone_limpo) == 12:
        return '55' + telefone_limpo
    elif len(telefone_limpo) == 13:
        return '550' + telefone_limpo
    elif len(telefone_limpo) == 14:
        return telefone_limpo
        
    else:
        return None  # Número inválido

#Função para Coletar os dados da Table Carregada
def collect_data(driver):
    templist = []
    i = 3
    
    while(1):
        try:
            start_time = time.time()
            table_dict = {}
            
            cns = driver.find_element(By.XPATH, f'//*[@id="main_page"]/form/center[2]/table/tbody/tr[{i}]/td[2]')
            name = driver.find_element(By.XPATH, f'//*[@id="main_page"]/form/center[2]/table/tbody/tr[{i}]/td[3]')
            
            table_dict['CNS'] = cns.get_attribute("innerHTML")
            table_dict['NAME'] = name.get_attribute("innerHTML")

            number = driver.find_element(By.XPATH, f'//*[@id="main_page"]/form/center[2]/table/tbody/tr[{i}]/td[5]')
            number.click()

            # Select Element - Extract number by pattern - Remove (. & - & space)
            text_number_element = WebDriverWait(driver, 1000).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="fichaAmbulatorial"]/table/tbody[6]/tr[2]/td'))
            )
            phone_pattern =  r'9[-.\s]?\d{4}[-.\s]?\d{4}'
            extract_number = re.findall(phone_pattern, text_number_element.get_attribute("innerHTML"))
            
            if extract_number:
                telefone_bruto = re.sub(r'[-.\s]', '', extract_number[0])
                table_dict['NUMBER'] = validar_telefone(telefone_bruto)
            else:
                table_dict['NUMBER'] = ""
                 
            end_time = time.time()  
            table_dict['COLETA_TEMPO'] = end_time - start_time
            table_dict['DATA_COLETA'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            
            back_button = driver.find_element(By.XPATH, '//*[@id="btnVoltar"]')
            back_button.click()
            templist.append(table_dict)

            WebDriverWait(driver, 1000).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main_page"]/form/center[1]/table/tbody/tr[10]/td/input[1]'))
            )

            i += 1
            print("Paciente ", i-3)

        except NoSuchElementException:
            return templist

#Função para anonimizar os dados
def anonimizar(nome, cns, numero):
    # Numero fixado devido a API de envio
    return "NOME SOBRENOME", 123456789012345, 554998238854