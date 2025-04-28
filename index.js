const fs = require('fs');
const qrcode = require('qrcode-terminal');
const { Client, LocalAuth } = require('whatsapp-web.js');

// ID do grupo alvo
const grupoAlvoId = '120363419029968840@g.us';

// Mapeamento de números para nomes dos compradores
const compradores = {
    "554792469843": "Jorge",
    "554784549969": "Eliane",
    "554797424883": "Andreia",
    "554799043869": "Tere",
    "554796768889": "Wesley"
};

// Inicializa o cliente WhatsApp com autenticação local
const client = new Client({
    authStrategy: new LocalAuth()
});

// Exibe o QR Code no terminal
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
});

// Confirma quando está pronto
client.on('ready', () => {
    console.log('============================================');
    console.log('✅🤖 BOT WhatsApp Conectado e Funcionando!');
    console.log(`👁️  Monitorando Grupo: ${grupoAlvoId}`);
    console.log('============================================');
});

// Remove espaços invisíveis e normaliza texto
function limparTexto(texto) {
    return texto
        .replace(/\u00a0/g, ' ')
        .replace(/\u200b/g, '')
        .replace(/\r/g, '')
        .replace(/\t/g, '')
        .replace(/\s+/g, ' ')
        .trim();
}

// Extrai valor das linhas com chave especificada
function pegarValor(linhas, chave) {
    const linha = linhas.find(l => limparTexto(l).toLowerCase().startsWith(limparTexto(chave).toLowerCase()));
    return linha ? limparTexto(linha.replace(chave, '').trim()) : '';
}

// Salva mensagens no arquivo JSON com tratamento de erro
function salvarMensagem(tipo, dados) {
    const arquivo = 'mensagens.json';
    let mensagens = [];

    try {
        if (fs.existsSync(arquivo)) {
            mensagens = JSON.parse(fs.readFileSync(arquivo, 'utf8'));
        }

        mensagens.push({ tipo, dados });
        fs.writeFileSync(arquivo, JSON.stringify(mensagens, null, 2));
        console.log('📄 mensagens.json atualizado com sucesso.');
    } catch (erro) {
        console.error('❌ Erro ao atualizar mensagens.json:', erro);
    }
}

// Extrai dados da solicitação com validação básica
function extrairSolicitacao(texto) {
    const linhas = texto.split('\n').map(l => l.trim());
    let compradorRaw = pegarValor(linhas, 'Comprador:').replace('@', '').trim();
    let compradorNome = compradores[compradorRaw] || compradorRaw;

    return {
        fornecedor: pegarValor(linhas, 'Fornecedor:'),
        nota_fiscal: pegarValor(linhas, 'Nota Fiscal:'),
        loja: pegarValor(linhas, 'Loja:'),
        motivo: pegarValor(linhas, 'Motivo:'),
        comprador: compradorNome,
        fornecedor_na_loja: pegarValor(linhas, 'Fornecedor na loja:') || pegarValor(linhas, 'Fornecedor está na loja?')
    };
}

// Extrai dados da resposta com validação básica
function extrairResposta(texto, remetente) {
    const linhas = texto.split('\n').map(l => l.trim());
    return {
        nota_fiscal: pegarValor(linhas, 'Nota Fiscal:'),
        status: pegarValor(linhas, 'Status:'),
        respondido_por: remetente
    };
}

// Recebe mensagens e realiza ações apropriadas
client.on('message', async (msg) => {
    if (msg.from !== grupoAlvoId) return;

    const textoOriginal = msg.body.trim();
    const textoPadronizado = limparTexto(textoOriginal.toLowerCase());

    const contato = await msg.getContact();
    const remetente = contato.pushname || contato.number || 'Desconhecido';

    console.log(`📨 Mensagem recebida de ${remetente}:`, textoOriginal);

    if (textoPadronizado.startsWith('solicitação de pedido')) {
        const dados = extrairSolicitacao(textoOriginal);
        if (!dados.fornecedor || !dados.nota_fiscal) {
            console.warn('⚠️ Solicitação inválida:', textoOriginal);
            return;
        }
        salvarMensagem('solicitacao', dados);
        console.log('📥 Solicitação registrada:', dados);
    } else if (textoPadronizado.startsWith('resposta comercial')) {
        const dados = extrairResposta(textoOriginal, remetente);
        if (!dados.nota_fiscal || !dados.status) {
            console.warn('⚠️ Resposta inválida:', textoOriginal);
            return;
        }
        salvarMensagem('resposta', dados);
        console.log('📥 Resposta registrada:', dados);
    } else {
        console.log('ℹ️ Mensagem ignorada: Não corresponde ao formato esperado.');
    }
});

// Inicializa o bot
client.initialize();