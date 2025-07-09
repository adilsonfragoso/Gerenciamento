#!/bin/bash

# Script de Deploy para Portainer - Stack ISOLADA
# Execute este script na VPS para configurar a stack de upload isolada

echo "=== Deploy da Stack de Upload ISOLADA para Portainer ==="
echo "⚠️  IMPORTANTE: Esta stack é COMPLETAMENTE ISOLADA da phpMyAdmin"
echo "   • Porta: 8080 (não interfere com porta 80)"
echo "   • Domínio: IP direto da VPS (não usa pma.megatrends.site)"
echo "   • Rede: Docker separada"
echo "   • Volumes: Independentes"
echo ""

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker instalado. Faça logout e login novamente."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose instalado."
fi

# Criar diretório do projeto
PROJECT_DIR="$HOME/gerenciamento-upload"
echo "📁 Criando diretório: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Verificar se os arquivos existem
REQUIRED_FILES=("docker-compose-upload.yml" "Dockerfile" "requirements.txt" "nginx.conf" "upload_server_vps.py")

echo "🔍 Verificando arquivos necessários..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Arquivo $file não encontrado!"
        echo "   Certifique-se de que todos os arquivos estão no diretório atual."
        exit 1
    fi
done

echo "✅ Todos os arquivos encontrados!"

# Criar diretório de logs
mkdir -p logs

# Verificar se a porta 8080 está em uso
if netstat -tlnp | grep :8080 > /dev/null; then
    echo "⚠️  Porta 8080 já está em uso. Verificando..."
    netstat -tlnp | grep :8080
    echo ""
    read -p "Deseja continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deploy cancelado."
        exit 1
    fi
fi

# Parar stack existente se houver
echo "🛑 Parando stack existente (se houver)..."
docker-compose -f docker-compose-upload.yml down 2>/dev/null || true

# Remover containers antigos
echo "🧹 Limpando containers antigos..."
docker container prune -f

# Build da imagem
echo "🔨 Fazendo build da imagem..."
docker-compose -f docker-compose-upload.yml build --no-cache

if [ $? -ne 0 ]; then
    echo "❌ Erro no build da imagem!"
    exit 1
fi

# Subir a stack
echo "🚀 Subindo a stack..."
docker-compose -f docker-compose-upload.yml up -d

if [ $? -ne 0 ]; then
    echo "❌ Erro ao subir a stack!"
    exit 1
fi

# Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 10

# Verificar status
echo "📊 Verificando status dos containers..."
docker-compose -f docker-compose-upload.yml ps

# Testar health check
echo "🏥 Testando health check..."
sleep 5

if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Health check passou!"
else
    echo "⚠️  Health check falhou. Verificando logs..."
    docker-compose -f docker-compose-upload.yml logs --tail=20
fi

# Obter IP da VPS
VPS_IP=$(hostname -I | awk '{print $1}')

# Mostrar informações finais
echo ""
echo "🎉 Deploy concluído com sucesso!"
echo ""
echo "📋 Informações da Stack ISOLADA:"
echo "   • Nome: gerenciamento-upload"
echo "   • Upload: http://$VPS_IP:8080/upload"
echo "   • Health: http://$VPS_IP:8080/health"
echo "   • Status: http://$VPS_IP:8080/status"
echo "   • Files: http://$VPS_IP:8080/files"
echo ""
echo "📁 Volumes criados:"
echo "   • uploads_data: $(docker volume ls | grep uploads_data || echo 'Não encontrado')"
echo ""
echo "🔧 Comandos úteis:"
echo "   • Ver logs: docker-compose -f docker-compose-upload.yml logs -f"
echo "   • Parar: docker-compose -f docker-compose-upload.yml down"
echo "   • Reiniciar: docker-compose -f docker-compose-upload.yml restart"
echo "   • Status: docker-compose -f docker-compose-upload.yml ps"
echo ""
echo "🌐 Para acessar via IP da VPS:"
echo "   • Upload: http://$VPS_IP:8080/upload"
echo "   • Health: http://$VPS_IP:8080/health"
echo "   • Images: http://$VPS_IP:8080/uploads/arquivo.jpg"
echo ""
echo "📝 Próximos passos:"
echo "   1. Configure o firewall para permitir porta 8080"
echo "   2. Atualize o arquivo config.py no projeto local com o IP: $VPS_IP"
echo "   3. Teste o upload via interface web"
echo "   4. Configure backup dos volumes se necessário"
echo ""
echo "⚙️  Configuração Local:"
echo "   No arquivo config.py do projeto local, atualize:"
echo "   VPS_IP = \"$VPS_IP\""
echo ""

# Verificar firewall
echo "🔥 Verificando firewall..."
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        echo "   Firewall ativo. Verificando porta 8080..."
        if ufw status | grep -q "8080.*ALLOW"; then
            echo "   ✅ Porta 8080 já está liberada"
        else
            echo "   ⚠️  Porta 8080 não está liberada. Execute: sudo ufw allow 8080"
        fi
        
        echo "   Verificando porta 80 (phpMyAdmin)..."
        if ufw status | grep -q "80.*ALLOW"; then
            echo "   ✅ Porta 80 (phpMyAdmin) está liberada"
        else
            echo "   ⚠️  Porta 80 não está liberada. Execute: sudo ufw allow 80"
        fi
    else
        echo "   Firewall inativo"
    fi
else
    echo "   UFW não encontrado"
fi

echo ""
echo "✅ Deploy finalizado!"
echo "🎯 Stack ISOLADA funcionando na porta 8080!" 