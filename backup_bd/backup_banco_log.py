# backup_banco_log.py
"""
Sistema de logging unificado para o backup do banco de dados.
Registra no sistema geral de logs seguindo o padrão do projeto.
"""

import logging
import datetime as dt
from pathlib import Path

class BackupBancoLogger:
    def __init__(self):
        # Configura diretório de logs seguindo estrutura do projeto
        self.logs_dir = Path("../scripts/andamento/logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivo de log geral do agendador (como especificado nas instruções)
        self.log_geral = self.logs_dir / "logs_geral_agendador.log"
        
        # Arquivo de log específico do backup
        self.log_backup = Path("../logs/backup_banco_de_dados.log")
        self.log_backup.parent.mkdir(exist_ok=True)
        
        self.setup_logging()
    
    def setup_logging(self):
        """Configura o sistema de logging"""
        
        # Logger para logs gerais (agendador)
        self.logger_geral = logging.getLogger('backup_agendador')
        self.logger_geral.setLevel(logging.INFO)
        
        # Handler para logs_geral_agendador.log
        handler_geral = logging.FileHandler(self.log_geral, encoding='utf-8')
        formatter_geral = logging.Formatter(
            '%(asctime)s - [AGENDADOR_BACKUP] - %(levelname)s - %(message)s'
        )
        handler_geral.setFormatter(formatter_geral)
        
        if not self.logger_geral.handlers:
            self.logger_geral.addHandler(handler_geral)
        
        # Logger para logs específicos do backup
        self.logger_backup = logging.getLogger('backup_dados')
        self.logger_backup.setLevel(logging.INFO)
        
        # Handler para backup_banco_de_dados.log
        handler_backup = logging.FileHandler(self.log_backup, encoding='utf-8')
        formatter_backup = logging.Formatter(
            '%(asctime)s - [BACKUP_BANCO] - %(levelname)s - %(message)s'
        )
        handler_backup.setFormatter(formatter_backup)
        
        if not self.logger_backup.handlers:
            self.logger_backup.addHandler(handler_backup)
    
    def log_agendador(self, level, message):
        """Registra no log geral do agendador"""
        getattr(self.logger_geral, level.lower())(message)
    
    def log_backup(self, level, message):
        """Registra no log específico do backup"""
        getattr(self.logger_backup, level.lower())(message)
    
    def log_ambos(self, level, message):
        """Registra em ambos os logs"""
        self.log_agendador(level, message)
        self.log_backup(level, message)

# Instância global para uso em outros scripts
backup_logger = BackupBancoLogger()
