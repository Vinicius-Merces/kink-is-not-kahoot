/**
 * Globo de Regiões AWS — hero da landing (CloudPath)
 *
 * Não é um globo decorativo: a geografia é real (Natural Earth 110m) e os
 * nós ficam nas coordenadas reais das Regiões da AWS, com sa-east-1
 * (São Paulo) destacada. Infraestrutura Global (Regiões, AZs, Edge) é
 * conteúdo de prova nas quatro certificações do site, então o hero mostra
 * o próprio assunto em vez de um enfeite.
 *
 * Camadas, de dentro para fora:
 *   1. núcleo opaco     — esconde o lado de trás, dá volume
 *   2. malha lat/long   — discreta, sugere o console
 *   3. terra pontilhada — continentes como nuvem de pontos
 *   4. linhas de costa  — contorno nítido por cima dos pontos
 *   5. nós das Regiões  — teal, sa-east-1 em coral com halo pulsante
 *   6. arcos            — rotas saindo de sa-east-1
 *   7. atmosfera        — halo por trás, com fresnel
 *   8. poeira estelar   — partículas ambientes ao redor
 *
 * Three.js e a geografia carregam sob demanda. Sem CDN, sem WebGL ou em
 * aparelho fraco, o hero volta a uma coluna em vez de deixar vão vazio.
 * Respeita prefers-reduced-motion, pausa fora da tela e com a aba oculta.
 */
