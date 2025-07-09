# Sistema de Recuperação de Rifas com Erro

## Visão Geral

O sistema agora possui um mecanismo robusto para recuperar automaticamente rifas que foram marcadas com erro quando os links são corrigidos.

## Como Funciona

### 1. Script Dedicado: `scripts/recuperar_rifas_erro.py`
- Busca APENAS rifas com `status_rifa = 'error'`
- Verifica se o link está funcionando
- Se funcionar, atualiza automaticamente para `status_rifa = 'ativo'`
- Gera logs detalhados em `scripts/logs/recuperar_erro.log`

### 2. Integração com Agendador
O agendador (`scripts/agendador_verificacao_rifas.py`) agora:
- Executa a verificação normal de rifas
- **SEMPRE** executa a recuperação de rifas com erro após cada verificação
- Garante que rifas com links corrigidos sejam recuperadas automaticamente

### 3. Execução Manual
Para forçar a recuperação imediatamente:

```bash
# Windows - usar o arquivo .bat
.\recuperar_rifas_erro.bat

# Ou diretamente via Python
python scripts/forcar_recuperacao_erro.py
```

## Fluxo de Recuperação

1. **Link quebra** → Sistema detecta → `status_rifa = 'error'`
2. **Link é corrigido** pelo usuário
3. **Script de recuperação executa** (automático ou manual)
4. **Verifica o link** → Se funciona → `status_rifa = 'ativo'`
5. **Rifa volta ao normal** no dashboard

## Logs e Monitoramento

### Verificar rifas com erro atuais:
```sql
SELECT * FROM extracoes_cadastro WHERE status_rifa = 'error';
```

### Verificar logs de recuperação:
```bash
# Windows PowerShell
Get-Content scripts/logs/recuperar_erro.log | Select-Object -Last 50
```

## Vantagens da Nova Abordagem

1. **Script dedicado** - Focado apenas em recuperar erros
2. **Execução garantida** - Sempre executa após verificação normal
3. **Logs separados** - Fácil rastreamento de recuperações
4. **Execução manual** - Pode forçar recuperação imediata
5. **Robustez** - Verifica múltiplos indicadores de funcionamento do link

## Manutenção

- O script é executado automaticamente pelo agendador
- Pode ser executado manualmente quando necessário
- Logs são mantidos em `scripts/logs/recuperar_erro.log`
- Não requer configuração adicional

## Resolução de Problemas

Se uma rifa não está sendo recuperada:
1. Verifique se o link realmente funciona no navegador
2. Execute `.\recuperar_rifas_erro.bat` manualmente
3. Verifique os logs em `scripts/logs/recuperar_erro.log`
4. Certifique-se de que o agendador está rodando 