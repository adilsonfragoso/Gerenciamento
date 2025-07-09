# Script cadRifas_litoral - Histórico de Atualizações

## 09-06-25 cadRifas_litoral_v1
- Baseado no script cadRifas_litoral_emteste
- Solicitado ao ChatGPT a atualização retirando a busca por dados em premiacoes_new2
- Busca as mesmas informações na tabela "premiacoes" do banco de dados

## 09-06-25 cadRifas_litoral_v2
- **Configuração centralizada**: Criado arquivo `config_cadRifas.py` para centralizar todas as configurações
- **Sistema de logs estruturado**: Implementado logging profissional com arquivo de log
- **Migração da pasta de imagens**: Alterado de `D:/Documentos/Workspace/ativos/img_litoraldasorte` para `uploads/` do sistema Gerenciamento
- **Segurança melhorada**: Credenciais podem ser definidas via variáveis de ambiente
- **Sistema de retry**: Implementado retry automático para falhas temporárias
- **Validação de configurações**: Verificação automática de arquivos e pastas necessários
- **Tratamento de erros robusto**: Melhor tratamento de exceções com logs detalhados
- **Timeouts configuráveis**: Timeouts centralizados e ajustáveis
- **Documentação**: Comentários e docstrings melhorados

### Principais Melhorias da v2:
1. **Organização**: Configurações separadas em arquivo próprio
2. **Logs**: Sistema de logging profissional em `scripts/logs/cadRifas.log`
3. **Segurança**: Suporte a variáveis de ambiente para credenciais
4. **Robustez**: Sistema de retry e validações
5. **Manutenibilidade**: Código mais limpo e documentado
6. **Integração**: Usa a pasta `uploads/` do sistema Gerenciamento

### Como usar a v2:
```bash
# Executar diretamente
python scripts/cadRifas_litoral_v2

# Com variáveis de ambiente (recomendado)
set DB_PASSWORD=sua_senha_aqui
set LITORAL_PASSWORD=sua_senha_litoral
python scripts/cadRifas_litoral_v2
```

### Arquivos necessários:
- `scripts/cadRifas_litoral_v2` - Script principal
- `scripts/config_cadRifas.py` - Configurações
- `uploads/` - Pasta com as imagens das siglas
- Arquivos de controle em `D:/Documentos/Workspace/ativos/`

## 09-06-25 cadRifas_litoral_v3
- **Parâmetros via linha de comando**: Siglas e data informados diretamente na execução
- **Consulta última edição no banco**: Busca a maior edição na tabela `extracoes`
- **Remoção de dependências de arquivos .txt**: Não precisa mais de `proximas_siglas.txt` nem `ultima_edicao.txt`
- **Validação de parâmetros**: Validação robusta de siglas e data fornecidos
- **Interface de linha de comando**: Uso de `argparse` para argumentos
- **Flexibilidade total**: Data e siglas definidas a cada execução
- **Modo teste/produção**: Controle para testar sem salvar dados
- **ChromeDriver automático**: Download e gerenciamento automático do driver

### Principais Melhorias da v3:
1. **Independência**: Não depende mais de arquivos .txt externos
2. **Flexibilidade**: Siglas e data definidas a cada execução
3. **Banco de dados**: Consulta última edição diretamente no banco
4. **Validação**: Validação robusta de parâmetros de entrada
5. **Simplicidade**: Interface clara de linha de comando
6. **Confiabilidade**: Dados sempre atualizados do banco
7. **Segurança**: Modo teste para validar automação sem salvar
8. **Automação**: ChromeDriver baixado automaticamente

### Como usar a v3:

#### **Configuração de Modo:**
No início do script, altere a variável:
```python
CRIAR_SORTEIO = False  # True = Salva o sorteio, False = Apenas simula (para testes)
```

#### **Sintaxe básica:**
```bash
python scripts/cadRifas_litoral_v3 --siglas "SIGLA1,SIGLA2,SIGLA3" --data "DD/MM/AAAA"
```

#### **Exemplos práticos:**
```bash
# Exemplo 1: Siglas simples
python scripts/cadRifas_litoral_v3 --siglas "PPT_1,PTM_5,FEDERAL" --data "10/06/2025"

# Exemplo 2: Com GRUPO (apenas gera link)
python scripts/cadRifas_litoral_v3 --siglas "CORUJINHA_3,GRUPO_ESPECIAL" --data "11/06/2025"

# Exemplo 3: Uma sigla apenas
python scripts/cadRifas_litoral_v3 --siglas "PPT_15" --data "12/06/2025"
```

#### **Com variáveis de ambiente (recomendado):**
```bash
set DB_PASSWORD=sua_senha_aqui
set LITORAL_PASSWORD=sua_senha_litoral
python scripts/cadRifas_litoral_v3 --siglas "PPT_1,PTM_5" --data "12/06/2025"
```

