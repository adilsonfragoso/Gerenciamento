# Documentação Detalhada dos Arquivos do Sistema

## Backend (FastAPI)

### `app/main.py`
**Função**: Aplicação principal do FastAPI
**Tamanho**: ~705 linhas
**Dependências**: FastAPI, pymysql, PIL, requests, subprocess

**Estrutura Principal**:
```python
# Modelos Pydantic
class PremiacaoUpdate(BaseModel)
class PremiacaoUpdatePartial(BaseModel)
class SiglasDiariasCreate(BaseModel)
class ScriptExecuteRequest(BaseModel)
class SiglaAvulsaCreate(BaseModel)

# Endpoints
@app.get("/") - Página inicial
@app.get("/editar") - Página de edição
@app.get("/premiacoes") - Página de premiações
@app.get("/edicoes") - Página de edições
@app.get("/api/edicoes") - Lista edições
@app.get("/api/edicoes/ultima-data") - Próxima data
@app.get("/api/edicoes/siglas-por-grupo/{data}") - Siglas por grupo
@app.post("/api/edicoes/cadastrar-siglas") - Cadastra siglas
@app.post("/api/edicoes/cadastrar-sigla-avulsa") - Cadastra sigla avulsa
@app.post("/api/edicoes/executar-script") - Executa script
@app.get("/api/premiacoes") - Lista premiações
@app.get("/siglas") - Lista siglas
@app.get("/premiacao/{id}") - Detalha premiação
@app.post("/premiacao") - Cria premiação
@app.put("/premiacao/{id}") - Atualiza premiação
@app.post("/upload-imagem") - Upload de imagem
```

**Funcionalidades Principais**:
- Roteamento de páginas HTML
- Endpoints da API REST
- Upload de imagens para VPS
- Execução de scripts externos
- Validação de dados com Pydantic
- Tratamento de erros HTTP

### `app/crud.py`
**Função**: Operações CRUD para premiações
**Tamanho**: ~30 linhas
**Dependências**: pymysql, db_config

**Funções**:
```python
def get_all_siglas() - Retorna todas as siglas ordenadas
def get_premiacao_by_id(id) - Retorna premiação por ID
```

**Características**:
- Ordenação especial por grupos de siglas
- Conexão automática com banco
- Tratamento de erros

### `app/db_config.py`
**Função**: Configuração do banco de dados
**Tamanho**: ~10 linhas
**Dependências**: Nenhuma

**Configuração**:
```python
DB_CONFIG = {
    'host': 'pma.megatrends.site',
    'user': 'root',
    'password': 'Define@4536#8521',
    'database': 'gerenciamento',
    'charset': 'utf8mb4'
}
```

---

## Frontend (HTML/JavaScript)

### `static/edicoes.html`
**Função**: Página principal do sistema
**Tamanho**: ~1266 linhas
**Dependências**: CSS inline, JavaScript inline

**Estrutura**:
```html
<!-- CSS Styles -->
<style>
  /* Estilos para tabelas, modais, botões, responsividade */
</style>

<!-- Modais -->
<div id="modalOverlay"> - Modal de confirmação de siglas
<div id="modalScriptOverlay"> - Modal de execução de script

<!-- Conteúdo Principal -->
<div class="container">
  <!-- Seção Novas Siglas -->
  <div class="nova-data-section">
    <!-- Campo de data, dia da semana, dropdown de siglas -->
    <!-- Botão Cadastrar Siglas -->
  </div>
  
  <!-- Seção Sigla Avulsa -->
  <div>
    <!-- Dropdown de premiações -->
    <!-- Botão Cadastrar Sigla Avulsa -->
  </div>
  
  <!-- Tabela de Edições -->
  <table id="edicoes-table">
    <!-- Cabeçalho e corpo da tabela -->
  </table>
</div>

<!-- JavaScript -->
<script>
  // Funções de formatação
  function formatarData(dataString)
  function formatarDiaSemana(diaSemana)
  
  // Funções de carregamento
  function carregarEdicoes()
  function carregarDataPadrao()
  function carregarPremiacoes()
  function carregarSiglasPorGrupo(data)
  
  // Funções de modal
  function mostrarModalConfirmacao(dados)
  function fecharModal()
  function alternarModoEdicao()
  function processarConfirmacao()
  
  // Funções de script
  function confirmarExecutarScript(edicao)
  function fecharModalScript()
  function executarScriptConfirmado()
  
  // Event listeners
  document.addEventListener('DOMContentLoaded', function() {
    // Inicialização e listeners
  })
</script>
```

**Funcionalidades**:
- Interface completa para gerenciamento de edições
- Modais interativos
- Validação de dados
- Execução de scripts
- Responsividade mobile
- Debug de datas

### `static/editar.html`
**Função**: Página de edição de premiações
**Tamanho**: ~711 linhas
**Dependências**: CSS inline, JavaScript inline

**Estrutura**:
```html
<!-- Formulário de Edição -->
<form id="editarForm">
  <!-- Campos: sigla, horario, precocota, prêmios, etc. -->
  <!-- Upload de imagem -->
  <!-- Botões de ação -->
</form>

<!-- JavaScript -->
<script>
  // Funções de validação
  // Funções de upload
  // Funções de formatação
  // Event listeners
</script>
```

