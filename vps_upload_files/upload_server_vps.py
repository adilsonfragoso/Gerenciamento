#!/usr/bin/env python3
"""
Servidor de upload para VPS externa - Versão Docker
Execute este script na VPS para receber uploads de imagens
"""

from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
import shutil
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/upload_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuração via variáveis de ambiente
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/uploads')
ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'jpg,jpeg').split(','))
MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB

# Criar pasta se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('/app/logs', exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

logger.info(f"Upload Server iniciado - Pasta: {UPLOAD_FOLDER}, Extensões: {ALLOWED_EXTENSIONS}, Tamanho max: {MAX_FILE_SIZE} bytes")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        logger.info(f"Upload recebido - IP: {request.remote_addr}")
        
        # Verificar se o arquivo foi enviado
        if 'file' not in request.files:
            logger.warning("Nenhum arquivo enviado")
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        sigla = request.form.get('sigla', '')
        
        if file.filename == '':
            logger.warning("Nenhum arquivo selecionado")
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not sigla:
            logger.warning("Sigla não fornecida")
            return jsonify({'error': 'Sigla não fornecida'}), 400
        
        # Validar tipo de arquivo
        if not allowed_file(file.filename):
            logger.warning(f"Tipo de arquivo não permitido: {file.filename}")
            return jsonify({'error': 'Apenas arquivos JPG/JPEG são permitidos'}), 400
        
        # Validar tamanho
        file.seek(0, 2)  # Ir para o final do arquivo
        file_size = file.tell()
        file.seek(0)  # Voltar para o início
        
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"Arquivo muito grande: {file_size} bytes")
            return jsonify({'error': f'Arquivo muito grande. Máximo {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
        
        # Usar a sigla exatamente como está no campo input
        # Gerar nome do arquivo
        filename = f"{sigla}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Verificar se arquivo já existe
        if os.path.exists(filepath):
            logger.info(f"Arquivo já existe, sobrescrevendo: {filename}")
        
        # Salvar arquivo
        file.save(filepath)
        logger.info(f"Arquivo salvo: {filename} ({file_size} bytes)")
        
        # Validar se é uma imagem válida
        try:
            with Image.open(filepath) as img:
                img.verify()
                logger.info(f"Imagem válida: {filename} - {img.size}")
        except Exception as e:
            os.remove(filepath)
            logger.error(f"Imagem inválida: {filename} - {str(e)}")
            return jsonify({'error': 'Arquivo de imagem inválido'}), 400
        
        # Retornar sucesso
        relative_path = f"uploads/{filename}"
        
        response_data = {
            'success': True,
            'filename': filename,
            'path': relative_path,
            'message': 'Imagem enviada com sucesso',
            'size': file_size,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Upload concluído com sucesso: {filename}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Erro interno: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Verificar se a pasta de upload existe e tem permissões
        if not os.access(UPLOAD_FOLDER, os.W_OK):
            return jsonify({'status': 'error', 'message': 'Sem permissão de escrita'}), 500
        
        # Contar arquivos
        file_count = len([f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))])
        
        return jsonify({
            'status': 'ok',
            'upload_folder': UPLOAD_FOLDER,
            'file_count': file_count,
            'max_file_size': MAX_FILE_SIZE,
            'allowed_extensions': list(ALLOWED_EXTENSIONS),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/files', methods=['GET'])
def list_files():
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Ordenar por data de modificação (mais recente primeiro)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'files': files,
            'count': len(files),
            'total_size': sum(f['size'] for f in files),
            'upload_folder': UPLOAD_FOLDER
        })
    except Exception as e:
        logger.error(f"Erro ao listar arquivos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'Upload Server',
        'version': '1.0.0',
        'endpoints': {
            'upload': '/upload (POST)',
            'health': '/health (GET)',
            'files': '/files (GET)'
        },
        'config': {
            'upload_folder': UPLOAD_FOLDER,
            'max_file_size': MAX_FILE_SIZE,
            'allowed_extensions': list(ALLOWED_EXTENSIONS)
        }
    })

if __name__ == '__main__':
    logger.info("=== Servidor de Upload para VPS (Docker) ===")
    logger.info(f"Pasta de upload: {UPLOAD_FOLDER}")
    logger.info(f"Extensões permitidas: {ALLOWED_EXTENSIONS}")
    logger.info(f"Tamanho máximo: {MAX_FILE_SIZE // (1024*1024)}MB")
    logger.info("Iniciando servidor na porta 5000...")
    
    app.run(host='0.0.0.0', port=5000, debug=False) 