// KINK Landing FX
// Fundo animado "rede de dados" (canvas) + scroll-reveal das seções.
// Respeita prefers-reduced-motion e pausa quando a aba não está visível.

(function () {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function initParticleNetwork() {
        const canvas = document.getElementById('bg-canvas');
        if (!canvas || prefersReducedMotion) return;

        const ctx = canvas.getContext('2d');
        let width, height, particles, animationId;
        let isVisible = true;
        const LINK_DISTANCE = 130;
        const COLORS = ['255,107,107', '78,205,196'];

        function buildParticles() {
            const area = width * height;
            const count = Math.max(24, Math.min(70, Math.floor(area / 18000)));
            particles = Array.from({ length: count }, () => ({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                r: Math.random() * 1.6 + 0.6,
                color: COLORS[Math.floor(Math.random() * COLORS.length)]
            }));
        }

        function resize() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
            buildParticles();
        }

        function step() {
            if (!isVisible) {
                animationId = requestAnimationFrame(step);
                return;
            }

            ctx.clearRect(0, 0, width, height);

            for (const p of particles) {
                p.x += p.vx;
                p.y += p.vy;
                if (p.x <= 0 || p.x >= width) p.vx *= -1;
                if (p.y <= 0 || p.y >= height) p.vy *= -1;
            }

            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const a = particles[i];
                    const b = particles[j];
                    const dx = a.x - b.x;
                    const dy = a.y - b.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < LINK_DISTANCE) {
                        ctx.strokeStyle = `rgba(78,205,196,${0.10 * (1 - dist / LINK_DISTANCE)})`;
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(a.x, a.y);
                        ctx.lineTo(b.x, b.y);
                        ctx.stroke();
                    }
                }
            }

            for (const p of particles) {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${p.color},0.55)`;
                ctx.fill();
            }

            animationId = requestAnimationFrame(step);
        }

        resize();
        animationId = requestAnimationFrame(step);

        window.addEventListener('resize', resize);
        document.addEventListener('visibilitychange', () => {
            isVisible = document.visibilityState === 'visible';
        });
    }

    function initScrollReveal() {
        const items = document.querySelectorAll('.reveal');
        if (!items.length) return;

        if (prefersReducedMotion || !('IntersectionObserver' in window)) {
            items.forEach((el) => el.classList.add('visible'));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

        items.forEach((el) => observer.observe(el));
    }

    document.addEventListener('DOMContentLoaded', () => {
        initParticleNetwork();
        initScrollReveal();
    });
})();
