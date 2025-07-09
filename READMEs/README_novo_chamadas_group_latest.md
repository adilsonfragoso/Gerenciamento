# 📱 Script de Envio de Links para WhatsApp - novo_chamadas_group_latest.py

> 📖 **Documentação Principal**: [../README.md](../README.md) - Visão geral completa do sistema

## 📋 Descrição Geral

O script `novo_chamadas_group_latest.py` é responsável por enviar mensagens para grupos de WhatsApp com links de sorteios e suas respectivas imagens. Ele busca dados diretamente da tabela `extracoes_cadastro` e utiliza a pasta `uploads` para as imagens.

## 🎯 Funcionalidades Principais

### 1. **Duas Lógicas de Envio**

#### **Primeira Prioridade - Links Pendentes**
- Busca registros com `status_envio_link = 'pendente'`
- Atualiza status para `'enviado'` após envio bem-sucedido
- Execução: `python scripts/novo_chamadas_group_latest.py`

#### **Segunda Prioridade - Edições Específicas**
- Busca por edição(s) específica(s) no campo `edicao`
- Envia independente do status atual
- **NÃO altera** o status após envio
- Aceita múltiplas edições simultaneamente

### 2. **Fonte de Dados**
- **Links**: Campo `link` da tabela `extracoes_cadastro`
- **Imagens**: Campo `extracao` para identificar imagem na pasta `uploads`
- **Informações**: Campos `edicao` e `sigla_oficial` para logs

## 🚀 Como Usar

### **Enviar Links Pendentes**
```bash
python scripts/novo_chamadas_group_latest.py
```

### **Enviar 1 Edição Específica**
```bash
python scripts/novo_chamadas_group_latest.py 6143
```

### **Enviar Múltiplas Edições**
```bash
python scripts/novo_chamadas_group_latest.py 6143 6144 6145
```

### **Enviar Várias Edições de Uma Vez**
```bash
python scripts/novo_chamadas_group_latest.py 6143 6144 6145 6146 6147
```

## ⚙️ Configurações

### **Banco de Dados**
```python
DB_CONFIG = {
    'host': 'pma.megatrends.site',
    'user': 'root',
    'password': 'Define@4536#8521',
    'database': 'litoral'
}
```

### **Pasta de Imagens**
```python
caminho_imagens = r"D:\Documentos\Workspace\Gerenciamento\uploads"
```

### **Grupos WhatsApp**
```python
#id_grupo = "120363307707983386@g.us"  # grupo links
id_grupo = "5512997650505-1562805682@g.us"  # grupo anotações
```

### **API WhatsApp**
```python
api_key = "k9J3mB7pQ2rT6vL1dS8nF4cW5aX0yZ2u"
url = "https://evolution-evolution.aras94.easypanel.host/message/sendMedia/bancada"
```

## 📊 Estrutura da Mensagem

### **Texto da Mensagem**
```
🔥VENDAS ABERTAS🔥

LINK PARA PARTICIPAR
👇👇👇👇👇👇👇👇👇
[LINK_DO_SORTEIO]

DESEJAMOS A TODOS UMA BOA SORTE 🍀🤞🏻
```

### **Formato da Mensagem**
- **Tipo**: Imagem com legenda
- **Mídia**: Imagem da extração (JPG/JPEG)
- **Legenda**: Texto formatado com link
- **Formato**: Base64

## 🔍 Busca de Imagens

### **Lógica de Busca**
1. Procura por arquivo `[extracao].jpg`
2. Se não encontrar, procura por `[extracao].jpeg`
3. Retorna caminho completo se encontrado
4. Retorna `None` se não encontrado

### **Exemplo**
- Campo `extracao` = "PT"
- Busca: `uploads/PT.jpg` ou `uploads/PT.jpeg`

## 📝 Logs e Feedback

### **Logs de Sucesso**
```
Modo: Enviar 3 edição(ões) específica(s): 6143, 6144, 6145

Enviando edição 6143 - Sigla: PTM
Mensagem enviada com sucesso - Edição: 6143, Sigla: PTM, Link: https://...
✅ Edição 6143 enviada com sucesso!

✅ Total de mensagens enviadas: 3
```

### **Logs de Erro**
```
❌ Edição 6143 não encontrada na tabela extracoes_cadastro
ERRO: Imagem PT não encontrada no diretório uploads
Falha ao enviar mensagem para edição 6143. Status Code: 400
```

## 🔄 Fluxo de Execução

