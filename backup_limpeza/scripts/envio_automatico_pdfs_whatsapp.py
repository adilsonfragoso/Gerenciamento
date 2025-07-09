#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Envio Automático de PDFs para WhatsApp
Baseado em novo_chamadas_group_latest.py
Envia PDFs automaticamente quando ficam disponíveis
"""

import os
import requests
import base64
import time
import sys
import logging
import mysql.connector
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs/envio_pdfs_whatsapp.log')), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Importar configurações centralizadas
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from db_config import DB_CONFIG

# Caminhos
caminho_imagens = r"D:\Documentos\Workspace\Gerenciamento\uploads"
caminho_pdfs = r"D:\Adilson\Downloads"

# ID do grupo no WhatsApp
#id_grupo = "120363307707983386@g.us"  # grupo links
id_grupo = "5512997650505-1562805682@g.us"  # grupo anotações

# Sua API Key
api_key = "9ADC66CB5A10-488D-9B85-4B4A7BB90E8A"

# URL da API Evolution para PDF
url_pdf = "https://evo2.linksystems.com.br/message/sendMedia/Bancada"

def montar_texto_pdf(edicao, sigla_oficial, link):
    """Monta o texto da mensagem para envio do PDF"""
    return (
        f"🎯 Edição: {edicao}\n\n"
        f"📄 Segue relatório dos participantes em anexo 📎\n\n"
        f"🏆 BOA SORTE A TODOS! 🍀🎉"
    )

def buscar_imagem(extracao):
    """Busca a imagem correspondente à extração"""
    for ext in [".jpg", ".jpeg", ".png"]:
        caminho_arquivo = os.path.join(caminho_imagens, extracao + ext)
        if os.path.isfile(caminho_arquivo):
            return caminho_arquivo
    return None

def buscar_pdf(edicao, sigla_oficial):
    """Busca o PDF correspondente à edição"""
    # Padrões de nome do PDF
    padroes = [
        f"relatorio_{edicao}.pdf",
        f"relatorio_{sigla_oficial}_{edicao}.pdf",
        f"{sigla_oficial}_{edicao}.pdf",
        f"edicao_{edicao}.pdf"
    ]
    
    for padrao in padroes:
        caminho_pdf = os.path.join(caminho_pdfs, padrao)
        if os.path.isfile(caminho_pdf):
            return caminho_pdf
    
    # Busca genérica por qualquer PDF que contenha a edição
    try:
        pasta_pdfs = Path(caminho_pdfs)
        for arquivo in pasta_pdfs.glob("*.pdf"):
            if str(edicao) in arquivo.name:
                return str(arquivo)
    except Exception as e:
        logger.error(f"Erro ao buscar PDF para edição {edicao}: {e}")
    
    return None

def buscar_rifas_com_pdf_pendente():
    """Busca rifas que têm PDF disponível mas ainda não foram enviadas para WhatsApp"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = """
        SELECT edicao, sigla_oficial, extracao, link, andamento, status_rifa,
               status_envio_pdf_whatsapp
        FROM extracoes_cadastro 
        WHERE status_rifa = 'concluído'
        AND andamento = '100%'
        AND (status_envio_pdf_whatsapp IS NULL OR status_envio_pdf_whatsapp = 'pendente')
        ORDER BY edicao DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Converter resultados para dicionários
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        resultados = []
        for row in rows:
            if row is not None and columns:
                resultados.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        
        # Filtrar apenas rifas que realmente têm PDF disponível
        rifas_com_pdf = []
        for rifa in resultados:
            pdf_path = buscar_pdf(rifa['edicao'], rifa['sigla_oficial'])
            if pdf_path:
                rifa['pdf_path'] = pdf_path
                rifas_com_pdf.append(rifa)
        
        return rifas_com_pdf
        
    except Exception as e:
        logger.error(f"Erro ao buscar rifas com PDF pendente: {e}")
        return []

def adicionar_coluna_status_pdf():
    """Adiciona a coluna status_envio_pdf_whatsapp se ela não existir"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Verificar se a coluna existe
        cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'litoral' 
        AND TABLE_NAME = 'extracoes_cadastro' 
        AND COLUMN_NAME = 'status_envio_pdf_whatsapp'
        """)
        
        if cursor.fetchone() is None:
            # Coluna não existe, vamos criá-la
            cursor.execute("""
            ALTER TABLE extracoes_cadastro 
            ADD COLUMN status_envio_pdf_whatsapp VARCHAR(20) DEFAULT 'pendente'
            """)
            conn.commit()
            logger.info("Coluna status_envio_pdf_whatsapp criada com sucesso")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Erro ao verificar/criar coluna status_envio_pdf_whatsapp: {e}")

