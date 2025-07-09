# 🐳 Stack Docker para Upload de Imagens - ISOLADA

Solução completa e **ISOLADA** para upload de imagens na VPS externa usando Docker e Portainer.

## ⚠️ IMPORTANTE: Stack Completamente Isolada

Esta stack é **COMPLETAMENTE ISOLADA** da sua stack phpMyAdmin:
- **Porta:** 8080 (não interfere com porta 80)
- **Domínio:** IP direto da VPS (não usa pma.megatrends.site)
- **Rede:** Rede Docker separada
- **Volumes:** Volumes independentes
- **Sem conflitos:** Não interfere com serviços existentes

## 🚀 Deploy Rápido

### Opção 1: Via Portainer (Recomendado)

1. **Copie os arquivos para a VPS:**
   ```bash
   # Na VPS, criar pasta
   mkdir -p ~/gerenciamento-upload
   cd ~/gerenciamento-upload
   
   # Copiar arquivos do projeto local
   # docker-compose-upload.yml, Dockerfile, requirements.txt, nginx.conf, upload_server_vps.py
   ```

2. **No Portainer:**
   - Acesse o Portainer
   - Vá para **Stacks** → **Add stack**
   - Nome: `gerenciamento-upload`
   - Cole o conteúdo do `docker-compose-upload.yml`
   - Clique em **Deploy the stack**

### Opção 2: Via Script Automático

```bash
# Na VPS, execute o script
chmod +x deploy_portainer.sh
./deploy_portainer.sh
```

### Opção 3: Via Linha de Comando

```bash
# Na VPS
cd ~/gerenciamento-upload
docker-compose -f docker-compose-upload.yml up -d
```

## 📁 Estrutura da Stack

```
gerenciamento-upload/
├── upload-server/          # Flask app (porta 5000)
│   ├── upload_server_vps.py
│   ├── requirements.txt
│   └── logs/
├── nginx-proxy/           # Nginx proxy (porta 8080)
│   └── nginx.conf
├── uploads_data/          # Volume persistente
└── logs/                  # Logs da aplicação
```

## 🌐 Endpoints

**Substitua `SEU_IP_VPS` pelo IP real da sua VPS:**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `http://SEU_IP_VPS:8080/upload` | POST | Upload de imagens |
| `http://SEU_IP_VPS:8080/health` | GET | Health check |
| `http://SEU_IP_VPS:8080/files` | GET | Listar arquivos |
| `http://SEU_IP_VPS:8080/uploads/arquivo.jpg` | GET | Acessar imagem |
| `http://SEU_IP_VPS:8080/status` | GET | Status do serviço |

## 🔧 Configuração

### 1. Descobrir IP da VPS

```bash
# Na VPS, descubra o IP
ip addr show
# ou
hostname -I
```

### 2. Atualizar config.py Local

No seu projeto local, edite o arquivo `config.py`:

```python
# Substitua pelo IP real da sua VPS
VPS_IP = "192.168.1.100"  # Exemplo - use o IP real da sua VPS

# Porta do serviço de upload
UPLOAD_PORT = 8080

# URL base para upload
UPLOAD_BASE_URL = f"http://{VPS_IP}:{UPLOAD_PORT}"

# Endpoints
UPLOAD_ENDPOINT = f"{UPLOAD_BASE_URL}/upload"
HEALTH_ENDPOINT = f"{UPLOAD_BASE_URL}/health"
FILES_ENDPOINT = f"{UPLOAD_BASE_URL}/files"
STATUS_ENDPOINT = f"{UPLOAD_BASE_URL}/status"
```

### Variáveis de Ambiente

```yaml
environment:
  - UPLOAD_FOLDER=/uploads
  - MAX_FILE_SIZE=10485760  # 10MB
  - ALLOWED_EXTENSIONS=jpg,jpeg
```

### Volumes

- `uploads_data`: Armazena as imagens
- `./logs`: Logs da aplicação

## 📊 Monitoramento

### Via Portainer

1. **Status dos Containers:**
   - Vá para **Containers**
   - Verifique `gerenciamento-upload-server` e `gerenciamento-nginx-proxy`

2. **Logs em Tempo Real:**
   - Clique no container
   - Vá para **Logs**
   - Monitore em tempo real

3. **Métricas:**
   - CPU, Memória, Rede
   - Configurar alertas

### Via Linha de Comando

```bash
# Status
docker-compose -f docker-compose-upload.yml ps

# Logs
docker-compose -f docker-compose-upload.yml logs -f

# Health check (substitua SEU_IP_VPS)
curl http://SEU_IP_VPS:8080/health
```

