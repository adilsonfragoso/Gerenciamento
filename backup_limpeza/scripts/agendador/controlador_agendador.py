#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlador do Agendador de Rifas
Permite iniciar, parar e verificar status do serviço

⚠️ IMPORTANTE: Antes de modificar este arquivo, leia a documentação em:
📖 scripts/agendador/README.md
🔗 scripts/agendador/DEPENDENCIAS.md

Este arquivo é uma alternativa ao gerenciar_agendador.bat.
Funciona como controlador Python para o agendador_servico.py.
"""

import sys
import os
import time
import json
import subprocess
import psutil
from datetime import datetime

class ControladorAgendador:
    def __init__(self):
        self.pid_file = "scripts/agendador.pid"
        self.status_file = "scripts/agendador_status.json"
        self.script_servico = "scripts/agendador/agendador_servico.py"
    
    def obter_status(self):
        """Obtém o status atual do serviço"""
        try:
            # Verificar se arquivo de status existe
            if not os.path.exists(self.status_file):
                return {'status': 'parado', 'detalhes': 'Arquivo de status não encontrado'}
            
            # Ler status
            with open(self.status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
            
            # Verificar se processo ainda está rodando
            pid = status_data.get('pid')
            if pid and psutil.pid_exists(pid):
                try:
                    processo = psutil.Process(pid)
                    if processo.is_running():
                        status_data['status'] = 'rodando'
                        status_data['detalhes'] = f'Processo {pid} ativo'
                    else:
                        status_data['status'] = 'parado'
                        status_data['detalhes'] = f'Processo {pid} não está rodando'
                except:
                    status_data['status'] = 'erro'
                    status_data['detalhes'] = f'Erro ao verificar processo {pid}'
            else:
                status_data['status'] = 'parado'
                status_data['detalhes'] = 'Processo não encontrado'
            
            return status_data
            
        except Exception as e:
            return {'status': 'erro', 'detalhes': f'Erro ao obter status: {e}'}
    
    def iniciar_servico(self):
        """Inicia o serviço em background"""
        try:
            # Verificar se já está rodando
            status = self.obter_status()
            if status['status'] == 'rodando':
                return {'sucesso': False, 'mensagem': 'Serviço já está rodando'}
            
            # Iniciar processo em background
            if os.name == 'nt':  # Windows
                # Usar pythonw para rodar sem janela
                processo = subprocess.Popen([
                    'pythonw', self.script_servico
                ], creationflags=subprocess.CREATE_NO_WINDOW)
            else:  # Linux/Mac
                processo = subprocess.Popen([
                    'python3', self.script_servico
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Aguardar um pouco para o serviço inicializar
            time.sleep(3)
            
            # Verificar se iniciou corretamente
            status = self.obter_status()
            if status['status'] == 'rodando':
                return {'sucesso': True, 'mensagem': f'Serviço iniciado com PID {status["pid"]}'}
            else:
                return {'sucesso': False, 'mensagem': 'Falha ao iniciar serviço'}
                
        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro ao iniciar: {e}'}
    
    def parar_servico(self):
        """Para o serviço"""
        try:
            status = self.obter_status()
            
            if status['status'] != 'rodando':
                return {'sucesso': False, 'mensagem': 'Serviço não está rodando'}
            
            pid = status.get('pid')
            if not pid:
                return {'sucesso': False, 'mensagem': 'PID não encontrado'}
            
            # Tentar parar o processo
            try:
                processo = psutil.Process(pid)
                processo.terminate()
                
                # Aguardar terminar gracefully
                processo.wait(timeout=10)
                
                return {'sucesso': True, 'mensagem': f'Serviço parado (PID {pid})'}
                
            except psutil.TimeoutExpired:
                # Forçar parada se não terminou
                processo.kill()
                return {'sucesso': True, 'mensagem': f'Serviço forçado a parar (PID {pid})'}
                
        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro ao parar: {e}'}
    
    def reiniciar_servico(self):
        """Reinicia o serviço"""
        resultado_parar = self.parar_servico()
        time.sleep(2)
        resultado_iniciar = self.iniciar_servico()
        
        return {
            'sucesso': resultado_iniciar['sucesso'],
            'mensagem': f"Parar: {resultado_parar['mensagem']} | Iniciar: {resultado_iniciar['mensagem']}"
        }
    
    def exibir_banner(self):
        """Exibe banner do controlador"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║              CONTROLADOR DO AGENDADOR DE RIFAS              ║
