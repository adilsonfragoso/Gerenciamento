// Importações necessárias
const qrcode = require('qrcode-terminal');
const { Client, MessageMedia, LocalAuth } = require('whatsapp-web.js');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Iniciando cliente WhatsApp...');

// Inicializa o cliente com LocalAuth para sessão persistente
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu'
        ]
    }
});

// Exibe o QR Code no terminal
client.on('qr', qr => {
    console.log('QR Code gerado! Escaneie para conectar:');
    qrcode.generate(qr, { small: true });
});

// Confirma quando o WhatsApp está conectado
client.on('ready', () => {
    console.log('WhatsApp conectado e pronto!');
});

// Listener para erros de autenticação
client.on('auth_failure', msg => {
    console.error('Falha na autenticacao:', msg);
});

// Listener para desconexão
client.on('disconnected', (reason) => {
    console.log('Cliente desconectado:', reason);
});

// Função para enviar mensagem com retry
async function sendMessageWithRetry(chatId, message, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            await client.sendMessage(chatId, message);
            return true;
        } catch (error) {
            console.error(`Tentativa ${i + 1} de envio falhou:`, error.message);
            if (i === retries - 1) {
                console.error('Todas as tentativas de envio falharam');
                return false;
            }
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }
    return false;
}

// Função para encontrar PDF por padrão de nome
function findPDF(edicao) {
    const downloadsDir = 'D:\\Adilson\\Downloads';
    const files = fs.readdirSync(downloadsDir);
    
    // Procura por arquivo que contenha o padrão do relatório
    const pdfFile = files.find(file => 
        file.includes(`edicao-${edicao}.pdf`) && 
        file.startsWith('relatorio-vendas-')
    );
    
    return pdfFile ? path.join(downloadsDir, pdfFile) : null;
}

// Inicializa o cliente
client.initialize();

// Listener principal de mensagens - VERSÃO LIMPA SEM LOGS EXCESSIVOS
client.on('message', async msg => {
    try {
        // Só responde se vier de um contato privado (não grupo)
        if (!msg.from.endsWith('@c.us')) return;

        console.log(`Mensagem recebida: ${msg.body}`);

        // Tenta interpretar o texto como número
        const input = msg.body.trim();
        const number = parseInt(input, 10);

        // Verifica se é número válido no intervalo
        if (!isNaN(number) && number >= 5350 && number <= 20000) {
            console.log(`Processando edicao ${number}...`);
            
            // Envia mensagem de processamento
            const processMsg = await sendMessageWithRetry(msg.from, `Processando a edicao ${number}...`);
            if (!processMsg) {
                console.error('Falha ao enviar mensagem de processamento');
                return;
            }

            // Executa o script Python
            console.log(`Executando script Python para edicao ${number}`);
            
            const child = exec(`python D:/Documentos/Workspace/relatorio_v1.py ${number}`, { 
                env: { 
                    ...process.env, 
                    PYTHONUNBUFFERED: "1", 
                    PYTHONIOENCODING: "utf-8" 
                }
            });

            // Mostra saída Python em tempo real (com codificação corrigida)
            child.stdout.on('data', (data) => {
                const output = data.toString('utf-8').trim();
                if (output) {
                    console.log(output);
                }
            });

            child.stderr.on('data', (data) => {
                const error = data.toString('utf-8').trim();
                if (error) {
                    console.error(error);
                }
            });

            child.on('close', async (code) => {
                if (code !== 0) {
                    console.error(`Erro ao executar script Python. Codigo: ${code}`);
                    await sendMessageWithRetry(msg.from, 'Erro ao processar a edicao. Verifique ou contate o suporte.');
                } else {
                    console.log('Script Python executado com sucesso');
                    
                    try {
                        // Procura pelo PDF gerado (sem usar glob)
                        const pdfPath = findPDF(number);
                        
                        if (!pdfPath || !fs.existsSync(pdfPath)) {
                            console.error('PDF nao encontrado');
                            await sendMessageWithRetry(msg.from, 'Erro ao localizar o relatorio.');
                            return;
                        }

                        console.log(`Enviando PDF: ${pdfPath}`);

                        // Envia o PDF para o WhatsApp
                        const media = MessageMedia.fromFilePath(pdfPath);
                        const pdfSent = await sendMessageWithRetry(msg.from, media);
                        
                        if (pdfSent) {
                            await sendMessageWithRetry(msg.from, 'Relatorio gerado com sucesso!');
                            console.log('PDF enviado com sucesso!');
                        } else {
                            await sendMessageWithRetry(msg.from, 'Erro ao enviar o relatorio.');
                        }
                    } catch (e) {
                        console.error('Erro ao processar PDF:', e);
                        await sendMessageWithRetry(msg.from, 'Erro ao enviar o relatorio.');
                    }
                }
            });
        } else if (!isNaN(number)) {
            console.log(`Numero ${number} fora do intervalo permitido (5350-20000)`);
        } else {
            console.log(`Mensagem nao e um numero valido: ${input}`);
        }
    } catch (error) {
        console.error('Erro geral no processamento da mensagem:', error);
    }
});

console.log('Bot iniciado e aguardando eventos...'); 