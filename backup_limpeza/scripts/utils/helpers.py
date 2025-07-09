"""
Funções auxiliares compartilhadas para scripts
"""

import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def validar_data(data_str: str) -> bool:
    """
    Valida se uma string representa uma data válida no formato YYYY-MM-DD
    
    Args:
        data_str (str): String da data
        
    Returns:
        bool: True se válida, False caso contrário
    """
    try:
        datetime.strptime(data_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validar_sigla(sigla: str) -> bool:
    """
    Valida se uma sigla é válida
    
    Args:
        sigla (str): Sigla a ser validada
        
    Returns:
        bool: True se válida, False caso contrário
    """
    if not sigla or not isinstance(sigla, str):
        return False
    
    # Remover espaços e converter para maiúsculas
    sigla_limpa = sigla.strip().upper()
    
    # Verificar se tem pelo menos 2 caracteres
    if len(sigla_limpa) < 2:
        return False
    
    # Verificar se contém apenas letras, números e underscore
    import re
    if not re.match(r'^[A-Z0-9_]+$', sigla_limpa):
        return False
    
    return True

def limpar_sigla(sigla: str) -> str:
    """
    Limpa e padroniza uma sigla
    
    Args:
        sigla (str): Sigla original
        
    Returns:
        str: Sigla limpa e padronizada
    """
    if not sigla:
        return ""
    
    # Remover espaços e converter para maiúsculas
    sigla_limpa = sigla.strip().upper()
    
    # Remover caracteres especiais (manter apenas letras, números e underscore)
    import re
    sigla_limpa = re.sub(r'[^A-Z0-9_]', '', sigla_limpa)
    
    return sigla_limpa

def formatar_resposta(success: bool, message: str, data: Any = None) -> Dict[str, Any]:
    """
    Formata resposta padrão para scripts
    
    Args:
        success (bool): Se a operação foi bem-sucedida
        message (str): Mensagem descritiva
        data (Any): Dados adicionais
        
    Returns:
        Dict[str, Any]: Resposta formatada
    """
    return {
        "success": success,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

def log_execucao(script_name: str, params: Dict[str, Any], resultado: Dict[str, Any]):
    """
    Registra log de execução de script
    
    Args:
        script_name (str): Nome do script
        params (Dict[str, Any]): Parâmetros de entrada
        resultado (Dict[str, Any]): Resultado da execução
    """
    logger.info(f"Execução do script {script_name}")
    logger.info(f"Parâmetros: {params}")
    logger.info(f"Resultado: {resultado['success']} - {resultado['message']}")
    
    if not resultado['success']:
        logger.error(f"Falha na execução: {resultado['message']}")

def obter_dia_semana(data_str: str) -> str:
    """
    Obtém o dia da semana em português
    
    Args:
        data_str (str): Data no formato YYYY-MM-DD
        
    Returns:
        str: Dia da semana em português
    """
    try:
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        dias = {
            0: 'segunda',
            1: 'terça', 
            2: 'quarta',
            3: 'quinta',
            4: 'sexta',
            5: 'sábado',
            6: 'domingo'
        }
        return dias[data_obj.weekday()]
    except ValueError:
        return ""

def determinar_grupo_dia(dia_semana: str) -> int:
    """
    Determina o grupo do dia da semana
    
    Args:
        dia_semana (str): Dia da semana
        
    Returns:
        int: Número do grupo (1, 2 ou 3)
    """
    grupo1 = ['segunda', 'terça', 'quinta', 'sexta']
    grupo2 = ['quarta', 'sábado']
    grupo3 = ['domingo']
    
    if dia_semana.lower() in grupo1:
        return 1
    elif dia_semana.lower() in grupo2:
        return 2
    elif dia_semana.lower() in grupo3:
        return 3
    else:
        return 0 