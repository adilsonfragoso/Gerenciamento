import os
import re
import datetime
import logging
import time
import sys
from time import sleep
from pathlib import Path

import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)

# Importar configurações centralizadas
from config_cadRifas import (
    DATABASE_CONFIG, BROWSER_CONFIG, LOGIN_CONFIG, PAYMENT_CONFIG,
    FILE_CONFIG, URL_CONFIG, TIMEOUT_CONFIG, LOGGING_CONFIG, RETRY_CONFIG,
    validar_configuracoes, criar_pasta_logs
)

# =============================================================================
# CONFIGURAÇÃO DE TESTE - ALTERE AQUI PARA TESTAR SEM SALVAR
# =============================================================================
CRIAR_SORTEIO = False  # True = Salva o sorteio, False = Apenas simula (para testes)

# =============================================================================
# Configuração de logging
# =============================================================================

def configurar_logging():
    """Configura o sistema de logging estruturado"""
    # Criar pasta de logs
    criar_pasta_logs()
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG['file'], encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

logger = configurar_logging()

# =============================================================================
# Funções utilitárias
# =============================================================================

def validar_data(data_str: str) -> bool:
    """Valida se a data está no formato DD/MM/AAAA"""
    try:
        datetime.datetime.strptime(data_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validar_siglas(siglas: list) -> bool:
    """Valida se as siglas estão no formato correto"""
    if not siglas:
        return False
    
    for sigla in siglas:
        if not sigla or not isinstance(sigla, str) or len(sigla.strip()) < 2:
            return False
    
    return True

def exibir_siglas(siglas):
    """Exibe as siglas informadas"""
    logger.info(f"Siglas informadas: {', '.join(siglas)}")

def esperar_elemento(driver, locator, cond=EC.visibility_of_element_located, to=None):
    """Aguarda até `to` segundos por uma condição sobre o `locator`."""
    timeout = to or TIMEOUT_CONFIG['element_wait']
    return WebDriverWait(driver, timeout).until(cond(locator))

def esperar_e_clicar(driver, locator, to=None):
    """Espera o elemento estar clicável e executa o clique."""
    timeout = to or TIMEOUT_CONFIG['element_wait']
    elem = esperar_elemento(driver, locator, EC.element_to_be_clickable, timeout)
    elem.click()
    return elem

# =============================================================================
# Login / abertura de navegador
# =============================================================================

def fazer_login_e_abrir_navegador():
    """Configura e abre o navegador, fazendo login no sistema"""
    try:
        # Configurar opções do Chrome
        chrome_options = Options()
        for option in BROWSER_CONFIG['options']:
            chrome_options.add_argument(option)
        
        # Configurar preferências
        chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.clipboard": 1}
        )
        
        # Inicializar driver
        driver = webdriver.Chrome(
            service=Service(BROWSER_CONFIG['driver_path']), 
            options=chrome_options
        )
        
        # Fazer login
        driver.get(LOGIN_CONFIG['url'])
        esperar_elemento(driver, (By.NAME, "email"))
        driver.find_element(By.NAME, "email").send_keys(LOGIN_CONFIG['email'])
        driver.find_element(By.NAME, "password").send_keys(LOGIN_CONFIG['password'])
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        esperar_elemento(driver, (By.XPATH, "//div[contains(@class,'MuiDrawer')]"))
        
        logger.info("Login efetuado com sucesso!")
        return driver
        
    except Exception as e:
        logger.error(f"Erro ao fazer login: {e}")
        raise

# =============================================================================
# Cadastro de sorteio
# =============================================================================

