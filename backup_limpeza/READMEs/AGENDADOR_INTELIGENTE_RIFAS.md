# 🤖 Agendador Inteligente de Rifas

## 📋 Visão Geral

Sistema de monitoramento automático que verifica o andamento das rifas com **intervalos dinâmicos** baseados em:
- **Percentual de andamento** (80% = 3min, 90% = 1min)
- **Proximidade do horário de fechamento** (15min antes = 1min)
- **Intervalo padrão** de 5 minutos

## ⚡ Intervalos de Monitoramento

### 🕐 Regras de Intervalo

| Condição | Intervalo | Motivo |
|----------|-----------|--------|
| **Padrão** | 5 minutos | Monitoramento normal |
| **80%+ de andamento** | 3 minutos | Rifa próxima do fim |
| **90%+ de andamento** | 1 minuto | Rifa quase finalizada |
| **15min antes do fechamento** | 1 minuto | Próximo do horário limite |

### 📅 Horários de Fechamento

| Sigla | Horário | Exemplo |
|-------|---------|---------|
| **PPT** | 09:20 | PPT, PPT EXTRA, PPT ESPECIAL |
| **PTM** | 11:20 | PTM, PTM EXTRA, PTM ESPECIAL |
| **PT** | 14:20 | PT, PT EXTRA, PT ESPECIAL |
| **PTV** | 16:20 | PTV, PTV EXTRA, PTV ESPECIAL |
| **PTN** | 18:20 | PTN, PTN EXTRA, PTN ESPECIAL |
| **FEDERAL** | 19:00 | FEDERAL, FEDERAL EXTRA |
| **CORUJINHA** | 21:30 | CORUJINHA, CORUJINHA EXTRA |

## 🚀 Como Usar

### Método 1: Arquivo Batch (Recomendado)
```batch
# Clique duplo no arquivo:
iniciar_agendador_rifas.bat
```

### Método 2: Python Direto
```bash
python scripts/iniciar_agendador.py
```

### Método 3: Agendador Direto
```bash
python scripts/agendador_verificacao_rifas.py
```

## 📊 Funcionamento Inteligente

### Exemplo Prático

**Cenário:** Temos 4 rifas ativas:
- PPT (Edição 6197): 8% - fecha às 09:20
- PT ESPECIAL (Edição 6198): 0% - fecha às 14:20
- PTM (Edição 6199): 85% - fecha às 11:20
- PTV (Edição 6200): 95% - fecha às 16:20

**Intervalos Aplicados:**
- **PPT**: 5 minutos (percentual baixo, longe do fechamento)
- **PT ESPECIAL**: 5 minutos (percentual baixo, longe do fechamento)
- **PTM**: 3 minutos (85% = acima de 80%)
- **PTV**: 1 minuto (95% = acima de 90%)

**Se for 09:05 (15min antes do PPT):**
- **PPT**: 1 minuto (próximo do fechamento - prioridade máxima)
- **PT ESPECIAL**: 5 minutos (mantém intervalo normal)
- **PTM**: 3 minutos (mantém por percentual)
- **PTV**: 1 minuto (mantém por percentual)

## 🔄 Fluxo de Execução

1. **Verificação Inicial**
   - Busca rifas com `status_rifa = 'ativo'`
   - Calcula intervalos para cada rifa
   - Exibe cronograma de monitoramento

2. **Monitoramento Contínuo**
   - Executa verificações nos intervalos calculados
   - Atualiza percentuais no banco
   - Recalcula intervalos após cada verificação

3. **Atualizações Automáticas**
   - **0%**: Preenche campos vazios
   - **1-99%**: Atualiza normalmente
   - **100%**: Marca como "concluído"
   - **Erro**: Marca como "error"

## 📝 Logs e Monitoramento

### Arquivos de Log
- **Principal**: `scripts/logs/agendador_rifas.log`
- **Verificações**: `scripts/logs/verificar_andamento.log`

### Informações Registradas
- Cronograma de monitoramento
- Rifas processadas em cada execução
- Mudanças de percentual
- Rifas concluídas (100%)
- Erros encontrados

## 🛠️ Dependências

```bash
pip install schedule pymysql selenium
```

## ⚙️ Configuração

### Banco de Dados
```python
DB_CONFIG = {
    'host': 'pma.megatrends.site',
    'user': 'root',
    'password': 'Define@4536#8521',
    'database': 'litoral',
    'charset': 'utf8mb4'
}
```

### Intervalos (Personalizáveis)
```python
INTERVALO_PADRAO = 5  # minutos
INTERVALO_80_PERCENT = 3  # minutos
INTERVALO_90_PERCENT = 1  # minuto
INTERVALO_PROXIMO_FECHAMENTO = 1  # minuto
MINUTOS_ANTES_FECHAMENTO = 15  # minutos
```

## 🎯 Vantagens

### ✅ Eficiência
- **Monitoramento inteligente**: Não desperdiça recursos
- **Intervalos dinâmicos**: Intensifica quando necessário
- **Processamento otimizado**: Apenas rifas ativas

### ✅ Precisão
- **Detecção de 100%**: Marca automaticamente como concluído
- **Gestão de erros**: Identifica e marca problemas
- **Proximidade de fechamento**: Monitora intensivamente nos momentos críticos

### ✅ Automação
- **Zero intervenção**: Funciona 24/7
- **Auto-reagendamento**: Ajusta intervalos automaticamente
- **Logs detalhados**: Rastreamento completo

## 🔧 Troubleshooting

### Problema: Agendador não inicia
**Solução**: Verificar dependências
```bash
pip install schedule pymysql selenium
```

### Problema: Erro de conexão com banco
**Solução**: Verificar configuração em `DB_CONFIG`

### Problema: Chrome não encontrado
**Solução**: Instalar ChromeDriver ou usar modo headless

## 📈 Próximos Passos

1. **Interface Web**: Dashboard de monitoramento em tempo real
2. **Notificações**: Alertas quando rifas chegam a 90% ou 100%
3. **Relatórios**: Estatísticas de performance e tempo de fechamento
4. **Backup**: Sistema de backup automático dos logs

---

## 🎉 Status Final

✅ **Sistema 100% Funcional**
- Agendador inteligente implementado
- Intervalos dinâmicos funcionando
- Monitoramento automático ativo
- Logs detalhados configurados
- Scripts de inicialização prontos

**O sistema está pronto para monitoramento contínuo das rifas!** 🚀 