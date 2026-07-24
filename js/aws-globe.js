/**
 * Globo de Regiões AWS — hero da landing (CloudPath)
 *
 * Não é um globo decorativo: os nós ficam nas coordenadas reais das Regiões
 * da AWS, e sa-east-1 (São Paulo) é destacada porque é a Região do público
 * daqui. Infraestrutura Global (Regiões, AZs, Edge Locations) é conteúdo de
 * prova nas quatro certificações cobertas pelo site, então o hero mostra o
 * próprio assunto em vez de um enfeite.
 *
 * Carrega o Three.js sob demanda (CDN). Se falhar, o hero segue intacto —
 * o canvas simplesmente não é preenchido. Respeita prefers-reduced-motion
 * (desenha sem girar) e pausa fora da tela / com a aba oculta.
 */
(function () {
    const canvas = document.getElementById('awsGlobe');
    if (!canvas) return;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Regiões reais da AWS (lat, lon). destaque = a Região de São Paulo.
    const REGIONS = [
        { id: 'us-east-1',      lat:  38.13, lon:  -78.45 },
        { id: 'us-west-2',      lat:  45.87, lon: -119.69 },
        { id: 'ca-central-1',   lat:  45.50, lon:  -73.57 },
        { id: 'sa-east-1',      lat: -23.55, lon:  -46.63, destaque: true },
        { id: 'eu-west-1',      lat:  53.41, lon:   -8.24 },
        { id: 'eu-central-1',   lat:  50.11, lon:    8.68 },
        { id: 'af-south-1',     lat: -33.92, lon:   18.42 },
        { id: 'me-south-1',     lat:  26.07, lon:   50.55 },
        { id: 'ap-south-1',     lat:  19.08, lon:   72.88 },
        { id: 'ap-southeast-1', lat:   1.35, lon:  103.82 },
        { id: 'ap-northeast-1', lat:  35.68, lon:  139.69 },
        { id: 'ap-southeast-2', lat: -33.87, lon:  151.21 },
    ];

    const TEAL = 0x4ecdc4;
    const CORAL = 0xff6b6b;
    const RAIO = 1;

    function paraVetor(THREE, lat, lon, raio) {
        const phi = (90 - lat) * (Math.PI / 180);
        const theta = (lon + 180) * (Math.PI / 180);
        return new THREE.Vector3(
            -raio * Math.sin(phi) * Math.cos(theta),
            raio * Math.cos(phi),
            raio * Math.sin(phi) * Math.sin(theta)
        );
    }

    // Sem Three.js (CDN fora do ar, offline) ou sem WebGL (aparelho antigo):
    // o hero vira uma coluna só, em vez de deixar um vão vazio ao lado do texto.
    function desistir() {
        const topo = document.querySelector('.hero-top');
        if (topo) topo.classList.add('sem-globo');
    }

    async function iniciar() {
        let THREE;
        try {
            THREE = await import('https://unpkg.com/three@0.160.0/build/three.module.js');
        } catch (e) {
            desistir();
            return;
        }

        const cena = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
        camera.position.set(0, 0, 3.5);

        let renderer;
        try {
            renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        } catch (e) {
            desistir(); // sem WebGL disponível
            return;
        }
        renderer.setClearColor(0x000000, 0);

        const globo = new THREE.Group();
        // leve inclinação: evita o eixo perfeitamente vertical, que achata a leitura
        globo.rotation.z = 0.28;
        cena.add(globo);

        // ── Malha do globo: paralelos e meridianos ──────────────────────
        // Anéis dão um traço mais limpo que o wireframe de triângulos.
        const matLinha = new THREE.LineBasicMaterial({ color: TEAL, transparent: true, opacity: 0.20 });
        const SEG = 96;

        for (let i = 1; i < 9; i++) {
            const lat = -90 + (i * 180) / 9;
            const r = Math.cos(lat * Math.PI / 180) * RAIO;
            const y = Math.sin(lat * Math.PI / 180) * RAIO;
            const pts = [];
            for (let s = 0; s <= SEG; s++) {
                const a = (s / SEG) * Math.PI * 2;
                pts.push(new THREE.Vector3(Math.cos(a) * r, y, Math.sin(a) * r));
            }
            globo.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), matLinha));
        }

        for (let m = 0; m < 12; m++) {
            const ang = (m / 12) * Math.PI * 2;
            const pts = [];
            for (let s = 0; s <= SEG; s++) {
                const t = (s / SEG) * Math.PI - Math.PI / 2;
                pts.push(new THREE.Vector3(
                    Math.cos(t) * Math.cos(ang) * RAIO,
                    Math.sin(t) * RAIO,
                    Math.cos(t) * Math.sin(ang) * RAIO
                ));
            }
            globo.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), matLinha));
        }

        // Casca interna: dá volume e esconde as linhas do lado de trás,
        // para o globo não virar um emaranhado transparente.
        const casca = new THREE.Mesh(
            new THREE.SphereGeometry(RAIO * 0.985, 48, 32),
            new THREE.MeshBasicMaterial({ color: 0x0a1424, transparent: true, opacity: 0.86 })
        );
        globo.add(casca);

        // ── Nós das Regiões ────────────────────────────────────────────
        const saoPaulo = REGIONS.find(r => r.destaque);
        const nosDestaque = [];

        REGIONS.forEach(regiao => {
            const pos = paraVetor(THREE, regiao.lat, regiao.lon, RAIO * 1.012);
            const cor = regiao.destaque ? CORAL : TEAL;
            const tamanho = regiao.destaque ? 0.032 : 0.019;

            const no = new THREE.Mesh(
                new THREE.SphereGeometry(tamanho, 12, 12),
                new THREE.MeshBasicMaterial({ color: cor })
            );
            no.position.copy(pos);
            globo.add(no);

            // halo — só na Região destacada, para o olho ir direto nela
            if (regiao.destaque) {
                const halo = new THREE.Mesh(
                    new THREE.SphereGeometry(tamanho * 2.4, 16, 16),
                    new THREE.MeshBasicMaterial({ color: cor, transparent: true, opacity: 0.22 })
                );
                halo.position.copy(pos);
                globo.add(halo);
                nosDestaque.push(halo);
            }
        });

        // ── Arcos saindo de sa-east-1 ──────────────────────────────────
        // Sugerem a rede global sem virar teia: só alguns destinos.
        const destinos = ['us-east-1', 'eu-west-1', 'ap-southeast-1', 'af-south-1'];
        const origem = paraVetor(THREE, saoPaulo.lat, saoPaulo.lon, RAIO * 1.01);

        destinos.forEach(id => {
            const alvo = REGIONS.find(r => r.id === id);
            if (!alvo) return;
            const fim = paraVetor(THREE, alvo.lat, alvo.lon, RAIO * 1.01);
            const meio = origem.clone().add(fim).multiplyScalar(0.5)
                .normalize().multiplyScalar(RAIO * 1.42);
            const curva = new THREE.QuadraticBezierCurve3(origem, meio, fim);
            globo.add(new THREE.Line(
                new THREE.BufferGeometry().setFromPoints(curva.getPoints(48)),
                new THREE.LineBasicMaterial({ color: CORAL, transparent: true, opacity: 0.34 })
            ));
        });

        // ── Dimensionamento ────────────────────────────────────────────
        // A .container da home nasce com display:none e só aparece depois que
        // o Firebase carrega. Medir antes disso dá tamanho 0 e o canvas fica
        // com buffer 1x1 (um pixel esticado). O ResizeObserver resolve: mede
        // quando o elemento realmente ganha tamanho, e em cada resize depois.
        let dimensionado = false;

        function redimensionar() {
            const rect = canvas.getBoundingClientRect();
            const l = rect.width;
            const a = rect.height;
            if (l < 2 || a < 2) return; // ainda oculto — espera o próximo aviso

            renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
            renderer.setSize(l, a, false);
            camera.aspect = l / a;
            camera.updateProjectionMatrix();

            if (!dimensionado) {
                dimensionado = true;
                canvas.classList.add('is-ready'); // revela só com tamanho real
                if (reducedMotion) renderer.render(cena, camera);
            }
        }

        redimensionar();
        window.addEventListener('resize', redimensionar);
        if ('ResizeObserver' in window) {
            new ResizeObserver(redimensionar).observe(canvas);
        }

        // ── Interação: arrastar para girar ─────────────────────────────
        let arrastando = false, ultimoX = 0, velocidade = 0.0016;
        const inercia = { v: 0 };

        const pegarX = (ev) => (ev.touches ? ev.touches[0].clientX : ev.clientX);
        const iniciarArrasto = (ev) => { arrastando = true; ultimoX = pegarX(ev); };
        const moverArrasto = (ev) => {
            if (!arrastando) return;
            const x = pegarX(ev);
            const d = (x - ultimoX) * 0.005;
            globo.rotation.y += d;
            inercia.v = d;
            ultimoX = x;
        };
        const soltarArrasto = () => { arrastando = false; };

        canvas.addEventListener('mousedown', iniciarArrasto);
        window.addEventListener('mousemove', moverArrasto);
        window.addEventListener('mouseup', soltarArrasto);
        canvas.addEventListener('touchstart', iniciarArrasto, { passive: true });
        canvas.addEventListener('touchmove', moverArrasto, { passive: true });
        canvas.addEventListener('touchend', soltarArrasto);

        // ── Laço de animação ───────────────────────────────────────────
        let visivel = true, rodando = true, t = 0;

        if ('IntersectionObserver' in window) {
            new IntersectionObserver(entradas => {
                visivel = entradas[0].isIntersecting;
            }, { threshold: 0.05 }).observe(canvas);
        }
        document.addEventListener('visibilitychange', () => { rodando = !document.hidden; });

        function quadro() {
            requestAnimationFrame(quadro);
            if (!visivel || !rodando || !dimensionado) return;

            if (!reducedMotion) {
                if (!arrastando) {
                    globo.rotation.y += velocidade + inercia.v;
                    inercia.v *= 0.94;
                }
                t += 0.02;
                // pulso discreto no halo de sa-east-1
                const p = 1 + Math.sin(t) * 0.14;
                nosDestaque.forEach(h => h.scale.setScalar(p));
            }
            renderer.render(cena, camera);
        }

        // Com movimento reduzido, o quadro estático é desenhado assim que o
        // canvas ganha tamanho (dentro de redimensionar).
        if (!reducedMotion) quadro();
    }

    // Só inicia depois da página carregar, para não competir com o conteúdo.
    if (document.readyState === 'complete') iniciar();
    else window.addEventListener('load', iniciar);
})();
