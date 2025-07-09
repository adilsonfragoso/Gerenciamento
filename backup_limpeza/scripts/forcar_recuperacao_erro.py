#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para forçar recuperação de rifas com erro
Pode ser executado manualmente ou via cron/agendador de tarefas
"""

import sys
import os

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.recuperar_rifas_erro import main as recuperar_rifas

if __name__ == "__main__":
    print("🔄 Forçando recuperação de rifas com erro...")
    recuperar_rifas()
    print("✅ Processo concluído!") 