"""
Configurações centralizadas do servidor
"""

# Configurações do servidor
SERVER_CONFIG = {
    "host": "0.0.0.0",  # Permite acesso de qualquer IP da rede
    "port": 8001,       # Porta fixa 8001
    "reload": True,     # Recarrega automaticamente em desenvolvimento
    "log_level": "info"
}

# Configurações de desenvolvimento
DEV_CONFIG = {
    "debug": True,
    "reload": True
}

# Configurações de produção
PROD_CONFIG = {
    "debug": False,
    "reload": False,
    "workers": 4
}

def get_server_config(environment="dev"):
    """
    Retorna as configurações do servidor baseado no ambiente
    
    Args:
        environment (str): Ambiente de execução ('dev' ou 'prod')
    
    Returns:
        dict: Configurações do servidor
    """
    config = SERVER_CONFIG.copy()
    
    if environment == "prod":
        config.update(PROD_CONFIG)
    else:
        config.update(DEV_CONFIG)
    
    return config 