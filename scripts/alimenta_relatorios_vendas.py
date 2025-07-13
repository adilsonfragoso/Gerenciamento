# -------------------------------------------------------------
# alimenta_relatorios_vendas.py
#
# Script automatizado para baixar relatórios de vendas do painel
# Litoral da Sorte e inserir diretamente na tabela 'relatorios_vendas'
# com novos campos e estrutura aprimorada.
#
# Funcionalidades principais:
# - Faz login no painel web com Selenium (login único)
# - Processa uma ou múltiplas edições de sorteio
# - Baixa o CSV de vendas de cada edição
# - Insere dados diretamente na tabela 'relatorios_vendas'
# - Ordena inserções por data/hora crescente
# - Separa horadata em campos 'data' e 'horacompra'
# - Adiciona novos campos: valor_cota, aprovado_por, host_pagamento, numeros
# - Remove o CSV após o processamento
# - Continua processamento mesmo se edições não existirem
#
# Formatos de uso:
# - Edição única:      python alimenta_relatorios_vendas.py 5197
# - Múltiplas edições: python alimenta_relatorios_vendas.py 5197 6020 6040 6700  
# - Sequência:         python alimenta_relatorios_vendas.py 5197-6020
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import unidecode
import os
import sys
import pandas as pd
import mysql.connector
import glob
from datetime import datetime, timedelta

# Importar configuração do banco
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db_config import DB_CONFIG

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
                
            print(f"Sigla extraída do arquivo: '{sigla}'")
            return sigla
                
    except Exception as e:
        print(f"Erro ao extrair sigla do arquivo: {e}")
    
    return None

def obter_horario_por_extracao(sigla_extraida):
    """
    Retorna o horário específico baseado na extração/sigla
    Reconhece variações como 'PT ESPECIAL', 'FEDERAL ESPECIAL', etc.
    IMPORTANTE: Verifica siglas mais específicas primeiro para evitar confusão
    """
    # Converter para maiúsculo e remover espaços extras
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
    
    # Verificar se a sigla contém alguma das extrações (verificando as mais específicas primeiro)
    for extracao_base, horario in horarios:
        if extracao_base in sigla:
            print(f"🕐 Horário definido para '{sigla}': {horario} (baseado em '{extracao_base}')")
            return horario
    
    # Se não encontrar correspondência, retornar horário padrão
    print(f"⚠️ Extração não reconhecida '{sigla}', usando horário padrão: 12:00:00")
    return '12:00:00'

