// Imprime o conteudo de serviceAccountKey.json codificado em Base64,
// pronto para colar no valor da variavel de ambiente FIREBASE_SERVICE_ACCOUNT_BASE64
// no painel do SquareCloud (ou em um arquivo .env local).
//
// Use Base64 porque alguns paineis (ex: SquareCloud) rejeitam valores de
// variavel de ambiente que contenham espacos, aspas ou quebras de linha,
// que sao inevitaveis no JSON da service account.
const path = require('path');

const keyPath = path.join(__dirname, '..', 'serviceAccountKey.json');

try {
    const serviceAccount = require(keyPath);
    const json = JSON.stringify(serviceAccount);
    console.log(Buffer.from(json, 'utf-8').toString('base64'));
} catch (error) {
    console.error('Nao foi possivel ler serviceAccountKey.json em:', keyPath);
    console.error(error.message);
    process.exit(1);
}
