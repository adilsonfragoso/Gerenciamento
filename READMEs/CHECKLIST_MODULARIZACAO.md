# Checklist de Modularização - Projeto Gerenciamento

## 📋 Checklist Geral

### ✅ Fase 1: Preparação
- [ ] **Criar backup do arquivo atual**
  ```bash
  cp app/main.py app/main_backup_$(date +%Y%m%d_%H%M%S).py
  ```

- [ ] **Criar estrutura de pastas**
  ```bash
  mkdir -p app/routers
  touch app/routers/__init__.py
  ```

- [ ] **Criar arquivos base**
  ```bash
  touch app/models.py
  touch app/crud.py
  touch app/utils.py
  ```

- [ ] **Verificar se a aplicação funciona antes da migração**
  ```bash
  python -m uvicorn app.main:app --reload --port 8001
  ```

### ✅ Fase 2: Migração de Modelos
- [ ] **Mover modelos Pydantic para `models.py`**
  - [ ] `PremiacaoUpdate`
  - [ ] `PremiacaoUpdatePartial`
  - [ ] `SiglasDiariasCreate`
  - [ ] `ScriptExecuteRequest`
  - [ ] `SiglaAvulsaCreate`
  - [ ] `ExcluirSiglasRequest`
  - [ ] `EdicoesEspecificasRequest`

- [ ] **Atualizar imports no `main.py`**
  ```python
  from app.models import (
      PremiacaoUpdate, PremiacaoUpdatePartial, SiglasDiariasCreate,
      ScriptExecuteRequest, SiglaAvulsaCreate, ExcluirSiglasRequest,
      EdicoesEspecificasRequest
  )
  ```

- [ ] **Testar se a aplicação ainda funciona**
  ```bash
  python -m uvicorn app.main:app --reload --port 8001
  ```

### ✅ Fase 3: Migração de Routers

#### 3.1 Router Views (Mais Simples)
- [ ] **Criar `app/routers/views.py`**
- [ ] **Mover endpoints HTML**:
  - [ ] `serve_index()` - GET `/`
  - [ ] `serve_editar()` - GET `/editar`
  - [ ] `serve_premiacoes()` - GET `/premiacoes`
  - [ ] `serve_edicoes()` - GET `/edicoes`
  - [ ] `serve_dashboard()` - GET `/dashboard`
  - [ ] `serve_teste_sigla_avulsa()` - GET `/teste-sigla-avulsa`
  - [ ] `serve_premiados_consulta()` - GET `/premiados_consulta`

- [ ] **Incluir router no `main.py`**
  ```python
  from app.routers import views
  app.include_router(views.router)
  ```

- [ ] **Testar endpoints HTML**
  ```bash
  curl http://localhost:8001/
  curl http://localhost:8001/editar
  curl http://localhost:8001/premiacoes
  ```

#### 3.2 Router Extrações (Poucos Endpoints)
- [ ] **Criar `app/routers/extracoes.py`**
- [ ] **Mover endpoints**:
  - [ ] `existe_pendente()` - GET `/api/extracoes/tem-pendente`
  - [ ] `existe_pendente_data()` - GET `/api/extracoes/tem-pendente-data`

- [ ] **Incluir router no `main.py`**
- [ ] **Testar endpoints**

#### 3.3 Router Premiações (CRUD Básico)
- [ ] **Criar `app/routers/premiacoes.py`**
- [ ] **Mover endpoints**:
  - [ ] `listar_premiacoes()` - GET `/api/premiacoes`
  - [ ] `listar_siglas()` - GET `/siglas`
  - [ ] `detalhar_premiacao()` - GET `/premiacao/{premiacao_id}`
  - [ ] `criar_premiacao()` - POST `/premiacao`
  - [ ] `atualizar_premiacao()` - PUT `/premiacao/{premiacao_id}`

- [ ] **Incluir router no `main.py`**
- [ ] **Testar CRUD completo**

#### 3.4 Router Uploads (Funcionalidade Isolada)
- [ ] **Criar `app/routers/uploads.py`**
- [ ] **Mover endpoints**:
  - [ ] `upload_imagem_temp()` - POST `/upload-imagem-temp`
  - [ ] `confirmar_upload()` - POST `/confirmar-upload`
  - [ ] `limpar_uploads_temp()` - POST `/limpar-uploads-temp`
  - [ ] `remover_upload_temp()` - DELETE `/remover-upload-temp`

