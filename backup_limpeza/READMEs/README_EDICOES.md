# Módulo de Edições - Sistema de Gerenciamento

> 📖 **Documentação Principal**: [README.md](README.md) - Visão geral completa do sistema

## Visão Geral

O módulo de edições gerencia o cadastro e execução de scripts para sorteios diários. Permite cadastrar siglas por data, executar scripts de automação e controlar o status de processamento através da tabela `extracoes_cadastro`.

## Estrutura de Dados

### Tabela `siglas_diarias`
Armazena as siglas cadastradas por data:
- `id`: Chave primária
- `diaSemana`: Dia da semana (segunda-feira, terça-feira, etc.)
- `data_sorteio`: Data do sorteio (YYYY-MM-DD)
- `siglas`: Lista de siglas separadas por vírgula
- `tipo`: Tipo do registro (vazio para normais, 'extra' para avulsas)

### Tabela `extracoes_cadastro`
Controla o status de processamento de cada sigla:
- `data_sorteio`: Data do sorteio
- `edicao`: Número da edição
- `sigla_oficial`: Sigla principal
- `extracao`: Sigla completa
- `status_cadastro`: Status do cadastro ('pendente', 'cadastrado', 'erro')
- `status_link`: Status do link ('pendente', 'gerado', 'erro')
- `link`: URL gerada para o sorteio

## Endpoints da API

### GET `/api/edicoes`
**Descrição:** Lista edições dos últimos 14 dias com verificação de pendências

**Resposta:**
```json
[
  {
    "diaSemana": "segunda-feira",
    "data_sorteio": "2025-01-20",
    "siglas": "PT_1, PT_2, FEDERAL",
    "tem_pendencias": true
  }
]
```

**Lógica:**
- Busca registros da tabela `siglas_diarias` dos últimos 14 dias
- Para cada edição, verifica se há registros pendentes em `extracoes_cadastro`
- Adiciona campo `tem_pendencias` baseado em `status_cadastro != 'cadastrado'`

### GET `/api/edicoes/ultima-data`
**Descrição:** Retorna a próxima data disponível para cadastro

**Resposta:**
```json
{
  "proxima_data": "2025-01-21"
}
```

**Lógica:**
- Busca a última data cadastrada em `siglas_diarias`
- Retorna a data seguinte (última + 1 dia)
- Se não há registros, retorna data atual

### GET `/api/edicoes/siglas-por-grupo/{data}`
**Descrição:** Retorna siglas dos últimos 3 registros do mesmo grupo da data

**Parâmetros:**
- `data`: Data no formato YYYY-MM-DD

**Resposta:**
```json
{
  "grupo": 1,
  "data_selecionada": "2025-01-20",
  "siglas": [
    {
      "diaSemana": "segunda-feira",
      "data_sorteio": "2025-01-13",
      "siglas": "PT_1, PT_2"
    }
  ]
}
```

**Lógica de Grupos:**
- **Grupo 1:** Segunda, terça, quinta, sexta
- **Grupo 2:** Quarta, sábado  
- **Grupo 3:** Domingo

### POST `/api/edicoes/cadastrar-siglas`
**Descrição:** Cadastra novas siglas para uma data

**Corpo da requisição:**
```json
{
  "data_sorteio": "2025-01-20",
  "siglas": "PT_1, PT_2, FEDERAL"
}
```

**Resposta:**
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

**Fluxo de Processamento:**
1. Valida formato da data e siglas
2. Verifica se já existe registro para a data
3. Insere na tabela `siglas_diarias`
4. **Alimenta automaticamente `extracoes_cadastro`:**
   - Busca maior edição existente
   - Para cada sigla (exceto 'GRUPO'):
     - Gera link baseado na sigla e edição
     - Busca dados da premiação na tabela `premiacoes`
     - Insere registro com `status_cadastro = 'pendente'`

### POST `/api/edicoes/cadastrar-sigla-avulsa`
**Descrição:** Cadastra uma sigla avulsa (tipo='extra')