## 🔒 Segurança

### Firewall

```bash
# Permitir porta 8080 para upload
sudo ufw allow 8080

# Manter porta 80 para phpMyAdmin
sudo ufw allow 80
```

### SSL/HTTPS (Opcional)

Para adicionar HTTPS, configure um proxy reverso com Let's Encrypt:

```yaml
services:
  nginx-proxy:
    ports:
      - "8443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
```

## 💾 Backup

### Backup Automático

```bash
# Backup das imagens
docker run --rm -v gerenciamento-upload_uploads_data:/uploads -v $(pwd):/backup alpine tar czf /backup/uploads_backup_$(date +%Y%m%d).tar.gz -C /uploads .

# Backup dos logs
docker run --rm -v gerenciamento-upload_logs:/logs -v $(pwd):/backup alpine tar czf /backup/logs_backup_$(date +%Y%m%d).tar.gz -C /logs .
```

### Script de Backup Automático

```bash
#!/bin/bash
# backup_uploads.sh

BACKUP_DIR="/backup/uploads"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup das imagens
docker run --rm \
  -v gerenciamento-upload_uploads_data:/uploads \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/uploads_$DATE.tar.gz -C /uploads .

# Manter apenas os últimos 7 backups
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +7 -delete

echo "Backup criado: uploads_$DATE.tar.gz"
```

## 🔄 Atualizações

### Via Portainer

1. Vá para **Stacks**
2. Clique em **gerenciamento-upload**
3. Clique em **Editor**
4. Atualize o código
5. Clique em **Update the stack**

### Via Linha de Comando

```bash
# Parar
docker-compose -f docker-compose-upload.yml down

# Rebuild
docker-compose -f docker-compose-upload.yml build --no-cache

# Subir
docker-compose -f docker-compose-upload.yml up -d
```

## 🛠️ Troubleshooting

### Problemas Comuns

#### 1. Stack não sobe

```bash
# Verificar logs
docker-compose -f docker-compose-upload.yml logs

# Verificar portas
netstat -tlnp | grep :8080
netstat -tlnp | grep :5000

# Verificar volumes
docker volume ls | grep uploads
```

#### 2. Upload falha

```bash
# Testar conectividade (substitua SEU_IP_VPS)
curl -X POST -F "file=@test.jpg" -F "sigla=TESTE" http://SEU_IP_VPS:8080/upload

# Verificar permissões
docker exec gerenciamento-upload-server ls -la /uploads

# Verificar logs do Nginx
docker logs gerenciamento-nginx-proxy
```

#### 3. Imagens não carregam

```bash
# Verificar se as imagens existem
docker exec gerenciamento-upload-server ls -la /uploads

# Verificar logs do Nginx
docker logs gerenciamento-nginx-proxy

# Testar acesso direto (substitua SEU_IP_VPS)
curl -I http://SEU_IP_VPS:8080/uploads/arquivo.jpg
```

## 🧹 Limpeza

### Remover Completamente

```bash
# Parar e remover containers
docker-compose -f docker-compose-upload.yml down

# Remover volumes (CUIDADO: perde as imagens!)
docker volume rm gerenciamento-upload_uploads_data

# Remover imagens
docker rmi gerenciamento-upload_upload-server
```

## ✅ Vantagens da Solução Docker

- **Isolamento Total:** Stack completamente separada da phpMyAdmin
- **Sem Conflitos:** Porta 8080 não interfere com porta 80
- **Escalabilidade:** Fácil de escalar horizontalmente
- **Monitoramento:** Logs e métricas integrados
- **Backup:** Volumes persistentes
- **Segurança:** Proxy reverso com Nginx
- **Manutenção:** Atualizações simples via Portainer
- **Portabilidade:** Funciona em qualquer VPS com Docker
- **Rollback:** Fácil reverter para versões anteriores
- **CI/CD:** Integração com pipelines de deploy

## 📞 Suporte

Para problemas ou dúvidas:

1. Verifique os logs: `docker-compose -f docker-compose-upload.yml logs`
2. Teste o health check: `curl http://SEU_IP_VPS:8080/health`
3. Verifique o status: `docker-compose -f docker-compose-upload.yml ps`
4. Consulte a documentação do Portainer

## 🔗 Links Úteis

- [Documentação Docker Compose](https://docs.docker.com/compose/)
- [Documentação Portainer](https://docs.portainer.io/)
- [Documentação Nginx](https://nginx.org/en/docs/)
- [Documentação Flask](https://flask.palletsprojects.com/) 