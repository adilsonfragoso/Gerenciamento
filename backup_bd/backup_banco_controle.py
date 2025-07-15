#!/usr/bin/env python3
# backup_banco_controle.py
"""
Script principal de controle do sistema de backup agendado.
Permite instalar, configurar, iniciar e gerenciar todo o sistema de backup.
"""

import sys
import subprocess
import os
from pathlib import Path

class ControladorBackup:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        
    def mostrar_menu(self):
        """Mostra o menu principal"""
        print("\n🗂️  SISTEMA DE BACKUP AUTOMÁTICO - CONTROLE PRINCIPAL")
        print("=" * 60)
        print("1. 📦  Instalar dependências")
        print("2. ⏰  Configurar agendamento (Tarefa Windows)")
        print("3. 🔍  Verificar status do agendamento")
        print("4. 🗑️  Remover agendamento")
        print("5. 🧪  Executar backup teste")
        print("6. 📊  Ver logs do agendador")
        print("7. 🚀  Executar agendador manual")
        print("8. ❌  Sair")
        print("=" * 60)
        
    def executar_script(self, nome_script, *args):
        """Executa um script Python"""
        script_path = self.script_dir / nome_script
        if not script_path.exists():
            print(f"❌  Script não encontrado: {nome_script}")
            return False
            
        try:
            cmd = [sys.executable, str(script_path)] + list(args)
            resultado = subprocess.run(cmd, cwd=str(self.script_dir))
            return resultado.returncode == 0
        except Exception as e:
            print(f"❌  Erro ao executar {nome_script}: {e}")
            return False
    
    def instalar_dependencias(self):
        """Instala as dependências necessárias"""
        print("\n📦  Instalando dependências...")
        return self.executar_script("backup_banco_instalar_dependencias.py")
    
    def configurar_agendamento(self):
        """Configura o agendamento no Windows"""
        print("\n⏰  Configurando agendamento...")
        return self.executar_script("backup_banco_tarefa_windows.py", "criar")
    
    def verificar_agendamento(self):
        """Verifica o status do agendamento"""
        print("\n🔍  Verificando agendamento...")
        return self.executar_script("backup_banco_tarefa_windows.py", "verificar")
    
    def remover_agendamento(self):
        """Remove o agendamento"""
        print("\n🗑️  Removendo agendamento...")
        resposta = input("⚠️  Tem certeza que deseja remover o agendamento? (s/n): ")
        if resposta.lower() in ['s', 'sim', 'y', 'yes']:
            return self.executar_script("backup_banco_tarefa_windows.py", "remover")
        else:
            print("✅  Operação cancelada")
            return True
    
    def executar_backup_teste(self):
        """Executa um backup de teste"""
        print("\n🧪  Executando backup de teste...")
        return self.executar_script("backup_banco_de_dados.py")
    
    def ver_logs(self):
        """Mostra os logs do agendador"""
        print("\n📊  Logs do agendador...")
        log_file = self.script_dir.parent / "scripts" / "andamento" / "logs" / "logs_geral_agendador.log"
        
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
                    
                # Mostra as últimas 20 linhas
                print("📄  Últimas 20 linhas do log:")
                print("-" * 50)
                for linha in linhas[-20:]:
                    print(linha.rstrip())
                print("-" * 50)
                
            except Exception as e:
                print(f"❌  Erro ao ler log: {e}")
        else:
            print("⚠️   Arquivo de log não encontrado")
            print(f"   Esperado em: {log_file}")
    
    def executar_agendador_manual(self):
        """Executa o agendador em modo manual"""
        print("\n🚀  Iniciando agendador manual...")
        print("⚠️   Use Ctrl+C para parar")
        return self.executar_script("backup_banco_agendador.py")
    
    def run(self):
        """Executa o controlador principal"""
        while True:
            self.mostrar_menu()
            
            try:
                escolha = input("\nEscolha uma opção (1-8): ").strip()
                
                if escolha == "1":
                    self.instalar_dependencias()
                elif escolha == "2":
                    self.configurar_agendamento()
                elif escolha == "3":
                    self.verificar_agendamento()
                elif escolha == "4":
                    self.remover_agendamento()
                elif escolha == "5":
                    self.executar_backup_teste()
                elif escolha == "6":
                    self.ver_logs()
                elif escolha == "7":
                    self.executar_agendador_manual()
                elif escolha == "8":
                    print("\n👋  Saindo...")
                    break
                else:
                    print("❌  Opção inválida. Escolha de 1 a 8.")
                    
                input("\n⏸️  Pressione Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋  Saindo...")
                break
            except Exception as e:
                print(f"\n❌  Erro: {e}")
                input("\n⏸️  Pressione Enter para continuar...")

if __name__ == "__main__":
    controlador = ControladorBackup()
    controlador.run()
