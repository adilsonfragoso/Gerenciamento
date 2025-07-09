#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agendador Principal Melhorado
Sistema de agendamento de tarefas para o sistema de gerenciamento de rifas.
"""

import schedule
import time
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configuração de logging
def setup_logging():
    """Configura o sistema de logging"""
    log_dir = Path("scripts/logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "agendador_principal.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def rodar_desativa_concluidas_v4():
    """Executa o script desativa_concluidas_v4.py com tratamento de erros"""
    try:
        logger.info("Iniciando execução: desativa_concluidas_v4.py")
        script_path = "scripts/desativa_concluidas_v4.py"
        
        if not os.path.exists(script_path):
            logger.error(f"Script não encontrado: {script_path}")
            return False
        
        result = os.system(f"python {script_path}")
        
        if result == 0:
            logger.info("desativa_concluidas_v4.py executado com sucesso")
            return True
        else:
            logger.error(f"Erro na execução de desativa_concluidas_v4.py (código: {result})")
            return False
            
    except Exception as e:
        logger.error(f"Exceção ao executar desativa_concluidas_v4.py: {e}")
        return False

def rodar_alimenta_premiados():
    """Executa o script alimenta_premiados.py com tratamento de erros"""
    try:
        logger.info("Iniciando execução: alimenta_premiados.py")
        script_path = "alimenta_premiados.py"
        
        if not os.path.exists(script_path):
            logger.error(f"Script não encontrado: {script_path}")
            return False
        
        result = os.system(f"python {script_path}")
        
        if result == 0:
            logger.info("alimenta_premiados.py executado com sucesso")
            return True
        else:
            logger.error(f"Erro na execução de alimenta_premiados.py (código: {result})")
            return False
            
    except Exception as e:
        logger.error(f"Exceção ao executar alimenta_premiados.py: {e}")
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
    logger.info("Configurando agendamentos...")
    
    # Mapear os dias da semana
    DIA = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    # Horários para cada caso
    horarios_padrao = ["10:00", "11:00", "12:00", "15:00", "17:00", "19:00", "22:00"]
    horarios_dias_federal = ["10:00", "11:00", "12:00", "15:00", "17:00", "19:30", "22:00"]
    horarios_domingo = ["10:00", "11:00", "12:00", "15:00", "17:00"]
    
    total_agendamentos = 0
    
    for i, dia in enumerate(DIA):
        logger.info(f"Configurando agendamentos para {dia}")
        
        if dia == "wednesday" or dia == "saturday":
            # Dias de federal (quarta e sábado)
            for h in horarios_dias_federal:
                getattr(schedule.every(), dia).at(h).do(rodar_desativa_concluidas_v4)
                total_agendamentos += 1
                logger.debug(f"   Agendado: {dia} às {h} - desativa_concluidas_v4")
            
            for h in horarios_menos_10min(horarios_dias_federal):
                getattr(schedule.every(), dia).at(h).do(rodar_alimenta_premiados)
                total_agendamentos += 1
                logger.debug(f"   Agendado: {dia} às {h} - alimenta_premiados")
                
        elif dia == "sunday":
            # Domingo
            for h in horarios_domingo:
                getattr(schedule.every(), dia).at(h).do(rodar_desativa_concluidas_v4)
                total_agendamentos += 1
                logger.debug(f"   Agendado: {dia} às {h} - desativa_concluidas_v4")
            
            for h in horarios_menos_10min(horarios_domingo):
                getattr(schedule.every(), dia).at(h).do(rodar_alimenta_premiados)
                total_agendamentos += 1
                logger.debug(f"   Agendado: {dia} às {h} - alimenta_premiados")
                
        else:
            # Dias normais
            for h in horarios_padrao:
                getattr(schedule.every(), dia).at(h).do(rodar_desativa_concluidas_v4)
                total_agendamentos += 1
                logger.debug(f"   Agendado: {dia} às {h} - desativa_concluidas_v4")
            
            for h in horarios_menos_10min(horarios_padrao):
                getattr(schedule.every(), dia).at(h).do(rodar_alimenta_premiados)
                total_agendamentos += 1
                logger.debug(f"   Agendado: {dia} às {h} - alimenta_premiados")
    
    logger.info(f"Total de {total_agendamentos} agendamentos configurados")
    return total_agendamentos

def mostrar_proximo_agendamento():
    """Mostra o próximo agendamento programado"""
    jobs = schedule.get_jobs()
    if jobs:
        logger.info(f"Total de {len(jobs)} agendamentos ativos")
        # Mostrar apenas o primeiro job como exemplo
        first_job = jobs[0]
        if first_job.next_run:
            logger.info(f"Exemplo de agendamento: {first_job} às {first_job.next_run}")
        else:
            logger.info(f"Exemplo de agendamento: {first_job} (sem horário definido)")
    else:
        logger.warning("Nenhum agendamento encontrado")

def main():
    """Função principal do agendador"""
    logger.info("Iniciando Agendador Principal")
    logger.info("=" * 50)
    
    try:
        # Configurar agendamentos
        total = configurar_agendamentos()
        
        if total == 0:
            logger.error("Nenhum agendamento foi configurado. Encerrando...")
            return
        
        # Mostrar próximo agendamento
        mostrar_proximo_agendamento()
        
        logger.info("Agendador iniciado. Aguardando execução dos agendamentos...")
        logger.info("Pressione Ctrl+C para parar o agendador")
        
        # Loop principal
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Agendador interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro crítico no agendador: {e}")
    finally:
        logger.info("Agendador encerrado")

if __name__ == "__main__":
    main() 