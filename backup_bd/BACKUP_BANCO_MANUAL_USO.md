# Sistema de Backup Automático - Instalação e Uso

## 📁 Estrutura Final

```
Gerenciamento/
├── backup_banco/                    # Pasta principal do sistema
│   ├── backup_banco_de_dados.py     # Script principal de backup
│   ├── backup_banco_agendador.py    # Agendador contínuo
│   ├── backup_banco_daemon.py       # Daemon silencioso
│   ├── backup_banco_controle.py     # Controlador Python
│   ├── backup_banco_log.py          # Sistema de logging
│   ├── backup_banco_tarefa_windows.py # Configurador de tarefas
│   ├── backup_banco_instalar_dependencias.py # Instalador
│   └── backup_banco_DOCUMENTACAO.md # Documentação detalhada
├── backup_banco_controle.bat        # Controlador BAT principal
├── backup_banco_startup.vbs         # Script para startup silencioso
└── backup_banco_teste.ps1           # Teste automatizado
```

## 🚀 Instalação e Configuração

### 1. Primeira Execução
```bash
# Execute o controlador BAT
backup_banco_controle.bat

# Escolha as opções na ordem:
# 7 - Configurar agendamento Windows
# 1 - Iniciar serviço de backup
# 4 - Verificar status
```

### 2. Para Startup Automático do Windows
1. Copie `backup_banco_startup.vbs` para a pasta Startup:
   ```
   C:\Users\[USUARIO]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
   ```
2. Ou configure via tecla Windows+R: `shell:startup`

## 🎮 Como Usar o Controlador BAT

Execute: `backup_banco_controle.bat`

### Opções Disponíveis:
- **1. Iniciar serviço** - Inicia o daemon de backup em background
- **2. Parar serviço** - Para o daemon de backup
- **3. Reiniciar serviço** - Reinicia o daemon completamente
- **4. Verificar status** - Mostra status do daemon + tarefa Windows
- **5. Backup manual** - Executa backup de teste imediatamente
- **6. Ver logs** - Mostra últimas linhas dos logs
- **7. Configurar agendamento** - Configura tarefa no Windows
- **8. Sair** - Fecha o controlador

## ⚙️ Características do Sistema

### Execução Silenciosa
- ✅ BAT executa sem manter terminal aberto
- ✅ Daemon roda completamente em background
- ✅ Não interfere com uso normal do sistema
- ✅ Startup automático disponível

### Controle de Processo
- ✅ PID file para controle do daemon
- ✅ Detecção automática se já está rodando
- ✅ Parada e reinicialização segura
- ✅ Status detalhado disponível

### Agendamento Duplo
- ✅ **Tarefa Windows**: Execução às 03:00h (recomendado)
- ✅ **Daemon Python**: Agendador contínuo (alternativo)

## 📊 Monitoramento

### Logs Disponíveis:
```
scripts/andamento/logs/logs_geral_agendador.log    # Log unificado do sistema
logs/backup_banco_daemon.log                       # Log do daemon
logs/backup_banco_de_dados.log                     # Log específico do backup
```

### Verificação de Status:
```bash
# Via BAT (opção 4)
backup_banco_controle.bat

# Via comando direto
cd backup_banco
python backup_banco_daemon.py status

# Via Windows
schtasks /query /tn "BackupBancoDiario"
```

## 🔧 Comandos Diretos (Avançado)

### Controle do Daemon:
```bash
cd backup_banco
python backup_banco_daemon.py start     # Iniciar
python backup_banco_daemon.py stop      # Parar  
python backup_banco_daemon.py restart   # Reiniciar
python backup_banco_daemon.py status    # Status
```

### Backup Manual:
```bash
cd backup_banco
python backup_banco_de_dados.py
```

## 🎯 Funcionamento

1. **Inicialização**: Sistema inicia automaticamente com Windows (se configurado)
2. **Agendamento**: Backup executa automaticamente às 03:00h diárias
3. **Rotação**: Mantém últimos 5 dias, remove backups antigos
4. **Logging**: Registra todas atividades nos logs unificados
5. **Controle**: BAT permite gestão completa sem conhecimento técnico

## ✅ Status de Implementação

- [x] Reorganização em pasta específica
- [x] Correção de caminhos e imports
- [x] Daemon silencioso para background
- [x] Arquivo BAT com menu numerado
- [x] Startup automático via VBS
- [x] Sistema de controle de PID
- [x] Logs unificados mantidos
- [x] Teste automatizado criado
- [x] Documentação completa

## 🏁 Sistema Pronto para Produção!

O sistema está completamente funcional e pode ser usado em produção. Use o arquivo BAT como interface principal e configure o startup automático conforme necessário.
