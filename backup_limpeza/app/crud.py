# crud.py
import pymysql
from .db_config import DB_CONFIG

def get_all_siglas():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT id, sigla FROM premiacoes
                ORDER BY
                  CASE
                    WHEN sigla REGEXP '^PPT(_| |$)' THEN 1
                    WHEN sigla REGEXP '^PTM(_| |$)' THEN 2
                    WHEN sigla REGEXP '^PT(_| |$)' THEN 3
                    WHEN sigla REGEXP '^PTV(_| |$)' THEN 4
                    WHEN sigla REGEXP '^PTN(_| |$)' THEN 5
                    WHEN sigla REGEXP '^FEDERAL(_| |$)' THEN 6
                    WHEN sigla REGEXP '^CORUJINHA(_| |$)' THEN 7
                    ELSE 8
                  END,
                  CAST(
                    IF(sigla REGEXP '^[A-Z]+_[0-9]+', SUBSTRING_INDEX(sigla, '_', -1), '0')
                    AS UNSIGNED
                  ),
                  sigla
            ''')
            return cursor.fetchall()
    finally:
        conn.close()

def get_premiacao_by_id(premiacao_id):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM premiacoes WHERE id=%s", (premiacao_id,))
            return cursor.fetchone()
    finally:
        conn.close()

# Outras funções de CRUD podem ser adicionadas aqui (create, update, delete)