**Corpo da requisição:**
```json
{
  "data_sorteio": "2025-01-20",
  "dia_semana": "segunda-feira",
  "siglas": "PT_ESPECIAL"
}
```

**Lógica:**
- Sempre define `tipo = 'extra'`
- Permite múltiplos registros para a mesma data
- Alimenta `extracoes_cadastro` igual ao cadastro normal

### POST `/api/edicoes/executar-script`
**Descrição:** Executa o script `cadRifas_litoral_v3`

**Corpo da requisição:**
```json
{
  "data_sorteio": "2025-01-20",
  "siglas": "PT_1, PT_2, FEDERAL"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Script executado com sucesso para 20/01/2025",
  "data": {
    "data_sorteio": "2025-01-20",
    "data_formatada": "20/01/2025",
    "siglas": ["PT_1", "PT_2", "FEDERAL"],
    "stdout": "...",
    "stderr": "",
    "returncode": 0
  }
}
```

**Execução do Script:**
- Converte data para formato DD/MM/AAAA
- Executa `scripts/cadRifas_litoral_v3` via subprocess
- Timeout de 5 minutos
- Variáveis de ambiente: `DB_PASSWORD`, `LITORAL_PASSWORD`

## Frontend (edicoes.html)

### Funcionalidades Principais

#### 1. Cadastro de Novas Siglas
- **Seleção de Data:** Input de data com validação
- **Dia da Semana:** Calculado automaticamente
- **Dropdown de Siglas:** Carrega últimas 3 siglas do mesmo grupo
- **Botão Cadastrar:** Abre modal de confirmação

#### 2. Cadastro de Sigla Avulsa
- **Seleção de Premiação:** Dropdown com todas as premiações
- **Cadastro Direto:** Sem modal, confirmação simples
- **Tipo Automático:** Sempre define como 'extra'

#### 3. Tabela de Edições
- **Listagem:** Últimas 14 edições cadastradas
- **Colunas:** Dia da semana, data, siglas, ações
- **Botão Executar Script:** Só aparece se há pendências

### Lógica de Exibição do Botão "Executar Script"

**Antes (baseado em data):**
```javascript
const mostrarBotao = dataSorteio.getTime() >= hoje.getTime();
```

**Agora (baseado em pendências):**
```javascript
const temPendencias = edicao.tem_pendencias === true;
```

**Critérios:**
- ✅ **Mostra botão:** `tem_pendencias === true`
- ❌ **Não mostra:** `tem_pendencias === false` (exibe "Sem pendências")

### Modais

#### Modal de Confirmação de Cadastro
- **Informações:** Data, dia, siglas
- **Edição:** Permite editar siglas antes de confirmar
- **Estados:** Visualizar ↔ Editar

#### Modal de Confirmação do Script
- **Aviso:** Explica o que o script fará
- **Informações:** Data, dia, siglas
- **Confirmação:** Execução irreversível

### JavaScript Principal

#### Função `carregarEdicoes()`
- Faz requisição para `/api/edicoes`
- Preenche tabela dinamicamente
- Controla exibição do botão baseado em `tem_pendencias`

#### Função `atualizarDiaSemanaEGrupo()`
- Calcula dia da semana baseado na data
- Determina grupo (1, 2 ou 3)
- Carrega siglas do grupo via `/api/edicoes/siglas-por-grupo/{data}`

#### Função `processarConfirmacao()`
- Valida siglas (originais ou editadas)
- Envia para `/api/edicoes/cadastrar-siglas`
- Recarrega tabela após sucesso

#### Função `executarScriptConfirmado()`
- Envia dados para `/api/edicoes/executar-script`
- Mostra loading durante execução
- Exibe resultado (sucesso/erro)

## Fluxo Completo

### 1. Cadastro de Siglas
```
Usuário seleciona data → Sistema calcula grupo → Carrega siglas similares → 
Usuário confirma → Backend cadastra em siglas_diarias → 
Backend alimenta extracoes_cadastro com status='pendente' → 
Frontend recarrega tabela
```

