# Erro DB config

## Problema

Ao tentar importar o DB_CONFIG em scripts Python, pode ocorrer o erro:

```
Import "db_config" could not be resolved
```

Ou:

```
ModuleNotFoundError: No module named 'db_config'
```

Isso acontece porque o Python não encontra o módulo `db_config` se o caminho do sys.path não estiver corretamente configurado para a raiz do projeto.

## Exemplo de erro

```python
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))
from db_config import DB_CONFIG  # ERRO!
```

## Solução

Adicione a raiz do projeto ao sys.path e faça o import usando o caminho completo do módulo:

```python
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db_config import DB_CONFIG
```

Assim, o Python encontra corretamente o módulo `app.db_config` em qualquer script do projeto.

---

**Dica:** Sempre padronize os imports de configuração para evitar esse tipo de erro em scripts futuros. 