- [ ] **Incluir router no `main.py`**
- [ ] **Testar upload de arquivos**

#### 3.5 Router Premiados (Consultas Complexas)
- [ ] **Criar `app/routers/premiados.py`**
- [ ] **Mover endpoints**:
  - [ ] `listar_premiados()` - GET `/api/premiados`
  - [ ] `obter_estatisticas_premiados()` - GET `/api/premiados/estatisticas`
  - [ ] `buscar_nomes()` - GET `/api/premiados/nomes`
  - [ ] `buscar_telefones()` - GET `/api/premiados/telefones`
  - [ ] `obter_estatisticas_pessoa()` - GET `/api/premiados/pessoa/{nome}`

- [ ] **Incluir router no `main.py`**
- [ ] **Testar consultas complexas**

#### 3.6 Router Dashboard (Lógica de Negócio)
- [ ] **Criar `app/routers/dashboard.py`**
- [ ] **Mover endpoints**:
  - [ ] `obter_extracoes_recentes()` - GET `/api/dashboard/extracoes-recentes`
  - [ ] `enviar_link_edicao()` - POST `/api/dashboard/enviar-link-edicao/{edicao}`
  - [ ] `gerar_relatorio()` - POST `/api/dashboard/gerar-relatorio/{edicao}`
  - [ ] `notificar_atualizacao_dashboard()` - POST `/api/dashboard/notify-update`
  - [ ] `verificar_pdf()` - GET `/api/dashboard/verificar-pdf/{edicao}`
  - [ ] `download_pdf()` - GET `/api/dashboard/download-pdf/{edicao}`
  - [ ] `verificar_atualizacoes_agendador()` - GET `/api/dashboard/check-updates`

- [ ] **Incluir router no `main.py`**
- [ ] **Testar funcionalidades do dashboard**

#### 3.7 Router Scripts (Execução Externa)
- [ ] **Criar `app/routers/scripts.py`**
- [ ] **Mover endpoints**:
  - [ ] `executar_verificar_links()` - POST `/api/scripts/verificar-links`
  - [ ] `obter_links_com_problemas()` - GET `/api/scripts/links-com-problemas`
  - [ ] `obter_links_pendentes()` - GET `/api/scripts/links-pendentes`
  - [ ] `executar_enviar_links_pendentes()` - POST `/api/scripts/enviar-links-pendentes`
  - [ ] `executar_enviar_edicoes_especificas()` - POST `/api/scripts/enviar-edicoes-especificas`
  - [ ] `executar_script_para_siglas()` - POST `/api/scripts/executar-para-siglas/{siglas_id}`
  - [ ] `verificar_status_agendador()` - GET `/api/scripts/status-agendador`
  - [ ] `executar_verificar_andamento_rifas()` - POST `/api/scripts/verificar-andamento-rifas`

- [ ] **Incluir router no `main.py`**
- [ ] **Testar execução de scripts**

#### 3.8 Router Edições (Mais Complexo)
- [ ] **Criar `app/routers/edicoes.py`**
- [ ] **Mover endpoints**:
  - [ ] `listar_edicoes()` - GET `/api/edicoes`
  - [ ] `obter_ultima_data()` - GET `/api/edicoes/ultima-data`
  - [ ] `obter_siglas_por_grupo()` - GET `/api/edicoes/siglas-por-grupo/{data}`
  - [ ] `cadastrar_siglas_diarias()` - POST `/api/edicoes/cadastrar-siglas`
  - [ ] `executar_script_cadrifas()` - POST `/api/edicoes/executar-script`
  - [ ] `cadastrar_sigla_avulsa()` - POST `/api/edicoes/cadastrar-sigla-avulsa`
  - [ ] `verificar_pendencias_siglas()` - GET `/api/edicoes/{siglas_id}/tem-pendencias`
  - [ ] `excluir_siglas_diarias()` - DELETE `/api/edicoes/excluir-siglas`

- [ ] **Incluir router no `main.py`**
- [ ] **Testar funcionalidades de edições**

### ✅ Fase 4: Refatoração de Utilitários
- [ ] **Identificar funções de banco de dados**
  - [ ] Mover para `crud.py`
  - [ ] Atualizar imports nos routers

- [ ] **Identificar funções utilitárias**
  - [ ] Mover para `utils.py`
  - [ ] Atualizar imports nos routers

