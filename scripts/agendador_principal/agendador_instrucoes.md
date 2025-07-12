# 📋 Agendador Desativa e Alimenta - Instruções Completas

## 🎯 **Visão Geral**

O Agendador Desativa e Alimenta é um sistema automatizado que executa scripts de forma programada e **completamente oculta** no Windows. Ele foi projetado para rodar em segundo plano sem interferir no uso do computador.

---

## 📁 **Arquivos do Sistema**

### **1. `agendador_desativa_alimenta.py`**
**Função**: Script principal que contém toda a lógica do agendador
**Características**:
- ✅ Executa tarefas **imediatamente** na primeira execução
- ✅ Configura **94 agendamentos** automáticos por semana
- ✅ Logs **simplificados** (apenas sucessos/erros)
- ✅ Execução **oculta** dos scripts (sem terminal)
- ✅ Intervalo de **3 minutos** entre scripts na execução inicial

**Scripts que executa**:
- `desativa_concluidas_v4.py`
- `alimenta_premiados.py`

### **2. `agendador_oculto.pyw`** (CORRIGIDO)
**Função**: Wrapper para executar o agendador sem abrir terminal
**Características**:
- ✅ Extensão `.pyw` = **sem janela** no Windows
- ✅ Execução **completamente invisível**
- ✅ Usa `subprocess` para maior confiabilidade
- ✅ Log de erros em arquivo separado

### **3. `startup_agendador.bat`** (NOVO)
**Função**: Arquivo batch otimizado para startup do Windows
**Características**:
- ✅ Aguarda 30s após boot para estabilizar sistema
- ✅ Execução em modo **minimizado**
- ✅ Log de inicialização para confirmar execução
- ✅ Ideal para **startup automático**

---

## 🚀 **Como Usar**

### **Opção 1: Execução Manual (Teste)**
```bash
# Navegue até a pasta do projeto
cd D:\Documentos\Workspace\Gerenciamento

# Execute diretamente (com terminal visível)
python scripts\agendador_principal\agendador_desativa_alimenta.py
```

### **Opção 2: Execução Oculta Manual**
```bash
# Navegue até a pasta do projeto
cd D:\Documentos\Workspace\Gerenciamento

# Execute em modo oculto (sem terminal)
pythonw scripts\agendador_principal\agendador_oculto.pyw
```

### **Opção 3: Startup Automático (Recomendado)**
1. **Abra a pasta de startup**:
   - Pressione `Win + R`
   - Digite: `shell:startup`
   - Pressione Enter

2. **Copie o arquivo**:
   - Copie `startup_agendador.bat`
   - Cole na pasta de startup que abriu

3. **Pronto!** O agendador iniciará automaticamente com o Windows

---

## ⏰ **Funcionamento Detalhado**

### **🚀 Execução Inicial (Primeira vez)**
Quando o agendador é iniciado:

1. **T+0min**: Executa `desativa_concluidas_v4.py`
2. **T+3min**: Executa `alimenta_premiados.py`
3. **T+3min+**: Inicia os agendamentos regulares

### **📅 Agendamentos Regulares**
Após a execução inicial, os scripts rodam automaticamente:

#### **Segunda, Terça, Quinta, Sexta** (Dias normais):
- **Horários**: 10:00, 11:00, 12:00, 15:00, 17:00, 19:00, 22:00
- **desativa_concluidas_v4**: Nos horários exatos
- **alimenta_premiados**: 10 minutos antes de cada horário

#### **Quarta e Sábado** (Dias de Federal):
- **Horários**: 10:00, 11:00, 12:00, 15:00, 17:00, 19:30, 22:00
- **desativa_concluidas_v4**: Nos horários exatos
- **alimenta_premiados**: 10 minutos antes de cada horário

#### **Domingo**:
- **Horários**: 10:00, 11:00, 12:00, 15:00, 17:00
- **desativa_concluidas_v4**: Nos horários exatos
- **alimenta_premiados**: 10 minutos antes de cada horário

---

## 📊 **Sistema de Logs**

### **Arquivo de Log Principal**
**Local**: `scripts/logs/agendador_principal_melhorado.log`

### **Formato dos Logs**
```
2025-07-10 14:00:00 - INFO - INICIO - Agendador Principal Melhorado iniciado
2025-07-10 14:00:15 - INFO - SUCESSO - desativa_concluidas_v4.py executado com sucesso
2025-07-10 14:00:15 - INFO - AGUARDANDO - 3 minutos antes do próximo script
2025-07-10 14:03:15 - INFO - SUCESSO - alimenta_premiados.py executado com sucesso
2025-07-10 14:03:15 - INFO - CONCLUIDO - Execução inicial bem-sucedida
2025-07-10 14:03:15 - INFO - RODANDO - Agendador em execução (modo oculto)
```