### **Modo Links Pendentes**
1. Conecta ao banco de dados
2. Busca registros com `status_envio_link = 'pendente'`
3. Para cada registro:
   - Busca imagem na pasta `uploads`
   - Monta mensagem com link
   - Envia para WhatsApp
   - Atualiza status para `'enviado'`
   - Aguarda 3 segundos
4. Exibe total de mensagens enviadas

### **Modo Edições Específicas**
1. Valida argumentos de linha de comando
2. Para cada edição informada:
   - Busca registro no banco
   - Busca imagem na pasta `uploads`
   - Monta mensagem com link
   - Envia para WhatsApp
   - **NÃO atualiza status**
   - Aguarda 3 segundos
3. Exibe total de mensagens enviadas

## 🛡️ Tratamento de Erros

### **Validação de Argumentos**
- Verifica se argumentos são números válidos
- Rejeita argumentos inválidos com mensagem de erro
- Continua processamento mesmo se uma edição falhar

### **Tratamento de Imagens**
- Verifica existência da imagem antes do envio
- Exibe erro específico se imagem não encontrada
- Continua com próximas edições

### **Tratamento de Banco**
- Tratamento de erros de conexão
- Rollback automático em caso de falha
- Logs detalhados de erros

## 📈 Exemplo de Uso Completo

### **Cenário 1: Enviar Links Pendentes**
```bash
$ python scripts/novo_chamadas_group_latest.py
Modo: Enviar links pendentes
Encontrados 6 links pendentes para enviar.

Processando edição 6142 - Sigla: PPT
Mensagem enviada com sucesso - Edição: 6142, Sigla: PPT, Link: https://...
Status de envio atualizado para edição 6142

✅ Total de mensagens enviadas: 6
```

### **Cenário 2: Enviar Edições Específicas**
```bash
$ python scripts/novo_chamadas_group_latest.py 6143 6144 6145
Modo: Enviar 3 edição(ões) específica(s): 6143, 6144, 6145

Enviando edição 6143 - Sigla: PTM
Mensagem enviada com sucesso - Edição: 6143, Sigla: PTM, Link: https://...
✅ Edição 6143 enviada com sucesso!

Enviando edição 6144 - Sigla: PT
Mensagem enviada com sucesso - Edição: 6144, Sigla: PT, Link: https://...
✅ Edição 6144 enviada com sucesso!

Enviando edição 6145 - Sigla: PTV
Mensagem enviada com sucesso - Edição: 6145, Sigla: PTV, Link: https://...
✅ Edição 6145 enviada com sucesso!

✅ Total de mensagens enviadas: 3
```

## 🔧 Dependências

### **Bibliotecas Python**
- `os` - Manipulação de arquivos e pastas
- `requests` - Requisições HTTP para API WhatsApp
- `base64` - Codificação de imagens
- `time` - Controle de tempo entre envios
- `sys` - Argumentos de linha de comando
- `mysql.connector` - Conexão com banco MySQL

### **Arquivos Necessários**
- Pasta `uploads/` com imagens das extrações
- Conexão com banco MySQL
- Acesso à API WhatsApp Evolution

## 📋 Próximos Passos Planejados

### **Integração com Frontend**
- [ ] Adicionar comando para executar `novo_verificalinks.py`
- [ ] Adicionar comando para executar `novo_chamadas_group_latest.py`
- [ ] Campo input para definir edições específicas
- [ ] Interface para seleção de modo (pendentes vs. específicas)

### **Automação do Processo Diário**
- [ ] Função para executar sequência completa:
  1. Cadastrar Siglas
  2. Executar Script
  3. Verificar Links
  4. Enviar para WhatsApp
- [ ] Interface unificada para todo o processo
- [ ] Logs consolidados do processo completo

## 🎯 Análise de Escalabilidade

O script está bem estruturado para escalabilidade:

### **Pontos Fortes**
- ✅ Separação clara entre modos de operação
- ✅ Aceita múltiplas edições simultaneamente
- ✅ Tratamento robusto de erros
- ✅ Logs detalhados para debugging
- ✅ Pausa entre envios para evitar rate limiting

### **Possíveis Melhorias**
- 🔄 Sistema de retry para mensagens que falharem
- 🔄 Modo de teste que simule envio sem enviar
- 🔄 Configuração via arquivo de configuração
- 🔄 Logs estruturados em arquivo
- 🔄 Métricas de performance e sucesso

---

**Última Atualização**: Dezembro 2024  
**Versão**: 2.0 (Suporte a múltiplas edições)  
**Autor**: Sistema de Gerenciamento de Sorteios 