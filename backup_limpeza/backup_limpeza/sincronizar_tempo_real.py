#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 SINCRONIZAÇÃO EM TEMPO REAL
Mantém pma.linksystems.com.br como espelho de pma.megatrends.site
"""

import mysql.connector
import time
import json
import hashlib
import threading
from datetime import datetime
import logging

class SincronizadorTempoReal:
    def __init__(self):
        # Configurações dos servidores
        self.servidor_origem = "pma.megatrends.site"
        self.servidor_destino = "pma.linksystems.com.br"
        self.usuario_origem = "root"
        self.usuario_destino = "adseg"
        self.senha_origem = "Define@4536#8521"
        self.senha_destino = "Define@4536#8521"
        
        # Bancos a sincronizar
        self.bancos = ["litoral", "teste", "gerenciamento_premiacoes"]
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sincronizacao_tempo_real.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Controle de sincronização
        self.ativo = False
        self.estatisticas = {
            'inicio': None,
            'total_operacoes': 0,
            'erros': 0,
            'ultima_sincronizacao': None
        }
    
    def conectar_origem(self):
        """Conecta ao servidor de origem"""
        try:
            return mysql.connector.connect(
                host=self.servidor_origem,
                user=self.usuario_origem,
                password=self.senha_origem,
                autocommit=True,
                connect_timeout=10
            )
        except Exception as e:
            self.logger.error(f"Erro ao conectar origem: {e}")
            return None
    
    def conectar_destino(self):
        """Conecta ao servidor de destino"""
        try:
            return mysql.connector.connect(
                host=self.servidor_destino,
                user=self.usuario_destino,
                password=self.senha_destino,
                autocommit=True,
                connect_timeout=10
            )
        except Exception as e:
            self.logger.error(f"Erro ao conectar destino: {e}")
            return None
    
    def obter_hash_tabela(self, conn, banco, tabela):
        """Obtém hash dos dados de uma tabela"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"USE {banco}")
            cursor.execute(f"SELECT * FROM {tabela} ORDER BY 1")
            dados = cursor.fetchall()
            cursor.close()
            
            # Criar hash dos dados
            dados_str = str(dados).encode('utf-8')
            return hashlib.md5(dados_str).hexdigest()
        except Exception as e:
            self.logger.error(f"Erro ao obter hash da tabela {banco}.{tabela}: {e}")
            return None
    
    def obter_tabelas_banco(self, conn, banco):
        """Obtém lista de tabelas de um banco"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"USE {banco}")
            cursor.execute("SHOW TABLES")
            tabelas = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tabelas
        except Exception as e:
            self.logger.error(f"Erro ao obter tabelas do banco {banco}: {e}")
            return []
    
    def sincronizar_tabela(self, banco, tabela):
        """Sincroniza uma tabela específica"""
        try:
            conn_origem = self.conectar_origem()
            conn_destino = self.conectar_destino()
            
            if not conn_origem or not conn_destino:
                return False
            
            # Obter dados da origem
            cursor_origem = conn_origem.cursor()
            cursor_origem.execute(f"USE {banco}")
            cursor_origem.execute(f"SELECT * FROM {tabela}")
            dados = cursor_origem.fetchall()
            
            # Obter estrutura da tabela
            cursor_origem.execute(f"SHOW CREATE TABLE {tabela}")
            create_table = cursor_origem.fetchone()[1]
            
            # Limpar tabela no destino e recriar
            cursor_destino = conn_destino.cursor()
            cursor_destino.execute(f"USE {banco}")
            cursor_destino.execute(f"DROP TABLE IF EXISTS {tabela}")
            cursor_destino.execute(create_table)
            
            # Inserir dados se houver
            if dados:
                # Obter colunas
                cursor_origem.execute(f"DESCRIBE {tabela}")
                colunas = [row[0] for row in cursor_origem.fetchall()]
                
                # Preparar INSERT
                placeholders = ', '.join(['%s'] * len(colunas))
                sql = f"INSERT INTO {tabela} VALUES ({placeholders})"
                
                cursor_destino.executemany(sql, dados)
            
            cursor_origem.close()
            cursor_destino.close()
            conn_origem.close()
            conn_destino.close()
            
            self.logger.info(f"✅ Tabela {banco}.{tabela} sincronizada ({len(dados)} registros)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao sincronizar tabela {banco}.{tabela}: {e}")
            return False
    
    def verificar_diferencas(self):
        """Verifica diferenças entre os servidores"""
        try:
            conn_origem = self.conectar_origem()
            conn_destino = self.conectar_destino()
            
            if not conn_origem or not conn_destino:
                return []
            
            diferencas = []
            
            for banco in self.bancos:
                self.logger.info(f"🔍 Verificando banco: {banco}")
                
                # Obter tabelas
                tabelas = self.obter_tabelas_banco(conn_origem, banco)
                
                for tabela in tabelas:
                    hash_origem = self.obter_hash_tabela(conn_origem, banco, tabela)
                    hash_destino = self.obter_hash_tabela(conn_destino, banco, tabela)
                    
                    if hash_origem != hash_destino:
                        diferencas.append({
                            'banco': banco,
                            'tabela': tabela,
                            'hash_origem': hash_origem,
                            'hash_destino': hash_destino
                        })
                        self.logger.warning(f"⚠️ Diferença detectada: {banco}.{tabela}")
            
            conn_origem.close()
            conn_destino.close()
            
            return diferencas
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar diferenças: {e}")
            return []
    
    def sincronizacao_inicial(self):
        """Executa sincronização inicial completa"""
        self.logger.info("🚀 Iniciando sincronização inicial...")
        
        try:
            conn_origem = self.conectar_origem()
            conn_destino = self.conectar_destino()
            
            if not conn_origem or not conn_destino:
                return False
            
            total_tabelas = 0
            sucesso = 0
            
            for banco in self.bancos:
                self.logger.info(f"📁 Processando banco: {banco}")
                
                # Criar banco no destino se não existir
                cursor_destino = conn_destino.cursor()
                cursor_destino.execute(f"CREATE DATABASE IF NOT EXISTS {banco}")
                cursor_destino.close()
                
                # Obter e sincronizar todas as tabelas
                tabelas = self.obter_tabelas_banco(conn_origem, banco)
                
                for tabela in tabelas:
                    total_tabelas += 1
                    if self.sincronizar_tabela(banco, tabela):
                        sucesso += 1
                    
                    # Pequena pausa para não sobrecarregar
                    time.sleep(0.1)
            
            conn_origem.close()
            conn_destino.close()
            
            self.logger.info(f"✅ Sincronização inicial concluída: {sucesso}/{total_tabelas} tabelas")
            return sucesso == total_tabelas
            
        except Exception as e:
            self.logger.error(f"❌ Erro na sincronização inicial: {e}")
            return False
    
    def monitorar_continuamente(self):
        """Monitora e sincroniza continuamente"""
        self.logger.info("🔄 Iniciando monitoramento contínuo...")
        self.ativo = True
        self.estatisticas['inicio'] = datetime.now()
        
        while self.ativo:
            try:
                inicio_ciclo = datetime.now()
                
                # Verificar diferenças
                diferencas = self.verificar_diferencas()
                
                if diferencas:
                    self.logger.info(f"🔧 Sincronizando {len(diferencas)} diferenças...")
                    
                    for diff in diferencas:
                        if self.sincronizar_tabela(diff['banco'], diff['tabela']):
                            self.estatisticas['total_operacoes'] += 1
                        else:
                            self.estatisticas['erros'] += 1
                
                self.estatisticas['ultima_sincronizacao'] = datetime.now()
                
                # Aguardar próximo ciclo (30 segundos)
                time.sleep(30)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Interrompido pelo usuário")
                break
            except Exception as e:
                self.logger.error(f"❌ Erro no monitoramento: {e}")
                self.estatisticas['erros'] += 1
                time.sleep(10)  # Aguardar um pouco antes de tentar novamente
        
        self.ativo = False
        self.logger.info("🔄 Monitoramento interrompido")
    
    def parar_sincronizacao(self):
        """Para a sincronização"""
        self.ativo = False
        self.logger.info("🛑 Parando sincronização...")
    
    def obter_status(self):
        """Obtém status da sincronização"""
        return {
            'ativo': self.ativo,
            'estatisticas': self.estatisticas,
            'servidores': {
                'origem': self.servidor_origem,
                'destino': self.servidor_destino
            }
        }

def main():
    """Função principal"""
    sincronizador = SincronizadorTempoReal()
    
    print("🔄 SINCRONIZAÇÃO EM TEMPO REAL")
    print("=" * 50)
    print("1. Sincronização inicial completa")
    print("2. Monitoramento contínuo")
    print("3. Verificar diferenças apenas")
    print("4. Status da sincronização")
    print("0. Sair")
    
    while True:
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n🚀 Executando sincronização inicial...")
            if sincronizador.sincronizacao_inicial():
                print("✅ Sincronização inicial concluída com sucesso!")
            else:
                print("❌ Erro na sincronização inicial")
        
        elif opcao == "2":
            print("\n🔄 Iniciando monitoramento contínuo...")
            print("Pressione Ctrl+C para parar")
            try:
                sincronizador.monitorar_continuamente()
            except KeyboardInterrupt:
                sincronizador.parar_sincronizacao()
        
        elif opcao == "3":
            print("\n🔍 Verificando diferenças...")
            diferencas = sincronizador.verificar_diferencas()
            if diferencas:
                print(f"⚠️ {len(diferencas)} diferenças encontradas:")
                for diff in diferencas:
                    print(f"  - {diff['banco']}.{diff['tabela']}")
            else:
                print("✅ Nenhuma diferença encontrada")
        
        elif opcao == "4":
            status = sincronizador.obter_status()
            print(f"\n📊 STATUS DA SINCRONIZAÇÃO")
            print(f"Ativo: {status['ativo']}")
            print(f"Total de operações: {status['estatisticas']['total_operacoes']}")
            print(f"Erros: {status['estatisticas']['erros']}")
            if status['estatisticas']['ultima_sincronizacao']:
                print(f"Última sincronização: {status['estatisticas']['ultima_sincronizacao']}")
        
        elif opcao == "0":
            if sincronizador.ativo:
                sincronizador.parar_sincronizacao()
            print("👋 Saindo...")
            break
        
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main() 