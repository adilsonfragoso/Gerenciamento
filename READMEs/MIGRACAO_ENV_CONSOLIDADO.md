# Migração para .env - Documento Consolidado
## Projeto Gerenciamento - Arquitetura Centralizada de Configurações

---

## 📋 Visão Geral

Este documento consolida toda a informação sobre a migração do projeto para usar arquivos `.env`, centralizando configurações em `app/db_config.py` e eliminando credenciais hardcoded do código.

### 🎯 Objetivos
- **Centralizar configurações** em um único local
- **Eliminar credenciais hardcoded** do código
- **Facilitar migração entre ambientes** (dev, test, prod)
- **Simplificar mudanças de servidor** (pma.megatrends.site → pma.linksystems.com.br)
- **Melhorar segurança** evitando exposição de dados sensíveis
- **Padronizar abordagem** em todo o projeto

---

## 🏗️ Arquitetura Alvo

```
Scripts → app/db_config.py → .env
```

### ❌ Situação Atual (Problemática)
```
Projeto/
├── app/
│   ├── main.py              # Usa .env ✅
│   └── db_config.py         # Usa .env ✅
├── scripts/
│   ├── config_cadRifas.py   # Hardcoded ❌
│   ├── cadRifas_litoral_latest.py
│   └── outros_scripts.py    # Hardcoded ❌
└── outros_arquivos.py       # Hardcoded ❌
```

### ✅ Situação Proposta (Ideal)
```
Projeto/
├── .env                     # Configurações centralizadas
├── app/
│   ├── main.py              # Usa .env ✅
│   └── db_config.py         # Usa .env ✅
├── scripts/
│   ├── config_cadRifas.py   # Usa .env ✅
│   ├── cadRifas_litoral_latest.py
│   └── outros_scripts.py    # Usa .env ✅
└── outros_arquivos.py       # Usa .env ✅
```

---

## 📊 Status Atual do Projeto

### ✅ Scripts Já Padronizados (NÃO MEXER)
- [x] **app/db_config.py**: ✅ Padronizado (usa .env)
- [x] **app/main.py**: ✅ Padronizado (usa db_config.py)
- [x] **scripts/novo_verificalinks.py**: ✅ CONCLUÍDO (Migrado para .env - SENHA REMOVIDA)

### ⚠️ Scripts Parcialmente Migrados (COMPLETAR)
- [x] **scripts/config_cadRifas.py**: ✅ CONCLUÍDO (Migração completa para .env - FALLBACKS REMOVIDOS)

### ❌ Scripts Críticos com Senhas Expostas (PRIORIDADE MÁXIMA)
- [x] **scripts/verificar_andamento_rifas.py**: ✅ CONCLUÍDO (Migração para db_config.py)
- [x] **scripts/novo_chamadas_group_latest.py**: ✅ CONCLUÍDO (Migração para db_config.py)
- [x] **scripts/cadastrar_siglas.py**: ✅ CONCLUÍDO (Migração para db_config.py)
- [x] **scripts/cadastrar_sigla_avulsa.py**: ✅ CONCLUÍDO (Migração para db_config.py)
- [x] **scripts/recuperar_rifas_erro.py**: ✅ CONCLUÍDO (Migração para db_config.py)

### ❌ Scripts Adicionais Encontrados (PRIORIDADE ALTA)
- [x] **scripts/envio_automatico_pdfs_whatsapp.py**: ✅ CONCLUÍDO (Migração para db_config.py)
- [x] **scripts/alimenta_premiados.py**: ✅ CONCLUÍDO (Migração para db_config.py)
- [ ] **alimenta_siglas_relatorios.py**: ❌ Não iniciado (SENHA EXPOSTA)

### 📈 Métricas de Progresso
- [x] **Scripts identificados**: 9/9
- [ ] **Scripts migrados**: 8/9 ✅
- [ ] **Configurações centralizadas**: 8/9
- [ ] **Testes realizados**: 8/9 ✅

---

## 🔧 Infraestrutura Atual

### ✅ Arquivos Existentes (NÃO MEXER)
- [x] **app/db_config.py**: ✅ Funcionando
- [x] **.env**: ✅ Existe na raiz
- [x] **python-dotenv**: ✅ Instalado

### 📝 Configurações Necessárias no .env

