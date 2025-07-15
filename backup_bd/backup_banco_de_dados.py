#!/usr/bin/env python3
# backup_banco_de_dados.py
"""
Faz dump dos bancos listados em SYNC_DATABASES, usando as variáveis definidas no .env,
e salva em <BACKUP_DIR>/<db>_YYYY-MM-DD.sql.gz.

Pré‑requisitos:
  pip install python-dotenv
  mysqldump disponível no PATH (vem com o MySQL Installer no Windows)
"""

import os, subprocess, gzip, shutil, datetime as dt
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv

print("🔧  Iniciando script de backup...")

# ───────────────────────── Configurações ───────────────────────
# Carrega .env do diretório pai
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

HOST = os.getenv("SYNC_DB_HOST_ORIGEM", "localhost")
USER = os.getenv("SYNC_DB_USER_ORIGEM")
PWD  = os.getenv("SYNC_DB_PASSWORD_ORIGEM")
DBS  = [db.strip() for db in os.getenv("SYNC_DATABASES", "").split(",") if db.strip()]

if not USER:
    USER = input("Usuário DB origem: ")
if not PWD:
    PWD = getpass("Senha DB origem: ")

# Configuração do mysqldump - tenta encontrar automaticamente
MYSQLDUMP_PATHS = [
    "mysqldump",  # Se estiver no PATH
    "C:/xampp/mysql/bin/mysqldump.exe",  # XAMPP padrão
    "C:/Program Files/MySQL/MySQL Server 8.0/bin/mysqldump.exe",  # MySQL 8.0
    "C:/Program Files/MySQL/MySQL Server 5.7/bin/mysqldump.exe",  # MySQL 5.7
    "C:/Program Files/MySQL/MySQL Workbench 8.0/mysqldump.exe",  # MySQL Workbench
]

def find_mysqldump():
    """Encontra o executável mysqldump"""
    for path in MYSQLDUMP_PATHS:
        try:
            subprocess.check_call([path, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return path
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None

MYSQLDUMP_CMD = find_mysqldump()

# pasta onde os dumps serão salvos (altere à vontade / pode usar rede)
BACKUP_DIR = Path(os.getenv("BACKUP_DIR", r"D:\Backups")).expanduser()
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# ───────────────────────── Funções ─────────────────────────────
def cleanup_old_backups(db_name: str, keep_days: int = 5):
    """Remove backups mais antigos que keep_days"""
    today = dt.date.today()
    cutoff_date = today - dt.timedelta(days=keep_days)
    
    removed_count = 0
    pattern = f"{db_name}_*.sql.gz"
    
    for backup_file in BACKUP_DIR.glob(pattern):
        try:
            # Extrai a data do nome do arquivo (formato: db_YYYY-MM-DD.sql.gz)
            date_str = backup_file.stem.split('_', 1)[1].replace('.sql', '')
            backup_date = dt.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            if backup_date < cutoff_date:
                backup_file.unlink()
                removed_count += 1
                print(f"🗑️  Removido backup antigo: {backup_file.name}")
                
        except (ValueError, IndexError):
            # Se não conseguir extrair a data, ignora o arquivo
            continue
    
    if removed_count > 0:
        print(f"🧹  Limpeza concluída: {removed_count} backup(s) antigo(s) removido(s)")
    
    return removed_count

def dump_database(db_name: str):
    today      = dt.date.today().isoformat()
    dump_path  = BACKUP_DIR / f"{db_name}_{today}.sql"
    gz_path    = dump_path.with_suffix(".sql.gz")

    # Verifica se já existe backup para hoje
    if gz_path.exists():
        size_mb = gz_path.stat().st_size / (1024 * 1024)
        print(f"\n⏭️  Backup do banco {db_name} já existe para hoje: {gz_path.name} ({size_mb:.2f} MB)")
        print("   Pulando criação de novo backup...")
        return True
    
    print(f"\n📦  Criando dump do banco {db_name} → {gz_path.name}")
    
    if not MYSQLDUMP_CMD:
        print("❌  mysqldump não encontrado. Verifique se o MySQL está instalado.")
        return False
    
    print(f"🔧  Usando mysqldump: {MYSQLDUMP_CMD}")
    
    cmd = [
        MYSQLDUMP_CMD,
        "-h", HOST,
        "-u", USER,
        f"-p{PWD}",
        "--routines", "--triggers", "--events",
        "--single-transaction",  # Para consistência
        "--databases", db_name,
    ]
    
    try:
        with dump_path.open("wb") as f:
            subprocess.check_call(cmd, stdout=f)

        # compacta
        with dump_path.open("rb") as src, gzip.open(gz_path, "wb") as dst:
            shutil.copyfileobj(src, dst)
        dump_path.unlink()          # remove o .sql "cru"
        
        # Mostrar tamanho do arquivo
        size_mb = gz_path.stat().st_size / (1024 * 1024)
        print(f"✅  Backup criado! Arquivo: {gz_path.name} ({size_mb:.2f} MB)")
        
        # Limpa backups antigos após criar o novo
        cleanup_old_backups(db_name)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌  Erro no mysqldump (código {e.returncode})")
        if dump_path.exists():
            dump_path.unlink()
        return False

# ───────────────────────── Execução ────────────────────────────
if __name__ == "__main__":
    print("🗂️  Iniciando sistema de backup com rotação de 5 dias...")
    print(f"📁  Diretório de backup: {BACKUP_DIR}")
    print(f"🎯  Bancos configurados: {', '.join(DBS)}")
    print(f"📅  Data atual: {dt.date.today()}")

    if not DBS:
        print("❌  A variável SYNC_DATABASES está vazia no .env — nada a fazer.")
        exit(1)

    if not MYSQLDUMP_CMD:
        print("❌  mysqldump não encontrado em nenhum local padrão.")
        print("💡  Instale o MySQL Client ou XAMPP para ter acesso ao mysqldump.")
        exit(1)

    sucessos = 0
    falhas = 0
    pulados = 0

    for db in DBS:
        # Verifica se já existe backup para hoje antes de tentar criar
        today = dt.date.today().isoformat()
        gz_path = BACKUP_DIR / f"{db}_{today}.sql.gz"
        
        if gz_path.exists():
            pulados += 1
            size_mb = gz_path.stat().st_size / (1024 * 1024)
            print(f"\n⏭️  Backup do banco {db} já existe para hoje: {gz_path.name} ({size_mb:.2f} MB)")
            print("   Executando apenas limpeza de backups antigos...")
            cleanup_old_backups(db)
        else:
            if dump_database(db):
                sucessos += 1
            else:
                falhas += 1

    print(f"\n📊  Resumo da execução:")
    print(f"✅  Novos backups criados: {sucessos}")
    print(f"⏭️  Backups já existentes (pulados): {pulados}")
    print(f"❌  Falhas: {falhas}")
    print(f"📁  Diretório: {BACKUP_DIR}")

    if falhas > 0:
        exit(1)
