# Mapeamento Técnico Detalhado - app/main.py

## 📊 Estatísticas do Arquivo

- **Arquivo**: `app/main.py`
- **Total de linhas**: 2.478
- **Endpoints**: 47 endpoints
- **Modelos Pydantic**: 7 modelos
- **Funções utilitárias**: ~15 funções

## 🔍 Análise por Seções

### Seção 1: Imports e Configurações (Linhas 1-50)
```python
# Imports principais
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Query, Body
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List
import pymysql
from pymysql.cursors import DictCursor
import os
import time
import uuid
import shutil
import subprocess
import json
import glob
from datetime import datetime, timedelta

# Configurações
UPLOAD_DIR = "uploads"
TEMP_UPLOAD_DIR = "uploads/temp"
DB_CONFIG = {...}  # Configuração do banco
```

### Seção 2: Modelos Pydantic (Linhas 50-130)
```python
# Modelos para serem movidos para models.py
class PremiacaoUpdate(BaseModel):
    sigla: str
    horario: Optional[str] = None
    precocota: Optional[float] = Field(None, alias="precocota")
    # ... outros campos

class PremiacaoUpdatePartial(BaseModel):
    sigla: Optional[str] = None
    # ... campos opcionais

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

class EdicoesEspecificasRequest(BaseModel):
    edicoes: List[int]
```

### Seção 3: Rotas de Interface Web (Linhas 130-180)
```python
# Endpoints HTML - Mover para routers/views.py
@app.get("/")
def serve_index():
    # Retorna página principal

@app.get("/editar")
def serve_editar():
    # Retorna página de edição

@app.get("/premiacoes")
def serve_premiacoes():
    # Retorna página de premiações

@app.get("/edicoes")
def serve_edicoes():
    # Retorna página de edições

@app.get("/dashboard")
def serve_dashboard():
    # Retorna página do dashboard

@app.get("/teste-sigla-avulsa")
def serve_teste_sigla_avulsa():
    # Retorna página de teste

@app.get("/premiados_consulta")
def serve_premiados_consulta():
    # Retorna página de consulta de premiados
```

## 📋 Mapeamento Completo de Endpoints

### Grupo 1: Edições (8 endpoints)
**Arquivo destino**: `routers/edicoes.py`

| Endpoint | Método | Função | Descrição |
|----------|--------|--------|-----------|
| `/api/edicoes` | GET | `listar_edicoes()` | Lista todas as edições |
| `/api/edicoes/ultima-data` | GET | `obter_ultima_data()` | Obtém a última data de edição |
| `/api/edicoes/siglas-por-grupo/{data}` | GET | `obter_siglas_por_grupo()` | Obtém siglas por grupo de data |
| `/api/edicoes/cadastrar-siglas` | POST | `cadastrar_siglas_diarias()` | Cadastra novas siglas diárias |
| `/api/edicoes/executar-script` | POST | `executar_script_cadrifas()` | Executa script de cadastro |
| `/api/edicoes/cadastrar-sigla-avulsa` | POST | `cadastrar_sigla_avulsa()` | Cadastra sigla avulsa |
| `/api/edicoes/{siglas_id}/tem-pendencias` | GET | `verificar_pendencias_siglas()` | Verifica pendências |
| `/api/edicoes/excluir-siglas` | DELETE | `excluir_siglas_diarias()` | Exclui siglas |

### Grupo 2: Premiações (5 endpoints)
**Arquivo destino**: `routers/premiacoes.py`

| Endpoint | Método | Função | Descrição |
|----------|--------|--------|-----------|
| `/api/premiacoes` | GET | `listar_premiacoes()` | Lista premiações |
| `/siglas` | GET | `listar_siglas()` | Lista siglas |
| `/premiacao/{premiacao_id}` | GET | `detalhar_premiacao()` | Detalha premiação |
| `/premiacao` | POST | `criar_premiacao()` | Cria premiação |
| `/premiacao/{premiacao_id}` | PUT | `atualizar_premiacao()` | Atualiza premiação |

### Grupo 3: Uploads (4 endpoints)
**Arquivo destino**: `routers/uploads.py`

| Endpoint | Método | Função | Descrição |
|----------|--------|--------|-----------|
| `/upload-imagem-temp` | POST | `upload_imagem_temp()` | Upload temporário |
| `/confirmar-upload` | POST | `confirmar_upload()` | Confirma upload |
| `/limpar-uploads-temp` | POST | `limpar_uploads_temp()` | Limpa uploads temp |
| `/remover-upload-temp` | DELETE | `remover_upload_temp()` | Remove upload temp |

