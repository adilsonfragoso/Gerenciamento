# Botão "Cadastrar Siglas" - Documentação Completa

> 📖 **Documentação Principal**: [README.md](README.md) - Visão geral completa do sistema

## Visão Geral

O botão **"Cadastrar Siglas"** é uma funcionalidade central do módulo de edições que permite cadastrar múltiplas siglas para uma data específica, seguindo regras de negócio definidas e alimentando automaticamente a tabela `extracoes_cadastro` para processamento posterior.

## Localização e Interface

### **Página:** `/edicoes`
### **Seção:** "Novas Siglas"
### **Posição:** Centro da seção, após o dropdown de siglas

```html
<button id="btnCadastrarSiglas" style="background: #1976d2; color: white; border: none; padding: 12px 24px; border-radius: 6px; font-size: 16px; font-weight: 500; cursor: pointer; transition: background-color 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    Cadastrar Siglas
</button>
```

## Pré-requisitos

### **Campos Obrigatórios:**
1. **Data selecionada** (`novaData`) - Input de data
2. **Siglas selecionadas** (`siglasDropdown`) - Dropdown com opções do grupo

### **Validações Frontend:**
- ✅ Data não pode estar vazia
- ✅ Dropdown de siglas deve ter uma opção selecionada
- ✅ Valor do dropdown deve ser JSON válido

## Fluxo Completo

### **1. Preparação dos Dados**

#### **1.1 Carregamento da Data Padrão**
```javascript
// Endpoint: GET /api/edicoes/ultima-data
// Retorna: { "proxima_data": "2025-01-21" }
```

#### **1.2 Cálculo do Dia da Semana**
```javascript
// Baseado na data selecionada
const data = new Date(dataString + 'T00:00:00-03:00');
const diasSemana = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado'];
const diaNome = diasSemana[data.getDay()];
```

#### **1.3 Determinação do Grupo**
```javascript
// Grupos baseados no dia da semana:
// Grupo 1: segunda, terça, quinta, sexta
// Grupo 2: quarta, sábado  
// Grupo 3: domingo
```

#### **1.4 Carregamento de Siglas do Grupo**
```javascript
// Endpoint: GET /api/edicoes/siglas-por-grupo/{data}
// Retorna: { "grupo": 1, "siglas": [...] }
```

### **2. Validações Frontend**

#### **2.1 Validação de Data**
```javascript
if (!novaDataInput.value) {
    alert('Por favor, selecione uma data primeiro.');
    return;
}
```

#### **2.2 Validação de Siglas**
```javascript
if (!siglasDropdown.value || siglasDropdown.value === "") {
    alert('Por favor, selecione uma opção de siglas.');
    return;
}
```

#### **2.3 Parse do JSON**
```javascript
try {
    const registroSelecionado = JSON.parse(siglasDropdown.value);
    siglasSelecionadas = registroSelecionado.siglas;
} catch (e) {
    alert('Erro ao processar as siglas selecionadas. Tente novamente.');
    return;
}
```

### **3. Modal de Confirmação**

#### **3.1 Estrutura do Modal**
```html
<div id="modalOverlay" class="modal-overlay">
    <div class="modal-content">
        <div class="modal-title">Confirmar Cadastro de Siglas</div>
        <div class="modal-info">
            <div class="modal-info-item">
                <span class="modal-info-label">Data:</span>
                <span class="modal-info-value" id="modalData"></span>
            </div>
            <div class="modal-info-item">
                <span class="modal-info-label">Dia:</span>
                <span class="modal-info-value" id="modalDia"></span>
            </div>
            <div class="modal-info-item">
                <span class="modal-info-label">Siglas:</span>
                <span class="modal-info-value" id="modalSiglas"></span>
            </div>
        </div>
        <div id="modalEditSection" class="modal-edit-section" style="display: none;">
            <h5>📝 Editar Siglas:</h5>
            <textarea id="modalEditInput" class="modal-edit-input" rows="4" placeholder="Digite as siglas separadas por vírgula..."></textarea>
        </div>
        <div class="modal-buttons">
            <button id="modalBtnCancel" class="modal-btn modal-btn-cancel">❌ Cancelar</button>
            <button id="modalBtnEdit" class="modal-btn modal-btn-edit">✏️ Editar</button>
            <button id="modalBtnConfirm" class="modal-btn modal-btn-confirm">✅ Confirmar</button>
        </div>
    </div>
</div>
```

#### **3.2 Estados do Modal**
- **Visualizar:** Mostra siglas originais
- **Editar:** Permite modificar siglas antes de confirmar
- **Confirmar:** Processa o cadastro

### **4. Backend - Endpoint Principal**

#### **4.1 Endpoint**
```python
POST /api/edicoes/cadastrar-siglas
```

