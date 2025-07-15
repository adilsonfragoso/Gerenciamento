#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📦 SCRIPT DE BACKUP PARA MIGRAÇÃO MANUAL
Cria backup dos bancos e prepara para migração manual via phpMyAdmin
"""

import os
import subprocess
import mysql.connector
from datetime import datetime
import shutil

class BackupMigracaoManual:
    def __init__(self):
        # Servidor origem (funcionando)
        self.servidor_origem = "pma.megatrends.site"
        self.usuario_origem = "root"
        self.senha_origem = "Define@4536#8521"
        
        self.bancos = ["litoral", "teste", "gerenciamento_premiacoes"]
        
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = f"backup_migracao_manual_{self.timestamp}"
        
    def log(self, mensagem):
        """Registra mensagem no console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {mensagem}")
    
    def testar_conectividade(self):
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
    
    def criar_backup(self):
        """Cria backup dos bancos de dados"""
        self.log("📦 Iniciando backup dos bancos de dados...")
        
        os.makedirs(self.backup_dir, exist_ok=True)
        
        for banco in self.bancos:
            try:
                backup_file = f"{self.backup_dir}/{banco}_backup_{self.timestamp}.sql"
                
                self.log(f"📥 Fazendo backup do banco '{banco}'...")
                
                cmd = [
                    "mysqldump",
                    f"-h{self.servidor_origem}",
                    f"-u{self.usuario_origem}",
                    f"-p{self.senha_origem}",
                    "--routines",
                    "--triggers",
                    "--single-transaction",
                    "--add-drop-database",
                    "--create-database",
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
        
        self.log(f"✅ Todos os backups concluídos em: {self.backup_dir}")
        return True
    
    def criar_instrucoes_migracao(self):
        """Cria arquivo com instruções para migração manual"""
        instrucoes = f"""
# 📋 INSTRUÇÕES PARA MIGRAÇÃO MANUAL

## 🔗 Acesse o phpMyAdmin
URL: http://pma.linksystems.com.br

## 🔐 Faça login com:
- **Servidor**: phpmyadmin_dados:3306
- **Usuário**: adseg
- **Senha**: Define@4536#8521

## 📤 Importe os bancos:

### 1. Banco 'litoral'
- Clique em "Importar"
- Selecione o arquivo: {self.backup_dir}/litoral_backup_{self.timestamp}.sql
- Clique em "Executar"

### 2. Banco 'teste'
- Clique em "Importar"
- Selecione o arquivo: {self.backup_dir}/teste_backup_{self.timestamp}.sql
- Clique em "Executar"

### 3. Banco 'gerenciamento_premiacoes'
- Clique em "Importar"
- Selecione o arquivo: {self.backup_dir}/gerenciamento_premiacoes_backup_{self.timestamp}.sql
- Clique em "Executar"

## ⚙️ Após a migração
Execute o script: python atualizar_configuracoes.py

## 📁 Arquivos de backup criados:
{self.backup_dir}/

## 🕐 Timestamp da migração: {self.timestamp}
"""
        
        instrucoes_file = f"{self.backup_dir}/INSTRUCOES_MIGRACAO.txt"
        with open(instrucoes_file, 'w', encoding='utf-8') as f:
            f.write(instrucoes)
        
        self.log(f"📋 Instruções salvas em: {instrucoes_file}")
    
    def executar_backup(self):
        """Executa o backup completo"""
        self.log("🚀 INICIANDO BACKUP PARA MIGRAÇÃO MANUAL")
        self.log("=" * 60)
        
        try:
            # 1. Testar conectividade
            if not self.testar_conectividade():
                self.log("❌ Falha na conectividade com servidor de origem")
                return False
            
            # 2. Criar backup
            if not self.criar_backup():
                self.log("❌ Falha na criação do backup")
                return False
            
            # 3. Criar instruções
            self.criar_instrucoes_migracao()
            
            self.log("🎉 BACKUP CONCLUÍDO COM SUCESSO!")
            self.log("✅ Arquivos de backup criados")
            self.log("📋 Instruções para migração manual geradas")
            self.log(f"📁 Diretório: {self.backup_dir}")
            self.log("\n💡 PRÓXIMOS PASSOS:")
            self.log("   1. Acesse: http://pma.linksystems.com.br")
            self.log("   2. Faça login manualmente")
            self.log("   3. Importe os arquivos .sql")
            self.log("   4. Execute: python atualizar_configuracoes.py")
            
            return True
            
        except Exception as e:
            self.log(f"❌ ERRO CRÍTICO NO BACKUP: {e}")
            return False

def main():
    backup = BackupMigracaoManual()
    backup.executar_backup()

if __name__ == "__main__":
    main() 