def processar_csv_e_inserir(edicao_desejada, caminho_csv):
    """Processa o CSV e insere os dados na tabela relatorios_vendas"""
    
    # Extrair sigla do nome do arquivo
    sigla_extraida = extrair_sigla_do_arquivo(caminho_csv)
    
    if not sigla_extraida:
        print("ERRO: Não foi possível extrair a sigla do arquivo. Verifique o nome do arquivo CSV.")
        return False

    # Verifica se o CSV existe
    if not os.path.exists(caminho_csv):
        print(f"ERRO: O arquivo CSV não foi encontrado: {caminho_csv}")
        return False

    try:
        # 1) Ler o CSV ignorando a 1a linha (cabeçalho) e sem usar nomes de coluna (header=None)
        df = pd.read_csv(
            caminho_csv,
            sep=';',
            encoding='utf-8',
            skiprows=1,
            header=None
        )

        # Mapeamento das colunas (A=0, B=1, C=2, etc.)
        df_nome = df.iloc[:, 6]      # G - nome
        df_telefone = df.iloc[:, 7]  # H - telefone
        df_qtd = df.iloc[:, 3]       # D - quantidade (qtd na nova tabela)
        df_total = df.iloc[:, 5]     # F - valorTotal já calculado (total da compra)
        df_horadata = df.iloc[:, 13] # N - horadata (será separado em data e horacompra)
        
        # Novas colunas específicas
        # valor_cota será calculado: coluna 5 (total) ÷ coluna 3 (qtd) = valor unitário
        df_aprovado_por = df.iloc[:, 16]  # Q - aprovado_por (coluna 16)
        df_host_pagamento = df.iloc[:, 15] # P - host_pagamento (coluna 15)
        df_numeros = df.iloc[:, 20]       # U - numeros (coluna 20)

        # 2) Conexão ao MySQL
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Verifica se já existe registro para esta edição em relatorios_importados
        sql_check = """
            SELECT COUNT(*) FROM relatorios_importados WHERE edicao = %s
        """
        cursor.execute(sql_check, (edicao_desejada,))
        existe = cursor.fetchone()[0]

        if existe != 0:
            print(f"Edição {edicao_desejada} já existe em relatorios_importados. Nada será inserido.")
            conn.close()
            return False

        # 3) PRIMEIRO: Calcular total de cotas e obter maior data do CSV
        total_cotas = 0
        maior_data = None
        
        for i in range(len(df)):
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
        cursor.execute(sql_insert_rel, (edicao_desejada, total_cotas, data_final, sigla_extraida))
        print(f"✅ Registro pai criado em relatorios_importados: edição {edicao_desejada}, total_cotas={total_cotas}, data={data_final.strftime('%Y-%m-%d %H:%M:%S')}")

        # 4) SEGUNDO: Preparar INSERT para relatorios_vendas (tabela filha)
        sql_insert = """
            INSERT INTO relatorios_vendas (nome, telefone, edicao, extracao, qtd, total, data, horacompra, valor_cota, aprovado_por, host_pagamento, numeros)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        total_inseridos = 0

        # 5) Preparar dados para inserção com ordenação por horadata
        dados_para_inserir = []
        
        for i in range(len(df)):
            nome = str(df_nome.iloc[i]).strip()
            telefone = str(df_telefone.iloc[i]).strip()
            edicao = edicao_desejada

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
                print(f"Erro ao converter data/hora para o registro {i}: {df_horadata.iloc[i]} - {e}")
                data_compra = None
                hora_compra = None

            # Ordem: nome, telefone, edicao, extracao, qtd, total, data, horacompra, valor_cota, aprovado_por, host_pagamento, numeros
            dados_para_inserir.append((
                nome, telefone, edicao, sigla_extraida, qtd, total, 
                data_compra, hora_compra, valor_cota, aprovado_por, host_pagamento, numeros,
                data_hora_completa  # Para ordenação (não será inserido)
            ))
        
        # Ordenar dados por horadata (ordem crescente) - usar o último elemento para ordenação
        dados_para_inserir.sort(key=lambda x: x[12] if x[12] is not None else datetime.min)
        
        # 6) Inserir dados ordenados no banco relatorios_vendas (removendo o campo de ordenação)
        for valores in dados_para_inserir:
            # Remover o último elemento (data_hora_completa usado só para ordenação)
            valores_para_inserir = valores[:12]
            cursor.execute(sql_insert, valores_para_inserir)
            total_inseridos += 1

        # 7) Confirmar todas as transações
        conn.commit()
        print(f"✅ {total_inseridos} linhas inseridas em 'relatorios_vendas' com sucesso!")
        return True

    except mysql.connector.Error as err:
        print(f"❌ Erro ao conectar ou inserir no banco: {err}")
        return False

    except Exception as e:
        print(f"❌ Erro ao ler CSV ou processar dados: {e}")
        return False

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

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
        sleep(1)
        print(f"🔍 Buscando: {edicao}")
    except NoSuchElementException:
        print(f"❌ Campo busca não encontrado: {edicao}")
        return False

    # Verificar se encontrou algum resultado
    try:
        # Aguardar um pouco para carregar resultados
        sleep(1)
        
        # Verificar se tem botão "Compras" (indica que edição existe)
        compras_btn = navegador.find_element(By.XPATH, "//button[@aria-label='Compras']")
        print(f"✅ Edição {edicao} encontrada")
        
    except NoSuchElementException:
        print(f"❌ Edição {edicao} não existe")
        return False

    # Clicar em Compras
    try:
        compras_btn.click()
        sleep(1)
        
        # Navegar com TAB
        actions = ActionChains(navegador)
        for _ in range(6):
            actions.send_keys(Keys.TAB).pause(0.1)
        actions.send_keys(Keys.ENTER).perform()
        sleep(1)
        
        # Clicar em Relatório de Vendas
        rel = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li//div[contains(text(), 'Relatório de Vendas')]"))
        )
        rel.click()
        sleep(1)
        print("✅ Relatório selecionado")
        
    except Exception as e:
        print(f"❌ Erro relatório {edicao}: {e}")
        return False

    # Capturar título com múltiplas tentativas
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
                print(f"✅ Título capturado (seletor {i+1}): {titulo}")
                break
        except Exception as e:
            print(f"⚠️ Seletor {i+1} falhou: {e}")
            continue
    
    if not titulo:
        print(f"❌ Não foi possível capturar título para edição {edicao}")
        return False
        
    slug = unidecode.unidecode(titulo.lower().replace(" ", "-"))
    nome_arquivo = f"relatorio-vendas-{slug}.csv"
    caminho_csv = os.path.join(caminho_downloads, nome_arquivo)
    print(f"📄 Arquivo esperado: {nome_arquivo}")

    # Aguardar download com busca mais robusta
    print("⏳ Aguardando download...")
    arquivo_encontrado = None
    
    for seg in range(15):  # Aumentar tempo de espera
        # Verificar arquivo pelo nome exato
        if os.path.exists(caminho_csv):
            arquivo_encontrado = caminho_csv
            print(f"✅ CSV baixado em {seg}s: {nome_arquivo}")
            break
        
        # Busca alternativa: procurar arquivos CSV recentes com padrão similar
        try:
            import glob
            from datetime import datetime, timedelta
            
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
                        print(f"✅ CSV encontrado por busca alternativa em {seg}s: {os.path.basename(arquivo)}")
                        break
            
            if arquivo_encontrado:
                break
                
        except Exception as e:
            print(f"⚠️ Erro na busca alternativa: {e}")
        
        sleep(1)
    
    if not arquivo_encontrado:
        print(f"❌ CSV não baixou: {edicao}")
        # Debug: listar arquivos recentes para diagnóstico
        try:
            import glob
            padrao = os.path.join(caminho_downloads, "relatorio-vendas-*.csv")
            arquivos_recentes = glob.glob(padrao)
            if arquivos_recentes:
                print(f"🔍 Arquivos CSV encontrados na pasta:")
                for arq in arquivos_recentes[-3:]:  # Mostrar últimos 3
                    print(f"   - {os.path.basename(arq)}")
        except:
            pass
        return False
    
    # Atualizar caminho do CSV para o arquivo encontrado
    caminho_csv = arquivo_encontrado

    # Processar CSV e inserir no banco
    print("📊 Processando dados para tabela relatorios_vendas...")
    sucesso = processar_csv_e_inserir(edicao, caminho_csv)

    # Remover CSV
    try:
        os.remove(caminho_csv)
        print(f"🗑️ CSV removido")
    except:
        pass

    return sucesso

def parsear_argumentos(args):
    """
    Processa argumentos de entrada para suportar diferentes formatos:
    - Edição única: 5197
    - Edições intercaladas: 5197 6020 6040 6700
    - Sequência: 5197-6020
    """
    edicoes = []
    
    for arg in args:
        if '-' in arg and arg.count('-') == 1:
            # Formato sequência: 5197-6020
            try:
                inicio, fim = map(int, arg.split('-'))
                if inicio <= fim:
                    edicoes.extend(range(inicio, fim + 1))
                else:
                    print(f"⚠️ Sequência inválida: {arg} (início deve ser menor que fim)")
            except ValueError:
                print(f"⚠️ Formato de sequência inválido: {arg}")
        else:
            # Edição única
            try:
                edicoes.append(int(arg))
            except ValueError:
                print(f"⚠️ Edição inválida: {arg}")
    
    # Remover duplicatas e ordenar
    edicoes = sorted(list(set(edicoes)))
    return edicoes

def main():
    if len(sys.argv) < 2:
        print("Uso: python alimenta_relatorios_vendas.py <edicoes>")
        print("Exemplos:")
        print("  Edição única:      python alimenta_relatorios_vendas.py 5197")
        print("  Múltiplas edições: python alimenta_relatorios_vendas.py 5197 6020 6040 6700")
        print("  Sequência:         python alimenta_relatorios_vendas.py 5197-6020")
        sys.exit(1)

    # Processar argumentos para obter lista de edições
    edicoes = parsear_argumentos(sys.argv[1:])
    
    if not edicoes:
        print("❌ Nenhuma edição válida fornecida")
        sys.exit(1)

    print(f"🎯 Processando {len(edicoes)} edição(ões): {edicoes}")
    
    navegador = criar_navegador()
    
    try:
        # Login único no início
        fazer_login(navegador)
        fechar_popup(navegador)
        sleep(2)
        
        # Ir para sorteios uma vez
        if not navegar_para_sorteios(navegador):
            print("❌ Falha inicial ao navegar para sorteios")
            return
        
        sucessos = 0
        falhas = 0
        inexistentes = 0
        
        # Processar cada edição
        for i, edicao in enumerate(edicoes, 1):
            print(f"\n📊 Processando edição {i}/{len(edicoes)}: {edicao}")
            
            try:
                resultado = processar_edicao(navegador, edicao)
                
                if resultado:
                    sucessos += 1
                    print(f"✅ Edição {edicao} processada com sucesso!")
                else:
                    # Verificar se é inexistente ou erro técnico baseado na mensagem
                    falhas += 1
                    print(f"❌ Falha ao processar edição {edicao}")
                
                # Voltar para sorteios (exceto na última edição)
                if i < len(edicoes):
                    print("🔄 Voltando para menu sorteios...")
                    if not navegar_para_sorteios(navegador):
                        print("⚠️ Falha ao voltar para sorteios, tentando continuar...")
                        sleep(2)
                        
            except Exception as e:
                falhas += 1
                print(f"❌ Erro crítico na edição {edicao}: {e}")
                
                # Tentar voltar para sorteios em caso de erro
                try:
                    navegar_para_sorteios(navegador)
                except:
                    print("⚠️ Não foi possível voltar para sorteios após erro")
        
        # Resumo final
        print(f"\n🎉 Processamento concluído!")
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas/Inexistentes: {falhas}")
        print(f"📊 Total processado: {sucessos + falhas}/{len(edicoes)}")
        
        if sucessos > 0:
            print(f"🎯 Taxa de sucesso: {(sucessos/len(edicoes)*100):.1f}%")
        
    except Exception as e:
        print(f"❌ Erro crítico no script: {e}")
    finally:
        print("🔒 Fechando navegador...")
        navegador.quit()

if __name__ == "__main__":
    main()
