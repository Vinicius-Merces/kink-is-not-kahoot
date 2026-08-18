// Navegação CloudPath — grupos com dropdown (desktop) e gaveta (mobile).
//
// Acessibilidade:
//  - Botões de grupo usam aria-expanded/aria-controls (padrão disclosure)
//  - Esc fecha dropdown aberto e a gaveta; clique fora também
//  - No mobile, os grupos ficam sempre abertos (viram seções da gaveta)
//  - A página atual marca o item (aria-current) e o grupo (.current)
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('navToggle');
    const menu = document.getElementById('navMenu');
    if (!menu) return;

    const groups = Array.from(menu.querySelectorAll('.nav-group'));
    const isMobile = () => window.matchMedia('(max-width: 900px)').matches;

    // ── Scrim (fundo escurecido atrás da gaveta no mobile) ──
    let scrim = document.querySelector('.nav-scrim');
    if (!scrim) {
        scrim = document.createElement('div');
        scrim.className = 'nav-scrim';
        scrim.setAttribute('aria-hidden', 'true');
        document.body.appendChild(scrim);
    }

    // ── Marca a página atual (item + grupo) ──
    const here = location.pathname.split('/').pop() || 'index.html';
    groups.forEach((group) => {
        const current = group.querySelector(`.nav-item[href="${here}"]`);
        if (current) {
            current.setAttribute('aria-current', 'page');
            group.classList.add('current');
        }
    });

    // ── Dropdowns (desktop) ──
    const closeGroup = (group) => {
        group.classList.remove('open');
        const btn = group.querySelector('.nav-group-btn');
        if (btn && !isMobile()) btn.setAttribute('aria-expanded', 'false');
    };
    const closeAllGroups = (except) => {
        groups.forEach((g) => { if (g !== except) closeGroup(g); });
    };

    groups.forEach((group) => {
        const btn = group.querySelector('.nav-group-btn');
        if (!btn) return;

        btn.addEventListener('click', () => {
            if (isMobile()) return; // na gaveta o grupo é uma seção fixa
            const willOpen = !group.classList.contains('open');
            closeAllGroups(group);
            group.classList.toggle('open', willOpen);
            btn.setAttribute('aria-expanded', String(willOpen));
        });
    });

    // ── Gaveta (mobile) ──
    const openDrawer = () => {
        if (toggle) toggle.setAttribute('aria-expanded', 'true');
        menu.classList.add('open');
        scrim.classList.add('show');
        document.body.style.overflow = 'hidden';
    };
    const closeDrawer = () => {
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
        menu.classList.remove('open');
        scrim.classList.remove('show');
        document.body.style.overflow = '';
    };

    if (toggle) {
        toggle.addEventListener('click', () => {
            const open = toggle.getAttribute('aria-expanded') === 'true';
            if (open) closeDrawer(); else openDrawer();
        });
    }
    scrim.addEventListener('click', closeDrawer);

    // Navegar por um link fecha tudo
    menu.querySelectorAll('a, button.btn-logout').forEach((el) => {
        el.addEventListener('click', () => { closeDrawer(); closeAllGroups(); });
    });

    // Esc: fecha dropdown aberto (e devolve o foco ao botão) ou a gaveta
    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;
        const open = groups.find((g) => g.classList.contains('open'));
        if (open) {
            closeGroup(open);
            const btn = open.querySelector('.nav-group-btn');
            if (btn) btn.focus();
            return;
        }
        closeDrawer();
    });

    // Clique fora fecha dropdowns
    document.addEventListener('click', (event) => {
        if (!menu.contains(event.target) && (!toggle || !toggle.contains(event.target))) {
            closeAllGroups();
        }
    });

    // ── Estado dos aria-expanded por viewport ──
    // Na gaveta os grupos ficam sempre visíveis; para o leitor de tela não
    // anunciar "recolhido" num conteúdo aberto, o estado acompanha o layout.
    const syncViewportState = () => {
        const mobile = isMobile();
        groups.forEach((group) => {
            const btn = group.querySelector('.nav-group-btn');
            if (!btn) return;
            if (mobile) {
                btn.setAttribute('aria-expanded', 'true');
                btn.setAttribute('tabindex', '-1');
                group.classList.remove('open');
            } else {
                btn.setAttribute('aria-expanded', group.classList.contains('open') ? 'true' : 'false');
                btn.removeAttribute('tabindex');
            }
        });
        if (!mobile) closeDrawer();
    };
    syncViewportState();
    window.addEventListener('resize', syncViewportState);
});

/**
 * Internationalization bootstrap for internal pages.
 *
 * The landing already bootstraps i18n through branding.js. Internal pages all
 * share nav-menu.js, making this the stable second entry point without adding
 * one script tag to every HTML page. The guards also make it safe on pages that
 * happen to load both entry points.
 */
(function bootstrapInternalI18n(global) {
    'use strict';
    if (global.I18n || document.querySelector('script[data-cloudpath-i18n]')) return;

    const script = document.createElement('script');
    script.src = new URL('js/i18n.js', document.baseURI).href;
    script.dataset.cloudpathI18n = 'true';
    script.async = true;
    script.onerror = () => console.warn('[i18n] runtime unavailable; keeping pt-BR content');
    document.head.appendChild(script);
})(window);
