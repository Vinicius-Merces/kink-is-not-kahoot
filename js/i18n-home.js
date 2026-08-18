/** CloudPath home-page locale adapter. */
(function (global) {
    'use strict';
    if (!global.I18n) return;

    const q = (selector, root = document) => root.querySelector(selector);
    const qa = (selector, root = document) => Array.from(root.querySelectorAll(selector));

    function bindText(selector, key) {
        const element = q(selector);
        if (element) element.setAttribute('data-i18n', key);
    }

    function bindAllText(selector, keys) {
        qa(selector).forEach((element, index) => {
            if (keys[index]) element.setAttribute('data-i18n', keys[index]);
        });
    }

    function bindAttribute(selector, attribute, key) {
        const element = q(selector);
        if (element) element.setAttribute(`data-i18n-${attribute}`, key);
    }

    function ensureCopySpan(element, key, position = 'after') {
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

    function bindIconRows(selector, keys) {
        qa(selector).forEach((element, index) => {
            if (keys[index]) ensureCopySpan(element, keys[index]);
        });
    }

    function bindCombatant(selector, key) {
        const element = q(selector);
        if (!element) return;
        const hp = element.querySelector('.hp');
        let copy = element.querySelector(':scope > .cp-i18n-copy');
        if (!copy) {
            copy = document.createElement('span');
            copy.className = 'cp-i18n-copy';
            Array.from(element.childNodes)
                .filter(node => node.nodeType === Node.TEXT_NODE && node.textContent.trim())
                .forEach(node => node.remove());
            element.insertBefore(copy, hp || element.firstChild);
            if (hp) copy.after(document.createTextNode(' '));
        }
        copy.setAttribute('data-i18n', key);
    }

    function localizeFooter() {
        const footer = q('.rebellion-badge p');
        if (!footer) return;
        const creator = footer.querySelector('a[href*="orbitalstudio.com.br"]');
        if (!creator) {
            footer.setAttribute('data-i18n', 'home.footer');
            return;
        }

        footer.removeAttribute('data-i18n');
        Array.from(footer.childNodes)
            .filter(node => node.nodeType === Node.TEXT_NODE)
            .forEach(node => node.remove());
        ensureCopySpan(footer, 'home.footerCreatorPrefix', 'before');
        creator.setAttribute('aria-label', global.I18n.t('home.creatorAria'));
    }

    function annotateHome() {
        if (!q('.hero-section')) return;

        bindText('.skip-link', 'home.skipLink');
        bindText('#loading-overlay .cp-loading-inner > p', 'home.loading');
        bindText('#navLoginBtn', 'auth.navLogin');
        bindText('#logoutBtn', 'common.logout');

        bindText('.hero-section h1.sr-only', 'home.heroSrTitle');
        bindText('.brand-hero-tagline', 'home.heroTagline');
        bindAttribute('.hero-terminal', 'aria-label', 'home.heroTerminalAria');

        const badges = qa('.hero-badges .hero-badge');
        if (badges[0]) ensureCopySpan(badges[0], 'common.online');
        if (badges[1]) badges[1].setAttribute('data-i18n', 'home.statusRegion');
        if (badges[2]) badges[2].setAttribute('data-i18n', 'home.statusExams');
        if (badges[3]) badges[3].setAttribute('data-i18n', 'home.statusRanking');

        bindAttribute('#awsGlobe', 'aria-label', 'home.globeAria');
        bindIconRows('.hero-globe-legend .chave', ['home.globeRegions', 'home.globePrimaryRegion']);

        bindText('.host-card h2', 'home.teacherTitle');
        bindText('.host-card > p', 'home.teacherDescription');
        bindIconRows('.host-card .card-feature-list li', [
            'home.teacherFeatures.unlimitedQuestions',
            'home.teacherFeatures.liveResults',
            'home.teacherFeatures.roomControl'
        ]);
        bindText('#hostBtn', 'home.createQuiz');
        bindText('#loginBtn', 'auth.googleWithIcon');

        bindText('.player-card h2', 'home.studentTitle');
        bindText('.player-card > p', 'home.studentDescription');
        bindIconRows('.player-card .card-feature-list li', [
            'home.studentFeatures.roomCode',
            'home.studentFeatures.realtime',
            'home.studentFeatures.ranking'
        ]);
        bindAttribute('#roomCode', 'placeholder', 'quiz.roomCode');
        bindAttribute('#roomCode', 'aria-label', 'quiz.roomCodeAria');
        bindText('#joinBtn', 'quiz.join');

        bindText('#metricasTitulo', 'home.metrics.title');
        bindAllText('.metricas .metrica-rotulo', [
            'home.metrics.certifications',
            'home.metrics.questions',
            'home.metrics.narratedChapters',
            'home.metrics.explainedTraps'
        ]);

        const banners = qa('.simulado-banner');
        if (banners[0]) {
            const title = q('h2', banners[0]);
            const description = q('p', banners[0]);
            if (title) title.setAttribute('data-i18n', 'home.examBanner.title');
            if (description) description.setAttribute('data-i18n', 'home.examBanner.description');
        }
        bindText('#simuladosBtn', 'home.practiceNowWithIcon');
        if (banners[1]) {
            const title = q('h2', banners[1]);
            const description = q('p', banners[1]);
            if (title) title.setAttribute('data-i18n', 'home.studyBanner.title');
            if (description) description.setAttribute('data-i18n', 'home.studyBanner.description');
        }
        bindText('#trilhaBtn', 'home.viewGuidesWithIcon');

        bindText('.arena-eyebrow', 'home.studyMode');
        bindText('.arena-lead', 'home.arenaLead');
        bindAllText('.arena-pontos li', [
            'home.arenaPoints.certifications',
            'home.arenaPoints.explanations',
            'home.arenaPoints.sync'
        ]);
        bindText('.arena-texto > a', 'home.enterArena');
        bindCombatant('.arena-combatentes > div:first-child .combatente-nome', 'home.arenaDemo.you');
        bindCombatant('.arena-combatentes > div:last-child .combatente-nome', 'home.arenaDemo.guardian');
        bindText('.arena-pergunta', 'home.arenaDemo.question');
        bindIconRows('.arena-alternativas .arena-alt', [
            'home.arenaDemo.optionA',
            'home.arenaDemo.optionB',
            'home.arenaDemo.optionC',
            'home.arenaDemo.optionD'
        ]);
        bindText('.arena-rodape-demo', 'home.arenaDemo.hit');

        bindAllText('.features .feature h3', [
            'home.features.realtime.title',
            'home.features.competitive.title',
            'home.features.unlimited.title'
        ]);
        bindAllText('.features .feature p', [
            'home.features.realtime.description',
            'home.features.competitive.description',
            'home.features.unlimited.description'
        ]);

        bindText('#aboutTitle', 'home.about.title');
        bindText('.about-role', 'home.about.role');
        bindAllText('.about-text > p', [
            'home.about.paragraph1',
            'home.about.paragraph2',
            'home.about.paragraph3',
            'home.about.paragraph4',
            'home.about.paragraph5'
        ]);
        bindIconRows('.about-focus-list li', [
            'home.about.focus.cloud',
            'home.about.focus.data',
            'home.about.focus.linux',
            'home.about.focus.development'
        ]);
        bindText('.about-badges-title', 'home.about.badgesTitle');
        const badgeImages = qa('.about-badges img');
        if (badgeImages[0]) badgeImages[0].setAttribute('alt', global.I18n.t('home.about.restartBadgeAlt'));
        if (badgeImages[1]) badgeImages[1].setAttribute('alt', global.I18n.t('home.about.practitionerBadgeAlt'));

        localizeFooter();

        bindAttribute('#loginModal .close', 'aria-label', 'common.close');
        bindText('#loginModalTitle', 'auth.modalTitle');
        bindText('#loginModal .modal-content > p', 'auth.modalDescription');
        bindText('#googleLoginBtn', 'auth.googleWithIcon');
    }

    function localizeFirebaseFallback() {
        const inner = q('#loading-overlay .cp-loading-inner');
        if (!inner) return;
        const paragraphs = qa(':scope > p', inner);
        const reload = q('button', inner);
        if (paragraphs.length >= 2 && reload) {
            paragraphs[0].setAttribute('data-i18n', 'errors.firebaseWithIcon');
            paragraphs[1].setAttribute('data-i18n', 'errors.firebaseReloadHint');
            reload.setAttribute('data-i18n', 'common.reload');
            global.I18n.apply(inner);
        }
    }

    function installLoadingObserver() {
        const overlay = q('#loading-overlay');
        if (!overlay || overlay.dataset.i18nObserved === 'true') return;
        overlay.dataset.i18nObserved = 'true';
        new MutationObserver(localizeFirebaseFallback).observe(overlay, { childList: true, subtree: true });
    }

    function installModalAccessibility() {
        const modal = q('#loginModal');
        if (!modal || modal.dataset.a11yEnhanced === 'true') return;
        modal.dataset.a11yEnhanced = 'true';
        let trigger = null;

        document.addEventListener('click', (event) => {
            const candidate = event.target.closest('#navLoginBtn, #loginBtn, #hostBtn, #simuladosBtn');
            if (candidate) trigger = candidate;
        }, true);

        const visible = () => getComputedStyle(modal).display !== 'none';
        const focusables = () => qa(
            'button:not([disabled]), a[href], input:not([disabled]), [tabindex]:not([tabindex="-1"])', modal
        ).filter(el => el.offsetParent !== null);

        document.addEventListener('keydown', (event) => {
            if (!visible()) return;
            if (event.key === 'Escape') {
                event.preventDefault();
                modal.style.display = 'none';
                if (trigger && document.contains(trigger)) trigger.focus();
                return;
            }
            if (event.key !== 'Tab') return;
            const items = focusables();
            if (!items.length) return;
            const first = items[0];
            const last = items[items.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        });

        new MutationObserver(() => {
            if (visible()) {
                const first = focusables()[0];
                if (first && !modal.contains(document.activeElement)) first.focus();
            }
        }).observe(modal, { attributes: true, attributeFilter: ['style', 'class'] });
    }

    global.I18n.registerAdapter(() => {
        annotateHome();
        installLoadingObserver();
        installModalAccessibility();
    });
})(window);
