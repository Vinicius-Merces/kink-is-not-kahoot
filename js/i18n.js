/**
 * CloudPath i18n runtime.
 *
 * Phase 0 goals:
 * - one locale source of truth for the whole frontend
 * - persistent PT/EN selection
 * - safe fallback to pt-BR
 * - key-based DOM translation instead of text search/replace
 * - no coupling with narration assets
 *
 * Supported markup:
 *   data-i18n="common.login"
 *   data-i18n-placeholder="quiz.roomCode"
 *   data-i18n-aria-label="common.close"
 *   data-i18n-title="common.close"
 */
(function (global) {
    'use strict';

    const DEFAULT_LOCALE = 'pt-BR';
    const SUPPORTED_LOCALES = ['pt-BR', 'en'];
    const STORAGE_KEY = 'cloudpath_locale_v1';
    const QUERY_KEY = 'lang';
    const CATALOG_ROOT = 'locales';

    const catalogs = new Map();
    let activeLocale = DEFAULT_LOCALE;
    let initialized = false;
    let readyPromise = null;

    function normalizeLocale(value) {
        if (!value) return null;
        const raw = String(value).trim().toLowerCase();
        if (raw === 'pt' || raw === 'pt-br' || raw === 'pt_br') return 'pt-BR';
        if (raw === 'en' || raw === 'en-us' || raw === 'en_us' || raw === 'en-gb') return 'en';
        return null;
    }

    function queryLocale() {
        try {
            return normalizeLocale(new URLSearchParams(global.location.search).get(QUERY_KEY));
        } catch (_) {
            return null;
        }
    }

    function storedLocale() {
        try {
            return normalizeLocale(global.localStorage.getItem(STORAGE_KEY));
        } catch (_) {
            return null;
        }
    }

    function resolveInitialLocale() {
        return queryLocale() || storedLocale() || DEFAULT_LOCALE;
    }

    async function fetchCatalog(locale) {
        if (catalogs.has(locale)) return catalogs.get(locale);
        const url = `${CATALOG_ROOT}/${locale}/ui.json`;
        const response = await fetch(url, { cache: 'no-cache' });
        if (!response.ok) throw new Error(`i18n catalog ${locale} unavailable (HTTP ${response.status})`);
        const catalog = await response.json();
        catalogs.set(locale, catalog);
        return catalog;
    }

    function readKey(object, key) {
        if (!object || !key) return undefined;
        return String(key).split('.').reduce((value, part) => {
            if (value === null || value === undefined || typeof value !== 'object') return undefined;
            return value[part];
        }, object);
    }

    function interpolate(value, params) {
        if (typeof value !== 'string' || !params) return value;
        return value.replace(/\{([a-zA-Z0-9_]+)\}/g, (match, key) => {
            return Object.prototype.hasOwnProperty.call(params, key) ? String(params[key]) : match;
        });
    }

    function t(key, params) {
        const active = catalogs.get(activeLocale);
        const fallback = catalogs.get(DEFAULT_LOCALE);
        const value = readKey(active, key);
        const fallbackValue = readKey(fallback, key);
        if (typeof value === 'string') return interpolate(value, params);
        if (typeof fallbackValue === 'string') return interpolate(fallbackValue, params);
        return key;
    }

    function applyElementText(root, selector, attributeName, targetAttribute) {
        root.querySelectorAll(selector).forEach((element) => {
            const key = element.getAttribute(attributeName);
            if (!key) return;
            const value = t(key);
            if (targetAttribute) element.setAttribute(targetAttribute, value);
            else element.textContent = value;
        });
    }

    function applyDocumentMeta() {
        const title = t('meta.title');
        if (title !== 'meta.title') document.title = title;

        const description = document.querySelector('meta[name="description"]');
        if (description) {
            const value = t('meta.description');
            if (value !== 'meta.description') description.setAttribute('content', value);
        }

        const ogTitle = document.querySelector('meta[property="og:title"]');
        if (ogTitle) {
            const value = t('meta.ogTitle');
            if (value !== 'meta.ogTitle') ogTitle.setAttribute('content', value);
        }

        const ogDescription = document.querySelector('meta[property="og:description"]');
        if (ogDescription) {
            const value = t('meta.ogDescription');
            if (value !== 'meta.ogDescription') ogDescription.setAttribute('content', value);
        }
    }

    function applyBrandSurface() {
        document.querySelectorAll('.brand-hero-tagline').forEach((element) => {
            element.textContent = t('brand.tagline');
        });
        document.querySelectorAll('.nav-logo').forEach((element) => {
            const label = t('brand.homeAriaLabel');
            if (label !== 'brand.homeAriaLabel') element.setAttribute('aria-label', label);
        });
    }

    function apply(root) {
        const scope = root || document;
        document.documentElement.lang = activeLocale === 'pt-BR' ? 'pt-BR' : 'en';
        document.documentElement.dataset.locale = activeLocale;

        applyElementText(scope, '[data-i18n]', 'data-i18n', null);
        applyElementText(scope, '[data-i18n-placeholder]', 'data-i18n-placeholder', 'placeholder');
        applyElementText(scope, '[data-i18n-aria-label]', 'data-i18n-aria-label', 'aria-label');
        applyElementText(scope, '[data-i18n-title]', 'data-i18n-title', 'title');

        if (scope === document) {
            applyDocumentMeta();
            applyBrandSurface();
            updateLanguageSwitcher();
        }
    }

    function persistLocale(locale) {
        try { global.localStorage.setItem(STORAGE_KEY, locale); } catch (_) { /* storage optional */ }
    }

    async function setLocale(locale, options) {
        const opts = options || {};
        const normalized = normalizeLocale(locale);
        if (!normalized || !SUPPORTED_LOCALES.includes(normalized)) {
            throw new Error(`Unsupported locale: ${locale}`);
        }

        await Promise.all([
            fetchCatalog(DEFAULT_LOCALE),
            normalized === DEFAULT_LOCALE ? Promise.resolve() : fetchCatalog(normalized),
        ]);

        const previous = activeLocale;
        activeLocale = normalized;
        if (opts.persist !== false) persistLocale(normalized);
        apply(document);

        if (previous !== normalized || opts.forceEvent) {
            document.dispatchEvent(new CustomEvent('cloudpath:localechange', {
                detail: { locale: normalized, previousLocale: previous },
            }));
        }
        return normalized;
    }

    function ensureSwitcherStyles() {
        if (document.getElementById('cloudpath-i18n-styles')) return;
        const style = document.createElement('style');
        style.id = 'cloudpath-i18n-styles';
        style.textContent = `
            .cp-language-switcher {
                display: inline-flex;
                align-items: center;
                gap: 2px;
                padding: 3px;
                margin-left: auto;
                border: 1px solid rgba(255,255,255,.14);
                border-radius: 999px;
                background: rgba(10,18,34,.48);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
            }
            .cp-language-switcher button {
                min-width: 38px;
                min-height: 30px;
                padding: 5px 9px;
                border: 0;
                border-radius: 999px;
                background: transparent;
                color: rgba(255,255,255,.68);
                font: 600 11px/1 'Montserrat', sans-serif;
                letter-spacing: .05em;
                cursor: pointer;
                transition: background .2s ease, color .2s ease, transform .2s ease;
            }
            .cp-language-switcher button:hover,
            .cp-language-switcher button:focus-visible {
                color: #fff;
                outline: none;
                background: rgba(255,255,255,.08);
            }
            .cp-language-switcher button[aria-pressed="true"] {
                color: #fff;
                background: rgba(78,205,196,.2);
                box-shadow: inset 0 0 0 1px rgba(78,205,196,.34);
            }
            @media (max-width: 720px) {
                .cp-language-switcher button { min-width: 34px; padding-inline: 7px; }
            }
        `;
        document.head.appendChild(style);
    }

    function switcherHost() {
        return document.querySelector('.navbar .nav-container')
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
        group.setAttribute('aria-label', t('language.selectorLabel'));

        const definitions = [
            ['pt-BR', 'PT'],
            ['en', 'EN'],
        ];

        definitions.forEach(([locale, shortLabel]) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.dataset.locale = locale;
            button.textContent = shortLabel;
            button.setAttribute('aria-label', t(locale === 'pt-BR' ? 'language.portuguese' : 'language.english'));
            button.addEventListener('click', () => {
                setLocale(locale).catch((error) => console.error('[i18n] locale switch failed:', error));
            });
            group.appendChild(button);
        });

        host.appendChild(group);
        updateLanguageSwitcher();
    }

    function updateLanguageSwitcher() {
        const group = document.querySelector('.cp-language-switcher');
        if (!group) return;
        group.setAttribute('aria-label', t('language.selectorLabel'));
        group.querySelectorAll('button[data-locale]').forEach((button) => {
            const locale = button.dataset.locale;
            button.setAttribute('aria-pressed', locale === activeLocale ? 'true' : 'false');
            button.setAttribute('aria-label', t(locale === 'pt-BR' ? 'language.portuguese' : 'language.english'));
        });
    }

    async function init() {
        if (readyPromise) return readyPromise;
        readyPromise = (async () => {
            const initial = resolveInitialLocale();
            await fetchCatalog(DEFAULT_LOCALE);
            if (initial !== DEFAULT_LOCALE) {
                try {
                    await fetchCatalog(initial);
                } catch (error) {
                    console.warn('[i18n] requested locale unavailable, using pt-BR:', error.message);
                }
            }
            activeLocale = catalogs.has(initial) ? initial : DEFAULT_LOCALE;
            persistLocale(activeLocale);

            const mount = () => {
                apply(document);
                createLanguageSwitcher();
                initialized = true;
                document.dispatchEvent(new CustomEvent('cloudpath:i18nready', {
                    detail: { locale: activeLocale },
                }));
            };

            if (document.readyState === 'loading') {
                await new Promise((resolve) => document.addEventListener('DOMContentLoaded', resolve, { once: true }));
            }
            mount();
            return activeLocale;
        })();
        return readyPromise;
    }

    global.I18n = {
        DEFAULT_LOCALE,
        SUPPORTED_LOCALES: SUPPORTED_LOCALES.slice(),
        normalizeLocale,
        init,
        setLocale,
        apply,
        t,
        get locale() { return activeLocale; },
        get initialized() { return initialized; },
        get ready() { return readyPromise || init(); },
    };

    init().catch((error) => {
        console.error('[i18n] initialization failed:', error);
        document.documentElement.lang = DEFAULT_LOCALE;
    });
})(window);
