# Configurações da VPS Externa
# Atualize estas configurações conforme sua VPS

# IP da VPS (substitua pelo IP real da sua VPS)
VPS_IP = "145.223.29.250"  # IP real da sua VPS

# Porta do serviço de upload (padrão: 8080)
UPLOAD_PORT = 8080

# URL base para upload
UPLOAD_BASE_URL = f"http://{VPS_IP}:{UPLOAD_PORT}"

# Endpoints
UPLOAD_ENDPOINT = f"{UPLOAD_BASE_URL}/upload"
HEALTH_ENDPOINT = f"{UPLOAD_BASE_URL}/health"
FILES_ENDPOINT = f"{UPLOAD_BASE_URL}/files"
STATUS_ENDPOINT = f"{UPLOAD_BASE_URL}/status"

# Configurações do banco MySQL (mantidas separadas)
MYSQL_HOST = "pma.megatrends.site"  # Seu domínio phpMyAdmin
MYSQL_PORT = 3306
MYSQL_USER = "seu_usuario"
MYSQL_PASSWORD = "sua_senha"
MYSQL_DATABASE = "seu_banco"

# Configurações de upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = ['jpg', 'jpeg'] 