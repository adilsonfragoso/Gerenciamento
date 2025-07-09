from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options  # Para configurar o navegador
from selenium.webdriver.chrome.service import Service  # Para controlar o ChromeDriver
from time import sleep
import time  # Para usar time.sleep()
import subprocess  # Necessário para usar a flag que oculta a janela

# CONFIGURAÇÕES
URL_PAGINA_INICIAL = "https://litoraldasorte.com"
URL_LOGIN = "https://painel.litoraldasorte.com"
LOGIN = 'desativa'
SENHA = 'Define@4536#8521'
INTERVALO_MINUTOS = 60  # Tempo em minutos entre execuções

# Caminho absoluto para o ChromeDriver
CHROMEDRIVER_PATH = r"D:\Documentos\Workspace\chromedriver.exe"
# Flag para impedir que a janela de console seja exibida (Windows)
CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW  # ou use 0x08000000 se necessário

# CONFIGURAÇÃO DO NAVEGADOR COM MODO HEADLESS
def iniciar_navegador():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o navegador em modo headless (oculto)
    chrome_options.add_argument("--disable-gpu")  # Desativa a aceleração GPU (recomendado)
    chrome_options.add_argument("--no-sandbox")  # Necessário em alguns sistemas Linux
    chrome_options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória no Linux
    chrome_options.add_argument("--window-size=1920,1080")  # Define uma resolução virtual
    chrome_options.add_argument("--log-level=3")  # Reduz mensagens de log

    # Cria o Service com a flag para não exibir a janela de console
    service = Service(CHROMEDRIVER_PATH, creationflags=CREATE_NO_WINDOW)
    return webdriver.Chrome(service=service, options=chrome_options)

# FUNÇÃO PARA COLETAR EDIÇÕES CONCLUÍDAS
def coletar_edicoes_concluidas(navegador):
    edicoes = []
    try:
        # Localizar todas as divs que possuem o status "Concluído"
        divs_concluidas = navegador.find_elements(
            By.XPATH, "//div[contains(@class, 'MuiPaper-root') and .//span[text()='Concluído']]"
        )
        for div in divs_concluidas:
            try:
                # Dentro da div, encontrar o número da edição no <h2> ou <h6>
                try:
                    numero_edicao = div.find_element(By.XPATH, ".//h2").text
                except:
                    numero_edicao = div.find_element(By.XPATH, ".//h6").text
                # Extrair apenas o número da edição (última parte do texto)
                edicao = numero_edicao.split(" ")[-1]
                edicoes.append(edicao)
            except Exception as e:
                print(f"[ERRO] Não foi possível processar uma div: {e}")
                continue
    except Exception as e:
        raise Exception(f"[ERRO] Falha ao coletar edições concluídas: {e}")
    return edicoes

# FUNÇÃO PARA REALIZAR LOGIN
def realizar_login(navegador):
    try:
        navegador.find_element(By.NAME, "email").send_keys(LOGIN)
        navegador.find_element(By.NAME, "password").send_keys(SENHA)
        navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sleep(2)
    except Exception as e:
        raise Exception(f"[ERRO] Não foi possível realizar login: {e}")

