# Agendador Inteligente de Rifas

Este diretório contém todos os scripts e arquivos relacionados ao **Agendador Inteligente de Rifas** do sistema de gerenciamento.

O agendador é responsável por:
- Monitorar automaticamente o andamento das rifas cadastradas.
- Atualizar status, percentuais e horários de fechamento.
- Gerar logs detalhados do funcionamento.
- Permitir controle (iniciar, parar, reiniciar) via scripts e menu .bat.

## Estrutura dos Arquivos

- **agendador_servico.py**
  - Script principal que executa o monitoramento automático das rifas em background.
  - Responsável por ler as rifas ativas, calcular intervalos de verificação e atualizar o status.

- **agendador_verificacao_rifas.py**
  - Módulo com as classes e funções auxiliares para lógica de verificação das rifas.
  - Usado pelo script principal para buscar rifas, calcular fechamentos, etc.

- **controlador_agendador.py**
  - Script de controle avançado (opcional) para manipular o agendador via linha de comando.
  - Pode ser usado para integrações ou automações específicas.

- **agendador_status.json**
  - Arquivo gerado automaticamente pelo agendador.
  - Contém informações de status: PID, rifas ativas, horário de início, etc.

- **logs/agendador_rifas.log**
  - Log detalhado de todas as ações e eventos do agendador.
  - Útil para auditoria, depuração e acompanhamento do funcionamento.

## Como usar

- Utilize o menu `gerenciar_agendador.bat` na raiz do projeto para iniciar, parar, reiniciar e monitorar o agendador de forma simples e centralizada.
- Os scripts desta pasta não devem ser executados diretamente, exceto para manutenção ou depuração avançada.

---

**Dica:** Mantenha todos os arquivos do agendador centralizados nesta pasta para facilitar a manutenção e evitar conflitos.

# 🎯 Sistema de Agendador de Rifas

## 📋 Visão Geral

Este sistema implementa um agendador inteligente para monitoramento automático de rifas, com verificação de andamento em tempo real e atualização automática do dashboard.

## 🏗️ Arquitetura do Sistema

```
gerenciar_agendador.bat (Interface Principal)
    ↓
agendador_servico.py (Serviço Principal)
    ↓
agendador_verificacao_rifas.py (Lógica de Negócio)
    ↓
verificar_andamento_rifas.py (Verificação Web)
```

## 📁 Estrutura de Arquivos

### 🔧 **Arquivos Principais:**

| Arquivo | Função | Status |
|---------|--------|--------|
| `agendador_servico.py` | Serviço principal em background | ✅ **ATIVO** |
| `agendador_verificacao_rifas.py` | Lógica de monitoramento inteligente | ✅ **DEPENDÊNCIA** |
| `controlador_agendador.py` | Controlador Python (backup) | 🔄 **ALTERNATIVO** |

### 🎮 **Interfaces de Controle:**

| Arquivo | Localização | Função |
|---------|-------------|--------|
| `gerenciar_agendador.bat` | **Raiz do projeto** | Interface principal |
| `agendador_rapido.bat` | **Raiz do projeto** | Comandos rápidos |

## 🔄 Fluxo de Funcionamento

### 1. **Inicialização**
```
gerenciar_agendador.bat → agendador_servico.py → agendador_verificacao_rifas.py
```

### 2. **Monitoramento Contínuo**
- **Verificação inicial** de todas as rifas ativas
- **Agendamento inteligente** baseado em:
  - Percentual de andamento (80% = 3min, 90% = 1min)
  - Proximidade do fechamento (15min antes = 1min)
  - Intervalo padrão de 5 minutos

### 3. **Processos Automáticos**
- ✅ Verificação de andamento das rifas
- 🔄 Recuperação de rifas com erro
- 📡 Notificação do dashboard
- 📄 Envio automático de PDFs para WhatsApp

## 🎯 Como Usar

### **Interface Principal (Recomendado):**
```bash
# Clique duas vezes no arquivo
gerenciar_agendador.bat
```