### Parâmetros obrigatórios:
- `--siglas`: Siglas separadas por vírgula (ex: "PPT_1,PTM_5,FEDERAL")
- `--data`: Data do sorteio no formato DD/MM/AAAA (ex: "10/06/2025")

### Arquivos necessários:
- `scripts/cadRifas_litoral_v3` - Script principal
- `scripts/config_cadRifas.py` - Configurações
- `uploads/` - Pasta com as imagens das siglas
- Banco de dados com tabelas `premiacoes` e `extracoes`

### Fluxo da v3:
1. **Recebe parâmetros** via linha de comando
2. **Valida siglas e data** fornecidos
3. **Consulta banco** para última edição na tabela `extracoes`
4. **Calcula edições** sequenciais a partir da última
5. **Processa cada sigla** no sistema web
6. **Gera links** e salva no banco (se modo produção)
7. **Logs completos** de todo o processo

### Modo Teste vs Produção:

#### **Modo Teste (`CRIAR_SORTEIO = False`):**
- ✅ **Preenche todo o formulário** automaticamente
- ✅ **Carrega imagens** corretamente
- ✅ **Valida dados** do banco
- ✅ **Gera links** (apenas no arquivo)
- ❌ **NÃO salva** sorteio no sistema
- ❌ **NÃO grava** no banco de dados
- ❌ **NÃO chama** script de afiliados

#### **Modo Produção (`CRIAR_SORTEIO = True`):**
- ✅ **Preenche todo o formulário** automaticamente
- ✅ **Carrega imagens** corretamente
- ✅ **Valida dados** do banco
- ✅ **Salva sorteio** no sistema
- ✅ **Grava no banco** de dados
- ✅ **Gera links** completos
- ✅ **Chama script** de afiliados

### Vantagens da v3:
- ✅ **Sem dependências externas** de arquivos .txt
- ✅ **Dados sempre atualizados** do banco de dados
- ✅ **Flexibilidade total** para siglas e datas
- ✅ **Interface clara** de linha de comando
- ✅ **Validação robusta** de parâmetros
- ✅ **Logs detalhados** de execução
- ✅ **Modo teste seguro** para validação
- ✅ **Controle total** sobre salvamento de dados
- ✅ **ChromeDriver automático** - sem downloads manuais

### Como testar com segurança:
1. **Configure modo teste**: `CRIAR_SORTEIO = False`
2. **Execute com poucas siglas**: `--siglas "PPT_1" --data "10/06/2025"`
3. **Observe o comportamento**: Formulário será preenchido mas não salvo
4. **Verifique logs**: Confirme que tudo funcionou corretamente
5. **Configure modo produção**: `CRIAR_SORTEIO = True`
6. **Execute em produção**: Com confiança de que tudo funciona

## 09-06-25 Atualização ChromeDriver Automático

### **Nova Funcionalidade:**
- **Download automático do ChromeDriver**: O script detecta a versão do Chrome e baixa o driver compatível
- **Sem downloads manuais**: Não precisa mais baixar e configurar o ChromeDriver manualmente
- **Compatibilidade automática**: Sempre usa a versão correta do driver
- **Funciona em Windows, macOS e Linux**: Suporte multiplataforma

### **Como funciona:**
1. **Detecta versão do Chrome** instalada no sistema
2. **Consulta API oficial** do ChromeDriver para versão compatível
3. **Faz download automático** do driver correto
4. **Testa funcionamento** antes de usar
5. **Reutiliza se já existir** e estiver funcionando

### **Vantagens:**
- ✅ **Zero configuração manual** do ChromeDriver
- ✅ **Sempre atualizado** com a versão do Chrome
- ✅ **Funciona automaticamente** em qualquer sistema
- ✅ **Detecta problemas** e baixa nova versão se necessário
- ✅ **Compatível com atualizações** do Chrome

### **Arquivos atualizados:**
- `scripts/novo_verificalinks.py` - ChromeDriver automático
- `scripts/config_cadRifas.py` - ChromeDriver automático
- `scripts/install_dependencies.py` - Instalador de dependências

### **Instalação:**
```bash
# Instalar dependências
python scripts/install_dependencies.py

# Executar scripts (ChromeDriver será baixado automaticamente)
python scripts/cadRifas_litoral_v3 --siglas "PPT_1" --data "10/06/2025"
python scripts/novo_verificalinks.py
```

### **Pasta do ChromeDriver:**
- **Localização**: `D:/Documentos/Workspace/chromedriver/`
- **Criada automaticamente** na primeira execução
- **Contém**: `chromedriver.exe` (Windows) ou `chromedriver` (Linux/macOS)