def cadastrar_sorteio(driver, edicao_data):
    """Cadastra um sorteio no sistema Litoral da Sorte usando dados completos da edição."""
    pasta_imagens = FILE_CONFIG['pasta_imagens']
    edicao = edicao_data['edicao']
    sigla_oficial = edicao_data['sigla_oficial']
    extracao = edicao_data['extracao']
    data_sorteio = edicao_data['data_sorteio'].strftime('%d/%m/%Y') if isinstance(edicao_data['data_sorteio'], (datetime.date, datetime.datetime)) else str(edicao_data['data_sorteio'])

    logger.info(f"Iniciando cadastro do sorteio {edicao} para sigla '{sigla_oficial}' (extracao: '{extracao}')")

    # Verificar modo de teste
    if not CRIAR_SORTEIO:
        logger.warning("MODO TESTE ATIVADO - Nenhum sorteio será criado!")

    # --- Dados vindos de extracoes_cadastro ---
    hora_do_sorteio = edicao_data["horario"]
    preco_str = f"{edicao_data['precocota']:.2f}".replace(".", ",")
    premios = [
        edicao_data["primeiro"], edicao_data["segundo"], edicao_data["terceiro"], edicao_data["quarto"],
        edicao_data["quinto"], edicao_data["sexto"], edicao_data["setimo"], edicao_data["oitavo"],
        edicao_data["nono"], edicao_data["decimo"],
    ]
    total_premios = int(edicao_data["totalpremios"] or 10)

    datahora = f"{data_sorteio} {hora_do_sorteio}"
    # Montar título diretamente com sigla_oficial
    titulo = (
        f"{sigla_oficial.upper()} RJ EDIÇÃO {edicao}"
        if sigla_oficial.upper() not in ("FEDERAL", "FEDERAL ESPECIAL")
        else f"{sigla_oficial.upper()} EDIÇÃO {edicao}"
    )

    # --- Fecha pop-up se existir ---------------------------------------------
    try:
        esperar_e_clicar(driver, (By.XPATH, '/html/body/div[2]/div[3]/div/div[2]/button'), to=4)
        logger.info("Pop-up fechado.")
    except TimeoutException:
        pass

    # --- Vai para "Novo Sorteio" --------------------------------------------
    esperar_e_clicar(driver, (
        By.XPATH,
        '//*[@id="root"]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/div[2]/ul[1]/div[2]/div[2]/span',
    ))
    esperar_e_clicar(driver, (By.XPATH, '//*[@id="root"]/div/main/div/div/div[1]/div[1]/div[2]/a'))

    # --- Aba Geral ------------------------------------------------------------
    esperar_elemento(driver, (By.NAME, "title")).send_keys(titulo)
    Select(driver.find_element(By.NAME, "category")).select_by_visible_text("Dinheiro")
    Select(driver.find_element(By.NAME, "reservationOption")).select_by_visible_text("Escolhe os bilhetes manualmente")
    esperar_elemento(driver, (
        By.XPATH,
        '//*[@id="root"]/div/main/div/div/form/div/div[1]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div[1]',
    )).send_keys(titulo)
    driver.execute_script("window.scrollTo(0, 0);")

    # --- Aba Números ----------------------------------------------------------
    esperar_e_clicar(driver, (
        By.XPATH,
        '//*[@id="root"]/div/main/div/div/form/div/div[1]/div[1]/div[3]/div/button[2]',
    ))
    campo_valor = esperar_elemento(driver, (By.NAME, "numbersConfig.price"))
    campo_valor.send_keys(Keys.CONTROL, "a", Keys.DELETE)
    driver.execute_script(
        "arguments[0].value=''; arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
        campo_valor,
    )
    campo_valor.send_keys(preco_str)
    Select(driver.find_element(By.NAME, "numbersConfig.qty")).select_by_visible_text("100")
    driver.find_element(By.NAME, "numbersConfig.qtyBuyer").clear()
    driver.find_element(By.NAME, "numbersConfig.qtyBuyer").send_keys("0")
    driver.find_element(By.NAME, "numbersConfig.defaultValue").clear()
    driver.find_element(By.NAME, "numbersConfig.defaultValue").send_keys("1")
    driver.find_element(By.NAME, "numbersConfig.showProgressBar").click()

    # --- Aba Imagens ----------------------------------------------------------
    esperar_e_clicar(driver, (
        By.XPATH,
        '//*[@id="root"]/div/main/div/div/form/div/div[1]/div[1]/div[3]/div/button[3]',
    ))
    input_img = driver.find_element(By.XPATH, '//input[@type="file" and @style="display: none;"]')
    
    # Buscar imagem usando extracao (sigla com sufixo)
    img_path = None
    for ext in ("jpeg", "jpg"):
        possible_path = os.path.join(pasta_imagens, f"{extracao}.{ext}")
        if os.path.isfile(possible_path):
            img_path = os.path.abspath(possible_path)
            break
    
    if not img_path:
        raise FileNotFoundError(f"Imagem de {extracao} não encontrada em {pasta_imagens}")
    
    input_img.send_keys(img_path)
    logger.info(f"Imagem carregada: {img_path}")

    # --- Aba Prêmios ----------------------------------------------------------
    XPATH_BTN_ADD = '//*[@id="root"]/div/main/div/div/form/div/div[1]/div[2]/div/div/button'
    esperar_e_clicar(driver, (
        By.XPATH,
        '//*[@id="root"]/div/main/div/div/form/div/div[1]/div[1]/div[3]/div/button[4]',
    ))
    chk_award = driver.find_element(By.NAME, "award")
    if not chk_award.is_selected():
        chk_award.click()

    for _ in range(total_premios - 1):
        try:
            esperar_e_clicar(driver, (By.XPATH, XPATH_BTN_ADD))
        except (TimeoutException, StaleElementReferenceException):
            break

    for idx, premio in enumerate(premios[:total_premios]):
        nome = f"awards[{idx}]"
        try:
            campo = esperar_elemento(driver, (By.NAME, nome))
            campo.send_keys(Keys.CONTROL, "a", Keys.DELETE)
            driver.execute_script(
                "arguments[0].value=''; arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
                campo,
            )
            campo.send_keys(premio)
        except (TimeoutException, StaleElementReferenceException):
            break
    driver.execute_script("window.scrollTo(0, 0);")

    # --- Aba Afiliados --------------------------------------------------------
    esperar_e_clicar(driver, (
        By.XPATH,
        '//*[@id="root"]/div/main/div/div/form/div/div[1]/div[1]/div[3]/div/button[5]',
    ))
    driver.find_element(By.NAME, "affiliates").click()
    driver.find_element(By.NAME, "affiliatesWhiteList").click()

    # --- Aba Pagamento --------------------------------------------------------
    logger.info("=== PREENCHENDO ABA PAGAMENTO ===")
    
    esperar_e_clicar(driver, (
        By.XPATH,
        '//*[@id="root"]/div/main/div/div/form/div/div[1]/div[1]/div[3]/div/button[7]',
    ))
    
    # Selecionar Info Pago
    logger.info("Selecionando Info Pago...")
    Select(driver.find_element(By.NAME, "paymentConfig.host")).select_by_visible_text("Info Pago")
    
    # Preencher Client ID
    client_id = PAYMENT_CONFIG['client_id']
    logger.info(f"Preenchendo Client ID: {client_id}")
    driver.find_element(By.NAME, "paymentConfig.infoPago.clientId").send_keys(client_id)
    
    # Preencher Client Secret
    client_secret = PAYMENT_CONFIG['client_secret']
    logger.info(f"Preenchendo Client Secret: {client_secret}")
    driver.find_element(By.NAME, "paymentConfig.infoPago.clientSecret").send_keys(client_secret)
    
    # Preencher Chave PIX
    chave_pix = PAYMENT_CONFIG['chave_pix']
    logger.info(f"Preenchendo Chave PIX: {chave_pix}")
    driver.find_element(By.NAME, "paymentConfig.infoPago.chavePix").send_keys(chave_pix)
    
    logger.info("=== ABA PAGAMENTO PREENCHIDA COM SUCESSO ===")

    # --- Volta à Aba Geral ---------------------------------------------------
    esperar_e_clicar(driver, (
        By.XPATH,
        '//*[@id="root"]/div/main/div/div/form/div/div[1]/div[1]/div[3]/div/button[1]',
    ))
    driver.find_element(By.NAME, "drawAuto").click()
    driver.find_element(By.NAME, "showDrawDate").click()
    driver.find_element(By.NAME, "orderDownload").click()
    driver.find_element(By.NAME, "statusText").send_keys("!")

    ActionChains(driver).send_keys(Keys.TAB * 2 + Keys.ENTER).perform()
    esperar_e_clicar(driver, (By.XPATH, '/html/body/div[2]/div[3]/div/div[1]/div/div[1]/div/button'))
    ActionChains(driver).send_keys(Keys.TAB * 2 + datahora + Keys.TAB * 2 + Keys.ENTER).perform()

    # --- Criar sorteio -------------------------------------------------------
    if CRIAR_SORTEIO:
        # MODO PRODUÇÃO - Criar sorteio
        logger.info("MODO PRODUÇÃO - Criando sorteio...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        esperar_e_clicar(driver, (By.XPATH, "//button[contains(., 'Criar Sorteio')]") , to=7)

        # Aguarda voltar para lista (botão "Novo Sorteio" visível)
        try:
            WebDriverWait(driver, 7).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="root"]/div/main/div/div/div[1]/div[1]/div[2]/a')
                )
            )
        except TimeoutException:
            sleep(2)

        logger.info(f"Sorteio {edicao} ({sigla_oficial}) cadastrado com sucesso!")
    else:
        # MODO TESTE - Não criar sorteio
        logger.warning(f"MODO TESTE - Sorteio {edicao} ({sigla_oficial}) NÃO foi criado!")
        logger.info("Formulário preenchido completamente, mas sorteio não foi salvo.")
        
        # Aguarda um pouco para visualizar o formulário preenchido
        sleep(3)
        
        # Volta para a lista sem salvar
        try:
            esperar_e_clicar(driver, (By.XPATH, '//*[@id="root"]/div/main/div/div/div[1]/div[1]/div[2]/a'))
        except TimeoutException:
            logger.info("Navegando de volta para a lista...")

    return True

