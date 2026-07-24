/**
 * Progresso de leitura das apostilas (CloudPath)
 *
 * As trilhas são longas (a do SAA-C03 tem 21 capítulos), e hoje não há
 * como saber onde você está. Duas peças, ambas informativas:
 *
 *   1. Barra fina no topo — quanto do texto já passou.
 *   2. Scroll-spy — destaca no índice lateral o capítulo que está sendo
 *      lido, para o menu deixar de ser uma lista estática.
 *
 * Só mede o artigo, não a página inteira: rodapé e navegação não contam
 * como leitura, senão a barra nunca chega ao fim de verdade.
 */
(function () {
    const capitulos = Array.from(document.querySelectorAll('.trilha-chapter[id]'));
    if (!capitulos.length) return;

    const semMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ── Barra de progresso ─────────────────────────────────────────────
    const barra = document.createElement('div');
    barra.className = 'leitura-barra';
    barra.setAttribute('role', 'progressbar');
    barra.setAttribute('aria-label', 'Progresso de leitura da apostila');
    barra.setAttribute('aria-valuemin', '0');
    barra.setAttribute('aria-valuemax', '100');
    const preenchimento = document.createElement('span');
    barra.appendChild(preenchimento);
    document.body.appendChild(barra);

    // O trecho "legível" vai do topo do primeiro capítulo ao fim do último.
    function limites() {
        const primeiro = capitulos[0];
        const ultimo = capitulos[capitulos.length - 1];
        const inicio = primeiro.getBoundingClientRect().top + window.scrollY;
        const fim = ultimo.getBoundingClientRect().bottom + window.scrollY;
        return { inicio, fim };
    }

    // ── Scroll-spy no índice lateral ───────────────────────────────────
    const links = new Map();
    capitulos.forEach(cap => {
        const link = document.querySelector(`.trilha-sidebar a[href="#${cap.id}"]`);
        if (link) links.set(cap.id, link);
    });

    let atual = null;
    function marcarAtual(id) {
        if (id === atual) return;
        atual = id;
        links.forEach((link, capId) => {
            const ativo = capId === id;
            link.classList.toggle('lendo', ativo);
            if (ativo) link.setAttribute('aria-current', 'true');
            else link.removeAttribute('aria-current');
        });
    }

    // ── Atualização (agendada por quadro, não por evento de scroll) ────
    let pendente = false;

    function atualizar() {
        pendente = false;

        const { inicio, fim } = limites();
        const alcance = Math.max(1, fim - inicio - window.innerHeight);
        const p = Math.min(1, Math.max(0, (window.scrollY - inicio) / alcance));
        preenchimento.style.width = (p * 100).toFixed(2) + '%';
        barra.setAttribute('aria-valuenow', Math.round(p * 100));

        // capítulo atual = o último cujo topo já passou de ~1/3 da tela
        const linha = window.scrollY + window.innerHeight * 0.33;
        let visto = capitulos[0];
        for (const cap of capitulos) {
            if (cap.getBoundingClientRect().top + window.scrollY <= linha) visto = cap;
            else break;
        }
        marcarAtual(visto.id);
    }

    function agendar() {
        if (pendente) return;
        pendente = true;
        requestAnimationFrame(atualizar);
    }

    window.addEventListener('scroll', agendar, { passive: true });
    window.addEventListener('resize', agendar);
    if (!semMovimento) barra.classList.add('anima');
    atualizar();
})();