### **Comandos Rápidos:**
```bash
agendador_rapido.bat start    # Iniciar
agendador_rapido.bat stop     # Parar
agendador_rapido.bat restart  # Reiniciar
agendador_rapido.bat status   # Ver status
```

## 📊 Monitoramento

### **Arquivos de Status:**
- `scripts/agendador.pid` - PID do processo ativo
- `scripts/agendador_status.json` - Status detalhado
- `scripts/logs/agendador_servico.log` - Logs do serviço

### **Verificação de Status:**
```bash
# Via interface
gerenciar_agendador.bat → Opção 4

# Via comando
agendador_rapido.bat status
```

## 🔧 Configuração

### **Horários de Fechamento:**
```python
HORARIOS_FECHAMENTO = {
    'PPT': '09:20',
    'PTM': '11:20', 
    'PT': '14:20',
    'PTV': '16:20',
    'PTN': '18:20',
    'FEDERAL': '19:00',
    'CORUJINHA': '21:30'
}
```

### **Intervalos de Monitoramento:**
- **Padrão:** 5 minutos
- **80% de andamento:** 3 minutos
- **90% de andamento:** 1 minuto
- **Próximo do fechamento:** 1 minuto

## 🚨 Troubleshooting

### **Problemas Comuns:**

1. **Agendador não inicia:**
   - Verificar se Python está instalado
   - Verificar dependências: `pip install schedule pymysql selenium`

2. **Dashboard não atualiza:**
   - Verificar se o servidor está rodando na porta 8001
   - Verificar logs em `scripts/logs/agendador_servico.log`

3. **Erro de encoding:**
   - Arquivo temporário, não afeta funcionamento
   - Relacionado ao envio automático de PDFs

### **Logs Importantes:**
- `scripts/logs/agendador_servico.log` - Log principal
- `scripts/logs/agendador_rifas.log` - Log de verificação

## 📈 Métricas de Performance

### **Monitoramento Ativo:**
- **6 rifas ativas** sendo monitoradas
- **Verificação a cada 5 minutos**
- **Atualização automática** do dashboard
- **Recuperação automática** de erros

### **Última Atualização:**
- **PPT (Edição 6259):** 9% → 11% ✅
- **Tempo de processamento:** ~30 segundos por verificação
- **Taxa de sucesso:** 100% (6/6 rifas)

## 🔄 Manutenção

### **Limpeza Regular:**
```bash
# Via interface
gerenciar_agendador.bat → Opção 7

# Manual
del scripts\agendador.pid
del scripts\agendador_status.json
```

### **Backup:**
- Arquivos de configuração estão versionados no Git
- Logs são mantidos para análise
- Status é recriado automaticamente

## 📞 Suporte

### **Em caso de problemas:**
1. Verificar logs em `scripts/logs/`
2. Usar `gerenciar_agendador.bat` → Opção 5 (Ver Logs)
3. Reiniciar o serviço via interface
4. Verificar status do processo

---

**⚠️ IMPORTANTE:** Sempre leia esta documentação antes de modificar qualquer arquivo do sistema de agendador!

# Gerenciamento do Agendador

## Como iniciar, parar e reiniciar o agendador

- **Iniciar:**
  - Pelo menu do Windows ou terminal, execute:
    - `gerenciar_agendador.bat` e escolha a opção 1
    - Ou rode diretamente: `python scripts/agendador/agendador_servico.py`
- **Parar:**
  - Use o menu do .bat (opção 2) ou rode:
    - `python scripts/agendador/controlador_agendador.py 2`
- **Reiniciar:**
  - Use o menu do .bat (opção 3) ou rode:
    - `python scripts/agendador/controlador_agendador.py 3`

## Arquivos principais
- `scripts/agendador/agendador_servico.py`: serviço principal do agendador (background)
- `scripts/agendador/controlador_agendador.py`: script de controle (iniciar, parar, reiniciar, status, logs)
- `gerenciar_agendador.bat`: menu visual para controle rápido

## Arquivos removidos/obsoletos
- `parar_agendador.py` não é mais utilizado. Toda a parada/reinício deve ser feita via controlador. 