```env
# Banco de Dados
DB_HOST=seu_servidor_aqui
DB_USER=seu_usuario_aqui
DB_PASSWORD=sua_senha_aqui
DB_NAME=nome_do_banco_aqui
DB_CHARSET=utf8mb4
DB_PORT=3306

# Servidor
SERVER_HOST=seu_servidor_aqui
SERVER_PORT=80
SERVER_PROTOCOL=http
LOGIN_URL=https://seu_servidor_aqui/login

# Login
LOGIN_EMAIL=seu_email@exemplo.com
LOGIN_PASSWORD=sua_senha_login_aqui

# Pagamento
PAYMENT_CLIENT_ID=seu_client_id_aqui
PAYMENT_CLIENT_SECRET=seu_client_secret_aqui
PAYMENT_CHAVE_PIX=sua_chave_pix_aqui

# Arquivos
UPLOAD_DIR=uploads
TEMP_UPLOAD_DIR=uploads/temp
IMAGES_DIR=uploads
LOGS_DIR=logs

# Navegador
CHROME_DRIVER_PATH=C:/chromedriver/chromedriver.exe
CHROME_HEADLESS=false
CHROME_TIMEOUT=30
```

---

## 🚨 Plano de Ação - Prioridades

### 🚨 FASE 1: Críticos (Segurança) - PRIORIDADE MÁXIMA

#### 1.1 Completar config_cadRifas.py (URGENTE)
**Status**: ⚠️ Parcialmente migrado (FALLBACK EXPOSTO)

**Problema atual**:
```python
# ATUAL (PROBLEMÁTICO):
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST"),  # ✅ OK
    "user": os.getenv("DB_USER"),  # ✅ OK
    "password": os.getenv("DB_PASSWORD"),  # ✅ OK
    "database": os.getenv("DB_NAME"),  # ✅ OK
    "charset": os.getenv("DB_CHARSET", "utf8mb4")  # ✅ OK
}

# FALTANDO MIGRAR:
BROWSER_CONFIG = {...}  # ❌ Ainda hardcoded
LOGIN_CONFIG = {...}    # ❌ Ainda hardcoded
PAYMENT_CONFIG = {...}  # ❌ Ainda hardcoded
```

**Ação necessária**:
- Migrar BROWSER_CONFIG, LOGIN_CONFIG, PAYMENT_CONFIG para usar .env
- Remover fallbacks expostos

#### 1.2 Migrar Scripts Críticos (URGENTE)
Todos os scripts abaixo têm a senha `"Define@4536#8521"` hardcoded:

1. **verificar_andamento_rifas.py** (LINHA 35)
2. **recuperar_rifas_erro.py** (LINHA 33)
3. **novo_chamadas_group_latest.py** (LINHA 8)
4. **envio_automatico_pdfs_whatsapp.py** (LINHA 30)

**Padrão de migração**:
```python
# ANTES (CRÍTICO):
DB_CONFIG = {
    'host': 'pma.megatrends.site',
    'user': 'root',
    'password': 'Define@4536#8521',  # ❌ SENHA EXPOSTA!
    'db': 'litoral',
    'charset': 'utf8mb4'
}

# DEPOIS (SEGURO):
import sys
sys.path.append('../app')
from db_config import DB_CONFIG
```

### 🔶 FASE 2: Importantes - PRIORIDADE ALTA
- [ ] **cadastrar_siglas.py**
- [ ] **cadastrar_sigla_avulsa.py**
- [ ] **alimenta_premiados.py**
- [ ] **alimenta_siglas_relatorios.py**

### 🔵 FASE 3: Outros Scripts - PRIORIDADE BAIXA
- [ ] **Identificar outros scripts com configurações**
- [ ] **Aplicar padrão de migração**
- [ ] **Testar individualmente**

---

## 🛠️ Processo de Migração por Script

### Template de Migração

#### 1. **Fazer Backup**
```bash
cp scripts/nome_do_script.py scripts/nome_do_script_backup_$(date +%Y%m%d_%H%M%S).py
```

#### 2. **Adicionar Import do db_config**
```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from db_config import DB_CONFIG
```

#### 3. **Substituir Configuração Hardcoded**
```python
# REMOVER:
# DB_CONFIG = {...}

# USAR:
# DB_CONFIG (importado de app.db_config)
```

#### 4. **Testar Script**
```bash
python scripts/nome_do_script.py
```

### Exemplo Prático: Migrando Script Simples

#### **Antes (Hardcoded)**
```python
# scripts/exemplo.py
DB_CONFIG = {
    'host': 'pma.megatrends.site',
    'user': 'root',
    'password': 'Define@4536#8521',  # ❌ SENHA EXPOSTA
    'db': 'litoral',
    'charset': 'utf8mb4'
}

def conectar_banco():
    return mysql.connector.connect(**DB_CONFIG)
```

