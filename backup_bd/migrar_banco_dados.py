#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 SCRIPT DE MIGRAÇÃO DE BANCO DE DADOS
De: pma.megatrends.site → Para: pma.linksystems.com.br

Executa migração completa com backup, transferência e atualização de código.
"""

import os
import re
import shutil
import subprocess
import mysql.connector
from datetime import datetime
import time
import json

class MigradorBancoDados:
    def __init__(self):
        self.servidor_origem = "pma.megatrends.site"
        self.servidor_destino = "pma.linksystems.com.br"
        self.usuario = "root"
        self.senha = "Define@4536#8521"  # Ajuste conforme necessário
        
        self.bancos = ["litoral", "teste", "gerenciamento_premiacoes"]
        
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
            'test_verificar_andamento.py',
            'alimenta_siglas_relatorios.py',
            'alimenta_premiados.py',
            'debug_horarios.py',
            'configurar_vps_externa.py',
            'processar_todas_edicoes.py',
            'processar_teste_corrigido.py',
            'processar_relatorios_funcionando.py',
            'processar_relatorios_final.py',
            'processar_relatorios_direto.py',
            'processar_relatorios_completo_v2.py',
            'processar_relatorios_completo.py',
            'processar_1000_edicoes_final.py'
        ]
        
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = f"migracao_log_{self.timestamp}.txt"
        
    def log(self, mensagem):
        """Registra mensagem no log e exibe no console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {mensagem}"
        print(log_msg)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def testar_conectividade(self, servidor):
        """Testa conectividade com servidor MySQL"""
        try:
            self.log(f"🔌 Testando conectividade com {servidor}...")
            conn = mysql.connector.connect(
                host=servidor,
                user=self.usuario,
                password=self.senha,
                connect_timeout=10
            )
            conn.close()
            self.log(f"✅ Conectividade OK com {servidor}")
            return True
        except Exception as e:
            self.log(f"❌ Erro ao conectar com {servidor}: {e}")
            return False
    
    def criar_backup(self):
        """Cria backup dos bancos de dados"""
        self.log("📦 Iniciando backup dos bancos de dados...")
        
        backup_dir = f"backup_migracao_{self.timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        for banco in self.bancos:
            try:
                backup_file = f"{backup_dir}/{banco}_backup_{self.timestamp}.sql"
                
                self.log(f"📥 Fazendo backup do banco '{banco}'...")
                
                cmd = [
                    "mysqldump",
                    f"-h{self.servidor_origem}",
                    f"-u{self.usuario}",
                    f"-p{self.senha}",
                    "--routines",
                    "--triggers",
                    "--single-transaction",
                    banco
                ]
                
                with open(backup_file, 'w', encoding='utf-8') as f:
                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                
                if result.returncode == 0:
                    size = os.path.getsize(backup_file)
                    self.log(f"✅ Backup de '{banco}' concluído: {size} bytes")
                else:
                    self.log(f"❌ Erro no backup de '{banco}': {result.stderr}")
                    return False
                    
            except Exception as e:
                self.log(f"❌ Erro ao fazer backup de '{banco}': {e}")
                return False
        
        self.log(f"✅ Todos os backups concluídos em: {backup_dir}")
        return backup_dir
    
    def verificar_bancos_destino(self):
        """Verifica se os bancos existem no servidor de destino"""
        try:
            self.log("🔍 Verificando bancos no servidor de destino...")
            
            conn = mysql.connector.connect(
                host=self.servidor_destino,
                user=self.usuario,
                password=self.senha
            )
            cursor = conn.cursor()
            
            for banco in self.bancos:
                cursor.execute(f"SHOW DATABASES LIKE '{banco}'")
                result = cursor.fetchone()
                
                if result:
                    self.log(f"⚠️  Banco '{banco}' já existe no destino")
                else:
                    self.log(f"📝 Criando banco '{banco}' no destino...")
                    cursor.execute(f"CREATE DATABASE {banco} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            conn.close()
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao verificar bancos de destino: {e}")
            return False
    
    def restaurar_bancos(self, backup_dir):
        """Restaura os bancos no servidor de destino"""
        self.log("📤 Iniciando restauração dos bancos...")
        
        for banco in self.bancos:
            try:
                backup_file = f"{backup_dir}/{banco}_backup_{self.timestamp}.sql"
                
                if not os.path.exists(backup_file):
                    self.log(f"⚠️  Arquivo de backup não encontrado: {backup_file}")
                    continue
                
                self.log(f"📤 Restaurando banco '{banco}'...")
                
                cmd = [
                    "mysql",
                    f"-h{self.servidor_destino}",
                    f"-u{self.usuario}",
                    f"-p{self.senha}",
                    banco
                ]
                
                with open(backup_file, 'r', encoding='utf-8') as f:
                    result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
                
                if result.returncode == 0:
                    self.log(f"✅ Banco '{banco}' restaurado com sucesso")
                else:
                    self.log(f"❌ Erro ao restaurar '{banco}': {result.stderr}")
                    return False
                    
            except Exception as e:
                self.log(f"❌ Erro ao restaurar '{banco}': {e}")
                return False
        
        return True
    
    def verificar_integridade(self):
        """Verifica integridade dos dados migrados"""
        self.log("🔍 Verificando integridade dos dados migrados...")
        
        try:
            # Conectar ao servidor de destino
            conn = mysql.connector.connect(
                host=self.servidor_destino,
                user=self.usuario,
                password=self.senha,
                database="litoral"
            )
            cursor = conn.cursor()
            
            # Verificar tabelas principais
            tabelas_verificar = [
                "extracoes_cadastro",
                "premiacoes", 
                "siglas_diarias"
            ]
            
            for tabela in tabelas_verificar:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                self.log(f"📊 Tabela '{tabela}': {count} registros")
            
            conn.close()
            self.log("✅ Verificação de integridade concluída")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro na verificação de integridade: {e}")
            return False
    
    def criar_backup_codigo(self):
        """Cria backup do código atual"""
        backup_dir = f"backup_codigo_{self.timestamp}"
        self.log(f"💾 Criando backup do código em: {backup_dir}")
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            for arquivo in self.arquivos_config:
                if os.path.exists(arquivo):
                    # Criar diretórios se necessário
                    dest_dir = os.path.join(backup_dir, os.path.dirname(arquivo))
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    # Copiar arquivo
                    dest_file = os.path.join(backup_dir, arquivo)
                    shutil.copy2(arquivo, dest_file)
                    self.log(f"📁 Backup: {arquivo}")
            
            return backup_dir
            
        except Exception as e:
            self.log(f"❌ Erro ao criar backup do código: {e}")
            return None
    
    def atualizar_configuracoes(self):
        """Atualiza todas as configurações de banco"""
        self.log("🔧 Atualizando configurações de banco...")
        
        arquivos_atualizados = 0
        
        for arquivo in self.arquivos_config:
            if os.path.exists(arquivo):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    # Substituir host
                    conteudo_novo = conteudo.replace(
                        self.servidor_origem,
                        self.servidor_destino
                    )
                    
                    if conteudo_novo != conteudo:
                        with open(arquivo, 'w', encoding='utf-8') as f:
                            f.write(conteudo_novo)
                        
                        self.log(f"✅ Atualizado: {arquivo}")
                        arquivos_atualizados += 1
                    else:
                        self.log(f"⚪ Sem alterações: {arquivo}")
                        
                except Exception as e:
                    self.log(f"❌ Erro ao atualizar {arquivo}: {e}")
                    return False
            else:
                self.log(f"⚠️  Arquivo não encontrado: {arquivo}")
        
        self.log(f"✅ {arquivos_atualizados} arquivos atualizados")
        return True
    
    def testar_aplicacoes(self):
        """Testa conectividade das aplicações após migração"""
        self.log("🧪 Testando aplicações após migração...")
        
        try:
            # Testar conexão principal
            conn = mysql.connector.connect(
                host=self.servidor_destino,
                user=self.usuario,
                password=self.senha,
                database="litoral"
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM extracoes_cadastro LIMIT 1")
            result = cursor.fetchone()
            
            conn.close()
            
            self.log(f"✅ Teste de aplicação: {result[0]} registros acessíveis")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro no teste de aplicação: {e}")
            return False
    
    def rollback_configuracoes(self, backup_dir):
        """Faz rollback das configurações"""
        self.log("🔄 Executando rollback das configurações...")
        
        try:
            for arquivo in self.arquivos_config:
                backup_file = os.path.join(backup_dir, arquivo)
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, arquivo)
                    self.log(f"🔄 Rollback: {arquivo}")
            
            self.log("✅ Rollback concluído")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro no rollback: {e}")
            return False
    
    def executar_migracao(self):
        """Executa o processo completo de migração"""
        self.log("🚀 INICIANDO MIGRAÇÃO DE BANCO DE DADOS")
        self.log(f"📊 De: {self.servidor_origem} → Para: {self.servidor_destino}")
        self.log(f"📋 Bancos: {', '.join(self.bancos)}")
        
        # 1. Testes iniciais
        if not self.testar_conectividade(self.servidor_origem):
            self.log("❌ FALHA: Servidor de origem inacessível")
            return False
        
        if not self.testar_conectividade(self.servidor_destino):
            self.log("❌ FALHA: Servidor de destino inacessível")
            return False
        
        # 2. Backup do código
        backup_codigo = self.criar_backup_codigo()
        if not backup_codigo:
            self.log("❌ FALHA: Não foi possível criar backup do código")
            return False
        
        # 3. Backup dos dados
        backup_dir = self.criar_backup()
        if not backup_dir:
            self.log("❌ FALHA: Não foi possível criar backup dos dados")
            return False
        
        # 4. Preparar servidor de destino
        if not self.verificar_bancos_destino():
            self.log("❌ FALHA: Erro ao preparar servidor de destino")
            return False
        
        # 5. Migrar dados
        if not self.restaurar_bancos(backup_dir):
            self.log("❌ FALHA: Erro na migração dos dados")
            return False
        
        # 6. Verificar integridade
        if not self.verificar_integridade():
            self.log("❌ FALHA: Dados corrompidos após migração")
            return False
        
        # 7. Atualizar configurações
        if not self.atualizar_configuracoes():
            self.log("❌ FALHA: Erro ao atualizar configurações")
            self.log("🔄 Executando rollback...")
            self.rollback_configuracoes(backup_codigo)
            return False
        
        # 8. Testar aplicações
        if not self.testar_aplicacoes():
            self.log("❌ FALHA: Aplicações não funcionando")
            self.log("🔄 Executando rollback...")
            self.rollback_configuracoes(backup_codigo)
            return False
        
        # 9. Sucesso!
        self.log("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        self.log(f"📁 Backup do código: {backup_codigo}")
        self.log(f"📁 Backup dos dados: {backup_dir}")
        self.log(f"📄 Log completo: {self.log_file}")
        
        return True

def main():
    print("🔄 MIGRADOR DE BANCO DE DADOS")
    print("=" * 50)
    
    migrador = MigradorBancoDados()
    
    # Confirmar migração
    resposta = input(f"Confirma migração de {migrador.servidor_origem} para {migrador.servidor_destino}? (s/N): ")
    
    if resposta.lower() != 's':
        print("❌ Migração cancelada pelo usuário")
        return
    
    # Executar migração
    sucesso = migrador.executar_migracao()
    
    if sucesso:
        print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"📄 Verifique o log: {migrador.log_file}")
    else:
        print("\n❌ MIGRAÇÃO FALHOU!")
        print(f"📄 Verifique o log: {migrador.log_file}")

if __name__ == "__main__":
    main() 