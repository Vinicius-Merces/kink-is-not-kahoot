/**
 * Branding — fonte unica da identidade do produto.
 *
 * O site esta em transicao de KINK -> CloudPath. Em vez de espalhar o nome
 * novo por 20 arquivos, tudo que e VISIVEL ao usuario passa por aqui.
 *
 * Na data de virada (CUTOVER), a marca troca sozinha: navbar, titulo da aba,
 * logo e tagline. Nao precisa de deploy no dia -- mas se quiser antecipar ou
 * adiar, basta mudar a constante CUTOVER abaixo.
 *
 * ATENCAO -- chaves de localStorage:
 * O progresso das trilhas vive em `kink_study_progress_v1`. Renomear a chave
 * apagaria o progresso de todo mundo. Por isso a migracao e feita por copia,
 * com fallback: le a chave nova, e se nao existir, herda a antiga.
 */
(function (global) {
    'use strict';

    // Virada da marca: 17/07/2026, 00h00 (horario de Brasilia).
    const CUTOVER = new Date('2026-07-17T00:00:00-03:00');

    const LEGACY = {
        name: 'KINK',
        tagline: 'is not Kahoot',
        fullName: 'KINK is not Kahoot',
    };

    const NEXT = {
        name: 'CloudPath',
        tagline: 'Sua trilha para a nuvem',
        fullName: 'CloudPath',
        domain: 'cloudpath.squareweb.app',
        url: 'https://cloudpath.squareweb.app',
        logo: 'images/branding/cloudpath-logo.png',
        logoSm: 'images/branding/cloudpath-logo-sm.png',
        icon: 'images/branding/cloudpath-icon.png',
    };

    const CREATOR = {
        name: 'Orbital Studio',
        url: 'https://orbitalstudio.com.br',
    };

    // Preview: abrir qualquer página com ?brand=cloudpath mostra a marca nova
    // sem precisar mexer na data. ?brand=kink força a antiga.
    function _override() {
        try {
            const p = new URLSearchParams(location.search).get('brand');
            if (p === 'cloudpath') return true;
            if (p === 'kink') return false;
        } catch (_) { /* ignora */ }
        return null;
    }

    const isLive = () => {
        const o = _override();
        if (o !== null) return o;
        return Date.now() >= CUTOVER.getTime();
    };

    /** Dias restantes ate a virada (0 se ja virou). */
    function daysUntilCutover() {
        const ms = CUTOVER.getTime() - Date.now();
        return ms <= 0 ? 0 : Math.ceil(ms / 86400000);
    }

    /** Data da virada formatada (17/07). */
    function cutoverLabel() {
        const d = String(CUTOVER.getDate()).padStart(2, '0');
        const m = String(CUTOVER.getMonth() + 1).padStart(2, '0');
        return `${d}/${m}`;
    }

    // -----------------------------------------------------------------------
    // Migracao de localStorage: copia kink_* -> cloudpath_*, preservando dados.
    // Idempotente. Mantem a chave antiga (rollback seguro).
    // -----------------------------------------------------------------------
    function migrateStorage() {
        try {
            for (let i = 0; i < localStorage.length; i++) {
                const oldKey = localStorage.key(i);
                if (!oldKey || !oldKey.startsWith('kink_')) continue;
                const newKey = oldKey.replace(/^kink_/, 'cloudpath_');
                if (localStorage.getItem(newKey) === null) {
                    localStorage.setItem(newKey, localStorage.getItem(oldKey));
                }
            }
        } catch (_) { /* storage indisponivel: segue sem migrar */ }
    }

    /**
     * Leitura com fallback: tenta a chave nova, herda a antiga se preciso.
     * Use isto no lugar de localStorage.getItem para qualquer chave de marca.
     */
    function storageGet(key) {
        try {
            const novo = localStorage.getItem(`cloudpath_${key}`);
            if (novo !== null) return novo;
            return localStorage.getItem(`kink_${key}`);
        } catch (_) { return null; }
    }

    function storageSet(key, value) {
        try {
            localStorage.setItem(`cloudpath_${key}`, value);
            localStorage.setItem(`kink_${key}`, value);  // mantem compat ate a virada
        } catch (_) { /* ignora */ }
    }

    // -----------------------------------------------------------------------
    // Aplica a marca ativa na pagina (roda sozinho apos o cutover)
    // -----------------------------------------------------------------------
    function apply() {
        if (!isLive()) return;   // antes da virada, nada muda

        const brand = NEXT;

        // Titulo da aba: "Trilha SAA-C03 - KINK is not Kahoot" -> "... - CloudPath"
        if (document.title) {
            document.title = document.title
                .replace(/KINK is not Kahoot/g, brand.fullName)
                .replace(/KINK/g, brand.name);
        }

        // Marca da navbar (.nav-logo) e da tela do aluno (.player-logo):
        // insere o LOGO como imagem. O texto continua no DOM (oculto via CSS),
        // servindo de fallback se a imagem falhar e de conteudo para leitores
        // de tela nao dependerem do alt sozinho.
        document.querySelectorAll('.nav-logo, .player-logo').forEach(el => {
            const h = el.querySelector('h1, h2');
            const sub = el.querySelector('span, p');
            if (h) h.textContent = brand.name;
            if (sub) sub.textContent = brand.tagline;

            if (!el.querySelector('.brand-logo-img')) {
                const img = document.createElement('img');
                img.className = 'brand-logo-img';
                img.src = brand.logo;                       // o PNG original
                img.srcset = `${brand.logoSm} 900w, ${brand.logo} 4000w`;
                img.sizes = '(max-width: 720px) 160px, 190px';
                img.alt = brand.name;
                img.decoding = 'async';
                el.prepend(img);
            }
        });

        // Hero da landing: logo grande no lugar do texto glitch
        const heroLogo = document.querySelector('.hero-section .logo');
        if (heroLogo && !heroLogo.querySelector('.brand-hero-logo')) {
            const img = document.createElement('img');
            img.className = 'brand-hero-logo';
            img.src = brand.logo;                           // o PNG original
            img.srcset = `${brand.logoSm} 900w, ${brand.logo} 4000w`;
            img.sizes = '(max-width: 720px) 90vw, 480px';
            img.alt = brand.name;
            img.width = 480;                                // evita salto de layout
            img.height = 110;
            heroLogo.prepend(img);

            const tag = document.createElement('p');
            tag.className = 'brand-hero-tagline';
            tag.textContent = brand.tagline;
            img.after(tag);
        }

        // Hero da landing (a estrutura real e .hero-section > .logo)
        const heroTitle = document.querySelector('.hero-section .glitch');
        if (heroTitle) {
            heroTitle.textContent = brand.name;
            heroTitle.setAttribute('data-text', brand.name);
        }
        const heroTagline = document.querySelector('.hero-section .tagline');
        if (heroTagline) heroTagline.textContent = brand.tagline;

        // Rodape da landing: preserva a assinatura do produto e referencia
        // explicitamente a Orbital Studio como criadora do CloudPath.
        const badge = document.querySelector('.rebellion-badge p');
        if (badge) {
            badge.textContent = `☁️ ${brand.name} — ${brand.tagline} · criado pela `;

            const creatorLink = document.createElement('a');
            creatorLink.href = CREATOR.url;
            creatorLink.target = '_blank';
            creatorLink.rel = 'noopener noreferrer';
            creatorLink.textContent = CREATOR.name;
            creatorLink.setAttribute('aria-label', `${CREATOR.name}, criadora do ${brand.name}`);
            creatorLink.style.color = 'inherit';
            creatorLink.style.textDecoration = 'none';
            creatorLink.style.borderBottom = '1px solid currentColor';

            badge.appendChild(creatorLink);
        }

        // Titulo do app no iOS
        const appTitle = document.querySelector('meta[name="apple-mobile-web-app-title"]');
        if (appTitle) appTitle.setAttribute('content', brand.name);

        // Favicons e icone do PWA
        document.querySelectorAll('link[rel="icon"]').forEach(link => {
            const size = link.getAttribute('sizes') === '16x16' ? 16 : 32;
            link.setAttribute('href', `images/branding/cloudpath-icon-${size}.png`);
        });
        const apple = document.querySelector('link[rel="apple-touch-icon"]');
        if (apple) apple.setAttribute('href', 'images/branding/cloudpath-icon-180.png');

        // Manifest do PWA (nome e icones novos)
        const manifest = document.querySelector('link[rel="manifest"]');
        if (manifest) manifest.setAttribute('href', 'manifest-cloudpath.json');

        // Player de música minimizado: troca o emoji pelo ícone do CloudPath.
        // O player renderiza depois, então observamos até o elemento existir.
        const marcarIcone = () => {
            const ic = document.getElementById('minimizedIcon');
            if (ic) { ic.classList.add('brand-icon'); return true; }
            return false;
        };
        if (!marcarIcone()) {
            const obs = new MutationObserver(() => { if (marcarIcone()) obs.disconnect(); });
            obs.observe(document.body, { childList: true, subtree: true });
            setTimeout(() => obs.disconnect(), 10000);
        }

        document.documentElement.classList.add('brand-cloudpath');
    }

    global.Brand = {
        LEGACY, NEXT, CUTOVER, CREATOR,
        isLive, daysUntilCutover, cutoverLabel,
        migrateStorage, storageGet, storageSet, apply,
        /** Marca ativa neste momento. */
        get current() { return isLive() ? NEXT : LEGACY; },
    };

    migrateStorage();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', apply);
    } else {
        apply();
    }
})(window);

