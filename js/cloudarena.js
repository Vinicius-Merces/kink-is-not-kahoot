/**
 * CloudArena — modo de estudo gamificado (RPG de batalha por turnos).
 *
 * 4 arenas independentes (CLF/SAA/DVA/DEA). Cada inimigo é uma questão do
 * banco existente + overlay do CloudArena (data/cloudarena/breakdowns/).
 * Batalha em 3 golpes: eliminação (2), escolha (entre correta e armadilha)
 * e golpe final (justificativa do porquê).
 *
 * Especificação completa: CLOUDARENA-SPEC.md. Zero chamadas de IA em runtime;
 * todo o conteúdo é estático.
 */
(function () {
    'use strict';

    // ════════════════════════════════════════════════════════════════════
    // Configuração das arenas
    // ════════════════════════════════════════════════════════════════════
    const ARENAS = {
        'clf-c02': {
            name: 'CLF-C02', title: 'Cloud Practitioner', maxLevel: 50, challenge: false,
            color: '#2dd4bf',
            // faixas de 10 níveis: [%iniciante, %medio, %avancado]
            curve: [[95, 5, 0], [72, 25, 2], [50, 38, 12], [32, 42, 26], [20, 38, 42]],
        },
        'saa-c03': {
            name: 'SAA-C03', title: 'Solutions Architect', maxLevel: 100, challenge: true,
            color: '#ff6b6b',
            curve: [[100, 0, 0], [90, 10, 0], [80, 20, 0], [65, 30, 5], [55, 35, 10],
                    [45, 40, 15], [35, 42, 23], [28, 42, 30], [22, 40, 38], [18, 37, 45]],
        },
        'dva-c02': {
            name: 'DVA-C02', title: 'Developer', maxLevel: 100, challenge: true,
            color: '#ffd166',
            curve: [[100, 0, 0], [90, 10, 0], [80, 20, 0], [65, 30, 5], [55, 35, 10],
                    [45, 40, 15], [35, 42, 23], [28, 42, 30], [22, 40, 38], [18, 37, 45]],
        },
        'dea-c01': {
            name: 'DEA-C01', title: 'Data Engineer', maxLevel: 100, challenge: true,
            color: '#a78bfa',
            curve: [[100, 0, 0], [90, 10, 0], [80, 20, 0], [65, 30, 5], [55, 35, 10],
                    [45, 40, 15], [35, 42, 23], [28, 42, 30], [22, 40, 38], [18, 37, 45]],
        },
    };
    const LEVELS = ['iniciante', 'medio', 'avancado'];
    const CHALLENGE_LENGTH = 20;

    // HP: regra geral — rounds = hp / 4
    const HP_NORMAL = 4;
    const HP_BOSS = 12;
    const HP_CHALLENGE_BOSS = 24;
    const HP_CHALLENGE_FINAL = 32;
    const HERO_BASE_HP = 10;
    const KILLS_PER_HERO_LEVEL = 5;

    // ════════════════════════════════════════════════════════════════════
    // Inimigos por tópico (SAA/DVA/DEA) e por domínio (CLF) — spec seção 13
    // ════════════════════════════════════════════════════════════════════
    const ENEMIES = {
        // Segurança/Identidade (roxo)
        'iam': { name: 'Guardião de Permissões', family: 'seguranca', emoji: '🛡️' },
        'security-services': { name: 'Sentinela GuardDuty', family: 'seguranca', emoji: '🛡️' },
        'governance': { name: 'Auditor Implacável', family: 'seguranca', emoji: '🛡️' },
        'security-dev': { name: 'Cifra Errante', family: 'seguranca', emoji: '🛡️' },
        'cognito': { name: 'Duplo Identidade', family: 'seguranca', emoji: '🛡️' },
        'data-security': { name: 'Vigia do Cofre', family: 'seguranca', emoji: '🛡️' },
        // Computação (laranja)
        'ec2-compute': { name: 'Instância Rebelde', family: 'computacao', emoji: '⚙️' },
        'serverless': { name: 'Fantasma sem Servidor', family: 'computacao', emoji: '⚙️' },
        'containers': { name: 'Enxame de Contêineres', family: 'computacao', emoji: '⚙️' },
        'lambda': { name: 'Gatilho Lambda', family: 'computacao', emoji: '⚙️' },
        'beanstalk': { name: 'Broto Beanstalk', family: 'computacao', emoji: '⚙️' },
        'emr': { name: 'Colmeia EMR', family: 'computacao', emoji: '⚙️' },
        // Armazenamento/Dados (azul)
        's3-storage': { name: 'Balde Sem Fundo', family: 'dados', emoji: '🗄️' },
        'databases': { name: 'Réplica Sombria', family: 'dados', emoji: '🗄️' },
        'analytics': { name: 'Oráculo de Dados', family: 'dados', emoji: '🗄️' },
        's3-dev': { name: 'Bucket Espectral', family: 'dados', emoji: '🗄️' },
        'dynamodb': { name: 'Tabela Voraz', family: 'dados', emoji: '🗄️' },
        'datalake-s3': { name: 'Lago Profundo', family: 'dados', emoji: '🗄️' },
        'redshift': { name: 'Colosso Redshift', family: 'dados', emoji: '🗄️' },
        'athena': { name: 'Esfinge Athena', family: 'dados', emoji: '🗄️' },
        'nosql-stores': { name: 'Chave-Valor Camaleão', family: 'dados', emoji: '🗄️' },
        // Rede (verde)
        'vpc': { name: 'Muralha VPC', family: 'rede', emoji: '🌐' },
        'edge-dns': { name: 'Eco de Borda', family: 'rede', emoji: '🌐' },
        'hybrid-networking': { name: 'Ponte Híbrida', family: 'rede', emoji: '🌐' },
        'api-gateway': { name: 'Portão de API', family: 'rede', emoji: '🌐' },
        // Resiliência (âmbar)
        'high-availability': { name: 'Sentinela Multi-AZ', family: 'resiliencia', emoji: '🔱' },
        'dr-backup': { name: 'Fênix de Backup', family: 'resiliencia', emoji: '🔱' },
        'troubleshooting': { name: 'Bug Persistente', family: 'resiliencia', emoji: '🔱' },
        // Operações/Monitoramento (cinza-azulado)
        'monitoring': { name: 'Olho do CloudWatch', family: 'operacoes', emoji: '👁️' },
        'cost': { name: 'Cobrador Implacável', family: 'operacoes', emoji: '👁️' },
        'migration': { name: 'Peregrino DMS', family: 'operacoes', emoji: '👁️' },
        'cicd': { name: 'Esteira Automática', family: 'operacoes', emoji: '👁️' },
        'cloudformation-sam': { name: 'Arquiteto de Templates', family: 'operacoes', emoji: '👁️' },
        'sdk-cli': { name: 'Terminal Sombrio', family: 'operacoes', emoji: '👁️' },
        // Integração/IA (magenta)
        'app-integration': { name: 'Mensageiro das Filas', family: 'integracao', emoji: '📮' },
        'ml-ai': { name: 'Oráculo Preditivo', family: 'integracao', emoji: '📮' },
        'messaging': { name: 'Eco da Fila', family: 'integracao', emoji: '📮' },
        // Pipeline de dados (teal)
        'de-fundamentals': { name: 'Fluxo Bruto', family: 'pipeline', emoji: '🌊' },
        'streaming': { name: 'Corrente Kinesis', family: 'pipeline', emoji: '🌊' },
        'batch-ingestion': { name: 'Caravana em Lote', family: 'pipeline', emoji: '🌊' },
        'glue-etl': { name: 'Cola ETL', family: 'pipeline', emoji: '🌊' },
        'orchestration': { name: 'Maestro de Pipelines', family: 'pipeline', emoji: '🌊' },
        'dataops': { name: 'Guardião da Qualidade', family: 'pipeline', emoji: '🌊' },
    };
    // CLF não tem topics — usa os 4 domínios oficiais da prova
    const CLF_ENEMIES = {
        'cloud-concepts': { name: 'Espírito da Nuvem', family: 'clf', emoji: '☁️' },
        'security-compliance': { name: 'Escudo de Conformidade', family: 'clf', emoji: '🛡️' },
        'technology-services': { name: 'Autômato de Serviços', family: 'clf', emoji: '🤖' },
        'billing-pricing-support': { name: 'Contador Implacável', family: 'clf', emoji: '💰' },
    };
    const FALLBACK_ENEMY = { name: 'Anomalia da Nuvem', family: 'clf', emoji: '⛈️' };

    // ════════════════════════════════════════════════════════════════════
    // Persistência (localStorage) — spec seção 12
    // ════════════════════════════════════════════════════════════════════
    const STATE_KEY = 'cloudpath_arena_state_v1';
    const ACH_KEY = 'cloudpath_arena_achievements_v1';

    function freshArenaState() {
        return {
            currentLevel: 1,
            enemiesDefeated: 0,
            heroCurrentHp: HERO_BASE_HP,
            bestLevelReached: 0,
            completed: false,
            challengeUnlocked: false,
            challengeBestLevel: 0,
            inChallenge: false,
            challengePosition: 0,
            bossesDefeated: [],       // níveis de chefe derrotados na história da arena
            recentQuestionIds: [],    // fila anti-repetição — SOBREVIVE à morte
            noDamageStreak: 0,
            lowestHpRatio: 1,
            heroLevelUpsThisRun: 0,
            hadGameOver: false,       // para a conquista Backup e Restore
            playDays: [],
        };
    }

    function loadState() {
        let raw = null;
        try { raw = JSON.parse(localStorage.getItem(STATE_KEY)); } catch (e) { /* corrompido */ }
        const state = raw && typeof raw === 'object' ? raw : {};
        state.heroChoice = state.heroChoice || null;
        state.arenas = state.arenas || {};
        for (const id of Object.keys(ARENAS)) {
            state.arenas[id] = Object.assign(freshArenaState(), state.arenas[id] || {});
        }
        return state;
    }

    function saveState() {
        try { localStorage.setItem(STATE_KEY, JSON.stringify(state)); } catch (e) { /* cheio/privado */ }
    }

    // heroLevel/heroMaxHp são SEMPRE derivados de enemiesDefeated (spec 12)
    function heroLevel(a) { return Math.floor(a.enemiesDefeated / KILLS_PER_HERO_LEVEL); }
    function heroMaxHp(a) { return HERO_BASE_HP + heroLevel(a); }

    function loadAchievements() {
        try { return JSON.parse(localStorage.getItem(ACH_KEY)) || { unlocked: {} }; }
        catch (e) { return { unlocked: {} }; }
    }
    function saveAchievements() {
        try { localStorage.setItem(ACH_KEY, JSON.stringify(achState)); } catch (e) { /* noop */ }
    }

    // ════════════════════════════════════════════════════════════════════
    // Estado global de execução
    // ════════════════════════════════════════════════════════════════════
    const state = loadState();
    const achState = loadAchievements();
    let achievementDefs = [];
    const arenaData = {};       // certId -> { pools: {nivel: [resolved...]}, total, coverage }
    let currentArena = null;    // certId da arena ativa
    let battle = null;          // estado da batalha em andamento

    const $ = (sel) => document.querySelector(sel);
    const app = () => $('#arenaApp');

    // ════════════════════════════════════════════════════════════════════
    // Carga de dados: banco + overlay, vínculo por TEXTO (spec seção 3)
    // ════════════════════════════════════════════════════════════════════
    async function fetchJson(url) {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status} em ${url}`);
        return res.json();
    }

    // O /data é bloqueado no static do servidor (protege gabaritos) — o jogo
    // recebe do endpoint /api/arena/<certId> apenas as questões COM overlay,
    // já resolvidas por texto e com o gabarito cruzado no servidor.
    // Uma chamada por arena; zero chamadas por batalha.
    async function loadArenaData(certId) {
        if (arenaData[certId]) return arenaData[certId];
        const payload = await fetchJson(`/api/arena/${certId}`);
        if (!payload.success) throw new Error(payload.error || 'Falha ao carregar a arena');
        const pools = payload.pools || { iniciante: [], medio: [], avancado: [] };
        const covered = LEVELS.reduce((s, l) => s + (pools[l] ? pools[l].length : 0), 0);
        arenaData[certId] = { pools, totalBank: payload.totalBank || 0, covered };
        return arenaData[certId];
    }

    // ════════════════════════════════════════════════════════════════════
    // Curva de dificuldade e sorteio (spec seções 4, 5, 8)
    // ════════════════════════════════════════════════════════════════════
    function bandFor(certId, level) {
        const arena = ARENAS[certId];
        const bandSize = 10;
        const idx = Math.min(Math.floor((level - 1) / bandSize), arena.curve.length - 1);
        return arena.curve[idx];
    }

    function pickDifficulty(certId, level, isBoss) {
        const arena = ARENAS[certId];
        let band;
        if (state.arenas[certId].inChallenge) {
            return 'avancado'; // Desafio: 100% avançado
        }
        if (isBoss) {
            // chefe antecipa a PRÓXIMA faixa
            const nextLevel = Math.min(level + 1, arena.maxLevel);
            band = bandFor(certId, Math.min(nextLevel + 9, arena.maxLevel));
        } else {
            band = bandFor(certId, level);
        }
        const roll = Math.random() * 100;
        if (roll < band[0]) return 'iniciante';
        if (roll < band[0] + band[1]) return 'medio';
        return 'avancado';
    }

    // Sorteia questão com anti-repetição; degrada para dificuldade adjacente
    function drawQuestion(certId, targetLevel) {
        const data = arenaData[certId];
        const a = state.arenas[certId];
        const order = {
            iniciante: ['iniciante', 'medio', 'avancado'],
            medio: ['medio', 'iniciante', 'avancado'],
            avancado: ['avancado', 'medio', 'iniciante'],
        }[targetLevel];

        for (const lvl of order) {
            const pool = data.pools[lvl];
            if (!pool.length) continue;
            if (lvl !== targetLevel) {
                console.warn(`[CloudArena] degradação: sem pool em "${targetLevel}", usando "${lvl}" (${certId})`);
            }
            const recent = new Set(a.recentQuestionIds);
            let eligible = pool.filter(q => !recent.has(q.id));
            if (!eligible.length) {
                // pool esgotado pela fila: limpa a fila desta arena e sorteia livre
                a.recentQuestionIds = [];
                eligible = pool.slice();
            }
            const q = eligible[Math.floor(Math.random() * eligible.length)];
            // fila ~40% do pool elegível da arena
            const maxQueue = Math.max(1, Math.floor(data.covered * 0.4));
            a.recentQuestionIds.push(q.id);
            while (a.recentQuestionIds.length > maxQueue) a.recentQuestionIds.shift();
            return q;
        }
        return null; // nenhum overlay disponível na arena
    }

    // Dano do inimigo (spec 7.3): 1.0→5.0 linear; Desafio = fixo 5.0
    function enemyDamage(certId) {
        const a = state.arenas[certId];
        if (a.inChallenge) return 5.0;
        const max = ARENAS[certId].maxLevel;
        const dmg = 1 + (a.currentLevel - 1) / (max - 1) * 4;
        return Math.round(dmg * 10) / 10;
    }

    function isBossLevel(certId, level) {
        const a = state.arenas[certId];
        if (a.inChallenge) return a.challengePosition % 5 === 0;
        return level % 10 === 0;
    }

    function bossHp(certId) {
        const a = state.arenas[certId];
        if (a.inChallenge) {
            return a.challengePosition === CHALLENGE_LENGTH ? HP_CHALLENGE_FINAL : HP_CHALLENGE_BOSS;
        }
        return HP_BOSS;
    }

    // ════════════════════════════════════════════════════════════════════
    // Sprites — herói animado, inimigos estáticos (spec seções 6 e 13)
    // ════════════════════════════════════════════════════════════════════
    // Herói: images/arena/hero/<masculino|feminino>/<idle|attack|hurt|victory|defeat>.png
    // Inimigo: images/arena/enemies/<topic>-idle.png / -attack.png
    //          CLF: images/arena/enemies/clf/<domain>-idle.png / -attack.png
    // Enquanto os PNGs não existem, o loader cai num placeholder (emoji).
    function heroSpriteUrl(stateName) {
        const choice = state.heroChoice || 'masculino';
        return `images/arena/hero/${choice}/${stateName}.png`;
    }

    function enemySpriteUrl(certId, topic, pose) {
        if (certId === 'clf-c02') return `images/arena/enemies/clf/${topic}-${pose}.png`;
        return `images/arena/enemies/${topic}-${pose}.png`;
    }

    function setSprite(imgEl, url, fallbackEmoji) {
        imgEl.onerror = () => {
            imgEl.style.display = 'none';
            const fb = imgEl.nextElementSibling;
            if (fb && fb.classList.contains('sprite-fallback')) fb.style.display = 'flex';
        };
        imgEl.onload = () => {
            imgEl.style.display = '';
            const fb = imgEl.nextElementSibling;
            if (fb && fb.classList.contains('sprite-fallback')) fb.style.display = 'none';
        };
        imgEl.src = url;
    }

    function enemyInfo(certId, topic) {
        if (certId === 'clf-c02') return CLF_ENEMIES[topic] || FALLBACK_ENEMY;
        return ENEMIES[topic] || FALLBACK_ENEMY;
    }

    // ════════════════════════════════════════════════════════════════════
    // Conquistas (spec seção 14)
    // ════════════════════════════════════════════════════════════════════
    function unlock(id, label) {
        if (achState.unlocked[id]) return;
        achState.unlocked[id] = new Date().toISOString();
        saveAchievements();
        showToast(`🏆 Conquista: ${label}`);
    }

    function checkThematicAchievements(certId, a) {
        // Multi-AZ: pelo menos 1 vitória nas 4 arenas
        const wonAll = Object.keys(ARENAS).every(id =>
            (state.arenas[id].enemiesDefeated > 0) || (state.arenas[id].bestLevelReached > 0));
        if (wonAll) unlock('multi-az', 'Multi-AZ');
        // Auto Scaling: 10 level-ups na mesma run
        if (a.heroLevelUpsThisRun >= 10) unlock('auto-scaling', 'Auto Scaling');
        // Reservado: 7 dias diferentes
        const today = new Date().toISOString().slice(0, 10);
        state.playDays = state.playDays || [];
        if (!state.playDays.includes(today)) state.playDays.push(today);
        if (state.playDays.length >= 7) unlock('reserved', 'Reservado');
    }

    function showToast(msg) {
        const t = document.createElement('div');
        t.className = 'arena-toast';
        t.textContent = msg;
        document.body.appendChild(t);
        requestAnimationFrame(() => t.classList.add('show'));
        setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 400); }, 3200);
    }

    // ════════════════════════════════════════════════════════════════════
    // Batalha — máquina de estados dos 3 golpes (spec seção 2)
    // ════════════════════════════════════════════════════════════════════
    function startEncounter(certId) {
        const a = state.arenas[certId];
        const boss = isBossLevel(certId, a.currentLevel);
        const hp = boss ? bossHp(certId) : HP_NORMAL;
        const totalRounds = hp / 4; // spec: rounds = HP ÷ 4

        // Retomada de sessão (spec 7.1): se fechou o navegador no meio de uma
        // batalha, reabre a MESMA pergunta do início (round/HP do chefe também).
        const pending = a.pendingEncounter;
        if (pending && findQuestionById(certId, pending.questionId)) {
            battle = {
                certId, boss: pending.boss,
                enemyMaxHp: pending.enemyMaxHp, enemyHp: pending.enemyHp,
                totalRounds: pending.totalRounds, round: pending.round,
                tookDamage: false, golpe1Mistake: false,
                enteredWithHp: a.heroCurrentHp,
                question: null, topic: null,
            };
            openQuestion(findQuestionById(certId, pending.questionId));
            return;
        }

        battle = {
            certId, boss,
            enemyMaxHp: hp, enemyHp: hp,
            totalRounds, round: 1,
            tookDamage: false,          // dano tomado no encontro inteiro
            golpe1Mistake: false,       // para Well-Architected
            enteredWithHp: a.heroCurrentHp,
            question: null,
            topic: null,
        };
        nextRound();
    }

    function findQuestionById(certId, qid) {
        const data = arenaData[certId];
        if (!data) return null;
        for (const lvl of LEVELS) {
            const q = data.pools[lvl].find(x => x.id === qid);
            if (q) return q;
        }
        return null;
    }

    function nextRound() {
        const a = state.arenas[battle.certId];
        const difficulty = pickDifficulty(battle.certId, a.currentLevel, battle.boss);
        const q = drawQuestion(battle.certId, difficulty);
        if (!q) {
            renderNoContent(battle.certId);
            return;
        }
        openQuestion(q);
    }

    function openQuestion(q) {
        const a = state.arenas[battle.certId];
        battle.question = q;
        battle.topic = q.topic;
        battle.phase = 'eliminate';
        battle.selected = new Set();
        battle.eliminatedTexts = [];
        battle.disabledJusts = new Set();
        // persiste o encontro em andamento para retomada exata
        a.pendingEncounter = {
            questionId: q.id, boss: battle.boss, round: battle.round,
            totalRounds: battle.totalRounds,
            enemyHp: battle.enemyHp, enemyMaxHp: battle.enemyMaxHp,
        };
        saveState();
        renderBattle();
    }

    function heroHit() { // herói causa 1 de dano fixo (spec 7.2)
        battle.enemyHp = Math.max(0, battle.enemyHp - 1);
        animateHero('attack');
        animateEnemyHurt();
    }

    function heroHurt(certId) {
        const dmg = enemyDamage(certId);
        const a = state.arenas[certId];
        a.heroCurrentHp = Math.round(Math.max(0, a.heroCurrentHp - dmg) * 10) / 10;
        a.lowestHpRatio = Math.min(a.lowestHpRatio, a.heroCurrentHp / heroMaxHp(a));
        battle.tookDamage = true;
        a.noDamageStreak = 0;
        animateEnemyAttack();
        saveState();
        if (a.heroCurrentHp <= 0) {
            setTimeout(() => gameOver(certId), 650);
            return true;
        }
        return false;
    }

    // Golpe 1 — eliminação de exatamente 2
    function confirmElimination() {
        if (battle.selected.size !== 2) return;
        const a = state.arenas[battle.certId];
        let died = false;
        for (const text of battle.selected) {
            const opt = battle.question.options.find(o => o.text === text);
            if (opt.stage === 'eliminate') {
                heroHit();
            } else {
                // eliminou a correta ou a armadilha — dano no jogador
                battle.golpe1Mistake = true;
                died = heroHurt(battle.certId);
                if (died) return;
            }
        }
        battle.eliminatedTexts = [...battle.selected];
        battle.phase = 'choose';
        saveState();
        renderBattle();
    }

    // Golpe 2 — escolha entre correta e armadilha
    function chooseOption(text) {
        const opt = battle.question.options.find(o => o.text === text);
        battle.chosenText = text;
        if (opt.stage === 'correct') {
            heroHit();
            battle.choseCorrect = true;
        } else {
            battle.choseCorrect = false;
            if (heroHurt(battle.certId)) return;
        }
        battle.phase = 'finalblow';
        saveState();
        renderBattle();
    }

    // Golpe 3 — justificativa; abate instantâneo só em inimigo normal ou
    // última round do chefe (spec 7.4)
    function chooseJustification(idx) {
        const just = battle.question.justifications[idx];
        const isLastRound = battle.round === battle.totalRounds;
        if (just.correct) {
            if (!battle.boss || isLastRound) {
                battle.enemyHp = 0; // abate garantido
                animateHero('attack');
                enemyDefeated();
            } else {
                heroHit();
                battle.round++;
                showToast(`Round ${battle.round} de ${battle.totalRounds} — o chefe resiste!`);
                setTimeout(nextRound, 900);
            }
        } else {
            battle.disabledJusts.add(idx);
            if (heroHurt(battle.certId)) return;
            renderBattle();
        }
    }

    function enemyDefeated() {
        const certId = battle.certId;
        const a = state.arenas[certId];
        a.pendingEncounter = null; // encontro resolvido — nada a retomar
        a.enemiesDefeated++;
        animateHero('victory');

        // level-up do herói a cada 5 derrotas: +1 HP máx e cura completa
        if (a.enemiesDefeated % KILLS_PER_HERO_LEVEL === 0) {
            a.heroLevelUpsThisRun = (a.heroLevelUpsThisRun || 0) + 1;
            a.heroCurrentHp = heroMaxHp(a);
            showToast(`⬆️ Nível de herói ${heroLevel(a)} — HP máximo ${heroMaxHp(a)}, vida restaurada!`);
        }

        // conquistas de perfeição
        if (!battle.tookDamage) {
            a.noDamageStreak = (a.noDamageStreak || 0) + 1;
            if (battle.boss) unlock('flawless-boss', 'Perícia Impecável');
            else unlock('no-scratch', 'Sem Arranhões');
            if (a.noDamageStreak >= 5) unlock('unbeaten-5', 'Invicto');
            if (a.noDamageStreak >= 10) unlock('unbeaten-10', 'Lenda Viva');
        }
        if (battle.enteredWithHp === 1) unlock('cold-start', 'Cold Start');
        if (battle.boss && !battle.golpe1Mistake) unlock('well-architected', 'Well-Architected');

        if (battle.boss) {
            const info = enemyInfo(certId, battle.topic);
            const levelLabel = a.inChallenge ? `desafio-${a.challengePosition}` : a.currentLevel;
            if (!a.bossesDefeated.includes(levelLabel)) a.bossesDefeated.push(levelLabel);
            unlock(`boss:${certId}:${levelLabel}`,
                `Derrotou ${info.name} (chefe ${a.inChallenge ? 'do Desafio pos. ' + a.challengePosition : 'nível ' + a.currentLevel}, arena ${ARENAS[certId].name})`);
            // caçador de chefes da arena
            const expected = a.inChallenge ? null : expectedBossLevels(certId);
            if (expected && expected.every(lv => a.bossesDefeated.includes(lv))) {
                unlock(`boss-hunter:${certId}`, `Caçador de Chefes ${ARENAS[certId].name}`);
            }
            if (a.inChallenge) {
                const pos = a.challengePosition;
                if (pos === 5) unlock(`challenge-floor-1:${certId}`, `1º Andar do Desafio ${ARENAS[certId].name}`);
                if (pos === 10) unlock(`challenge-floor-2:${certId}`, `2º Andar do Desafio ${ARENAS[certId].name}`);
                if (pos === 15) unlock(`challenge-floor-3:${certId}`, `3º Andar do Desafio ${ARENAS[certId].name}`);
                if (pos === CHALLENGE_LENGTH) unlock(`challenge-top:${certId}`, `Topo da Arena ${ARENAS[certId].name}`);
            }
        }

        checkThematicAchievements(certId, a);
        advanceProgress(certId);
    }

    function expectedBossLevels(certId) {
        const max = ARENAS[certId].maxLevel;
        const levels = [];
        for (let l = 10; l <= max; l += 10) levels.push(l);
        return levels;
    }

    function advanceProgress(certId) {
        const a = state.arenas[certId];
        const arena = ARENAS[certId];

        if (a.inChallenge) {
            if (a.challengePosition >= CHALLENGE_LENGTH) {
                a.challengeBestLevel = Math.max(a.challengeBestLevel, CHALLENGE_LENGTH);
                saveState();
                renderChallengeVictory(certId);
                return;
            }
            a.challengePosition++;
            a.challengeBestLevel = Math.max(a.challengeBestLevel, a.challengePosition - 1);
            saveState();
            setTimeout(() => startEncounter(certId), 900);
            return;
        }

        a.bestLevelReached = Math.max(a.bestLevelReached, a.currentLevel);

        if (a.currentLevel >= arena.maxLevel) {
            // fim da arena principal
            unlock(`cleared:${certId}`, `Certificado ${arena.name}`);
            const allCleared = Object.keys(ARENAS).every(id =>
                achState.unlocked[`cleared:${id}`]);
            if (allCleared) unlock('all-cleared', 'Arquiteto Completo');
            if (a.lowestHpRatio >= 0.2) unlock('high-availability', 'Alta Disponibilidade');

            if (arena.challenge) {
                a.challengeUnlocked = true;
                a.inChallenge = true;
                a.challengePosition = 1;
                a.heroCurrentHp = heroMaxHp(a); // recompensa: entra com HP cheio
                a.completed = true;
                saveState();
                renderChallengeIntro(certId);
            } else {
                // CLF: vitória de arena (distinta de game over)
                unlock('free-tier-graduate', 'Free Tier Graduate');
                a.completed = true;
                saveState();
                renderArenaVictory(certId);
            }
            return;
        }

        a.currentLevel++;
        saveState();
        setTimeout(() => startEncounter(certId), 900);
    }

    function gameOver(certId) {
        const a = state.arenas[certId];
        const levelReached = a.inChallenge
            ? `${ARENAS[certId].maxLevel} + desafio ${a.challengePosition}`
            : a.currentLevel;
        const prevBest = a.bestLevelReached;
        a.bestLevelReached = Math.max(a.bestLevelReached, a.inChallenge ? ARENAS[certId].maxLevel : a.currentLevel);

        state.lastResult = {
            examId: certId, type: 'gameover',
            levelReached: a.inChallenge ? ARENAS[certId].maxLevel : a.currentLevel,
            heroLevel: heroLevel(a),
            date: new Date().toISOString(),
        };

        // Reset da run — recentQuestionIds e recordes SOBREVIVEM (spec 7.1)
        const preserved = {
            recentQuestionIds: a.recentQuestionIds,
            bestLevelReached: a.bestLevelReached,
            challengeBestLevel: a.challengeBestLevel,
            bossesDefeated: a.bossesDefeated,
            playDays: a.playDays,
        };
        Object.assign(a, freshArenaState(), preserved);
        a.pendingEncounter = null;
        a.hadGameOver = true;
        a.prevBestBeforeDeath = prevBest;
        saveState();
        renderGameOver(certId, levelReached);
    }

    // ════════════════════════════════════════════════════════════════════
    // Animações — herói tem poses desenhadas; inimigo é overlay/deslocamento
    // em código sobre sprite estático (spec seção 13)
    // ════════════════════════════════════════════════════════════════════
    function animateHero(pose) {
        const img = $('#heroSprite');
        if (!img) return;
        setSprite(img, heroSpriteUrl(pose), '🧑‍🚀');
        const wrap = $('#heroWrap');
        wrap.classList.remove('hero-attack', 'hero-hurt');
        void wrap.offsetWidth;
        if (pose === 'attack') wrap.classList.add('hero-attack');
        if (pose === 'hurt') wrap.classList.add('hero-hurt');
        setTimeout(() => setSprite(img, heroSpriteUrl('idle'), '🧑‍🚀'), 700);
    }

    function animateEnemyHurt() {
        const wrap = $('#enemyWrap');
        if (!wrap) return;
        wrap.classList.remove('enemy-hurt');
        void wrap.offsetWidth;
        wrap.classList.add('enemy-hurt'); // sobreposição vermelha 0,5s via CSS
        setTimeout(() => wrap.classList.remove('enemy-hurt'), 550);
        updateHpBars();
    }

    function animateEnemyAttack() {
        const wrap = $('#enemyWrap');
        const img = $('#enemySprite');
        if (!wrap || !img) return;
        setSprite(img, enemySpriteUrl(battle.certId, battle.topic, 'attack'), null);
        wrap.classList.add('enemy-attacking'); // desloca em direção ao herói via CSS
        setTimeout(() => {
            animateHero('hurt');
            updateHpBars();
        }, 320);
        setTimeout(() => {
            wrap.classList.remove('enemy-attacking');
            setSprite(img, enemySpriteUrl(battle.certId, battle.topic, 'idle'), null);
        }, 700);
    }

    // ════════════════════════════════════════════════════════════════════
    // Render — telas
    // ════════════════════════════════════════════════════════════════════
    function esc(s) {
        const d = document.createElement('div');
        d.textContent = String(s);
        return d.innerHTML;
    }

    function renderHome() {
        currentArena = null;
        battle = null;
        const cards = Object.entries(ARENAS).map(([id, arena]) => {
            const a = state.arenas[id];
            const inRun = a.enemiesDefeated > 0 || a.currentLevel > 1 || a.inChallenge;
            const status = a.inChallenge
                ? `Modo Desafio — posição ${a.challengePosition}/20`
                : `Nível ${a.currentLevel}/${arena.maxLevel}`;
            return `
            <div class="arena-card" style="--arena-color:${arena.color}">
                <div class="arena-card-head">
                    <h3>${arena.name}</h3><span>${esc(arena.title)}</span>
                </div>
                <div class="arena-card-stats">
                    <div>${status}</div>
                    <div>❤️ ${a.heroCurrentHp}/${heroMaxHp(a)} HP · herói nv. ${heroLevel(a)}</div>
                    <div>🏆 Recorde: nível ${a.bestLevelReached}${a.challengeBestLevel ? ` · Desafio ${a.challengeBestLevel}` : ''}</div>
                </div>
                <button class="arena-btn" data-arena="${id}">${inRun ? '▶ Continuar' : '⚔️ Começar'}</button>
            </div>`;
        }).join('');

        app().innerHTML = `
            <div class="arena-home">
                <div class="arena-hero-select">
                    <span>Seu herói:</span>
                    <button class="hero-choice ${state.heroChoice === 'masculino' ? 'active' : ''}" data-hero="masculino">🧑‍🚀 Herói</button>
                    <button class="hero-choice ${state.heroChoice === 'feminino' ? 'active' : ''}" data-hero="feminino">👩‍🚀 Heroína</button>
                    <button class="arena-link" id="achievementsBtn">🏆 Conquistas</button>
                </div>
                <div class="arena-cards">${cards}</div>
            </div>`;

        app().querySelectorAll('.hero-choice').forEach(b =>
            b.addEventListener('click', () => { state.heroChoice = b.dataset.hero; saveState(); renderHome(); }));
        $('#achievementsBtn').addEventListener('click', renderAchievements);
        app().querySelectorAll('.arena-btn').forEach(b =>
            b.addEventListener('click', () => enterArena(b.dataset.arena)));
    }

    async function enterArena(certId) {
        if (!state.heroChoice) {
            showToast('Escolha seu herói primeiro!');
            return;
        }
        app().innerHTML = '<div class="arena-loading">Carregando a arena…</div>';
        try {
            await loadArenaData(certId);
        } catch (err) {
            app().innerHTML = `<div class="arena-loading">Erro ao carregar: ${esc(err.message)}</div>`;
            return;
        }
        currentArena = certId;
        startEncounter(certId);
    }

    function hpBarHtml(id, current, max, color) {
        const pct = Math.max(0, Math.min(100, (current / max) * 100));
        return `
            <div class="hp-bar" id="${id}">
                <div class="hp-label">${current} / ${max}</div>
                <div class="hp-track"><div class="hp-fill" style="width:${pct}%;background:${color}"></div></div>
            </div>`;
    }

    function updateHpBars() {
        if (!battle) return;
        const a = state.arenas[battle.certId];
        const eb = $('#enemyHp'); const hb = $('#heroHp');
        if (eb) {
            eb.querySelector('.hp-label').textContent = `${battle.enemyHp} / ${battle.enemyMaxHp}`;
            eb.querySelector('.hp-fill').style.width = `${(battle.enemyHp / battle.enemyMaxHp) * 100}%`;
        }
        if (hb) {
            hb.querySelector('.hp-label').textContent = `${a.heroCurrentHp} / ${heroMaxHp(a)}`;
            hb.querySelector('.hp-fill').style.width = `${(a.heroCurrentHp / heroMaxHp(a)) * 100}%`;
        }
    }

    function renderBattle() {
        const certId = battle.certId;
        const arena = ARENAS[certId];
        const a = state.arenas[certId];
        const q = battle.question;
        const info = enemyInfo(certId, battle.topic);
        const levelLabel = a.inChallenge
            ? `Desafio ${a.challengePosition}/20`
            : `Nível ${a.currentLevel}/${arena.maxLevel}`;
        const bossTag = battle.boss
            ? `<span class="boss-tag">CHEFE — round ${battle.round}/${battle.totalRounds}</span>` : '';

        let phaseHtml = '';
        if (battle.phase === 'eliminate') {
            phaseHtml = `
                <p class="phase-title">⚡ Golpe 1 — Elimine exatamente 2 alternativas ERRADAS</p>
                <div class="option-list">
                    ${q.options.map(o => `
                        <label class="option-check ${battle.selected.has(o.text) ? 'selected' : ''}">
                            <input type="checkbox" data-text="${esc(o.text)}" ${battle.selected.has(o.text) ? 'checked' : ''}>
                            <span>${esc(o.text)}</span>
                        </label>`).join('')}
                </div>
                <button class="arena-action" id="confirmElim" ${battle.selected.size === 2 ? '' : 'disabled'}>Confirmar eliminação</button>`;
        } else if (battle.phase === 'choose') {
            // sobram sempre a correta e a armadilha (spec seção 2)
            const remaining = q.options.filter(o => o.stage === 'correct' || o.stage === 'trap');
            const feedback = battle.eliminatedTexts.map(t => {
                const o = q.options.find(x => x.text === t);
                const ok = o.stage === 'eliminate';
                return `<div class="elim-feedback ${ok ? 'good' : 'bad'}">${ok ? '✅' : '💥'} ${esc(t)}${!ok && o.reasonWrong ? ` — ${esc(o.reasonWrong)}` : ''}${!ok && o.stage === 'correct' ? ' — essa era a CORRETA!' : ''}</div>`;
            }).join('');
            phaseHtml = `
                ${feedback}
                <p class="phase-title">🎯 Golpe 2 — Qual das duas é a resposta certa?</p>
                <div class="option-list">
                    ${remaining.map(o => `<button class="option-btn" data-text="${esc(o.text)}">${esc(o.text)}</button>`).join('')}
                </div>`;
        } else if (battle.phase === 'finalblow') {
            const correctOpt = q.options.find(o => o.stage === 'correct');
            const chosenNote = battle.choseCorrect
                ? `<div class="elim-feedback good">✅ Você escolheu certo: ${esc(battle.chosenText)}</div>`
                : `<div class="elim-feedback bad">💥 A correta era: <strong>${esc(correctOpt.text)}</strong> — agora acerte o PORQUÊ.</div>`;
            phaseHtml = `
                ${chosenNote}
                <p class="phase-title">💥 Golpe final — POR QUE essa é a resposta certa?</p>
                <div class="option-list">
                    ${q.justifications.map((j, i) => `
                        <button class="option-btn just ${battle.disabledJusts.has(i) ? 'disabled' : ''}"
                                data-just="${i}" ${battle.disabledJusts.has(i) ? 'disabled' : ''}>${esc(j.text)}</button>`).join('')}
                </div>`;
        }

        app().innerHTML = `
            <div class="battle-screen" style="--arena-color:${arena.color}">
                <div class="battle-top">
                    <button class="arena-link" id="backHome">← Arenas</button>
                    <span class="battle-level">${arena.name} · ${levelLabel} ${bossTag}</span>
                    <span class="battle-dmg">dano inimigo: ${enemyDamage(certId)}</span>
                </div>
                <div class="battle-field">
                    <div class="fighter" id="heroWrap">
                        ${hpBarHtml('heroHp', a.heroCurrentHp, heroMaxHp(a), '#2dd4bf')}
                        <img id="heroSprite" class="sprite" alt="Herói">
                        <div class="sprite-fallback">${state.heroChoice === 'feminino' ? '👩‍🚀' : '🧑‍🚀'}</div>
                        <div class="fighter-name">Você · nv. ${heroLevel(a)}</div>
                    </div>
                    <div class="vs">VS</div>
                    <div class="fighter ${battle.boss ? 'is-boss' : ''}" id="enemyWrap">
                        ${hpBarHtml('enemyHp', battle.enemyHp, battle.enemyMaxHp, '#ff6b6b')}
                        <img id="enemySprite" class="sprite" alt="${esc(info.name)}">
                        <div class="sprite-fallback">${info.emoji}</div>
                        <div class="fighter-name">${esc(info.name)}${battle.boss ? ' 👑' : ''}</div>
                    </div>
                </div>
                <div class="battle-question">
                    <p class="question-text">${esc(q.text)}</p>
                    ${phaseHtml}
                </div>
            </div>`;

        setSprite($('#heroSprite'), heroSpriteUrl('idle'));
        setSprite($('#enemySprite'), enemySpriteUrl(certId, battle.topic, 'idle'));
        $('#backHome').addEventListener('click', () => { saveState(); renderHome(); });

        if (battle.phase === 'eliminate') {
            app().querySelectorAll('.option-check input').forEach(cb => {
                cb.addEventListener('change', () => {
                    const text = cb.dataset.text;
                    if (cb.checked) {
                        if (battle.selected.size >= 2) { cb.checked = false; return; }
                        battle.selected.add(text);
                    } else {
                        battle.selected.delete(text);
                    }
                    renderBattle();
                });
            });
            const btn = $('#confirmElim');
            if (btn) btn.addEventListener('click', confirmElimination);
        } else if (battle.phase === 'choose') {
            app().querySelectorAll('.option-btn').forEach(b =>
                b.addEventListener('click', () => chooseOption(b.dataset.text)));
        } else if (battle.phase === 'finalblow') {
            app().querySelectorAll('.option-btn.just:not(.disabled)').forEach(b =>
                b.addEventListener('click', () => chooseJustification(parseInt(b.dataset.just, 10))));
        }
    }

    function renderNoContent(certId) {
        app().innerHTML = `
            <div class="arena-end">
                <h2>😴 Sem inimigos por aqui…</h2>
                <p>Esta arena ainda não tem questões com conteúdo do CloudArena na dificuldade atual.
                   Novos inimigos chegam conforme a cobertura de conteúdo cresce.</p>
                <button class="arena-action" id="backHome2">← Voltar às arenas</button>
            </div>`;
        $('#backHome2').addEventListener('click', renderHome);
    }

    function renderGameOver(certId, levelReached) {
        const arena = ARENAS[certId];
        app().innerHTML = `
            <div class="arena-end gameover">
                <h2>💀 Game Over</h2>
                <p>Você caiu no nível <strong>${esc(levelReached)}</strong> da arena ${arena.name}.</p>
                <p>Recorde da arena: nível ${state.arenas[certId].bestLevelReached}.</p>
                <div class="end-actions">
                    <button class="arena-action" id="retryBtn">⚔️ Nova run</button>
                    <button class="arena-action ghost" id="shareBtn">📤 Compartilhar</button>
                    <button class="arena-link" id="backHome3">← Arenas</button>
                </div>
                <canvas id="shareCanvas" width="1080" height="566" style="display:none"></canvas>
            </div>`;
        $('#retryBtn').addEventListener('click', () => enterArena(certId));
        $('#backHome3').addEventListener('click', renderHome);
        $('#shareBtn').addEventListener('click', () => shareCard(certId, `Cheguei ao nível ${levelReached}`, 'gameover'));
    }

    function renderArenaVictory(certId) {
        const arena = ARENAS[certId];
        app().innerHTML = `
            <div class="arena-end victory">
                <h2>🎉 Arena concluída!</h2>
                <p>Você derrotou o chefe final da arena <strong>${arena.name}</strong> — nível ${arena.maxLevel} completo!</p>
                <div class="end-actions">
                    <button class="arena-action ghost" id="shareBtn">📤 Compartilhar</button>
                    <button class="arena-link" id="backHome4">← Arenas</button>
                </div>
                <canvas id="shareCanvas" width="1080" height="566" style="display:none"></canvas>
            </div>`;
        $('#backHome4').addEventListener('click', renderHome);
        $('#shareBtn').addEventListener('click', () => shareCard(certId, `Arena ${arena.name} concluída!`, 'victory'));
    }

    function renderChallengeIntro(certId) {
        const arena = ARENAS[certId];
        app().innerHTML = `
            <div class="arena-end victory">
                <h2>🏔️ Nível ${arena.maxLevel} vencido!</h2>
                <p>O <strong>Modo Desafio</strong> foi desbloqueado: 20 batalhas seguidas, 100% avançado,
                   chefe a cada 5. Sua run continua — mesmo herói, HP restaurado ao máximo como recompensa.</p>
                <p>⚠️ Se você cair, a próxima run recomeça do nível 1 — o Desafio precisa ser reconquistado.</p>
                <div class="end-actions">
                    <button class="arena-action" id="startChallenge">🔥 Entrar no Desafio</button>
                    <button class="arena-link" id="backHome5">← Arenas (continua depois)</button>
                </div>
            </div>`;
        $('#startChallenge').addEventListener('click', () => startEncounter(certId));
        $('#backHome5').addEventListener('click', renderHome);
    }

    function renderChallengeVictory(certId) {
        const arena = ARENAS[certId];
        app().innerHTML = `
            <div class="arena-end victory">
                <h2>👑 TOPO DA ARENA!</h2>
                <p>Você venceu as 20 batalhas do Modo Desafio da arena <strong>${arena.name}</strong> —
                   incluindo o chefe final de 32 HP. Não existe nada mais difícil neste jogo.</p>
                <div class="end-actions">
                    <button class="arena-action ghost" id="shareBtn">📤 Compartilhar</button>
                    <button class="arena-link" id="backHome6">← Arenas</button>
                </div>
                <canvas id="shareCanvas" width="1080" height="566" style="display:none"></canvas>
            </div>`;
        $('#backHome6').addEventListener('click', renderHome);
        $('#shareBtn').addEventListener('click', () => shareCard(certId, 'Topo do Modo Desafio!', 'victory'));
    }

    // ════════════════════════════════════════════════════════════════════
    // Conquistas — tela (spec seção 14)
    // ════════════════════════════════════════════════════════════════════
    function renderAchievements() {
        const rows = [];
        for (const def of achievementDefs) {
            if (def.scope === 'global') {
                rows.push({ id: def.id, def, unlocked: !!achState.unlocked[def.id] });
            } else if (def.scope === 'per-arena') {
                const arenas = def.arenas || Object.keys(ARENAS);
                for (const id of arenas) {
                    rows.push({
                        id: `${def.id}:${id}`, def,
                        suffix: ` — ${ARENAS[id].name}`,
                        unlocked: !!achState.unlocked[`${def.id}:${id}`] || !!achState.unlocked[`${def.id.replace(/s$/, '')}:${id}`]
                            || !!achState.unlocked[`cleared:${id}`] && def.id === 'cleared',
                    });
                }
            }
        }
        // per-boss: geradas dos dados — lista as desbloqueadas
        const bossRows = Object.keys(achState.unlocked)
            .filter(k => k.startsWith('boss:'))
            .map(k => `<div class="ach-item unlocked"><span class="ach-icon">⚔️</span><div><strong>Chefe derrotado</strong><small>${esc(k.replace('boss:', '').replace(':', ' — nível '))}</small></div></div>`)
            .join('');

        app().innerHTML = `
            <div class="arena-achievements">
                <div class="battle-top">
                    <button class="arena-link" id="backHome7">← Arenas</button>
                    <span class="battle-level">🏆 Conquistas</span><span></span>
                </div>
                <div class="ach-grid">
                    ${rows.map(r => {
                        const key = r.def.scope === 'global' ? r.def.id : r.id;
                        const unlocked = !!achState.unlocked[key];
                        return `
                        <div class="ach-item ${unlocked ? 'unlocked' : 'locked'}">
                            <span class="ach-icon">${r.def.icon || '🏅'}</span>
                            <div>
                                <strong>${esc(r.def.name)}${r.suffix || ''}</strong>
                                <small>${esc(r.def.description)}</small>
                            </div>
                        </div>`;
                    }).join('')}
                </div>
                ${bossRows ? `<h3 class="ach-section">Chefes derrotados</h3><div class="ach-grid">${bossRows}</div>` : ''}
            </div>`;
        $('#backHome7').addEventListener('click', renderHome);
    }

    // ════════════════════════════════════════════════════════════════════
    // Compartilhamento — canvas client-side (spec seção 9)
    // ════════════════════════════════════════════════════════════════════
    function shareCard(certId, headline, kind) {
        const arena = ARENAS[certId];
        const a = state.arenas[certId];
        const canvas = $('#shareCanvas');
        const ctx = canvas.getContext('2d');
        const brand = (window.Branding && window.Branding.current) ? window.Branding.current : { name: 'CloudPath' };

        // fundo
        const grad = ctx.createLinearGradient(0, 0, 1080, 566);
        grad.addColorStop(0, '#0f172a');
        grad.addColorStop(1, '#1a1a2e');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 1080, 566);
        ctx.fillStyle = arena.color;
        ctx.fillRect(0, 0, 1080, 10);

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 56px Montserrat, sans-serif';
        ctx.fillText('CloudArena', 60, 110);
        ctx.font = '28px Montserrat, sans-serif';
        ctx.fillStyle = '#8892a6';
        ctx.fillText(`${brand.name || 'CloudPath'} — arena ${arena.name} (${arena.title})`, 60, 160);

        ctx.fillStyle = kind === 'victory' ? '#2dd4bf' : '#ffd166';
        ctx.font = 'bold 64px Montserrat, sans-serif';
        ctx.fillText(headline, 60, 280);

        ctx.fillStyle = '#cdd3de';
        ctx.font = '32px Montserrat, sans-serif';
        ctx.fillText(`Herói nível ${heroLevel(a)} · Recorde: nível ${a.bestLevelReached}`, 60, 350);
        ctx.font = '90px serif';
        ctx.fillText(state.heroChoice === 'feminino' ? '👩‍🚀' : '🧑‍🚀', 880, 320);

        ctx.fillStyle = '#8892a6';
        ctx.font = '24px Montserrat, sans-serif';
        ctx.fillText('Estude jogando — simulados AWS gamificados', 60, 500);

        canvas.toBlob(async (blob) => {
            const file = new File([blob], 'cloudarena.png', { type: 'image/png' });
            const text = `${headline} na arena ${arena.name} do CloudArena! ⚔️`;
            if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
                try { await navigator.share({ files: [file], text }); return; } catch (e) { /* cancelado */ }
            }
            // fallback: download + links diretos
            const url = URL.createObjectURL(blob);
            const box = document.createElement('div');
            box.className = 'share-box';
            box.innerHTML = `
                <a href="${url}" download="cloudarena.png" class="arena-action">⬇️ Baixar cartão (PNG)</a>
                <a class="arena-action ghost" target="_blank" rel="noopener"
                   href="https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}">🐦 X</a>
                <a class="arena-action ghost" target="_blank" rel="noopener"
                   href="https://wa.me/?text=${encodeURIComponent(text)}">💬 WhatsApp</a>`;
            const end = document.querySelector('.arena-end');
            const old = end.querySelector('.share-box');
            if (old) old.remove();
            end.appendChild(box);
        }, 'image/png');
    }

    // ════════════════════════════════════════════════════════════════════
    // Boot
    // ════════════════════════════════════════════════════════════════════
    async function init() {
        try {
            const defs = await fetchJson('data/cloudarena/achievements.json');
            achievementDefs = defs.achievements || [];
        } catch (e) {
            achievementDefs = [];
        }
        // registra o dia de jogo (conquista Reservado)
        const today = new Date().toISOString().slice(0, 10);
        state.playDays = state.playDays || [];
        if (!state.playDays.includes(today)) { state.playDays.push(today); saveState(); }
        renderHome();
    }

    document.addEventListener('DOMContentLoaded', init);
})();
