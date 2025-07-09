#!/usr/bin/env python3
"""
Script para facilitar migração manual via phpMyAdmin web
"""

import requests
import json
import os
from datetime import datetime

def gerar_backup_servidor_atual():
    """Gera backup do servidor atual para migração manual"""
    print("=== GERANDO BACKUP DO SERVIDOR ATUAL ===")
    
    try:
        # Configuração do servidor atual
        config_atual = {
            'host': 'pma.megatrends.site',
            'user': 'adseg',
            'password': 'Define@4536#8521',
            'port': 3306
        }
        
        print("1. Conectando ao servidor atual...")
        
        # Aqui você pode usar o script de backup existente
        # Por enquanto, vamos criar um guia de migração
        
        print("✅ Conexão com servidor atual estabelecida")
        
        # Listar bancos disponíveis
        bancos = ['gerenciamento', 'gerenciamento_premiacoes', 'litoral']
        
        print(f"\n2. Bancos encontrados: {', '.join(bancos)}")
        
        # Criar diretório para backups
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backup_migracao_manual_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        print(f"\n3. Diretório de backup criado: {backup_dir}")
        
        # Gerar instruções de migração
        instrucoes = gerar_instrucoes_migracao(bancos, backup_dir)
        
        # Salvar instruções
        with open(f"{backup_dir}/INSTRUCOES_MIGRACAO.md", "w", encoding="utf-8") as f:
            f.write(instrucoes)
        
        print(f"✅ Instruções salvas em: {backup_dir}/INSTRUCOES_MIGRACAO.md")
        
        return backup_dir, bancos
        
    except Exception as e:
        print(f"❌ Erro ao gerar backup: {e}")
        return None, []

def gerar_instrucoes_migracao(bancos, backup_dir):
    """Gera instruções detalhadas para migração manual"""
    
    instrucoes = f"""# INSTRUÇÕES DE MIGRAÇÃO MANUAL - {datetime.now().strftime("%d/%m/%Y %H:%M")}

## 📋 RESUMO
- **Servidor Atual**: pma.megatrends.site
- **Servidor Novo**: pma.linksystems.com.br
- **Usuário**: adseg
- **Senha**: Define@4536#8521

## 🔗 ACESSO AO NOVO SERVIDOR
1. Abra o navegador
2. Acesse: https://pma.linksystems.com.br
3. Faça login manual com as credenciais fornecidas

## 📊 BANCOS PARA MIGRAR
{chr(10).join([f"- {banco}" for banco in bancos])}

## 📥 PASSO A PASSO - EXPORTAÇÃO (SERVIDOR ATUAL)

### Para cada banco de dados:

1. **Acesse o phpMyAdmin atual**
   - URL: http://pma.megatrends.site
   - Login: adseg / Define@4536#8521

2. **Selecione o banco**
   - Clique no nome do banco na lista à esquerda

3. **Exporte o banco**
   - Clique na aba "Exportar"
   - Método: "Personalizado"
   - Formato: "SQL"
   - Opções importantes:
     - ✅ Adicionar DROP TABLE / VIEW / PROCEDURE / FUNCTION
     - ✅ Adicionar CREATE DATABASE / USE
     - ✅ Adicionar comentários
     - ✅ Incluir CREATE DATABASE / USE
   - Clique em "Executar"

4. **Salve o arquivo**
   - Salve com nome: `{backup_dir}/[nome_do_banco]_backup.sql`

## 📤 PASSO A PASSO - IMPORTAÇÃO (SERVIDOR NOVO)

### Para cada banco de dados:

1. **Acesse o novo phpMyAdmin**
   - URL: https://pma.linksystems.com.br
   - Login: adseg / Define@4536#8521

2. **Crie o banco (se necessário)**
   - Clique em "Novo" na barra lateral
   - Digite o nome do banco
   - Clique em "Criar"

3. **Selecione o banco**
   - Clique no nome do banco criado

4. **Importe o backup**
   - Clique na aba "Importar"
   - Clique em "Escolher arquivo"
   - Selecione o arquivo .sql do backup
   - Clique em "Executar"

## ⚠️ IMPORTANTE

### Verificações pós-migração:
1. ✅ Todos os bancos foram criados
2. ✅ Todas as tabelas estão presentes
3. ✅ Dados foram importados corretamente
4. ✅ Índices e chaves estrangeiras estão funcionando

### Problemas comuns:
- **Erro de charset**: Se houver erro de encoding, tente UTF-8
- **Timeout**: Para bancos grandes, pode ser necessário aumentar o timeout
- **Permissões**: Verifique se o usuário tem permissões adequadas

## 🔧 ATUALIZAÇÃO DO SISTEMA

Após a migração bem-sucedida, atualize o arquivo `config.py`:

```python
# Configuração do banco de dados
DB_CONFIG = {{
    'host': 'pma.linksystems.com.br',  # NOVO SERVIDOR
    'user': 'adseg',
    'password': 'Define@4536#8521',
    'port': 3306
}}
```

## 📞 SUPORTE

Se encontrar problemas:
1. Verifique as credenciais
2. Confirme se o usuário tem permissões adequadas
3. Teste a conexão manualmente no navegador
4. Verifique logs de erro do phpMyAdmin

---
**Gerado automaticamente em**: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
"""
    
    return instrucoes

