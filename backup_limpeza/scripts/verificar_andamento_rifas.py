#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar o andamento das rifas através dos links cadastrados
Atualiza a coluna 'andamento' na tabela extracoes_cadastro
Versão atualizada com controle de status_rifa
"""

import sys
import os
import time
import re
import logging
import requests
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
        logging.FileHandler(os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs/verificar_andamento.log')), encoding='utf-8'),
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
        chrome_options.add_argument('--headless')  # Executar em modo headless
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        logger.error(f"Erro ao criar driver: {e}")
        raise

def extrair_percentual_andamento(driver, link):
    """Extrai o percentual de andamento de uma rifa através do link"""
    try:
        logger.info(f"Acessando link: {link}")
        
        # Verificar se o link é válido
        if not link or not link.startswith('http'):
            logger.error(f"Link inválido: {link}")
            return "ERRO_LINK_INVALIDO"
        
        try:
            driver.get(link)
        except WebDriverException as e:
            logger.error(f"Erro ao acessar o link {link}: {e}")
            return "ERRO_ACESSO"
        
        # Aguardar a página carregar
        time.sleep(3)
        
        # Verificar se a página carregou corretamente (não é página de erro 404, 500, etc.)
        try:
            page_title = driver.title.lower()
            current_url = driver.current_url.lower()
            
            # Verificar título da página
            if "404" in page_title or "not found" in page_title or "erro" in page_title or "error" in page_title:
                logger.warning(f"Página de erro detectada no título para o link: {link}")
                return "ERRO_PAGINA_NAO_ENCONTRADA"
            
            # Verificar se foi redirecionado para página de erro
            if "404" in current_url or "error" in current_url or "not-found" in current_url:
                logger.warning(f"Redirecionamento para página de erro detectado: {current_url}")
                return "ERRO_PAGINA_NAO_ENCONTRADA"
            
            # Verificar se a página contém mensagens de erro comuns
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                error_messages = [
                    "página não encontrada",
                    "page not found", 
                    "404 error",
                    "não foi possível encontrar",
                    "campanha não encontrada",
                    "link inválido",
                    "expirado",
                    "indisponível"
                ]
                
                for error_msg in error_messages:
                    if error_msg in body_text:
                        logger.warning(f"Mensagem de erro encontrada na página: {error_msg}")
                        return "ERRO_PAGINA_NAO_ENCONTRADA"
            except:
                pass
                
        except:
            pass
        
        # Tentar encontrar o elemento usando o XPath fornecido
        xpath_andamento = "//*[@id='root']/div/div[1]/div[2]/div[3]/form/div[1]/div[1]/div/div"
        
        try:
            # Aguardar o elemento aparecer
            elemento = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, xpath_andamento))
            )
            
            texto_andamento = elemento.text.strip()
            logger.info(f"Texto encontrado no elemento: {texto_andamento}")
            
            # Extrair percentual usando regex
            match = re.search(r'(\d+)%', texto_andamento)
            if match:
                percentual = match.group(1) + '%'
                logger.info(f"Percentual extraído: {percentual}")
                return percentual
            else:
                logger.warning(f"Percentual não encontrado no texto: {texto_andamento}")
                # Se não encontrou percentual no texto, assumir 0%
                logger.info("Assumindo 0% quando percentual não encontrado no texto")
                return "0%"
                
        except TimeoutException:
            logger.warning(f"Elemento não encontrado usando XPath. Tentando seletores alternativos...")
            
            # Tentar seletores alternativos
            seletores_alternativos = [
                "div[class*='progress']",
                "div[class*='percent']",
                "div[class*='andamento']",
                "span[class*='progress']",
                "span[class*='percent']",
                ".progress-bar",
                ".percentage",
                "[data-testid*='progress']",
                "[data-testid*='percent']"
            ]
            
            for seletor in seletores_alternativos:
                try:
                    elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
                    for elemento in elementos:
                        texto = elemento.text.strip()
                        if re.search(r'\d+%', texto):
                            match = re.search(r'(\d+)%', texto)
                            if match:
                                percentual = match.group(1) + '%'
                                logger.info(f"Percentual encontrado com seletor alternativo {seletor}: {percentual}")
                                return percentual
                except:
                    continue
            
            # Se não encontrou com seletores, tentar buscar em todo o HTML
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                matches = re.findall(r'(\d+)%', body_text)
                if matches:
                    # Pegar o primeiro percentual encontrado que faça sentido (0-100)
                    for match in matches:
                        if 0 <= int(match) <= 100:
                            percentual = match + '%'
                            logger.info(f"Percentual encontrado no body: {percentual}")
                            return percentual
            except:
                pass
            
            logger.warning(f"Não foi possível encontrar o percentual de andamento para o link: {link}")
            # Se não encontrou nada, assumir 0% ao invés de erro
            logger.info("Assumindo 0% quando não foi possível encontrar percentual")
            return "0%"
            
    except Exception as e:
        logger.error(f"Erro geral ao extrair percentual do link {link}: {e}")
        return "ERRO_GERAL"

def buscar_links_para_verificar():
    """Busca todos os links da tabela extracoes_cadastro que precisam ser verificados"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Buscar apenas registros com status_rifa = 'ativo'
        query = """
        SELECT id, edicao, sigla_oficial, link, andamento, status_rifa
        FROM extracoes_cadastro 
        WHERE link IS NOT NULL 
        AND link != '' 
        AND link LIKE 'https://litoraldasorte.com%'
        AND status_rifa = 'ativo'
        ORDER BY edicao DESC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        links_para_verificar = []
        for resultado in resultados:
            # Detectar se o campo andamento está realmente vazio no banco
            andamento_banco = resultado[4]
            campo_vazio_no_banco = (andamento_banco is None or andamento_banco == '')
            
            links_para_verificar.append({
                'id': resultado[0],
                'edicao': resultado[1],
                'sigla_oficial': resultado[2],
                'link': resultado[3],
                'andamento_atual': andamento_banco if andamento_banco else '0%',
                'campo_vazio_no_banco': campo_vazio_no_banco,  # Flag para forçar atualização
                'status_rifa': resultado[5]
            })
        
        cursor.close()
        connection.close()
        
        logger.info(f"Encontrados {len(links_para_verificar)} links ATIVOS para verificar")
        return links_para_verificar
        
    except Exception as e:
        logger.error(f"Erro ao buscar links para verificar: {e}")
        return []

def notificar_dashboard_atualizado():
    """Notifica o dashboard que os dados foram atualizados"""
    try:
        # URL do endpoint no dashboard (assumindo que está rodando na porta 8001)
        dashboard_url = "http://localhost:8001/api/dashboard/notify-update"
        
        # Tentar notificar o dashboard
        response = requests.post(dashboard_url, timeout=5)
        
        if response.status_code == 200:
            logger.info("🔄 Dashboard notificado para atualização")
        else:
            logger.warning(f"⚠️ Dashboard respondeu com status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Dashboard não está acessível - sem notificação")
    except requests.exceptions.Timeout:
        logger.warning("⚠️ Timeout ao notificar dashboard")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao notificar dashboard: {e}")

def atualizar_andamento_e_status(registro_id, percentual):
    """Atualiza o percentual de andamento e status no banco de dados"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Determinar o novo status baseado no percentual
        if percentual.startswith("ERRO_"):
            # Se houve erro, marcar status como 'error'
            novo_status = 'error'
            percentual_para_salvar = None  # Não alterar o percentual em caso de erro
            query = "UPDATE extracoes_cadastro SET status_rifa = %s WHERE id = %s"
            cursor.execute(query, (novo_status, registro_id))
            logger.info(f"Status atualizado para 'error' no registro ID {registro_id}")
        elif percentual == "100%":
            # Se chegou a 100%, marcar como 'concluído'
            novo_status = 'concluído'
            query = "UPDATE extracoes_cadastro SET andamento = %s, status_rifa = %s WHERE id = %s"
            cursor.execute(query, (percentual, novo_status, registro_id))
            logger.info(f"Andamento atualizado para {percentual} e status para 'concluído' no registro ID {registro_id}")
        else:
            # Para outros percentuais (incluindo 0%), apenas atualizar andamento
            query = "UPDATE extracoes_cadastro SET andamento = %s WHERE id = %s"
            cursor.execute(query, (percentual, registro_id))
            logger.info(f"Andamento atualizado para {percentual} no registro ID {registro_id}")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao atualizar andamento/status no banco para ID {registro_id}: {e}")
        return False