- [ ] **Centralizar configurações**
  - [ ] Verificar `db_config.py`
  - [ ] Atualizar imports

### ✅ Fase 5: Limpeza e Testes
- [ ] **Limpar `main.py`**
  - [ ] Remover endpoints movidos
  - [ ] Manter apenas inicialização do FastAPI
  - [ ] Organizar imports

- [ ] **Testar aplicação completa**
  ```bash
  python -m uvicorn app.main:app --reload --port 8001
  ```

- [ ] **Testar todos os endpoints**
  ```bash
  # Testar endpoints principais
  curl http://localhost:8001/api/premiacoes
  curl http://localhost:8001/api/edicoes
  curl http://localhost:8001/api/premiados
  curl http://localhost:8001/api/dashboard/extracoes-recentes
  ```

- [ ] **Verificar logs e erros**
  - [ ] Verificar console do servidor
  - [ ] Verificar logs de erro
  - [ ] Testar funcionalidades críticas

## 🔧 Comandos Úteis Durante a Migração

### Verificar Tamanho dos Arquivos
```bash
# Antes da migração
wc -l app/main.py

# Durante a migração
wc -l app/routers/*.py
wc -l app/models.py
wc -l app/crud.py
wc -l app/utils.py
```

### Verificar Imports
```bash
# Verificar imports no projeto
grep -r "import" app/
grep -r "from" app/

# Verificar imports específicos
grep -r "from app.models" app/
grep -r "from app.crud" app/
```

### Testar Aplicação
```bash
# Testar se inicia
python -m uvicorn app.main:app --reload --port 8001

# Testar endpoints específicos
curl -X GET http://localhost:8001/api/premiacoes
curl -X GET http://localhost:8001/api/edicoes
curl -X GET http://localhost:8001/api/premiados
```

### Verificar Estrutura
```bash
# Verificar estrutura de arquivos
tree app/
find app/ -name "*.py" -type f
```

## ⚠️ Pontos de Atenção

### Durante Cada Fase:
- [ ] **Fazer commit após cada router migrado**
- [ ] **Testar endpoints antes de prosseguir**
- [ ] **Verificar se não há imports circulares**
- [ ] **Manter backup do estado anterior**

### Problemas Comuns:
- [ ] **Imports circulares**: Reorganizar estrutura
- [ ] **Configurações não encontradas**: Verificar `db_config.py`
- [ ] **Endpoints não funcionando**: Verificar inclusão do router
- [ ] **Erros de sintaxe**: Verificar imports e dependências

## 📊 Métricas de Progresso

### Contadores:
- [ ] **Routers criados**: 0/8
- [ ] **Endpoints migrados**: 0/47
- [ ] **Modelos movidos**: 0/7
- [ ] **Funções utilitárias movidas**: 0/15

### Status por Router:
- [ ] **Views**: ❌ Não iniciado
- [ ] **Extrações**: ❌ Não iniciado
- [ ] **Premiações**: ❌ Não iniciado
- [ ] **Uploads**: ❌ Não iniciado
- [ ] **Premiados**: ❌ Não iniciado
- [ ] **Dashboard**: ❌ Não iniciado
- [ ] **Scripts**: ❌ Não iniciado
- [ ] **Edições**: ❌ Não iniciado

## 🎯 Critérios de Sucesso

### Para Cada Router:
- [ ] **Arquivo criado e funcional**
- [ ] **Endpoints respondendo corretamente**
- [ ] **Imports organizados**
- [ ] **Testes passando**

### Para o Projeto:
- [ ] **Aplicação iniciando sem erros**
- [ ] **Todos os endpoints funcionando**
- [ ] **Código mais organizado**
- [ ] **Documentação atualizada**

## 📝 Notas de Implementação

### Para cada router criado, adicionar:
```python
"""
Router: [Nome do Router]
Descrição: [Descrição do que o router faz]
Endpoints: [Lista de endpoints]
Autor: [Seu nome]
Data: [Data de criação]
"""
```

### Estrutura padrão de router:
```python
from fastapi import APIRouter, HTTPException
from app.models import *
from app.crud import *
from app.utils import *

router = APIRouter(prefix="/api/[nome]", tags=["[nome]"])

# Endpoints aqui...
```

---

**Data de criação**: Janeiro 2025  
**Versão**: 1.0  
**Status**: Checklist Pronto  
**Próximo passo**: Iniciar Fase 1 - Preparação 