(function () {
    const canvas = document.getElementById('awsGlobe');
    if (!canvas) return;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const REGIOES = [
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
    const R = 1;

    function desistir() {
        const topo = document.querySelector('.hero-top');
        if (topo) topo.classList.add('sem-globo');
    }

    // lat/lon -> posição na esfera
    function vet(THREE, lat, lon, raio) {
        const phi = (90 - lat) * (Math.PI / 180);
        const theta = (lon + 180) * (Math.PI / 180);
        return new THREE.Vector3(
            -raio * Math.sin(phi) * Math.cos(theta),
            raio * Math.cos(phi),
            raio * Math.sin(phi) * Math.sin(theta)
        );
    }

    async function iniciar() {
        let THREE, geo;
        try {
            [THREE, geo] = await Promise.all([
                import('https://unpkg.com/three@0.160.0/build/three.module.js'),
                import('./world-data.js'),
            ]);
        } catch (e) {
            desistir();
            return;
        }

        const cena = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
        camera.position.set(0, 0, 3.4);

        let renderer;
        try {
            renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        } catch (e) {
            desistir();
            return;
        }
        renderer.setClearColor(0x000000, 0);

        // Grupo externo inclina o eixo; o interno gira. Assim a rotação não
        // "cambaleia" como aconteceria girando um grupo já inclinado no Z.
        const eixo = new THREE.Group();
        eixo.rotation.z = 0.36;
        eixo.rotation.x = 0.16;
        cena.add(eixo);

        const globo = new THREE.Group();
        eixo.add(globo);

        // ── 1. Núcleo ──────────────────────────────────────────────────
        globo.add(new THREE.Mesh(
            new THREE.SphereGeometry(R * 0.995, 64, 48),
            new THREE.MeshBasicMaterial({ color: 0x081226 })
        ));

        // ── 2. Malha lat/long (bem discreta) ───────────────────────────
        const matMalha = new THREE.LineBasicMaterial({ color: TEAL, transparent: true, opacity: 0.085 });
        const SEG = 96;
        for (let i = 1; i < 8; i++) {
            const lat = -90 + (i * 180) / 8;
            const r = Math.cos(lat * Math.PI / 180) * R * 1.001;
            const y = Math.sin(lat * Math.PI / 180) * R * 1.001;
            const pts = [];
            for (let s = 0; s <= SEG; s++) {
                const a = (s / SEG) * Math.PI * 2;
                pts.push(new THREE.Vector3(Math.cos(a) * r, y, Math.sin(a) * r));
            }
            globo.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), matMalha));
        }
        for (let m = 0; m < 12; m++) {
            const ang = (m / 12) * Math.PI * 2;
            const pts = [];
            for (let s = 0; s <= SEG; s++) {
                const t = (s / SEG) * Math.PI - Math.PI / 2;
                pts.push(new THREE.Vector3(
                    Math.cos(t) * Math.cos(ang) * R * 1.001,
                    Math.sin(t) * R * 1.001,
                    Math.cos(t) * Math.sin(ang) * R * 1.001
                ));
            }
            globo.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), matMalha));
        }

        // ── 3. Terra pontilhada ────────────────────────────────────────
        // A nuvem de pontos lê como visualização de dados — a mesma
        // linguagem do fundo animado do site.
        const posTerra = [];
        for (let i = 0; i < geo.TERRA.length; i += 2) {
            const p = vet(THREE, geo.TERRA[i + 1], geo.TERRA[i], R * 1.004);
            posTerra.push(p.x, p.y, p.z);
        }
        const geomTerra = new THREE.BufferGeometry();
        geomTerra.setAttribute('position', new THREE.Float32BufferAttribute(posTerra, 3));
        globo.add(new THREE.Points(geomTerra, new THREE.PointsMaterial({
            color: 0x7fe3dc, size: 0.016, sizeAttenuation: true,
            transparent: true, opacity: 0.62, depthWrite: false,
        })));

        // ── 4. Linhas de costa ─────────────────────────────────────────
        const matCosta = new THREE.LineBasicMaterial({ color: TEAL, transparent: true, opacity: 0.5 });
        geo.COSTAS.forEach(anel => {
            const pts = [];
            for (let i = 0; i < anel.length; i += 2) {
                pts.push(vet(THREE, anel[i + 1], anel[i], R * 1.006));
            }
            globo.add(new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts), matCosta));
        });

        // ── 5. Nós das Regiões ─────────────────────────────────────────
        const saoPaulo = REGIOES.find(r => r.destaque);
        const halos = [];
        const anéis = [];

        REGIOES.forEach(reg => {
            const pos = vet(THREE, reg.lat, reg.lon, R * 1.012);
            const cor = reg.destaque ? CORAL : TEAL;
            const tam = reg.destaque ? 0.030 : 0.016;

            const no = new THREE.Mesh(
                new THREE.SphereGeometry(tam, 14, 14),
                new THREE.MeshBasicMaterial({ color: cor })
            );
            no.position.copy(pos);
            globo.add(no);

            const halo = new THREE.Mesh(
                new THREE.SphereGeometry(tam * 2.2, 16, 16),
                new THREE.MeshBasicMaterial({ color: cor, transparent: true, opacity: reg.destaque ? 0.26 : 0.16, depthWrite: false })
            );
            halo.position.copy(pos);
            globo.add(halo);
            if (reg.destaque) halos.push(halo);

            // anel de radar em sa-east-1: expande e some, em laço
            if (reg.destaque) {
                for (let k = 0; k < 2; k++) {
                    const anel = new THREE.Mesh(
                        new THREE.RingGeometry(tam * 1.6, tam * 1.9, 32),
                        new THREE.MeshBasicMaterial({ color: cor, transparent: true, opacity: 0.5, side: THREE.DoubleSide, depthWrite: false })
                    );
                    anel.position.copy(pos);
                    anel.lookAt(0, 0, 0);
                    anel.userData.fase = k * 0.5;
                    globo.add(anel);
                    anéis.push(anel);
                }
            }
        });

        // ── 6. Arcos saindo de sa-east-1 ───────────────────────────────
        const destinos = ['us-east-1', 'eu-west-1', 'ap-southeast-1', 'af-south-1', 'us-west-2'];
        const origem = vet(THREE, saoPaulo.lat, saoPaulo.lon, R * 1.01);
        const pulsos = [];

        destinos.forEach(id => {
            const alvo = REGIOES.find(r => r.id === id);
            if (!alvo) return;
            const fim = vet(THREE, alvo.lat, alvo.lon, R * 1.01);
            const dist = origem.distanceTo(fim);
            const meio = origem.clone().add(fim).multiplyScalar(0.5)
                .normalize().multiplyScalar(R * (1 + dist * 0.24));
            const curva = new THREE.QuadraticBezierCurve3(origem, meio, fim);

            globo.add(new THREE.Line(
                new THREE.BufferGeometry().setFromPoints(curva.getPoints(64)),
                new THREE.LineBasicMaterial({ color: CORAL, transparent: true, opacity: 0.30 })
            ));

            // pulso viajando pelo arco: dá vida sem poluir
            const pulso = new THREE.Mesh(
                new THREE.SphereGeometry(0.012, 8, 8),
                new THREE.MeshBasicMaterial({ color: 0xffb3a0 })
            );
            pulso.userData = { curva, t: Math.random() };
            globo.add(pulso);
            pulsos.push(pulso);
        });

        // ── 7. Atmosfera (fresnel) ─────────────────────────────────────
        const atmosfera = new THREE.Mesh(
            new THREE.SphereGeometry(R * 1.16, 64, 48),
            new THREE.ShaderMaterial({
                transparent: true,
                side: THREE.BackSide,
                depthWrite: false,
                uniforms: { cor: { value: new THREE.Color(TEAL) } },
                vertexShader: `
                    varying vec3 vN;
                    void main() {
                        vN = normalize(normalMatrix * normal);
                        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                    }`,
                fragmentShader: `
                    uniform vec3 cor;
                    varying vec3 vN;
                    void main() {
                        float i = pow(0.62 - dot(vN, vec3(0.0, 0.0, 1.0)), 2.6);
                        gl_FragColor = vec4(cor, 1.0) * i * 0.9;
                    }`,
            })
        );
        eixo.add(atmosfera);

        // ── 8. Poeira estelar ──────────────────────────────────────────
        const nPart = 420;
        const posPart = [];
        for (let i = 0; i < nPart; i++) {
            // casca esférica ao redor do globo, sem entrar nele
            const raio = 1.7 + Math.random() * 1.5;
            const t = Math.acos(2 * Math.random() - 1);
            const f = Math.random() * Math.PI * 2;
            posPart.push(
                raio * Math.sin(t) * Math.cos(f),
                raio * Math.cos(t) * 0.7,
                raio * Math.sin(t) * Math.sin(f)
            );
        }
        const geomPart = new THREE.BufferGeometry();
        geomPart.setAttribute('position', new THREE.Float32BufferAttribute(posPart, 3));
        const particulas = new THREE.Points(geomPart, new THREE.PointsMaterial({
            color: 0x9fd8ff, size: 0.013, sizeAttenuation: true,
            transparent: true, opacity: 0.5, depthWrite: false,
        }));
        cena.add(particulas);

        // ── Dimensionamento ────────────────────────────────────────────
        // A .container da home nasce com display:none e só aparece depois do
        // Firebase. Medir antes disso daria buffer 1x1 (um pixel esticado);
        // o ResizeObserver mede quando o elemento ganha tamanho de verdade.
        let dimensionado = false;
        function redimensionar() {
            const r = canvas.getBoundingClientRect();
            if (r.width < 2 || r.height < 2) return;
            renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
            renderer.setSize(r.width, r.height, false);
            camera.aspect = r.width / r.height;
            camera.updateProjectionMatrix();
            if (!dimensionado) {
                dimensionado = true;
                canvas.classList.add('is-ready');
                if (reducedMotion) renderer.render(cena, camera);
            }
        }
        redimensionar();
        window.addEventListener('resize', redimensionar);
        if ('ResizeObserver' in window) new ResizeObserver(redimensionar).observe(canvas);

        // ── Interação ──────────────────────────────────────────────────
        let arrastando = false, ultimoX = 0, ultimoY = 0;
        const inercia = { x: 0 };
        const VEL = 0.0013;

        const px = ev => (ev.touches ? ev.touches[0].clientX : ev.clientX);
        const py = ev => (ev.touches ? ev.touches[0].clientY : ev.clientY);

        const pegar = ev => { arrastando = true; ultimoX = px(ev); ultimoY = py(ev); };
        const mover = ev => {
            if (!arrastando) return;
            const x = px(ev), y = py(ev);
            const dx = (x - ultimoX) * 0.005;
            globo.rotation.y += dx;
            // inclinar um pouco no eixo X dá sensação de globo de verdade
            eixo.rotation.x = Math.max(-0.5, Math.min(0.6, eixo.rotation.x + (y - ultimoY) * 0.003));
            inercia.x = dx;
            ultimoX = x; ultimoY = y;
        };
        const soltar = () => { arrastando = false; };

        canvas.addEventListener('mousedown', pegar);
        window.addEventListener('mousemove', mover);
        window.addEventListener('mouseup', soltar);
        canvas.addEventListener('touchstart', pegar, { passive: true });
        canvas.addEventListener('touchmove', mover, { passive: true });
        canvas.addEventListener('touchend', soltar);

        // ── Laço ───────────────────────────────────────────────────────
        let visivel = true, rodando = true, t = 0;

        if ('IntersectionObserver' in window) {
            new IntersectionObserver(e => { visivel = e[0].isIntersecting; }, { threshold: 0.05 })
                .observe(canvas);
        }
        document.addEventListener('visibilitychange', () => { rodando = !document.hidden; });

        function quadro() {
            requestAnimationFrame(quadro);
            if (!visivel || !rodando || !dimensionado) return;

            if (!reducedMotion) {
                if (!arrastando) {
                    globo.rotation.y += VEL + inercia.x;
                    inercia.x *= 0.95;
                }
                t += 0.016;

                const p = 1 + Math.sin(t * 2) * 0.16;
                halos.forEach(h => h.scale.setScalar(p));

                // anéis de radar: expandem e desvanecem
                anéis.forEach(a => {
                    const f = ((t * 0.5 + a.userData.fase) % 1);
                    a.scale.setScalar(1 + f * 3.2);
                    a.material.opacity = 0.5 * (1 - f);
                });

                // pulsos correndo pelos arcos
                pulsos.forEach(pu => {
                    pu.userData.t = (pu.userData.t + 0.0055) % 1;
                    pu.position.copy(pu.userData.curva.getPoint(pu.userData.t));
                });

                particulas.rotation.y -= 0.0004;
            }
            renderer.render(cena, camera);
        }

        if (!reducedMotion) quadro();
    }

    if (document.readyState === 'complete') iniciar();
    else window.addEventListener('load', iniciar);
})();
