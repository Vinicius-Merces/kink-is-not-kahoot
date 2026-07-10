/**
 * StudyProgress — modulo compartilhado entre as paginas de trilha (apostila),
 * simulados e historico: conclusao de capitulos, streak de estudo, badges de
 * progresso, e o mapa dominio-do-exame -> capitulo-da-apostila (usado para
 * linkar "revisar este dominio" a partir do historico de simulados).
 *
 * Tudo fica em localStorage (sem backend) sob uma unica chave para nao
 * espalhar chaves soltas pelo localStorage.
 */
(function (global) {
    'use strict';

    const STORAGE_KEY = 'kink_study_progress_v1';

    function loadState() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return { trilhas: {}, streak: { current: 0, longest: 0, lastDate: null } };
            const parsed = JSON.parse(raw);
            return {
                trilhas: parsed.trilhas || {},
                streak: parsed.streak || { current: 0, longest: 0, lastDate: null },
            };
        } catch (e) {
            return { trilhas: {}, streak: { current: 0, longest: 0, lastDate: null } };
        }
    }

    function saveState(state) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch (e) {
            // localStorage indisponivel (modo privado etc.) - degrada em silencio
        }
    }

    // ── Conclusao de capitulos ──────────────────────────────────────────────
    function toggleChapter(trilhaId, capId) {
        const state = loadState();
        if (!state.trilhas[trilhaId]) state.trilhas[trilhaId] = { completed: [] };
        const list = state.trilhas[trilhaId].completed;
        const idx = list.indexOf(capId);
        let nowComplete;
        if (idx === -1) {
            list.push(capId);
            nowComplete = true;
        } else {
            list.splice(idx, 1);
            nowComplete = false;
        }
        saveState(state);
        scheduleSync();
        return nowComplete;
    }

    function isChapterComplete(trilhaId, capId) {
        const state = loadState();
        const trilha = state.trilhas[trilhaId];
        return !!(trilha && trilha.completed.includes(capId));
    }

    function getCompletedSet(trilhaId) {
        const state = loadState();
        const trilha = state.trilhas[trilhaId];
        return new Set(trilha ? trilha.completed : []);
    }

    // ── Streak de estudo ─────────────────────────────────────────────────────
    function todayKey() {
        const d = new Date();
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    }

    function daysBetween(a, b) {
        const msPerDay = 24 * 60 * 60 * 1000;
        return Math.round((new Date(b) - new Date(a)) / msPerDay);
    }

    function recordStudyActivity() {
        const state = loadState();
        const today = todayKey();
        const streak = state.streak;

        if (streak.lastDate === today) {
            return streak; // ja registrado hoje, nao muda nada
        }

        if (streak.lastDate) {
            const gap = daysBetween(streak.lastDate, today);
            streak.current = gap === 1 ? streak.current + 1 : 1;
        } else {
            streak.current = 1;
        }

        streak.longest = Math.max(streak.longest || 0, streak.current);
        streak.lastDate = today;
        state.streak = streak;
        saveState(state);
        scheduleSync();
        return streak;
    }

    function getStreak() {
        const state = loadState();
        // Se o ultimo estudo nao foi hoje nem ontem, o streak "ativo" e zero
        // (so resolvido de fato na proxima recordStudyActivity, mas exibimos
        // honestamente para nao mostrar um streak que ja quebrou).
        const streak = state.streak;
        if (streak.lastDate) {
            const gap = daysBetween(streak.lastDate, todayKey());
            if (gap > 1) return { current: 0, longest: streak.longest || 0 };
        }
        return { current: streak.current || 0, longest: streak.longest || 0 };
    }


    // ── Sincronizacao com a conta (Firebase Auth + backend) ─────────────────
    // O progresso continua funcionando offline via localStorage; quando o
    // usuario esta logado, o estado e mesclado com o salvo na conta e cada
    // alteracao e enviada ao backend (debounced), permitindo estudar no
    // celular e continuar no computador com o mesmo progresso.
    let syncTimer = null;
    let syncInitialized = false;

    function mergeStates(local, remote) {
        if (!remote || typeof remote !== 'object') return local;
        const merged = { trilhas: {}, streak: {} };
        const remoteTrilhas = remote.trilhas || {};
        const ids = new Set([...Object.keys(local.trilhas || {}), ...Object.keys(remoteTrilhas)]);
        ids.forEach(id => {
            const l = (local.trilhas[id] && local.trilhas[id].completed) || [];
            const r = (remoteTrilhas[id] && remoteTrilhas[id].completed) || [];
            merged.trilhas[id] = { completed: Array.from(new Set([...l, ...r])) };
        });
        const ls = local.streak || {};
        const rs = remote.streak || {};
        merged.streak = (String(rs.lastDate || '') > String(ls.lastDate || '')) ? { ...rs } : { ...ls };
        merged.streak.longest = Math.max(ls.longest || 0, rs.longest || 0, merged.streak.current || 0);
        return merged;
    }

    function firebaseUser() {
        try {
            return (typeof firebase !== 'undefined' && firebase.auth) ? firebase.auth().currentUser : null;
        } catch (e) { return null; }
    }

    async function pushState() {
        const user = firebaseUser();
        if (!user) return;
        try {
            const token = await user.getIdToken();
            await fetch('/api/study-progress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ state: loadState() })
            });
        } catch (e) { /* offline/erro de rede - tenta na proxima alteracao */ }
    }

    function scheduleSync() {
        if (!firebaseUser()) return;
        clearTimeout(syncTimer);
        syncTimer = setTimeout(pushState, 2500);
    }

    async function pullAndMerge(user) {
        try {
            const token = await user.getIdToken();
            const res = await fetch('/api/study-progress', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (!data.success) return;
            const before = JSON.stringify(loadState());
            const merged = mergeStates(loadState(), data.state);
            if (JSON.stringify(merged) !== before) {
                saveState(merged);
                window.dispatchEvent(new CustomEvent('studyprogress:synced'));
            }
            pushState();
        } catch (e) { /* segue com o estado local */ }
    }

    function initSync() {
        if (syncInitialized) return;
        if (typeof firebase === 'undefined' || !firebase.auth) return; // SDK ainda nao carregou
        syncInitialized = true;
        firebase.auth().onAuthStateChanged(user => { if (user) pullAndMerge(user); });
    }

    // O firebase carrega depois deste script: tenta na carga da pagina e
    // re-tenta por alguns segundos ate o SDK existir.
    if (typeof window !== 'undefined') {
        window.addEventListener('load', () => {
            let tries = 0;
            const timer = setInterval(() => {
                initSync();
                if (syncInitialized || ++tries > 20) clearInterval(timer);
            }, 500);
        });
    }

    // ── Badges por percentual de conclusao ───────────────────────────────────
    const BADGE_TIERS = [
        { min: 100, emoji: '🏆', label: 'Apostila completa' },
        { min: 75, emoji: '⭐', label: 'Quase lá' },
        { min: 50, emoji: '🔥', label: 'Na metade' },
        { min: 1, emoji: '🌱', label: 'Começando' },
        { min: 0, emoji: '📖', label: 'Não iniciado' },
    ];

    function getBadge(percent) {
        return BADGE_TIERS.find(tier => percent >= tier.min) || BADGE_TIERS[BADGE_TIERS.length - 1];
    }

    // ── Mapa dominio do exame -> capitulos da apostila ───────────────────────
    // Usado pelo historico de simulados para linkar "revisar este dominio"
    // direto na apostila certa. Nao precisa ser uma particao perfeita dos
    // capitulos - so precisa apontar para os capitulos mais relevantes.
    const DOMAIN_CHAPTER_MAP = {
        'SAA-C03': {
            trilhaId: 'saa-c03',
            trilhaUrl: 'trilha-saa.html',
            domains: {
                'secure-architectures': [1, 4, 9, 17, 19],
                'resilient-architectures': [2, 5, 6, 7],
                'high-performing-architectures': [3, 8, 12, 14, 16, 18],
                'cost-optimized-architectures': [13],
            },
        },
        'DEA-C01': {
            trilhaId: 'dea-c01',
            trilhaUrl: 'trilha-dea.html',
            domains: {
                'data-ingestion-transformation': [1, 2, 3, 4, 8],
                'data-store-management': [5, 6, 7, 12],
                'data-operations-support': [9, 10],
                'data-security-governance': [11],
            },
        },
        'DVA-C02': {
            trilhaId: 'dva-c02',
            trilhaUrl: 'trilha-dva.html',
            domains: {
                'development-aws-services': [1, 2, 3, 4, 5, 6],
                'security': [7, 8],
                'deployment': [9, 10, 11, 13],
                'troubleshooting-optimization': [12, 14],
            },
        },
    };

    function getReviewChapters(certCode, domainId) {
        const certMap = DOMAIN_CHAPTER_MAP[certCode];
        if (!certMap) return null;
        const chapters = certMap.domains[domainId];
        if (!chapters || !chapters.length) return null;
        return { trilhaUrl: certMap.trilhaUrl, chapters };
    }

    global.StudyProgress = {
        toggleChapter,
        isChapterComplete,
        getCompletedSet,
        recordStudyActivity,
        getStreak,
        getBadge,
        getReviewChapters,
    };
})(window);
