#!/usr/bin/env python3
# backup_banco_agendador.py
"""
Agendador para execução automática de backups diários às 03:13
Executa o script backup_banco_de_dados.py todos os dias no horário configurado.
"""

import schedule
import time
import subprocess
import datetime as dt
import os
from pathlib import Path
from backup_banco_log import backup_logger

def executar_backup():
    """Executa o script de backup e registra o resultado"""
    try:
        backup_logger.log_agendador("INFO", "Iniciando backup agendado...")
        
        # Executa o script de backup
        script_path = Path(__file__).parent / "backup_banco_de_dados.py"
        
        if not script_path.exists():
            backup_logger.log_agendador("ERROR", f"Script de backup não encontrado: {script_path}")
            return
        
        # Executa o backup
        resultado = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            text=True,
            cwd=str(script_path.parent)
        )
        
        if resultado.returncode == 0:
            backup_logger.log_agendador("INFO", "Backup executado com sucesso!")
            if resultado.stdout.strip():
                backup_logger.log_backup("INFO", f"Saída: {resultado.stdout}")
        else:
            backup_logger.log_agendador("ERROR", f"Erro na execução do backup (código {resultado.returncode})")
            if resultado.stderr.strip():
                backup_logger.log_agendador("ERROR", f"Erro: {resultado.stderr}")
            
    except Exception as e:
        backup_logger.log_agendador("ERROR", f"Exceção durante execução do backup: {e}")

def main():
    """Função principal do agendador"""
    backup_logger.log_agendador("INFO", "Iniciando agendador de backup...")
    backup_logger.log_agendador("INFO", "Backup programado para execução diária às 03:13")
    
    print("Agendador de backup iniciado...")
    print("Backup programado para execução diária às 03:13")
    print("Logs salvos em:")
    print(f"   - scripts/andamento/logs/logs_geral_agendador.log")
    print(f"   - logs/backup_banco_de_dados.log")
    
    # Agenda a execução diária às 03:13
    schedule.every().day.at("03:13").do(executar_backup)
    
    # Opcional: executar backup imediatamente para teste (descomente se necessário)
    # backup_logger.log_agendador("INFO", "Executando backup de teste...")
    # executar_backup()
    
    backup_logger.log_agendador("INFO", "Agendador ativo. Aguardando próxima execução...")
    print("Agendador ativo. Use Ctrl+C para parar.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto
            
    except KeyboardInterrupt:
        backup_logger.log_agendador("INFO", "Agendador interrompido pelo usuário")
        print("\nAgendador interrompido pelo usuário")
    except Exception as e:
        backup_logger.log_agendador("ERROR", f"Erro no agendador: {e}")
        print(f"Erro no agendador: {e}")

if __name__ == "__main__":
    main()
