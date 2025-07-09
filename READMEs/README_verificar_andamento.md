# Script de Verificação de Andamento das Rifas

Este script automatiza a verificação do percentual de andamento das rifas através dos links cadastrados na tabela `extracoes_cadastro`.

## 📋 Funcionalidades

- **Verificação Automática**: Visita cada link cadastrado e extrai o percentual de andamento
- **Múltiplas Estratégias**: Usa XPath fornecido + seletores alternativos para maior confiabilidade
- **Atualização Inteligente**: Só atualiza o banco quando o percentual realmente mudou
- **Logs Detalhados**: Registra todo o processo para acompanhamento e debug
- **Execução Segura**: Headless browser com timeouts e tratamento de erros

## 🗄️ Estrutura do Banco

### Coluna `andamento` na tabela `extracoes_cadastro`

```sql
ALTER TABLE extracoes_cadastro 
ADD COLUMN andamento VARCHAR(10) NULL DEFAULT '0%'
COMMENT 'Percentual de andamento da rifa (0% a 100%)';
```

## 📂 Arquivos Criados

### 1. `add_andamento_field.sql`
Script SQL para adicionar a coluna `andamento` na tabela.

### 2. `scripts/verificar_andamento_rifas.py`
Script principal que executa a verificação.

### 3. `test_verificar_andamento.py`
Script de teste para verificar se tudo está configurado corretamente.

## 🚀 Como Usar

### Preparação (Execute uma vez)

1. **Adicionar coluna no banco**:
```sql
-- Execute o conteúdo do arquivo add_andamento_field.sql
ALTER TABLE extracoes_cadastro 
ADD COLUMN andamento VARCHAR(10) NULL DEFAULT '0%';
```

2. **Instalar dependências** (se necessário):
```bash
pip install selenium pymysql
```

3. **Testar configuração**:
```bash
python test_verificar_andamento.py
```

### Execução

#### Via API (Recomendado)
```bash
# POST para o endpoint
curl -X POST http://192.168.10.115:8001/api/scripts/verificar-andamento-rifas
```

#### Via Script Direto
```bash
python scripts/verificar_andamento_rifas.py
```

## 🔍 Como Funciona

### 1. Busca de Links
O script busca todos os registros da tabela `extracoes_cadastro` que possuem:
- `link` não nulo e não vazio
- `link` que comece com `https://litoraldasorte.com`

### 2. Extração do Percentual
Para cada link, o script:

1. **XPath Principal**: Tenta usar o XPath fornecido:
   ```
   //*[@id="root"]/div/div[1]/div[2]/div[3]/form/div[1]/div[1]/div/div
   ```

2. **Seletores Alternativos**: Se o XPath falhar, tenta:
   ```css
   div[class*='progress']
   div[class*='percent']
   span[class*='progress']
   .progress-bar
   .percentage
   ```

3. **Busca no Body**: Como último recurso, procura por padrões `\d+%` em todo o HTML

### 3. Validação e Atualização
- Extrai percentuais entre 0% e 100%
- Só atualiza o banco se o valor mudou
- Registra logs detalhados de cada operação

## 📊 Logs e Monitoramento

### Arquivo de Log
```
scripts/logs/verificar_andamento.log
```

### Informações Registradas
- Links acessados
- Percentuais encontrados
- Atualizações realizadas
- Erros e exceções
- Resumo final com estatísticas

### Exemplo de Log
```
2025-01-20 10:30:15 - INFO - === INICIANDO VERIFICAÇÃO DE ANDAMENTO DAS RIFAS ===
2025-01-20 10:30:16 - INFO - Encontrados 25 links para verificar
2025-01-20 10:30:17 - INFO - --- Processando 1/25 ---
2025-01-20 10:30:17 - INFO - Edição: 1234
2025-01-20 10:30:17 - INFO - Sigla: PT
2025-01-20 10:30:17 - INFO - Andamento atual: 0%
2025-01-20 10:30:18 - INFO - Acessando link: https://litoraldasorte.com/...
2025-01-20 10:30:22 - INFO - Texto encontrado no elemento: 45%
2025-01-20 10:30:22 - INFO - Percentual extraído: 45%
2025-01-20 10:30:23 - INFO - ✅ Andamento atualizado: 0% → 45%
```

## ⚙️ Configurações

### Timeouts
- **Página**: 15 segundos para encontrar elementos
- **Script Total**: 30 minutos (1800 segundos)
- **Entre Requests**: 2 segundos para não sobrecarregar o servidor

### Chrome Options
```python
chrome_options.add_argument('--headless')  # Sem interface gráfica
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
```

## 🔧 Solução de Problemas

### Erro: "Coluna andamento não encontrada"
```bash
# Execute o script SQL primeiro
mysql -u root -p gerenciamento_rifas < add_andamento_field.sql
```

### Erro: "ChromeDriver não encontrado"
```bash
# Instalar ChromeDriver
# Windows: Baixar de https://chromedriver.chromium.org/
# Linux: sudo apt-get install chromium-chromedriver
```

### Erro: "Timeout na execução"
- Verifique a conexão com a internet
- Alguns sites podem estar lentos
- O script continua de onde parou na próxima execução

### Erro: "Elemento não encontrado"
- O site pode ter mudado a estrutura
- O script tenta múltiplas estratégias automaticamente
- Verifique os logs para detalhes

## 📈 Integração com Dashboard

O script pode ser integrado ao sistema existente:

### Endpoint da API
```
POST /api/scripts/verificar-andamento-rifas
```

### Resposta
```json
{
  "success": true,
  "message": "Script de verificação de andamento executado com sucesso",
  "data": {
    "total_processado": 25,
    "sucessos": 23,
    "erros": 2,
    "output": "..."
  }
}
```

### Adição ao Frontend
Pode ser adicionado um botão na página de edições:
```html
<button onclick="verificarAndamento()">🔍 Verificar Andamento</button>
```

## 🔐 Segurança

- **Headless**: Executa sem interface gráfica
- **Rate Limiting**: Pausa entre requisições
- **Timeout**: Evita travamentos
- **Logs**: Registra todas as ações para auditoria
- **Validação**: Só aceita percentuais válidos (0-100%)

## 📋 Próximos Passos

1. **Executar o script SQL** para adicionar a coluna
2. **Testar com alguns links** usando o script de teste
3. **Executar o script completo** via API ou diretamente
4. **Monitorar os logs** para verificar o funcionamento
5. **Integrar ao frontend** se necessário

O script está pronto para uso e pode ser executado quantas vezes for necessário para manter os percentuais atualizados! 