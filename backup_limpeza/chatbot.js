// ----------------------------
//   chatbot.js  (versão 3)
// ----------------------------

const qrcode = require('qrcode-terminal');
const { Client, MessageMedia, LocalAuth } = require('whatsapp-web.js');
const { exec } = require('child_process');
const fs   = require('fs');
const path = require('path');

// Utilitário para pausar
const wait = ms => new Promise(r => setTimeout(r, ms));

// ───────────────────────────
//  Configuração do cliente
// ───────────────────────────
const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run', '--no-zygote', '--disable-gpu',
    ],
  },
  skipOldMessages: false,   // ainda queremos histórico completo
});

// QR-Code
client.on('qr', qr => {
  console.log('🔑 QR recebido – escaneie:');
  qrcode.generate(qr, { small: true });
});

// Estado geral
client.on('ready', () => console.log('✅ WhatsApp conectado.'));
client.on('auth_failure', m => console.error('❌ Falha de auth:', m));
client.on('disconnected', r => console.warn('🔌 Desconectado:', r));

// ───────────────────────────
//  Funções auxiliares
// ───────────────────────────
async function sendMessageWithRetry(to, msg, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      await client.sendMessage(to, msg);
      return true;
    } catch (err) {
      console.error(`Tentativa ${i + 1} falhou:`, err.message);
      if (i === retries - 1) return false;
      await wait(1500);
    }
  }
  return false;
}

// Pega texto de qualquer formato
function extractText(msg) {
  return (
    msg.body ||
    msg.caption ||
    msg?._data?.body ||
    msg?._data?.extendedTextMessage?.text ||
    ''
  ).trim();
}

// ───────────────────────────
//  Processamento principal
// ───────────────────────────
async function processEdition(msg) {
  if (msg.from?.includes('@g.us')) return;        // ignora grupos

  const raw = extractText(msg);
  const edition = parseInt(raw, 10);
  if (isNaN(edition) || edition < 5350 || edition > 20000) return;

  console.log(`👉 Edição solicitada: ${edition}`);

  if (!(await sendMessageWithRetry(msg.from, `Processando a edição ${edition}…`)))
    return console.error('Falha ao avisar usuário.');

  // Executa script Python
  const child = exec(`python D:/Documentos/Workspace/Gerenciamento/relatorio_v1.py ${edition}`, {
    env: { ...process.env, PYTHONUNBUFFERED: '1', PYTHONIOENCODING: 'utf-8' },
  });

  child.stdout.on('data', d => console.log(d.toString('utf-8').trim()));
  child.stderr.on('data', d => console.error(d.toString('utf-8').trim()));

  child.on('close', async code => {
    if (code !== 0) {
      await sendMessageWithRetry(msg.from, 'Erro ao processar a edição.');
      return;
    }

    // Localiza PDF
    const dir = 'D:\\Adilson\\Downloads';
    const pdf = fs.readdirSync(dir).find(f =>
      f.includes(`edicao-${edition}.pdf`) && f.includes('relatorio-vendas')
    );
    if (!pdf) {
      await sendMessageWithRetry(msg.from, 'Relatório não encontrado.');
      return;
    }

    const media = MessageMedia.fromFilePath(path.join(dir, pdf));
    if (await sendMessageWithRetry(msg.from, media))
      await sendMessageWithRetry(msg.from, 'Relatório gerado com sucesso!');
  });
}

// ───────────────────────────
//  Listeners
// ───────────────────────────

// 1) Mensagens normais (digitadas)
client.on('message', async msg => {
  await processEdition(msg);
});

// 2) ACK – cobre o caso “API Evolution”
client.on('message_ack', async (msg, ack) => {
  // ack 1=entregue, 2=lida, 3=visualizada áudio; ignorar se veio de você
  if (msg.fromMe) return;
  // Apenas primeira vez que o ack muda (evita rodar várias vezes)
  if (ack === 1) await processEdition(msg);
});

// 3) Reservado (pode comentar se quiser)
client.on('message_create', async msg => {
  if (!msg.fromMe) await processEdition(msg);
});

// ───────────────────────────
client.initialize();
