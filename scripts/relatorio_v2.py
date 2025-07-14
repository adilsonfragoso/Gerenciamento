# -------------------------------------------------------------
# relatorio_v3.py
#
# Script automatizado para baixar relatórios de vendas do painel
# Litoral da Sorte, processar cada edição de sorteio, gerar PDF 
# e inserir os dados diretamente no banco de dados.
# 
# Versão avançada com detecção robusta de arquivos e inserção
# integrada no banco de dados.
# -------------------------------------------------------------
#
# 📋 RELEASE NOTES - RELATORIO V3.0
# Melhorias implementadas em relação ao relatorio_v2.py:
#
# 🚀 VERSÃO 3.0 - DETECÇÃO ROBUSTA E INSERÇÃO INTEGRADA
# ═══════════════════════════════════════════════════════════
#
# ✅ DETECÇÃO ROBUSTA DE ARQUIVOS:
#    • Solução para problema de divergência de nomes de arquivo
#    • Busca alternativa por padrão e timestamp recente  
#    • Múltiplos seletores para captura de título
#    • Diagnóstico avançado com listagem de arquivos encontrados
#    • Timeout aumentado para 15 segundos
#
# ✅ INSERÇÃO INTEGRADA NO BANCO:
#    • Lógica de inserção acoplada no mesmo script
#    • Baseada na estrutura robusta do alimenta_relatorios_vendas.py
#    • Eliminação da dependência do inserir_no_bd.py
#    • Controle direto sobre transações do banco
#    • Validação de duplicatas integrada
#
# ✅ SISTEMA DE LOGS APRIMORADO:
#    • Log específico: scripts/logs/relatorio_v3.log
#    • Log de erros centralizados: scripts/logs/logs_geral.log  
#    • Padrão consistente com formato existente
#    • Rastreamento detalhado de cada etapa
#    • Origem do log claramente identificada
#
# ✅ PROCESSAMENTO DE DADOS MELHORADO:
#    • Separação de data e hora (campos data e horacompra)
#    • Ordenação por horadata crescente
#    • Cálculo de valor_cota automatizado
#    • Mapeamento completo de colunas CSV
#    • Tratamento robusto de tipos de dados
#
# ✅ MANUTENIBILIDADE:
#    • Código modularizado em funções específicas
#    • Seção destacada para inserção no banco
#    • Comentários detalhados em português
#    • Estrutura preparada para expansão futura
#    • Release notes no topo do arquivo
#
# 🔧 CORREÇÕES E MELHORIAS:
#    • Problema de divergência de nomes resolvido
#    • Detecção de downloads mais confiável
#    • Eliminação de dependências externas
#    • Performance otimizada
#    • Logs com encoding UTF-8 correto
#
# 📊 RESULTADO: Script completamente autossuficiente e robusto
# -------------------------------------------------------------

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
import sys
import glob
import mysql.connector
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Importar configuração do banco
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db_config import DB_CONFIG

# =============================================================================
# Configurações de Login (seguindo padrão MIGRACAO_ENV_CONSOLIDADO)
# =============================================================================
LOGIN_CONFIG = {
    "url": os.getenv("LOGIN_URL", "https://painel.litoraldasorte.com"),
    "email": os.getenv("LOGIN_EMAIL"),
    "password": os.getenv("LOGIN_PASSWORD")
}