### 2. Execução do Script
```
Usuário clica "Executar Script" → Modal de confirmação → 
Backend executa cadRifas_litoral_v3 → Script processa registros pendentes → 
Script atualiza status_cadastro='cadastrado' → Frontend recarrega tabela
```

### 3. Controle de Pendências
```
Backend consulta siglas_diarias → Para cada data, verifica extracoes_cadastro → 
Conta registros com status_cadastro != 'cadastrado' → 
Retorna tem_pendencias: true/false → Frontend exibe/oculta botão
```

## Regras de Negócio

### Validações
- **Data única:** Não permite cadastro duplo para mesma data
- **Siglas obrigatórias:** Pelo menos uma sigla deve ser informada
- **Formato de data:** YYYY-MM-DD obrigatório
- **Premiação existente:** Sigla deve existir na tabela `premiacoes`

### Grupos de Dias
- **Grupo 1:** Segunda, terça, quinta, sexta
- **Grupo 2:** Quarta, sábado
- **Grupo 3:** Domingo

### Status de Processamento
- **pendente:** Registro criado, aguardando execução do script
- **cadastrado:** Script executado com sucesso
- **erro:** Falha na execução do script

### Links Gerados
- **Formato:** `https://litoraldasorte.com/{titulo-slug}`
- **FEDERAL:** `{SIGLA} EDIÇÃO {NUMERO}`
- **Outras:** `{SIGLA} RJ EDIÇÃO {NUMERO}`
- **Slug:** Título em minúsculo, espaços por hífens

## Arquivos Relacionados

- **Backend:** `app/main.py` (endpoints 140-827)
- **Frontend:** `static/edicoes.html` (linhas 1-1333)
- **Script:** `scripts/cadRifas_litoral_v3`
- **CSS:** `static/css/index.css`

## Dependências

- **Backend:** FastAPI, PyMySQL, uvicorn
- **Frontend:** JavaScript vanilla, CSS customizado
- **Banco:** MySQL com tabelas `siglas_diarias`, `extracoes_cadastro`, `premiacoes`

## Troubleshooting

### Botão não aparece
- Verificar se há registros em `extracoes_cadastro` com `status_cadastro != 'cadastrado'`
- Verificar se a data está nos últimos 14 dias

### Erro no cadastro
- Verificar se já existe registro para a data
- Verificar se as siglas existem na tabela `premiacoes`

### Script não executa
- Verificar se o arquivo `scripts/cadRifas_litoral_v3` existe
- Verificar variáveis de ambiente `DB_PASSWORD`, `LITORAL_PASSWORD`
- Verificar timeout (5 minutos)

## Funcionalidade de Exclusão de Siglas

### Como funciona
- **Onde:** Tabela "Siglas Cadastradas" na página de edições
- **Quem pode ser excluído:** Apenas registros com data vigente (hoje) ou futura
- **Como excluir:** Clique em qualquer linha da tabela (não há ícone ou botão extra, mantém o visual limpo)
- **Confirmação:** Ao clicar, aparece uma mensagem de confirmação detalhada, informando a data, siglas e o impacto da exclusão
- **O que é excluído:** O registro em `siglas_diarias` e todos os registros relacionados em `extracoes_cadastro` (mesmo `id_siglas_diarias`)
- **Proteção:** Não é possível excluir registros de datas passadas
- **Feedback:** Após exclusão, logs informam sucesso e quantidade de registros relacionados excluídos

### Fluxo resumido
1. Usuário clica em uma linha de siglas cadastradas (vigente/futura)
2. Modal de confirmação é exibido
3. Usuário confirma
4. Backend exclui o registro e todos os relacionados
5. Tabela é recarregada automaticamente

### Visual
- Nenhuma alteração visual na tabela (sem ícones, sublinhados ou botões extras)
- Linha fica levemente destacada ao passar o mouse (hover)
- Cursor pointer indica que é clicável

### Regras de negócio
- Exclusão só permitida para datas >= hoje
- Exclusão é definitiva (não pode ser desfeita)
- Exclusão em cascata garante integridade dos dados 