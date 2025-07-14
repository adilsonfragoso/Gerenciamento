// Importações necessárias
const qrcode = require('qrcode-terminal');
const { Client, MessageMedia } = require('whatsapp-web.js');
const { exec } = require('child_process'); // Para executar scripts Python

console.log('🚀 Iniciando cliente WhatsApp...');

// Inicializa o cliente (sem LocalAuth)
const client = new Client();

// Variável para controlar se está pronto
let isReady = false;

// LOGS PARA TODOS OS EVENTOS POSSÍVEIS
client.on('qr', qr => {
    console.log('📱 QR Code gerado! Escaneie para conectar:');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ EVENTO READY! WhatsApp conectado e pronto!');
    isReady = true;
});

client.on('authenticated', () => {
    console.log('🔐 EVENTO AUTHENTICATED! Autenticado com sucesso!');
});

client.on('auth_failure', (msg) => {
    console.log('❌ EVENTO AUTH_FAILURE! Falha na autenticação:', msg);
});

client.on('disconnected', (reason) => {
    console.log('🔌 EVENTO DISCONNECTED! Desconectado:', reason);
    isReady = false;
});

client.on('loading_screen', (percent, message) => {
    console.log(`⏳ EVENTO LOADING_SCREEN! Carregando... ${percent}% - ${message}`);
});

client.on('change_state', (state) => {
    console.log(`🔄 EVENTO CHANGE_STATE! Estado mudou para: ${state}`);
    if (state === 'CONNECTED') {
        console.log('🎯 CONECTADO! Forçando ready...');
        isReady = true;
    }
});

// EVENTOS ADICIONAIS
client.on('contact_changed', (message, oldId, newId, isContact) => {
    console.log(`👤 EVENTO CONTACT_CHANGED! ${oldId} -> ${newId}`);
});

client.on('group_join', (notification) => {
    console.log(`👥 EVENTO GROUP_JOIN! ${notification.id.user} entrou no grupo`);
});

client.on('group_leave', (notification) => {
    console.log(`👥 EVENTO GROUP_LEAVE! ${notification.id.user} saiu do grupo`);
});

client.on('message_create', (message) => {
    console.log(`📨 EVENTO MESSAGE_CREATE! De: ${message.from}, Corpo: "${message.body}"`);
});

client.on('message_revoke_me', (message, revoked_msg) => {
    console.log(`🚫 EVENTO MESSAGE_REVOKE_ME! Mensagem revogada`);
});

client.on('message_revoke_everyone', (message, revoked_msg) => {
    console.log(`🚫 EVENTO MESSAGE_REVOKE_EVERYONE! Mensagem revogada para todos`);
});

client.on('message_ack', (message, ack) => {
    console.log(`✓ EVENTO MESSAGE_ACK! Confirmação: ${ack}`);
});

client.on('media_uploaded', (message) => {
    console.log(`📎 EVENTO MEDIA_UPLOADED! Mídia enviada`);
});

// Inicializa o cliente (abre a sessão)
console.log('🔌 Inicializando cliente...');
client.initialize();

// Timeout para forçar ready se não acontecer em 30 segundos
setTimeout(() => {
    if (!isReady) {
        console.log('⚡ Forçando estado ready após timeout...');
        isReady = true;
    }
}, 30000);

// LISTENER PRINCIPAL DE MENSAGENS
client.on('message', async msg => {
    console.log('🔔 EVENTO MESSAGE! ================================');
    console.log(`📞 De: ${msg.from}`);
    console.log(`💬 Corpo: "${msg.body}"`);
    console.log(`📝 Tipo: ${msg.type}`);
    console.log(`👤 isGroup: ${msg.from.includes('@g.us')}`);
    console.log(`✅ isPrivate: ${msg.from.endsWith('@c.us')}`);
    console.log(`🤖 isReady: ${isReady}`);
    console.log('================================================');
    
    if (!isReady) {
        console.log('⚠️ Bot ainda não está pronto! Ignorando mensagem...');
        return;
    }
    
    // Só responde se vier de um contato privado (não grupo)
    if (!msg.from.endsWith('@c.us')) {
        console.log(`❌ Ignorando mensagem de grupo: ${msg.from}`);
        return;
    }

    console.log(`✅ Processando mensagem de contato privado: ${msg.from}`);

    // Tenta interpretar o texto como número
    const input = msg.body.trim();
    console.log(`📝 Input recebido: "${input}"`);
    
    const number = parseInt(input, 10);
    console.log(`🔢 Número parseado: ${number}`);

    // Verifica se é número
    if (!isNaN(number)) {
        console.log(`✅ É um número válido: ${number}`);
        
        // Verifica se está dentro do intervalo 5350–20000 (exemplo de regra)
        if (number >= 5350 && number <= 20000) {
            console.log(`✅ Número está no intervalo válido: ${number}`);
            
            // Executa o script Python imediatamente
            console.log(`🚀 Enviando mensagem de processamento...`);
            await client.sendMessage(msg.from, `Processando a edição ${number}...`);

            // Chama o script Gerenciamento/scripts/relatorio_v2.py passando a edição como argumento
            console.log(`🐍 Executando: python D:/Documentos/Workspace/Gerenciamento/scripts/relatorio_v2.py ${number}`);
            exec(`python D:/Documentos/Workspace/Gerenciamento/scripts/relatorio_v2.py ${number}`, async (err, stdout, stderr) => {
                if (err) {
                    console.error('❌ Erro na execução do Python:', err);
                    await client.sendMessage(msg.from, 'Erro ao processar a edição. Verifique ou contate o suporte.');
                } else {
                    console.log('✅ Script Python executado com sucesso');
                    console.log('📄 stdout:', stdout);
                    
                    // Procura pela linha que contém "PDF gerado:" para obter o caminho correto
                    const logs = stdout.trim().split('\n');
                    const pdfLine = logs.find(line => line.includes('PDF gerado:'));
                    
                    if (!pdfLine) {
                        console.error('❌ Linha com "PDF gerado:" não encontrada no stdout');
                        await client.sendMessage(msg.from, 'Erro: PDF não foi gerado corretamente.');
                        return;
                    }
                    
                    const pdfPath = pdfLine.replace('PDF gerado:', '').trim();
                    console.log(`📁 Caminho do PDF: ${pdfPath}`);

                    try {
                        // Envia o PDF para o WhatsApp
                        console.log(`📤 Enviando PDF...`);
                        const media = MessageMedia.fromFilePath(pdfPath);
                        await client.sendMessage(msg.from, media);
                        await client.sendMessage(msg.from, 'Relatório gerado com sucesso!');
                        console.log(`✅ PDF enviado com sucesso!`);
                    } catch (e) {
                        console.error('❌ Erro ao enviar PDF:', e);
                        await client.sendMessage(msg.from, 'Erro ao enviar o relatório. Verifique a edição ou contate o suporte.');
                    }
                }
            });
        } else {
            console.log(`❌ Número fora do intervalo (5350-20000): ${number}`);
        }
    } else {
        console.log(`❌ Não é um número válido: "${input}"`);
    }
});

console.log('🤖 Bot iniciado e aguardando eventos...');
