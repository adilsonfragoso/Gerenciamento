# 📋 Sistema de Verificação de Andamento de Rifas

## 🎯 **SCRIPTS DO PROCESSO**

### **📊 Scripts Principais:**
1. **`agendador_verificacao_rifas.py`** - Agendador inteligente (cérebro do sistema)
2. **`verificar_andamento_rifas.py`** - Verificação web com Selenium
3. **`recuperar_rifas_erro.py`** - Recuperação de rifas com erro
4. **`envio_automatico_pdfs_whatsapp.py`** - Envio automático de PDFs

### **🔧 Scripts de Suporte:**
5. **`agendador_servico.py`** - Serviço em background
6. **`gerenciar_agendador.bat`** - Interface de controle
7. **`agendador_status.json`** - Status do sistema
8. **`agendador_notifications.json`** - Notificações para dashboard

---

## 🔄 **HIERARQUIA DE EXECUÇÃO**

```
1. gerenciar_agendador.bat (Interface)
   ↓
2. agendador_servico.py (Serviço em Background)
   ↓  
3. agendador_verificacao_rifas.py (Agendador Inteligente)
   ↓
4. verificar_andamento_rifas.py (Verificação Web)
   ↓
5. recuperar_rifas_erro.py (Recuperação)
   ↓
6. envio_automatico_pdfs_whatsapp.py (PDFs)
```

---

## 📋 **DESCRIÇÃO DETALHADA DE CADA SCRIPT**

### **1. 🧠 `agendador_verificacao_rifas.py` - CÉREBRO INTELIGENTE**

#### **🎯 Função Principal:**
- **Coordena** todo o sistema de verificação
- **Calcula intervalos dinâmicos** baseado no andamento das rifas
- **Agenda verificações** de forma inteligente

#### **⏰ Intervalos Inteligentes:**
- **95%+ andamento** → **MODO FOCO** (monitora apenas essa rifa a cada **1 minuto**)
- **90%+ andamento** → Verifica a cada **1 minuto**
- **80%+ andamento** → Verifica a cada **3 minutos**
- **15min antes do fechamento** → Verifica a cada **1 minuto**
- **Padrão** → Verifica a cada **5 minutos**

#### **🕐 Horários de Fechamento:**
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

#### **🔄 Fluxo de Execução:**
1. **Busca rifas ativas** no banco (status 'ativo' ou 'error')
2. **Calcula intervalos** baseado em andamento e proximidade do fechamento
3. **Cria jobs dinâmicos** agrupados por intervalo
4. **Executa verificações** em sequência
5. **Reagenda automaticamente** baseado no novo estado

#### **📊 Exemplo de Cronograma Normal:**
```
📋 CRONOGRAMA ATUAL:
⏰ A cada 1 min (90%+ andamento):
  • PTN 6293 - 92%
⏰ A cada 3 min (80%+ andamento):
  • PT 6294 - 85%
⏰ A cada 5 min (intervalo padrão):
  • PPT 6295 - 45%
  • FEDERAL 6296 - 30%
```

#### **🎯 Exemplo de Cronograma MODO FOCO:**
```
🎯 MODO FOCO ATIVADO: PTN 6293 (95%)
🔍 CONCENTRANDO MONITORAMENTO APENAS NESTA RIFA ATÉ 100%

📋 CRONOGRAMA MODO FOCO:
🎯 A cada 1 min (FOCO 95%+):
  • PTN 6293 (Edição 6293) - 95%
```

#### **🎯 MODO FOCO (95%+) - FUNCIONALIDADE ESPECIAL:**

**Concentra todo o monitoramento em uma única rifa quando ela atinge 95% de andamento.**

**🔄 Como funciona:**
1. **Detecção:** Quando uma rifa atinge 95%
2. **Ativação:** Sistema entra em "modo foco"
3. **Concentração:** Monitora APENAS essa rifa a cada 1 minuto
4. **Outras rifas:** Temporariamente ignoradas
5. **Conclusão:** Quando rifa atinge 100%, volta ao modo normal
6. **Processamento:** Executa todas as ações de conclusão (PDFs, etc.)

**🎯 Vantagens:**
- **Máxima precisão** no momento crítico
- **Recursos concentrados** na rifa mais importante
- **Detecção imediata** quando atinge 100%
- **Processamento rápido** de conclusão

**📊 Logs do Modo Foco:**
```
🎯 MODO FOCO ATIVADO: PTN 6293 (95%)
🔍 CONCENTRANDO MONITORAMENTO APENAS NESTA RIFA ATÉ 100%
🎯 Verificando apenas rifa em foco: PTN 6293
🏆 RIFA EM FOCO CONCLUÍDA: PTN 6293 - SAINDO DO MODO FOCO
🔄 SAINDO DO MODO FOCO - Voltando ao monitoramento normal
```

---

### **2. 🌐 `verificar_andamento_rifas.py` - VERIFICAÇÃO WEB**

#### **🎯 Função Principal:**
- **Acessa os sites** das rifas usando Selenium
- **Extrai percentuais** de andamento
- **Atualiza banco de dados** com novos dados

#### **🔧 Tecnologias Utilizadas:**
- **Selenium WebDriver** (Chrome headless)
- **PyMySQL** para banco de dados
- **Regex** para extração de percentuais

#### **🔍 Estratégias de Extração:**
1. **XPath específico** (método principal)
2. **Seletores CSS alternativos** (fallback)
3. **Busca em todo HTML** (último recurso)
4. **Assume 0%** se nada encontrado

