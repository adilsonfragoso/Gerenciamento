#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script dedicado para recuperar rifas com erro
Executa APENAS a verificação de rifas com status_rifa = 'error'
"""

import sys
import os
import time
import re
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import pymysql

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs/recuperar_erro.log')), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Importar configurações centralizadas
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from db_config import DB_CONFIG

def criar_driver():
    """Cria e configura o driver do Chrome"""
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        logger.error(f"Erro ao criar driver: {e}")
        raise

def verificar_link_funciona(driver, link):
    """Verifica se um link está funcionando"""
    try:
        logger.info(f"🔗 Verificando link: {link}")
        
        # Acessar o link
        driver.get(link)
        time.sleep(3)
        
        # Verificar título da página
        title = driver.title.lower()
        current_url = driver.current_url.lower()
        
        # Verificar se é página de erro
        if any(erro in title for erro in ["404", "not found", "erro", "error"]):
            logger.warning(f"❌ Página de erro detectada no título: {driver.title}")
            return False
            
        if any(erro in current_url for erro in ["404", "error", "not-found"]):
            logger.warning(f"❌ URL de erro detectada: {driver.current_url}")
            return False
        
        # Tentar encontrar o elemento de percentual
        xpath_andamento = "//*[@id='root']/div/div[1]/div[2]/div[3]/form/div[1]/div[1]/div/div"
        
        try:
            elemento = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath_andamento))
            )
            texto = elemento.text.strip()
            logger.info(f"✅ Elemento encontrado com texto: '{texto}'")
            
            # Se encontrou o elemento, o link funciona
            match = re.search(r'(\d+)%', texto)
            if match:
                percentual = match.group(1) + '%'
                logger.info(f"✅ Link funcionando! Percentual: {percentual}")
                return percentual
            else:
                logger.info(f"✅ Link funcionando! Assumindo 0%")
                return "0%"
                
        except TimeoutException:
            # Tentar encontrar indicadores de que a página carregou
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                
                # Se tem conteúdo relacionado a rifas, provavelmente funciona
                if any(palavra in body_text for palavra in ["rifa", "sorteio", "campanha", "prêmio"]):
                    logger.info("✅ Link parece funcionar (conteúdo de rifa encontrado)")
                    return "0%"
                else:
                    logger.warning("❌ Link não parece ter conteúdo de rifa")
                    return False
            except:
                logger.warning("❌ Não foi possível verificar o conteúdo da página")
                return False
                
    except WebDriverException as e:
        logger.error(f"❌ Erro ao acessar link: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False

def recuperar_rifa(rifa_id, percentual):
    """Atualiza o status de uma rifa de 'error' para 'ativo'"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['db'],
            charset=DB_CONFIG['charset']
        )
        cursor = connection.cursor()
        
        # SEMPRE atualizar para ativo quando o link funciona
        query = """
        UPDATE extracoes_cadastro 
        SET status_rifa = 'ativo', 
            andamento = %s
        WHERE id = %s
        """
        
        cursor.execute(query, (percentual, rifa_id))
        connection.commit()
        
        linhas_afetadas = cursor.rowcount
        cursor.close()
        connection.close()
        
        if linhas_afetadas > 0:
            logger.info(f"✅ Rifa ID {rifa_id} RECUPERADA! Status: error → ativo, Andamento: {percentual}")
            return True
        else:
            logger.warning(f"⚠️ Nenhuma linha afetada ao tentar recuperar rifa ID {rifa_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao recuperar rifa no banco: {e}")
        return False

def buscar_rifas_com_erro():
    """Busca todas as rifas com status_rifa = 'error'"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['db'],
            charset=DB_CONFIG['charset']
        )
        cursor = connection.cursor()
        
        query = """
        SELECT id, edicao, sigla_oficial, link, andamento
        FROM extracoes_cadastro 
        WHERE status_rifa = 'error'
        AND link IS NOT NULL 
        AND link != ''
        ORDER BY edicao DESC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        logger.info(f"📊 Encontradas {len(resultados)} rifas com erro")
        return resultados
        
    except Exception as e:
        logger.error(f"Erro ao buscar rifas com erro: {e}")
        return []

def main():
    """Função principal - recupera rifas com erro"""
    logger.info("="*60)
    logger.info("🚀 INICIANDO RECUPERAÇÃO DE RIFAS COM ERRO")
    logger.info("="*60)
    
    # Buscar rifas com erro
    rifas_erro = buscar_rifas_com_erro()
    
    if not rifas_erro:
        logger.info("✅ Nenhuma rifa com erro encontrada!")
        return
    
    # Criar driver
    driver = None
    recuperadas = 0
    falhas = 0
    
    try:
        driver = criar_driver()
        logger.info("🌐 Driver do Chrome criado com sucesso")
        
        for rifa in rifas_erro:
            rifa_id, edicao, sigla, link, andamento_atual = rifa
            
            logger.info(f"\n{'='*40}")
            logger.info(f"📍 Verificando: {sigla} (Edição {edicao})")
            logger.info(f"   ID: {rifa_id}")
            logger.info(f"   Andamento atual: {andamento_atual}")
            
            # Verificar se o link funciona
            resultado = verificar_link_funciona(driver, link)
            
            if resultado:  # Se retornou um percentual, o link funciona
                # Recuperar a rifa
                if recuperar_rifa(rifa_id, resultado):
                    recuperadas += 1
                    logger.info(f"🎉 SUCESSO: {sigla} foi recuperada!")
                else:
                    falhas += 1
                    logger.error(f"❌ FALHA: Não foi possível recuperar {sigla}")
            else:
                logger.warning(f"⚠️ Link ainda com problema: {sigla}")
                falhas += 1
            
            # Pausa entre verificações
            time.sleep(2)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 RESUMO FINAL:")
        logger.info(f"   Total verificadas: {len(rifas_erro)}")
        logger.info(f"   ✅ Recuperadas: {recuperadas}")
        logger.info(f"   ❌ Ainda com erro: {falhas}")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Erro na execução: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("🔒 Driver encerrado")
            except:
                pass

if __name__ == "__main__":
    main() 