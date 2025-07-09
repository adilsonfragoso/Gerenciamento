from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import unidecode
import os
import sys
import mysql.connector
from datetime import datetime

# ===================== CONFIGURAÇÃO =====================
HEADLESS = False  # False para debug, True para produção
driver_path = r"D:\Documentos\Workspace\chromedriver.exe"
service = Service(driver_path)

# Configuração do banco de dados
DB_CONFIG = {
    'host': 'pma.megatrends.site',
    'user': 'root',
    'password': 'Define@4536#8521',
    'database': 'teste',
    'charset': 'utf8mb4',
}

def conectar_banco():
    """Conecta ao banco de dados MySQL"""
    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        return conexao
    except mysql.connector.Error as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        return None

def buscar_edicoes_para_extrair():
    """Busca edições que não têm extração (coluna Extracao vazia)"""
    conexao = conectar_banco()
    if not conexao:
        return []
    
    try:
        cursor = conexao.cursor()
        query = "SELECT edicao FROM relatorios_importados WHERE Extracao IS NULL OR Extracao = '' ORDER BY edicao"
        cursor.execute(query)
        edicoes = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conexao.close()
        return edicoes
    except mysql.connector.Error as e:
        print(f"❌ Erro ao buscar edições: {e}")
        return []

def converter_data_mysql(data_hora_str):
    """Converte data/hora do formato '25/06/2025 09:20:00' para formato MySQL '2025-06-25 09:20:00'"""
    try:
        # Parse da data no formato brasileiro
        dt = datetime.strptime(data_hora_str, "%d/%m/%Y %H:%M:%S")
        # Retorna no formato MySQL
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"⚠️ Erro ao converter data '{data_hora_str}': {e}")
        return None

def atualizar_extracao_banco(edicao, sigla, data_mysql):
    """Atualiza a extração no banco de dados"""
    conexao = conectar_banco()
    if not conexao:
        return False
    
    try:
        cursor = conexao.cursor()
        query = "UPDATE relatorios_importados SET Extracao = %s, data = %s WHERE edicao = %s"
        cursor.execute(query, (sigla, data_mysql, edicao))
        conexao.commit()
        cursor.close()
        conexao.close()
        print(f"✅ Banco atualizado - Edição: {edicao}, Sigla: {sigla}, Data: {data_mysql}")
        return True
    except mysql.connector.Error as e:
        print(f"❌ Erro ao atualizar banco: {e}")
        return False

def criar_navegador():
    if HEADLESS:
        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--window-size=1920,1080')
        return webdriver.Chrome(service=service, options=opts)
    else:
        return webdriver.Chrome(service=service)

def fazer_login(navegador):
    print("🔐 Fazendo login...")
    navegador.get("https://painel.litoraldasorte.com")
    sleep(2)
    navegador.execute_script("window.print = function(){};")
    navegador.find_element(By.NAME, "email").send_keys("Dev2")
    navegador.find_element(By.NAME, "password").send_keys("453629")
    navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    sleep(3)
    print("✅ Login realizado")

def fechar_popup(navegador):
    try:
        btn = WebDriverWait(navegador, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Entendi']"))
        )
        btn.click()
        WebDriverWait(navegador, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.MuiDialog-container"))
        )
        print("✅ Pop-up fechado")
    except TimeoutException:
        pass

def limpar_overlays(navegador):
    """Remove overlays que bloqueiam cliques"""
    try:
        # Pressionar ESC para fechar modais
        body = navegador.find_element(By.TAG_NAME, "body")
        for _ in range(3):
            body.send_keys(Keys.ESCAPE)
            sleep(0.3)
        
        # Remover backdrops via JavaScript
        navegador.execute_script("""
            document.querySelectorAll('div.MuiBackdrop-root').forEach(backdrop => {
                if (backdrop.style.opacity !== '0') {
                    backdrop.remove();
                }
            });
        """)
        
        sleep(1)
        print("🧹 Overlays removidos")
        
    except Exception as e:
        print(f"⚠️ Aviso limpeza: {e}")

def limpar_campo_busca(navegador):
    """Limpa completamente o campo de busca"""
    try:
        campo = navegador.find_element(By.XPATH, "//input[@placeholder='Pesquisar por título do sorteio...']")
        campo.click()
        sleep(0.3)
        
        # Selecionar tudo e deletar
        campo.send_keys(Keys.CONTROL + "a")
        sleep(0.2)
        campo.send_keys(Keys.DELETE)
        sleep(0.2)
        
        # Garantir que está vazio via JavaScript
        navegador.execute_script("arguments[0].value = '';", campo)
        navegador.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", campo)
        
        print("🧹 Campo de busca limpo")
        return True
        
    except Exception as e:
        print(f"⚠️ Erro ao limpar campo: {e}")
        return False

def navegar_para_sorteios(navegador):
    try:
        # Limpar qualquer overlay
        limpar_overlays(navegador)
        
        # Tentar clicar no menu sorteios
        menu_xpath = '//*[@id="root"]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/div[2]/ul[1]/div[2]/div[2]/span'
        
        # Aguardar elemento estar clicável
        menu = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, menu_xpath))
        )
        
        # Usar JavaScript para garantir o clique
        navegador.execute_script("arguments[0].scrollIntoView(true);", menu)
        sleep(1)
        navegador.execute_script("arguments[0].click();", menu)
        sleep(2)
        
        # Limpar campo de busca após navegar
        limpar_campo_busca(navegador)
        
        print("📋 Navegando para sorteios...")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao navegar para sorteios: {e}")
        return False