### **Logs informativos:**
```
Versão do Chrome detectada: 120.0.6099.109
Versão do ChromeDriver necessária: 120.0.6099.109
Baixando ChromeDriver 120.0.6099.109 para win32...
ChromeDriver 120.0.6099.109 baixado com sucesso!
ChromeDriver encontrado e funcionando: D:\Documentos\Workspace\chromedriver\chromedriver.exe
```

## 12-06-25 Atualização Campo id_siglas_diarias

### **Nova Funcionalidade:**
- **Campo de rastreabilidade**: Adicionado campo `id_siglas_diarias` na tabela `extracoes_cadastro`
- **Vinculação entre tabelas**: Cada edição em `extracoes_cadastro` agora está vinculada ao registro original em `siglas_diarias`
- **Rastreabilidade completa**: Permite identificar qual registro de `siglas_diarias` originou cada edição
- **Diferenciação de origem**: Distingue registros criados via "Cadastrar Siglas" vs "Executar Script"

### **Como funciona:**

#### **Botão "Cadastrar Siglas":**
1. **Insere na tabela `siglas_diarias`** e captura o `id` do registro recém-criado
2. **Para cada sigla**, insere na tabela `extracoes_cadastro` incluindo o `id_siglas_diarias` com o valor do `id` capturado

#### **Botão "Cadastrar Sigla Avulsa":**
1. **Insere na tabela `siglas_diarias`** e captura o `id` do registro recém-criado
2. **Insere na tabela `extracoes_cadastro`** incluindo o `id_siglas_diarias` com o valor do `id` capturado

#### **Botão "Executar Script":**
1. **Insere diretamente na tabela `extracoes_cadastro`** com `id_siglas_diarias` = `NULL`
2. **Não cria registro em `siglas_diarias`**, pois funciona independentemente

### **Estrutura da Tabela extracoes_cadastro:**
```sql
-- Nova coluna adicionada
ALTER TABLE extracoes_cadastro ADD COLUMN id_siglas_diarias INT NULL;

-- Exemplo de uso
SELECT 
    ec.edicao,
    ec.sigla_oficial,
    ec.data_sorteio,
    sd.siglas as siglas_originais,
    sd.diaSemana
FROM extracoes_cadastro ec
LEFT JOIN siglas_diarias sd ON ec.id_siglas_diarias = sd.id
WHERE ec.data_sorteio = '2025-06-13';
```

### **Vantagens da Implementação:**
- ✅ **Rastreabilidade**: Cada edição está vinculada ao registro original em `siglas_diarias`
- ✅ **Integridade**: Permite consultas que relacionam as duas tabelas
- ✅ **Flexibilidade**: Diferencia registros criados via diferentes métodos
- ✅ **Consistência**: Todos os endpoints já estão atualizados
- ✅ **Auditoria**: Permite rastrear a origem de cada edição
- ✅ **Relatórios**: Facilita geração de relatórios com dados relacionados

### **Casos de Uso:**
1. **Relatórios**: Identificar quantas edições foram criadas a partir de cada cadastro de siglas
2. **Auditoria**: Rastrear a origem de cada edição no sistema
3. **Análise**: Comparar dados entre `siglas_diarias` e `extracoes_cadastro`
4. **Manutenção**: Identificar registros órfãos ou inconsistentes

### **Endpoints Atualizados:**
- ✅ `/api/edicoes/cadastrar-siglas` - Inclui `id_siglas_diarias` com `registro_id`
- ✅ `/api/edicoes/cadastrar-sigla-avulsa` - Inclui `id_siglas_diarias` com `registro_id`
- ✅ `/api/edicoes/executar-script` - Inclui `id_siglas_diarias` como `NULL`

### **Exemplo de Consulta:**
```sql
-- Buscar todas as edições criadas a partir de um cadastro específico
SELECT 
    ec.edicao,
    ec.sigla_oficial,
    ec.status_cadastro,
    sd.siglas as siglas_originais,
    sd.data_sorteio
FROM extracoes_cadastro ec
INNER JOIN siglas_diarias sd ON ec.id_siglas_diarias = sd.id
WHERE sd.id = 123;

-- Buscar edições sem vínculo (criadas via "Executar Script")
SELECT 
    edicao,
    sigla_oficial,
    data_sorteio
FROM extracoes_cadastro
WHERE id_siglas_diarias IS NULL;
```

### **Impacto na Performance:**
- ✅ **Mínimo**: Apenas um campo adicional por registro
- ✅ **Índices**: Recomenda-se criar índice na coluna `id_siglas_diarias`
- ✅ **Consultas**: Melhora performance de joins entre as tabelas

### **Migração:**
- ✅ **Automática**: Novos registros já incluem o campo
- ✅ **Retrocompatibilidade**: Registros antigos mantêm `id_siglas_diarias` = `NULL`
- ✅ **Sem impacto**: Não afeta funcionalidades existentes

