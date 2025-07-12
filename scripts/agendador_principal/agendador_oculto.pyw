#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agendador Oculto - Executa o agendador principal em modo completamente oculto
Este arquivo .pyw não abre terminal no Windows
Versão corrigida usando subprocess
"""

import os
import sys
import subprocess
from datetime import datetime

# Mudar para o diretório do projeto
project_dir = r"D:\Documentos\Workspace\Gerenciamento"
os.chdir(project_dir)

# Executar o agendador principal
try:
    # Usar subprocess para executar o script de forma mais confiável
    result = subprocess.run([
        sys.executable,
        "scripts/agendador_principal/agendador_desativa_alimenta.py"
    ],
    cwd=project_dir,
    capture_output=False,  # Não capturar output para evitar problemas
    check=True
    )
    
except subprocess.CalledProcessError as e:
    # Log de erro em caso de falha na execução
    try:
        os.makedirs("scripts/logs", exist_ok=True)
        with open("scripts/logs/agendador_oculto_erro.log", "a", encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp} - ERRO EXECUCAO - Código: {e.returncode}\n")
    except:
        pass  # Falha silenciosa se não conseguir escrever log

except Exception as e:
    # Log de erro em caso de falha crítica
    try:
        os.makedirs("scripts/logs", exist_ok=True)
        with open("scripts/logs/agendador_oculto_erro.log", "a", encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp} - ERRO CRITICO - {e}\n")
    except:
        pass  # Falha silenciosa se não conseguir escrever log
