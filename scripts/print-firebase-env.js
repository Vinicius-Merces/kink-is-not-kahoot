// Imprime o conteudo de serviceAccountKey.json minificado em uma linha,
// pronto para colar no valor da variavel de ambiente FIREBASE_SERVICE_ACCOUNT
// no painel do SquareCloud (ou em um arquivo .env local).
const path = require('path');

const keyPath = path.join(__dirname, '..', 'serviceAccountKey.json');

try {
    const serviceAccount = require(keyPath);
    console.log(JSON.stringify(serviceAccount));
} catch (error) {
    console.error('Nao foi possivel ler serviceAccountKey.json em:', keyPath);
    console.error(error.message);
    process.exit(1);
}
