#Baixa relatórios de vendas do painel Litoral da Sorte e processa no banco de dados
#não gera PDF, apenas CSV
#busca por de acordo com a ultima edição do sorteio


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
import subprocess

# ===================== CONFIGURAÇÃO =====================
HEADLESS = False  # False para debug, True para produção
driver_path = r"D:\Documentos\Workspace\chromedriver.exe"
caminho_downloads = r"D:\Adilson\Downloads"
service = Service(driver_path)

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
    sleep(3) #ERA 4
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
        sleep(0.3)#ERA 0.5
        
        # Selecionar tudo e deletar
        campo.send_keys(Keys.CONTROL + "a")
        sleep(0.2)#ERA 0.2
        campo.send_keys(Keys.DELETE)
        sleep(0.2)#ERA 0.2  
        
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
        sleep(2)#ERA 6
        
        # Limpar campo de busca após navegar
        limpar_campo_busca(navegador)
        
        print("📋 Navegando para sorteios...")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao navegar para sorteios: {e}")
        return False

def processar_edicao(navegador, edicao):
    print(f"\n🚀 Processando edição: {edicao}")
    
    # Buscar edição
    try:
        # Garantir que campo está limpo antes de digitar
        limpar_campo_busca(navegador)
        sleep(1)
        
        campo = navegador.find_element(By.XPATH, "//input[@placeholder='Pesquisar por título do sorteio...']")
        campo.click()
        sleep(0.5)
        campo.send_keys(str(edicao))
        sleep(1)#ERA 5
        print(f"🔍 Buscando: {edicao}")
    except NoSuchElementException:
        print(f"❌ Campo busca não encontrado: {edicao}")
        return False

    # Verificar se encontrou algum resultado
    try:
        # Aguardar um pouco para carregar resultados
        sleep(1)#ERA 2
        
        # Verificar se tem botão "Compras" (indica que edição existe)
        compras_btn = navegador.find_element(By.XPATH, "//button[@aria-label='Compras']")
        print(f"✅ Edição {edicao} encontrada")
        
    except NoSuchElementException:
        print(f"❌ Edição {edicao} não existe - pulando")
        return False

    # Clicar em Compras
    try:
        compras_btn.click()
        sleep(1)#
        
        # Navegar com TAB
        actions = ActionChains(navegador)
        for _ in range(6):
            actions.send_keys(Keys.TAB).pause(0.1)#ERA 0.5
        actions.send_keys(Keys.ENTER).perform()
        sleep(1)#ERA 3
        
        # Clicar em Relatório de Vendas
        rel = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li//div[contains(text(), 'Relatório de Vendas')]"))
        )
        rel.click()
        sleep(1)#ERA 2
        print("✅ Relatório selecionado")
        
    except Exception as e:
        print(f"❌ Erro relatório {edicao}: {e}")
        return False

    # Capturar título
    try:
        titulo_elem = navegador.find_element(
            By.XPATH,
            '//*[@id="root"]/div/main/div/div/div[2]/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div[1]/div/div[1]/div/h4'
        )
        titulo = titulo_elem.text
        slug = unidecode.unidecode(titulo.lower().replace(" ", "-"))
        nome_arquivo = f"relatorio-vendas-{slug}.csv"
        caminho_csv = os.path.join(caminho_downloads, nome_arquivo)
        print(f"📄 Arquivo: {nome_arquivo}")
    except Exception as e:
        print(f"❌ Erro título {edicao}: {e}")
        return False

    # Aguardar download
    print("⏳ Aguardando download...")
    for seg in range(10):
        if os.path.exists(caminho_csv):
            print(f"✅ CSV baixado em {seg}s")
            break
        sleep(1)
    else:
        print(f"❌ CSV não baixou: {edicao}")
        return False

    # Processar no banco
    print("📊 Processando banco...")
    res = subprocess.run(
        ["python", "D:/Documentos/Workspace/inserir_no_bd.py", str(edicao), caminho_csv],
        capture_output=True, text=True, encoding='utf-8'
    )
    
    if res.returncode == 0:
        saida = res.stdout.strip() or "Processado"
        print(f"✅ {saida}")
    else:
        print(f"❌ Erro banco: {res.stderr.strip()}")

    # Remover CSV
    try:
        os.remove(caminho_csv)
        print(f"🗑️ CSV removido")
    except:
        pass

    return True

def main():
    if len(sys.argv) < 2:
        print("Uso: python script.py <início> [fim]")
        sys.exit(1)

    try:
        inicio = int(sys.argv[1])
        fim = int(sys.argv[2]) if len(sys.argv) > 2 else inicio
    except ValueError:
        print("Parâmetros inválidos")
        sys.exit(1)

    print(f"🎯 Processando edições {inicio}-{fim}")
    
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
        pulos = 0  # Contador para edições que não existem
        
        # Loop das edições
        for edicao in range(inicio, fim + 1):
            try:
                resultado = processar_edicao(navegador, edicao)
                
                if resultado:
                    sucessos += 1
                    print(f"✅ Sucesso: {edicao}")
                elif resultado is False:
                    # Distinguir entre falha técnica e edição inexistente
                    falhas += 1
                    print(f"❌ Falha: {edicao}")
                
                # Voltar para sorteios (exceto última)
                if edicao < fim:
                    print("🔄 Voltando sorteios...")
                    if not navegar_para_sorteios(navegador):
                        print("❌ Falha voltar sorteios")
                        break
                        
            except Exception as e:
                falhas += 1
                print(f"❌ Erro {edicao}: {e}")
        
        # Resultado
        print(f"\n🎉 Concluído!")
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {falhas}")
        print(f"📊 Total: {sucessos + falhas}/{fim - inicio + 1}")
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
    finally:
        print("🔒 Fechando navegador...")
        navegador.quit()

if __name__ == "__main__":
    main() 