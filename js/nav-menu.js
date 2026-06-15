// Menu sanduíche (mobile): abre/fecha o .nav-menu e cuida da acessibilidade básica
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('navToggle');
    const menu = document.getElementById('navMenu');
    if (!toggle || !menu) return;

    const openMenu = () => {
        toggle.setAttribute('aria-expanded', 'true');
        menu.classList.add('open');
    };

    const closeMenu = () => {
        toggle.setAttribute('aria-expanded', 'false');
        menu.classList.remove('open');
    };

    toggle.addEventListener('click', () => {
        const isOpen = toggle.getAttribute('aria-expanded') === 'true';
        if (isOpen) closeMenu(); else openMenu();
    });

    menu.querySelectorAll('a, button').forEach((el) => {
        el.addEventListener('click', closeMenu);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') closeMenu();
    });

    document.addEventListener('click', (event) => {
        if (toggle.getAttribute('aria-expanded') !== 'true') return;
        if (!menu.contains(event.target) && !toggle.contains(event.target)) {
            closeMenu();
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) closeMenu();
    });
});
