#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agendador de Rifas - Versão Serviço (Background)
Roda em background sem interface visual

⚠️ IMPORTANTE: Antes de modificar este arquivo, leia a documentação em:
📖 scripts/agendador/README.md
🔗 scripts/agendador/DEPENDENCIAS.md

Este arquivo é parte do sistema de agendador e possui dependências críticas.
Modificações incorretas podem quebrar todo o sistema de monitoramento.
"""

import sys
import os
import time
import signal
import logging
from datetime import datetime
import json

# Adicionar o diretório scripts ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agendador_verificacao_rifas import AgendadorRifas

class AgendadorServico:
    def __init__(self):
        self.agendador = None
        self.rodando = False
        self.pid_file = "scripts/agendador.pid"
        self.status_file = "scripts/agendador_status.json"
        self.configurar_logging()
        
    def configurar_logging(self):
        """Configura logging apenas para arquivo (sem console)"""
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'agendador_servico.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8')
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def salvar_pid(self):
        """Salva o PID do processo em arquivo"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            self.logger.info(f"PID {os.getpid()} salvo em {self.pid_file}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar PID: {e}")
    
    def remover_pid(self):
        """Remove o arquivo PID"""
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
                self.logger.info("Arquivo PID removido")
        except Exception as e:
            self.logger.error(f"Erro ao remover PID: {e}")
    
    def atualizar_status(self, status, rifas_ativas=0, ultima_verificacao=None):
        """Atualiza arquivo de status"""
        try:
            status_data = {
                'status': status,
                'pid': os.getpid(),
                'inicio': datetime.now().isoformat(),
                'rifas_ativas': rifas_ativas,
                'ultima_verificacao': ultima_verificacao.isoformat() if ultima_verificacao else None,
                'log_file': os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs/agendador_servico.log'))
            }
            
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar status: {e}")
    
    def criar_notificacao_dashboard(self, rifas_processadas=0, detalhes=""):
        """Cria notificação para o dashboard sobre processamento de rifas"""
        try:
            notification_file = "scripts/agendador_notifications.json"
            
            notification_data = {
                "last_update": datetime.now().isoformat(),
                "rifas_processadas": rifas_processadas,
                "detalhes": detalhes,
                "agendador_pid": os.getpid()
            }
            
            with open(notification_file, 'w', encoding='utf-8') as f:
                json.dump(notification_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"🔔 Notificação criada para dashboard: {rifas_processadas} rifas processadas")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar notificação para dashboard: {e}")
    
    def signal_handler(self, signum, frame):
        """Manipulador de sinais para parada graceful"""
        self.logger.info(f"Sinal {signum} recebido. Parando serviço...")
        self.parar()
    
    def iniciar(self):
        """Inicia o serviço em background"""
        try:
            self.logger.info("=== INICIANDO AGENDADOR COMO SERVIÇO ===")
            
            # Salvar PID
            self.salvar_pid()
            
            # Configurar manipuladores de sinal
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Criar agendador
            self.agendador = AgendadorRifas()
            self.rodando = True
            
            # Verificação inicial
            rifas_ativas = self.agendador.buscar_rifas_ativas()
            self.logger.info(f"Encontradas {len(rifas_ativas)} rifas ativas")
            
            # Atualizar status
            self.atualizar_status('rodando', len(rifas_ativas), datetime.now())
            
            # Executar verificação inicial
            self.agendador.executar_verificacao_inicial()
            
            self.logger.info("Serviço iniciado com sucesso - rodando em background")
            
            # Loop principal
            while self.rodando:
                try:
                    import schedule
                    
                    # Verificar se há jobs pendentes
                    jobs_pendentes = schedule.jobs
                    if jobs_pendentes:
                        self.logger.info(f"Executando {len(jobs_pendentes)} jobs agendados...")
                        
                        # Capturar rifas antes da execução
                        rifas_antes = self.agendador.buscar_rifas_ativas()
                        
                        # Executar jobs pendentes
                        schedule.run_pending()
                        
                        # Verificar se houve processamento
                        rifas_depois = self.agendador.buscar_rifas_ativas()
                        
                        # Se houve mudanças, criar notificação
                        if len(rifas_depois) != len(rifas_antes):
                            self.criar_notificacao_dashboard(
                                rifas_processadas=len(rifas_depois),
                                detalhes=f"Processamento automático: {len(rifas_antes)} → {len(rifas_depois)} rifas"
                            )
                    else:
                        schedule.run_pending()
                    
                    time.sleep(30)
                    
                    # Atualizar status periodicamente
                    if datetime.now().minute % 5 == 0:  # A cada 5 minutos
                        rifas_ativas = self.agendador.buscar_rifas_ativas()
                        self.atualizar_status('rodando', len(rifas_ativas), datetime.now())
                        
                except Exception as e:
                    self.logger.error(f"Erro no loop principal: {e}")
                    time.sleep(60)
            
        except Exception as e:
            self.logger.error(f"Erro crítico no serviço: {e}")
            self.atualizar_status('erro', 0)
        finally:
            self.cleanup()
    
    def parar(self):
        """Para o serviço"""
        self.rodando = False
        self.logger.info("Serviço parado")
        self.atualizar_status('parado', 0)
    
    def cleanup(self):
        """Limpeza ao finalizar"""
        self.remover_pid()
        if os.path.exists(self.status_file):
            try:
                os.remove(self.status_file)
            except:
                pass

def main():
    """Função principal"""
    servico = AgendadorServico()
    servico.iniciar()

if __name__ == "__main__":
    main() 