#### **🛡️ Detecção de Erros:**
- **Links inválidos** → ERRO_LINK_INVALIDO
- **Páginas 404** → ERRO_PAGINA_NAO_ENCONTRADA
- **Timeout** → ERRO_ACESSO
- **Exceções gerais** → ERRO_GERAL

#### **💾 Atualização do Banco:**
- **0%-99%** → Status permanece 'ativo'
- **100%** → Status muda para 'concluído'
- **Erro** → Status muda para 'error'

#### **📊 Exemplo de Log:**
```
=== INICIANDO VERIFICAÇÃO DE ANDAMENTO DAS RIFAS ===
--- Processando 1/3 ---
Edição: 6293
Sigla: PTN
Andamento atual: 92%
✅ Andamento atualizado: 92% → 95%
🏆 Rifa CONCLUÍDA: 95% → 100%
```

---

### **3. 🔄 `recuperar_rifas_erro.py` - RECUPERAÇÃO DE ERROS**

#### **🎯 Função Principal:**
- **Busca rifas com status 'error'**
- **Tenta verificar novamente**
- **Recupera rifas que falharam temporariamente**

#### **🔧 Lógica de Recuperação:**
1. **Identifica rifas** com status 'error'
2. **Tenta acessar** os links novamente
3. **Se sucesso** → Volta status para 'ativo'
4. **Se falha** → Mantém como 'error'

#### **⏰ Execução:**
- **Sempre executada** após verificação principal
- **Automática** pelo agendador inteligente

---

### **4. 📱 `envio_automatico_pdfs_whatsapp.py` - ENVIO DE PDFs**

#### **🎯 Função Principal:**
- **Detecta rifas concluídas** (100%)
- **Gera PDFs automaticamente**
- **Envia via WhatsApp** (se configurado)

#### **🔄 Trigger de Execução:**
- **Executado automaticamente** quando rifas atingem 100%
- **Chamado pelo** agendador após verificações

---

### **5. 🔧 `agendador_servico.py` - SERVIÇO EM BACKGROUND**

#### **🎯 Função Principal:**
- **Executa como serviço** do Windows
- **Mantém o agendador** rodando continuamente
- **Gerencia PID** e status do sistema

#### **📊 Funcionalidades:**
- **Controle de processo** (start/stop/status)
- **Logs de serviço**
- **Recuperação automática** em caso de falha

---

### **6. 🖥️ `gerenciar_agendador.bat` - INTERFACE DE CONTROLE**

#### **🎯 Função Principal:**
- **Interface amigável** para controlar o agendador
- **Menu interativo** com opções

#### **📋 Opções Disponíveis:**
1. **Iniciar** agendador
2. **Parar** agendador
3. **Status** do sistema
4. **Ver logs**
5. **Reiniciar** serviço

---

### **7. 📄 `agendador_status.json` - STATUS DO SISTEMA**

#### **🎯 Função Principal:**
- **Armazena status** atual do agendador
- **Informações de execução**
- **Usado pelo dashboard** para monitoramento

#### **📊 Estrutura:**
```json
{
    "status": "rodando",
    "pid": 25528,
    "ultima_verificacao": "2025-07-10T23:57:24.553",
    "rifas_ativas": 6,
    "proxima_verificacao": "2025-07-10T23:58:24"
}
```

---

### **8. 🔔 `agendador_notifications.json` - NOTIFICAÇÕES**

#### **🎯 Função Principal:**
- **Notificações para dashboard**
- **Comunicação entre agendador e interface web**

#### **📊 Estrutura:**
```json
{
    "ultima_atualizacao": "2025-07-10T23:57:24",
    "mudancas_detectadas": true,
    "rifas_atualizadas": 2,
    "rifas_concluidas": 1
}
```

---

## 🎯 **FLUXO COMPLETO DO SISTEMA**

### **🔄 Sequência de Execução:**

1. **🚀 Inicialização:**
   - `gerenciar_agendador.bat` → `agendador_servico.py` → `agendador_verificacao_rifas.py`

2. **📊 Verificação Inicial:**
   - Executa `verificar_andamento_rifas.py` imediatamente
   - Configura cronograma baseado no estado atual

3. **⏰ Monitoramento Contínuo:**
   - Jobs executam em intervalos dinâmicos
   - Reagendamento automático após cada verificação

4. **🔄 Ciclo de Verificação:**
   ```
   verificar_andamento_rifas.py
   ↓
   recuperar_rifas_erro.py
   ↓
   notificar_dashboard_atualizado()
   ↓
   envio_automatico_pdfs_whatsapp.py
   ↓
   atualizar_cronograma_monitoramento()
   ```

5. **📡 Comunicação:**
   - Dashboard recebe notificações
   - Status atualizado em tempo real
   - Logs detalhados para monitoramento

---

## 🎯 **RESUMO EXECUTIVO**

Este sistema implementa um **monitoramento inteligente e adaptativo** de rifas que:

- **🧠 Pensa** (calcula intervalos baseado no contexto)
- **👀 Observa** (monitora sites em tempo real)
- **🔄 Adapta** (reagenda baseado em mudanças)
- **📡 Comunica** (notifica dashboard e usuários)
- **🛠️ Recupera** (tenta corrigir erros automaticamente)
- **📱 Age** (envia PDFs quando necessário)

**É um sistema completamente autônomo que funciona 24/7 sem intervenção manual!** 🚀
