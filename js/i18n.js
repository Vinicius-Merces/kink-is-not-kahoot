/** CloudPath i18n runtime. */
(function (global) {
    'use strict';

    const DEFAULT_LOCALE = 'pt-BR';
    const SUPPORTED_LOCALES = ['pt-BR', 'en'];
    const STORAGE_KEY = 'cloudpath_locale_v1';
    const QUERY_KEY = 'lang';
    const CATALOG_FILES = ['ui.json', 'simulator.json'];
    const catalogs = new Map();
    const adapters = [];
    let activeLocale = DEFAULT_LOCALE;
    let initialized = false;
    let readyPromise = null;

    function normalizeLocale(value) {
        if (!value) return null;
        const raw = String(value).trim().toLowerCase();
        if (['pt', 'pt-br', 'pt_br'].includes(raw)) return 'pt-BR';
        if (['en', 'en-us', 'en_us', 'en-gb'].includes(raw)) return 'en';
        return null;
    }

    function currentLeaf() {
        let path = '/';
        try { path = global.location.pathname || '/'; } catch (_) {}
        return path.split('/').filter(Boolean).pop() || 'index.html';
    }

    function resolveInitialLocale() {
        let query = null;
        let stored = null;
        try { query = normalizeLocale(new URLSearchParams(global.location.search).get(QUERY_KEY)); } catch (_) {}
        try { stored = normalizeLocale(global.localStorage.getItem(STORAGE_KEY)); } catch (_) {}
        return query || stored || DEFAULT_LOCALE;
    }

    function deepMerge(target, source) {
        const output = target && typeof target === 'object' && !Array.isArray(target) ? target : {};
        Object.entries(source || {}).forEach(([key, value]) => {
            if (value && typeof value === 'object' && !Array.isArray(value)) {
                output[key] = deepMerge(output[key], value);
            } else {
                output[key] = value;
            }
        });
        return output;
    }

    async function fetchCatalog(locale) {
        if (catalogs.has(locale)) return catalogs.get(locale);
        const catalog = {};
        for (const file of CATALOG_FILES) {
            const response = await fetch(`locales/${locale}/${file}`, { cache: 'no-cache' });
            if (!response.ok) throw new Error(`i18n catalog ${locale}/${file} unavailable (HTTP ${response.status})`);
            deepMerge(catalog, await response.json());
        }
        catalogs.set(locale, catalog);
        return catalog;
    }

    function readKey(object, key) {
        return String(key || '').split('.').reduce((value, part) => {
            if (!value || typeof value !== 'object') return undefined;
            return value[part];
        }, object);
    }

    function interpolate(value, params) {
        if (typeof value !== 'string' || !params) return value;
        return value.replace(/\{([a-zA-Z0-9_]+)\}/g, (match, key) =>
            Object.prototype.hasOwnProperty.call(params, key) ? String(params[key]) : match);
    }

    function t(key, params) {
        const value = readKey(catalogs.get(activeLocale), key);
        const fallback = readKey(catalogs.get(DEFAULT_LOCALE), key);
        if (typeof value === 'string') return interpolate(value, params);
        if (typeof fallback === 'string') return interpolate(fallback, params);
        return key;
    }

    function translate(root, selector, keyAttribute, targetAttribute) {
        root.querySelectorAll(selector).forEach((element) => {
            const key = element.getAttribute(keyAttribute);
            if (!key) return;
            const value = t(key);
            if (targetAttribute) element.setAttribute(targetAttribute, value);
            else element.textContent = value;
        });
    }

    function applyMeta() {
        // Page-specific metadata is migrated with each page adapter.
        if (currentLeaf() !== 'index.html') return;
        document.title = t('meta.title');
        const bindings = [
            ['meta[name="description"]', 'meta.description'],
            ['meta[property="og:title"]', 'meta.ogTitle'],
            ['meta[property="og:description"]', 'meta.ogDescription']
        ];
        bindings.forEach(([selector, key]) => {
            const element = document.querySelector(selector);
            if (element) element.setAttribute('content', t(key));
        });
    }

    function applyBrandSurface() {
        document.querySelectorAll('.brand-hero-tagline').forEach(el => { el.textContent = t('brand.tagline'); });
        document.querySelectorAll('.nav-logo').forEach(el => { el.setAttribute('aria-label', t('brand.homeAriaLabel')); });
    }

    function runAdapters() {
        adapters.forEach((adapter) => {
            try { adapter({ locale: activeLocale, t }); }
            catch (error) { console.warn('[i18n] page adapter failed:', error); }
        });
    }

    function apply(root) {
        const scope = root || document;
        document.documentElement.lang = activeLocale === 'pt-BR' ? 'pt-BR' : 'en';
        document.documentElement.dataset.locale = activeLocale;
        if (scope === document) runAdapters();
        translate(scope, '[data-i18n]', 'data-i18n');
        translate(scope, '[data-i18n-placeholder]', 'data-i18n-placeholder', 'placeholder');
        translate(scope, '[data-i18n-aria-label]', 'data-i18n-aria-label', 'aria-label');
        translate(scope, '[data-i18n-title]', 'data-i18n-title', 'title');
        if (scope === document) {
            applyMeta();
            applyBrandSurface();
            updateLanguageSwitcher();
        }
    }

    function registerAdapter(adapter) {
        if (typeof adapter !== 'function' || adapters.includes(adapter)) return;
        adapters.push(adapter);
        if (initialized) apply(document);
    }

    async function setLocale(locale, options) {
        const opts = options || {};
        const normalized = normalizeLocale(locale);
        if (!normalized || !SUPPORTED_LOCALES.includes(normalized)) throw new Error(`Unsupported locale: ${locale}`);
        await Promise.all([
            fetchCatalog(DEFAULT_LOCALE),
            normalized === DEFAULT_LOCALE ? Promise.resolve() : fetchCatalog(normalized)
        ]);
        const previous = activeLocale;
        activeLocale = normalized;
        if (opts.persist !== false) {
            try { global.localStorage.setItem(STORAGE_KEY, normalized); } catch (_) {}
        }
        apply(document);
        if (previous !== normalized || opts.forceEvent) {
            document.dispatchEvent(new CustomEvent('cloudpath:localechange', {
                detail: { locale: normalized, previousLocale: previous }
            }));
        }
        return normalized;
    }

    function ensureSwitcherStyles() {
        if (document.getElementById('cloudpath-i18n-styles')) return;
        const style = document.createElement('style');
        style.id = 'cloudpath-i18n-styles';
        style.textContent = `
            .cp-language-switcher{display:inline-flex;align-items:center;gap:2px;padding:3px;margin-left:auto;border:1px solid rgba(255,255,255,.14);border-radius:999px;background:rgba(10,18,34,.48);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);flex-shrink:0}
            .navbar-landing .user-info .cp-language-switcher{margin-left:0}
            .nav-menu .cp-language-switcher{margin-left:.25rem;margin-right:.1rem}
            .cp-language-switcher button{min-width:38px;min-height:30px;padding:5px 9px;border:0;border-radius:999px;background:transparent;color:rgba(255,255,255,.68);font:600 11px/1 'Montserrat',sans-serif;letter-spacing:.05em;cursor:pointer;transition:background .2s ease,color .2s ease}
            .cp-language-switcher button:hover,.cp-language-switcher button:focus-visible{color:#fff;outline:none;background:rgba(255,255,255,.08)}
            .cp-language-switcher button[aria-pressed="true"]{color:#fff;background:rgba(78,205,196,.2);box-shadow:inset 0 0 0 1px rgba(78,205,196,.34)}
            @media(max-width:900px){.nav-menu .cp-language-switcher{margin:.4rem .3rem .8rem;width:max-content}.cp-language-switcher{padding:2px}.cp-language-switcher button{min-width:31px;min-height:28px;padding-inline:6px}}
            @media(max-width:720px){.navbar-landing .user-info{gap:.3rem}.navbar-landing .nav-login-btn{padding-inline:.55rem}}
            @media(max-width:380px){.cp-language-switcher button{min-width:29px;padding-inline:5px;font-size:10px}}
        `;
        document.head.appendChild(style);
    }

    function switcherHost() {
        return document.querySelector('.navbar-landing .user-info')
            || document.querySelector('.navbar .nav-menu')
            || document.querySelector('.navbar .nav-container')
            || document.querySelector('.navbar')
            || document.querySelector('nav');
    }

    function createLanguageSwitcher() {
        if (document.querySelector('.cp-language-switcher')) return;
        const host = switcherHost();
        if (!host) return;
        ensureSwitcherStyles();
        const group = document.createElement('div');
        group.className = 'cp-language-switcher';
        group.setAttribute('role', 'group');
        [['pt-BR', 'PT'], ['en', 'EN']].forEach(([locale, label]) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.dataset.locale = locale;
            button.textContent = label;
            button.addEventListener('click', () => setLocale(locale).catch(error => console.error('[i18n] locale switch failed:', error)));
            group.appendChild(button);
        });

        if (host.classList.contains('nav-menu')) {
            const logout = host.querySelector('#logoutBtn, .btn-logout');
            host.insertBefore(group, logout || null);
        } else {
            host.prepend(group);
        }
        updateLanguageSwitcher();
    }

    function updateLanguageSwitcher() {
        const group = document.querySelector('.cp-language-switcher');
        if (!group) return;
        group.setAttribute('aria-label', t('language.selectorLabel'));
        group.querySelectorAll('button[data-locale]').forEach(button => {
            const locale = button.dataset.locale;
            button.setAttribute('aria-pressed', locale === activeLocale ? 'true' : 'false');
            button.setAttribute('aria-label', t(locale === 'pt-BR' ? 'language.portuguese' : 'language.english'));
        });
    }

    function adapterUrls() {
        const urls = ['js/i18n-shared.js'];
        if (currentLeaf() === 'index.html') urls.push('js/i18n-home.js');
        return urls;
    }

    function loadAdapter(path) {
        return new Promise(resolve => {
            const existing = Array.from(document.querySelectorAll('script[data-cloudpath-i18n-adapter]'))
                .find(script => script.dataset.cloudpathI18nAdapter === path);
            if (existing) { resolve(); return; }
            const script = document.createElement('script');
            script.src = new URL(path, document.baseURI).href;
            script.dataset.cloudpathI18nAdapter = path;
            script.async = true;
            script.onload = resolve;
            script.onerror = () => { console.warn(`[i18n] page adapter unavailable: ${path}`); resolve(); };
            document.head.appendChild(script);
        });
    }

    async function loadAdapters() {
        for (const path of adapterUrls()) await loadAdapter(path);
    }

    async function init() {
        if (readyPromise) return readyPromise;
        readyPromise = (async () => {
            const initial = resolveInitialLocale();
            await fetchCatalog(DEFAULT_LOCALE);
            if (initial !== DEFAULT_LOCALE) {
                try { await fetchCatalog(initial); }
                catch (error) { console.warn('[i18n] requested locale unavailable, using pt-BR:', error.message); }
            }
            activeLocale = catalogs.has(initial) ? initial : DEFAULT_LOCALE;
            try { global.localStorage.setItem(STORAGE_KEY, activeLocale); } catch (_) {}
            if (document.readyState === 'loading') {
                await new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve, { once: true }));
            }
            await loadAdapters();
            apply(document);
            createLanguageSwitcher();
            initialized = true;
            document.dispatchEvent(new CustomEvent('cloudpath:i18nready', { detail: { locale: activeLocale } }));
            return activeLocale;
        })();
        return readyPromise;
    }

    global.I18n = {
        DEFAULT_LOCALE,
        SUPPORTED_LOCALES: SUPPORTED_LOCALES.slice(),
        CATALOG_FILES: CATALOG_FILES.slice(),
        normalizeLocale,
        init,
        setLocale,
        apply,
        registerAdapter,
        t,
        get locale() { return activeLocale; },
        get initialized() { return initialized; },
        get ready() { return readyPromise || init(); }
    };

    init().catch(error => {
        console.error('[i18n] initialization failed:', error);
        document.documentElement.lang = DEFAULT_LOCALE;
    });
})(window);