# =============================================================================
# Função principal com retry
# =============================================================================

def cadastrar_sorteio_com_retry(driver, edicao_data):
    """Cadastra sorteio com sistema de retry usando dados completos da edição."""
    max_attempts = RETRY_CONFIG['max_attempts']
    delay = RETRY_CONFIG['delay_between_attempts']
    edicao = edicao_data['edicao']
    for tentativa in range(max_attempts):
        try:
            logger.info(f"Tentativa {tentativa + 1} de {max_attempts} para edição {edicao}")
            return cadastrar_sorteio(driver, edicao_data)
        except Exception as e:
            logger.warning(f"Tentativa {tentativa + 1} falhou para edição {edicao}: {e}")
            if tentativa < max_attempts - 1:
                logger.info(f"Aguardando {delay} segundos antes da próxima tentativa...")
                time.sleep(delay)
            else:
                logger.error(f"Todas as tentativas falharam para edição {edicao}")
                raise

def atualizar_status_cadastro(edicao):
    """Atualiza o status_cadastro para 'cadastrado' na tabela extracoes_cadastro para a edição informada."""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        cur.execute("UPDATE extracoes_cadastro SET status_cadastro = 'cadastrado' WHERE edicao = %s", (edicao,))
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Status de cadastro atualizado para 'cadastrado' na edição {edicao}")
    except Exception as e:
        logger.error(f"Erro ao atualizar status_cadastro para edição {edicao}: {e}")
        raise

