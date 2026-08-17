(() => {
    'use strict';

    const CATALOG_URL = (locale) => `/locales/${locale}/internal-literals.json`;
    const SKIP_TAGS = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'PRE', 'CODE', 'SVG']);
    let catalogs = null;
    let observer = null;
    let applying = false;

    const normalizedLocale = () => {
        const locale = window.I18n?.locale || document.documentElement.lang || 'pt-BR';
        return String(locale).toLowerCase().startsWith('en') ? 'en' : 'pt-BR';
    };

    async function loadCatalogs() {
        if (catalogs) return catalogs;
        const [ptResponse, enResponse] = await Promise.all([
            fetch(CATALOG_URL('pt-BR'), { cache: 'no-cache' }),
            fetch(CATALOG_URL('en'), { cache: 'no-cache' }),
        ]);
        if (!ptResponse.ok || !enResponse.ok) {
            throw new Error(`Internal literal catalogs unavailable: PT=${ptResponse.status}, EN=${enResponse.status}`);
        }
        const [pt, en] = await Promise.all([ptResponse.json(), enResponse.json()]);
        const ptMap = pt.internalLiterals || {};
        const enMap = en.internalLiterals || {};
        const ptKeys = Object.keys(ptMap).sort();
        const enKeys = Object.keys(enMap).sort();
        if (ptKeys.length !== enKeys.length || ptKeys.some((key, index) => key !== enKeys[index])) {
            throw new Error('Internal PT/EN literal catalogs are out of parity');
        }
        catalogs = { 'pt-BR': ptMap, en: enMap };
        return catalogs;
    }

    function buildMap(locale) {
        const sourceLocale = locale === 'en' ? 'pt-BR' : 'en';
        const source = catalogs[sourceLocale];
        const target = catalogs[locale];
        const map = new Map();
        for (const key of Object.keys(source)) {
            const from = String(source[key] || '').trim();
            const to = String(target[key] || '').trim();
            if (from && to && from !== to) map.set(from, to);
        }
        return map;
    }

    function preserveWhitespace(original, replacement) {
        const leading = original.match(/^\s*/)?.[0] || '';
        const trailing = original.match(/\s*$/)?.[0] || '';
        return `${leading}${replacement}${trailing}`;
    }

    function translateDynamic(value, locale) {
        if (!value) return value;
        const rules = locale === 'en'
            ? [
                [/^Questão\s+(\d+)$/i, 'Question $1'],
                [/^Pergunta\s+(\d+)$/i, 'Question $1'],
                [/^Nível\s+(\d+)$/i, 'Level $1'],
                [/^Pontos:\s*(.+)$/i, 'Points: $1'],
                [/^Pontuação:\s*(.+)$/i, 'Score: $1'],
                [/^Tempo:\s*(.+)$/i, 'Time: $1'],
                [/^Acertos:\s*(.+)$/i, 'Correct: $1'],
                [/^Erros:\s*(.+)$/i, 'Mistakes: $1'],
                [/^(\d+)\s+participantes?$/i, '$1 participants'],
                [/^(\d+)\s+jogadores?$/i, '$1 players'],
            ]
            : [
                [/^Question\s+(\d+)$/i, 'Questão $1'],
                [/^Level\s+(\d+)$/i, 'Nível $1'],
                [/^Points:\s*(.+)$/i, 'Pontos: $1'],
                [/^Score:\s*(.+)$/i, 'Pontuação: $1'],
                [/^Time:\s*(.+)$/i, 'Tempo: $1'],
                [/^Correct:\s*(.+)$/i, 'Acertos: $1'],
                [/^Mistakes:\s*(.+)$/i, 'Erros: $1'],
                [/^(\d+)\s+participants?$/i, '$1 participantes'],
                [/^(\d+)\s+players?$/i, '$1 jogadores'],
            ];
        for (const [pattern, replacement] of rules) {
            if (pattern.test(value)) return value.replace(pattern, replacement);
        }
        return value;
    }

    function translateValue(value, map, locale) {
        if (typeof value !== 'string' || !value.trim()) return value;
        const trimmed = value.trim();
        const exact = map.get(trimmed);
        if (exact) return preserveWhitespace(value, exact);
        const dynamic = translateDynamic(trimmed, locale);
        return dynamic === trimmed ? value : preserveWhitespace(value, dynamic);
    }

    function applyNode(root, map, locale) {
        if (!root) return;
        if (root.nodeType === Node.TEXT_NODE) {
            const parent = root.parentElement;
            if (!parent || SKIP_TAGS.has(parent.tagName)) return;
            const translated = translateValue(root.nodeValue, map, locale);
            if (translated !== root.nodeValue) root.nodeValue = translated;
            return;
        }
        if (root.nodeType !== Node.ELEMENT_NODE && root !== document) return;
        const element = root.nodeType === Node.ELEMENT_NODE ? root : null;
        if (element && SKIP_TAGS.has(element.tagName)) return;

        if (element) {
            for (const attribute of ['aria-label', 'title', 'placeholder']) {
                if (!element.hasAttribute(attribute)) continue;
                const current = element.getAttribute(attribute);
                const translated = translateValue(current, map, locale);
                if (translated !== current) element.setAttribute(attribute, translated);
            }
        }

        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        let node;
        while ((node = walker.nextNode())) applyNode(node, map, locale);
        const scope = root.querySelectorAll ? root.querySelectorAll('[aria-label], [title], [placeholder]') : [];
        for (const child of scope) {
            for (const attribute of ['aria-label', 'title', 'placeholder']) {
                if (!child.hasAttribute(attribute)) continue;
                const current = child.getAttribute(attribute);
                const translated = translateValue(current, map, locale);
                if (translated !== current) child.setAttribute(attribute, translated);
            }
        }
    }

    async function apply(root = document) {
        if (applying) return;
        applying = true;
        try {
            await loadCatalogs();
            const locale = normalizedLocale();
            document.documentElement.dataset.internalLocale = locale;
            applyNode(root, buildMap(locale), locale);
        } catch (error) {
            console.error('[Internal i18n]', error);
        } finally {
            applying = false;
        }
    }

    function observe() {
        if (observer || !document.body) return;
        observer = new MutationObserver((mutations) => {
            if (applying) return;
            const roots = new Set();
            for (const mutation of mutations) {
                if (mutation.type === 'characterData') roots.add(mutation.target);
                for (const node of mutation.addedNodes || []) roots.add(node);
                if (mutation.type === 'attributes') roots.add(mutation.target);
            }
            for (const root of roots) apply(root);
        });
        observer.observe(document.body, {
            subtree: true,
            childList: true,
            characterData: true,
            attributes: true,
            attributeFilter: ['aria-label', 'title', 'placeholder'],
        });
    }

    document.addEventListener('cloudpath:i18nready', () => apply(document));
    document.addEventListener('cloudpath:localechange', () => apply(document));
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => { apply(document); observe(); }, { once: true });
    } else {
        apply(document);
        observe();
    }
})();