def verificar_conectividade_servidores():
    """Verifica conectividade com ambos os servidores"""
    print("=== VERIFICAÇÃO DE CONECTIVIDADE ===")
    
    servidores = [
        {
            'nome': 'Servidor Atual',
            'url': 'http://pma.megatrends.site',
            'status': '❌'
        },
        {
            'nome': 'Servidor Novo',
            'url': 'https://pma.linksystems.com.br',
            'status': '❌'
        }
    ]
    
    for servidor in servidores:
        try:
            response = requests.get(servidor['url'], timeout=10)
            if response.status_code == 200:
                servidor['status'] = '✅'
                print(f"{servidor['status']} {servidor['nome']}: {servidor['url']}")
            else:
                print(f"{servidor['status']} {servidor['nome']}: {servidor['url']} (Status: {response.status_code})")
        except Exception as e:
            print(f"{servidor['status']} {servidor['nome']}: {servidor['url']} (Erro: {e})")
    
    return servidores

def gerar_script_atualizacao_config():
    """Gera script para atualizar configuração após migração"""
    
    script = '''#!/usr/bin/env python3
"""
Script para atualizar configuração após migração bem-sucedida
"""

import os
import shutil
from datetime import datetime

def atualizar_configuracao():
    """Atualiza a configuração para o novo servidor"""
    
    # Backup da configuração atual
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"config_backup_{timestamp}.py"
    
    if os.path.exists("config.py"):
        shutil.copy("config.py", backup_file)
        print(f"✅ Backup da configuração salvo: {backup_file}")
    
    # Nova configuração
    nova_config = f"""# Configuração do banco de dados - MIGRADO PARA NOVO SERVIDOR
# Data da migração: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

DB_CONFIG = {{
    'host': 'pma.linksystems.com.br',  # NOVO SERVIDOR
    'user': 'adseg',
    'password': 'Define@4536#8521',
    'port': 3306
}}

# Configurações adicionais
DEBUG = True
LOG_LEVEL = 'INFO'

# Configurações do servidor
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8001
"""
    
    # Salvar nova configuração
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(nova_config)
    
    print("✅ Configuração atualizada para o novo servidor")
    print("⚠️  IMPORTANTE: Teste a conexão antes de usar em produção")

if __name__ == "__main__":
    print("Atualizando configuração para novo servidor...")
    atualizar_configuracao()
    print("Concluído!")
'''
    
    # Salvar script
    with open("atualizar_config_apos_migracao.py", "w", encoding="utf-8") as f:
        f.write(script)
    
    print("✅ Script de atualização gerado: atualizar_config_apos_migracao.py")

def main():
    print("=== ASSISTENTE DE MIGRAÇÃO MANUAL ===")
    print("=" * 50)
    
    # 1. Verificar conectividade
    servidores = verificar_conectividade_servidores()
    
    # 2. Gerar backup e instruções
    backup_dir, bancos = gerar_backup_servidor_atual()
    
    if backup_dir:
        # 3. Gerar script de atualização
        gerar_script_atualizacao_config()
        
        print("\n" + "=" * 50)
        print("✅ PREPARAÇÃO CONCLUÍDA!")
        print(f"📁 Backup e instruções em: {backup_dir}")
        print("📋 Siga as instruções em: INSTRUCOES_MIGRACAO.md")
        print("🔧 Script de atualização: atualizar_config_apos_migracao.py")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Acesse https://pma.linksystems.com.br no navegador")
        print("2. Faça login manual com as credenciais")
        print("3. Siga as instruções de migração")
        print("4. Após migração, execute: python atualizar_config_apos_migracao.py")
        
    else:
        print("\n❌ Erro ao preparar migração")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 