# 📁 Índice da Pasta Agendador

## 🎯 **Arquivos Principais**

### 🔧 **Core do Sistema:**
- **`agendador_servico.py`** - Serviço principal em background
- **`agendador_verificacao_rifas.py`** - Lógica de monitoramento inteligente

### 🎮 **Controle:**
- **`controlador_agendador.py`** - Controlador Python (alternativa)

## 📚 **Documentação:**

### 📖 **Leitura Obrigatória:**
- **`README.md`** - Documentação completa do sistema
- **`DEPENDENCIAS.md`** - Diagrama de dependências

### 📋 **Este Arquivo:**
- **`INDEX.md`** - Índice da pasta (você está aqui)

## 🚀 **Como Usar:**

### **Interface Principal (Recomendado):**
```bash
# Na raiz do projeto
gerenciar_agendador.bat
```

### **Comandos Rápidos:**
```bash
# Na raiz do projeto
agendador_rapido.bat start
agendador_rapido.bat stop
agendador_rapido.bat status
```

## ⚠️ **Importante:**

### **Antes de Modificar QUALQUER arquivo:**
1. **SEMPRE** leia o `README.md`
2. **SEMPRE** leia o `DEPENDENCIAS.md`
3. **SEMPRE** faça backup
4. **SEMPRE** teste as mudanças

### **Estrutura de Dependências:**
```
gerenciar_agendador.bat (raiz)
    ↓
agendador_servico.py (esta pasta)
    ↓
agendador_verificacao_rifas.py (esta pasta)
    ↓
verificar_andamento_rifas.py (scripts/)
```

## 📊 **Status Atual:**
- ✅ **6 rifas ativas** sendo monitoradas
- ✅ **Verificação a cada 5 minutos**
- ✅ **Dashboard atualizado automaticamente**
- ✅ **Recuperação automática de erros**

## 🔧 **Manutenção:**
- Logs em: `scripts/logs/`
- Status em: `scripts/agendador_status.json`
- PID em: `scripts/agendador.pid`

---

**📞 Suporte:** Em caso de problemas, consulte o `README.md` primeiro! 