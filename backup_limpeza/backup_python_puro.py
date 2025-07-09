#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📦 SCRIPT DE BACKUP USANDO PYTHON PURO
Cria backup dos bancos usando apenas Python, sem mysqldump
"""

import os
import mysql.connector
from datetime import datetime
import shutil

class BackupPythonPuro:
    def __init__(self):
        # Servidor origem (funcionando)
        self.servidor_origem = "pma.megatrends.site"
        self.usuario_origem = "root"
        self.senha_origem = "Define@4536#8521"
        
        self.bancos = ["litoral", "teste", "gerenciamento_premiacoes"]
        
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = f"backup_python_{self.timestamp}"
        
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
    
    def obter_estrutura_banco(self, conn, banco):
        """Obtém a estrutura completa do banco"""
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute(f"SHOW TABLES FROM `{banco}`")
        tabelas = [row[0] for row in cursor.fetchall()]
        
        sql_lines = []
        
        # Criar banco
        sql_lines.append(f"CREATE DATABASE IF NOT EXISTS `{banco}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        sql_lines.append(f"USE `{banco}`;")
        sql_lines.append("")
        
        for tabela in tabelas:
            try:
                # Obter estrutura da tabela
                cursor.execute(f"SHOW CREATE TABLE `{banco}`.`{tabela}`")
                create_table = cursor.fetchone()[1]
                sql_lines.append(f"{create_table};")
                sql_lines.append("")
                
                # Obter dados da tabela
                cursor.execute(f"SELECT COUNT(*) FROM `{banco}`.`{tabela}`")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    cursor.execute(f"SELECT * FROM `{banco}`.`{tabela}`")
                    colunas = [desc[0] for desc in cursor.description]
                    
                    # Buscar dados em lotes para não sobrecarregar a memória
                    offset = 0
                    limit = 1000
                    
                    while offset < count:
                        cursor.execute(f"SELECT * FROM `{banco}`.`{tabela}` LIMIT {limit} OFFSET {offset}")
                        rows = cursor.fetchall()
                        
                        if rows:
                            sql_lines.append(f"INSERT INTO `{tabela}` ({', '.join([f'`{col}`' for col in colunas])}) VALUES")
                            
                            values = []
                            for row in rows:
                                row_values = []
                                for val in row:
                                    if val is None:
                                        row_values.append("NULL")
                                    elif isinstance(val, (int, float)):
                                        row_values.append(str(val))
                                    else:
                                        # Escapar aspas simples
                                        escaped_val = str(val).replace("'", "\\'")
                                        row_values.append(f"'{escaped_val}'")
                                values.append(f"({', '.join(row_values)})")
                            
                            sql_lines.append(",\n".join(values) + ";")
                            sql_lines.append("")
                        
                        offset += limit
                        
            except Exception as e:
                self.log(f"⚠️  Erro ao processar tabela '{tabela}': {e}")
                continue
        
        return "\n".join(sql_lines)
    
    def criar_backup(self):
        """Cria backup dos bancos de dados usando Python puro"""
        self.log("📦 Iniciando backup dos bancos de dados...")
        
        os.makedirs(self.backup_dir, exist_ok=True)
        
        try:
            # Conectar ao servidor origem
            conn = mysql.connector.connect(
                host=self.servidor_origem,
                user=self.usuario_origem,
                password=self.senha_origem,
                connect_timeout=30
            )
            
            for banco in self.bancos:
                try:
                    backup_file = f"{self.backup_dir}/{banco}_backup_{self.timestamp}.sql"
                    
                    self.log(f"📥 Fazendo backup do banco '{banco}'...")
                    
                    # Obter estrutura e dados
                    sql_content = self.obter_estrutura_banco(conn, banco)
                    
                    # Salvar arquivo
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        f.write(sql_content)
                    
                    size = os.path.getsize(backup_file)
                    self.log(f"✅ Backup de '{banco}' concluído: {size} bytes")
                    
                except Exception as e:
                    self.log(f"❌ Erro ao fazer backup de '{banco}': {e}")
                    return False
            
            conn.close()
            self.log(f"✅ Todos os backups concluídos em: {self.backup_dir}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro na conexão: {e}")
            return False
    
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
        self.log("🚀 INICIANDO BACKUP USANDO PYTHON PURO")
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
    backup = BackupPythonPuro()
    backup.executar_backup()

if __name__ == "__main__":
    main() 