import re
from scripts.alimenta_premiados import conectar_banco

def calcular_valor_real(premio):
    # Extrai valor em reais
    valor_reais = 0.0
    match_reais = re.search(r'R\$\s*([\d\.]+,\d{2})', premio)
    if match_reais:
        valor_reais = float(match_reais.group(1).replace('.', '').replace(',', '.'))
    
    # Extrai cotas
    match_cotas = re.search(r'(\d+)\s+COTAS?\s+DO\s+SORTEIO\s+DA\s+(.+)', premio, re.IGNORECASE)
    valor_cotas = 0.0
    if match_cotas:
        qtd_cotas = int(match_cotas.group(1))
        nome_cota = match_cotas.group(2).strip().upper()
        # Buscar valor_cota no banco
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
