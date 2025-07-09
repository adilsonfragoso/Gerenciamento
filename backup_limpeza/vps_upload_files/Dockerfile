FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY upload_server_vps.py .

# Criar diretório de uploads
RUN mkdir -p /uploads /app/logs

# Definir permissões
RUN chmod 755 /uploads

# Expor porta
EXPOSE 5000

# Comando para executar a aplicação
CMD ["python", "upload_server_vps.py"] 