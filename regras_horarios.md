# Regras de Horários - Sistema de Rifas

## Horários Oficiais dos Sorteios

O sistema utiliza os seguintes horários fixos para cada tipo de rifa:

| Sigla | Horário | Descrição |
|-------|---------|-----------|
| **PPT** | 09:20 | Primeira rifa da manhã |
| **PTM** | 11:20 | Rifa do meio da manhã |
| **PT** | 14:20 | Rifa da tarde |
| **PTV** | 16:20 | Rifa da tarde avançada |
| **PTN** | 18:20 | Rifa da noite |
| **FEDERAL** | 19:00 | Rifa federal |
| **CORUJINHA** | 21:30 | Última rifa da noite |

## Regras de Validação de Horários

### 1. Ordem de Especificidade das Siglas

Para evitar confusão na identificação das siglas, o sistema verifica na seguinte ordem (mais específicas primeiro):

1. **CORUJINHA** - Mais específica
2. **FEDERAL** - Mais específica  
3. **PPT** - Mais específica
4. **PTV** - Mais específica que PT
5. **PTN** - Mais específica que PT
6. **PTM** - Mais específica que PT
7. **PT** - Menos específica (verificada por último)

**Exemplo:** 
- `PT ESPECIAL` → `PT`
- `PTV EXTRA` → `PTV` (não PT)
- `PPT EXTRA` → `PPT` (não PT)



### Estrutura de Dados
```python
siglas_horarios = {
    'PPT': time(9, 20),     # 09:20
    'PTM': time(11, 20),    # 11:20
    'PT': time(14, 20),     # 14:20
    'PTV': time(16, 20),    # 16:20
    'PTN': time(18, 20),    # 18:20
    'FEDERAL': time(19, 0), # 19:00
    'CORUJINHA': time(21, 30) # 21:30
}
`
