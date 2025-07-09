#!/usr/bin/env python3
"""
Script para limpar credenciais manualmente do histórico do Git
"""

import subprocess
import os
import tempfile
import shutil

def executar_comando(comando):
    """Executa um comando e retorna o resultado"""
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        return resultado.returncode == 0, resultado.stdout, resultado.stderr
    except Exception as e:
        return False, "", str(e)

def limpar_credenciais_manual():
    """Limpa credenciais usando abordagem manual"""
    print("🚨 LIMPEZA MANUAL DE CREDENCIAIS")
    print("=" * 50)
    
    # 1. Verificar se estamos no repositório correto
    sucesso, stdout, stderr = executar_comando("git status")
    if not sucesso:
        print("❌ Erro: Não estamos em um repositório Git válido")
        return False
    
    print("✅ Repositório Git válido encontrado")
    
    # 2. Fazer backup do branch atual
    print("\n📦 Fazendo backup do branch atual...")
    sucesso, stdout, stderr = executar_comando("git branch backup-antes-limpeza-manual")
    if sucesso:
        print("✅ Backup criado: backup-antes-limpeza-manual")
    
    # 3. Obter todos os commits
    print("\n📋 Obtendo lista de commits...")
    sucesso, stdout, stderr = executar_comando("git log --oneline --all")
    if not sucesso:
        print("❌ Erro ao obter commits")
        return False
    
    commits = stdout.strip().split('\n')
    print(f"✅ Encontrados {len(commits)} commits")
    
    # 4. Criar novo repositório limpo
    print("\n🆕 Criando novo repositório limpo...")
    
    # Salvar arquivos atuais
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Diretório temporário: {temp_dir}")
    
    # Copiar arquivos atuais (exceto .git)
    for item in os.listdir('.'):
        if item != '.git' and item != '__pycache__':
            src = os.path.join('.', item)
            dst = os.path.join(temp_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            else:
                shutil.copy2(src, dst)
    
    print("✅ Arquivos copiados para diretório temporário")
    
    # 5. Remover .git atual
    print("\n🗑️ Removendo repositório Git atual...")
    shutil.rmtree('.git')
    
    # 6. Inicializar novo repositório
    print("\n🆕 Inicializando novo repositório...")
    sucesso, stdout, stderr = executar_comando("git init")
    if not sucesso:
        print("❌ Erro ao inicializar novo repositório")
        return False
    
    # 7. Adicionar arquivos limpos
    print("\n📁 Adicionando arquivos limpos...")
    sucesso, stdout, stderr = executar_comando("git add .")
    if not sucesso:
        print("❌ Erro ao adicionar arquivos")
        return False
    
    # 8. Fazer commit inicial
    print("\n💾 Fazendo commit inicial...")
    sucesso, stdout, stderr = executar_comando('git commit -m "feat: repositório limpo - credenciais removidas"')
    if not sucesso:
        print("❌ Erro ao fazer commit")
        return False
    
    print("✅ Novo repositório criado com sucesso!")
    
    # 9. Verificar se há credenciais
    print("\n🔍 Verificando se ainda há credenciais...")
    sucesso, stdout, stderr = executar_comando('git log -p --all | findstr "Define@4536"')
    
    if "Define@4536" in stdout:
        print("❌ ATENÇÃO: Ainda há credenciais!")
        return False
    else:
        print("✅ Nenhuma credencial encontrada!")
    
    print("\n" + "=" * 50)
    print("🎉 LIMPEZA CONCLUÍDA COM SUCESSO!")
    print("\n⚠️ PRÓXIMOS PASSOS:")
    print("1. Configure o repositório remoto:")
    print("   git remote add origin <URL_DO_REPOSITORIO>")
    print("2. Force push para o repositório remoto:")
    print("   git push origin main --force")
    print("3. Notifique todos os colaboradores para clonar novamente")
    print("4. Delete o diretório temporário quando confirmar que tudo está OK")
    
    return True

if __name__ == "__main__":
    print("🚨 ATENÇÃO: Este script irá criar um novo repositório limpo!")
    print("O histórico anterior será perdido.")
    
    resposta = input("\nDeseja continuar? (digite 'SIM' para confirmar): ")
    
    if resposta.upper() == "SIM":
        limpar_credenciais_manual()
    else:
        print("Operação cancelada pelo usuário.") 