def executar_envio_automatico_pdfs():
    """Executa o script de envio automático de PDFs para WhatsApp"""
    try:
        import subprocess
        import sys
        
        script_path = os.path.join(os.path.dirname(__file__), "envio_automatico_pdfs_whatsapp.py")
        
        if not os.path.exists(script_path):
            logger.warning("⚠️ Script de envio automático de PDFs não encontrado")
            return
        
        logger.info("🚀 Executando script de envio automático de PDFs...")
        
        # Executar o script em background para não bloquear
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300  # 5 minutos timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ Script de envio automático de PDFs executado com sucesso")
            # Log das principais linhas do output
            output_lines = result.stdout.split('\n')
            for line in output_lines[-10:]:  # Últimas 10 linhas
                if line.strip() and ('enviado' in line.lower() or 'pdf' in line.lower()):
                    logger.info(f"📄 {line.strip()}")
        else:
            logger.warning(f"⚠️ Script de envio automático retornou código {result.returncode}")
            if result.stderr:
                logger.warning(f"Erro: {result.stderr}")
                
    except subprocess.TimeoutExpired:
        logger.warning("⚠️ Timeout ao executar script de envio automático de PDFs")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao executar script de envio automático de PDFs: {e}")

def main():
    """Função principal do script"""
    logger.info("=== INICIANDO VERIFICAÇÃO DE ANDAMENTO DAS RIFAS (APENAS ATIVOS) ===")
    
    # Buscar links para verificar
    links = buscar_links_para_verificar()
    if not links:
        logger.info("Nenhum link ATIVO encontrado para verificar")
        return
    
    # Criar driver do Chrome
    driver = None
    try:
        driver = criar_driver()
        logger.info("Driver do Chrome criado com sucesso")
        
        sucessos = 0
        erros = 0
        concluidos = 0
        atualizados = 0
        
        for i, link_info in enumerate(links, 1):
            logger.info(f"\n--- Processando {i}/{len(links)} ---")
            logger.info(f"Edição: {link_info['edicao']}")
            logger.info(f"Sigla: {link_info['sigla_oficial']}")
            logger.info(f"Andamento atual: {link_info['andamento_atual']}")
            logger.info(f"Status atual: {link_info['status_rifa']}")
            
            # Extrair percentual
            percentual = extrair_percentual_andamento(driver, link_info['link'])
            
            # Verificar se houve erro
            if isinstance(percentual, str) and percentual.startswith("ERRO_"):
                logger.warning(f"⚠️ Erro detectado: {percentual}")
                if atualizar_andamento_e_status(link_info['id'], percentual):
                    logger.warning(f"❌ Status marcado como 'error' devido a: {percentual}")
                    erros += 1
                else:
                    logger.error(f"❌ Erro ao marcar status como 'error' no banco")
                
                # Pausa menor para links com erro
                time.sleep(1)
                continue
            
            # Se chegou aqui, temos um percentual válido (incluindo 0%)
            if percentual:
                # Verificar se precisa atualizar percentual OU se precisa marcar como concluído
                precisa_atualizar = (percentual != link_info['andamento_atual'])
                precisa_concluir = (percentual == "100%" and link_info['status_rifa'] == 'ativo')
                precisa_preencher_vazio = link_info['campo_vazio_no_banco']  # Forçar quando campo estava vazio
                
                if precisa_atualizar or precisa_concluir or precisa_preencher_vazio:
                    if atualizar_andamento_e_status(link_info['id'], percentual):
                        if percentual == "100%" and link_info['status_rifa'] == 'ativo':
                            logger.info(f"🏆 Rifa CONCLUÍDA: {link_info['andamento_atual']} → {percentual}")
                            concluidos += 1
                        elif precisa_preencher_vazio:
                            logger.info(f"📝 Campo vazio preenchido: VAZIO → {percentual}")
                            atualizados += 1
                        elif precisa_atualizar:
                            logger.info(f"✅ Andamento atualizado: {link_info['andamento_atual']} → {percentual}")
                            atualizados += 1
                        else:
                            logger.info(f"🏆 Status alterado para CONCLUÍDO (100%)")
                            concluidos += 1
                        sucessos += 1
                    else:
                        logger.error(f"❌ Erro ao atualizar andamento/status no banco")
                        erros += 1
                else:
                    logger.info(f"ℹ️ Andamento não mudou: {percentual}")
                    sucessos += 1
            else:
                logger.error(f"❌ Não foi possível extrair o percentual")
                erros += 1
            
            # Pausa entre requisições para não sobrecarregar o servidor
            time.sleep(2)
        
        logger.info(f"\n=== RESUMO FINAL ===")
        logger.info(f"Total de links ATIVOS: {len(links)}")
        logger.info(f"Sucessos: {sucessos}")
        logger.info(f"Erros: {erros}")
        logger.info(f"Rifas concluídas (100%): {concluidos}")
        logger.info(f"Andamentos atualizados: {atualizados}")
        logger.info(f"Processados efetivamente: {sucessos + erros}")
        
        # NOVA FUNCIONALIDADE: Notificar o dashboard para atualização
        if atualizados > 0 or concluidos > 0:
            logger.info(f"📡 Notificando dashboard sobre {atualizados + concluidos} atualizações...")
            notificar_dashboard_atualizado()
        else:
            logger.info("ℹ️ Nenhuma atualização realizada - dashboard não notificado")
        
        # NOVA FUNCIONALIDADE: Executar envio automático de PDFs quando há rifas concluídas
        if concluidos > 0:
            logger.info(f"📄 {concluidos} rifa(s) concluída(s)! Verificando envio automático de PDFs...")
            executar_envio_automatico_pdfs()
        
    except Exception as e:
        logger.error(f"Erro na execução principal: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Driver do Chrome encerrado")
            except:
                pass

if __name__ == "__main__":
    main() 