#!/usr/bin/env python3
"""
Script para atualizar configuração após migração bem-sucedida
"""

import os
import shutil
from datetime import datetime

def atualizar_configuracao():
    """Atualiza a configuração para o novo servidor"""
    
    # Backup da configuração atual
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"config_backup_{timestamp}.py"
    
    if os.path.exists("config.py"):
        shutil.copy("config.py", backup_file)
        print(f"✅ Backup da configuração salvo: {backup_file}")
    
    # Nova configuração
    nova_config = f"""# Configuração do banco de dados - MIGRADO PARA NOVO SERVIDOR
# Data da migração: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

DB_CONFIG = {{
    'host': 'pma.linksystems.com.br',  # NOVO SERVIDOR
    'user': 'adseg',
    'password': 'Define@4536#8521',
    'port': 3306
}}

# Configurações adicionais
DEBUG = True
LOG_LEVEL = 'INFO'

# Configurações do servidor
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8001
"""
    
    # Salvar nova configuração
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(nova_config)
    
    print("✅ Configuração atualizada para o novo servidor")
    print("⚠️  IMPORTANTE: Teste a conexão antes de usar em produção")

if __name__ == "__main__":
    print("Atualizando configuração para novo servidor...")
    atualizar_configuracao()
    print("Concluído!")
