// Helpers para ler/gravar as pools de perguntas em data/exams/{certId}/{level}.json
const fs = require('fs');
const path = require('path');

const EXAMS_DIR = path.join(__dirname, '..', '..', '..', 'data', 'exams');

// Lista as pools (cert x nível) disponíveis em data/exams, com filtros opcionais
function listPools({ certsFilter, levelsFilter } = {}) {
    const pools = [];
    for (const certId of fs.readdirSync(EXAMS_DIR).sort()) {
        const certDir = path.join(EXAMS_DIR, certId);
        if (!fs.statSync(certDir).isDirectory()) continue;
        if (certsFilter && !certsFilter.includes(certId)) continue;

        for (const file of fs.readdirSync(certDir).sort()) {
            if (!file.endsWith('.json')) continue;
            const level = path.basename(file, '.json');
            if (levelsFilter && !levelsFilter.includes(level)) continue;
            pools.push({ certId, level, filePath: path.join(certDir, file) });
        }
    }
    return pools;
}

function loadPool(filePath) {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}

function savePool(filePath, pool) {
    fs.writeFileSync(filePath, JSON.stringify(pool, null, 2) + '\n', 'utf-8');
}

// Próximo número sequencial a usar nos IDs (ex: clf-ini-013), com base no maior já existente
function getNextSeqNumber(questions) {
    let max = 0;
    for (const q of questions) {
        const m = /(\d+)\s*$/.exec(q.id || '');
        if (m) max = Math.max(max, parseInt(m[1], 10));
    }
    return max + 1;
}

// Distribui `targetTotal` perguntas entre os domínios respeitando os pesos
// (método dos maiores restos) e calcula quantas faltam gerar em cada domínio,
// considerando as perguntas já existentes (`questions`).
function computePlan(domains, questions, targetTotal) {
    const allocations = domains.map(d => {
        const raw = d.weight * targetTotal;
        return { domainId: d.id, domainName: d.name, weight: d.weight, target: Math.floor(raw), remainder: raw - Math.floor(raw) };
    });

    const allocated = allocations.reduce((sum, a) => sum + a.target, 0);
    let remaining = targetTotal - allocated;

    const byRemainder = [...allocations].sort((a, b) => b.remainder - a.remainder);
    for (let i = 0; i < remaining; i++) {
        byRemainder[i % byRemainder.length].target++;
    }

    return allocations.map(a => {
        const existingCount = questions.filter(q => q.domain === a.domainId).length;
        return {
            domainId: a.domainId,
            domainName: a.domainName,
            weight: a.weight,
            target: a.target,
            existingCount,
            needed: Math.max(0, a.target - existingCount)
        };
    });
}

module.exports = { EXAMS_DIR, listPools, loadPool, savePool, getNextSeqNumber, computePlan };
