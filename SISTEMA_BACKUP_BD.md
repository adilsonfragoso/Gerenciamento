# Sistema de Backup e Migração de Banco de Dados

## 📁 Estrutura Organizada - Pasta backup_bd

```
backup_bd/                               # Pasta principal de backup e migração
├── backup_banco_de_dados.py            # ⭐ Script principal de backup diário
├── backup_banco_agendador.py           # Agendador contínuo  
├── backup_banco_daemon.py              # Daemon silencioso
├── backup_banco_controle.py            # Controlador Python
├── backup_banco_log.py                 # Sistema de logging unificado
├── backup_banco_tarefa_windows.py      # Configurador de tarefas Windows
├── backup_banco_instalar_dependencias.py # Instalador de dependências
├── backup_banco_controle.bat           # ⭐ Controlador BAT principal
├── backup_banco_startup.vbs            # Startup silencioso
├── backup_para_migracao_manual.py      # ⭐ Script de migração manual
├── backup_python_puro.py               # Backup simples sem dependências
├── migrar_banco_dados.py               # Migração automatizada
├── migrar_banco_dados_via_web.py       # Migração via web
├── backup_banco_DOCUMENTACAO.md        # Documentação técnica detalhada
└── BACKUP_BANCO_MANUAL_USO.md          # Manual de uso
```

## 🚀 Como Usar

### Acesso Rápido (Recomendado)
```bash
# Execute do diretório raiz:
backup_controle.bat
```
Este arquivo irá abrir automaticamente o controlador na pasta backup_bd.

### Acesso Direto
```bash
# Entre na pasta backup_bd:
cd backup_bd

# Execute o controlador:
backup_banco_controle.bat
```

## ⚙️ Principais Funcionalidades

### 1. 🔄 Backup Automático Diário
- **Script**: `backup_banco_de_dados.py`
- **Horário**: 03:00h diárias
- **Rotação**: Mantém últimos 5 dias
- **Banco**: litoral (configurado no .env)

### 2. 📤 Migração Manual para phpMyAdmin
- **Script**: `backup_para_migracao_manual.py`
- **Função**: Cria backups para importação manual
- **Destino**: http://pma.linksystems.com.br
- **Gera**: Instruções detalhadas para migração

### 3. 🎮 Controle via BAT
- **Arquivo**: `backup_banco_controle.bat`
- **Menu**: 8 opções numeradas
- **Sem emojis**: Compatível com Windows
- **Background**: Execução silenciosa disponível

## 📋 Menu do Controlador BAT

```
1. Iniciar serviço de backup      ← Inicia daemon em background
2. Parar serviço de backup        ← Para daemon
3. Reiniciar serviço de backup    ← Reinicia completamente  
4. Verificar status do serviço    ← Status detalhado
5. Executar backup manual (teste) ← Teste imediato
6. Ver logs do sistema            ← Últimas linhas dos logs
7. Configurar agendamento Windows ← Setup inicial
8. Sair                           ← Fechar
```

## 📊 Configuração no .env

```env
# Configuração atual (apenas banco litoral)
SYNC_DB_HOST_ORIGEM=pma.linksystems.com.br
SYNC_DB_USER_ORIGEM=adseg  
SYNC_DB_PASSWORD_ORIGEM=Define@4536#8521
SYNC_DATABASES=litoral

# Diretório de backup (opcional)
BACKUP_DIR=D:\Backups
```

## 🗂️ Localização dos Logs

```
../scripts/andamento/logs/logs_geral_agendador.log  # Log unificado do sistema
../logs/backup_banco_de_dados.log                   # Log específico do backup
../logs/backup_banco_daemon.log                     # Log do daemon
```

## ✅ Arquivos Removidos (Limpeza)

- ❌ `backup_banco_de_dados_novo.py` (duplicado/teste)
- ❌ `backup_banco_servico_windows.py` (complexidade desnecessária)
- ❌ `backup_banco_teste.ps1` (arquivo de teste)
- ❌ Pasta `backup_banco/` (antiga estrutura)
- ❌ Arquivos `__pycache__/` (cache Python)

## 🎯 Scripts Principais para Uso

### Backup Diário Automático
```bash
cd backup_bd
python backup_banco_de_dados.py
```

### Migração Manual
```bash
cd backup_bd  
python backup_para_migracao_manual.py
```

### Controle Completo
```bash
cd backup_bd
backup_banco_controle.bat
```

## 📱 Startup Automático

Para iniciar automaticamente com Windows:
1. Copie `backup_bd/backup_banco_startup.vbs` para:
   ```
   C:\Users\[USUARIO]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
   ```

## 🔧 Manutenção

- **Verificar status**: Use opção 4 do menu BAT
- **Ver logs**: Use opção 6 do menu BAT
- **Teste manual**: Use opção 5 do menu BAT
- **Configuração**: Use opção 7 do menu BAT

## ✅ Sistema Completamente Funcional

✅ Todos os arquivos organizados em `backup_bd/`
✅ Caminhos corrigidos para nova estrutura
✅ Scripts testados e funcionando
✅ Documentação atualizada
✅ Arquivos desnecessários removidos
✅ Acesso simplificado via `backup_controle.bat` na raiz