### **Tipos de Log**
- **INICIO**: Agendador iniciado
- **SUCESSO**: Script executado com sucesso
- **ERRO**: Falha na execução de script
- **AGUARDANDO**: Intervalo entre execuções
- **CONCLUIDO**: Execução inicial finalizada
- **RODANDO**: Agendador em funcionamento
- **PARADO**: Agendador interrompido
- **ENCERRADO**: Agendador finalizado

---

## 🔧 **Solução de Problemas**

### **Como verificar se está funcionando**
1. **Verifique o log principal**: `scripts/logs/agendador_desativa_alimenta.log`
2. **Procure por**: "RODANDO - Agendador em execução"
3. **Verifique execuções**: Logs de SUCESSO/ERRO dos scripts
4. **Log de startup**: `scripts/logs/startup_agendador.log` (se usar startup)

### **Como parar o agendador**
1. **Abra o Gerenciador de Tarefas** (`Ctrl + Shift + Esc`)
2. **Procure por**: `python.exe` ou `pythonw.exe`
3. **Finalize** o processo relacionado ao agendador

### **Problemas comuns e soluções**
- **❌ Não inicia**: Verifique se Python está instalado e no PATH
- **❌ Scripts falham**: Verifique os caminhos dos arquivos no código
- **❌ Sem logs**: Verifique permissões da pasta `scripts/logs`
- **❌ Erro "No module"**: Use execução direta em vez de .pyw
- **❌ Redirecionamento**: Removido `> nul 2>&1` que causava problemas

---

## ⚙️ **Configurações Avançadas**

### **Alterar horários**
Edite a função `configurar_agendamentos()` em `agendador_desativa_alimenta.py`:
```python
horarios_padrao = ["10:00", "11:00", "12:00", "15:00", "17:00", "19:00", "22:00"]
```

### **Alterar intervalo inicial**
Edite a função `executar_tarefas_iniciais()`:
```python
time.sleep(180)  # 180 = 3 minutos
```

### **Adicionar novos scripts**
1. Crie uma nova função similar a `rodar_desativa_concluidas_v4()`
2. Adicione aos agendamentos em `configurar_agendamentos()`

---

## 🎯 **Resumo de Uso**

### **Para uso diário**:
1. **Coloque no startup** (Opção 3 acima)
2. **Esqueça que existe** - roda automaticamente
3. **Verifique logs** ocasionalmente se necessário

### **Para desenvolvimento/teste**:
1. **Execute manualmente** (Opção 1)
2. **Monitore logs** em tempo real
3. **Pare via Gerenciador de Tarefas** quando necessário

---

## 📞 **Suporte**

- **Logs**: Sempre verifique `scripts/logs/agendador_desativa_alimenta.log`
- **Erros críticos**: Verifique `scripts/logs/agendador_erro_critico.log`
- **Modificações**: Edite `agendador_principal_melhorado.py` conforme necessário

---

## 🔄 **Arquivos Atualizados e Corrigidos**

### **✅ Problemas Resolvidos:**
1. **Redirecionamento removido**: `> nul 2>&1` causava falhas no `alimenta_premiados.py`
2. **Import corrigido**: Arquivo `.pyw` agora usa `subprocess` em vez de imports complexos
3. **Logs melhorados**: Arquivos de erro separados para diagnóstico
4. **Startup otimizado**: Aguarda 30s para estabilizar o sistema

### **📁 Arquivos Finais:**
- ✅ `agendador_desativa_alimenta.py` - Script principal (FUNCIONANDO)
- ✅ `agendador_oculto.pyw` - Execução oculta (CORRIGIDO)
- ✅ `startup_agendador.bat` - Startup automático (NOVO)
- ✅ `agendador_instrucoes.md` - Esta documentação (ATUALIZADA)

### **🚀 Instruções Finais:**

#### **Para testar agora:**
```bash
cd D:\Documentos\Workspace\Gerenciamento
python scripts\agendador_principal\agendador_desativa_alimenta.py
```

#### **Para usar em modo oculto:**
```bash
cd D:\Documentos\Workspace\Gerenciamento
pythonw scripts\agendador_principal\agendador_oculto.pyw
```

#### **Para startup automático:**
1. Copie `startup_agendador.bat`
2. `Win + R` → `shell:startup`
3. Cole o arquivo na pasta
4. Reinicie o Windows

### **📊 Logs para monitorar:**
- **Principal**: `scripts/logs/agendador_desativa_alimenta.log`
- **Startup**: `scripts/logs/startup_agendador.log`
- **Erros oculto**: `scripts/logs/agendador_oculto_erro.log`

---

**✅ Sistema configurado para execução completamente oculta e automática!**