**Funcionalidades**:
- Formulário completo para edição
- Upload de imagens
- Validação de campos
- Integração com VPS

### `static/index.html`
**Função**: Página inicial do sistema
**Tamanho**: ~93 linhas
**Dependências**: CSS inline

**Estrutura**:
```html
<!-- Menu de navegação -->
<nav class="menu">
  <!-- Links para outras páginas -->
</nav>

<!-- Conteúdo principal -->
<div class="container">
  <!-- Descrição do sistema -->
  <!-- Lista de funcionalidades -->
</div>
```

**Funcionalidades**:
- Navegação principal
- Descrição do sistema
- Links para funcionalidades

### `static/premiacoes.html`
**Função**: Página de consulta de premiações
**Tamanho**: ~88 linhas
**Dependências**: CSS inline, JavaScript inline

**Estrutura**:
```html
<!-- Tabela de consulta -->
<table id="siglas-table">
  <!-- Cabeçalho e corpo -->
</table>

<!-- JavaScript -->
<script>
  // Funções de consulta
  // Funções de exibição
</script>
```

**Funcionalidades**:
- Consulta de siglas
- Exibição em tabela
- Filtros básicos

---

## Arquivos de Estilo

### `static/css/index.css`
**Função**: Estilos globais do sistema
**Tamanho**: ~26 linhas
**Dependências**: Nenhuma

**Conteúdo**:
```css
/* Estilos básicos */
body, html
.container
.menu
/* Responsividade */
@media (max-width: 600px)
```

---

## Arquivos JavaScript

### `static/js/index.js`
**Função**: JavaScript auxiliar global
**Tamanho**: ~26 linhas
**Dependências**: Nenhuma

**Conteúdo**:
```javascript
// Funções utilitárias globais
// Event listeners comuns
```

---

## Diretórios do Sistema

### `uploads/`
**Função**: Armazenamento local de imagens
**Conteúdo**: Imagens enviadas pelos usuários
**Processo**: Temporário antes do upload para VPS

### `temp_uploads/`
**Função**: Processamento temporário de imagens
**Conteúdo**: Arquivos temporários durante upload
**Processo**: Limpeza automática após processamento

### `scripts/`
**Função**: Scripts externos do sistema
**Conteúdo**: `cadRifas_litoral_v3`
**Processo**: Execução via subprocesso

---

## Configurações Externas

### VPS Externa
**Host**: pma.megatrends.site
**Serviços**: MySQL, FTP, HTTP
**Configuração**: 
```python
VPS_FTP_CONFIG = {
    'host': 'pma.megatrends.site',
    'user': 'root',
    'password': 'Define@4536#8521',
    'upload_path': '/uploads/'
}
```

### Script Externo
**Arquivo**: `cadRifas_litoral_v3`
**Linguagem**: Python
**Dependências**: Selenium WebDriver
**Parâmetros**: `--siglas`, `--data`
**Funcionalidade**: Automação de cadastro no sistema Litoral da Sorte

---

## Dependências do Sistema

### Python (Backend)
```
fastapi
uvicorn
pymysql
Pillow
requests
pydantic
python-multipart
```

### JavaScript (Frontend)
- Vanilla JavaScript (sem dependências externas)
- APIs nativas do navegador
- Fetch API para requisições

### CSS (Frontend)
- CSS3 puro
- Flexbox para layout
- Media queries para responsividade

---

## Estrutura de Banco de Dados

### Tabela `siglas_diarias`
```sql
CREATE TABLE siglas_diarias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    diaSemana VARCHAR(20),
    data_sorteio DATE,
    siglas TEXT,
    tipo VARCHAR(10) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela `premiacoes`
```sql
CREATE TABLE premiacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sigla VARCHAR(100),
    horario VARCHAR(50),
    precocota DECIMAL(10,2),
    primeiro VARCHAR(100),
    segundo VARCHAR(100),
    terceiro VARCHAR(100),
    -- ... outros campos de prêmios
    imagem_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Fluxo de Dados

### Cadastro de Siglas Regulares
1. Frontend: Seleção de data → Dropdown de siglas → Modal de confirmação
2. Backend: Validação → Inserção com `tipo = ''`
3. Frontend: Feedback → Recarregamento da tabela

### Cadastro de Sigla Avulsa
1. Frontend: Seleção de data → Dropdown de premiações → Confirmação
2. Backend: Validação → Inserção com `tipo = 'extra'`
3. Frontend: Feedback → Recarregamento da tabela

### Execução de Script
1. Frontend: Clique no botão → Modal de confirmação
2. Backend: Validação → Execução do script → Logs
3. Frontend: Feedback de sucesso/erro

### Upload de Imagem
1. Frontend: Seleção de arquivo → Validação
2. Backend: Processamento → Upload para VPS → Resposta
3. Frontend: Feedback de sucesso/erro

---

**Última Atualização**: Dezembro 2024
**Versão**: 1.6.0
**Status**: Documentação completa 