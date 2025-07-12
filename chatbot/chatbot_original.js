// Importações necessárias
const qrcode = require('qrcode-terminal');
const { Client, MessageMedia } = require('whatsapp-web.js');
const { exec } = require('child_process'); // Para executar scripts Python

// Inicializa o cliente (sem LocalAuth)
const client = new Client();

// Exibe o QR Code no terminal
client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

// Confirma quando o WhatsApp está conectado
client.on('ready', () => {
    console.log('Tudo certo! WhatsApp conectado.');
});

// Inicializa o cliente (abre a sessão)
client.initialize();

// Listener principal de mensagens
client.on('message', async msg => {
    // Só responde se vier de um contato privado (não grupo)
    if (!msg.from.endsWith('@c.us')) return;

    // Tenta interpretar o texto como número
    const input = msg.body.trim();
    const number = parseInt(input, 10);

    // Verifica se é número
    if (!isNaN(number)) {
        // Verifica se está dentro do intervalo 5350–20000 (exemplo de regra)
        if (number >= 5350 && number <= 20000) {
            // Executa o script Python imediatamente
            await client.sendMessage(msg.from, `Processando a edição ${number}...`);

            // Chama o script relatorio_v1.py passando a edição como argumento
            exec(`python D:/Documentos/Workspace/relatorio_v1.py ${number}`, async (err, stdout, stderr) => {
                if (err) {
                    console.error(err);
                    await client.sendMessage(msg.from, 'Erro ao processar a edição. Verifique ou contate o suporte.');
                } else {
                    // Extrai a última linha do stdout para obter o caminho do PDF
                    const logs = stdout.trim().split('\n');
                    const pdfPath = logs[logs.length - 1].trim();

                    try {
                        // Envia o PDF para o WhatsApp
                        const media = MessageMedia.fromFilePath(pdfPath);
                        await client.sendMessage(msg.from, media);
                        await client.sendMessage(msg.from, 'Relatório gerado com sucesso!');
                    } catch (e) {
                        console.error(e);
                        await client.sendMessage(msg.from, 'Erro ao enviar o relatório. Verifique a edição ou contate o suporte.');
                    }
                }
            });
        }
        // Se o número não está no intervalo, ignore ou responda algo
    }
    // Se não for número, ignore ou responda algo
}); 