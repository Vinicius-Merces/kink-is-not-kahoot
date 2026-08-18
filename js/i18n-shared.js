/** Shared CloudPath locale bindings used across internal pages. */
(function (global) {
    'use strict';
    if (!global.I18n) return;

    const q = (selector, root = document) => root.querySelector(selector);
    const qa = (selector, root = document) => Array.from(root.querySelectorAll(selector));

    function ensureCopySpan(element, key, position = 'before') {
        if (!element) return;
        let copy = element.querySelector(':scope > .cp-i18n-copy');
        if (!copy) {
            copy = document.createElement('span');
            copy.className = 'cp-i18n-copy';
            Array.from(element.childNodes)
                .filter(node => node.nodeType === Node.TEXT_NODE && node.textContent.trim())
                .forEach(node => node.remove());
            if (position === 'before') element.prepend(copy);
            else element.append(copy);
        }
        copy.setAttribute('data-i18n', key);
    }

    function bindText(selector, key) {
        const element = q(selector);
        if (element) element.setAttribute('data-i18n', key);
    }

    function bindNavItem(href, labelKey, hintKey) {
        const item = q(`.nav-item[href="${href}"]`);
        if (!item) return;
        const label = q('.nav-item-label', item);
        const hint = q('.nav-item-hint', item);
        if (label) label.setAttribute('data-i18n', labelKey);
        if (hint) hint.setAttribute('data-i18n', hintKey);
    }

    function updateToggleLabel() {
        const toggle = q('#navToggle');
        if (!toggle) return;
        const key = toggle.getAttribute('aria-expanded') === 'true' ? 'nav.closeMenu' : 'nav.openMenu';
        toggle.setAttribute('aria-label', global.I18n.t(key));
    }

    function installToggleObserver() {
        const toggle = q('#navToggle');
        if (!toggle || toggle.dataset.i18nObserved === 'true') return;
        toggle.dataset.i18nObserved = 'true';
        new MutationObserver(updateToggleLabel).observe(toggle, {
            attributes: true,
            attributeFilter: ['aria-expanded']
        });
    }

    function annotateSharedNavigation() {
        const nav = q('.navbar');
        if (!nav) return;

        nav.setAttribute('aria-label', global.I18n.t('nav.mainAria'));
        bindText('.skip-link', 'home.skipLink');
        updateToggleLabel();
        installToggleObserver();

        const groupButtons = qa('.nav-group-btn');
        const groupKeys = ['nav.groups.study', 'nav.groups.quizzes', 'nav.groups.performance'];
        groupButtons.forEach((button, index) => {
            if (groupKeys[index]) ensureCopySpan(button, groupKeys[index], 'before');
        });

        bindNavItem('simulados.html', 'nav.items.exams.label', 'nav.items.exams.hint');
        bindNavItem('trilha.html', 'nav.items.study.label', 'nav.items.study.hint');
        bindNavItem('cloudarena.html', 'nav.items.arena.label', 'nav.items.arena.hint');
        bindNavItem('my-quizzes.html', 'nav.items.myQuizzes.label', 'nav.items.myQuizzes.hint');
        bindNavItem('create-quiz.html', 'nav.items.createQuiz.label', 'nav.items.createQuiz.hint');
        bindNavItem('progresso.html', 'nav.items.progress.label', 'nav.items.progress.hint');
        bindNavItem('historico.html', 'nav.items.history.label', 'nav.items.history.hint');

        bindText('.nav-menu #logoutBtn, .nav-menu .btn-logout', 'common.logout');
    }

    function loadPageAdapter() {
        let leaf = '';
        try { leaf = location.pathname.split('/').filter(Boolean).pop() || 'index.html'; } catch (_) {}
        if (leaf !== 'simulados.html') return;
        if (document.querySelector('script[data-cloudpath-i18n-page="simulados"]')) return;

        const script = document.createElement('script');
        script.src = new URL('js/i18n-simulados.js', document.baseURI).href;
        script.dataset.cloudpathI18nPage = 'simulados';
        script.async = true;
        script.onerror = () => console.warn('[i18n] simulator adapter unavailable');
        document.head.appendChild(script);
    }

    global.I18n.registerAdapter(() => {
        annotateSharedNavigation();
    });

    loadPageAdapter();
})(window);
