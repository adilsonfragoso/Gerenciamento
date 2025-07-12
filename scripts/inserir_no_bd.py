import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db_config import DB_CONFIG
import pandas as pd
import mysql.connector
from datetime import datetime

# Função para extrair sigla do nome do arquivo CSV
def extrair_sigla_do_arquivo(caminho_csv):
    """Extrai a sigla do nome do arquivo CSV aplicando as regras corretas"""
    try:
        nome_arquivo = os.path.basename(caminho_csv)
        
        # Remove prefixo e sufixo
        if nome_arquivo.startswith("relatorio-vendas-"):
            nome_sem_prefixo = nome_arquivo[17:]  # Remove "relatorio-vendas-"
            nome_sem_sufixo = nome_sem_prefixo.replace(".csv", "")  # Remove ".csv"
            
            # Converter hífens para espaços e deixar em maiúsculo
            texto_processado = nome_sem_sufixo.replace("-", " ").upper()
            
            # Aplicar as regras de extração
            if " RJ " in texto_processado:
                # Se contém "RJ", a sigla é o que vem antes de "RJ"
                sigla = texto_processado.split(" RJ ")[0].strip()
            elif " EDICAO " in texto_processado:
                # Se não contém "RJ", a sigla é o que vem antes de "EDICAO"
                sigla = texto_processado.split(" EDICAO ")[0].strip()
            else:
                return None
                
            print(f"Sigla extraída do arquivo: '{sigla}'")
            return sigla
                
    except Exception as e:
        print(f"Erro ao extrair sigla do arquivo: {e}")
    
    return None

if len(sys.argv) < 3:
    print("Uso correto: python inserir_no_bd.py <edicao> <caminho_csv>")
    sys.exit(1)

edicao_desejada = sys.argv[1]    # Edição (ex: 5362)
caminho_csv = sys.argv[2]       # Caminho do CSV

# Extrair sigla do nome do arquivo
sigla_extraida = extrair_sigla_do_arquivo(caminho_csv)

if not sigla_extraida:
    print("ERRO: Não foi possível extrair a sigla do arquivo. Verifique o nome do arquivo CSV.")
    sys.exit(1)

# Verifica se o CSV existe
if not os.path.exists(caminho_csv):
    print(f"ERRO: O arquivo CSV não foi encontrado: {caminho_csv}")
    sys.exit(1)

try:
    # 1) Ler o CSV ignorando a 1a linha (cabeçalho) e sem usar nomes de coluna (header=None)
    df = pd.read_csv(
        caminho_csv,
        sep=';',        # Ajuste o delimitador conforme seu CSV
        encoding='utf-8',
        skiprows=1,     # Ignora a primeira linha
        header=None     # Não usar linha de cabeçalho
    )

    # Colunas de interesse:
    #  A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7, ...
    df_nome       = df.iloc[:, 6]  # G
    df_telefone   = df.iloc[:, 7]  # H
    df_quantidade = df.iloc[:, 3]  # D
    df_valor      = df.iloc[:, 5]  # F
    df_horadata   = df.iloc[:, 13] # M (coluna 13)

    # 2) Conexão ao MySQL
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Verifica se já existe registro para esta edição em relatorios_importados
    sql_check = """
        SELECT COUNT(*) FROM relatorios_importados WHERE edicao = %s
    """
    cursor.execute(sql_check, (edicao_desejada,))
    existe = cursor.fetchone()[0]

    if existe != 0:
        print(f"Edição {edicao_desejada} já existe em relatorios_importados. Nada será inserido em interno nem em relatorios_importados.")
        conn.close()
        sys.exit(0)

    # 3) Preparar INSERT para interno
    sql_insert = """
        INSERT INTO interno (nome, telefone, edicao, Extracao, quantidade, valorTotal, horadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    total_inseridos = 0

    # 4) Percorre cada linha do DataFrame e insere no banco
    for i in range(len(df)):
        nome     = str(df_nome.iloc[i]).strip()
        telefone = str(df_telefone.iloc[i]).strip()
        edicao   = edicao_desejada

        try:
            quantidade = int(df_quantidade.iloc[i])
        except:
            quantidade = 0

        try:
            valor_total = float(str(df_valor.iloc[i]).replace(',', '.'))
        except:
            valor_total = 0.0

        # Usar data/hora oficial da coluna 13
        try:
            data_compra = datetime.strptime(str(df_horadata.iloc[i]).strip(), "%d/%m/%Y, %H:%M:%S")
        except Exception as e:
            print(f"Erro ao converter data/hora para o registro {i}: {df_horadata.iloc[i]} - {e}")
            data_compra = None

        # ORDEM CORRIGIDA: nome, telefone, edicao, Extracao, quantidade, valorTotal, horadata
        valores = (nome, telefone, edicao, sigla_extraida, quantidade, valor_total, data_compra)
        cursor.execute(sql_insert, valores)
        total_inseridos += 1

    # **Nova parte**: somar todas as quantidades e inserir em relatorios_importados
    # Calcula o total de cotas enviadas nesta execução
    total_cotas = 0
    for q in df_quantidade:
        try:
            total_cotas += int(q)
        except:
            continue

    # Verifica se já existe registro para esta edição em relatorios_importados
    sql_check = """
        SELECT COUNT(*) FROM relatorios_importados WHERE edicao = %s
    """
    cursor.execute(sql_check, (edicao_desejada,))
    existe = cursor.fetchone()[0]

    if existe == 0:
        sql_insert_rel = """
            INSERT INTO relatorios_importados (edicao, total_cotas, data, Extracao)
            VALUES (%s, %s, NOW(), %s)
        """
        cursor.execute(sql_insert_rel, (edicao_desejada, total_cotas, sigla_extraida))
    else:
        print(f"Edição {edicao_desejada} já existe em relatorios_importados. Não será inserido novamente.")

    # 5) Confirmar transações
    conn.commit()
    print(f"{total_inseridos} linhas inseridas em 'interno' e total_cotas={total_cotas} gravado em 'relatorios_importados'.")

except mysql.connector.Error as err:
    print(f"Erro ao conectar ou inserir no banco: {err}")

except Exception as e:
    print(f"Erro ao ler CSV ou processar dados: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