# -------------------- CONFIGURAÇÃO DE LOGS --------------------
def configurar_logs(edicao):
    """Configura sistema de logs específico e geral"""
    # Log detalhado para relatorio_v3.log
    log_detalhado = logging.getLogger('relatorio_v3')
    log_detalhado.setLevel(logging.DEBUG)
    
    # Handler para arquivo de log detalhado
    handler_detalhado = logging.FileHandler(
        f'D:/Documentos/Workspace/Gerenciamento/scripts/logs/relatorio_v3.log', 
        encoding='utf-8'
    )
    formatter_detalhado = logging.Formatter(
        '%(asctime)s - [EDICAO {}] - %(levelname)s - %(message)s'.format(edicao)
    )
    handler_detalhado.setFormatter(formatter_detalhado)
    log_detalhado.addHandler(handler_detalhado)
    
    # Log geral apenas para erros (seguindo padrão existente)
    log_geral = logging.getLogger('logs_geral')
    log_geral.setLevel(logging.ERROR)
    
    # Handler para arquivo de log geral (apenas erros)
    handler_geral = logging.FileHandler(
        f'D:/Documentos/Workspace/Gerenciamento/scripts/logs/logs_geral.log', 
        encoding='utf-8'
    )
    formatter_geral = logging.Formatter(
        '%(asctime)s - [RELATORIO_V3] - [EDICAO {}] - ERROR - %(message)s'.format(edicao)
    )
    handler_geral.setFormatter(formatter_geral)
    log_geral.addHandler(handler_geral)
    
    return log_detalhado, log_geral

def log_info(mensagem):
    """Log de informação (console + arquivo detalhado)"""
    print(mensagem)
    logger_detalhado.info(mensagem)

def log_error(mensagem):
    """Log de erro (console + arquivo detalhado + arquivo geral)"""
    print(f"ERRO: {mensagem}")
    logger_detalhado.error(mensagem)
    logger_geral.error(mensagem)

def log_warning(mensagem):
    """Log de aviso (console + arquivo detalhado)"""
    print(f"AVISO: {mensagem}")
    logger_detalhado.warning(mensagem)

# -------------------- VALIDAÇÃO DE PARÂMETROS --------------------
if len(sys.argv) != 2:
    print("Uso: python relatorio_v3.py <numero_edicao>")
    print("Exemplo: python relatorio_v3.py 5877")
    sys.exit(1)

edicao_converter = sys.argv[1]
logger_detalhado, logger_geral = configurar_logs(edicao_converter)

log_info("=== INICIANDO RELATORIO V3.0 ===")
log_info("Python executado: " + sys.executable)
log_info(f"EDICAO SOLICITADA: {edicao_converter}")
log_info("INICIANDO PROCESSAMENTO...")

# -------------------- CONFIGURAÇÃO SELENIUM --------------------
HEADLESS = True
driver_path = r"D:\Documentos\Workspace\chromedriver.exe"
service = Service(driver_path)

if HEADLESS:
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--window-size=1920,1080")
    chrome_opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_opts.add_experimental_option("useAutomationExtension", False)
    navegador = webdriver.Chrome(service=service, options=chrome_opts)
else:
    navegador = webdriver.Chrome(service=service)

caminho_downloads = r"D:\Adilson\Downloads"

# -------------------- FUNÇÕES DE ROBUSTEZ --------------------
def fechar_popup():
    """Fecha popup inicial se aparecer"""
    try:
        btn = WebDriverWait(navegador, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Entendi']"))
        )
        btn.click()
        WebDriverWait(navegador, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.MuiDialog-container"))
        )
        log_info("Pop-up fechado.")
    except TimeoutException:
        log_info("Pop-up não apareceu.")

def limpar_overlays():
    """Remove overlays que bloqueiam cliques"""
    try:
        body = navegador.find_element(By.TAG_NAME, "body")
        for _ in range(3):
            body.send_keys(Keys.ESCAPE)
            sleep(0.3)
        navegador.execute_script("""
            document.querySelectorAll('div.MuiBackdrop-root').forEach(function(backdrop){
                if(backdrop.style.opacity!=='0'){
                    backdrop.remove();
                }
            });
        """)
        sleep(1)
        log_info("Overlays removidos")
    except Exception as e:
        log_warning(f"Aviso limpeza: {e}")

