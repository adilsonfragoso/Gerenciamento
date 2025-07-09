import os
import requests
import base64
import time
import sys
import mysql.connector

# Importar configurações centralizadas
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from db_config import DB_CONFIG

# Caminho para as imagens (nova pasta)
caminho_imagens = r"D:\Documentos\Workspace\Gerenciamento\uploads"

# ID do grupo no WhatsApp
id_grupo = "120363307707983386@g.us"  # grupo links
#id_grupo = "5512997650505-1562805682@g.us"  # grupo anotações

# Sua API Key
api_key = "9ADC66CB5A10-488D-9B85-4B4A7BB90E8A"

# URL da API Evolution
url = "https://evo2.linksystems.com.br/message/sendMedia/Bancada"

# Configurações para retry
MAX_TENTATIVAS = 3
DELAY_ENTRE_TENTATIVAS = 5  # segundos
TIMEOUT_REQUISICAO = 30  # segundos

# Função para montar o texto da mensagem
def montar_texto(link):
    return (
        "🔥VENDAS ABERTAS🔥\n\n"
        "LINK PARA PARTICIPAR\n"
        "👇👇👇👇👇👇👇👇👇\n"
        f"{link}\n\n"
        "DESEJAMOS A TODOS UMA BOA SORTE 🍀🤞🏻"
    )

# Função para buscar a imagem correspondente à extração
def buscar_imagem(extracao):
    for ext in [".jpg", ".jpeg"]:
        caminho_arquivo = os.path.join(caminho_imagens, extracao + ext)
        if os.path.isfile(caminho_arquivo):
            return caminho_arquivo
    return None

# Função para buscar links pendentes da tabela extracoes_cadastro
def buscar_links_pendentes():
    """Busca todos os links com status_envio_link = 'pendente'"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if not conn.is_connected():
            print("Erro: Não foi possível conectar ao banco de dados")
            return []
            
        cursor = conn.cursor()
        
        query = """
        SELECT link, extracao, edicao, sigla_oficial 
        FROM extracoes_cadastro 
        WHERE status_envio_link = 'pendente'
        ORDER BY edicao ASC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Converter resultados para dicionários
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        resultados = []
        
        # Verificar se rows não é None antes de iterar
        if rows is not None:
            for row in rows:
                if row is not None and columns:
                    resultados.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        
        return resultados
    except Exception as e:
        print(f"Erro ao buscar links pendentes: {e}")
        return []

# Função para buscar link por edição específica
def buscar_link_por_edicao(edicao):
    """Busca link de uma edição específica"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if not conn.is_connected():
            print("Erro: Não foi possível conectar ao banco de dados")
            return None
            
        cursor = conn.cursor()
        
        query = """
        SELECT link, extracao, edicao, sigla_oficial 
        FROM extracoes_cadastro 
        WHERE edicao = %s
        """
        
        cursor.execute(query, (edicao,))
        row = cursor.fetchone()
        
        # Converter resultado para dicionário
        if row is not None and cursor.description:
            columns = [desc[0] for desc in cursor.description]
            resultado = dict(zip(columns, row))
        else:
            resultado = None
        
        cursor.close()
        conn.close()
        
        return resultado
    except Exception as e:
        print(f"Erro ao buscar edição {edicao}: {e}")
        return None

# Função para atualizar status de envio
def atualizar_status_envio(edicao):
    """Atualiza status_envio_link para 'enviado'"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if not conn.is_connected():
            print("Erro: Não foi possível conectar ao banco de dados")
            return
            
        cursor = conn.cursor()
        
        query = "UPDATE extracoes_cadastro SET status_envio_link = 'enviado' WHERE edicao = %s"
        cursor.execute(query, (edicao,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"Status de envio atualizado para edição {edicao}")
    except Exception as e:
        print(f"Erro ao atualizar status de envio para edição {edicao}: {e}")

# Função para enviar mensagem para WhatsApp com retry automático
def enviar_mensagem_whatsapp(link, extracao, edicao, sigla_oficial):
    """Envia mensagem para WhatsApp com imagem e link, com sistema de retry"""
    
    caminho_imagem = buscar_imagem(extracao)
    if not caminho_imagem:
        print(f"ERRO: Imagem {extracao} não encontrada no diretório {caminho_imagens}.")
        return False

    texto_msg = montar_texto(link)

    # Converter imagem para base64
    try:
        with open(caminho_imagem, "rb") as img_file:
            imagem_base64 = base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Erro ao ler imagem {caminho_imagem}: {e}")
        return False

    # Montar o payload
    payload = {
        "number": id_grupo,
        "mediatype": "image",
        "mimetype": "image/jpeg",
        "caption": texto_msg,
        "media": imagem_base64,
        "fileName": os.path.basename(caminho_imagem),
    }

    # Cabeçalhos da requisição
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }

    # Sistema de retry - tentar até MAX_TENTATIVAS vezes
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            print(f"  Tentativa {tentativa}/{MAX_TENTATIVAS}...")
            
            response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT_REQUISICAO)
            
            if response.status_code in [200, 201]:
                print(f"  [OK] SUCESSO na tentativa {tentativa}! Mensagem enviada - Edição: {edicao}")
                return True
            else:
                print(f"  [ERRO] Falha na tentativa {tentativa}. Status Code: {response.status_code}")
                
                # Se não é a última tentativa, aguardar antes de tentar novamente
                if tentativa < MAX_TENTATIVAS:
                    print(f"  [WAIT] Aguardando {DELAY_ENTRE_TENTATIVAS}s antes da próxima tentativa...")
                    time.sleep(DELAY_ENTRE_TENTATIVAS)
                    
        except requests.exceptions.Timeout:
            print(f"  [TIMEOUT] Timeout na tentativa {tentativa} (>{TIMEOUT_REQUISICAO}s)")
            if tentativa < MAX_TENTATIVAS:
                print(f"  [WAIT] Aguardando {DELAY_ENTRE_TENTATIVAS}s antes da próxima tentativa...")
                time.sleep(DELAY_ENTRE_TENTATIVAS)
                
        except requests.exceptions.RequestException as e:
            print(f"  [ERRO] Erro de conexão na tentativa {tentativa}: {e}")
            if tentativa < MAX_TENTATIVAS:
                print(f"  [WAIT] Aguardando {DELAY_ENTRE_TENTATIVAS}s antes da próxima tentativa...")
                time.sleep(DELAY_ENTRE_TENTATIVAS)
    
    # Se chegou aqui, todas as tentativas falharam
    print(f"  [FALHA] FALHA TOTAL: Todas as {MAX_TENTATIVAS} tentativas falharam para edição {edicao}")
    return False

