/**
 * Polimento de animação da landing (CloudPath)
 *
 *  1. Contadores das métricas — sobem até o número final quando a seção
 *     entra na tela. Os alvos vêm do próprio HTML (data-alvo), então o
 *     número exibido antes do JS já é o correto: sem JS, sem animação,
 *     mas o dado continua certo.
 *  2. Terminal do hero — digita o comando em vez de aparecer pronto.
 *
 * Ambos respeitam prefers-reduced-motion.
 */
(function () {
    const semMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ── 1. Contadores ──────────────────────────────────────────────────
    function formatar(n) {
        return n.toLocaleString('pt-BR');
    }

    function animarNumero(el, alvo, duracao) {
        let terminou = false;
        const finalizar = () => {
            if (terminou) return;
            terminou = true;
            el.textContent = formatar(alvo);
        };

        const t0 = performance.now();
        function passo(agora) {
            if (terminou) return;
            const p = Math.min(1, (agora - t0) / duracao);
            // easeOutExpo: acelera e desacelera no fim — a chegada no número
            // final é o momento que o olho espera
            const e = p === 1 ? 1 : 1 - Math.pow(2, -10 * p);
            el.textContent = formatar(Math.round(alvo * e));
            if (p < 1) requestAnimationFrame(passo);
            else finalizar();
        }
        requestAnimationFrame(passo);

        // Rede de segurança: se o rAF parar no meio (aba em segundo plano,
        // throttling do navegador), o número não pode ficar congelado num
        // valor errado — a métrica exibida tem de ser sempre a verdadeira.
        setTimeout(finalizar, duracao + 300);
    }

    function iniciarContadores() {
        const numeros = document.querySelectorAll('[data-alvo]');
        if (!numeros.length) return;

        // Sem JS de animação (ou sem movimento), mostra o valor final direto
        if (semMovimento || !('IntersectionObserver' in window)) {
            numeros.forEach(el => {
                el.textContent = formatar(parseInt(el.dataset.alvo, 10) || 0);
            });
            return;
        }

        numeros.forEach(el => { el.textContent = '0'; });

        const obs = new IntersectionObserver(entradas => {
            entradas.forEach(e => {
                if (!e.isIntersecting) return;
                const el = e.target;
                const alvo = parseInt(el.dataset.alvo, 10) || 0;
                // escalona a saída de cada número, para não subirem em bloco
                const atraso = parseInt(el.dataset.atraso, 10) || 0;
                setTimeout(() => animarNumero(el, alvo, 1400), atraso);
                obs.unobserve(el);
            });
        }, { threshold: 0.55 });

        numeros.forEach(el => obs.observe(el));
    }

    // ── 2. Terminal digitando ──────────────────────────────────────────
    function iniciarTerminal() {
        const cmd = document.querySelector('.hero-terminal .cmd');
        if (!cmd || semMovimento) return;

        // Guarda a marcação original (tem <span class="flag">) para restaurar
        // ao final — digitar HTML caractere a caractere quebraria as tags.
        const htmlFinal = cmd.innerHTML;
        const texto = cmd.textContent;
        cmd.textContent = '';

        let i = 0;
        const velocidade = 38; // ms por caractere

        function digitar() {
            if (i <= texto.length) {
                cmd.textContent = texto.slice(0, i);
                i++;
                setTimeout(digitar, velocidade);
            } else {
                cmd.innerHTML = htmlFinal; // devolve o destaque do --cert
            }
        }
        // começa junto com a cascata de entrada do hero
        setTimeout(digitar, 620);
    }

    function iniciar() {
        iniciarContadores();
        iniciarTerminal();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', iniciar);
    } else {
        iniciar();
    }
})();