def limpar_campo_busca():
    """Limpa completamente o campo de busca"""
    try:
        campo = navegador.find_element(By.XPATH, "//input[@placeholder='Pesquisar por título do sorteio...']")
        campo.click()
        sleep(0.3)
        campo.send_keys(Keys.CONTROL + "a")
        sleep(0.2)
        campo.send_keys(Keys.DELETE)
        sleep(0.2)
        navegador.execute_script("arguments[0].value = '';", campo)
        navegador.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", campo)
        log_info("Campo de busca limpo")
        return True
    except Exception as e:
        log_error(f"Erro ao limpar campo: {e}")
        return False

def capturar_titulo_robusto():
    """Captura título com múltiplas tentativas - NOVA FUNCIONALIDADE V3"""
    titulo = None
    seletores_titulo = [
        # Seletor principal
        '//*[@id="root"]/div/main/div/div/div[2]/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div[1]/div/div[1]/div/h4',
        # Seletores alternativos
        "//h4[contains(@class, 'MuiTypography')]",
        "//div[contains(@class, 'MuiGrid')]//h4",
        "//h4",
        "//div[@role='dialog']//h4"
    ]
    
    for i, seletor in enumerate(seletores_titulo):
        try:
            titulo_elem = navegador.find_element(By.XPATH, seletor)
            titulo = titulo_elem.text.strip()
            if titulo and len(titulo) > 10:  # Título válido deve ter mais de 10 caracteres
                log_info(f"Titulo capturado (seletor {i+1}): {titulo}")
                return titulo
        except Exception as e:
            log_warning(f"Seletor {i+1} falhou: {e}")
            continue
    
    log_error(f"Não foi possível capturar título para edição {edicao_converter}")
    return None

def detectar_arquivo_baixado_robusto(nome_esperado, edicao):
    """
    Detecta arquivo baixado considerando divergências de nome - NOVA FUNCIONALIDADE V3
    Implementa solução para problema documentado em DOCUMENTACAO_DIVERGENCIA_NOMES.md
    """
    caminho_esperado = os.path.join(caminho_downloads, nome_esperado)
    arquivo_encontrado = None
    
    log_info("Aguardando download com deteccao robusta...")
    
    for seg in range(15):  # Aumentar tempo de espera para 15 segundos
        # Verificar arquivo pelo nome exato
        if os.path.exists(caminho_esperado):
            arquivo_encontrado = caminho_esperado
            log_info(f"CSV baixado em {seg}s: {nome_esperado}")
            break
        
        # Busca alternativa: procurar arquivos CSV recentes com padrão similar
        try:
            # Buscar arquivos CSV na pasta downloads modificados nos últimos 2 minutos
            padrao = os.path.join(caminho_downloads, "relatorio-vendas-*.csv")
            arquivos_csv = glob.glob(padrao)
            
            for arquivo in arquivos_csv:
                # Verificar se foi modificado recentemente (últimos 2 minutos)
                tempo_modificacao = datetime.fromtimestamp(os.path.getmtime(arquivo))
                if datetime.now() - tempo_modificacao < timedelta(minutes=2):
                    # Verificar se contém a edição no nome
                    if str(edicao) in os.path.basename(arquivo):
                        arquivo_encontrado = arquivo
                        log_info(f"CSV encontrado por busca alternativa em {seg}s: {os.path.basename(arquivo)}")
                        break
            
            if arquivo_encontrado:
                break
                
        except Exception as e:
            log_warning(f"Erro na busca alternativa: {e}")
        
        sleep(1)
    
    if not arquivo_encontrado:
        log_error(f"CSV não baixou: {edicao}")
        # Debug: listar arquivos recentes para diagnóstico
        try:
            padrao = os.path.join(caminho_downloads, "relatorio-vendas-*.csv")
            arquivos_recentes = glob.glob(padrao)
            if arquivos_recentes:
                log_warning("Arquivos CSV encontrados na pasta:")
                for arq in arquivos_recentes[-3:]:  # Mostrar últimos 3
                    log_warning(f"   - {os.path.basename(arq)}")
        except:
            pass
        return None
    
    return arquivo_encontrado