#### **4.2 Payload**
```json
{
    "data_sorteio": "2025-01-20",
    "siglas": "PT_1, PT_2, FEDERAL"
}
```

#### **4.3 Validações Backend**

##### **4.3.1 Formato de Data**
```python
try:
    data_obj = datetime.strptime(dados.data_sorteio, '%Y-%m-%d')
except ValueError:
    raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
```

##### **4.3.2 Cálculo do Dia da Semana**
```python
dias_mapping = {
    0: 'segunda-feira', 1: 'terça-feira', 2: 'quarta-feira',
    3: 'quinta-feira', 4: 'sexta-feira', 5: 'sábado', 6: 'domingo'
}
dia_semana_idx = data_obj.weekday()
dia_semana_str = dias_mapping[dia_semana_idx]
```

##### **4.3.3 Validação de Siglas**
```python
if not dados.siglas or not dados.siglas.strip():
    raise HTTPException(status_code=400, detail="Siglas não podem estar vazias")

siglas_list = [s.strip() for s in dados.siglas.split(',') if s.strip()]
if not siglas_list:
    raise HTTPException(status_code=400, detail="Nenhuma sigla válida encontrada")
```

##### **4.3.4 Verificação de Duplicidade**
```python
check_query = "SELECT id FROM siglas_diarias WHERE data_sorteio = %s"
cursor.execute(check_query, (dados.data_sorteio,))
existing = cursor.fetchone()

if existing:
    raise HTTPException(status_code=409, detail=f"Já existe registro para a data {dados.data_sorteio}")
```

### **5. Inserção na Tabela `siglas_diarias`**

#### **5.1 Query de Inserção**
```sql
INSERT INTO siglas_diarias (diaSemana, data_sorteio, siglas, tipo)
VALUES (%s, %s, %s, '')
```

#### **5.2 Dados Inseridos**
- `diaSemana`: Dia da semana calculado
- `data_sorteio`: Data fornecida
- `siglas`: Lista de siglas separadas por vírgula
- `tipo`: Vazio (diferente de 'extra' para siglas avulsas)

### **6. Alimentação Automática da `extracoes_cadastro`**

#### **6.1 Busca da Próxima Edição**
```python
cursor2.execute("SELECT MAX(edicao) FROM extracoes_cadastro")
max_edicao = cursor2.fetchone()[0] or 0
proxima_edicao = max_edicao + 1
edicao_atual = proxima_edicao
```

#### **6.2 Processamento de Cada Sigla**
```python
for sigla in siglas_list:
    if 'GRUPO' in sigla.upper():
        continue  # Ignorar grupos
    
    sigla_oficial = sigla.split('_')[0] if '_' in sigla else sigla
    extracao = sigla
    data_sorteio = dados.data_sorteio
```

#### **6.3 Geração de Links**
```python
base_url = 'https://litoraldasorte.com/campanha/'
if sigla_oficial.upper() in ['FEDERAL', 'FEDERAL ESPECIAL']:
    titulo = f"{sigla_oficial.upper()} EDIÇÃO {edicao_atual}"
else:
    titulo = f"{sigla_oficial.upper()} RJ EDIÇÃO {edicao_atual}"
slug = titulo.lower().replace(' ', '-').replace('edição', 'edicao')
link = base_url + slug
```

#### **6.4 Busca de Dados da Premiação**
```python
cursor2.execute("SELECT * FROM premiacoes WHERE sigla = %s LIMIT 1", (sigla,))
premiacao = cursor2.fetchone()
if not premiacao:
    raise HTTPException(status_code=400, detail=f"Sigla '{sigla}' não encontrada na tabela premiacoes")
```

#### **6.5 Inserção na `extracoes_cadastro`**
```python
insert_cols = [
    'data_sorteio', 'edicao', 'sigla_oficial', 'extracao', 'link',
    'status_cadastro', 'status_link', 'error_msg',
    'horario', 'precocota', 'primeiro', 'segundo', 'terceiro', 'quarto', 'quinto',
    'sexto', 'setimo', 'oitavo', 'nono', 'decimo',
    'decimo_primeiro', 'decimo_segundo', 'decimo_terceiro', 'decimo_quarto',
    'numeracao', 'totalpremios', 'totalpremios_oficial', 'totalpremiacao',
    'premiosextras', 'arrecad', 'lucro', 'id_siglas_diarias'
]

insert_values = [
    data_sorteio, edicao_atual, sigla_oficial, extracao, link,
    'pendente', 'pendente', '',
    premiacao[2], premiacao[3], premiacao[4], premiacao[5], premiacao[6], premiacao[7], premiacao[8],
    premiacao[9], premiacao[10], premiacao[11], premiacao[12], premiacao[13],
    premiacao[14], premiacao[15], premiacao[16], premiacao[17],
    premiacao[18], premiacao[19], premiacao[20], premiacao[21],
    premiacao[22], premiacao[23], premiacao[24], cursor.lastrowid
]
```