def atualizar_status_envio_pdf(edicao, status='enviado'):
    """Atualiza o status de envio do PDF para WhatsApp"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = "UPDATE extracoes_cadastro SET status_envio_pdf_whatsapp = %s WHERE edicao = %s"
        cursor.execute(query, (status, edicao))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        logger.info(f"Status PDF WhatsApp atualizado para '{status}' na edição {edicao}")
        
    except Exception as e:
        logger.error(f"Erro ao atualizar status PDF WhatsApp para edição {edicao}: {e}")

def enviar_pdf_whatsapp(rifa):
    """Envia PDF para WhatsApp apenas com texto simples"""
    edicao = rifa['edicao']
    sigla_oficial = rifa['sigla_oficial']
    link = rifa['link']
    pdf_path = rifa['pdf_path']
    
    logger.info(f"Iniciando envio do PDF para edição {edicao} - {sigla_oficial}")
    
    # 1. Primeiro enviar texto informativo (sem imagem)
    sucesso_texto = enviar_texto_simples(edicao, sigla_oficial, link)
    if not sucesso_texto:
        logger.error(f"Falha ao enviar texto informativo para edição {edicao}")
        return False
    
    # Pequena pausa entre envios
    time.sleep(2)
    
    # 2. Depois enviar o PDF
    sucesso_pdf = enviar_arquivo_pdf(edicao, sigla_oficial, pdf_path)
    if not sucesso_pdf:
        logger.error(f"Falha ao enviar PDF para edição {edicao}")
        return False
    
    logger.info(f"PDF enviado com sucesso para edição {edicao}")
    return True

def enviar_imagem_informativa(edicao, sigla_oficial, extracao, link):
    """Envia a imagem informativa da rifa"""
    caminho_imagem = buscar_imagem(extracao)
    if not caminho_imagem:
        logger.warning(f"Imagem {extracao} não encontrada, enviando apenas texto")
        return enviar_texto_simples(edicao, sigla_oficial, link)
    
    texto_msg = montar_texto_pdf(edicao, sigla_oficial, link)
    
    # Converter imagem para base64
    try:
        with open(caminho_imagem, "rb") as img_file:
            imagem_base64 = base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"Erro ao ler imagem {caminho_imagem}: {e}")
        return False
    
    # Montar o payload
    payload = {
        "number": id_grupo,
        "mediatype": "image",
        "mimetype": "image/jpeg",
        "caption": texto_msg,
        "media": imagem_base64,
        "fileName": os.path.basename(caminho_imagem),
    }
    
    # Cabeçalhos da requisição
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    # Enviar requisição
    try:
        response = requests.post(url_pdf, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            logger.info(f"Imagem informativa enviada com sucesso para edição {edicao}")
            return True
        else:
            logger.error(f"Falha ao enviar imagem para edição {edicao}. Status Code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar imagem para edição {edicao}: {e}")
        return False

def enviar_texto_simples(edicao, sigla_oficial, link):
    """Envia apenas texto quando não há imagem disponível"""
    texto_msg = montar_texto_pdf(edicao, sigla_oficial, link)
    
    payload = {
        "number": id_grupo,
        "text": texto_msg
    }
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    url_texto = "https://evolution-evolution.aras94.easypanel.host/message/sendText/bancada"
    
    try:
        response = requests.post(url_texto, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            logger.info(f"Texto informativo enviado com sucesso para edição {edicao}")
            return True
        else:
            logger.error(f"Falha ao enviar texto para edição {edicao}. Status Code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar texto para edição {edicao}: {e}")
        return False

def enviar_arquivo_pdf(edicao, sigla_oficial, pdf_path):
    """Envia o arquivo PDF"""
    
    # Converter PDF para base64
    try:
        with open(pdf_path, "rb") as pdf_file:
            pdf_base64 = base64.b64encode(pdf_file.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"Erro ao ler PDF {pdf_path}: {e}")
        return False
    
    # Nome do arquivo
    nome_arquivo = f"Relatório_{sigla_oficial}_{edicao}.pdf"
    
    # Montar o payload
    payload = {
        "number": id_grupo,
        "mediatype": "document",
        "mimetype": "application/pdf",
        "media": pdf_base64,
        "fileName": nome_arquivo,
    }
    
    # Cabeçalhos da requisição
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    # Enviar requisição
    try:
        response = requests.post(url_pdf, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            logger.info(f"PDF enviado com sucesso para edição {edicao}")
            return True
        else:
            logger.error(f"Falha ao enviar PDF para edição {edicao}. Status Code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar PDF para edição {edicao}: {e}")
        return False

def main():
    """Função principal do script"""
    logger.info("=== Iniciando Envio Automático de PDFs para WhatsApp ===")
    
    # Garantir que a coluna de status existe
    adicionar_coluna_status_pdf()
    
    # Buscar rifas com PDF disponível
    rifas_pendentes = buscar_rifas_com_pdf_pendente()
    
    if not rifas_pendentes:
        logger.info("Nenhuma rifa com PDF pendente para envio")
        return
    
    logger.info(f"Encontradas {len(rifas_pendentes)} rifas com PDF para enviar")
    
    envios_realizados = 0
    
    for rifa in rifas_pendentes:
        edicao = rifa['edicao']
        sigla_oficial = rifa['sigla_oficial']
        
        logger.info(f"\nProcessando edição {edicao} - {sigla_oficial}")
        
        try:
            # Marcar como enviando
            atualizar_status_envio_pdf(edicao, 'enviando')
            
            # Enviar PDF
            sucesso = enviar_pdf_whatsapp(rifa)
            
            if sucesso:
                # Marcar como enviado
                atualizar_status_envio_pdf(edicao, 'enviado')
                envios_realizados += 1
                logger.info(f"✅ PDF da edição {edicao} enviado com sucesso!")
            else:
                # Marcar como erro
                atualizar_status_envio_pdf(edicao, 'erro')
                logger.error(f"❌ Falha ao enviar PDF da edição {edicao}")
            
            # Pausa entre envios para não sobrecarregar a API
            if len(rifas_pendentes) > 1:
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"Erro inesperado ao processar edição {edicao}: {e}")
            atualizar_status_envio_pdf(edicao, 'erro')
    
    logger.info(f"\n=== RESUMO FINAL ===")
    logger.info(f"Total de PDFs processados: {len(rifas_pendentes)}")
    logger.info(f"PDFs enviados com sucesso: {envios_realizados}")
    logger.info(f"Falhas: {len(rifas_pendentes) - envios_realizados}")

if __name__ == "__main__":
    main() 