# =============================================================================
# Leitura de edições pendentes na tabela extracoes_cadastro
# =============================================================================
def ler_edicoes_pendentes_extracoes_cadastro():
    """Busca todas as edições pendentes ou com erro na tabela extracoes_cadastro e retorna uma lista de dicts com todos os campos necessários."""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                ec.id, ec.data_sorteio, ec.edicao, ec.sigla_oficial, ec.extracao, ec.link,
                ec.status_cadastro, ec.status_link, ec.error_msg, ec.id_siglas_diarias,
                ep.horario, ep.precocota, ep.primeiro, ep.segundo, ep.terceiro, ep.quarto, ep.quinto,
                ep.sexto, ep.setimo, ep.oitavo, ep.nono, ep.decimo,
                ep.decimo_primeiro, ep.decimo_segundo, ep.decimo_terceiro, ep.decimo_quarto,
                ep.numeracao, ep.totalpremios, ep.totalpremios_oficial, ep.totalpremiacao,
                ep.premiosextras, ep.arrecad, ep.lucro
            FROM extracoes_cadastro ec
            INNER JOIN extracoes_premiacao ep ON ec.edicao = ep.edicao
            WHERE ec.status_cadastro IN ('pendente', 'error') 
            ORDER BY ec.edicao ASC
        """)
        rows = cur.fetchall()
        
        # Converter resultados para dicionários
        columns = [desc[0] for desc in cur.description] if cur.description else []
        edicoes = []
        for row in rows:
            if row is not None and columns:
                edicoes.append(dict(zip(columns, row)))
        
        cur.close()
        conn.close()
        return edicoes
    except Exception as e:
        logger.error(f"Erro ao buscar edições pendentes em extracoes_cadastro: {e}")
        raise

def main():
    """Função principal do script"""
    logger.info("=== INICIANDO SCRIPT CADRIFAS_LITORAL_V4 ===")

    if CRIAR_SORTEIO:
        logger.info("MODO PRODUÇÃO ATIVADO - Sorteios serão criados!")
    else:
        logger.warning("MODO TESTE ATIVADO - Nenhum sorteio será criado!")

    try:
        # Validar configurações
        validar_configuracoes()
        logger.info("Configurações validadas com sucesso")

        # Buscar edições pendentes
        edicoes_pendentes = ler_edicoes_pendentes_extracoes_cadastro()
        if not edicoes_pendentes:
            logger.info("Nenhuma edição pendente ou com erro encontrada na tabela extracoes_cadastro. Encerrando script.")
            return

        logger.info(f"Total de edições pendentes ou com erro encontradas: {len(edicoes_pendentes)}")
        for ed in edicoes_pendentes:
            logger.info(f"Edição {ed['status_cadastro']}: {ed['edicao']} | Sigla: {ed['sigla_oficial']} | Data: {ed['data_sorteio']}")

        # Configurar e abrir navegador
        driver = fazer_login_e_abrir_navegador()
        edicoes_cadastradas = []

        for ed in reversed(edicoes_pendentes):
            sigla = ed['sigla_oficial']
            edicao = ed['edicao']
            data_sorteio = ed['data_sorteio'].strftime('%d/%m/%Y') if isinstance(ed['data_sorteio'], (datetime.date, datetime.datetime)) else str(ed['data_sorteio'])
            logger.info(f"\nProcessando edição {edicao} para '{sigla}'...")
            try:
                if cadastrar_sorteio_com_retry(driver, ed):
                    if CRIAR_SORTEIO:
                        atualizar_status_cadastro(edicao)
                        edicoes_cadastradas.append(edicao)
            except FileNotFoundError as e:
                logger.warning(f"[AVISO] {e}")
            except Exception as e:
                logger.error(f"[ERRO] Falha na edição {edicao}: {e}")

        sleep(2)
        driver.quit()

        logger.info("Processamento concluído das edições pendentes.")
        if CRIAR_SORTEIO:
            logger.info("=== SCRIPT CONCLUÍDO COM SUCESSO (MODO PRODUÇÃO) ===")
        else:
            logger.warning("=== SCRIPT CONCLUÍDO COM SUCESSO (MODO TESTE) ===")

    except Exception as e:
        logger.error(f"Erro crítico no script: {e}")
        raise

if __name__ == "__main__":
    main()