# -------------------- LOGIN E NAVEGAÇÃO --------------------
try:
    log_info("CONECTANDO AO PAINEL...")
    
    # Validação de credenciais de login
    if not LOGIN_CONFIG["email"] or not LOGIN_CONFIG["password"]:
        log_error("Credenciais de login não encontradas no arquivo .env")
        log_error("Verifique se LOGIN_EMAIL e LOGIN_PASSWORD estão definidos")
        navegador.quit()
        sys.exit(1)
    
    navegador.get(LOGIN_CONFIG["url"])
    sleep(2)
    navegador.execute_script("window.print = function(){};")

    log_info("FAZENDO LOGIN...")
    navegador.find_element(By.NAME, "email").send_keys(LOGIN_CONFIG["email"])
    navegador.find_element(By.NAME, "password").send_keys(LOGIN_CONFIG["password"])
    navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    sleep(4)

    fechar_popup()
    sleep(2)
    limpar_overlays()

    # Navegar para sorteios com robustez
    menu_xpath = '//*[@id="root"]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/div[2]/ul[1]/div[2]/div[2]/span'
    try:
        menu = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, menu_xpath))
        )
        navegador.execute_script("arguments[0].scrollIntoView(true);", menu)
        sleep(1)
        navegador.execute_script("arguments[0].click();", menu)
        sleep(2)
        log_info("Navegacao para sorteios concluida")
    except Exception as e:
        log_error(f"Erro ao navegar para sorteios: {e}")
        raise

    # Limpar campo de busca antes de usar
    limpar_campo_busca()
    sleep(1)

    log_info(f"BUSCANDO EDICAO {edicao_converter}...")
    busca = navegador.find_element(By.XPATH, "//input[@placeholder='Pesquisar por título do sorteio...']")
    busca.clear()
    busca.send_keys(edicao_converter)
    sleep(3)  # Aguardar resultados da busca

    # Verificar se existe botão de relatórios (indicador de que a edição foi encontrada)
    try:
        log_info("Aguardando resultados da busca...")
        botao_compras = WebDriverWait(navegador, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Compras']"))
        )
        log_info("Edição encontrada! Acessando relatórios...")
        botao_compras.click()
        sleep(1)
    except TimeoutException:
        log_error(f"Edição {edicao_converter} não foi encontrada no sistema!")
        log_error("A edição pode não existir ou estar inativa.")
        print(f"ERRO: Edição {edicao_converter} não foi encontrada no sistema!")  # Para o chatbot capturar
        navegador.quit()
        sys.exit(1)

    # Navegar para relatório de vendas
    ac = ActionChains(navegador)
    for _ in range(6): 
        ac.send_keys(Keys.TAB).pause(0.2)
    ac.send_keys(Keys.ENTER).perform()
    sleep(1)

    try:
        WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li//div[contains(text(), 'Relatório de Vendas')]"))
        ).click()
        sleep(1)
        log_info("Relatorio de vendas selecionado")
    except Exception as e:
        log_error(f"Erro ao selecionar relatório de vendas: {e}")
        raise

    # Capturar título com detecção robusta
    titulo = capturar_titulo_robusto()
    if not titulo:
        navegador.quit()
        sys.exit(1)

    slug = unidecode.unidecode(titulo.lower().replace(" ", "-"))
    nome_csv = f"relatorio-vendas-{slug}.csv"
    
    log_info(f"Arquivo esperado: {nome_csv}")

    # Detectar arquivo baixado com método robusto
    caminho_csv = detectar_arquivo_baixado_robusto(nome_csv, edicao_converter)
    
    if not caminho_csv:
        navegador.quit()
        sys.exit(1)

    log_info("Download detectado com sucesso!")

except Exception as e:
    log_error(f"Erro crítico durante automação: {e}")
    navegador.quit()
    sys.exit(1)