/**
 * Card de aviso do rebrand na landing page.
 * - Some sozinho apos a virada (nao vira lixo no site).
 * - Dispensavel; a escolha e lembrada, mas o aviso volta faltando 1 dia.
 */
(function (global) {
    'use strict';

    const DISMISS_KEY = 'rebrand_notice_dismissed_v1';

    function initRebrandNotice() {
        const card = document.getElementById('rebrandNotice');
        if (!card || !global.Brand) return;

        const B = global.Brand;

        // Ja virou: o aviso nao faz mais sentido.
        if (B.isLive()) { card.remove(); return; }

        const dias = B.daysUntilCutover();

        // Respeita o "dispensar" -- mas na reta final (<=1 dia) o aviso volta,
        // porque perder o endereco novo custa mais que a irritacao do card.
        if (B.storageGet(DISMISS_KEY) === '1' && dias > 1) { card.remove(); return; }

        const dateEl = document.getElementById('rebrandDate');
        if (dateEl) dateEl.textContent = B.cutoverLabel();

        const daysEl = document.getElementById('rebrandDays');
        const cdEl = document.getElementById('rebrandCountdown');
        if (daysEl) {
            if (dias === 0) {
                daysEl.textContent = 'hoje';
                daysEl.style.fontSize = '1.2rem';
            } else {
                daysEl.textContent = dias;
                const label = cdEl && cdEl.querySelector('.rebrand-countdown-label');
                if (label) label.textContent = dias === 1 ? 'dia' : 'dias';
            }
        }

        const btn = document.getElementById('rebrandDismiss');
        if (btn) {
            btn.addEventListener('click', () => {
                B.storageSet(DISMISS_KEY, '1');
                card.style.transition = 'opacity .25s ease, transform .25s ease';
                card.style.opacity = '0';
                card.style.transform = 'translateY(-8px)';
                setTimeout(() => card.remove(), 250);
            });
        }

        card.hidden = false;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initRebrandNotice);
    } else {
        initRebrandNotice();
    }
})(window);