def extrair_sigla(texto_titulo):
    """Extrai a sigla do título conforme as regras especificadas"""
    try:
        if "RJ" in texto_titulo:
            # Extrair o que está antes de "RJ"
            sigla = texto_titulo.split("RJ")[0].strip()
        elif "EDIÇÃO" in texto_titulo:
            # Extrair o que está antes de "EDIÇÃO"
            sigla = texto_titulo.split("EDIÇÃO")[0].strip()
        else:
            # Fallback - retorna o título inteiro
            sigla = texto_titulo.strip()
            
        return sigla
    except Exception as e:
        print(f"⚠️ Erro ao extrair sigla: {e}")
        return None

def digitar_edicao_e_extrair_dados(navegador, edicao):
    """Digita a edição no campo de busca, extrai os dados e atualiza o banco"""
    print(f"\n🚀 Processando edição: {edicao}")
    
    try:
        # Garantir que campo está limpo antes de digitar
        limpar_campo_busca(navegador)
        sleep(1)
        
        campo = navegador.find_element(By.XPATH, "//input[@placeholder='Pesquisar por título do sorteio...']")
        campo.click()
        sleep(0.5)
        campo.send_keys(str(edicao))
        sleep(2)  # Aguardar mais tempo para carregar os resultados
        print(f"🔍 Digitado: {edicao}")
        
        # Verificar se carregou algum resultado
        try:
            # Aguardar os elementos carregarem
            WebDriverWait(navegador, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='root']/div/main/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[1]/td/div/div[1]/div/p"))
            )
            
            # Extrair título (sigla)
            titulo_element = navegador.find_element(By.XPATH, "//*[@id='root']/div/main/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[1]/td/div/div[1]/div/p")
            texto_titulo = titulo_element.text
            sigla = extrair_sigla(texto_titulo)
            
            # Extrair data/hora
            data_element = navegador.find_element(By.XPATH, "//*[@id='root']/div/main/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[1]/td/div/div[1]/div/span")
            texto_data = data_element.text
            
            # Extrair apenas a data/hora (depois de "Sorteio:")
            if "Sorteio:" in texto_data:
                data_hora = texto_data.split("Sorteio:")[1].strip()
            else:
                data_hora = texto_data.strip()
            
            # Converter data para formato MySQL
            data_mysql = converter_data_mysql(data_hora)
            
            # Exibir resultados
            print(f"\n📊 RESULTADOS DA EDIÇÃO {edicao}:")
            print(f"📋 Título completo: {texto_titulo}")
            print(f"🏷️ Sigla extraída: {sigla}")
            print(f"📅 Data/Hora original: {data_hora}")
            print(f"🗄️ Data MySQL: {data_mysql}")
            print(f"📄 Texto span completo: {texto_data}")
            
            # Atualizar banco de dados
            if sigla and data_mysql:
                sucesso_banco = atualizar_extracao_banco(edicao, sigla, data_mysql)
                if sucesso_banco:
                    print(f"✅ Dados salvos no banco para edição {edicao}")
                else:
                    print(f"❌ Erro ao salvar no banco para edição {edicao}")
                    return False
            else:
                print(f"❌ Dados incompletos para edição {edicao} - não salvando no banco")
                return False
            
            return True
            
        except TimeoutException:
            print(f"❌ Nenhum resultado encontrado para a edição {edicao}")
            return False
        except NoSuchElementException:
            print(f"❌ Elementos não encontrados para a edição {edicao}")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao processar edição {edicao}: {e}")
        return False

def main():
    print("🔍 Buscando edições para extrair dados...")
    
    # Buscar edições que precisam de extração
    edicoes_para_extrair = buscar_edicoes_para_extrair()
    
    if not edicoes_para_extrair:
        print("✅ Nenhuma edição pendente de extração encontrada!")
        return
    
    print(f"📋 Encontradas {len(edicoes_para_extrair)} edições para processar:")
    print(f"🎯 Edições: {edicoes_para_extrair}")
    
    # Confirmar processamento
    resposta = input(f"\n🤔 Deseja processar {len(edicoes_para_extrair)} edições? (s/n): ")
    if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
        print("❌ Processamento cancelado pelo usuário")
        return
    
    navegador = criar_navegador()
    
    try:
        # Login único
        fazer_login(navegador)
        fechar_popup(navegador)
        sleep(2)
        
        # Ir para sorteios
        if not navegar_para_sorteios(navegador):
            print("❌ Falha inicial sorteios")
            return
        
        sucessos = falhas = 0
        
        # Loop das edições
        for i, edicao in enumerate(edicoes_para_extrair, 1):
            print(f"\n📊 Progresso: {i}/{len(edicoes_para_extrair)}")
            try:
                resultado = digitar_edicao_e_extrair_dados(navegador, edicao)
                
                if resultado:
                    sucessos += 1
                    print(f"✅ Sucesso: {edicao}")
                else:
                    falhas += 1
                    print(f"❌ Falha: {edicao}")
                
                # Voltar para sorteios (exceto última)
                if i < len(edicoes_para_extrair):
                    print("🔄 Voltando sorteios...")
                    if not navegar_para_sorteios(navegador):
                        print("❌ Falha voltar sorteios")
                        break
                        
            except Exception as e:
                falhas += 1
                print(f"❌ Erro {edicao}: {e}")
        
        # Resultado
        print(f"\n🎉 Processamento concluído!")
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {falhas}")
        print(f"📊 Total: {sucessos + falhas}/{len(edicoes_para_extrair)}")
        
        # Verificar se restaram edições pendentes
        edicoes_restantes = buscar_edicoes_para_extrair()
        if edicoes_restantes:
            print(f"⚠️ Ainda restam {len(edicoes_restantes)} edições pendentes")
        else:
            print("🎊 Todas as edições foram processadas!")
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
    finally:
        print("🔒 Fechando navegador...")
        navegador.quit()

if __name__ == "__main__":
    main() 