#!/usr/bin/env python3
"""
Script para cadastrar sigla avulsa
Executado a partir da página edições
"""

import sys
import os
import logging
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# Importar configurações centralizadas
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db_config import DB_CONFIG

def get_db_connection():
    """Conecta ao banco MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
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

def cadastrar_sigla_avulsa(sigla, data_sorteio=None):
    """
    Cadastra uma sigla avulsa na tabela premiacoes
    
    Args:
        sigla (str): Sigla a ser cadastrada
        data_sorteio (str, optional): Data do sorteio no formato YYYY-MM-DD
    """
    try:
        logger.info(f"Iniciando cadastro da sigla avulsa: {sigla}")
        
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
        
        # Verificar se já existe a sigla
        check_query = "SELECT id FROM premiacoes WHERE sigla = %s"
        cursor.execute(check_query, (sigla,))
        existing = cursor.fetchone()
        
        if existing:
            logger.warning(f"Já existe a sigla {sigla} no sistema")
            cursor.close()
            connection.close()
            return {
                "success": False,
                "message": f"Já existe a sigla {sigla} no sistema",
                "data": None
            }
        
        # Preparar dados para inserção
        current_time = datetime.now()
        
        # Inserir registro
        insert_query = """
        INSERT INTO premiacoes (sigla, data_sorteio, created_at, updated_at)
        VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (sigla, data_sorteio, current_time, current_time))
        connection.commit()
        
        registro_id = cursor.lastrowid
        
        logger.info(f"Sigla avulsa cadastrada com sucesso. ID: {registro_id}")
        
        cursor.close()
        connection.close()
        return {
            "success": True,
            "message": f"Sigla {sigla} cadastrada com sucesso",
            "data": {
                "id": registro_id,
                "sigla": sigla,
                "data_sorteio": data_sorteio,
                "created_at": current_time.isoformat()
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
    finally:
        # Não é mais necessário fechar aqui, pois já fechamos após uso
        pass

def main():
    """
    Função principal para execução direta do script
    """
    if len(sys.argv) < 2:
        print("Uso: python cadastrar_sigla_avulsa.py <sigla> [data_sorteio]")
        sys.exit(1)
    
    sigla = sys.argv[1]
    data_sorteio = sys.argv[2] if len(sys.argv) > 2 else None
    
    resultado = cadastrar_sigla_avulsa(sigla, data_sorteio)
    
    if resultado["success"]:
        print(f"SUCESSO: {resultado['message']}")
    else:
        print(f"ERRO: {resultado['message']}")
    sys.exit(1 if not resultado["success"] else 0)

if __name__ == "__main__":
    main() 