# FUNÇÃO PARA PROCESSAR UMA EDIÇÃO
def processar_edicao(navegador, edicao_para_desativar):
    try:
        print(f"\n[INFO] Processando edição {edicao_para_desativar} ...")
        
        # Fechar TODOS os popups possíveis antes de continuar
        popups_fechados = 0
        for i in range(5):  # Tenta fechar até 5 popups
            try:
                # Tentar diferentes seletores de popup
                seletores_popup = [
                    '/html/body/div[2]/div[3]/div/div[2]/button',
                    "//button[contains(text(), 'Fechar')]",
                    "//button[contains(text(), 'OK')]",
                    "//button[contains(text(), 'Cancelar')]",
                    "//div[contains(@class, 'MuiDialog')]//button",
                    "//button[@aria-label='Close']",
                    "//button[@aria-label='Fechar']"
                ]
                
                popup_fechado = False
                for seletor in seletores_popup:
                    try:
                        popup = navegador.find_element(By.XPATH, seletor)
                        if popup.is_displayed():
                            popup.click()
                            popup_fechado = True
                            popups_fechados += 1
                            print(f"Popup fechado com seletor: {seletor}")
                            sleep(1)
                            break
                    except:
                        continue
                
                if not popup_fechado:
                    break  # Se não encontrou mais popups, para o loop
                    
            except Exception as e:
                break
        
        if popups_fechados > 0:
            print(f"Total de {popups_fechados} popup(s) fechado(s).")
        
        sleep(2)  # Aguarda um pouco mais após fechar popups
        
        # Acessar o menu sorteios
        menu_sorteios = navegador.find_element(
            By.XPATH, '//*[@id="root"]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/div[2]/ul[1]/div[2]/div[2]/span'
        )
        menu_sorteios.click()
        sleep(1)
        try:
            wait = WebDriverWait(navegador, 10)
            linhas_por_pagina_button = wait.until(EC.element_to_be_clickable(
                (By.CLASS_NAME, 'MuiTablePagination-select')))
            linhas_por_pagina_button.click()
            opcao_25 = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//li[text()="25"]')))
            opcao_25.click()
        except TimeoutException:
            print("Não foi possível encontrar o botão ou a opção de linhas por página.")
        sleep(1)
        # Buscar rifa por edição
        campo_busca_edicao = navegador.find_element(
            By.XPATH, "//input[@placeholder='Pesquisar por título do sorteio...']")
        campo_busca_edicao.click()
        campo_busca_edicao.clear()
        campo_busca_edicao.send_keys(str(edicao_para_desativar))
        sleep(3)  # Aumentado de 1 para 3 segundos para carregar resultados
        
        # Opção editar rifa - com melhor tratamento de espera
        wait = WebDriverWait(navegador, 10)
        try:
            botao_editar_rifa = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Editar']")))
            botao_editar_rifa.click()
        except TimeoutException:
            print(f"[ERRO] Botão Editar não encontrado para edição {edicao_para_desativar}")
            return  # Pula para a próxima edição
        sleep(1)
        # Verificar o estado atual do botão "Mostrar o sorteio na página inicial"
        exibir_sorteio = navegador.find_element(By.NAME, "showHome")
        estado_botao = exibir_sorteio.get_attribute("checked")
        if estado_botao == "true":
            print(f"O botão está ativado. Desativando...")
            exibir_sorteio.click()
        else:
            print(f"O botão já está desativado. Nada a fazer.")
        # Rolagem para o botão salvar
        navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Localiza o botão "Salvar" pelo texto e clica
        botao_salvar = navegador.find_element(
            By.XPATH, "//button[contains(., 'Salvar')]")
        botao_salvar.click()
        sleep(2)  # Aguarda salvar antes de ir para a próxima edição
    except Exception as e:
        print(f"[ERRO] Falha ao processar edição {edicao_para_desativar}: {e}")

# FUNÇÃO PRINCIPAL
def main():
    navegador = None
    try:
        print("[INFO] Iniciando execução do script...")
        # Inicializar o navegador em modo oculto
        navegador = iniciar_navegador()
        print("[INFO] Acessando a página inicial...")
        navegador.get(URL_PAGINA_INICIAL)
        sleep(3)

        # Fazer login no painel de administração (uma única vez no início)
        print("[INFO] Fazendo login no painel...")
        navegador.get(URL_LOGIN)
        sleep(2)
        realizar_login(navegador)

        total_processadas = 0
        iteracao = 1

        # Loop principal: processar todas as edições concluídas
        while True:
            print(f"\n[INFO] === ITERAÇÃO {iteracao} ===")

            # Acessar a página inicial para buscar edições concluídas
            navegador.get(URL_PAGINA_INICIAL)
            sleep(3)

            # Coletar edições com status "Concluído"
            edicoes_concluidas = coletar_edicoes_concluidas(navegador)

            if not edicoes_concluidas:
                print("[INFO] Nenhuma edição concluída encontrada nesta iteração.")
                break  # Sai do loop se não encontrou mais edições

            print(f"[INFO] Edições concluídas identificadas na iteração {iteracao}: {edicoes_concluidas}")

            # Voltar para o painel para processar as edições
            navegador.get(URL_LOGIN)
            sleep(2)

            # Processar edições concluídas encontradas
            for edicao in edicoes_concluidas:
                processar_edicao(navegador, edicao)
            total_processadas += 1

            print(f"[INFO] Iteração {iteracao} concluída. Total processadas até agora: {total_processadas}")
            iteracao += 1

        print(f"\n[INFO] Execução concluída com sucesso!")
        print(f"[INFO] Total de edições processadas: {total_processadas}")
        print(f"[INFO] Total de iterações realizadas: {iteracao - 1}")

    except Exception as e:
        print(f"[ERRO] Ocorreu um erro: {e}")
    finally:
        if navegador:
            navegador.quit()
            print("[INFO] Navegador fechado.")
        print("[INFO] Script finalizado.")

# EXECUÇÃO PRINCIPAL
if __name__ == "__main__":
    main() 