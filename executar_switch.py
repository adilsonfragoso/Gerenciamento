#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 SCRIPT DE SWITCH FINAL
Altera todas as configurações para usar o novo servidor pma.linksystems.com.br
"""

import os
import re
import shutil
import glob
from datetime import datetime
import subprocess

class ExecutorSwitch:
    def __init__(self):
        self.servidor_antigo = "pma.megatrends.site"
        self.servidor_novo = "pma.linksystems.com.br"
        
        # Lista completa de arquivos para atualizar
        self.arquivos_config = [
            'app/db_config.py',
            'app/main.py',
            'config.py',
            'scripts/config_cadRifas.py',
            'scripts/verificar_andamento_rifas.py',
            'scripts/recuperar_rifas_erro.py',
            'scripts/novo_verificalinks.py',
            'scripts/novo_chamadas_group_latest.py',
            'scripts/novo_chamadas_group_backup.py',
            'scripts/envio_automatico_pdfs_whatsapp.py',
            'scripts/agendador_verificacao_rifas.py',
            'scripts/agendador_servico_v2.py',
            'scripts/agendador_servico.py',
            'scripts/agendador.py',
            'scripts/cadastrar_sigla_avulsa.py',
            'scripts/cadastrar_siglas.py',
            'scripts/cadRifas_litoral_latest_backup.py',
            'scripts/cadRifas_litoral_latest.py',
            'scripts/desativa_concluidas_v4.py',
            'scripts/desativa_concluidas_v5.py',
            'scripts/relatorio_dashboard_automatico.py',
            'alimenta_premiados_lote.py',
            'alimenta_premiados_rapido.py',
            'alimenta_premiados_ultra_rapido.py',
            'alimenta_premiados.py',
            'alimenta_siglas_relatorios.py',
            'migrar_banco_dados.py',
            'relatorio_corrigido_v2.py',
            'relatorio_final_corrigido.py'
        ]
        
        self.backup_dir = f"backup_configs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def criar_backup_configs(self):
        """Cria backup de todas as configurações atuais"""
        print(f"📁 Criando backup das configurações em: {self.backup_dir}")
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        backup_count = 0
        for arquivo in self.arquivos_config:
            if os.path.exists(arquivo):
                # Criar estrutura de diretórios no backup
                backup_path = os.path.join(self.backup_dir, arquivo)
                backup_dir_path = os.path.dirname(backup_path)
                
                if backup_dir_path and not os.path.exists(backup_dir_path):
                    os.makedirs(backup_dir_path)
                
                # Copiar arquivo
                shutil.copy2(arquivo, backup_path)
                backup_count += 1
                print(f"  ✅ {arquivo}")
        
        print(f"📦 Backup concluído: {backup_count} arquivos salvos")
        return backup_count > 0
    
    def alterar_configuracao_arquivo(self, arquivo):
        """Altera a configuração de um arquivo específico"""
        try:
            if not os.path.exists(arquivo):
                print(f"  ⚠️ Arquivo não encontrado: {arquivo}")
                return False
            
            # Ler conteúdo do arquivo
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Substituir servidor antigo pelo novo
            conteudo_novo = conteudo.replace(self.servidor_antigo, self.servidor_novo)
            
            # Verificar se houve mudança
            if conteudo == conteudo_novo:
                print(f"  ℹ️ Nenhuma alteração necessária: {arquivo}")
                return True
            
            # Escrever novo conteúdo
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo_novo)
            
            print(f"  ✅ Atualizado: {arquivo}")
            return True
            
        except Exception as e:
            print(f"  ❌ Erro ao alterar {arquivo}: {e}")
            return False
    
    def executar_switch(self):
        """Executa o switch completo"""
        print("🔄 EXECUTANDO SWITCH FINAL")
        print("=" * 50)
        
        # 1. Criar backup
        if not self.criar_backup_configs():
            print("❌ Erro ao criar backup. Abortando...")
            return False
        
        print("\n🔧 Alterando configurações...")
        
        # 2. Alterar configurações
        sucesso = 0
        total = len(self.arquivos_config)
        
        for arquivo in self.arquivos_config:
            if self.alterar_configuracao_arquivo(arquivo):
                sucesso += 1
        
        print(f"\n📊 RESULTADO: {sucesso}/{total} arquivos atualizados")
        
        if sucesso == total:
            print("✅ SWITCH CONCLUÍDO COM SUCESSO!")
            print(f"🔄 Todos os sistemas agora apontam para: {self.servidor_novo}")
            print(f"📁 Backup salvo em: {self.backup_dir}")
            return True
        else:
            print("⚠️ SWITCH PARCIALMENTE CONCLUÍDO")
            print(f"❌ {total - sucesso} arquivos não foram atualizados")
            return False
    
    def rollback_switch(self):
        """Desfaz o switch restaurando o backup"""
        print("🔄 EXECUTANDO ROLLBACK")
        print("=" * 50)
        
        if not os.path.exists(self.backup_dir):
            print(f"❌ Backup não encontrado: {self.backup_dir}")
            return False
        
        print(f"📁 Restaurando backup de: {self.backup_dir}")
        
        sucesso = 0
        total = 0
        
        # Restaurar todos os arquivos do backup
        for root, dirs, files in os.walk(self.backup_dir):
            for file in files:
                backup_file = os.path.join(root, file)
                # Calcular caminho relativo
                rel_path = os.path.relpath(backup_file, self.backup_dir)
                original_file = rel_path
                
                total += 1
                
                try:
                    shutil.copy2(backup_file, original_file)
                    print(f"  ✅ Restaurado: {original_file}")
                    sucesso += 1
                except Exception as e:
                    print(f"  ❌ Erro ao restaurar {original_file}: {e}")
        
        print(f"\n📊 ROLLBACK: {sucesso}/{total} arquivos restaurados")
        
        if sucesso == total:
            print("✅ ROLLBACK CONCLUÍDO COM SUCESSO!")
            print(f"🔄 Todos os sistemas voltaram para: {self.servidor_antigo}")
            return True
        else:
            print("⚠️ ROLLBACK PARCIALMENTE CONCLUÍDO")
            return False
    
    def verificar_status(self):
        """Verifica qual servidor está sendo usado atualmente"""
        print("🔍 VERIFICANDO STATUS ATUAL")
        print("=" * 50)
        
        usando_antigo = 0
        usando_novo = 0
        sem_config = 0
        
        for arquivo in self.arquivos_config:
            if not os.path.exists(arquivo):
                sem_config += 1
                continue
            
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                if self.servidor_antigo in conteudo:
                    usando_antigo += 1
                    print(f"  🔴 {arquivo} → {self.servidor_antigo}")
                elif self.servidor_novo in conteudo:
                    usando_novo += 1
                    print(f"  🟢 {arquivo} → {self.servidor_novo}")
                else:
                    sem_config += 1
                    print(f"  ⚪ {arquivo} → sem configuração")
                    
            except Exception as e:
                sem_config += 1
                print(f"  ❌ {arquivo} → erro: {e}")
        
        print(f"\n📊 RESUMO:")
        print(f"🔴 Usando {self.servidor_antigo}: {usando_antigo}")
        print(f"🟢 Usando {self.servidor_novo}: {usando_novo}")
        print(f"⚪ Sem configuração/erro: {sem_config}")
        
        if usando_novo > 0 and usando_antigo == 0:
            print(f"✅ MIGRAÇÃO COMPLETA - Todos os sistemas usam {self.servidor_novo}")
        elif usando_antigo > 0 and usando_novo == 0:
            print(f"🔴 USANDO SERVIDOR ANTIGO - Todos os sistemas usam {self.servidor_antigo}")
        else:
            print(f"⚠️ ESTADO MISTO - Alguns sistemas usam servidores diferentes!")
        
        return {
            'antigo': usando_antigo,
            'novo': usando_novo,
            'sem_config': sem_config
        }

def main():
    """Função principal"""
    executor = ExecutorSwitch()
    
    print("🔄 EXECUTOR DE SWITCH - MIGRAÇÃO DE BANCO")
    print("=" * 50)
    print("1. Executar switch completo")
    print("2. Rollback (voltar configuração anterior)")
    print("3. Verificar status atual")
    print("4. Apenas criar backup das configurações")
    print("0. Sair")
    
    while True:
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n⚠️ ATENÇÃO: Isso irá alterar TODAS as configurações!")
            confirma = input("Deseja continuar? (s/N): ").strip().lower()
            
            if confirma == 's':
                executor.executar_switch()
            else:
                print("❌ Switch cancelado")
        
        elif opcao == "2":
            print("\n🔄 Executando rollback...")
            executor.rollback_switch()
        
        elif opcao == "3":
            executor.verificar_status()
        
        elif opcao == "4":
            executor.criar_backup_configs()
        
        elif opcao == "0":
            print("👋 Saindo...")
            break
        
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main() 