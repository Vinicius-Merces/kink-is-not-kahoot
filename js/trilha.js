// Comportamento compartilhado pelas páginas da Trilha de Estudos:
// menu mobile, scroll-spy da sidebar, barra de progresso de leitura e accordions de Q&A.

document.addEventListener('DOMContentLoaded', () => {
    syncNavbarHeight();
    initMobileMenu();
    initScrollSpy();
    initReadingProgress();
    initAccordions();
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
