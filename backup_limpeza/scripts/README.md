# Scripts Executáveis

Esta pasta contém scripts que serão executados a partir da página "edições" do sistema.

## Estrutura Recomendada

```
scripts/
├── README.md                    # Este arquivo
├── cadastrar_siglas.py         # Script para cadastrar siglas diárias
├── cadastrar_sigla_avulsa.py   # Script para cadastrar sigla avulsa
├── processar_dados.py          # Script para processar dados
└── utils/                      # Utilitários compartilhados
    ├── __init__.py
    ├── database.py             # Conexão com banco
    └── helpers.py              # Funções auxiliares
```

## Convenções

1. **Nomenclatura**: Use snake_case para nomes de arquivos
2. **Execução**: Scripts devem ser executáveis via Python
3. **Logs**: Sempre incluir logs para rastreamento
4. **Tratamento de Erros**: Implementar try/catch adequado
5. **Configuração**: Usar `config.py` da raiz do projeto

## Exemplo de Script

```python
#!/usr/bin/env python3
"""
Script para cadastrar siglas diárias
Executado a partir da página edições
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import VPS_IP, VPS_PORT
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Iniciando execução do script")
        # Lógica do script aqui
        logger.info("Script executado com sucesso")
    except Exception as e:
        logger.error(f"Erro na execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Integração com o Backend

Os scripts serão chamados pelo backend FastAPI através de endpoints específicos:

- `POST /api/edicoes/executar-script/cadastrar-siglas`
- `POST /api/edicoes/executar-script/cadastrar-sigla-avulsa`

## Segurança

- Validar sempre os parâmetros de entrada
- Usar timeouts para execução
- Implementar controle de acesso se necessário
- Logs de auditoria para todas as execuções 