### Grupo 4: Dashboard (7 endpoints)
**Arquivo destino**: `routers/dashboard.py`

| Endpoint | Método | Função | Descrição |
|----------|--------|--------|-----------|
| `/api/dashboard/extracoes-recentes` | GET | `obter_extracoes_recentes()` | Extrações recentes |
| `/api/dashboard/enviar-link-edicao/{edicao}` | POST | `enviar_link_edicao()` | Envia link |
| `/api/dashboard/gerar-relatorio/{edicao}` | POST | `gerar_relatorio()` | Gera relatório |
| `/api/dashboard/notify-update` | POST | `notificar_atualizacao_dashboard()` | Notifica atualização |
| `/api/dashboard/verificar-pdf/{edicao}` | GET | `verificar_pdf()` | Verifica PDF |
| `/api/dashboard/download-pdf/{edicao}` | GET | `download_pdf()` | Download PDF |
| `/api/dashboard/check-updates` | GET | `verificar_atualizacoes_agendador()` | Verifica atualizações |

### Grupo 5: Premiados (5 endpoints)
**Arquivo destino**: `routers/premiados.py`

| Endpoint | Método | Função | Descrição |
|----------|--------|--------|-----------|
| `/api/premiados` | GET | `listar_premiados()` | Lista premiados |
| `/api/premiados/estatisticas` | GET | `obter_estatisticas_premiados()` | Estatísticas |
| `/api/premiados/nomes` | GET | `buscar_nomes()` | Busca nomes |
| `/api/premiados/telefones` | GET | `buscar_telefones()` | Busca telefones |
| `/api/premiados/pessoa/{nome}` | GET | `obter_estatisticas_pessoa()` | Estatísticas pessoa |

### Grupo 6: Scripts (8 endpoints)
**Arquivo destino**: `routers/scripts.py`

| Endpoint | Método | Função | Descrição |
|----------|--------|--------|-----------|
| `/api/scripts/verificar-links` | POST | `executar_verificar_links()` | Verifica links |
| `/api/scripts/links-com-problemas` | GET | `obter_links_com_problemas()` | Links com problemas |
| `/api/scripts/links-pendentes` | GET | `obter_links_pendentes()` | Links pendentes |
| `/api/scripts/enviar-links-pendentes` | POST | `executar_enviar_links_pendentes()` | Envia links pendentes |
| `/api/scripts/enviar-edicoes-especificas` | POST | `executar_enviar_edicoes_especificas()` | Envia edições específicas |
| `/api/scripts/executar-para-siglas/{siglas_id}` | POST | `executar_script_para_siglas()` | Executa para siglas |
| `/api/scripts/status-agendador` | GET | `verificar_status_agendador()` | Status agendador |
| `/api/scripts/verificar-andamento-rifas` | POST | `executar_verificar_andamento_rifas()` | Verifica andamento |

### Grupo 7: Extrações (2 endpoints)
**Arquivo destino**: `routers/extracoes.py`

| Endpoint | Método | Função | Descrição |
|----------|--------|--------|-----------|
| `/api/extracoes/tem-pendente` | GET | `existe_pendente()` | Verifica pendente |
| `/api/extracoes/tem-pendente-data` | GET | `existe_pendente_data()` | Verifica pendente por data |

### Grupo 8: Views (7 endpoints)
**Arquivo destino**: `routers/views.py`

| Endpoint | Método | Função | Descrição |
|----------|--------|--------|-----------|
| `/` | GET | `serve_index()` | Página principal |
| `/editar` | GET | `serve_editar()` | Página de edição |
| `/premiacoes` | GET | `serve_premiacoes()` | Página de premiações |
| `/edicoes` | GET | `serve_edicoes()` | Página de edições |
| `/dashboard` | GET | `serve_dashboard()` | Página do dashboard |
| `/teste-sigla-avulsa` | GET | `serve_teste_sigla_avulsa()` | Página de teste |
| `/premiados_consulta` | GET | `serve_premiados_consulta()` | Página de consulta |

## 🔧 Funções Utilitárias Identificadas

