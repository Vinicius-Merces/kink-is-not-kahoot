// Comportamento compartilhado pelas páginas da Trilha de Estudos:
// menu mobile, scroll-spy da sidebar, barra de progresso de leitura,
// accordions de Q&A, conclusão de capítulos, streak/badge e busca.

document.addEventListener('DOMContentLoaded', () => {
    syncNavbarHeight();
    initMobileMenu();
    initScrollSpy();
    initReadingProgress();
    initAccordions();

    if (window.StudyProgress) {
        window.StudyProgress.recordStudyActivity();
        initChapterCompletion();
        initSidebarSearch();
    }
});

// Mede a altura real do navbar e expõe via --navbar-height, para o
// toggle "☰ Capítulos" (sticky) ficar colado abaixo dele em vez de
// sobrepor (ambos usam position: sticky; top: 0)
function syncNavbarHeight() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    const update = () => {
        document.documentElement.style.setProperty('--navbar-height', navbar.offsetHeight + 'px');
    };

    update();
    window.addEventListener('resize', update);
}

function initMobileMenu() {
    const toggle = document.querySelector('.trilha-menu-toggle');
    const sidebar = document.querySelector('.trilha-sidebar');
    const closeBtn = document.querySelector('.trilha-sidebar-close');
    if (!toggle || !sidebar) return;

    const backdrop = document.createElement('div');
    backdrop.className = 'trilha-sidebar-backdrop';
    document.body.appendChild(backdrop);

    const open = () => {
        sidebar.classList.add('open');
        backdrop.classList.add('open');
        toggle.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
        sidebar.focus();
    };

    const close = () => {
        sidebar.classList.remove('open');
        backdrop.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    };

    toggle.addEventListener('click', () => {
        sidebar.classList.contains('open') ? close() : open();
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', close);
    }

    // Fecha ao tocar fora do menu (na área escurecida)
    backdrop.addEventListener('click', close);

    // Fecha o menu ao escolher um capítulo (mobile)
    sidebar.querySelectorAll('.trilha-nav-item').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 960) close();
        });
    });

    // Fecha com ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) close();
    });

    // Fecha se a tela crescer para o layout desktop
    window.addEventListener('resize', () => {
        if (window.innerWidth > 960 && sidebar.classList.contains('open')) close();
    });
}

function initScrollSpy() {
    const sections = document.querySelectorAll('.trilha-main [id]');
    const navItems = document.querySelectorAll('.trilha-nav-item');
    if (!sections.length || !navItems.length) return;

    const navMap = new Map();
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && href.startsWith('#')) {
            navMap.set(href.slice(1), item);
        }
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const navItem = navMap.get(entry.target.id);
            if (!navItem) return;
            if (entry.isIntersecting) {
                navItems.forEach(item => {
                    item.classList.remove('active');
                    item.removeAttribute('aria-current');
                });
                navItem.classList.add('active');
                navItem.setAttribute('aria-current', 'true');
            }
        });
    }, { rootMargin: '-20% 0px -70% 0px', threshold: 0 });

    sections.forEach(section => observer.observe(section));
}

function initReadingProgress() {
    const fill = document.querySelector('.trilha-progress-fill');
    const valueLabel = document.querySelector('.trilha-progress-value');
    const main = document.querySelector('.trilha-main');
    if (!fill || !main) return;

    const update = () => {
        const docHeight = main.scrollHeight - window.innerHeight;
        const scrolled = window.scrollY;
        const pct = docHeight > 0 ? Math.min(100, Math.max(0, (scrolled / docHeight) * 100)) : 0;
        fill.style.width = pct + '%';
        if (valueLabel) valueLabel.textContent = Math.round(pct) + '%';
    };

    update();
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
}

