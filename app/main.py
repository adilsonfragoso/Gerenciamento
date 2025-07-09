import logging
logger = logging.getLogger(__name__)
from fastapi import FastAPI, HTTPException, Body, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import pymysql
from pymysql.cursors import DictCursor
from .crud import get_all_siglas, get_premiacao_by_id
from .db_config import DB_CONFIG
import shutil
from PIL import Image
import uuid
from datetime import datetime
import ftplib
import io
import requests
import subprocess
import sys
import re
import time

# Configurar logging adequadamente
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tentar importar pytz para fuso horário, se não estiver disponível usar fallback
try:
    import pytz
    USE_PYTZ = True
except ImportError:
    USE_PYTZ = False
    print("Aviso: pytz não está disponível. Usando fuso horário local.")

# Configuração para upload de imagens na VPS externa
VPS_FTP_CONFIG = {
    'host': 'pma.megatrends.site',  # Mesmo host do MySQL
    'user': 'root',  # Ajuste conforme suas credenciais FTP
    'password': 'Define@4536#8521',  # Ajuste conforme suas credenciais FTP
    'upload_path': '/uploads/'  # Caminho na VPS onde as imagens serão salvas
}

# Configurações de upload
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
TEMP_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "temp")

# Criar diretórios se não existirem
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

# Modelo para validar os dados recebidos (ex: campos monetários, "parametros", etc.)
class PremiacaoUpdate(BaseModel):
    sigla: str
    horario: Optional[str] = None
    precocota: Optional[float] = Field(None, alias="precocota")
    primeiro: Optional[str] = None
    segundo: Optional[str] = None
    terceiro: Optional[str] = None
    quarto: Optional[str] = None
    quinto: Optional[str] = None
    sexto: Optional[str] = None
    setimo: Optional[str] = None
    oitavo: Optional[str] = None
    nono: Optional[str] = None
    decimo: Optional[str] = None
    decimo_primeiro: Optional[str] = None
    decimo_segundo: Optional[str] = None
    decimo_terceiro: Optional[str] = None
    decimo_quarto: Optional[str] = None
    numeracao: Optional[str] = None
    totalpremios: Optional[int] = None
    totalpremios_oficial: Optional[int] = None
    totalpremiacao: Optional[float] = Field(None, alias="totalpremiacao")
    premiosextras: Optional[float] = Field(None, alias="premiosextras")
    arrecad: Optional[float] = Field(None, alias="arrecad")
    lucro: Optional[float] = Field(None, alias="lucro")
    parametros: Optional[str] = None
    imagem_path: Optional[str] = None

# Modelo para validar os dados recebidos no PUT (atualizar) – onde sigla é opcional (para permitir atualizar sem enviar sigla).
class PremiacaoUpdatePartial(BaseModel):
    sigla: Optional[str] = None
    horario: Optional[str] = None
    precocota: Optional[float] = Field(None, alias="precocota")
    primeiro: Optional[str] = None
    segundo: Optional[str] = None
    terceiro: Optional[str] = None
    quarto: Optional[str] = None
    quinto: Optional[str] = None
    sexto: Optional[str] = None
    setimo: Optional[str] = None
    oitavo: Optional[str] = None
    nono: Optional[str] = None
    decimo: Optional[str] = None
    decimo_primeiro: Optional[str] = None
    decimo_segundo: Optional[str] = None
    decimo_terceiro: Optional[str] = None
    decimo_quarto: Optional[str] = None
    numeracao: Optional[str] = None
    totalpremios: Optional[int] = None
    totalpremios_oficial: Optional[int] = None
    totalpremiacao: Optional[float] = Field(None, alias="totalpremiacao")
    premiosextras: Optional[float] = Field(None, alias="premiosextras")
    arrecad: Optional[float] = Field(None, alias="arrecad")
    lucro: Optional[float] = Field(None, alias="lucro")
    parametros: Optional[str] = None
    imagem_path: Optional[str] = None

class SiglasDiariasCreate(BaseModel):
    data_sorteio: str
    siglas: str

class ScriptExecuteRequest(BaseModel):
    data_sorteio: str
    siglas: str

class SiglaAvulsaCreate(BaseModel):
    data_sorteio: str
    dia_semana: str
    siglas: str
    tipo: str = 'extra'

class ExcluirSiglasRequest(BaseModel):
    id: int

app = FastAPI()

# Servir arquivos estáticos (frontend)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../static")), name="static")

