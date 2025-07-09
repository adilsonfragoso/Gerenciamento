#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 SCRIPT DE MIGRAÇÃO DE BANCO DE DADOS VIA WEB
De: pma.megatrends.site → Para: pma.linksystems.com.br (via phpMyAdmin)

Executa migração completa usando phpMyAdmin web em vez de conexão direta MySQL.
"""

import os
import re
import shutil
import subprocess
import mysql.connector
import requests
from datetime import datetime
import time
import json

class MigradorBancoDadosWeb:
    def __init__(self):
        # Servidor origem (funcionando)
        self.servidor_origem = "pma.megatrends.site"
        self.usuario_origem = "root"
        self.senha_origem = "Define@4536#8521"
        
        # Servidor destino (via phpMyAdmin web)
        self.servidor_destino_web = "http://pma.linksystems.com.br"
        self.servidor_destino_mysql = "phpmyadmin_dados:3306"  # Nome interno
        self.usuario_destino = "adseg"
        self.senha_destino = "Define@4536#8521"
        
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
        self.log_file = f"migracao_web_log_{self.timestamp}.txt"
        
        # Sessão para phpMyAdmin
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        
    def log(self, mensagem):
        """Registra mensagem no log e exibe no console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {mensagem}"
        print(log_msg)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def testar_conectividade_origem(self):
        """Testa conectividade com servidor MySQL de origem"""
        try:
            self.log(f"🔌 Testando conectividade com {self.servidor_origem}...")
            conn = mysql.connector.connect(
                host=self.servidor_origem,
                user=self.usuario_origem,
                password=self.senha_origem,
                connect_timeout=10
            )
            conn.close()
            self.log(f"✅ Conectividade OK com {self.servidor_origem}")
            return True
        except Exception as e:
            self.log(f"❌ Erro ao conectar com {self.servidor_origem}: {e}")
            return False
    
    def login_phpmyadmin(self):
        """Faz login no phpMyAdmin web"""
        try:
            self.log(f"🌐 Fazendo login no phpMyAdmin: {self.servidor_destino_web}")
            
            # Primeira requisição para obter cookies
            response = self.session.get(self.servidor_destino_web, timeout=10)
            if response.status_code != 200:
                self.log(f"❌ Erro ao acessar phpMyAdmin: {response.status_code}")
                return False
            
            # Dados de login
            login_data = {
                'pma_username': self.usuario_destino,
                'pma_password': self.senha_destino,
                'pma_servername': self.servidor_destino_mysql,
                'server': '1'
            }
            
            # Fazer login
            login_response = self.session.post(
                self.servidor_destino_web,
                data=login_data,
                timeout=10
            )
            
            # Verificar se o login foi bem-sucedido
            if "error" in login_response.text.lower() or "incorrect" in login_response.text.lower():
                self.log("❌ Login falhou - credenciais incorretas")
                return False
            elif "index.php" in login_response.url or "main.php" in login_response.url:
                self.log("✅ Login realizado com sucesso!")
                return True
            else:
                self.log("⚠️ Resposta inesperada do login")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro no login: {e}")
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
                    f"-u{self.usuario_origem}",
                    f"-p{self.senha_origem}",
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
        """Verifica se os bancos existem no servidor de destino via phpMyAdmin"""
        try:
            self.log("🔍 Verificando bancos no servidor de destino...")
            
            # Fazer login primeiro
            if not self.login_phpmyadmin():
                return False
            
            # Acessar página de bancos
            db_url = f"{self.servidor_destino_web}/db_structure.php"
            response = self.session.get(db_url, timeout=10)
            
            if response.status_code == 200:
                html = response.text.lower()
                
                for banco in self.bancos:
                    if banco in html:
                        self.log(f"⚠️  Banco '{banco}' já existe no destino")
                    else:
                        self.log(f"📝 Banco '{banco}' não existe - será criado")
                
                return True
            else:
                self.log(f"❌ Erro ao acessar lista de bancos: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao verificar bancos de destino: {e}")
            return False
    
    def criar_bancos_via_web(self):
        """Cria bancos de dados via phpMyAdmin web"""
        self.log("📝 Criando bancos de dados via phpMyAdmin...")
        
        for banco in self.bancos:
            try:
                # URL para criar banco
                create_url = f"{self.servidor_destino_web}/server_databases.php"
                
                create_data = {
                    'new_dbname': banco,
                    'db_collation': 'utf8mb4_unicode_ci',
                    'sql_query': f"CREATE DATABASE `{banco}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                }
                
                response = self.session.post(create_url, data=create_data, timeout=10)
                
                if response.status_code == 200 and "error" not in response.text.lower():
                    self.log(f"✅ Banco '{banco}' criado com sucesso")
                else:
                    self.log(f"⚠️  Banco '{banco}' pode já existir ou erro na criação")
                    
            except Exception as e:
                self.log(f"❌ Erro ao criar banco '{banco}': {e}")
    
    def importar_dados_via_web(self, backup_dir):
        """Importa dados via phpMyAdmin web"""
        self.log("📤 Iniciando importação de dados via phpMyAdmin...")
        
        for banco in self.bancos:
            try:
                backup_file = f"{backup_dir}/{banco}_backup_{self.timestamp}.sql"
                
                if not os.path.exists(backup_file):
                    self.log(f"⚠️  Arquivo de backup não encontrado: {backup_file}")
                    continue
                
                self.log(f"📤 Importando dados para banco '{banco}'...")
                
                # Ler arquivo SQL
                with open(backup_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # URL para importar
                import_url = f"{self.servidor_destino_web}/import.php"
                
                # Preparar dados para upload
                files = {
                    'import_file': (f"{banco}.sql", sql_content, 'application/sql')
                }
                
                data = {
                    'db': banco,
                    'sql_query': sql_content,
                    'sql_delimiter': ';',
                    'sql_type': 'INSERT'
                }
                
                response = self.session.post(import_url, data=data, files=files, timeout=30)
                
                if response.status_code == 200 and "error" not in response.text.lower():
                    self.log(f"✅ Dados de '{banco}' importados com sucesso")
                else:
                    self.log(f"❌ Erro ao importar dados de '{banco}'")
                    
            except Exception as e:
                self.log(f"❌ Erro ao importar dados de '{banco}': {e}")
    
    def atualizar_configuracoes(self):
        """Atualiza configurações nos arquivos"""
        self.log("⚙️  Atualizando configurações nos arquivos...")
        
        # Backup das configurações atuais
        backup_config_dir = f"backup_config_{self.timestamp}"
        os.makedirs(backup_config_dir, exist_ok=True)
        
        for arquivo in self.arquivos_config:
            if os.path.exists(arquivo):
                try:
                    # Fazer backup
                    backup_file = f"{backup_config_dir}/{os.path.basename(arquivo)}"
                    shutil.copy2(arquivo, backup_file)
                    
                    # Ler arquivo
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    # Substituir configurações
                    conteudo_novo = conteudo.replace(
                        self.servidor_origem, 
                        self.servidor_destino_mysql
                    )
                    
                    # Se houve mudança, salvar
                    if conteudo_novo != conteudo:
                        with open(arquivo, 'w', encoding='utf-8') as f:
                            f.write(conteudo_novo)
                        self.log(f"✅ Configuração atualizada: {arquivo}")
                    else:
                        self.log(f"ℹ️  Nenhuma mudança necessária: {arquivo}")
                        
                except Exception as e:
                    self.log(f"❌ Erro ao atualizar {arquivo}: {e}")
        
        self.log(f"✅ Backup das configurações em: {backup_config_dir}")
    
    def executar_migracao(self):
        """Executa a migração completa"""
        self.log("🚀 INICIANDO MIGRAÇÃO COMPLETA")
        self.log("=" * 60)
        
        try:
            # 1. Testar conectividade origem
            if not self.testar_conectividade_origem():
                self.log("❌ Falha na conectividade com servidor de origem")
                return False
            
            # 2. Testar login phpMyAdmin
            if not self.login_phpmyadmin():
                self.log("❌ Falha no login do phpMyAdmin")
                return False
            
            # 3. Criar backup
            backup_dir = self.criar_backup()
            if not backup_dir:
                self.log("❌ Falha na criação do backup")
                return False
            
            # 4. Verificar bancos destino
            self.verificar_bancos_destino()
            
            # 5. Criar bancos se necessário
            self.criar_bancos_via_web()
            
            # 6. Importar dados
            self.importar_dados_via_web(backup_dir)
            
            # 7. Atualizar configurações
            self.atualizar_configuracoes()
            
            self.log("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            self.log("✅ Todos os dados foram migrados")
            self.log("✅ Configurações foram atualizadas")
            self.log(f"📋 Log completo: {self.log_file}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ ERRO CRÍTICO NA MIGRAÇÃO: {e}")
            return False

def main():
    migrador = MigradorBancoDadosWeb()
    migrador.executar_migracao()

if __name__ == "__main__":
    main() 