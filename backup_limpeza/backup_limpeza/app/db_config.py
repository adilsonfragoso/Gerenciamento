# db_config.py
# Configurações de conexão ao banco MySQL

from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}