#### **6.6 Verificação de Duplicidade**
```python
cursor2.execute("SELECT COUNT(*) FROM extracoes_cadastro WHERE sigla_oficial=%s AND data_sorteio=%s AND edicao=%s", (sigla_oficial, data_sorteio, edicao_atual))
if cursor2.fetchone()[0] == 0:
    # Só insere se não existir
    insert_sql = f"INSERT INTO extracoes_cadastro ({', '.join(insert_cols)}) VALUES ({', '.join(['%s']*len(insert_cols))})"
    cursor2.execute(insert_sql, insert_values)
    connection2.commit()
```

### **7. Resposta de Sucesso**

#### **7.1 Estrutura da Resposta**
```json
{
    "success": true,
    "message": "Siglas cadastradas com sucesso para 2025-01-20",
    "data": {
        "id": 123,
        "data_sorteio": "2025-01-20",
        "dia_semana": "segunda-feira",
        "siglas": ["PT_1", "PT_2", "FEDERAL"],
        "siglas_str": "PT_1, PT_2, FEDERAL"
    }
}
```

### **8. Atualização do Frontend**

#### **8.1 Recarregamento da Tabela**
```javascript
await carregarEdicoes();
```

#### **8.2 Limpeza do Formulário**
```javascript
document.getElementById('siglasDropdown').value = "";
```

#### **8.3 Fechamento do Modal**
```javascript
fecharModal();
```

## Regras de Negócio

### **1. Grupos de Dias da Semana**
- **Grupo 1:** Segunda, terça, quinta, sexta
- **Grupo 2:** Quarta, sábado
- **Grupo 3:** Domingo

### **2. Geração de Links**
- **FEDERAL/FEDERAL ESPECIAL:** `{SIGLA} EDIÇÃO {NUMERO}`
- **Demais siglas:** `{SIGLA} RJ EDIÇÃO {NUMERO}`
- **Base URL:** `https://litoraldasorte.com/campanha/`
- **Slug:** Título em minúsculo, espaços por hífens, "edição" → "edicao"

### **3. Status Inicial**
- **status_cadastro:** `'pendente'`
- **status_link:** `'pendente'`
- **error_msg:** `''`

### **4. Validações**
- ✅ Data única por registro
- ✅ Siglas devem existir na tabela `premiacoes`
- ✅ Formato de data: YYYY-MM-DD
- ✅ Pelo menos uma sigla válida
- ✅ Ignorar siglas com 'GRUPO' no nome

## Tratamento de Erros

### **1. Erros Frontend**
- Data não selecionada
- Siglas não selecionadas
- Erro de parsing JSON
- Erro de conexão

### **2. Erros Backend**
- Formato de data inválido
- Siglas vazias
- Data duplicada
- Sigla não encontrada em `premiacoes`
- Erro de banco de dados

### **3. Mensagens de Erro**
```javascript
const errorMessage = resultado.detail || resultado.message || 'Erro desconhecido';
alert(`❌ Erro ao cadastrar siglas:\n${errorMessage}`);
```

## Diferenças para "Cadastrar Sigla Avulsa"

### **1. Fonte dos Dados**
- **Cadastrar Siglas:** Dropdown com siglas do grupo
- **Sigla Avulsa:** Dropdown com todas as premiações

### **2. Campo Tipo**
- **Cadastrar Siglas:** `tipo = ''` (vazio)
- **Sigla Avulsa:** `tipo = 'extra'` (forçado)

### **3. Validações**
- **Cadastrar Siglas:** Múltiplas siglas, verifica duplicidade por data
- **Sigla Avulsa:** Uma sigla, permite múltiplos registros por data

### **4. Modal**
- **Cadastrar Siglas:** Modal completo com edição
- **Sigla Avulsa:** Confirmação simples (confirm)

## 🔗 Nova Funcionalidade: Campo id_siglas_diarias

### **Atualização 12-06-25**
- **Campo adicionado**: `id_siglas_diarias` na tabela `extracoes_cadastro`
- **Propósito**: Vincular edições ao registro original em `siglas_diarias`
- **Rastreabilidade**: Identificar origem de cada edição

### **Como Funciona no Botão "Cadastrar Siglas"**

#### **1. Captura do ID**
```python
# Após inserir na tabela siglas_diarias
registro_id = cursor.lastrowid  # ID do registro recém-criado
```