### Funções de Banco de Dados (mover para `crud.py`)
```python
# Funções identificadas no código:
- get_all_siglas()
- get_premiacao_by_id()
- get_ultima_data_siglas()
- get_siglas_por_grupo()
- get_premiacoes_ordenadas()
- get_edicoes_com_pendencias()
- get_extracoes_recentes()
- get_premiados_paginados()
- get_estatisticas_premiados()
- get_links_com_problemas()
- get_links_pendentes()
- get_status_agendador()
```

### Funções Utilitárias (mover para `utils.py`)
```python
# Funções identificadas:
- validar_arquivo_upload()
- gerar_nome_arquivo_temp()
- limpar_arquivos_temp()
- executar_script_externo()
- processar_resultado_script()
- gerar_relatorio_pdf()
- verificar_arquivo_pdf()
- formatar_data()
- validar_data()
- calcular_estatisticas()
```

## 📍 Localização por Linhas

### Modelos Pydantic
- **Linhas 50-130**: Todos os modelos Pydantic

### Endpoints por Grupo
- **Views**: Linhas 135-180
- **Edições**: Linhas 177-1613
- **Premiações**: Linhas 300-500
- **Uploads**: Linhas 350-650
- **Dashboard**: Linhas 1684-2400
- **Premiados**: Linhas 2146-2400
- **Scripts**: Linhas 1162-2000
- **Extrações**: Linhas 1104-1159

## 🔄 Dependências Identificadas

### Imports Compartilhados
```python
# Todos os routers precisarão:
from fastapi import APIRouter, HTTPException
from pymysql.cursors import DictCursor
import pymysql
from app.db_config import DB_CONFIG
from app.models import *  # Modelos específicos
```

### Dependências entre Módulos
- **Dashboard** depende de **Edições** (para obter dados)
- **Scripts** depende de **Edições** (para executar scripts)
- **Premiados** depende de **Premiações** (para dados)
- **Uploads** é independente
- **Views** é independente

## ⚠️ Pontos de Atenção na Migração

### 1. Configurações Compartilhadas
```python
# Manter centralizado em db_config.py:
- DB_CONFIG
- UPLOAD_DIR
- TEMP_UPLOAD_DIR
- Outras configurações
```

### 2. Imports Circulares
- **Evitar**: Router A importa Router B e vice-versa
- **Solução**: Usar imports locais ou reorganizar estrutura

### 3. Funções Compartilhadas
- **Identificar**: Funções usadas por múltiplos routers
- **Mover**: Para `utils.py` ou `crud.py`

### 4. Tratamento de Erros
- **Manter**: Padrão consistente de HTTPException
- **Centralizar**: Funções de validação comum

## 📊 Métricas de Complexidade

### Por Router (estimativa)
| Router | Endpoints | Linhas Estimadas | Complexidade |
|--------|-----------|------------------|--------------|
| Views | 7 | ~50 | Baixa |
| Premiações | 5 | ~200 | Média |
| Uploads | 4 | ~150 | Média |
| Extrações | 2 | ~60 | Baixa |
| Premiados | 5 | ~300 | Alta |
| Dashboard | 7 | ~400 | Alta |
| Scripts | 8 | ~500 | Alta |
| Edições | 8 | ~600 | Alta |

### Total Estimado
- **Antes**: 2.478 linhas em 1 arquivo
- **Depois**: ~2.260 linhas distribuídas em 8 arquivos
- **Redução**: ~8% de código (removendo duplicações)

## 🎯 Ordem de Migração Recomendada

1. **Views** (mais simples, independente)
2. **Extrações** (poucos endpoints)
3. **Premiações** (CRUD básico)
4. **Uploads** (funcionalidade isolada)
5. **Premiados** (consultas complexas)
6. **Dashboard** (lógica de negócio)
7. **Scripts** (execução externa)
8. **Edições** (mais complexo, dependências)

## 📝 Checklist de Migração

### Para cada router:
- [ ] Criar arquivo do router
- [ ] Mover endpoints
- [ ] Atualizar imports
- [ ] Testar endpoints
- [ ] Verificar dependências
- [ ] Documentar router

### Geral:
- [ ] Mover modelos para `models.py`
- [ ] Mover funções utilitárias
- [ ] Atualizar `main.py`
- [ ] Testar aplicação completa
- [ ] Verificar logs
- [ ] Documentar mudanças

---

**Data**: Janeiro 2025  
**Versão**: 1.0  
**Status**: Mapeamento Completo 