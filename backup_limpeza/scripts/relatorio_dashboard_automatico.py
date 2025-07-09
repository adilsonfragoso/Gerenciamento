from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import unidecode
import os
import pandas as pd
import pdfkit
from datetime import datetime
import sys
import subprocess
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# ===================== CONFIGURAÇÃO OTIMIZADA PARA VELOCIDADE =====================
# SEMPRE headless para máxima velocidade
HEADLESS = True

driver_path = r"D:\Documentos\Workspace\chromedriver.exe"
service = Service(driver_path)

chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-images')  # Não carregar imagens para velocidade
chrome_options.add_argument('--disable-javascript')  # Desabilitar JS desnecessário
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-logging')
chrome_options.add_argument('--silent')

# Configurar downloads
prefs = {
    "download.default_directory": r"D:\Adilson\Downloads",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

navegador = webdriver.Chrome(service=service, options=chrome_options)
navegador.set_page_load_timeout(30)  # Timeout de 30s para carregamento

# Caminho para a pasta de downloads
caminho_downloads = r"D:\Adilson\Downloads"

# Defina a edição para conversão (recebida via argumento)
if len(sys.argv) < 2:
    print("ERRO: Edição não fornecida como argumento")
    sys.exit(1)

edicao_converter = sys.argv[1]
print(f"[DASHBOARD AUTO] Iniciando geração de relatório para edição {edicao_converter}")

try:
    # Abre o site
    print("[DASHBOARD AUTO] Acessando painel...")
    navegador.get("https://painel.litoraldasorte.com")
    sleep(1)  # Reduzido de 2 para 1

    # Desativa prompt de impressão do Windows
    navegador.execute_script("window.print = function(){};")

    # Fazer login
    print("[DASHBOARD AUTO] Fazendo login...")
    login = 'relatoriodash'
    senha = 'Define@4536#8521'
    navegador.find_element(By.NAME, "email").send_keys(login)
    navegador.find_element(By.NAME, "password").send_keys(senha)
    navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    sleep(2)  # Reduzido de 4 para 2

    # Função para fechar popup "Entendi" (mais rápida)
    def fechar_popup_rapido(navegador):
        try:
            btn = WebDriverWait(navegador, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Entendi']"))
            )
            btn.click()
            print("[DASHBOARD AUTO] Pop-up fechado")
        except TimeoutException:
            print("[DASHBOARD AUTO] Nenhum pop-up para fechar")

    # Fecha popup e aguarda menos
    fechar_popup_rapido(navegador)
    sleep(1)  # Reduzido de 2 para 1

    # Acessar o menu sorteios
    print("[DASHBOARD AUTO] Acessando menu sorteios...")
    menu_sorteios = navegador.find_element(
        By.XPATH,
        '//*[@id="root"]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/div[2]/ul[1]/div[2]/div[2]/span'
    )
    menu_sorteios.click()
    sleep(3)  # Reduzido de 6 para 3

    # Buscar rifa por edição
    print(f"[DASHBOARD AUTO] Buscando edição {edicao_converter}...")
    campo_busca_edicao = navegador.find_element(
        By.XPATH, 
        "//input[@placeholder='Pesquisar por título do sorteio...']"
    )
    campo_busca_edicao.click()
    campo_busca_edicao.clear()
    campo_busca_edicao.send_keys(edicao_converter)
    sleep(2)  # Reduzido de 5 para 2

    # Clica no carrinho de compras
    print("[DASHBOARD AUTO] Acessando relatório de vendas...")
    botao_compras = navegador.find_element(By.XPATH, "//button[@aria-label='Compras']")
    botao_compras.click()
    sleep(2)  # Reduzido de 3 para 2

    # Navegação por teclado para selecionar opção (mais rápida)
    actions = ActionChains(navegador)
    for _ in range(6):
        actions.send_keys(Keys.TAB).pause(0.2)  # Reduzido de 0.5 para 0.2
    actions.send_keys(Keys.ENTER)
    actions.perform()
    sleep(2)  # Reduzido de 3 para 2

    # Selecionar "Relatório de Vendas"
    try:
        WebDriverWait(navegador, 8).until(  # Reduzido de 10 para 8
            EC.visibility_of_element_located((By.XPATH, "//div[@class='css-j7qwjs']"))
        )
        relatorio_vendas = WebDriverWait(navegador, 8).until(
            EC.element_to_be_clickable((By.XPATH, "//li//div[contains(text(), 'Relatório de Vendas')]"))
        )
        relatorio_vendas.click()
        print("[DASHBOARD AUTO] Relatório de vendas selecionado")
        sleep(1)  # Reduzido de 2 para 1
    except Exception as e:
        print(f"[DASHBOARD AUTO] ERRO ao acessar relatório: {e}")
        raise

    # Obter título da página e montar nome de arquivo
    print("[DASHBOARD AUTO] Obtendo título e preparando download...")
    try:
        titulo_elemento = navegador.find_element(
            By.XPATH,
            '//*[@id="root"]/div/main/div/div/div[2]/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div[1]/div/div[1]/div/h4'
        )
        titulo_original = titulo_elemento.text
        titulo_modificado = unidecode.unidecode(titulo_original.lower().replace(" ", "-"))
        nome_arquivo = f"relatorio-vendas-{titulo_modificado}.csv"
        print(f"[DASHBOARD AUTO] Arquivo esperado: {nome_arquivo}")
    except Exception as e:
        print(f"[DASHBOARD AUTO] ERRO ao obter título: {e}")
        raise

    # Esperar download do CSV (mais eficiente)
    caminho_arquivo = os.path.join(caminho_downloads, nome_arquivo)
    max_espera = 15  # Aumentado para 15s para segurança
    csv_encontrado = False

    print("[DASHBOARD AUTO] Aguardando download do CSV...")
    for i in range(max_espera):
        if os.path.exists(caminho_arquivo):
            # Verificar se o arquivo não está vazio e foi completamente baixado
            if os.path.getsize(caminho_arquivo) > 0:
                csv_encontrado = True
                print(f"[DASHBOARD AUTO] CSV encontrado após {i} segundo(s)")
                break
        sleep(1)

    if not csv_encontrado:
        print(f"[DASHBOARD AUTO] ERRO: CSV não encontrado após {max_espera}s")
        navegador.quit()
        sys.exit(1)

    # Configurar wkhtmltopdf
    caminho_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=caminho_wkhtmltopdf)

    # Função de criptografia de telefone
    def criptografar_telefone(telefone):
        if len(telefone) == 15:  
            return telefone[:7] + "***-**" + telefone[-2:]
        return telefone

    # Processar CSV e gerar PDF
    print("[DASHBOARD AUTO] Processando dados e gerando PDF...")
    
    # Ler CSV e processar
    df = pd.read_csv(caminho_arquivo, sep=";", encoding="utf-8")
    colunas_desejadas = [6, 7, 20]
    df = df.iloc[:, colunas_desejadas]
    df.columns = ['Nome', 'Telefone', 'Números adquiridos']
    df = df.sort_values(by='Nome')
    df['Telefone'] = df['Telefone'].apply(criptografar_telefone)

    # Gerar HTML para PDF (otimizado)
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ text-align: center; margin-bottom: 20px; color: #333; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #ddd; text-align: left; padding: 8px; font-size: 12px; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 10px; color: #666; }}
        </style>
    </head>
    <body>
        <h1>{titulo_original}</h1>
        {df.to_html(index=False, border=0, escape=False)}
        <div class="footer">
            Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}
        </div>
    </body>
    </html>
    """
    
    caminho_html = os.path.join(caminho_downloads, f"relatorio_temp_{edicao_converter}.html")
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Gerar PDF com configurações otimizadas
    caminho_pdf = caminho_arquivo.replace(".csv", ".pdf")
    
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'quiet': ''  # Silenciar saída do wkhtmltopdf
    }
    
    pdfkit.from_file(caminho_html, caminho_pdf, options=options, configuration=config)
    print(f"[DASHBOARD AUTO] PDF gerado: {caminho_pdf}")
    
    # Limpar arquivo temporário
    os.remove(caminho_html)

    # Tentar chamar inserir_no_bd.py (não crítico se falhar)
    try:
        print(f"[DASHBOARD AUTO] Enviando dados ao banco...")
        subprocess.run(
            ["python", "D:/Documentos/Workspace/inserir_no_bd.py", edicao_converter, caminho_arquivo],
            check=True,
            timeout=30  # Timeout de 30s
        )
        print("[DASHBOARD AUTO] Dados enviados ao banco com sucesso!")
    except Exception as e:
        print(f"[DASHBOARD AUTO] Aviso: Falha ao enviar ao banco: {e}")

    # Remover CSV
    if os.path.exists(caminho_arquivo):
        os.remove(caminho_arquivo)
        print(f"[DASHBOARD AUTO] CSV removido")

    print(f"[DASHBOARD AUTO] ✅ Relatório concluído com sucesso!")
    print(f"[DASHBOARD AUTO] Arquivo: {os.path.basename(caminho_pdf)}")

except Exception as e:
    print(f"[DASHBOARD AUTO] ❌ ERRO GERAL: {e}")
    sys.exit(1)
finally:
    # Sempre fechar navegador
    try:
        navegador.quit()
    except:
        pass

# Imprimir caminho do PDF (para o sistema)
print(os.path.join(caminho_downloads, nome_arquivo.replace(".csv", ".pdf"))) 