#### **2. Inclusão na extracoes_cadastro**
```python
insert_cols = [
    'data_sorteio', 'edicao', 'sigla_oficial', 'extracao', 'link',
    'status_cadastro', 'status_link', 'error_msg',
    'horario', 'precocota', 'primeiro', 'segundo', 'terceiro', 'quarto', 'quinto',
    'sexto', 'setimo', 'oitavo', 'nono', 'decimo',
    'decimo_primeiro', 'decimo_segundo', 'decimo_terceiro', 'decimo_quarto',
    'numeracao', 'totalpremios', 'totalpremios_oficial', 'totalpremiacao',
    'premiosextras', 'arrecad', 'lucro', 'id_siglas_diarias'
]

insert_values = [
    data_sorteio, edicao_atual, sigla_oficial, extracao, link,
    'pendente', 'pendente', '',
    premiacao[2], premiacao[3], premiacao[4], premiacao[5], premiacao[6], premiacao[7], premiacao[8],
    premiacao[9], premiacao[10], premiacao[11], premiacao[12], premiacao[13],
    premiacao[14], premiacao[15], premiacao[16], premiacao[17],
    premiacao[18], premiacao[19], premiacao[20], premiacao[21],
    premiacao[22], premiacao[23], premiacao[24], registro_id
]
```

### **Vantagens da Implementação**

#### **1. Rastreabilidade Completa**
- Cada edição está vinculada ao registro original
- Permite identificar qual cadastro de siglas originou cada edição

#### **2. Consultas Relacionadas**
```sql
-- Buscar todas as edições de um cadastro específico
SELECT 
    ec.edicao,
    ec.sigla_oficial,
    ec.status_cadastro,
    sd.siglas as siglas_originais,
    sd.data_sorteio
FROM extracoes_cadastro ec
INNER JOIN siglas_diarias sd ON ec.id_siglas_diarias = sd.id
WHERE sd.id = 123;
```

#### **3. Diferenciação de Origem**
- **Com `id_siglas_diarias`**: Criado via "Cadastrar Siglas" ou "Cadastrar Sigla Avulsa"
- **Com `id_siglas_diarias = NULL`**: Criado via "Executar Script"

#### **4. Auditoria e Relatórios**
- Rastrear origem de cada edição
- Gerar relatórios de produtividade
- Identificar padrões de uso

### **Impacto no Fluxo Existente**
- ✅ **Sem quebra**: Funcionalidades existentes continuam funcionando
- ✅ **Retrocompatibilidade**: Registros antigos mantêm `id_siglas_diarias = NULL`
- ✅ **Transparente**: Usuário não percebe mudança na interface
- ✅ **Benéfico**: Melhora rastreabilidade e auditoria

### **Exemplo de Uso**
```sql
-- Relatório de edições por cadastro
SELECT 
    sd.id as cadastro_id,
    sd.data_sorteio,
    sd.siglas as siglas_cadastradas,
    COUNT(ec.id) as total_edicoes,
    SUM(CASE WHEN ec.status_cadastro = 'cadastrado' THEN 1 ELSE 0 END) as edicoes_processadas
FROM siglas_diarias sd
LEFT JOIN extracoes_cadastro ec ON sd.id = ec.id_siglas_diarias
GROUP BY sd.id, sd.data_sorteio, sd.siglas
ORDER BY sd.data_sorteio DESC;
```

## Arquivos Relacionados

### **Frontend**
- `static/edicoes.html` (linhas 1000-1200)

### **Backend**
- `app/main.py` (linhas 473-600)

### **Banco de Dados**
- Tabela `siglas_diarias`
- Tabela `extracoes_cadastro`
- Tabela `premiacoes`

## Logs e Debug

### **1. Console do Navegador**
```javascript
console.log('Dados para cadastro:', dados);
console.log('Siglas cadastradas com sucesso:', resultado);
```

### **2. Logs do Backend**
- Validações de dados
- Erros de banco
- Processamento de siglas

## Testes Recomendados

### **1. Cenários de Sucesso**
- Cadastro com uma sigla
- Cadastro com múltiplas siglas
- Cadastro com sigla FEDERAL
- Cadastro com sigla comum

### **2. Cenários de Erro**
- Data duplicada
- Sigla inexistente
- Data inválida
- Siglas vazias

### **3. Cenários de Interface**
- Modal de edição
- Validações frontend
- Loading states
- Recarregamento da tabela

## Gerenciamento e Exclusão de Siglas

- Após cadastrar, é possível excluir registros de siglas diretamente pela tabela "Siglas Cadastradas" (apenas datas vigentes/futuras)
- Basta clicar na linha desejada para abrir a confirmação de exclusão
- A exclusão remove o registro e todos os relacionados em `extracoes_cadastro`
- Exclusão não é permitida para datas passadas

---

**Última Atualização:** Janeiro 2025  
**Versão:** 1.0.0  
**Status:** Implementado e Funcional 