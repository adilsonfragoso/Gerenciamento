# Sistema de Backup Automático - Documentação

## 📋 Visão Geral
Sistema completo de backup automático de banco de dados com rotação de 5 dias e agendamento diário às 03:00h.

## 🗂️ Arquivos Criados (Prefixo: backup_banco_)

### 📜 Scripts Principais
- **`backup_banco_de_dados.py`** - Script principal de backup com rotação
- **`backup_banco_agendador.py`** - Agendador usando biblioteca `schedule`  
- **`backup_banco_controle.py`** - Interface de controle principal
- **`backup_banco_log.py`** - Sistema de logging unificado

### ⚙️ Scripts de Configuração
- **`backup_banco_tarefa_windows.py`** - Configurador de tarefas do Windows
- **`backup_banco_instalar_dependencias.py`** - Instalador de dependências
- **`backup_banco_servico_windows.py`** - Serviço Windows (avançado)

## 🚀 Como Usar

### 1. Instalação Rápida
```bash
# Execute o controlador principal
python backup_banco_controle.py

# Ou siga os passos manuais:
python backup_banco_instalar_dependencias.py
python backup_banco_tarefa_windows.py criar
```

### 2. Configuração Manual
```bash
# 1. Instalar dependências
python backup_banco_instalar_dependencias.py

# 2. Configurar agendamento Windows
python backup_banco_tarefa_windows.py criar

# 3. Verificar configuração
python backup_banco_tarefa_windows.py verificar

# 4. Teste manual
python backup_banco_de_dados.py
```

## ⏰ Sistema de Agendamento

### Tarefa Windows (Recomendado)
- **Execução**: Diária às 03:00h
- **Nome**: BackupBancoDiario
- **Comando**: `python backup_banco_de_dados.py`
- **Local**: Agendador de Tarefas do Windows

### Agendador Manual (Alternativo)
```bash
# Executa agendador em modo contínuo
python backup_banco_agendador.py
```

## 🔄 Sistema de Rotação
- **Mantém**: Últimos 5 dias de backup
- **Remove**: Backups com mais de 5 dias
- **Comportamento**: 
  - Se backup do dia existe → Pula criação, executa limpeza
  - Se backup não existe → Cria novo + limpa antigos

## 📁 Estrutura de Arquivos

### Backups
```
D:\Backups\
├── litoral_2025-07-15.sql.gz
├── litoral_2025-07-14.sql.gz
└── ... (últimos 5 dias)
```

### Logs
```
scripts/andamento/logs/
└── logs_geral_agendador.log    # Log geral unificado

logs/
└── backup_banco_de_dados.log   # Log específico do backup
```

## 🎯 Variáveis do .env
```env
# Configurações obrigatórias
SYNC_DB_HOST_ORIGEM=pma.linksystems.com.br
SYNC_DB_USER_ORIGEM=adseg
SYNC_DB_PASSWORD_ORIGEM=Define@4536#8521
SYNC_DATABASES=litoral

# Opcional - diretório de backup
BACKUP_DIR=D:\Backups
```

## 📊 Comandos de Gestão

### Verificar Status
```bash
# Via script
python backup_banco_tarefa_windows.py verificar

# Via Windows
schtasks /query /tn "BackupBancoDiario"
```

### Ver Logs
```bash
# Via script
python backup_banco_controle.py  # opção 6

# Manual
Get-Content "scripts/andamento/logs/logs_geral_agendador.log" | Select-Object -Last 20
```

### Remover Agendamento
```bash
python backup_banco_tarefa_windows.py remover
```

## 🛠️ Dependências
- **python-dotenv** - Carregamento de variáveis .env
- **schedule** - Agendamento Python
- **pywin32** - Serviços Windows (opcional)

## 🔧 Troubleshooting

### Backup não executa
1. Verificar tarefa Windows: `schtasks /query /tn "BackupBancoDiario"`
2. Testar script manual: `python backup_banco_de_dados.py`
3. Verificar logs: `scripts/andamento/logs/logs_geral_agendador.log`

### Erro de mysqldump
- Verificar instalação MySQL Workbench
- Caminhos verificados automaticamente:
  - `C:/Program Files/MySQL/MySQL Workbench 8.0/mysqldump.exe`
  - `C:/xampp/mysql/bin/mysqldump.exe`
  - Sistema PATH

### Logs não aparecem
- Verificar permissões de escrita
- Estrutura de diretórios criada automaticamente
- Log geral: `scripts/andamento/logs/logs_geral_agendador.log`

## 📝 Padrão de Logs
```
2025-07-15 03:00:01 - [AGENDADOR_BACKUP] - INFO - 🕐 Iniciando backup agendado...
2025-07-15 03:00:15 - [AGENDADOR_BACKUP] - INFO - ✅ Backup executado com sucesso!
```

## ✅ Status de Implementação
- [x] Script de backup com rotação
- [x] Agendamento Windows (schtasks)
- [x] Sistema de logging unificado
- [x] Interface de controle
- [x] Instalador de dependências
- [x] Documentação completa
- [x] Teste e validação

## 🎯 Próximos Passos
1. ✅ Sistema está operacional
2. ⏰ Agendamento configurado para 03:00h diário
3. 📊 Monitorar logs nos primeiros dias
4. 🔧 Ajustar se necessário
