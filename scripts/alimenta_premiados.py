#Esse script usa um script chamado "calculo_valor_real.py" para calcular o valor real dos prêmios.



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
import re
import mysql.connector
from mysql.connector import Error
import argparse
import contextlib
import re

# ===================== CONFIGURAÇÃO =====================
HEADLESS = False  # False para debug, True para produção
LOG_FILE = None   # Caminho do log se em modo oculto
driver_path = r"D:\Documentos\Workspace\chromedriver.exe"
service = Service(driver_path)


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db_config import DB_CONFIG

def calcular_valor_real(premio):
    valor_reais = 0.0
    match_reais = re.search(r'R\$\s*([\d\.]+,\d{2})', premio)
    if match_reais:
        valor_reais = float(match_reais.group(1).replace('.', '').replace(',', '.'))
    match_cotas = re.search(r'(\d+)\s+COTAS?\s+DO\s+SORTEIO\s+DA\s+(.+)', premio, re.IGNORECASE)
    valor_cotas = 0.0
    if match_cotas:
        qtd_cotas = int(match_cotas.group(1))
        nome_cota = match_cotas.group(2).strip().upper()
        conexao = conectar_banco()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute("SELECT valor_cota FROM cotas WHERE UPPER(cota) LIKE %s LIMIT 1", (f"%{nome_cota}%",))
                resultado = cursor.fetchone()
                if resultado:
                    valor_unitario = float(resultado[0])
                    valor_cotas = qtd_cotas * valor_unitario
            finally:
                cursor.close()
                conexao.close()
    return round(valor_reais + valor_cotas, 2)

def configurar_oculto():
    global HEADLESS, LOG_FILE
    HEADLESS = True
    LOG_FILE = os.path.join(os.path.dirname(__file__), 'alimenta_premiados_oculto.log')
    # Redirecionar prints para arquivo
    class Logger:
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, 'a', encoding='utf-8')
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
        def flush(self):
            self.terminal.flush()
            self.log.flush()
    sys.stdout = Logger(LOG_FILE)
    sys.stderr = Logger(LOG_FILE)

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