function initAccordions() {
    document.querySelectorAll('.qa-question').forEach(btn => {
        btn.setAttribute('aria-expanded', 'false');
        btn.addEventListener('click', () => {
            const item = btn.closest('.qa-item');
            if (!item) return;
            const isOpen = item.classList.toggle('open');
            btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
    });
}

// ── Conclusão de capítulos: checkbox na sidebar + resumo (badge/streak) ─────
function initChapterCompletion() {
    const sidebar = document.querySelector('.trilha-sidebar');
    const trilhaId = sidebar && sidebar.dataset.trilhaId;
    if (!trilhaId) return;

    const chapterLinks = Array.from(document.querySelectorAll('.trilha-nav-item[href^="#cap"]'));
    if (!chapterLinks.length) return;

    const totalChapters = chapterLinks.length;

    function renderSummary() {
        const completed = window.StudyProgress.getCompletedSet(trilhaId);
        const percent = totalChapters ? Math.round((completed.size / totalChapters) * 100) : 0;
        const badge = window.StudyProgress.getBadge(percent);
        const streak = window.StudyProgress.getStreak();

        let summary = document.querySelector('.trilha-completion-summary');
        if (!summary) {
            summary = document.createElement('div');
            summary.className = 'trilha-completion-summary';
            const progressEl = document.querySelector('.trilha-progress');
            if (progressEl) {
                progressEl.insertAdjacentElement('afterend', summary);
            } else {
                sidebar.querySelector('.trilha-sidebar-header').insertAdjacentElement('afterend', summary);
            }
        }

        summary.innerHTML = `
            <div class="trilha-completion-badge">
                <span class="badge-emoji">${badge.emoji}</span>
                <span>${badge.label}</span>
            </div>
            <div>
                <div class="trilha-completion-count">${completed.size}/${totalChapters} capítulos</div>
                <div class="trilha-streak ${streak.current > 0 ? 'active' : ''}" title="Dias seguidos estudando">
                    🔥 ${streak.current} ${streak.current === 1 ? 'dia' : 'dias'}
                </div>
            </div>
        `;

        chapterLinks.forEach(link => {
            const capId = link.getAttribute('href').slice(1);
            link.classList.toggle('chapter-done', completed.has(capId));
            const check = link.querySelector('.chapter-check');
            if (check) check.classList.toggle('done', completed.has(capId));
        });
    }

    chapterLinks.forEach(link => {
        const capId = link.getAttribute('href').slice(1);
        const check = document.createElement('button');
        check.type = 'button';
        check.className = 'chapter-check';
        check.setAttribute('aria-label', 'Marcar capítulo como concluído');
        check.textContent = '✓';
        check.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            window.StudyProgress.toggleChapter(trilhaId, capId);
            renderSummary();
        });
        link.appendChild(check);
    });

    renderSummary();
}

// ── Busca dentro da apostila (sobre os títulos de seção) ────────────────────
function initSidebarSearch() {
    const sidebar = document.querySelector('.trilha-sidebar');
    if (!sidebar) return;

    const index = Array.from(document.querySelectorAll('.trilha-chapter')).flatMap(chapter => {
        const capLabel = chapter.querySelector('.trilha-chapter-num');
        const chapterTitle = chapter.querySelector('.trilha-chapter-header h2');
        const headings = Array.from(chapter.querySelectorAll('h2, h3'));
        return headings.map(h => ({
            text: h.textContent.trim(),
            chapterLabel: capLabel ? capLabel.textContent.trim() : '',
            chapterTitle: chapterTitle ? chapterTitle.textContent.trim() : '',
            id: chapter.id,
            targetEl: h,
        }));
    });

    if (!index.length) return;

    const wrap = document.createElement('div');
    wrap.className = 'trilha-search-wrap';
    wrap.innerHTML = `
        <input type="search" class="trilha-search-input" placeholder="🔎 Buscar na apostila..." aria-label="Buscar na apostila">
        <div class="trilha-search-results"></div>
    `;
    const header = sidebar.querySelector('.trilha-sidebar-header');
    if (header) header.insertAdjacentElement('afterend', wrap);

    const input = wrap.querySelector('.trilha-search-input');
    const results = wrap.querySelector('.trilha-search-results');

    function closeResults() {
        results.classList.remove('open');
        results.innerHTML = '';
    }

    input.addEventListener('input', () => {
        const term = input.value.trim().toLowerCase();
        if (term.length < 2) {
            closeResults();
            return;
        }

        const matches = index.filter(item => item.text.toLowerCase().includes(term)).slice(0, 12);
        if (!matches.length) {
            results.innerHTML = '<div class="trilha-search-empty">Nenhum resultado.</div>';
            results.classList.add('open');
            return;
        }

        results.innerHTML = matches.map((item, i) => `
            <button type="button" class="trilha-search-result-item" data-index="${i}">
                <span class="result-chapter">${item.chapterLabel} · ${item.chapterTitle}</span>
                ${item.text}
            </button>
        `).join('');
        results.classList.add('open');

        results.querySelectorAll('.trilha-search-result-item').forEach((btn, i) => {
            btn.addEventListener('click', () => {
                matches[i].targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                history.replaceState(null, '', `#${matches[i].id}`);
                closeResults();
                input.value = '';
                if (window.innerWidth <= 960) {
                    document.querySelector('.trilha-sidebar')?.classList.remove('open');
                    document.querySelector('.trilha-sidebar-backdrop')?.classList.remove('open');
                }
            });
        });
    });

    document.addEventListener('click', (e) => {
        if (!wrap.contains(e.target)) closeResults();
    });
}
