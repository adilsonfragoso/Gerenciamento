#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agendador Desativa e Alimenta
Sistema de agendamento de tarefas para desativar rifas concluídas e alimentar premiações.
"""

import schedule
import time
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configuração de logging (modo oculto)
def setup_logging():
    """Configura o sistema de logging para modo oculto"""
    log_dir = Path("scripts/logs")
    log_dir.mkdir(exist_ok=True)

    # Configurar apenas arquivo de log, sem output no console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "agendador_desativa_alimenta.log", encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def rodar_desativa_concluidas_v4():
    """Executa o script desativa_concluidas_v4.py em modo oculto"""
    try:
        script_path = "scripts/desativa_concluidas_v4.py"

        if not os.path.exists(script_path):
            logger.error(f"ERRO - Script não encontrado: {script_path}")
            return False

        # Executar o script
        result = os.system(f"python {script_path}")

        if result == 0:
            logger.info("SUCESSO - desativa_concluidas_v4.py executado com sucesso")
            return True
        else:
            logger.error(f"ERRO - desativa_concluidas_v4.py falhou (código: {result})")
            return False

    except Exception as e:
        logger.error(f"ERRO - Exceção em desativa_concluidas_v4.py: {e}")
        return False

def rodar_alimenta_premiados():
    """Executa o script alimenta_premiados.py em modo oculto"""
    try:
        script_path = r"D:\\Documentos\Workspace\\Gerenciamento\\scripts\\alimenta_premiados.py"

        if not os.path.exists(script_path):
            logger.error(f"ERRO - Script não encontrado: {script_path}")
            return False

        # Executar o script (sem redirecionamento que pode causar problemas)
        result = os.system(f'python "{script_path}"')

        if result == 0:
            logger.info("SUCESSO - alimenta_premiados.py executado com sucesso")
            return True
        else:
            logger.error(f"ERRO - alimenta_premiados.py falhou (código: {result})")
            return False

    except Exception as e:
        logger.error(f"ERRO - Exceção em alimenta_premiados.py: {e}")
        return False

def horarios_menos_10min(lista_horarios):
    """Calcula horários 10 minutos antes dos horários fornecidos"""
    novos = []
    for h in lista_horarios:
        try:
            t = datetime.strptime(h, "%H:%M") - timedelta(minutes=10)
            novos.append(t.strftime("%H:%M"))
        except ValueError as e:
            logger.error(f"Erro ao processar horário {h}: {e}")
    return novos

def configurar_agendamentos():
    """Configura todos os agendamentos do sistema"""
    # Mapear os dias da semana
    DIA = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    # Horários para cada caso
    horarios_padrao = ["10:00", "11:00", "12:00", "15:00", "17:00", "19:00", "22:00"]
    horarios_dias_federal = ["10:00", "11:00", "12:00", "15:00", "17:00", "19:30", "22:00"]
    horarios_domingo = ["10:00", "11:00", "12:00", "15:00", "17:00"]

    total_agendamentos = 0

    for dia in DIA:
        if dia == "wednesday" or dia == "saturday":
            # Dias de federal (quarta e sábado)
            for h in horarios_dias_federal:
                getattr(schedule.every(), dia).at(h).do(rodar_desativa_concluidas_v4)
                total_agendamentos += 1

            for h in horarios_menos_10min(horarios_dias_federal):
                getattr(schedule.every(), dia).at(h).do(rodar_alimenta_premiados)
                total_agendamentos += 1

        elif dia == "sunday":
            # Domingo
            for h in horarios_domingo:
                getattr(schedule.every(), dia).at(h).do(rodar_desativa_concluidas_v4)
                total_agendamentos += 1

            for h in horarios_menos_10min(horarios_domingo):
                getattr(schedule.every(), dia).at(h).do(rodar_alimenta_premiados)
                total_agendamentos += 1

        else:
            # Dias normais
            for h in horarios_padrao:
                getattr(schedule.every(), dia).at(h).do(rodar_desativa_concluidas_v4)
                total_agendamentos += 1

            for h in horarios_menos_10min(horarios_padrao):
                getattr(schedule.every(), dia).at(h).do(rodar_alimenta_premiados)
                total_agendamentos += 1

    logger.info(f"AGENDAMENTOS - {total_agendamentos} tarefas configuradas")
    return total_agendamentos

def executar_tarefas_iniciais():
    """Executa todas as tarefas imediatamente na primeira execução"""
    logger.info("INICIO - Execução inicial do agendador")

    # Executar desativa_concluidas_v4
    sucesso_desativa = rodar_desativa_concluidas_v4()

    # Aguardar 3 minutos entre as execuções
    logger.info("AGUARDANDO - 3 minutos antes do próximo script")
    time.sleep(180)  # 3 minutos = 180 segundos

    # Executar alimenta_premiados
    sucesso_alimenta = rodar_alimenta_premiados()

    # Log final da execução inicial
    if sucesso_desativa and sucesso_alimenta:
        logger.info("CONCLUIDO - Execução inicial bem-sucedida")
    else:
        logger.error("CONCLUIDO - Execução inicial com falhas")

    logger.info("AGENDADOR - Iniciando agendamentos regulares")

def main():
    """Função principal do agendador em modo oculto"""
    logger.info("INICIO - Agendador Desativa e Alimenta iniciado")

    try:
        # EXECUÇÃO INICIAL: Executar todas as tarefas imediatamente
        executar_tarefas_iniciais()

        # Configurar agendamentos
        total = configurar_agendamentos()

        if total == 0:
            logger.error("ERRO - Nenhum agendamento configurado")
            return

        logger.info("RODANDO - Agendador em execução (modo oculto)")

        # Loop principal (sem output no console)
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto

    except KeyboardInterrupt:
        logger.info("PARADO - Agendador interrompido")
    except Exception as e:
        logger.error(f"ERRO CRITICO - {e}")
    finally:
        logger.info("ENCERRADO - Agendador finalizado")

if __name__ == "__main__":
    main()
