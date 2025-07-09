# Sistema de Envio Automático de PDFs para WhatsApp

## Visão Geral

Sistema automático que **envia PDFs de relatórios finais** para grupos do WhatsApp quando as rifas atingem 100% e os PDFs ficam disponíveis. Baseado no script `novo_chamadas_group_latest.py` e integrado ao sistema de sincronização existente.

## Funcionalidades

### ✅ O que foi implementado

1. **Detecção Automática**: Identifica rifas com 100% + PDF disponível
2. **Envio Duplo**: Primeira mensagem com imagem + texto, segunda com PDF
3. **Controle de Status**: Evita envios duplicados
4. **Integração Total**: Funciona com agendador e scripts existentes
5. **Logs Detalhados**: Monitoramento completo do processo
6. **API Endpoint**: Execução manual via interface

### 📱 Fluxo de Envio

Quando uma rifa atinge 100%:
```
1. Rifa detectada como concluída (100%)
2. Sistema verifica se PDF existe na pasta downloads/
3. Se existe PDF + status != 'enviado':
   → Envia imagem + texto informativo
   → Aguarda 2 segundos  
   → Envia arquivo PDF
   → Marca como 'enviado'
```

## Arquivos do Sistema

### Script Principal
**`scripts/envio_automatico_pdfs_whatsapp.py`**
- Baseado em `novo_chamadas_group_latest.py`
- Mantém mesma API Key e configurações de grupo
- Novo texto específico para PDFs finais
- Busca inteligente de PDFs por nome de arquivo

### Integração Existente
**`scripts/verificar_andamento_rifas.py`**
- Executa envio automático quando detecta rifas concluídas
- Logs integrados ao sistema existente

**`scripts/agendador_verificacao_rifas.py`**
- Verificação contínua de PDFs pendentes
- Execução a cada ciclo do agendador

**`app/main.py`**
- Endpoint: `POST /api/scripts/envio-automatico-pdfs-whatsapp`
- Execução manual via API

## Configuração

### Grupos do WhatsApp
```python
# Mantém a mesma configuração do script original
#id_grupo = "120363307707983386@g.us"  # grupo links
id_grupo = "5512997650505-1562805682@g.us"  # grupo anotações
```
✅ **Sem alteração necessária** - usa a configuração que já funciona

### Caminhos
```python
caminho_imagens = r"D:\Documentos\Workspace\Gerenciamento\uploads"
caminho_pdfs = r"D:\Documentos\Workspace\Gerenciamento\downloads"  # Pasta dos PDFs
```

### Status no Banco
Nova coluna criada automaticamente:
```sql
ALTER TABLE extracoes_cadastro 
ADD COLUMN status_envio_pdf_whatsapp VARCHAR(20) DEFAULT 'pendente'
```

**Estados possíveis:**
- `pendente` - PDF pode ser enviado
- `enviando` - Envio em andamento  
- `enviado` - PDF já foi enviado
- `erro` - Falha no envio

## Mensagem Enviada

### 1. Imagem + Texto Informativo
```
📊 RELATÓRIO FINAL - PPT 📊

🎯 Edição: 6199
✅ Resultado oficial disponível!

🔗 Link da campanha:
https://litoraldasorte.com/campanha/ppt-rj-edicao-6199

📄 Segue o relatório em anexo 📎

📅 Gerado em: 23/06/2025 às 22:44

🏆 PARABÉNS AOS GANHADORES! 🎉
```

### 2. Arquivo PDF
- Nome: `Relatório_PPT_6199.pdf`
- Tipo: document/pdf
- Conteúdo: PDF completo do relatório

## Como Usar

### Modo Automático (Recomendado)
O sistema funciona **automaticamente** quando:
- [Agendador inteligente está rodando][[memory:20860880843242208]]
- Script de verificação detecta rifa 100%
- PDF está disponível na pasta downloads/
- Status ≠ 'enviado'

### Modo Manual
```bash
# Executar diretamente
python scripts/envio_automatico_pdfs_whatsapp.py

# Via API
curl -X POST http://localhost:8001/api/scripts/envio-automatico-pdfs-whatsapp
```

### Via Dashboard
Em breve será adicionado botão no dashboard para execução manual.

## Busca Inteligente de PDFs

