#!/usr/bin/env python3
"""
Script para cadastrar siglas diárias
Executado a partir da página edições
"""

import sys
import os
import logging
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import requests


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db_config import DB_CONFIG

def get_db_connection():
    """Conecta ao banco MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if not connection.is_connected():
            logger.error("Não foi possível estabelecer conexão com o banco")
            return None
        return connection
    except Error as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        return None

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def cadastrar_siglas_diarias(data_sorteio, siglas_selecionadas):
    """
    Cadastra siglas diárias na tabela siglas_diarias
    
    Args:
        data_sorteio (str): Data no formato YYYY-MM-DD
        siglas_selecionadas (list): Lista de siglas para cadastrar
    """
    try:
        logger.info(f"Iniciando cadastro de siglas para {data_sorteio}")
        
        # Conectar ao banco
        connection = get_db_connection()
        if connection is None:
            logger.error("Não foi possível conectar ao banco de dados.")
            return {
                "success": False,
                "message": "Não foi possível conectar ao banco de dados.",
                "data": None
            }
        cursor = connection.cursor()
        
        # Verificar se já existe registro para esta data
        check_query = "SELECT id FROM siglas_diarias WHERE data_sorteio = %s"
        cursor.execute(check_query, (data_sorteio,))
        existing = cursor.fetchone()
        
        if existing:
            logger.warning(f"Já existe registro para a data {data_sorteio}")
            cursor.close()
            connection.close()
            return {
                "success": False,
                "message": f"Já existe registro para a data {data_sorteio}",
                "data": None
            }
        
        # Calcular dia da semana
        data_obj = datetime.strptime(data_sorteio, '%Y-%m-%d')
        dia_semana = data_obj.strftime('%A')  # Nome completo do dia
        
        # Inserir registro
        insert_query = """
        INSERT INTO siglas_diarias (diaSemana, data_sorteio, siglas, created_at)
        VALUES (%s, %s, %s, NOW())
        """
        
        siglas_str = ', '.join(siglas_selecionadas)
        cursor.execute(insert_query, (dia_semana, data_sorteio, siglas_str))
        connection.commit()
        
        registro_id = cursor.lastrowid
        
        logger.info(f"Siglas cadastradas com sucesso. ID: {registro_id}")
        
        cursor.close()
        connection.close()
        return {
            "success": True,
            "message": f"Siglas cadastradas com sucesso para {data_sorteio}",
            "data": {
                "id": registro_id,
                "data_sorteio": data_sorteio,
                "siglas": siglas_selecionadas,
                "dia_semana": dia_semana
            }
        }
        
    except Error as e:
        logger.error(f"Erro no banco de dados: {e}")
        return {
            "success": False,
            "message": f"Erro no banco de dados: {e}",
            "data": None
        }
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return {
            "success": False,
            "message": f"Erro inesperado: {e}",
            "data": None
        }

def main():
    """
    Função principal para execução direta do script
    """
    if len(sys.argv) < 3:
        print("Uso: python cadastrar_siglas.py <data_sorteio> <sigla1,sigla2,sigla3>")
        sys.exit(1)
    
    data_sorteio = sys.argv[1]
    siglas_str = sys.argv[2]
    siglas_selecionadas = [s.strip() for s in siglas_str.split(',')]
    
    resultado = cadastrar_siglas_diarias(data_sorteio, siglas_selecionadas)
    
    if resultado["success"]:
        print(f"SUCESSO: {resultado['message']}")
        sys.exit(0)
    else:
        print(f"ERRO: {resultado['message']}")
        sys.exit(1)

def enviar_para_api(data_sorteio, siglas_selecionadas):
    """
    Envia os dados para a API
    
    Args:
        data_sorteio (str): Data no formato YYYY-MM-DD
        siglas_selecionadas (list): Lista de siglas para cadastrar
    """
    # Configuração da API (ajustar conforme necessário)
    API_HOST = "localhost"
    API_PORT = "8001"
    
    url = f"http://{API_HOST}:{API_PORT}/api/siglas"
    payload = {
        "data_sorteio": data_sorteio,
        "siglas_selecionadas": siglas_selecionadas
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            resultado = response.json()
            if resultado.get('success'):
                print(f"SUCESSO: {resultado['message']}")
                return True
            else:
                print(f"ERRO: {resultado['message']}")
                return False
        else:
            print(f"ERRO: Falha na requisição - Status {response.status_code}") 
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha na conexão com a API - {e}")
        return False

if __name__ == "__main__":
    main() 