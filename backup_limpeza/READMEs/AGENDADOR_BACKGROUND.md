# 🔒 Agendador de Rifas - Versão Background (Oculto)

## 🎯 Problema Resolvido

**Problema:** Terminal do agendador pode ser fechado acidentalmente, interrompendo o monitoramento.

**Solução:** Sistema que roda **completamente em background** (oculto), sem janelas visíveis, impossível de fechar por acidente.

## 🚀 Como Funciona

### 🔧 Sistema de Serviço
- **Execução oculta**: Sem janelas ou terminais visíveis
- **Controle remoto**: Interface separada para gerenciar o serviço
- **Logs em arquivo**: Todo o histórico salvo em arquivos
- **Auto-recuperação**: Reinicia automaticamente em caso de erro

### 📊 Monitoramento Inteligente
- **Intervalos dinâmicos**: 5min → 3min (80%) → 1min (90%/15min antes)
- **Status em tempo real**: Arquivo JSON com status atual
- **PID tracking**: Controle preciso do processo

## 📁 Arquivos do Sistema

### 🎮 Controladores
- **`controlador_agendador.bat`** - Interface principal (duplo clique)
- **`iniciar_servico_oculto.bat`** - Inicia serviço rapidamente
- **`parar_servico.bat`** - Para o serviço rapidamente

### 🐍 Scripts Python
- **`scripts/agendador_servico_v2.py`** - Serviço em background
- **`scripts/controlador_agendador.py`** - Controlador do serviço

### 📝 Arquivos de Status
- **`scripts/agendador.pid`** - ID do processo (temporário)
- **`scripts/agendador_status.json`** - Status em tempo real
- **`scripts/logs/agendador_servico.log`** - Logs do serviço

## 🎮 Como Usar

### Método 1: Interface Gráfica (Recomendado)
```
1. Duplo clique em: controlador_agendador.bat
2. Escolher opção:
   1 - Iniciar Serviço
   2 - Parar Serviço  
   3 - Reiniciar Serviço
   4 - Atualizar Status
   5 - Ver Logs
   0 - Sair
```

### Método 2: Início Rápido
```
Duplo clique em: iniciar_servico_oculto.bat
```

### Método 3: Linha de Comando
```bash
# Iniciar
python scripts/controlador_agendador.py start

# Parar
python scripts/controlador_agendador.py stop

# Status
python scripts/controlador_agendador.py status

# Reiniciar
python scripts/controlador_agendador.py restart
```

## 📊 Interface do Controlador

```
╔══════════════════════════════════════════════════════════════╗
║              CONTROLADOR DO AGENDADOR DE RIFAS              ║
║                                                              ║
║  🎮 Controle total do serviço de monitoramento               ║
║  🔍 Verificação de status em tempo real                     ║
║  🚀 Execução em background (oculto)                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

📊 STATUS DO AGENDADOR:
   Status: RODANDO
   Detalhes: Processo 39848 ativo
   PID: 39848
   Rifas Ativas: 2
   Última Verificação: 23:15:42
   Log: scripts/logs/agendador_servico.log

🎮 OPÇÕES:
   1 - Iniciar Serviço
   2 - Parar Serviço
   3 - Reiniciar Serviço
   4 - Atualizar Status
   5 - Ver Logs
   0 - Sair
```

## 🔍 Monitoramento em Tempo Real

### Arquivo de Status (JSON)
```json
{
  "status": "rodando",
  "pid": 39848,
  "inicio": "2025-01-21T23:15:30",
  "rifas_ativas": 2,
  "ultima_verificacao": "2025-01-21T23:15:42",
  "log_file": "scripts/logs/agendador_servico.log"
}
```

### Verificação de Processo
- **Ativo**: Processo rodando normalmente
- **Parado**: Serviço não está executando
- **Erro**: Problema detectado no serviço

## 📝 Sistema de Logs

### Log Principal: `agendador_servico.log`
```
2025-01-21 23:15:30 - INFO - === INICIANDO AGENDADOR COMO SERVIÇO ===
2025-01-21 23:15:30 - INFO - PID 39848 salvo em scripts/agendador.pid
2025-01-21 23:15:31 - INFO - Encontradas 2 rifas ativas
2025-01-21 23:15:32 - INFO - Serviço iniciado com sucesso - rodando em background
2025-01-21 23:15:42 - INFO - 🔄 Executando verificação (intervalo 5min)
```

### Logs de Verificação: `verificar_andamento.log`
- Detalhes de cada verificação de rifa
- Mudanças de percentual
- Erros encontrados

## ⚡ Vantagens do Sistema Background

### ✅ **Impossível Fechar por Acidente**
- Sem janelas visíveis
- Processo independente
- Não aparece na barra de tarefas

### ✅ **Controle Total**
- Interface dedicada para gerenciar
- Status em tempo real
- Logs detalhados

### ✅ **Robustez**
- Auto-recuperação de erros
- Monitoramento de processo
- Parada graceful

### ✅ **Facilidade de Uso**
- Arquivos batch para Windows
- Interface intuitiva
- Comandos simples

## 🔧 Troubleshooting

### Problema: Serviço não inicia
```bash
# Verificar dependências
pip install schedule pymysql selenium psutil

# Verificar logs
python scripts/controlador_agendador.py
# Escolher opção 5 - Ver Logs
```

### Problema: Processo "fantasma"
```bash
# Forçar parada
python scripts/controlador_agendador.py stop

# Verificar se parou
python scripts/controlador_agendador.py status
```

### Problema: Logs não aparecem
- Aguardar alguns minutos (serviço pode estar inicializando)
- Verificar se há rifas ativas no banco
- Reiniciar o serviço

## 🎯 Cenários de Uso

### 💼 **Uso Diário**
1. **Manhã**: `iniciar_servico_oculto.bat`
2. **Durante o dia**: Serviço roda sozinho
3. **Noite**: `parar_servico.bat` (opcional)

### 🔧 **Manutenção**
1. **Verificar status**: `controlador_agendador.bat`
2. **Ver logs**: Opção 5 no controlador
3. **Reiniciar**: Opção 3 no controlador

### 🚨 **Emergência**
1. **Parar imediatamente**: `parar_servico.bat`
2. **Verificar problema**: Ver logs no controlador
3. **Reiniciar**: `iniciar_servico_oculto.bat`

## 📈 Comparação: Visível vs Background

| Aspecto | Versão Visível | Versão Background |
|---------|----------------|-------------------|
| **Segurança** | ❌ Pode ser fechado | ✅ Impossível fechar |
| **Interface** | ✅ Visual direto | ✅ Controlador dedicado |
| **Logs** | ✅ Console + arquivo | ✅ Apenas arquivo |
| **Controle** | ❌ Limitado | ✅ Total |
| **Robustez** | ❌ Frágil | ✅ Robusto |

---

## 🎉 **Sistema Perfeito para Produção!**

✅ **Implementação Completa**
- Serviço em background funcional
- Controlador intuitivo
- Logs detalhados
- Arquivos batch para facilitar uso

✅ **Pronto para Uso 24/7**
- Monitoramento contínuo
- Impossível fechar por acidente
- Controle total do serviço
- Interface amigável

**Agora você pode deixar o monitoramento rodando sem se preocupar em fechar o terminal por acidente!** 🚀 