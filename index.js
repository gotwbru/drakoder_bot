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

// Inicia o cliente com autenticação local
const client = new Client({
    authStrategy: new LocalAuth()
});

// Exibe o QR Code no terminal
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
});

// Confirma quando está pronto
client.on('ready', () => {
    console.log('✅ Bot conectado e rodando!');
    console.log(`🎯 Monitorando grupo: ${grupoAlvoId}`);
});

// Salva uma mensagem no arquivo JSON
function salvarMensagem(tipo, dados) {
    const arquivo = 'mensagens.json';
    let mensagens = [];

    if (fs.existsSync(arquivo)) {
        mensagens = JSON.parse(fs.readFileSync(arquivo));
    }

    mensagens.push({ tipo, dados });
    fs.writeFileSync(arquivo, JSON.stringify(mensagens, null, 2));
    console.log('📄 mensagens.json atualizado:', JSON.stringify(mensagens, null, 2));
}

// Função auxiliar para extrair valores com normalização
function pegarValor(linhas, chave) {
    const linha = linhas.find(l => removerEspacosInvisiveis(l).startsWith(removerEspacosInvisiveis(chave)));
    return linha ? removerEspacosInvisiveis(linha.replace(chave, '').trim()) : '';
}

// Remove espaços invisíveis como \xa0 ou similares
function removerEspacosInvisiveis(texto) {
    return texto.replace(/\s+/g, ' ').replace(/\u00a0/g, ' ').trim();
}

// Extrai dados da solicitação
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

// Extrai dados da resposta
function extrairResposta(texto, remetente) {
    const linhas = texto.split('\n').map(l => l.trim());
    return {
        nota_fiscal: pegarValor(linhas, 'Nota Fiscal:'),
        status: pegarValor(linhas, 'Status:'),
        respondido_por: remetente
    };
}

// Lê mensagens recebidas
client.on('message', async (msg) => {
    if (msg.from !== grupoAlvoId) return; // Ignora se não for do grupo alvo

    const textoOriginal = msg.body.trim();
    const textoPadronizado = textoOriginal.toLowerCase();
    const remetente = msg._data.notifyName || msg._data.pushName || 'Desconhecido';

    if (textoPadronizado.startsWith('solicitação de pedido')) {
        const dados = extrairSolicitacao(textoOriginal);
        salvarMensagem('solicitacao', dados);
        console.log('📥 Solicitação registrada:', dados);
    }
    else if (textoPadronizado.startsWith('resposta comercial')) {
        const dados = extrairResposta(textoOriginal, remetente);
        salvarMensagem('resposta', dados);
        console.log('📥 Resposta registrada:', dados);
    }    
});

// Inicializa o bot
client.initialize();
