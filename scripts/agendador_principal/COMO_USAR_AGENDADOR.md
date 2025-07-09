# 🚀 Como Usar o Agendador

## 📋 Arquivos Essenciais

- **`agendador_principal.py`** - Agendador original
- **`agendador_principal_melhorado.py`** - Agendador com logs (recomendado)
- **`agendador_startup.bat`** - Script para startup automático
- **`configurar_startup.bat`** - Configurador do startup

## 🎯 Configuração Rápida

### **1. Configurar Startup Automático:**
```cmd
scripts\agendador_principal\configurar_startup.bat
```
Escolha a opção **1** - "Adicionar ao Startup do Usuário"

### **2. Executar Manualmente (se necessário):**
```cmd
# Agendador original
python scripts\agendador_principal\agendador_principal.py

# Agendador melhorado (com logs)
python scripts\agendador_principal\agendador_principal_melhorado.py
```

## 📊 Monitoramento

- **Logs do agendador:** `scripts\logs\agendador_principal.log`
- **Logs do startup:** `scripts\logs\agendador_startup.log`

## ✅ Resultado

Depois de configurar, o agendador **iniciará automaticamente** quando você ligar o computador e executará:
- `desativa_concluidas_v4.py` - nos horários programados
- `alimenta_premiados.py` - 10 minutos antes dos horários principais

**Pronto! Não precisa fazer mais nada.** 🎉 