# Servir imagens uploadadas
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Servir imagens da pasta img
app.mount("/img", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../img")), name="img")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "../static/dashboard.html"))

@app.get("/editar")
def serve_editar():
    # Limpar arquivos temporários automaticamente ao entrar na edição
    try:
        import glob
        temp_pattern = os.path.join(TEMP_UPLOAD_DIR, "*")
        temp_files = glob.glob(temp_pattern)
        
        removed_count = 0
        for temp_file in temp_files:
            if os.path.isfile(temp_file):
                os.remove(temp_file)
                removed_count += 1
        
        if removed_count > 0:
            print(f"Limpeza automática: {removed_count} arquivos temporários removidos")
            
    except Exception as e:
        print(f"Erro na limpeza automática: {e}")
    
    return FileResponse(os.path.join(os.path.dirname(__file__), "../static/editar.html"))

@app.get("/premiacoes")
def serve_premiacoes():
    return FileResponse(os.path.join(os.path.dirname(__file__), "../static/premiacoes.html"))

@app.get("/edicoes")
def serve_edicoes():
    return FileResponse(os.path.join(os.path.dirname(__file__), "../static/edicoes.html"))

@app.get("/dashboard")
def serve_dashboard():
    return FileResponse(os.path.join(os.path.dirname(__file__), "../static/dashboard.html"))

@app.get("/teste-sigla-avulsa")
def serve_teste_sigla_avulsa():
    return FileResponse(os.path.join(os.path.dirname(__file__), "../test_sigla_avulsa.html"))

@app.get("/api/edicoes")
def listar_edicoes():
    """Consulta a tabela siglas_diarias retornando diaSemana, data_sorteio e siglas dos últimos 14 dias, com verificação de pendências"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        
        # Query principal para buscar edições
        query = """
        SELECT id, diaSemana, data_sorteio, siglas 
        FROM siglas_diarias 
        WHERE data_sorteio >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        ORDER BY data_sorteio DESC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        # Para cada edição, verificar se há pendências na tabela extracoes_cadastro
        for resultado in resultados:
            data_sorteio = resultado['data_sorteio'] if resultado and 'data_sorteio' in resultado else None
            if not data_sorteio:
                resultado['tem_pendencias'] = False
                continue
            # Verificar se há registros pendentes para esta data
            query_pendentes = """
            SELECT COUNT(*) as total_pendentes
            FROM extracoes_cadastro 
            WHERE data_sorteio = %s 
            AND status_cadastro != 'cadastrado'
            """
            cursor.execute(query_pendentes, (data_sorteio,))
            pendentes = cursor.fetchone()
            resultado['tem_pendencias'] = pendentes['total_pendentes'] > 0 if pendentes and 'total_pendentes' in pendentes else False
        
        cursor.close()
        connection.close()
        
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar edições: {str(e)}")

@app.get("/api/edicoes/ultima-data")
def obter_ultima_data():
    """Retorna a data do último sorteio para definir a data padrão"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        
        query = """
        SELECT data_sorteio 
        FROM siglas_diarias 
        ORDER BY data_sorteio DESC 
        LIMIT 1
        """
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if resultado and 'data_sorteio' in resultado:
            from datetime import datetime, timedelta
            ultima_data = resultado['data_sorteio']
            # Se for string, converter para datetime
            if isinstance(ultima_data, str):
                ultima_data = datetime.strptime(ultima_data, '%Y-%m-%d')
            # Adicionar 1 dia
            proxima_data = ultima_data + timedelta(days=1)
            return {"proxima_data": proxima_data.strftime('%Y-%m-%d')}
        else:
            from datetime import datetime
            data_atual = datetime.now()
            return {"proxima_data": data_atual.strftime('%Y-%m-%d')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter última data: {str(e)}")

@app.get("/api/edicoes/siglas-por-grupo/{data}")
def obter_siglas_por_grupo(data: str):
    """Retorna as siglas dos últimos 3 registros do mesmo grupo da data informada"""
    try:
        from datetime import datetime
        # Converter a data para objeto datetime
        data_obj = datetime.strptime(data, '%Y-%m-%d')
        # Determinar o grupo baseado no dia da semana
        dia_semana = data_obj.strftime('%A').lower()
        # Mapear dias da semana para grupos
        grupos = {
            'monday': 1,    # segunda-feira - Grupo 1
            'tuesday': 1,   # terça-feira - Grupo 1
            'wednesday': 2, # quarta-feira - Grupo 2
            'thursday': 1,  # quinta-feira - Grupo 1
            'friday': 1,    # sexta-feira - Grupo 1
            'saturday': 2,  # sábado - Grupo 2
            'sunday': 3     # domingo - Grupo 3
        }
        grupo = grupos.get(dia_semana, 1)
        # Definir quais dias da semana pertencem ao grupo
        dias_grupo = {
            1: ['monday', 'tuesday', 'thursday', 'friday'],  # Grupo 1: segunda, terça, quinta, sexta
            2: ['wednesday', 'saturday'],                    # Grupo 2: quarta, sábado
            3: ['sunday']                                    # Grupo 3: domingo
        }
        dias_do_grupo = dias_grupo[grupo]
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        # Converter dias da semana para números do MySQL (1=domingo, 2=segunda, ..., 7=sábado)
        dias_numeros = []
        for dia in dias_do_grupo:
            if dia == 'sunday': dias_numeros.append(1)
            elif dia == 'monday': dias_numeros.append(2)
            elif dia == 'tuesday': dias_numeros.append(3)
            elif dia == 'wednesday': dias_numeros.append(4)
            elif dia == 'thursday': dias_numeros.append(5)
            elif dia == 'friday': dias_numeros.append(6)
            elif dia == 'saturday': dias_numeros.append(7)
        dias_str = ','.join(map(str, dias_numeros))
        query = f"""
        SELECT diaSemana, data_sorteio, siglas 
        FROM siglas_diarias 
        WHERE data_sorteio < %s 
        AND DAYOFWEEK(data_sorteio) IN ({dias_str})
        AND (tipo IS NULL OR tipo != 'extra')
        ORDER BY data_sorteio DESC 
        LIMIT 3
        """
        cursor.execute(query, (data,))
        resultados = cursor.fetchall()
        cursor.close()
        connection.close()
        return {
            "grupo": grupo,
            "data_selecionada": data,
            "siglas": resultados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter siglas por grupo: {str(e)}")

@app.get("/api/premiacoes")
def listar_premiacoes():
    """Lista todas as premiações em ordem crescente por sigla"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        query = """
        SELECT id, sigla 
        FROM premiacoes 
        ORDER BY
          CASE
            WHEN sigla REGEXP '^PPT(_| |$)' THEN 1
            WHEN sigla REGEXP '^PTM(_| |$)' THEN 2
            WHEN sigla REGEXP '^PT(_| |$)' THEN 3
            WHEN sigla REGEXP '^PTV(_| |$)' THEN 4
            WHEN sigla REGEXP '^PTN(_| |$)' THEN 5
            WHEN sigla REGEXP '^FEDERAL(_| |$)' THEN 6
            WHEN sigla REGEXP '^CORUJINHA(_| |$)' THEN 7
            ELSE 8
          END,
          CAST(
            IF(sigla REGEXP '^[A-Z]+_[0-9]+', SUBSTRING_INDEX(sigla, '_', -1), '0')
            AS UNSIGNED
          ),
          sigla
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        connection.close()
        return [r for r in resultados if r and 'id' in r and 'sigla' in r]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar premiações: {str(e)}")

@app.get("/siglas")
def listar_siglas():
    siglas = get_all_siglas()
    return [{"id": s[0], "sigla": s[1]} for s in siglas]

@app.get("/premiacao/{premiacao_id}")
def detalhar_premiacao(premiacao_id: int):
    dado = get_premiacao_by_id(premiacao_id)
    if not dado:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return dado

# Endpoint para upload temporário de imagem
@app.post("/upload-imagem-temp")
async def upload_imagem_temp(file: UploadFile = File(...)):
    # Validar tipo de arquivo - apenas JPG/JPEG
    if not file.content_type or not file.content_type.lower() in ['image/jpeg', 'image/jpg']:
        raise HTTPException(status_code=400, detail="Apenas arquivos JPG/JPEG são permitidos")
    
    # Validar extensão do arquivo
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome não permitido")
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ['.jpg', '.jpeg']:
        raise HTTPException(status_code=400, detail="Apenas arquivos com extensão .jpg ou .jpeg são permitidos")
    
    # Validar tamanho (máximo 10MB)
    file.file.seek(0, 2)  # Move para o final do arquivo
    file_size = file.file.tell()
    file.file.seek(0)  # Volta para o início
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo 10MB")
    
    try:
        # Gerar nome único temporário
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        temp_filename = f"temp_{timestamp}_{unique_id}.jpg"
        temp_file_path = os.path.join(TEMP_UPLOAD_DIR, temp_filename)
        
        # Salvar arquivo temporário
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Retornar caminho relativo para o frontend
        temp_path = f"uploads/temp/{temp_filename}"
        
        return {
            "success": True,
            "temp_path": temp_path,
            "message": "Upload temporário realizado com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload temporário: {str(e)}")

# Endpoint para confirmar upload temporário
@app.post("/confirmar-upload")
async def confirmar_upload(temp_path: str = Form(...), sigla: str = Form(...)):
    try:
        # Extrair nome do arquivo temporário
        temp_filename = os.path.basename(temp_path)
        temp_file_path = os.path.join(TEMP_UPLOAD_DIR, temp_filename)
        
        # Verificar se arquivo temporário existe
        if not os.path.exists(temp_file_path):
            raise HTTPException(status_code=404, detail="Arquivo temporário não encontrado")
        
        # Usar a sigla exatamente como está no campo input
        # Gerar nome final do arquivo
        final_filename = f"{sigla}.jpg"
        final_file_path = os.path.join(UPLOAD_DIR, final_filename)
        
        # Se já existe arquivo com o nome final, removê-lo
        if os.path.exists(final_file_path):
            os.remove(final_file_path)
        
        # Mover arquivo temporário para nome final
        shutil.move(temp_file_path, final_file_path)
        
        # Retornar caminho final
        final_path = f"uploads/{final_filename}"
        
        return {
            "success": True,
            "path": final_path,
            "filename": final_filename,
            "message": "Upload confirmado com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao confirmar upload: {str(e)}")

# Endpoint para limpar uploads temporários
@app.post("/limpar-uploads-temp")
async def limpar_uploads_temp():
    try:
        import time
        import glob
        
        # Buscar todos os arquivos na pasta temp
        temp_pattern = os.path.join(TEMP_UPLOAD_DIR, "*")
        temp_files = glob.glob(temp_pattern)
        
        # Remover todos os arquivos temporários (independente da idade)
        removed_count = 0
        
        for temp_file in temp_files:
            if os.path.isfile(temp_file):
                os.remove(temp_file)
                removed_count += 1
        
        return {
            "success": True,
            "removed_count": removed_count,
            "message": f"{removed_count} arquivos temporários removidos"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar uploads temporários: {str(e)}")

# Endpoint para criar (POST) um novo registro de premiação.
@app.post("/premiacao")
def criar_premiacao(premiacao: PremiacaoUpdate = Body(...)):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            # Monta a query de INSERT com todos os campos
            campos = []
            values = []
            for k, v in premiacao.dict(exclude_unset=True).items():
                if k == "imagem_path" and (v is None or v == ""):
                    campos.append(k)
                    values.append(None)
                elif v is not None:
                    campos.append(k)
                    values.append(v)
            if not campos:
                raise HTTPException(status_code=400, detail="Nenhum campo enviado para criar.")
            placeholders = ", ".join(["%s"] * len(campos))
            query = f"INSERT INTO premiacoes ({', '.join(campos)}) VALUES ({placeholders})"
            cursor.execute(query, values)
            conn.commit()
            return {"detail": "Registro criado com sucesso."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar registro: {e}")
    finally:
        conn.close()

# Endpoint para atualizar (PUT) um registro de premiação (sobrescrevendo o registro inteiro com os dados enviados).
@app.put("/premiacao/{premiacao_id}")
def atualizar_premiacao(premiacao_id: int, premiacao: PremiacaoUpdatePartial = Body(...)):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            # Primeiro verificar se o registro existe
            cursor.execute("SELECT id FROM premiacoes WHERE id = %s", (premiacao_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Registro não encontrado.")
            
            # Monta a query de UPDATE
            campos = []
            values = []
            for k, v in premiacao.dict(exclude_unset=True).items():
                if k == "imagem_path" and (v is None or v == ""):
                    campos.append(k)
                    values.append(None)
                elif v is not None:
                    campos.append(k)
                    values.append(v)
            if not campos:
                raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualizar.")
            set_clause = ", ".join([f"{k}=%s" for k in campos])
            query = f"UPDATE premiacoes SET {set_clause} WHERE id=%s"
            values.append(premiacao_id)
            cursor.execute(query, values)
            conn.commit()
            return {"detail": "Registro atualizado com sucesso."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar registro: {e}")
    finally:
        conn.close()

# Endpoint para cadastrar siglas diárias
@app.post("/api/edicoes/cadastrar-siglas")
def cadastrar_siglas_diarias(dados: SiglasDiariasCreate):
    """
    Cadastra siglas diárias na tabela siglas_diarias
    
    Args:
        dados: Objeto com data_sorteio e siglas
    """
    try:
        from datetime import datetime
        
        # Validar formato da data
        try:
            data_obj = datetime.strptime(dados.data_sorteio, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
        
        # Calcular dia da semana no formato 'segunda-feira', 'terça-feira', etc.
        dias_mapping = {
            0: 'segunda-feira',
            1: 'terça-feira',
            2: 'quarta-feira',
            3: 'quinta-feira',
            4: 'sexta-feira',
            5: 'sábado',
            6: 'domingo'
        }
        dia_semana_idx = data_obj.weekday()
        # Ajuste: Python weekday() começa em 0=segunda, 6=domingo
        if dia_semana_idx == 6:
            dia_semana_str = 'domingo'
        else:
            dia_semana_str = dias_mapping[dia_semana_idx]
        
        # Validar siglas
        if not dados.siglas or not dados.siglas.strip():
            raise HTTPException(status_code=400, detail="Siglas não podem estar vazias")
        
        # Limpar e validar siglas
        siglas_list = [s.strip() for s in dados.siglas.split(',') if s.strip()]
        if not siglas_list:
            raise HTTPException(status_code=400, detail="Nenhuma sigla válida encontrada")
        
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        try:
            # Verificar se já existe registro para esta data
            check_query = "SELECT id FROM siglas_diarias WHERE data_sorteio = %s"
            cursor.execute(check_query, (dados.data_sorteio,))
            existing = cursor.fetchone()
            
            if existing:
                raise HTTPException(status_code=409, detail=f"Já existe registro para a data {dados.data_sorteio}")
            
            # Inserir registro (sem created_at, com campo tipo vazio)
            insert_query = """
            INSERT INTO siglas_diarias (diaSemana, data_sorteio, siglas, tipo)
            VALUES (%s, %s, %s, '')
            """
            
            siglas_str = ', '.join(siglas_list)
            cursor.execute(insert_query, (dia_semana_str, dados.data_sorteio, siglas_str))
            connection.commit()
            
            registro_id = cursor.lastrowid
            
            # --- NOVO FLUXO: Alimentar extracoes_cadastro ---
            try:
                # 1. Buscar maior edição em extracoes_cadastro
                connection2 = pymysql.connect(**DB_CONFIG)
                cursor2 = connection2.cursor()
                cursor2.execute("SELECT MAX(edicao) FROM extracoes_cadastro")
                res = cursor2.fetchone()
                max_edicao = res[0] if res and res[0] is not None else 0
                proxima_edicao = max_edicao + 1
                edicao_atual = proxima_edicao
                
                # 2. Para cada sigla informada (ignorando 'GRUPO')
                for sigla in siglas_list:
                    if 'GRUPO' in sigla.upper():
                        continue  # Ignorar grupos
                    sigla_oficial = sigla.split('_')[0] if '_' in sigla else sigla
                    extracao = sigla
                    data_sorteio = dados.data_sorteio
                    # Gerar link conforme regra do script antigo
                    base_url = 'https://litoraldasorte.com/campanha/'
                    if sigla_oficial.upper() in ['FEDERAL', 'FEDERAL ESPECIAL']:
                        titulo = f"{sigla_oficial.upper()} EDIÇÃO {edicao_atual}"
                    else:
                        titulo = f"{sigla_oficial.upper()} RJ EDIÇÃO {edicao_atual}"
                    slug = titulo.lower().replace(' ', '-').replace('edição', 'edicao')
                    link = base_url + slug
                    # Buscar dados em premiacoes
                    cursor2.execute("SELECT * FROM premiacoes WHERE sigla = %s LIMIT 1", (sigla,))
                    premiacao = cursor2.fetchone()
                    if not premiacao:
                        raise HTTPException(status_code=400, detail=f"Sigla '{sigla}' não encontrada na tabela premiacoes. Corrija e tente novamente.")
                    
                    # Montar campos para extracoes_cadastro (dados de controle)
                    insert_cols_cadastro = [
                        'data_sorteio', 'edicao', 'sigla_oficial', 'extracao', 'link',
                        'status_cadastro', 'status_link', 'error_msg', 'id_siglas_diarias'
                    ]
                    insert_values_cadastro = [
                        data_sorteio, edicao_atual, sigla_oficial, extracao, link,
                        'pendente', 'pendente', '', registro_id
                    ]
                    
                    # Montar campos para extracoes_premiacao (dados de premiação)
                    insert_cols_premiacao = [
                        'edicao', 'horario', 'precocota', 'primeiro', 'segundo', 'terceiro', 'quarto', 'quinto',
                        'sexto', 'setimo', 'oitavo', 'nono', 'decimo',
                        'decimo_primeiro', 'decimo_segundo', 'decimo_terceiro', 'decimo_quarto',
                        'numeracao', 'totalpremios', 'totalpremios_oficial', 'totalpremiacao',
                        'premiosextras', 'arrecad', 'lucro', 'id_siglas_diarias'
                    ]
                    insert_values_premiacao = [
                        edicao_atual,
                        premiacao[2], premiacao[3], premiacao[4], premiacao[5], premiacao[6], premiacao[7], premiacao[8],
                        premiacao[9], premiacao[10], premiacao[11], premiacao[12], premiacao[13],
                        premiacao[14], premiacao[15], premiacao[16], premiacao[17],
                        premiacao[18], premiacao[19], premiacao[20], premiacao[21],
                        premiacao[22], premiacao[23], premiacao[24], registro_id
                    ]
                    
                    # Verificar se já existe a mesma sigla, data e edição
                    cursor2.execute("SELECT COUNT(*) FROM extracoes_cadastro WHERE sigla_oficial=%s AND data_sorteio=%s AND edicao=%s", (sigla_oficial, data_sorteio, edicao_atual))
                    res = cursor2.fetchone()
                    if res and res[0] == 0:
                        # Inserir em extracoes_cadastro
                        insert_sql_cadastro = f"INSERT INTO extracoes_cadastro ({', '.join(insert_cols_cadastro)}) VALUES ({', '.join(['%s']*len(insert_cols_cadastro))})"
                        cursor2.execute(insert_sql_cadastro, insert_values_cadastro)
                        
                        # Inserir em extracoes_premiacao
                        insert_sql_premiacao = f"INSERT INTO extracoes_premiacao ({', '.join(insert_cols_premiacao)}) VALUES ({', '.join(['%s']*len(insert_cols_premiacao))})"
                        cursor2.execute(insert_sql_premiacao, insert_values_premiacao)
                        
                        connection2.commit()
                    edicao_atual += 1
                cursor2.close()
                connection2.close()
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro ao alimentar extracoes_cadastro: {str(e)}")
            # --- FIM NOVO FLUXO ---
            
            return {
                "success": True,
                "message": f"Siglas cadastradas com sucesso para {dados.data_sorteio}",
                "data": {
                    "id": registro_id,
                    "data_sorteio": dados.data_sorteio,
                    "dia_semana": dia_semana_str,
                    "siglas": siglas_list,
                    "siglas_str": siglas_str
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            connection.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao cadastrar siglas: {str(e)}")
        finally:
            cursor.close()
            connection.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

# Endpoint para executar script cadRifas_litoral_latest
@app.post("/api/edicoes/executar-script")
def executar_script_cadrifas(dados: ScriptExecuteRequest):
    """
    Executa o script cadRifas_litoral_latest com os parâmetros fornecidos
    
    Args:
        dados: Objeto com data_sorteio e siglas
    """
    try:
        import sys
        import os
        from datetime import datetime
        
        # Validar formato da data
        try:
            data_obj = datetime.strptime(dados.data_sorteio, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
        
        # Validar siglas
        if not dados.siglas or not dados.siglas.strip():
            raise HTTPException(status_code=400, detail="Siglas não podem estar vazias")
        
        # Limpar e validar siglas
        siglas_list = [s.strip() for s in dados.siglas.split(',') if s.strip()]
        if not siglas_list:
            raise HTTPException(status_code=400, detail="Nenhuma sigla válida encontrada")
        
        # Converter data para formato DD/MM/AAAA (formato esperado pelo script)
        data_formatada = data_obj.strftime('%d/%m/%Y')
        
        # Primeiro, cadastrar as siglas na tabela siglas_diarias
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        try:
            # Determinar dia da semana
            dia_semana = data_obj.strftime('%A').lower()
            dias_pt = {
                'monday': 'segunda',
                'tuesday': 'terça', 
                'wednesday': 'quarta',
                'thursday': 'quinta',
                'friday': 'sexta',
                'saturday': 'sábado',
                'sunday': 'domingo'
            }
            dia_semana_pt = dias_pt.get(dia_semana, dia_semana)
            
            # Cadastrar na tabela siglas_diarias
            insert_siglas_query = """
            INSERT INTO siglas_diarias (diaSemana, data_sorteio, siglas, tipo)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_siglas_query, (dia_semana_pt, dados.data_sorteio, dados.siglas, 'normal'))
            connection.commit()
            siglas_diarias_id = cursor.lastrowid
            
            logger.info(f"Registro criado na tabela siglas_diarias com ID: {siglas_diarias_id}")
            
            # Buscar maior edição em extracoes_cadastro
            cursor.execute("SELECT MAX(edicao) FROM extracoes_cadastro")
            res = cursor.fetchone()
            max_edicao = res[0] if res and res[0] is not None else 0
            edicao_atual = max_edicao + 1
            
            edicoes_criadas = []
            
            for sigla in siglas_list:
                if 'GRUPO' not in sigla.upper():
                    sigla_oficial = sigla.split('_')[0] if '_' in sigla else sigla
                    extracao = sigla
                    data_sorteio = dados.data_sorteio
                    
                    # Gerar link conforme regra do script
                    base_url = 'https://litoraldasorte.com/campanha/'
                    if sigla_oficial.upper() in ['FEDERAL', 'FEDERAL ESPECIAL']:
                        titulo = f"{sigla_oficial.upper()} EDIÇÃO {edicao_atual}"
                    else:
                        titulo = f"{sigla_oficial.upper()} RJ EDIÇÃO {edicao_atual}"
                    slug = titulo.lower().replace(' ', '-').replace('edição', 'edicao')
                    link = base_url + slug
                    
                    # Buscar dados em premiacoes
                    cursor.execute("SELECT * FROM premiacoes WHERE sigla = %s LIMIT 1", (sigla,))
                    premiacao = cursor.fetchone()
                    if not premiacao:
                        raise HTTPException(status_code=400, detail=f"Sigla '{sigla}' não encontrada na tabela premiacoes. Corrija e tente novamente.")
                    
                    # Montar campos para extracoes_cadastro (dados de controle)
                    insert_cols_cadastro = [
                        'data_sorteio', 'edicao', 'sigla_oficial', 'extracao', 'link',
                        'status_cadastro', 'status_link', 'error_msg', 'id_siglas_diarias'
                    ]
                    insert_values_cadastro = [
                        data_sorteio, edicao_atual, sigla_oficial, extracao, link,
                        'pendente', 'pendente', '', siglas_diarias_id
                    ]
                    
                    # Montar campos para extracoes_premiacao (dados de premiação)
                    insert_cols_premiacao = [
                        'edicao', 'horario', 'precocota', 'primeiro', 'segundo', 'terceiro', 'quarto', 'quinto',
                        'sexto', 'setimo', 'oitavo', 'nono', 'decimo',
                        'decimo_primeiro', 'decimo_segundo', 'decimo_terceiro', 'decimo_quarto',
                        'numeracao', 'totalpremios', 'totalpremios_oficial', 'totalpremiacao',
                        'premiosextras', 'arrecad', 'lucro', 'id_siglas_diarias'
                    ]
                    insert_values_premiacao = [
                        edicao_atual,
                        premiacao[2], premiacao[3], premiacao[4], premiacao[5], premiacao[6], premiacao[7], premiacao[8],
                        premiacao[9], premiacao[10], premiacao[11], premiacao[12], premiacao[13],
                        premiacao[14], premiacao[15], premiacao[16], premiacao[17],
                        premiacao[18], premiacao[19], premiacao[20], premiacao[21],
                        premiacao[22], premiacao[23], premiacao[24], siglas_diarias_id
                    ]
                    
                    # Verificar se já existe a mesma sigla, data e edição
                    cursor.execute("SELECT COUNT(*) FROM extracoes_cadastro WHERE sigla_oficial=%s AND data_sorteio=%s AND edicao=%s", (sigla_oficial, data_sorteio, edicao_atual))
                    res = cursor.fetchone()
                    if res and res[0] == 0:
                        # Inserir em extracoes_cadastro
                        insert_sql_cadastro = f"INSERT INTO extracoes_cadastro ({', '.join(insert_cols_cadastro)}) VALUES ({', '.join(['%s']*len(insert_cols_cadastro))})"
                        cursor.execute(insert_sql_cadastro, insert_values_cadastro)
                        
                        # Inserir em extracoes_premiacao
                        insert_sql_premiacao = f"INSERT INTO extracoes_premiacao ({', '.join(insert_cols_premiacao)}) VALUES ({', '.join(['%s']*len(insert_cols_premiacao))})"
                        cursor.execute(insert_sql_premiacao, insert_values_premiacao)
                        
                        connection.commit()
                        edicoes_criadas.append(edicao_atual)
                        edicao_atual += 1
                
                connection.commit()
            
            cursor.close()
            connection.close()
            
            logger.info(f"Registros criados na tabela extracoes_cadastro: {edicoes_criadas}")
            
        except Exception as e:
            connection.rollback()
            cursor.close()
            connection.close()
            raise HTTPException(status_code=500, detail=f"Erro ao cadastrar siglas na tabela extracoes_cadastro: {str(e)}")
        
        # Verificar se o script existe
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'cadRifas_litoral_latest.py')
        if not os.path.exists(script_path):
            raise HTTPException(status_code=500, detail="Script cadRifas_litoral_latest.py não encontrado")
        
        # Preparar comando (sem argumentos, pois o script lê da tabela)
        comando = [
            sys.executable,  # Python interpreter
            script_path
        ]
        
        # Preparar ambiente de execução
        env = os.environ.copy()
        
        # Adicionar variáveis de ambiente necessárias se não existirem
        if 'DB_PASSWORD' not in env:
            env['DB_PASSWORD'] = 'Define@4536#8521'
        if 'LITORAL_PASSWORD' not in env:
            env['LITORAL_PASSWORD'] = 'Define@4536#8521'
        
        # Definir diretório de trabalho
        working_dir = os.path.join(os.path.dirname(__file__), '..')
        
        logger.info(f"Executando script: {' '.join(comando)}")
        logger.info(f"Diretório de trabalho: {working_dir}")
        logger.info(f"Script path: {script_path}")
        
        # Executar script com contexto melhorado
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            cwd=working_dir,  # Diretório do projeto
            env=env,  # Variáveis de ambiente
            timeout=300,  # 5 minutos de timeout
            shell=False  # Não usar shell para evitar problemas de escape
        )
        
        # Verificar resultado
        if resultado.returncode == 0:
            return {
                "success": True,
                "message": f"Script executado com sucesso para {data_formatada}",
                "data": {
                    "data_sorteio": dados.data_sorteio,
                    "data_formatada": data_formatada,
                    "siglas": siglas_list,
                    "edicoes_criadas": edicoes_criadas,
                    "stdout": resultado.stdout,
                    "stderr": resultado.stderr,
                    "returncode": resultado.returncode
                }
            }
        else:
            error_msg = resultado.stderr if resultado.stderr else resultado.stdout
            logger.error(f"Script falhou com returncode {resultado.returncode}: {error_msg}")
            raise HTTPException(
                status_code=500, 
                detail=f"Erro na execução do script (returncode: {resultado.returncode}): {error_msg}"
            )
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout na execução do script")
        raise HTTPException(status_code=500, detail="Timeout na execução do script (5 minutos)")
    except Exception as e:
        logger.error(f"Erro inesperado na execução do script: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@app.post("/api/edicoes/cadastrar-sigla-avulsa")
def cadastrar_sigla_avulsa(dados: SiglaAvulsaCreate):
    """
    Cadastra uma sigla avulsa na tabela siglas_diarias, sempre com tipo='extra'.
    Permite múltiplos registros para a mesma data, mas não permite a mesma sigla na mesma data.
    """
    try:
        # Validar formato da data
        from datetime import datetime
        try:
            data_obj = datetime.strptime(dados.data_sorteio, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
        
        # Validar siglas
        if not dados.siglas or not dados.siglas.strip():
            raise HTTPException(status_code=400, detail="Sigla não pode estar vazia")
        
        # Validar dia da semana
        if not dados.dia_semana or not dados.dia_semana.strip():
            raise HTTPException(status_code=400, detail="Dia da semana não pode estar vazio")
        
        # Forçar tipo = 'extra' (mesmo se vier diferente)
        tipo = 'extra'
        
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        try:
            # Verificar se já existe a mesma sigla na mesma data
            check_query = """
            SELECT id, siglas FROM siglas_diarias 
            WHERE data_sorteio = %s AND siglas = %s
            """
            cursor.execute(check_query, (dados.data_sorteio, dados.siglas))
            existing = cursor.fetchone()
            
            if existing:
                raise HTTPException(
                    status_code=409, 
                    detail=f"Já existe um registro para a sigla '{dados.siglas}' na data {dados.data_sorteio}. Não é possível cadastrar a mesma sigla na mesma data."
                )
            
            insert_query = """
            INSERT INTO siglas_diarias (diaSemana, data_sorteio, siglas, tipo)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (dados.dia_semana, dados.data_sorteio, dados.siglas, tipo))
            connection.commit()
            registro_id = cursor.lastrowid
            # --- NOVO FLUXO: Alimentar extracoes_cadastro para sigla avulsa ---
            try:
                # 1. Buscar maior edição em extracoes_cadastro
                connection2 = pymysql.connect(**DB_CONFIG)
                cursor2 = connection2.cursor()
                cursor2.execute("SELECT MAX(edicao) FROM extracoes_cadastro")
                res = cursor2.fetchone()
                max_edicao = res[0] if res and res[0] is not None else 0
                edicao_atual = max_edicao + 1
                sigla = dados.siglas.strip()
                if 'GRUPO' not in sigla.upper():
                    # LÓGICA ATUAL: Extrair prefixo da sigla
                    base_sigla = sigla.split('_')[0] if '_' in sigla else sigla
                    
                    # NOVA LÓGICA: Verificar se já existe sigla_oficial para a mesma data
                    # e determinar sufixo EXTRA se necessário
                    cursor2.execute("""
                        SELECT sigla_oficial FROM extracoes_cadastro 
                        WHERE data_sorteio = %s AND sigla_oficial LIKE %s
                        ORDER BY sigla_oficial
                    """, (dados.data_sorteio, f"{base_sigla}%"))
                    
                    siglas_existentes = [row[0] for row in cursor2.fetchall()]
                    
                    # Determinar sufixo baseado nas siglas existentes
                    if not siglas_existentes:
                        # Primeira sigla desta base - sem sufixo
                        sigla_oficial = base_sigla
                    else:
                        # Verificar se já existe a base sem sufixo
                        if base_sigla in siglas_existentes:
                            # Contar quantas EXTRA já existem
                            extras_count = 0
                            for sigla_existente in siglas_existentes:
                                if sigla_existente.startswith(f"{base_sigla} EXTRA"):
                                    extras_count += 1
                            
                            if extras_count == 0:
                                sigla_oficial = f"{base_sigla} EXTRA"
                            else:
                                sigla_oficial = f"{base_sigla} EXTRA {extras_count + 1}"
                        else:
                            # Base não existe ainda - usar sem sufixo
                            sigla_oficial = base_sigla
                    
                    extracao = sigla
                    data_sorteio = dados.data_sorteio
                    # Gerar link conforme regra do script antigo
                    base_url = 'https://litoraldasorte.com/campanha/'
                    if sigla_oficial.upper() in ['FEDERAL', 'FEDERAL ESPECIAL']:
                        titulo = f"{sigla_oficial.upper()} EDIÇÃO {edicao_atual}"
                    else:
                        titulo = f"{sigla_oficial.upper()} RJ EDIÇÃO {edicao_atual}"
                    slug = titulo.lower().replace(' ', '-').replace('edição', 'edicao')
                    link = base_url + slug
                    # Buscar dados em premiacoes
                    cursor2.execute("SELECT * FROM premiacoes WHERE sigla = %s LIMIT 1", (sigla,))
                    premiacao = cursor2.fetchone()
                    if not premiacao:
                        raise HTTPException(status_code=400, detail=f"Sigla '{sigla}' não encontrada na tabela premiacoes. Corrija e tente novamente.")
                    
                    # Montar campos para extracoes_cadastro (dados de controle)
                    insert_cols_cadastro = [
                        'data_sorteio', 'edicao', 'sigla_oficial', 'extracao', 'link',
                        'status_cadastro', 'status_link', 'error_msg', 'id_siglas_diarias'
                    ]
                    insert_values_cadastro = [
                        data_sorteio, edicao_atual, sigla_oficial, extracao, link,
                        'pendente', 'pendente', '', registro_id
                    ]
                    
                    # Montar campos para extracoes_premiacao (dados de premiação)
                    insert_cols_premiacao = [
                        'edicao', 'horario', 'precocota', 'primeiro', 'segundo', 'terceiro', 'quarto', 'quinto',
                        'sexto', 'setimo', 'oitavo', 'nono', 'decimo',
                        'decimo_primeiro', 'decimo_segundo', 'decimo_terceiro', 'decimo_quarto',
                        'numeracao', 'totalpremios', 'totalpremios_oficial', 'totalpremiacao',
                        'premiosextras', 'arrecad', 'lucro', 'id_siglas_diarias'
                    ]
                    insert_values_premiacao = [
                        edicao_atual,
                        premiacao[2], premiacao[3], premiacao[4], premiacao[5], premiacao[6], premiacao[7], premiacao[8],
                        premiacao[9], premiacao[10], premiacao[11], premiacao[12], premiacao[13],
                        premiacao[14], premiacao[15], premiacao[16], premiacao[17],
                        premiacao[18], premiacao[19], premiacao[20], premiacao[21],
                        premiacao[22], premiacao[23], premiacao[24], registro_id
                    ]
                    
                    # Verificar se já existe a mesma sigla, data e edição
                    cursor2.execute("SELECT COUNT(*) FROM extracoes_cadastro WHERE sigla_oficial=%s AND data_sorteio=%s AND edicao=%s", (sigla_oficial, data_sorteio, edicao_atual))
                    res = cursor2.fetchone()
                    if res and res[0] == 0:
                        # Inserir em extracoes_cadastro
                        insert_sql_cadastro = f"INSERT INTO extracoes_cadastro ({', '.join(insert_cols_cadastro)}) VALUES ({', '.join(['%s']*len(insert_cols_cadastro))})"
                        cursor2.execute(insert_sql_cadastro, insert_values_cadastro)
                        
                        # Inserir em extracoes_premiacao
                        insert_sql_premiacao = f"INSERT INTO extracoes_premiacao ({', '.join(insert_cols_premiacao)}) VALUES ({', '.join(['%s']*len(insert_cols_premiacao))})"
                        cursor2.execute(insert_sql_premiacao, insert_values_premiacao)
                        
                        connection2.commit()
                cursor2.close()
                connection2.close()
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro ao alimentar extracoes_cadastro: {str(e)}")
            # --- FIM NOVO FLUXO ---
            return {
                "success": True,
                "message": f"Sigla avulsa cadastrada com sucesso para {dados.data_sorteio}",
                "data": {
                    "id": registro_id,
                    "data_sorteio": dados.data_sorteio,
                    "dia_semana": dados.dia_semana,
                    "siglas": dados.siglas,
                    "tipo": tipo
                }
            }
        except HTTPException:
            connection.rollback()
            raise
        except Exception as e:
            connection.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao cadastrar sigla avulsa: {str(e)}")
        finally:
            cursor.close()
            connection.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@app.get("/api/extracoes/tem-pendente")
def existe_pendente(data_sorteio: str = Query(...), sigla: str = Query(...)):
    """
    Verifica se existe pelo menos um registro em extracoes_cadastro para a data e sigla informadas,
    com status_cadastro = 'pendente' OU 'error', e data_sorteio >= '2025-06-12'.
    Retorna {"tem_pendente": true/false}
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cur = conn.cursor()
        query = """
            SELECT COUNT(*) FROM extracoes_cadastro
            WHERE data_sorteio = %s
              AND extracao = %s
              AND (status_cadastro = 'pendente' OR status_cadastro = 'error')
              AND data_sorteio >= '2025-06-12'
        """
        cur.execute(query, (data_sorteio, sigla))
        res = cur.fetchone()
        count = res[0] if res and res[0] is not None else 0
        cur.close()
        conn.close()
        return {"tem_pendente": count > 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar pendências: {str(e)}")

@app.get("/api/extracoes/tem-pendente-data")
def existe_pendente_data(data_sorteio: str = Query(...)):
    """
    Verifica se existe pelo menos um registro em extracoes_cadastro para a data informada,
    com status_cadastro diferente de 'cadastrado' e data_sorteio >= '2025-06-12'.
    Retorna {"tem_pendente": true/false}
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cur = conn.cursor()
        query = """
            SELECT COUNT(*) FROM extracoes_cadastro
            WHERE data_sorteio = %s
              AND data_sorteio >= '2025-06-12'
              AND status_cadastro != 'cadastrado'
        """
        cur.execute(query, (data_sorteio,))
        res = cur.fetchone()
        count = res[0] if res and res[0] is not None else 0
        cur.close()
        conn.close()
        return {"tem_pendente": count > 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar pendências: {str(e)}")

# =============================================================================
# NOVOS ENDPOINTS PARA SCRIPTS
# =============================================================================

class EdicoesEspecificasRequest(BaseModel):
    edicoes: List[int]

@app.post("/api/scripts/verificar-links")
def executar_verificar_links():
    """
    Executa o script novo_verificalinks.py para verificar links
    """
    try:
        # Caminho para o script
        script_path = os.path.join(os.path.dirname(__file__), "../scripts/novo_verificalinks.py")
        
        # Verificar se o script existe
        if not os.path.exists(script_path):
            raise HTTPException(status_code=404, detail="Script novo_verificalinks.py não encontrado")
        
        # Executar script
        resultado = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(script_path),
            timeout=600  # 10 minutos de timeout
        )
        
        # Verificar resultado
        if resultado.returncode == 0:
            # Extrair informações do output
            output_lines = resultado.stdout.split('\n')
            links_verificados = 0
            links_validos = 0
            links_invalidos = 0
            
            for line in output_lines:
                line = line.strip()
                if "Total testado:" in line:
                    # Extrair número de links testados
                    match = re.search(r'Total testado:\s*(\d+)', line)
                    if match:
                        links_verificados = int(match.group(1))
                elif "Links OK:" in line:
                    # Extrair número de links válidos
                    match = re.search(r'Links OK:\s*(\d+)', line)
                    if match:
                        links_validos = int(match.group(1))
                elif "Links ERRO:" in line:
                    # Extrair número de links inválidos
                    match = re.search(r'Links ERRO:\s*(\d+)', line)
                    if match:
                        links_invalidos = int(match.group(1))
            
            return {
                "success": True,
                "message": "Verificação de links concluída com sucesso",
                "links_verificados": links_verificados,
                "links_validos": links_validos,
                "links_invalidos": links_invalidos,
                "stdout": resultado.stdout,
                "stderr": resultado.stderr
            }
        else:
            error_msg = resultado.stderr if resultado.stderr else resultado.stdout
            raise HTTPException(
                status_code=500,
                detail=f"Erro na verificação de links: {error_msg}"
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout na verificação de links (10 minutos)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@app.get("/api/scripts/links-com-problemas")
def obter_links_com_problemas():
    """
    Retorna apenas os números das edições com status_link = 'error' ou 'pendente'
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        
        # Buscar edições com status_link = 'error' ou 'pendente'
        cursor.execute("""
            SELECT edicao, sigla_oficial, status_link 
            FROM extracoes_cadastro 
            WHERE status_link IN ('error', 'pendente') 
            ORDER BY edicao ASC
        """)
        
        problemas = cursor.fetchall()
        cursor.close()
        connection.close()
        
        # Extrair apenas os números das edições
        edicoes_problemas = [str(p['edicao']) for p in problemas]
        
        return {
            "success": True,
            "total": len(edicoes_problemas),
            "edicoes": edicoes_problemas,
            "edicoes_detalhadas": problemas
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar links com problemas: {str(e)}")

@app.get("/api/scripts/links-pendentes")
def obter_links_pendentes():
    """
    Retorna apenas os números das edições com links pendentes
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        
        # Buscar edições com status_envio_link = 'pendente'
        cursor.execute("""
            SELECT edicao, sigla_oficial 
            FROM extracoes_cadastro 
            WHERE status_envio_link = 'pendente' 
            ORDER BY edicao ASC
        """)
        
        pendentes = cursor.fetchall()
        cursor.close()
        connection.close()
        
        # Extrair apenas os números das edições
        edicoes_pendentes = [str(p['edicao']) for p in pendentes]
        
        return {
            "success": True,
            "total": len(edicoes_pendentes),
            "edicoes": edicoes_pendentes,
            "edicoes_detalhadas": pendentes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar links pendentes: {str(e)}")

@app.post("/api/scripts/enviar-links-pendentes")
def executar_enviar_links_pendentes():
    """
    Executa o script novo_chamadas_group_latest.py para enviar links pendentes
    """
    import re
    
    try:
        # Caminho para o script
        script_path = os.path.join(os.path.dirname(__file__), "../scripts/novo_chamadas_group_latest.py")
        
        # Verificar se o script existe
        if not os.path.exists(script_path):
            raise HTTPException(status_code=404, detail="Script novo_chamadas_group_latest.py não encontrado")
        
        # Executar script (sem argumentos = modo pendentes)
        resultado = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(script_path),
            timeout=300  # 5 minutos de timeout
        )
        
        # Verificar resultado
        if resultado.returncode == 0:
            # Extrair informações do output
            output_lines = resultado.stdout.split('\n')
            mensagens_enviadas = None
            edicoes_enviadas = []

            for line in output_lines:
                line = line.strip()
                # Prioridade para o formato exato do script
                if mensagens_enviadas is None and "SUCESSO: Total de mensagens enviadas:" in line:
                    match = re.search(r'SUCESSO: Total de mensagens enviadas:\s*(\d+)', line)
                    if match:
                        mensagens_enviadas = int(match.group(1))
                elif "edição" in line.lower() and "enviada com sucesso" in line.lower():
                    match = re.search(r'edição (\d+)', line)
                    if match:
                        edicoes_enviadas.append(int(match.group(1)))
            # Se não encontrou o formato exato, tenta o genérico
            if mensagens_enviadas is None:
                for line in output_lines:
                    if "total de mensagens enviadas" in line.lower():
                        match = re.search(r'(\d+)', line)
                        if match:
                            mensagens_enviadas = int(match.group(1))
                            break
            if mensagens_enviadas is None:
                mensagens_enviadas = 0

            return {
                "success": True,
                "message": "Envio de links pendentes concluído com sucesso",
                "mensagens_enviadas": mensagens_enviadas,
                "edicoes_enviadas": edicoes_enviadas,
                "stdout": resultado.stdout,
                "stderr": resultado.stderr
            }
        else:
            error_msg = resultado.stderr if resultado.stderr else resultado.stdout
            raise HTTPException(
                status_code=500,
                detail=f"Erro no envio de links pendentes: {error_msg}"
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout no envio de links pendentes (5 minutos)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@app.post("/api/scripts/enviar-edicoes-especificas")
def executar_enviar_edicoes_especificas(dados: EdicoesEspecificasRequest):
    """
    Executa o script novo_chamadas_group_latest.py para enviar edições específicas
    """
    import re
    
    try:
        # Validar edições
        if not dados.edicoes or len(dados.edicoes) == 0:
            raise HTTPException(status_code=400, detail="Nenhuma edição informada")
        
        # Caminho para o script
        script_path = os.path.join(os.path.dirname(__file__), "../scripts/novo_chamadas_group_latest.py")
        
        # Verificar se o script existe
        if not os.path.exists(script_path):
            raise HTTPException(status_code=404, detail="Script novo_chamadas_group_latest.py não encontrado")
        
        # Preparar comando com argumentos
        comando = ["python", script_path] + [str(edicao) for edicao in dados.edicoes]
        
        # Executar script com edições específicas
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(script_path),
            timeout=300  # 5 minutos de timeout
        )
        
        # Verificar resultado
        if resultado.returncode == 0:
            # Extrair informações do output
            output_lines = resultado.stdout.split('\n')
            mensagens_enviadas = 0
            edicoes_enviadas = []
            
            for line in output_lines:
                if "total de mensagens enviadas" in line.lower():
                    # Extrair número de mensagens
                    match = re.search(r'(\d+)', line)
                    if match:
                        mensagens_enviadas = int(match.group(1))
                elif "edição" in line.lower() and "enviada com sucesso" in line.lower():
                    # Extrair número da edição
                    match = re.search(r'edição (\d+)', line)
                    if match:
                        edicoes_enviadas.append(int(match.group(1)))
            
            return {
                "success": True,
                "message": f"Envio de {len(dados.edicoes)} edições específicas concluído com sucesso",
                "mensagens_enviadas": mensagens_enviadas,
                "edicoes_enviadas": edicoes_enviadas,
                "edicoes_solicitadas": dados.edicoes,
                "stdout": resultado.stdout,
                "stderr": resultado.stderr
            }
        else:
            error_msg = resultado.stderr if resultado.stderr else resultado.stdout
            raise HTTPException(
                status_code=500,
                detail=f"Erro no envio de edições específicas: {error_msg}"
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout no envio de edições específicas (5 minutos)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@app.post("/api/scripts/executar-para-siglas/{siglas_id}")
def executar_script_para_siglas(siglas_id: int):
    """
    Executa o script cadRifas_litoral_latest.py apenas para edições pendentes/erro
    de um registro específico de siglas_diarias
    """
    try:
        # Verificar se o registro de siglas_diarias existe
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        
        # Verificar se o registro existe
        cursor.execute("SELECT id, data_sorteio, siglas FROM siglas_diarias WHERE id = %s", (siglas_id,))
        registro_siglas = cursor.fetchone()
        
        if not registro_siglas:
            raise HTTPException(status_code=404, detail=f"Registro de siglas com ID {siglas_id} não encontrado")
        
        # Buscar edições pendentes/erro para este registro
        cursor.execute("""
            SELECT edicao, sigla_oficial, extracao, status_cadastro 
            FROM extracoes_cadastro 
            WHERE id_siglas_diarias = %s 
            AND status_cadastro IN ('pendente', 'error')
            ORDER BY edicao
        """, (siglas_id,))
        
        edicoes_pendentes = cursor.fetchall()
        cursor.close()
        connection.close()
        
        if not edicoes_pendentes:
            return {
                "success": True,
                "message": f"Nenhuma edição pendente encontrada para o registro {siglas_id}",
                "edicoes_processadas": 0,
                "edicoes_pendentes": []
            }
        
        # Extrair números das edições
        edicoes_ids = [edicao['edicao'] for edicao in edicoes_pendentes]
        
        # Caminho para o script
        script_path = os.path.join(os.path.dirname(__file__), "../scripts/cadRifas_litoral_latest.py")
        
        # Verificar se o script existe
        if not os.path.exists(script_path):
            raise HTTPException(status_code=404, detail="Script cadRifas_litoral_latest.py não encontrado")
        
        # Preparar comando com argumentos (números das edições)
        comando = [sys.executable, script_path] + [str(edicao_id) for edicao_id in edicoes_ids]
        
        logger.info(f"Executando script para siglas_id {siglas_id} com edições: {edicoes_ids}")
        logger.info(f"Comando: {' '.join(comando)}")
        
        # Configurar ambiente
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONLEGACYWINDOWSFSENCODING'] = '0'
        
        # Executar script com encoding adequado
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Substitui caracteres inválidos
            cwd=os.path.dirname(script_path),
            timeout=600,  # 10 minutos de timeout
            env=env
        )
        
        # Verificar resultado
        if resultado.returncode == 0:
            return {
                "success": True,
                "message": f"Script executado com sucesso para {len(edicoes_ids)} edições pendentes",
                "edicoes_processadas": len(edicoes_ids),
                "edicoes_pendentes": edicoes_ids,
                "registro_siglas": {
                    "id": registro_siglas['id'],
                    "data_sorteio": registro_siglas['data_sorteio'],
                    "siglas": registro_siglas['siglas']
                },
                "stdout": resultado.stdout,
                "stderr": resultado.stderr
            }
        else:
            error_msg = resultado.stderr if resultado.stderr else resultado.stdout
            raise HTTPException(
                status_code=500,
                detail=f"Erro na execução do script: {error_msg}"
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout na execução do script (10 minutos)")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@app.delete("/api/edicoes/excluir-siglas")
def excluir_siglas_diarias(dados: ExcluirSiglasRequest):
    """
    Exclui um registro de siglas_diarias e todos os registros relacionados em extracoes_cadastro
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        
        # Primeiro, verificar se o registro existe e obter informações
        query_verificar = "SELECT id, data_sorteio, siglas FROM siglas_diarias WHERE id = %s"
        cursor.execute(query_verificar, (dados.id,))
        registro = cursor.fetchone()
        
        if not registro:
            raise HTTPException(status_code=404, detail=f"Registro com ID {dados.id} não encontrado")
        
        # Verificar se a data é futura ou atual (não permitir excluir datas passadas)
        from datetime import datetime, date
        data_registro = registro['data_sorteio']
        data_atual = date.today()
        
        if isinstance(data_registro, str):
            data_registro = datetime.strptime(data_registro, '%Y-%m-%d').date()
        
        if data_registro < data_atual:
            raise HTTPException(
                status_code=400, 
                detail="Não é possível excluir registros de datas passadas"
            )
        
        # Iniciar transação
        connection.begin()
        
        try:
            # 1. Excluir registros relacionados em extracoes_cadastro
            query_excluir_extracoes = "DELETE FROM extracoes_cadastro WHERE id_siglas_diarias = %s"
            cursor.execute(query_excluir_extracoes, (dados.id,))
            registros_extracoes_excluidos = cursor.rowcount
            
            # 2. Excluir registros relacionados em extracoes_premiacao
            query_excluir_premiacao = "DELETE FROM extracoes_premiacao WHERE id_siglas_diarias = %s"
            cursor.execute(query_excluir_premiacao, (dados.id,))
            registros_premiacao_excluidos = cursor.rowcount
            
            # 3. Excluir o registro principal em siglas_diarias
            query_excluir_siglas = "DELETE FROM siglas_diarias WHERE id = %s"
            cursor.execute(query_excluir_siglas, (dados.id,))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Erro ao excluir registro com ID {dados.id}")
            
            # Confirmar transação
            connection.commit()
            
            return {
                "success": True,
                "message": f"Registro excluído com sucesso",
                "id_excluido": dados.id,
                "data_sorteio": registro['data_sorteio'],
                "siglas": registro['siglas'],
                "registros_extracoes_excluidos": registros_extracoes_excluidos,
                "registros_premiacao_excluidos": registros_premiacao_excluidos
            }
            
        except Exception as e:
            # Rollback em caso de erro
            connection.rollback()
            raise e
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir registro: {str(e)}")
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

# Endpoint para remover upload temporário
@app.delete("/remover-upload-temp")
async def remover_upload_temp(temp_path: str = Form(...)):
    try:
        # Extrair nome do arquivo temporário
        temp_filename = os.path.basename(temp_path)
        temp_file_path = os.path.join(TEMP_UPLOAD_DIR, temp_filename)
        
        # Verificar se é realmente um arquivo temporário
        if not temp_filename.startswith('temp_'):
            raise HTTPException(status_code=400, detail="Apenas arquivos temporários podem ser removidos")
        
        # Verificar se arquivo temporário existe
        if not os.path.exists(temp_file_path):
            return {"success": True, "message": "Arquivo temporário não encontrado (já removido)"}
        
        # Remover arquivo
        os.remove(temp_file_path)
        
        return {
            "success": True,
            "message": "Arquivo temporário removido com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover arquivo temporário: {str(e)}")

@app.get("/api/edicoes/{siglas_id}/tem-pendencias")
def verificar_pendencias_siglas(siglas_id: int):
    """
    Verifica se um registro de siglas_diarias tem edições pendentes/erro
    """
    try:
        logger.info(f"Verificando pendências para siglas_id: {siglas_id}")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        
        # Verificar se o registro existe
        cursor.execute("SELECT id, data_sorteio, siglas FROM siglas_diarias WHERE id = %s", (siglas_id,))
        registro_siglas = cursor.fetchone()
        
        if not registro_siglas:
            logger.warning(f"Registro de siglas com ID {siglas_id} não encontrado")
            raise HTTPException(status_code=404, detail=f"Registro de siglas com ID {siglas_id} não encontrado")
        
        # Buscar edições pendentes/erro
        cursor.execute("""
            SELECT edicao, sigla_oficial, extracao, status_cadastro 
            FROM extracoes_cadastro 
            WHERE id_siglas_diarias = %s 
            AND status_cadastro IN ('pendente', 'error')
            ORDER BY edicao
        """, (siglas_id,))
        
        edicoes_pendentes = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return {
            "tem_pendencias": len(edicoes_pendentes) > 0,
            "total_pendencias": len(edicoes_pendentes),
            "edicoes_pendentes": edicoes_pendentes,
            "registro_siglas": registro_siglas
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar pendências: {str(e)}")

# =============================================================================
# ENDPOINTS DA DASHBOARD
# =============================================================================

@app.get("/api/dashboard/extracoes-recentes")
def obter_extracoes_recentes():
    """
    Retorna apenas as extrações ATIVAS para exibir no dashboard
    - Filtra apenas rifas com status_rifa = 'ativo'
    - Remove rifas que atingiram 100% há mais de 30 minutos do horário de fechamento
    - Independente da data
    """
    try:
        from datetime import datetime, timedelta
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        # Buscar todas as extrações ativas (sem filtro de data)
        cursor.execute("""
            SELECT 
                ec.id,
                ec.edicao,
                ec.sigla_oficial,
                ec.extracao,
                ec.link,
                ec.status_cadastro,
                ec.status_link,
                ec.error_msg,
                ec.andamento,
                ec.status_rifa,
                ec.data_sorteio,
                p.horario
            FROM extracoes_cadastro ec
            LEFT JOIN premiacoes p ON ec.extracao = p.sigla
            WHERE ec.status_rifa IN ('ativo', 'concluído', 'error')
            AND ec.link IS NOT NULL 
            AND ec.link != ''
            ORDER BY ec.edicao ASC
        """)
        extracoes_raw = cursor.fetchall()
        extracoes_validas = []
        agora = datetime.now()
        for extracao in extracoes_raw:
            andamento_raw = extracao['andamento'] if extracao and 'andamento' in extracao else None
            if andamento_raw and isinstance(andamento_raw, str) and andamento_raw.strip():
                extracao['andamento_percentual'] = andamento_raw
            else:
                extracao['andamento_percentual'] = '0%'
            tem_erro_x = extracao['andamento_percentual'] == 'X'
            percentual_str = extracao['andamento_percentual'].replace('%', '')
            try:
                if tem_erro_x:
                    extracao['andamento_numerico'] = 0
                else:
                    extracao['andamento_numerico'] = int(percentual_str)
            except:
                extracao['andamento_numerico'] = 0
            if (extracao.get('status_rifa') == 'error' if extracao else False) or tem_erro_x:
                extracao['deve_exibir'] = True
            elif extracao['andamento_numerico'] < 100 and (extracao.get('status_rifa') != 'concluído' if extracao else True):
                extracao['deve_exibir'] = True
            else:
                data_sorteio = extracao['data_sorteio'] if extracao and 'data_sorteio' in extracao else None
                horario_str = extracao['horario'] if extracao and 'horario' in extracao else None
                if horario_str and data_sorteio:
                    try:
                        if isinstance(data_sorteio, str):
                            data_obj = datetime.strptime(data_sorteio, '%Y-%m-%d')
                        else:
                            from datetime import date
                            if isinstance(data_sorteio, date):
                                data_obj = datetime.combine(data_sorteio, datetime.min.time())
                            else:
                                data_obj = data_sorteio
                        horario_clean = horario_str.strip()
                        if 'AM' in horario_clean or 'PM' in horario_clean:
                            time_obj = datetime.strptime(horario_clean, '%I:%M %p')
                            hora = time_obj.hour
                            minuto = time_obj.minute
                        else:
                            horario_parts = horario_clean.split(':')
                            hora = int(horario_parts[0])
                            minuto = int(horario_parts[1]) if len(horario_parts) > 1 else 0
                        fechamento = data_obj.replace(hour=hora, minute=minuto, second=0)
                        limite_exibicao = fechamento + timedelta(minutes=30)
                        extracao['deve_exibir'] = agora <= limite_exibicao
                    except Exception as e:
                        print(f"Erro ao processar horário para edição {extracao['edicao'] if extracao and 'edicao' in extracao else ''}: {e}")
                        extracao['deve_exibir'] = True
                else:
                    extracao['deve_exibir'] = False
            if extracao['deve_exibir']:
                tem_erro_x = extracao['andamento_percentual'] == 'X'
                extracao['tem_erro'] = (extracao['status_cadastro'] == 'error' if extracao and 'status_cadastro' in extracao else False) or (extracao.get('status_rifa') == 'error' if extracao else False) or tem_erro_x
                extracao['status_rifa_atual'] = extracao.get('status_rifa', 'ativo') if extracao else 'ativo'
                cursor.execute("""
                    SELECT imagem_path 
                    FROM premiacoes 
                    WHERE sigla = %s 
                    LIMIT 1
                """, (extracao['extracao'] if extracao and 'extracao' in extracao else None,))
                premiacao = cursor.fetchone()
                if premiacao and 'imagem_path' in premiacao and premiacao['imagem_path']:
                    extracao['imagem_path'] = premiacao['imagem_path']
                else:
                    extracao['imagem_path'] = None
                if extracao['andamento_numerico'] == 100:
                    import unidecode
                    titulo_simulado = f"{extracao['sigla_oficial']} RJ Edição {extracao['edicao']}" if extracao and 'sigla_oficial' in extracao and 'edicao' in extracao else ''
                    titulo_modificado = unidecode.unidecode(titulo_simulado.lower().replace(" ", "-"))
                    nome_arquivo = f"relatorio-vendas-{titulo_modificado}.pdf"
                    caminho_pdf = f"D:/Adilson/Downloads/{nome_arquivo}"
                    extracao['tem_pdf'] = os.path.exists(caminho_pdf)
                else:
                    extracao['tem_pdf'] = False
                extracoes_validas.append(extracao)
        data_atual = datetime.now()
        dias_semana = {
            0: 'Segunda-feira',
            1: 'Terça-feira', 
            2: 'Quarta-feira',
            3: 'Quinta-feira',
            4: 'Sexta-feira',
            5: 'Sábado',
            6: 'Domingo'
        }
        dia_semana = dias_semana[data_atual.weekday()]
        data_formatada = f"{dia_semana}, {data_atual.strftime('%d/%m/%Y')}"
        cursor.close()
        connection.close()
        return {
            "data_recente": data_formatada,
            "data_sorteio": data_atual.strftime('%Y-%m-%d'),
            "extracoes": extracoes_validas,
            "total_ativas": len(extracoes_validas)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar extrações ativas: {str(e)}")

@app.post("/api/dashboard/enviar-link-edicao/{edicao}")
def enviar_link_edicao(edicao: int):
    """
    Envia o link de uma edição específica via WhatsApp
    """
    try:
        # Buscar informações da edição
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        
        cursor.execute("""
            SELECT 
                id,
                edicao,
                sigla_oficial,
                extracao,
                link
            FROM extracoes_cadastro 
            WHERE edicao = %s
            LIMIT 1
        """, (edicao,))
        
        extracao = cursor.fetchone()
        
        if not extracao:
            raise HTTPException(status_code=404, detail=f"Edição {edicao} não encontrada")
        
        # Buscar imagem da premiação
        cursor.execute("""
            SELECT imagem_path 
            FROM premiacoes 
            WHERE sigla = %s 
            LIMIT 1
        """, (extracao['extracao'],))
        premiacao = cursor.fetchone()
        if premiacao and premiacao['imagem_path']:
            extracao['imagem_path'] = premiacao['imagem_path']
        else:
            extracao['imagem_path'] = None
        
        cursor.close()
        connection.close()
        
        # Executar o script de envio para esta edição específica
        script_path = os.path.join(os.path.dirname(__file__), "../scripts/novo_chamadas_group_latest.py")
        
        if not os.path.exists(script_path):
            raise HTTPException(status_code=404, detail="Script de envio não encontrado")
        
        # Executar script com a edição específica
        resultado = subprocess.run(
            ["python", script_path, str(edicao)],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(script_path),
            timeout=60  # 1 minuto de timeout
        )
        
        if resultado.returncode == 0:
            # Atualizar status_link para 'enviado'
            connection = pymysql.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE extracoes_cadastro 
                SET status_link = 'enviado' 
                WHERE edicao = %s
            """, (edicao,))
            connection.commit()
            cursor.close()
            connection.close()
            
            return {
                "success": True,
                "message": f"Link da edição {edicao} enviado com sucesso",
                "edicao": edicao,
                "link": extracao['link'],
                "stdout": resultado.stdout
            }
        else:
            error_msg = resultado.stderr if resultado.stderr else resultado.stdout
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao enviar link: {error_msg}"
            )
            
    except HTTPException:
        raise
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout no envio do link (1 minuto)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@app.post("/api/scripts/verificar-andamento-rifas")
def executar_verificar_andamento_rifas():
    """
    Executa o script para verificar o andamento das rifas através dos links cadastrados
    """
    try:
        script_path = os.path.join("scripts", "verificar_andamento_rifas.py")
        
        if not os.path.exists(script_path):
            raise HTTPException(status_code=404, detail="Script de verificação de andamento não encontrado")
        
        logger.info("Iniciando execução do script de verificação de andamento das rifas")
        
        # Configurar ambiente
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Executar o script
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=1800,  # 30 minutos - pode demorar mais que outros scripts
            env=env
        )
        
        # Verificar se houve erro na execução
        if result.returncode != 0:
            logger.error(f"Erro na execução do script de verificação de andamento: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro na execução do script: {result.stderr}"
            )
        
        logger.info("Script de verificação de andamento executado com sucesso")
        
        # Extrair informações do output para o resumo
        output_lines = result.stdout.split('\n')
        total_links = 0
        sucessos = 0
        erros = 0
        ignorados = 0
        processados_efetivamente = 0
        
        for line in output_lines:
            if "Total de links:" in line:
                try:
                    total_links = int(line.split(":")[1].strip())
                except:
                    pass
            elif "Sucessos:" in line:
                try:
                    sucessos = int(line.split(":")[1].strip())
                except:
                    pass
            elif "Erros:" in line:
                try:
                    erros = int(line.split(":")[1].strip())
                except:
                    pass
            elif "Ignorados:" in line:
                try:
                    ignorados = int(line.split(":")[1].strip())
                except:
                    pass
            elif "Processados efetivamente:" in line:
                try:
                    processados_efetivamente = int(line.split(":")[1].strip())
                except:
                    pass
        
        return {
            "success": True,
            "message": "Script de verificação de andamento executado com sucesso",
            "data": {
                "total_links": total_links,
                "sucessos": sucessos,
                "erros": erros,
                "ignorados": ignorados,
                "processados_efetivamente": processados_efetivamente,
                "output": result.stdout
            }
        }
        
    except subprocess.TimeoutExpired:
        logger.error("Timeout na execução do script de verificação de andamento")
        raise HTTPException(status_code=500, detail="Timeout na execução do script (30 minutos)")
    except Exception as e:
        logger.error(f"Erro inesperado na execução do script de verificação de andamento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@app.post("/api/dashboard/gerar-relatorio/{edicao}")
def gerar_relatorio(edicao: int):
    """Endpoint para gerar relatório PDF de uma edição que atingiu 100%"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        cursor.execute("""
            SELECT andamento, sigla_oficial 
            FROM extracoes_cadastro 
            WHERE edicao = %s
        """, (edicao,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        andamento = result['andamento'] if result and 'andamento' in result else None
        if not result or not andamento or andamento.strip() != '100%':
            raise HTTPException(status_code=400, detail="Relatório só pode ser gerado para rifas 100% vendidas")
        script_path = os.path.join("scripts", "relatorio_v1.py")
        if not os.path.exists(script_path):
            raise HTTPException(status_code=404, detail="Script de relatório não encontrado")
        logger.info(f"Iniciando geração de relatório para edição {edicao}")
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        result_proc = subprocess.run(
            [sys.executable, script_path, str(edicao)],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300,  # 5 minutos timeout
            env=env
        )
        if result_proc.returncode == 0:
            logger.info(f"Relatório gerado com sucesso para edição {edicao}")
            return {
                "success": True,
                "message": f"Relatório para edição {edicao} gerado com sucesso",
                "edicao": edicao,
                "output": result_proc.stdout
            }
        else:
            logger.error(f"Erro ao gerar relatório para edição {edicao}: {result_proc.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao gerar relatório: {result_proc.stderr}"
            )
    except HTTPException:
        raise
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout ao gerar relatório para edição {edicao}")
        raise HTTPException(status_code=500, detail="Timeout ao gerar relatório (5 minutos)")
    except Exception as e:
        logger.error(f"Erro inesperado ao gerar relatório: {e}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

@app.post("/api/dashboard/notify-update")
def notificar_atualizacao_dashboard():
    """Endpoint para notificar o dashboard sobre atualizações de dados"""
    try:
        logger.info("🔄 Dashboard notificado sobre atualização de dados")
        return {
            "success": True,
            "message": "Dashboard notificado com sucesso",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao processar notificação do dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/dashboard/verificar-pdf/{edicao}")
def verificar_pdf(edicao: int):
    """Verifica se o PDF da edição existe"""
    try:
        # Buscar título da edição no banco para montar nome do arquivo
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        
        cursor.execute("""
            SELECT sigla_oficial 
            FROM extracoes_cadastro 
            WHERE edicao = %s
        """, (edicao,))
        
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not result:
            return {"existe": False, "nome_arquivo": None}
        
        sigla = result['sigla_oficial']
        
        # Simular o padrão de nome que o script cria
        # Por exemplo: relatorio-vendas-ppt-rj-edicao-6197.pdf
        import unidecode
        titulo_simulado = f"{sigla} RJ Edição {edicao}"
        titulo_modificado = unidecode.unidecode(titulo_simulado.lower().replace(" ", "-"))
        nome_arquivo = f"relatorio-vendas-{titulo_modificado}.pdf"
        
        # Verificar se existe no diretório de downloads
        caminho_pdf = f"D:/Adilson/Downloads/{nome_arquivo}"
        existe = os.path.exists(caminho_pdf)
        
        return {
            "existe": existe,
            "nome_arquivo": nome_arquivo if existe else None,
            "caminho": caminho_pdf if existe else None
        }
        
    except Exception as e:
        logger.error(f"Erro ao verificar PDF: {e}")
        return {"existe": False, "nome_arquivo": None}

@app.get("/api/dashboard/download-pdf/{edicao}")
def download_pdf(edicao: int):
    """Download do PDF da edição"""
    try:
        # Verificar se o PDF existe
        verificacao = verificar_pdf(edicao)
        
        if not verificacao["existe"]:
            raise HTTPException(status_code=404, detail="PDF não encontrado")
        
        caminho_pdf = verificacao["caminho"]
        nome_arquivo = verificacao["nome_arquivo"]
        
        # Retornar o arquivo para download
        return FileResponse(
            path=caminho_pdf,
            filename=nome_arquivo,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer download do PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/premiados_consulta")
def serve_premiados_consulta():
    return FileResponse(os.path.join(os.path.dirname(__file__), "../static/premiados_consulta.html"))

@app.get("/api/premiados")
def listar_premiados(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(50, ge=1, le=500, description="Itens por página"),
    edicao: Optional[str] = Query(None, description="Filtrar por edição"),
    extracao: Optional[str] = Query(None, description="Filtrar por extração/sigla"),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    colocacao: Optional[str] = Query(None, description="Filtrar por colocação")
):
    """
    Lista premiados da tabela premiados com paginação e filtros
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        # Construir query base
        where_conditions = []
        params = []
        # Aplicar filtros
        if edicao:
            where_conditions.append("edicao = %s")
            params.append(edicao)
        if extracao:
            where_conditions.append("extracao LIKE %s")
            params.append(f"%{extracao}%")
        if nome:
            where_conditions.append("nome LIKE %s")
            params.append(f"%{nome}%")
        if colocacao:
            where_conditions.append("colocacao = %s")
            params.append(colocacao)
        # Montar WHERE clause
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        # Query para contar total
        count_query = f"SELECT COUNT(*) as total FROM premiados {where_clause}"
        cursor.execute(count_query, params)
        res = cursor.fetchone()
        total_records = res['total'] if res and 'total' in res else 0
        # Calcular offset
        offset = (page - 1) * limit
        # Query principal com paginação
        query = f"""
        SELECT id, edicao, extracao, nome, telefone, colocacao, premio
        FROM premiados 
        {where_clause}
        ORDER BY edicao DESC, colocacao ASC
        LIMIT %s OFFSET %s
        """
        # Adicionar limit e offset aos parâmetros
        query_params = params + [limit, offset]
        cursor.execute(query, query_params)
        premiados = cursor.fetchall()
        # Calcular informações de paginação
        total_pages = (total_records + limit - 1) // limit if total_records else 1
        cursor.close()
        connection.close()
        return {
            "premiados": [p for p in premiados if p and 'id' in p],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_records": total_records,
                "records_per_page": limit,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "filters": {
                "edicao": edicao,
                "extracao": extracao,
                "nome": nome,
                "colocacao": colocacao
            }
        }
    except Exception as e:
        logger.error(f"Erro ao listar premiados: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.get("/api/premiados/estatisticas")
def obter_estatisticas_premiados():
    """
    Obtém estatísticas da tabela premiados
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        # Total de premiados
        cursor.execute("SELECT COUNT(*) as total FROM premiados")
        res = cursor.fetchone()
        total = res['total'] if res and 'total' in res else 0
        # Últimas 5 edições
        cursor.execute("SELECT DISTINCT edicao FROM premiados ORDER BY edicao DESC LIMIT 5")
        ultimas_edicoes = [row['edicao'] for row in cursor.fetchall() if row and 'edicao' in row]
        # Top 5 extrações com mais premiados
        cursor.execute("""
            SELECT extracao, COUNT(*) as total 
            FROM premiados 
            GROUP BY extracao 
            ORDER BY total DESC 
            LIMIT 5
        """)
        top_extracoes = [row for row in cursor.fetchall() if row and 'extracao' in row and 'total' in row]
        # Distribuição por colocação
        cursor.execute("""
            SELECT colocacao, COUNT(*) as total 
            FROM premiados 
            GROUP BY colocacao 
            ORDER BY CAST(colocacao AS UNSIGNED)
        """)
        por_colocacao = [row for row in cursor.fetchall() if row and 'colocacao' in row and 'total' in row]
        cursor.close()
        connection.close()
        return {
            "total_premiados": total,
            "ultimas_edicoes": ultimas_edicoes,
            "top_extracoes": top_extracoes,
            "distribuicao_colocacao": por_colocacao
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.get("/api/premiados/nomes")
def buscar_nomes(q: str = Query("", description="Termo de busca para nomes")):
    """
    Busca nomes de premiados para autocomplete
    """
    try:
        if len(q.strip()) < 2:
            return {"nomes": []}
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        # Buscar nomes únicos que contenham o termo
        query = """
        SELECT DISTINCT nome 
        FROM premiados 
        WHERE nome LIKE %s 
        ORDER BY nome ASC 
        LIMIT 20
        """
        cursor.execute(query, (f"%{q}%",))
        resultados = cursor.fetchall()
        nomes = [r['nome'] for r in resultados if r and 'nome' in r]
        cursor.close()
        connection.close()
        return {"nomes": nomes}
    except Exception as e:
        logger.error(f"Erro ao buscar nomes: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/premiados/telefones")
def buscar_telefones(q: str = Query("", description="Termo de busca para telefones")):
    """
    Busca telefones de premiados para autocomplete
    """
    try:
        if len(q.strip()) < 2:
            return {"telefones": []}
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        # Buscar telefones únicos que contenham o termo
        query = """
        SELECT DISTINCT telefone, nome
        FROM premiados 
        WHERE telefone LIKE %s AND telefone IS NOT NULL
        ORDER BY telefone ASC 
        LIMIT 20
        """
        cursor.execute(query, (f"%{q}%",))
        resultados = cursor.fetchall()
        telefones = [{"telefone": r['telefone'], "nome": r['nome']} for r in resultados if r and 'telefone' in r and 'nome' in r]
        cursor.close()
        connection.close()
        return {"telefones": telefones}
    except Exception as e:
        logger.error(f"Erro ao buscar telefones: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/scripts/status-agendador")
def verificar_status_agendador():
    """
    Verifica se o agendador está funcionando
    """
    try:
        import os
        
        # Verificar se o arquivo de status existe
        status_file = "scripts/agendador_status.json"
        
        if not os.path.exists(status_file):
            return {"ativo": False, "motivo": "Arquivo de status não encontrado"}
        
        # Ler o arquivo de status
        with open(status_file, 'r') as f:
            import json
            status_data = json.load(f)
        
        # Verificar se o agendador está ativo
        status = status_data.get("status", "").lower()
        if status in ["running", "rodando"]:
            return {
                "ativo": True, 
                "ultimo_check": status_data.get("ultima_verificacao", status_data.get("last_check")),
                "rifas_ativas": status_data.get("rifas_ativas", 0),
                "pid": status_data.get("pid")
            }
        else:
            return {"ativo": False, "motivo": f"Agendador parado (status: {status})"}
            
    except Exception as e:
        logger.error(f"Erro ao verificar status do agendador: {e}")
        return {"ativo": False, "motivo": f"Erro: {str(e)}"}

@app.get("/api/dashboard/check-updates")
def verificar_atualizacoes_agendador():
    """
    Verifica se o agendador processou dados novos
    """
    try:
        import os
        import json
        from datetime import datetime, timedelta
        
        # Verificar se o arquivo de notificação existe
        notification_file = "scripts/agendador_notifications.json"
        
        if not os.path.exists(notification_file):
            return {"has_updates": False, "motivo": "Arquivo de notificação não encontrado"}
        
        # Ler o arquivo de notificação
        with open(notification_file, 'r') as f:
            notification_data = json.load(f)
        
        # Verificar se há atualizações recentes (últimos 30 segundos)
        last_update = datetime.fromisoformat(notification_data.get("last_update", "1970-01-01T00:00:00"))
        now = datetime.now()
        
        # Se a última atualização foi há menos de 30 segundos, considerar como nova
        if (now - last_update).total_seconds() < 30:
            # Marcar como lida removendo o arquivo ou atualizando timestamp
            notification_data["last_checked"] = now.isoformat()
            with open(notification_file, 'w') as f:
                json.dump(notification_data, f, indent=2)
            
            return {
                "has_updates": True, 
                "last_update": notification_data.get("last_update"),
                "rifas_processadas": notification_data.get("rifas_processadas", 0)
            }
        else:
            return {"has_updates": False, "last_checked": now.isoformat()}
            
    except Exception as e:
        logger.error(f"Erro ao verificar atualizações: {e}")
        return {"has_updates": False, "motivo": f"Erro: {str(e)}"}

@app.get("/api/premiados/pessoa/{nome}")
def obter_estatisticas_pessoa(nome: str):
    """
    Obtém estatísticas detalhadas de uma pessoa específica
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(DictCursor)
        
        # Estatísticas gerais da pessoa
        query_stats = """
        SELECT 
            COUNT(*) as total_premiacoes,
            SUM(CAST(valor_real AS DECIMAL(10,2))) as total_recebido,
            MIN(edicao) as primeira_edicao,
            MAX(edicao) as ultima_edicao,
            GROUP_CONCAT(DISTINCT telefone) as telefones
        FROM premiados 
        WHERE nome = %s
        """
        
        cursor.execute(query_stats, (nome,))
        stats = cursor.fetchone()
        
        if not stats or stats['total_premiacoes'] == 0:
            return {
                "existe": False,
                "nome": nome,
                "message": "Pessoa não encontrada nos registros"
            }
        
        # Histórico detalhado de premiações
        query_historico = """
        SELECT edicao, extracao, colocacao, premio, valor_real
        FROM premiados 
        WHERE nome = %s
        ORDER BY edicao DESC
        """
        
        cursor.execute(query_historico, (nome,))
        historico = cursor.fetchall()
        
        # Agrupamento por extração
        query_por_extracao = """
        SELECT 
            extracao,
            COUNT(*) as vezes_premiado,
            SUM(CAST(valor_real AS DECIMAL(10,2))) as total_por_extracao
        FROM premiados 
        WHERE nome = %s
        GROUP BY extracao
        ORDER BY total_por_extracao DESC
        """
        
        cursor.execute(query_por_extracao, (nome,))
        por_extracao = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {
            "existe": True,
            "nome": nome,
            "total_premiacoes": stats['total_premiacoes'],
            "total_recebido": float(stats['total_recebido']) if stats['total_recebido'] else 0,
            "primeira_edicao": stats['primeira_edicao'],
            "ultima_edicao": stats['ultima_edicao'],
            "telefones": stats['telefones'].split(',') if stats['telefones'] else [],
            "historico": historico,
            "por_extracao": por_extracao
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas da pessoa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