║                                                              ║
║  🎮 Controle total do serviço de monitoramento               ║
║  🔍 Verificação de status em tempo real                     ║
║  🚀 Execução em background (oculto)                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def exibir_status_detalhado(self):
        """Exibe status detalhado do serviço"""
        status = self.obter_status()
        
        print("📊 STATUS DO AGENDADOR:")
        print(f"   Status: {status['status'].upper()}")
        print(f"   Detalhes: {status.get('detalhes', 'N/A')}")
        
        if status['status'] == 'rodando':
            print(f"   PID: {status.get('pid', 'N/A')}")
            print(f"   Rifas Ativas: {status.get('rifas_ativas', 'N/A')}")
            
            ultima_verificacao = status.get('ultima_verificacao')
            if ultima_verificacao:
                dt = datetime.fromisoformat(ultima_verificacao)
                print(f"   Última Verificação: {dt.strftime('%H:%M:%S')}")
            
            log_file = status.get('log_file')
            if log_file and os.path.exists(log_file):
                print(f"   Log: {log_file}")
        
        print()
    
    def menu_interativo(self):
        """Menu interativo para controlar o serviço"""
        while True:
            self.exibir_banner()
            self.exibir_status_detalhado()
            
            print("🎮 OPÇÕES:")
            print("   1 - Iniciar Serviço")
            print("   2 - Parar Serviço")
            print("   3 - Reiniciar Serviço")
            print("   4 - Atualizar Status")
            print("   5 - Ver Logs")
            print("   0 - Sair")
            print()
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == '1':
                print("🚀 Iniciando serviço...")
                resultado = self.iniciar_servico()
                print(f"{'✅' if resultado['sucesso'] else '❌'} {resultado['mensagem']}")
                
            elif opcao == '2':
                print("🛑 Parando serviço...")
                resultado = self.parar_servico()
                print(f"{'✅' if resultado['sucesso'] else '❌'} {resultado['mensagem']}")
                
            elif opcao == '3':
                print("🔄 Reiniciando serviço...")
                resultado = self.reiniciar_servico()
                print(f"{'✅' if resultado['sucesso'] else '❌'} {resultado['mensagem']}")
                
            elif opcao == '4':
                print("🔄 Atualizando status...")
                
            elif opcao == '5':
                self.mostrar_logs()
                
            elif opcao == '0':
                print("👋 Saindo...")
                break
                
            else:
                print("❌ Opção inválida!")
            
            if opcao != '4':
                input("\nPressione Enter para continuar...")
    
    def mostrar_logs(self):
        """Mostra os últimos logs do serviço"""
        log_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "logs/agendador_servico.log"))
        
        if not os.path.exists(log_file):
            print("❌ Arquivo de log não encontrado")
            return
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            print("\n📝 ÚLTIMOS 20 LOGS:")
            print("-" * 60)
            
            for linha in linhas[-20:]:
                print(linha.strip())
                
            print("-" * 60)
            
        except Exception as e:
            print(f"❌ Erro ao ler logs: {e}")

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        # Modo comando
        controlador = ControladorAgendador()
        comando = sys.argv[1].lower()
        
        if comando == 'start':
            resultado = controlador.iniciar_servico()
            print(resultado['mensagem'])
            sys.exit(0 if resultado['sucesso'] else 1)
            
        elif comando == 'stop':
            resultado = controlador.parar_servico()
            print(resultado['mensagem'])
            sys.exit(0 if resultado['sucesso'] else 1)
            
        elif comando == 'restart':
            resultado = controlador.reiniciar_servico()
            print(resultado['mensagem'])
            sys.exit(0 if resultado['sucesso'] else 1)
            
        elif comando == 'status':
            status = controlador.obter_status()
            print(f"Status: {status['status']}")
            if status.get('detalhes'):
                print(f"Detalhes: {status['detalhes']}")
            sys.exit(0)
            
        else:
            print("Comandos disponíveis: start, stop, restart, status")
            sys.exit(1)
    else:
        # Modo interativo
        controlador = ControladorAgendador()
        controlador.menu_interativo()

if __name__ == "__main__":
    main() 