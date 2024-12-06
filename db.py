#TESTE
# import mysql.connector

# import os
# from dotenv import load_dotenv
# load_dotenv('config.env')

# conexao = mysql.connector.connect (
#     host= 'localhost',
#     database= 'db_saude',
#     user= os.getenv('USER_DB'),
#     password= os.getenv('PASS_DB'),
#     auth_plugin= 'mysql_native_password'
# )

# if conexao.is_connected():
#     print("Conectado ao DB!")
#     cursor = conexao.cursor()

#Create
def db_create(cursor, conexao, codigo, nome, cns, telefone, anonimo, telefone_valido,tempo_coleta,data_coleta):
    try:
        query = '''
            INSERT INTO pacientes 
            (codigo, nome, cns, telefone, anonimo, telefone_valido, tempo_coleta, data_coleta) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        # Executa a query com os valores
        cursor.execute(query, (codigo, nome, cns, telefone, anonimo, telefone_valido, tempo_coleta, data_coleta))
        conexao.commit()
        
        last_id = cursor.lastrowid
        return f"Procedimento ID {last_id} Criado no DB!"
    except Exception as e:
        return f"Erro: {str(e)}"

#Read
def db_readall(cursor, conexao):  # Select ALL DB
    try:
        cursor.execute('SELECT * FROM pacientes')
        return cursor.fetchall()
    except Exception as e:
        return f"Erro ao ler os dados: {str(e)}"

def db_read(cursor, conexao, id):  # Select ONE DB
    try:
        query = 'SELECT * FROM pacientes WHERE id = %s'
        
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        
        if result:
            return result
        else:
            return f"Nenhum registro encontrado com ID ({id})."
    except Exception as e:
        return f"Erro ao buscar registro: {str(e)}"

def db_read_send(cursor, conexao):  # Select All No Sended DB
    try:        
        cursor.execute('SELECT * FROM pacientes WHERE enviado = 0 AND telefone_valido = 1 AND erro_status <> 1')
        result = cursor.fetchall()
        
        if result:
            return result
        else:
            return "Nenhum registro"
            
    except Exception as e:
        return f"Erro ao buscar registro: {str(e)}"

#Update
def db_update(cursor, conexao, enviado, erro_status, tempo_envio, erro, id, data_envio):
    try:
        query = '''
            UPDATE pacientes 
            SET enviado = %s, erro_status = %s, tempo_envio = %s, erro = %s, data_envio = %s
            WHERE id = %s
        '''
        cursor.execute(query, (enviado, erro_status, tempo_envio, erro, data_envio, id))
        conexao.commit()
        return f"Procedimento ID ({id}) Alterado no DB!"
    except Exception as e:
        return f"Error = {str(e)}"

#Delete
def db_delete(cursor, conexao, id):
    try:
        query = 'DELETE FROM pacientes WHERE id = %s'
        
        cursor.execute(query, (id,))
        conexao.commit()
        
        if cursor.rowcount == 0:
            return f"Nenhum registro encontrado com ID ({id})."
        
        return f"Registro com ID ({id}) Removido!"
    except Exception as e:
        return f"Error = {str(e)}"

# TESTE
# cursor.close()
# conexao.close()