O sistema busca PDFs usando múltiplos padrões:
```python
padroes = [
    f"relatorio_{edicao}.pdf",
    f"relatorio_{sigla_oficial}_{edicao}.pdf", 
    f"{sigla_oficial}_{edicao}.pdf",
    f"edicao_{edicao}.pdf"
]
```

**Busca genérica:** Qualquer PDF que contenha o número da edição no nome.

## Logs e Monitoramento

### Arquivo de Log
**`scripts/logs/envio_pdfs_whatsapp.log`**

### Logs Principais
```
=== Iniciando Envio Automático de PDFs para WhatsApp ===
Encontradas 2 rifas com PDF para enviar
Processando edição 6199 - PPT
✅ PDF da edição 6199 enviado com sucesso!
📱 2 PDF(s) enviado(s) automaticamente para WhatsApp
```

### No Script de Verificação
```
📄 2 rifa(s) concluída(s)! Verificando envio automático de PDFs...
🚀 Executando script de envio automático de PDFs...
✅ Script de envio automático de PDFs executado com sucesso
```

### No Agendador
```
📄 Executando verificação de envio automático de PDFs...
📱 1 PDF(s) enviado(s) automaticamente para WhatsApp
```

## Estados do Sistema

### Fluxo Normal
```
Rifa 0% → 50% → 100% → PDF gerado → PDF enviado → Status 'enviado'
```

### Recuperação de Falhas
```
Status 'erro' → Retry automático no próximo ciclo → Sucesso → 'enviado'
```

### Prevenção de Duplicatas
```
Status 'enviado' → PDF ignorado em verificações futuras
```

## Vantagens da Implementação

### ✅ Baseado no Script Funcionante
- Mesma API, mesma autenticação
- Mesmo grupo configurado
- Zero mudanças na infraestrutura existente

### ✅ Integração Perfeita  
- Funciona com agendador inteligente
- Sincronização automática com dashboard
- Logs integrados ao sistema

### ✅ Controle Total
- Evita envios duplicados
- Status detalhado no banco
- Recuperação automática de falhas

### ✅ Flexibilidade
- Execução automática E manual
- Busca inteligente de arquivos
- Fallback para texto se não houver imagem

## Exemplo de Uso Completo

### Cenário: Rifa PPT atinge 100%

1. **Agendador detecta**: PPT 6199 = 100%
2. **Script atualiza**: status_rifa = 'concluído' 
3. **Dashboard sincroniza**: Mostra ícone PDF disponível
4. **PDF gerado**: Arquivo aparece em downloads/
5. **Envio automático**: 
   - Verifica status_envio_pdf_whatsapp = 'pendente'
   - Envia imagem + texto para grupo
   - Envia PDF para grupo  
   - Atualiza status = 'enviado'
6. **Resultado**: Grupo recebe notificação completa automaticamente!

## Monitoramento de Funcionamento

### Verificar se está funcionando
```bash
# Ver logs do envio
tail -f scripts/logs/envio_pdfs_whatsapp.log

# Ver logs do agendador  
tail -f scripts/logs/agendador_rifas.log

# Verificar status no banco
SELECT edicao, sigla_oficial, status_rifa, status_envio_pdf_whatsapp 
FROM extracoes_cadastro 
WHERE status_rifa = 'concluído'
ORDER BY edicao DESC;
```

### Forçar envio manual
```bash
# Se algum PDF não foi enviado automaticamente
python scripts/envio_automatico_pdfs_whatsapp.py
```

## Troubleshooting

### PDF não enviado?
1. Verificar se arquivo existe em downloads/
2. Verificar status_envio_pdf_whatsapp no banco
3. Verificar logs em envio_pdfs_whatsapp.log
4. Executar manualmente para ver erro específico

### API WhatsApp com erro?
- Mesma configuração do script original
- Se original funciona, este também deve funcionar
- Verificar API Key e configuração de grupo

### Status travado em 'enviando'?
```sql
-- Resetar status para retry
UPDATE extracoes_cadastro 
SET status_envio_pdf_whatsapp = 'pendente' 
WHERE status_envio_pdf_whatsapp = 'enviando'
```

## Conclusão

O sistema está **totalmente integrado** e funciona automaticamente. Quando uma rifa chega a 100% e o PDF fica disponível, o grupo do WhatsApp recebe:

1. **Imagem da rifa** + texto comemorativo
2. **Arquivo PDF** do relatório final

Tudo isso **sem intervenção manual**, mantendo a mesma infraestrutura que já funciona perfeitamente! 🚀📱 