def conectar_banco():
    """Conecta ao banco MySQL"""
    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        return conexao
    except Error as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def inserir_premiacao(edicao, extracao, nome, telefone, colocacao, premio, titulo, valor_real=None):
    """Insere uma premiação na tabela premiados"""
    conexao = conectar_banco()
    if not conexao:
        return False
    
    try:
        cursor = conexao.cursor()
        if valor_real is None:
            valor_real = calcular_valor_real(premio)
        query = """
        INSERT INTO premiados (edicao, extracao, nome, telefone, colocacao, premio, titulo, valor_real)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (edicao, extracao, nome, telefone, colocacao, premio, titulo, valor_real)
        cursor.execute(query, valores)
        conexao.commit()
        print(f"✅ Premiação {colocacao}º lugar salva no banco: {nome} | valor_real: {valor_real}")
        return True
    except Error as e:
        print(f"❌ Erro ao inserir premiação: {e}")
        return False
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

def obter_maior_edicao_premiados():
    """Obtém a maior edição já processada na tabela premiados"""
    conexao = conectar_banco()
    if not conexao:
        return 0
    
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT MAX(edicao) FROM premiados")
        resultado = cursor.fetchone()
        maior_edicao = resultado[0] if resultado and resultado[0] is not None else 0
        return maior_edicao
        
    except Error as e:
        print(f"❌ Erro ao consultar premiados: {e}")
        return 0
        
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

def obter_maior_edicao_extracoes():
    """Obtém a maior edição disponível na tabela extracoes_cadastro com andamento 100%"""
    conexao = conectar_banco()
    if not conexao:
        return 0
    
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT MAX(edicao) FROM extracoes_cadastro WHERE andamento = '100%'")
        resultado = cursor.fetchone()
        maior_edicao = resultado[0] if resultado and resultado[0] is not None else 0
        return maior_edicao
        
    except Error as e:
        print(f"❌ Erro ao consultar extracoes_cadastro: {e}")
        return 0
        
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

def obter_maior_edicao_disponivel():
    """Obtém a maior edição disponível na tabela extracoes_cadastro independente do andamento"""
    conexao = conectar_banco()
    if not conexao:
        return 0
    
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT MAX(edicao) FROM extracoes_cadastro")
        resultado = cursor.fetchone()
        maior_edicao = resultado[0] if resultado and resultado[0] is not None else 0
        return maior_edicao
        
    except Error as e:
        print(f"❌ Erro ao consultar extracoes_cadastro: {e}")
        return 0
        
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

def fazer_login(navegador):
    print("🔐 Fazendo login...")
    navegador.get("https://painel.litoraldasorte.com")
    sleep(2)
    navegador.execute_script("window.print = function(){};")
    navegador.find_element(By.NAME, "email").send_keys("relatoriodash")
    navegador.find_element(By.NAME, "password").send_keys("Define@4536#8521")
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

def extrair_informacoes_reveladas(navegador):
    """Extrai nomes, telefones, títulos e prêmios organizados por premiação"""
    try:
        print("📋 Extraindo informações completas por premiação...")
        
        # Aguardar um pouco para garantir que as informações carregaram
        sleep(2)
        
        # Buscar todas as divs de premiação (cada prêmio tem sua div)
        divs_premiacoes = navegador.find_elements(By.CSS_SELECTOR, "div.css-1bnl7m3")
        
        premiacoes = {}
        
        print(f"🏆 Encontradas {len(divs_premiacoes)} premiações")
        
        for i, div_premiacao in enumerate(divs_premiacoes, 1):
            try:
                # Extrair a colocação do prêmio (1º, 2º, etc.)
                try:
                    paragrafo_colocacao = div_premiacao.find_element(By.TAG_NAME, "p")
                    colocacao_texto = paragrafo_colocacao.text.strip()
                    # Extrair apenas o número da colocação
                    import re
                    match = re.search(r'(\d+)', colocacao_texto)
                    colocacao = match.group(1) if match else str(i)
                except:
                    colocacao = str(i)
                
                # Buscar a div que contém os dados do ganhador
                try:
                    div_dados = div_premiacao.find_element(By.CSS_SELECTOR, "div.css-1pq59s1")
                    
                    # Extrair nome (primeiro h1)
                    nome = ""
                    try:
                        h1_nome = div_dados.find_element(By.TAG_NAME, "h1")
                        nome = h1_nome.text.strip()
                    except:
                        nome = "Nome não encontrado"
                    
                    # Extrair telefone (span com classe específica)
                    telefone = ""
                    try:
                        span_telefone = div_dados.find_element(By.CSS_SELECTOR, "span.css-okm2xv")
                        telefone = span_telefone.text.strip()
                        # Remover o prefixo "Telefone: " se existir
                        if telefone.startswith("Telefone: "):
                            telefone = telefone.replace("Telefone: ", "")
                    except:
                        telefone = "Telefone não encontrado"
                    
                    # Extrair título (span com classe css-1kqhtuk)
                    titulo = ""
                    try:
                        span_titulo = div_dados.find_element(By.CSS_SELECTOR, "span.css-1kqhtuk")
                        titulo = span_titulo.text.strip()
                        # Remover o prefixo "Título: " se existir
                        if titulo.startswith("Título: "):
                            titulo = titulo.replace("Título: ", "")
                    except:
                        titulo = "Título não encontrado"
                    
                    # Extrair prêmio (span com classe css-176slt)
                    premio = ""
                    try:
                        span_premio = div_dados.find_element(By.CSS_SELECTOR, "span.css-176slt")
                        premio = span_premio.text.strip()
                        # Remover o prefixo "Prêmio: " se existir
                        if premio.startswith("Prêmio: "):
                            premio = premio.replace("Prêmio: ", "")
                    except:
                        premio = "Prêmio não encontrado"
                    
                    # Armazenar informações completas da premiação
                    premiacoes[f"{colocacao}º Prêmio"] = {
                        'nome': nome,
                        'telefone': telefone,
                        'titulo': titulo,
                        'premio': premio,
                        'colocacao': colocacao
                    }
                    
                    print(f"🏆 {colocacao}º Prêmio: {nome} | Título: {titulo} | Prêmio: {premio} | Tel: {telefone}")
                    
                except Exception as e:
                    print(f"⚠️ Erro ao extrair dados da premiação {i}: {e}")
                    continue
                
            except Exception as e:
                print(f"⚠️ Erro ao processar div de premiação {i}: {e}")
                continue
        
        return premiacoes
        
    except Exception as e:
        print(f"❌ Erro ao extrair informações: {e}")
        return {}

def revelar_informacoes_ocultas(navegador, cabecalho):
    """Clica em TODOS os ícones do olho para revelar todas as informações"""
    try:
        # Aguardar carregar o div principal das premiações
        div_principal = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-cuz3o0"))
        )
        print("✅ Div principal das premiações carregado")
        
        cliques_sucesso = 0
        todos_svgs_clicados = []
        
        print("🎯 Procurando SVG do olho pelas classes específicas...")
        print("🔍 Classes alvo: css-d0uhtl (que funciona) e css-hjsfpi (2º prêmio teste)")
        
        try:
            # Aguardar elementos SVG aparecerem
            print("⏳ Aguardando elementos SVG aparecerem...")
            elementos_svg = WebDriverWait(navegador, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "svg.iconify.iconify--ic"))
            )
            
            print(f"✅ Encontrados {len(elementos_svg)} SVGs com classes iconify!")
            
                         # Procurar especificamente pelo SVG com as classes corretas
            elemento_svg = None
            svgs_candidatos = []
            
            for i, svg in enumerate(elementos_svg, 1):
                try:
                    classes = svg.get_attribute('class') or ""
                    
                    # Verificar se tem as classes específicas dos ícones olho 
                    if ("css-d0uhtl" in classes or "css-hjsfpi" in classes) and "iconify" in classes:
                        if "css-d0uhtl" in classes:
                            todos_svgs_clicados.append((svg, i, "css-d0uhtl"))
                        elif "css-hjsfpi" in classes:
                            todos_svgs_clicados.append((svg, i, "css-hjsfpi"))
                    # Se não encontrar os exatos, guardar candidatos próximos
                    elif ("css-d0" in classes or "css-n2e6h8" in classes or "css-h" in classes) and "iconify" in classes:
                        svgs_candidatos.append((svg, i, classes))
                        
                except Exception:
                    continue
            
            # VERSÃO OTIMIZADA - Cliques rápidos sem logs excessivos
            if todos_svgs_clicados:
                print(f"✅ Encontrados {len(todos_svgs_clicados)} ícones para clicar - iniciando cliques rápidos...")
                
                # Clicar rapidamente em todos
                for i, (svg, num, tipo) in enumerate(todos_svgs_clicados, 1):
                    try:
                        if svg.is_displayed():
                            svg.click()
                            cliques_sucesso += 1
                            print(f"👁️ {i}/{len(todos_svgs_clicados)} ✅", end=" ")
                            #sleep(0.1)  # Pausa mínima
                    except:
                        print(f"❌ {i}", end=" ")
                        continue
                
                print()  # Nova linha após todos os cliques
                
                # Extrair informações apenas uma vez no final
                print("\n📊 EXTRAINDO INFORMAÇÕES POR PREMIAÇÃO...")
                premiacoes = extrair_informacoes_reveladas(navegador)
                
                # Mostrar resultado organizado por premiação
                if premiacoes:
                    print("\n🏆 RESULTADOS COMPLETOS POR PREMIAÇÃO:")
                    print("=" * 80)
                    print(f"📝 SIGLA: {cabecalho['sigla']}")
                    print(f"🔢 EDIÇÃO: {cabecalho['edicao']}")
                    print(f"📄 TEXTO COMPLETO: {cabecalho['texto_completo']}")
                    print("=" * 80)
                    
                    premiacao_salvas = 0
                    
                    for colocacao, dados in premiacoes.items():
                        print(f"\n🥇 {colocacao}:")
                        print(f"   👤 Nome: {dados['nome']}")
                        print(f"   📞 Telefone: {dados['telefone']}")
                        print(f"   🎫 Título: {dados['titulo']}")
                        print(f"   🏆 Prêmio: {dados['premio']}")
                        
                        # Extrair número da colocação (1º, 2º, etc.)
                        colocacao_numero = dados['colocacao']
                        
                        # Inserir no banco MySQL
                        if inserir_premiacao(
                            edicao=cabecalho['edicao'],
                            extracao=cabecalho['sigla'], 
                            nome=dados['nome'],
                            telefone=dados['telefone'],
                            colocacao=colocacao_numero,
                            premio=dados['premio'],
                            titulo=dados['titulo']
                        ):
                            premiacao_salvas += 1
                    
                    print(f"\n💾 BANCO DE DADOS: {premiacao_salvas}/{len(premiacoes)} premiações salvas!")
                    print(f"✅ TOTAL: {len(premiacoes)} premiações encontradas!")
                    print("=" * 80)
                else:
                    print("⚠️ Nenhuma premiação encontrada")
                        
            # Se não encontrou nenhum SVG específico, tentar candidatos
            elif svgs_candidatos:
                print(f"⚠️ Nenhum SVG específico encontrado. Testando {len(svgs_candidatos)} candidatos...")
                
                # Usar apenas o primeiro candidato em card de premiação
                for svg, num, classes in svgs_candidatos:
                    try:
                        # Verificar se o SVG está dentro de um card de premiação
                        elemento_pai = svg.find_element(By.XPATH, "./ancestor::div[contains(@class, 'MuiCard-root')]")
                        if elemento_pai:
                            print(f"🎯 Usando candidato {num}: {classes}")
                            todos_svgs_clicados = [(svg, num, "candidato")]
                            break
                    except:
                        continue
            
            else:
                print(f"⚠️ EDIÇÃO {cabecalho['edicao']}: Nenhum SVG de premiação encontrado - possivelmente sem premiações")
                
        except TimeoutException:
            print(f"⚠️ EDIÇÃO {cabecalho['edicao']}: Timeout - elementos não carregaram (possivelmente sem premiações)")
        except Exception as e:
            print(f"⚠️ EDIÇÃO {cabecalho['edicao']}: Erro geral - {str(e)[:50]}")
        
        print(f"\n✅ Total de cliques realizados: {cliques_sucesso}")
        
        # Se não conseguiu clicar em nenhum ícone, significa que não há premiações
        if cliques_sucesso == 0:
            print(f"📝 EDIÇÃO {cabecalho['edicao']}: SEM PREMIAÇÕES ATRIBUÍDAS")
            print("=" * 60)
            print(f"📝 SIGLA: {cabecalho['sigla']}")
            print(f"🔢 EDIÇÃO: {cabecalho['edicao']}")
            print(f"⚠️ STATUS: Sem premiações para exibir")
            print("=" * 60)
        
        # Aguardar um pouco para que as informações carreguem
        sleep(1)  # Reduzido para 1 segundo
        
        return True  # Sempre retorna True para não interromper o processamento em lote
        
    except Exception as e:
        print(f"❌ EDIÇÃO {cabecalho['edicao']}: Erro crítico - {e}")
        return True  # Mesmo com erro, continua o processamento

def digitar_edicao_e_clicar_compras(navegador, edicao):
    """Digita a edição no campo de busca, clica em Compras e revela informações"""
    print(f"\n🚀 Processando edição: {edicao}")
    
    try:
        # Garantir que campo está limpo antes de digitar
        limpar_campo_busca(navegador)
        sleep(1)
        
        campo = navegador.find_element(By.XPATH, "//input[@placeholder='Pesquisar por título do sorteio...']")
        campo.click()
        sleep(0.5)
        campo.send_keys(str(edicao))
        sleep(1)  # Reduzido para 1 segundo
        print(f"🔍 Digitado: {edicao}")
        
        # Verificar se encontrou algum resultado
        try:
            # Aguardar aparecer botão "Compras"
            compras_btn = WebDriverWait(navegador, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Compras']"))
            )
            print(f"✅ Edição {edicao} encontrada")
            
            # EXTRAIR SIGLA ANTES de clicar em Compras
            sigla_extraida = extrair_sigla_da_pesquisa(navegador)
            
            # Clicar no botão Compras
            compras_btn.click()
            sleep(2)  # Reduzido para 2 segundos
            print(f"✅ Clicou em Compras para edição {edicao}")
            
            # Criar objeto cabeçalho com as informações extraídas
            cabecalho = {
                'sigla': sigla_extraida,
                'edicao': str(edicao),
                'texto_completo': f"{sigla_extraida} EDIÇÃO {edicao}"
            }
            
            # Revelar informações ocultas
            print("👁️ Procurando ícones de olho para revelar informações...")
            sucesso_revelacao = revelar_informacoes_ocultas(navegador, cabecalho)
            
            if sucesso_revelacao:
                print("✅ Informações reveladas com sucesso!")
            else:
                print("⚠️ Não foi possível revelar todas as informações")
            
            # Para processamento em lote, não pausar
            # print(f"\n⏸️ PAUSANDO após revelar informações da edição {edicao}")
            # print("🔍 Verifique se as informações foram reveladas corretamente")
            # input("Pressione ENTER para continuar...")
            
            return True
            
        except TimeoutException:
            print(f"❌ Nenhum resultado encontrado para a edição {edicao}")
            return False
        except NoSuchElementException:
            print(f"❌ Botão Compras não encontrado para a edição {edicao}")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao processar edição {edicao}: {e}")
        return False

def extrair_sigla_da_pesquisa(navegador):
    """Extrai a sigla da div de resultado da pesquisa"""
    try:
        print("📋 Extraindo sigla da página de pesquisa...")
        
        # Buscar a div com o resultado da pesquisa que contém a informação da edição
        # Procurar por elementos que contenham texto sobre a edição
        elementos_resultado = navegador.find_elements(By.XPATH, "//*[contains(@class, 'MuiTypography')]")
        
        for elemento in elementos_resultado:
            try:
                texto = elemento.text.strip()
                # Procurar por texto que contenha padrões de edição
                if texto and len(texto) > 10 and any(palavra in texto.upper() for palavra in ['EDIÇÃO', 'EDITION', 'ED.']):
                    print(f"🎯 Texto encontrado: '{texto}'")
                    
                    sigla = ""
                    
                    # Aplicar as regras de extração
                    if "RJ" in texto:
                        # Se contém "RJ", a sigla é o que vem antes de "RJ"
                        partes = texto.split("RJ")
                        sigla = partes[0].strip()
                    elif "EDIÇÃO" in texto:
                        # Se não contém "RJ", a sigla é o que vem antes de "EDIÇÃO"
                        partes = texto.split("EDIÇÃO")
                        sigla = partes[0].strip()
                    elif "EDITION" in texto:
                        # Variação em inglês
                        partes = texto.split("EDITION")
                        sigla = partes[0].strip()
                    
                    if sigla:
                        print(f"✅ Sigla extraída: '{sigla}'")
                        return sigla
                        
            except Exception:
                continue
        
        print("⚠️ Nenhuma sigla encontrada na pesquisa")
        return "Sigla não encontrada"
        
    except Exception as e:
        print(f"❌ Erro ao extrair sigla: {e}")
        return "Erro na extração"

def main():
    parser = argparse.ArgumentParser(description='Alimentador automático de premiações')
    parser.add_argument('--oculto', '-o', action='store_true', help='Executa em modo oculto (headless, sem prints no terminal)')
    args = parser.parse_args()

    if args.oculto:
        configurar_oculto()

    print("🚀 ALIMENTADOR AUTOMÁTICO DE PREMIAÇÕES")
    print("=" * 50)
    
    # Obter faixa de edições para processar
    print("📊 Consultando banco de dados...")
    maior_processada = obter_maior_edicao_premiados()
    maior_disponivel_100 = obter_maior_edicao_extracoes()
    maior_disponivel_total = obter_maior_edicao_disponivel()
    
    if maior_disponivel_100 == 0:
        print("❌ Nenhuma edição com andamento 100% encontrada na tabela extracoes_cadastro")
        return
    
    edicao_inicial = maior_processada + 1
    edicao_final = maior_disponivel_100
    
    if edicao_inicial > edicao_final:
        print(f"✅ Todas as edições com andamento 100% já foram processadas!")
        print(f"📊 Última edição processada com 100%: {maior_processada}")
        print(f"📊 Maior edição em andamento: {maior_disponivel_total}")
        return
    
    print(f"🎯 Faixa de processamento: {edicao_inicial} até {edicao_final} (andamento 100%)")
    print(f"📊 Total de edições para processar: {edicao_final - edicao_inicial + 1}")
    print("=" * 50)
    
    navegador = criar_navegador()
    
    try:
        # Login único
        print("🔐 Iniciando sessão...")
        fazer_login(navegador)
        fechar_popup(navegador)
        sleep(2)
        
        # Ir para sorteios
        if not navegar_para_sorteios(navegador):
            print("❌ Falha inicial sorteios")
            return
        
        sucessos = 0
        falhas = 0
        
        # Processar edições sequencialmente
        for edicao_atual in range(edicao_inicial, edicao_final + 1):
            print(f"\n🔄 PROCESSANDO EDIÇÃO {edicao_atual} ({edicao_atual - edicao_inicial + 1}/{edicao_final - edicao_inicial + 1})")
            
            try:
                resultado = digitar_edicao_e_clicar_compras(navegador, edicao_atual)
                
                if resultado:
                    sucessos += 1
                    print(f"✅ Edição {edicao_atual} processada com sucesso!")
                else:
                    falhas += 1
                    print(f"❌ Falha ao processar edição {edicao_atual}")
                
                # Navegar de volta para sorteios (exceto na última edição)
                if edicao_atual < edicao_final:
                    print("🔄 Voltando para sorteios...")
                    if not navegar_para_sorteios(navegador):
                        print("❌ Erro ao voltar para sorteios - interrompendo processamento")
                        break
                    sleep(1)  # Pequena pausa entre edições
                
            except Exception as e:
                falhas += 1
                print(f"❌ Erro crítico na edição {edicao_atual}: {e}")
                
                # Tentar recuperar navegando de volta para sorteios
                try:
                    print("🔄 Tentando recuperar navegação...")
                    navegar_para_sorteios(navegador)
                except:
                    print("❌ Não foi possível recuperar - interrompendo")
                    break
        
        # Relatório final
        print("\n" + "=" * 60)
        print("🎉 PROCESSAMENTO CONCLUÍDO!")
        print("=" * 60)
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {falhas}")
        print(f"📊 Total processado: {sucessos + falhas}")
        print(f"📊 Faixa processada: {edicao_inicial} - {edicao_inicial + sucessos + falhas - 1}")
        if sucessos > 0:
            print(f"🎯 Nova maior edição processada: {edicao_inicial + sucessos - 1}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro crítico no processamento: {e}")
    finally:
        print("🔒 Fechando navegador...")
        navegador.quit()

if __name__ == "__main__":
    main()