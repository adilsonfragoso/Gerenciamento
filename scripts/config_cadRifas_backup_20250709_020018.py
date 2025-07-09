#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurações centralizadas para o script cadRifas_litoral
Versão: v2 - Com download automático do ChromeDriver
"""

import os
import subprocess
import requests
import zipfile
import platform
from pathlib import Path

# =============================================================================
# Configurações do Banco de Dados
# =============================================================================

DATABASE_CONFIG = {
    "host": "pma.megatrends.site",
    "user": "root", 
    "password": os.getenv("DB_PASSWORD", "Define@4536#8521"),
    "database": "litoral"
}

# =============================================================================
# Configurações do Navegador
# =============================================================================

def get_chrome_version():
    """Obtém a versão do Chrome instalada no sistema"""
    try:
        if platform.system() == "Windows":
            # Windows - verifica no registro
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
        elif platform.system() == "Darwin":  # macOS
            # macOS - verifica no Applications
            result = subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                                  capture_output=True, text=True)
            return result.stdout.strip().split()[-1]
        else:  # Linux
            # Linux - verifica com comando
            result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
            return result.stdout.strip().split()[-1]
    except Exception as e:
        print(f"Erro ao obter versão do Chrome: {e}")
        return None

def get_chromedriver_version(chrome_version):
    """Obtém a versão do ChromeDriver compatível com a versão do Chrome"""
    if not chrome_version:
        return None
    
    # Extrai versão major (ex: 137.0.7151.69 -> 137)
    major_version = int(chrome_version.split('.')[0])
    
    # Primeiro tenta a versão major exata
    try:
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            chromedriver_version = response.text.strip()
            print(f"ChromeDriver compatível encontrado: versão {chromedriver_version} (para Chrome {major_version})")
            return chromedriver_version
    except Exception as e:
        print(f"Tentativa para versão major {major_version} falhou: {e}")
    
    # Se não encontrar, tenta versões major anteriores
    for version_to_try in range(major_version - 1, major_version - 10, -1):  # Tenta até 10 versões major anteriores
        try:
            # Consulta a API do ChromeDriver para obter a versão mais recente
            url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version_to_try}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                chromedriver_version = response.text.strip()
                print(f"ChromeDriver compatível encontrado: versão {chromedriver_version} (para Chrome {version_to_try})")
                return chromedriver_version
        except Exception as e:
            print(f"Tentativa para versão major {version_to_try} falhou: {e}")
            continue
    
    print(f"Não foi possível encontrar ChromeDriver compatível para Chrome {major_version}")
    return None

def download_chromedriver(version, download_path):
    """Faz download do ChromeDriver compatível"""
    try:
        # Determina a plataforma
        if platform.system() == "Windows":
            platform_name = "win32"
        elif platform.system() == "Darwin":  # macOS
            platform_name = "mac64"
        else:  # Linux
            platform_name = "linux64"
        
        # URL do download
        url = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_{platform_name}.zip"
        
        print(f"Baixando ChromeDriver {version} para {platform_name}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Salva o arquivo ZIP
        zip_path = download_path / "chromedriver.zip"
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extrai o ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(download_path)
        
        # Remove o ZIP
        zip_path.unlink()
        
        # Define permissões de execução (Linux/macOS)
        if platform.system() != "Windows":
            chromedriver_path = download_path / "chromedriver"
            chromedriver_path.chmod(0o755)
        
        print(f"ChromeDriver {version} baixado com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao baixar ChromeDriver: {e}")
        return False

def get_chromedriver_path():
    """Obtém o caminho do ChromeDriver, baixando automaticamente se necessário"""
    # Pasta para armazenar o ChromeDriver
    download_path = Path("D:/Documentos/Workspace/chromedriver")
    download_path.mkdir(exist_ok=True)
    
    # Caminho do executável
    if platform.system() == "Windows":
        chromedriver_exe = download_path / "chromedriver.exe"
    else:
        chromedriver_exe = download_path / "chromedriver"
    
    # Se já existe, verifica se está funcionando
    if chromedriver_exe.exists():
        try:
            # Testa se o ChromeDriver funciona
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            service = Service(str(chromedriver_exe))
            driver = webdriver.Chrome(service=service)
            driver.quit()
            print(f"ChromeDriver encontrado e funcionando: {chromedriver_exe}")
            return str(chromedriver_exe)
        except Exception as e:
            print(f"ChromeDriver existente não funciona: {e}")
            # Remove o arquivo corrompido
            chromedriver_exe.unlink(missing_ok=True)
    
    # Obtém versão do Chrome
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("Não foi possível detectar a versão do Chrome. Verifique se o Chrome está instalado.")
        return None
    
    print(f"Versão do Chrome detectada: {chrome_version}")
    
    # Obtém versão compatível do ChromeDriver
    chromedriver_version = get_chromedriver_version(chrome_version)
    if not chromedriver_version:
        print("Não foi possível obter a versão compatível do ChromeDriver.")
        return None
    
    print(f"Versão do ChromeDriver necessária: {chromedriver_version}")
    
    # Faz download
    if download_chromedriver(chromedriver_version, download_path):
        return str(chromedriver_exe)
    
    return None

# Obtém o caminho do ChromeDriver automaticamente
CHROMEDRIVER_PATH = get_chromedriver_path()

BROWSER_CONFIG = {
    "driver_path": CHROMEDRIVER_PATH,
    "options": [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",
        "--disable-javascript",
        "--disable-css",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor"
    ]
}

# =============================================================================
# Configurações de Login
# =============================================================================

LOGIN_CONFIG = {
    "url": "https://painel.litoraldasorte.com",
    "email": "dev",
    "password": "453629"
}

# =============================================================================
# Configurações de Pagamento
# =============================================================================

PAYMENT_CONFIG = {
    "client_id": "11151160128039923883",
    "client_secret": "jZlYzM0NDMtMGMzZC00NzkyLWI1N2ItN",
    "chave_pix": "4437d697-f765-45f8-89be-213dda9862c5"
}

# =============================================================================
# Configurações de Arquivos
# =============================================================================

FILE_CONFIG = {
    "pasta_imagens": os.path.abspath(os.path.join(os.path.dirname(__file__), "../uploads")),
    "links_gerados": "D:/Documentos/Workspace/ativos/links_gerados.txt"
}

# =============================================================================
# Configurações de URLs
# =============================================================================

URL_CONFIG = {
    "litoral": "https://litoraldasorte.com/campanha/",
    "rapidas": "https://rifasrapidas.com/"
}

# =============================================================================
# Configurações de Timeout
# =============================================================================

TIMEOUT_CONFIG = {
    "element_wait": 10,
    "page_load": 30,
    "retry_delay": 2
}

# =============================================================================
# Configurações de Logging
# =============================================================================

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.path.abspath(os.path.join(os.path.dirname(__file__), "logs/cadRifas.log"))
}

# =============================================================================
# Configurações de Retry
# =============================================================================

RETRY_CONFIG = {
    "max_attempts": 3,
    "delay_between_attempts": 5
}

# =============================================================================
# Funções de Validação
# =============================================================================

def validar_configuracoes():
    """Valida se todas as configurações estão corretas"""
    # Verificar se o ChromeDriver está disponível
    if not CHROMEDRIVER_PATH:
        raise ValueError("ChromeDriver não está disponível. Verifique se o Chrome está instalado.")
    
    # Verificar se a pasta de imagens existe
    if not os.path.exists(FILE_CONFIG["pasta_imagens"]):
        raise ValueError(f"Pasta de imagens não encontrada: {FILE_CONFIG['pasta_imagens']}")
    
    # Verificar se as credenciais estão definidas
    if not LOGIN_CONFIG["email"] or not LOGIN_CONFIG["password"]:
        raise ValueError("Credenciais de login não estão definidas")
    
    # Verificar se as configurações de pagamento estão definidas
    if not all(PAYMENT_CONFIG.values()):
        raise ValueError("Configurações de pagamento incompletas")

def criar_pasta_logs():
    """Cria a pasta de logs se não existir"""
    log_dir = os.path.dirname(LOGGING_CONFIG["file"])
    os.makedirs(log_dir, exist_ok=True) 