def main():
    print("=== Script de Envio de Links para WhatsApp ===")
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        # Modo: enviar edições específicas
        edicoes = []
        for arg in sys.argv[1:]:
            try:
                edicao = int(arg)
                edicoes.append(edicao)
            except ValueError:
                print(f"ERRO: '{arg}' não é um número de edição válido")
                print("Uso: python novo_chamadas_group_latest.py [numero_edicao1] [numero_edicao2] ...")
                return
        
        if not edicoes:
            print("ERRO: Nenhuma edição válida informada")
            print("Uso: python novo_chamadas_group_latest.py [numero_edicao1] [numero_edicao2] ...")
            return
        
        print(f"Modo: Enviar {len(edicoes)} edição(ões) específica(s): {', '.join(map(str, edicoes))}")
        
        sucessos = 0
        falhas = 0
        
        for i, edicao in enumerate(edicoes, 1):
            print(f"\n[{i}/{len(edicoes)}] Processando edição {edicao}...")
            
            resultado = buscar_link_por_edicao(edicao)
            if resultado:
                link = resultado['link']
                extracao = resultado['extracao']
                sigla_oficial = resultado['sigla_oficial']
                
                print(f"  [ENVIO] Enviando: Edição {edicao} - Sigla: {sigla_oficial}")
                sucesso = enviar_mensagem_whatsapp(link, extracao, edicao, sigla_oficial)
                
                if sucesso:
                    sucessos += 1
                    print(f"  [OK] SUCESSO: Edição {edicao} enviada!")
                else:
                    falhas += 1
                    print(f"  [ERRO] FALHA: Edição {edicao} não pôde ser enviada")
            else:
                falhas += 1
                print(f"  [ERRO] ERRO: Edição {edicao} não encontrada na tabela extracoes_cadastro")
        
        # Estatísticas finais
        total = sucessos + falhas
        taxa_sucesso = (sucessos / total * 100) if total > 0 else 0
        
        print(f"\n=== RELATÓRIO FINAL ===")
        print(f"[OK] Sucessos: {sucessos}")
        print(f"[ERRO] Falhas: {falhas}")
        print(f"[TAXA] Taxa de sucesso: {taxa_sucesso:.1f}%")
        print(f"[TOTAL] Total processado: {total}")
                
    else:
        # Modo: enviar links pendentes
        print("Modo: Enviar links pendentes")
        
        links_pendentes = buscar_links_pendentes()
        
        if not links_pendentes:
            print("Nenhum link pendente encontrado.")
            return
        
        print(f"Encontrados {len(links_pendentes)} links pendentes para enviar.")
        
        sucessos = 0
        falhas = 0
        
        for i, registro in enumerate(links_pendentes, 1):
            link = registro['link']
            extracao = registro['extracao']
            edicao = registro['edicao']
            sigla_oficial = registro['sigla_oficial']
            
            print(f"\n[{i}/{len(links_pendentes)}] Processando edição {edicao} - Sigla: {sigla_oficial}")
            
            sucesso = enviar_mensagem_whatsapp(link, extracao, edicao, sigla_oficial)
            
            if sucesso:
                sucessos += 1
                # Atualizar status para 'enviado'
                atualizar_status_envio(edicao)
                print(f"  [OK] Status atualizado para 'enviado'")
            else:
                falhas += 1
                print(f"  [ERRO] Status mantido como 'pendente' devido à falha")
            
            # Pausa entre envios (só se não for o último)
            if i < len(links_pendentes):
                print(f"  [WAIT] Aguardando 3s antes do próximo envio...")
                time.sleep(3)
        
        # Estatísticas finais
        total = sucessos + falhas
        taxa_sucesso = (sucessos / total * 100) if total > 0 else 0
        
        print(f"\n=== RELATÓRIO FINAL ===")
        print(f"[OK] Sucessos: {sucessos}")
        print(f"[ERRO] Falhas: {falhas}")
        print(f"[TAXA] Taxa de sucesso: {taxa_sucesso:.1f}%")
        print(f"[TOTAL] Total processado: {total}")
        
        if falhas > 0:
            print(f"\n[AVISO] ATENÇÃO: {falhas} links permaneceram como 'pendente'")
            print("        Execute o script novamente para tentar reenviar os que falharam.")

if __name__ == "__main__":
    main()