# -------------------- PROCESSAMENTO DO CSV --------------------
try:
    log_info("INICIANDO PROCESSAMENTO DO CSV...")
    
    df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8')
    log_info(f"CSV carregado: {len(df)} linhas encontradas")
    
    # -------------------- PDF CONFIG -------------------
    wkhtml = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config_pdf = pdfkit.configuration(wkhtmltopdf=wkhtml)

    def criptografar(tel):
        return tel[:7] + "***-**" + tel[-2:] if len(tel) == 15 else tel

    # -------------------- PROCESSAMENTO ----------------
    log_info("PROCESSANDO DADOS...")
    df = df.iloc[:, [6, 7, 20]]          # Nome, Telefone, Números adquiridos
    df.columns = ["Nome", "Telefone", "Números"]

    def juntar(series):
        nums = []
        for item in series:
            nums += [p.strip() for p in str(item).split(",") if p.strip()]
        nums = sorted(set(nums), key=int)
        return ", ".join(nums)

    agrupado = (
        df.groupby("Telefone")
          .agg(Nome=("Nome", "first"), Números=("Números", juntar))
          .reset_index()
    )

    agrupado["Telefone"] = agrupado["Telefone"].apply(criptografar)
    agrupado = agrupado[["Nome", "Telefone", "Números"]]
    agrupado = agrupado.sort_values("Nome")

    # -------------------- GERAR HTML/PDF ----------------
    log_info("CRIANDO PDF...")
    html = f"""
<html><head><meta charset="utf-8"><style>
 body{{font-family:Arial,sans-serif;margin:0;padding:0}}
 h1{{
     text-align:center;
     margin:25px 0 15px 0;
     font-size:24pt;
     font-weight:bold;
     color:#0d47a1;
 }}
 table{{width:100%;border-collapse:collapse}}
 colgroup {{
     width:100%;
 }}
 th,td{{border:1px solid #ddd;padding:8px}}
 th{{
     background:#6495ED;           /* cabeçalho */
     color:#fff;
     text-align:center;
     font-size:18pt;               /* +2 pt */
 }}
 td{{font-size:16pt}}              /* +1 pt */
 td:nth-child(2),th:nth-child(2){{text-align:center}}
 th:first-child,td:first-child{{width:48%;white-space:normal;word-wrap:break-word}}
 th:nth-child(2),td:nth-child(2){{width:20%}}
 th:nth-child(3),td:nth-child(3){{width:32%;text-align:center}}
 tr:nth-child(even) td{{background:#f6f6f6}}  /* zebra */
</style></head><body>
<h1>{titulo}</h1>
{agrupado.to_html(index=False, border=0)}
</body></html>
"""
    
    tmp_html = os.path.join(caminho_downloads, "relatorio_temp.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html)

    caminho_pdf = caminho_csv.replace(".csv", ".pdf")
    pdfkit.from_file(tmp_html, caminho_pdf, configuration=config_pdf)
    os.remove(tmp_html)
    log_info("PDF GERADO COM SUCESSO!")

except Exception as e:
    log_error(f"Erro no processamento do CSV: {e}")
    print(f"ERRO: Falha no processamento: {e}")  # Para o chatbot capturar
    navegador.quit()
    sys.exit(1)

# ================== INSERÇÃO NO BANCO DE DADOS ==================
# Esta seção implementa a lógica de inserção diretamente no script,
# baseada na estrutura robusta do alimenta_relatorios_vendas.py
# ==================================================================

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
                
            log_info(f"Sigla extraída do arquivo: '{sigla}'")
            return sigla
                
    except Exception as e:
        log_error(f"Erro ao extrair sigla do arquivo: {e}")
    
    return None

def obter_horario_por_extracao(sigla_extraida):
    """
    Retorna o horário específico baseado na extração/sigla
    IMPORTANTE: Verifica siglas mais específicas primeiro para evitar confusão
    """
    sigla = sigla_extraida.upper().strip()
    
    # Mapeamento de horários por extração - ORDEM IMPORTANTE (mais específicos primeiro)
    horarios = [
        ('CORUJINHA', '21:30:00'),
        ('FEDERAL', '19:00:00'),
        ('PPT', '09:20:00'),
        ('PTM', '11:20:00'), 
        ('PTN', '18:20:00'),
        ('PTV', '16:20:00'),
        ('PT', '14:20:00'),  # PT deve vir DEPOIS de PTN e PTV para não confundir
    ]
    
    # Verificar se a sigla contém alguma das extrações
    for extracao_base, horario in horarios:
        if extracao_base in sigla:
            log_info(f"Horario definido para '{sigla}': {horario} (baseado em '{extracao_base}')")
            return horario
    
    # Se não encontrar correspondência, retornar horário padrão
    log_warning(f"Extração não reconhecida '{sigla}', usando horário padrão: 12:00:00")
    return '12:00:00'

def inserir_dados_banco_integrado():
    """
    Insere dados no banco de dados diretamente (sem dependência externa)
    Baseado na lógica robusta do alimenta_relatorios_vendas.py
    """
    try:
        log_info("INICIANDO INSERCAO NO BANCO DE DADOS...")
        
        # Extrair sigla do nome do arquivo
        sigla_extraida = extrair_sigla_do_arquivo(caminho_csv)
        
        if not sigla_extraida:
            log_error("Não foi possível extrair a sigla do arquivo. Verifique o nome do arquivo CSV.")
            return False

        # 1) Ler o CSV com cabeçalho para usar nomes das colunas
        df_banco = pd.read_csv(
            caminho_csv,
            sep=';',
            encoding='utf-8'
        )

        # Mapeamento das colunas usando nomes corretos
        df_nome = df_banco['Nome']                    # Nome
        df_telefone = df_banco['Telefone']            # Telefone
        df_qtd = df_banco['Quantidade']               # Quantidade
        df_total = df_banco['Valor']                  # Valor
        df_horadata = df_banco['Data da Compra']      # Data da Compra
        
        # Novas colunas específicas
        df_aprovado_por = df_banco['Aprovado por']    # Aprovado por
        df_host_pagamento = df_banco['Host do Pagamento'] # Host do Pagamento
        df_numeros = df_banco['Números']              # Números

        # 2) Conexão ao MySQL
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Verifica se já existe registro para esta edição em relatorios_importados
        sql_check = "SELECT COUNT(*) FROM relatorios_importados WHERE edicao = %s"
        cursor.execute(sql_check, (edicao_converter,))
        existe = cursor.fetchone()[0]

        if existe != 0:
            log_info(f"Edição {edicao_converter} já existe em relatorios_importados. Nada será inserido.")
            conn.close()
            return True  # Retorna True porque não é erro, apenas já existe

        # 3) PRIMEIRO: Calcular total de cotas e obter maior data do CSV
        total_cotas = 0
        maior_data = None
        
        for i in range(len(df_banco)):
            # Somar cotas
            try:
                total_cotas += int(df_qtd.iloc[i])
            except:
                continue
            
            # Encontrar a maior data
            try:
                data_registro = datetime.strptime(str(df_horadata.iloc[i]).strip(), "%d/%m/%Y, %H:%M:%S")
                if maior_data is None or data_registro > maior_data:
                    maior_data = data_registro
            except:
                continue
        
        # Se não conseguiu extrair nenhuma data, usar data atual
        if maior_data is None:
            maior_data = datetime.now()
        
        # Obter horário específico baseado na extração
        horario_extracao = obter_horario_por_extracao(sigla_extraida)
        
        # Combinar a maior data com o horário da extração
        data_final = datetime.combine(maior_data.date(), datetime.strptime(horario_extracao, "%H:%M:%S").time())
        
        # Inserir em relatorios_importados PRIMEIRO
        sql_insert_rel = """
            INSERT INTO relatorios_importados (edicao, total_cotas, data, Extracao)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql_insert_rel, (edicao_converter, total_cotas, data_final, sigla_extraida))
        log_info(f"Registro pai criado em relatorios_importados: edicao {edicao_converter}, total_cotas={total_cotas}")

        # 4) SEGUNDO: Preparar INSERT para relatorios_vendas (tabela filha)
        sql_insert = """
            INSERT INTO relatorios_vendas (nome, telefone, edicao, extracao, qtd, total, data, horacompra, valor_cota, aprovado_por, host_pagamento, numeros)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        total_inseridos = 0

        # 5) Preparar dados para inserção com ordenação por horadata
        dados_para_inserir = []
        
        for i in range(len(df_banco)):
            nome = str(df_nome.iloc[i]).strip()
            telefone = str(df_telefone.iloc[i]).strip()
            edicao = edicao_converter

            try:
                qtd = int(df_qtd.iloc[i])
            except:
                qtd = 0

            try:
                total = float(str(df_total.iloc[i]).replace(',', '.'))
            except:
                total = 0.0

            # Calcular valor_cota = total ÷ quantidade
            try:
                if qtd > 0:
                    valor_cota = total / qtd
                else:
                    valor_cota = 0.0
            except:
                valor_cota = 0.0

            aprovado_por = str(df_aprovado_por.iloc[i]).strip()
            host_pagamento = str(df_host_pagamento.iloc[i]).strip()
            numeros = str(df_numeros.iloc[i]).strip()

            # Processar data/hora da coluna 13 e separar em data e horacompra
            try:
                data_hora_completa = datetime.strptime(str(df_horadata.iloc[i]).strip(), "%d/%m/%Y, %H:%M:%S")
                data_compra = data_hora_completa.date()  # Apenas a data
                hora_compra = data_hora_completa.time()  # Apenas a hora
            except Exception as e:
                log_warning(f"Erro ao converter data/hora para o registro {i}: {df_horadata.iloc[i]} - {e}")
                data_compra = None
                hora_compra = None

            # Ordem: nome, telefone, edicao, extracao, qtd, total, data, horacompra, valor_cota, aprovado_por, host_pagamento, numeros
            dados_para_inserir.append((
                nome, telefone, edicao, sigla_extraida, qtd, total, 
                data_compra, hora_compra, valor_cota, aprovado_por, host_pagamento, numeros,
                data_hora_completa  # Para ordenação (não será inserido)
            ))
        
        # Ordenar dados por horadata (ordem crescente)
        dados_para_inserir.sort(key=lambda x: x[12] if x[12] is not None else datetime.min)
        
        # 6) Inserir dados ordenados no banco relatorios_vendas
        for valores in dados_para_inserir:
            # Remover o último elemento (data_hora_completa usado só para ordenação)
            valores_para_inserir = valores[:12]
            cursor.execute(sql_insert, valores_para_inserir)
            total_inseridos += 1

        # 7) Confirmar todas as transações
        conn.commit()
        log_info(f"{total_inseridos} linhas inseridas em 'relatorios_vendas' com sucesso!")
        log_info("Dados salvos no banco com sucesso!")
        return True

    except mysql.connector.Error as err:
        log_error(f"Erro ao conectar ou inserir no banco: {err}")
        return False

    except Exception as e:
        log_error(f"Erro ao processar dados para banco: {e}")
        return False

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Executar inserção no banco de dados
sucesso_banco = inserir_dados_banco_integrado()

if not sucesso_banco:
    log_error("Falha na inserção no banco de dados")
    
# ================== FIM DA INSERÇÃO NO BANCO ==================

# -------------------- LIMPEZA E FINALIZAÇÃO --------------------
try:
    if os.path.exists(caminho_csv):
        os.remove(caminho_csv)
        log_info("CSV temporário removido.")

    navegador.quit()
    log_info("=== RELATORIO V3.0 CONCLUÍDO COM SUCESSO ===")
    log_info(f"PDF gerado: {caminho_pdf}")
    
    if sucesso_banco:
        log_info("Dados inseridos no banco de dados com sucesso!")
    else:
        log_warning("Houve problemas na insercao no banco de dados")

except Exception as e:
    log_error(f"Erro na finalização: {e}")
    print(f"ERRO: Falha na finalização: {e}")  # Para o chatbot capturar
    navegador.quit()
    sys.exit(1)