#### **Depois (Usando db_config)**
```python
# scripts/exemplo.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from db_config import DB_CONFIG

def conectar_banco():
    return mysql.connector.connect(**DB_CONFIG)
```

---

## ✅ Checklist de Validação

### Para cada script migrado:
- [ ] **Configurações carregadas do .env**
- [ ] **Funcionalidade mantida**
- [ ] **Sem erros de configuração**
- [ ] **Testes passando**

### Para o projeto:
- [ ] **Todas as configurações centralizadas**
- [ ] **Segurança mantida**
- [ ] **Facilidade de migração**
- [ ] **Documentação atualizada**

---

## 🔧 Comandos de Validação

### Verificar Configurações
```bash
# Verificar se .env está sendo carregado
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('DB_HOST:', os.getenv('DB_HOST'))"

# Verificar se db_config.py carrega corretamente
python -c "from app.db_config import DB_CONFIG; print('DB Config:', DB_CONFIG)"
```

### Verificar Scripts
```bash
# Testar import de configurações
python -c "from scripts.config_cadRifas import DATABASE_CONFIG; print('Config OK:', 'host' in DATABASE_CONFIG)"

# Testar script completo
python scripts/cadRifas_litoral_latest.py
```

### Verificar Segurança
```bash
# Verificar se não há credenciais hardcoded
grep -r "password.*=.*['\"]" scripts/
grep -r "senha.*=.*['\"]" scripts/
grep -r "secret.*=.*['\"]" scripts/
```

### Verificar Versionamento
```bash
# Verificar se .env não está versionado
git status .env
# Deve mostrar "untracked" ou não aparecer

# Verificar se .env.example está versionado
git status .env.example
# Deve estar tracked
```

---

## ⚠️ Pontos de Atenção

### Durante a Migração:
- [ ] **Fazer backup antes de cada mudança**
- [ ] **Testar cada script individualmente**
- [ ] **Verificar se não há imports quebrados**
- [ ] **Manter versão anterior funcionando**
- [ ] **NÃO MEXER nos scripts já padronizados**

### Problemas Comuns:
- [ ] **Variável não encontrada**: Verificar se está no .env
- [ ] **Tipo de dado incorreto**: Usar conversão adequada (int, bool)
- [ ] **Caminho relativo**: Usar caminhos absolutos ou relativos corretos
- [ ] **Permissões**: Verificar se .env tem permissões corretas

---

## 🎯 Próximos Passos Recomendados

### **Imediato (Hoje)**
1. **Completar migração do `config_cadRifas.py`** (mais urgente)
2. **Migrar os 4 scripts críticos da FASE 1** (verificar_andamento_rifas.py, recuperar_rifas_erro.py, novo_chamadas_group_latest.py, envio_automatico_pdfs_whatsapp.py)

### **Curto Prazo (Esta semana)**
3. **Migrar scripts da FASE 2** (cadastrar_siglas.py, cadastrar_sigla_avulsa.py, alimenta_premiados.py, alimenta_siglas_relatorios.py)
4. **Criar `.env.example`** como template
5. **Testar todos os scripts migrados**

### **Médio Prazo (Próxima semana)**
6. **Identificar e migrar scripts restantes**
7. **Documentar processo completo**
8. **Validar migração em ambiente de teste**

---

## 📝 Exemplo de Migração de Servidor

### **Antes da Migração**
```env
# .env
SERVER_HOST=pma.megatrends.site
LOGIN_URL=https://pma.megatrends.site/login
```

### **Durante a Migração**
```env
# .env
SERVER_HOST=pma.linksystems.com.br
LOGIN_URL=https://pma.linksystems.com.br/login
```

### **Resultado**
- **Um único arquivo** para mudar
- **Todos os scripts** automaticamente atualizados
- **Zero alteração** no código
- **Migração instantânea**

---

## 🔄 Benefícios Esperados

### Imediatos
- **Segurança**: Credenciais não expostas no código
- **Flexibilidade**: Mudanças sem alterar código
- **Organização**: Configurações centralizadas

### Médio Prazo
- **Facilidade de migração**: Mudar servidor em um arquivo
- **Ambientes múltiplos**: dev, test, prod
- **Manutenibilidade**: Menos código para manter

### Longo Prazo
- **Escalabilidade**: Fácil adição de novos ambientes
- **Automação**: Deploy automatizado
- **Padrões**: Código mais profissional

---

**Data de criação**: Janeiro 2025  
**Versão**: 2.0 (Consolidado)  
**Status**: Documento Único  
**Próximo passo**: Completar migração do config_cadRifas.py 