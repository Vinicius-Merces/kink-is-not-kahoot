// Incorpora as questões geradas (output/{certId}-{level}.generated.json) às
// pools oficiais em data/exams/{certId}/{level}.json.
//
// Faz dedup por `id`: se uma questão gerada já existe na pool (mesmo id),
// ela é ignorada. Após o merge bem-sucedido, o arquivo de staging é removido.
//
// Uso:
//   node merge.js                                 (mergeia tudo que houver em output/)
//   node merge.js --certs=clf-c02 --levels=iniciante
//   node merge.js --dry-run                       (mostra o que seria feito, sem alterar nada)
const fs = require('fs');
const path = require('path');

const { listPools, loadPool, savePool } = require('./lib/pools');

const OUTPUT_DIR = path.join(__dirname, 'output');

function parseArgs(argv) {
    const args = {};
    for (const arg of argv) {
        const m = /^--([^=]+)(?:=(.*))?$/.exec(arg);
        if (!m) continue;
        args[m[1]] = m[2] === undefined ? true : m[2];
    }
    return args;
}

const args = parseArgs(process.argv.slice(2));
const DRY_RUN = !!args['dry-run'];
const certsFilter = args.certs ? String(args.certs).split(',').map(s => s.trim()) : null;
const levelsFilter = args.levels ? String(args.levels).split(',').map(s => s.trim()) : null;

function mergePool(certId, level, filePath) {
    const stagedPath = path.join(OUTPUT_DIR, `${certId}-${level}.generated.json`);
    if (!fs.existsSync(stagedPath)) return;

    const staged = JSON.parse(fs.readFileSync(stagedPath, 'utf-8'));
    if (!Array.isArray(staged.questions) || staged.questions.length === 0) {
        console.log(`=== ${certId} - ${level} === nada para mergear (staging vazio).`);
        return;
    }

    const pool = loadPool(filePath);
    const existingIds = new Set(pool.questions.map(q => q.id));
    const toAdd = staged.questions.filter(q => !existingIds.has(q.id));
    const skipped = staged.questions.length - toAdd.length;

    console.log(`=== ${pool.certCode} (${certId}) - ${level} ===`);
    console.log(`  pool atual: ${pool.questions.length} questões`);
    console.log(`  staging: ${staged.questions.length} questões (${skipped} já existiam, ignoradas)`);
    console.log(`  a adicionar: ${toAdd.length}`);

    if (DRY_RUN) return;

    pool.questions.push(...toAdd);
    savePool(filePath, pool);
    fs.unlinkSync(stagedPath);

    console.log(`  ✅ pool atualizada: ${pool.questions.length} questões. Arquivo de staging removido.`);
}

function main() {
    const pools = listPools({ certsFilter, levelsFilter });
    if (pools.length === 0) {
        console.log('Nenhuma pool encontrada com os filtros informados.');
        return;
    }

    for (const { certId, level, filePath } of pools) {
        mergePool(certId, level, filePath);
    }

    console.log(DRY_RUN ? '\n✅ Simulação concluída (dry-run, nada foi alterado).' : '\n✅ Merge concluído.');
}

main();
