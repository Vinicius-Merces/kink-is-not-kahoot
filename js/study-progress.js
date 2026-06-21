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
