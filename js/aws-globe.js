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
        // Câmera afastada de propósito: o globo ocupa ~70% da moldura, então a
        // atmosfera tem espaço para desvanecer ANTES da borda do canvas. Antes
        // ela batia no limite quadrado e desenhava um contorno reto.
        const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
        camera.position.set(0, 0, 4.5);

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

        // Junta vários caminhos num único objeto de linhas. Cada contorno
        // como um objeto separado custaria uma chamada de desenho por quadro
        // — com 128 ilhas isso derruba o FPS. Mesclado, é uma chamada só.
        function juntarLinhas(caminhos, fecharAnel) {
            const pos = [];
            caminhos.forEach(pts => {
                for (let i = 0; i < pts.length - 1; i++) {
                    pos.push(pts[i].x, pts[i].y, pts[i].z, pts[i + 1].x, pts[i + 1].y, pts[i + 1].z);
                }
                if (fecharAnel && pts.length > 2) {
                    const a = pts[pts.length - 1], b = pts[0];
                    pos.push(a.x, a.y, a.z, b.x, b.y, b.z);
                }
            });
            const g = new THREE.BufferGeometry();
            g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
            return g;
        }

        // ── 1. Núcleo ──────────────────────────────────────────────────
        // Segmentação generosa: é a silhueta que o olho lê como "redondo".
        globo.add(new THREE.Mesh(
            new THREE.SphereGeometry(R * 0.995, 96, 64),
            new THREE.MeshBasicMaterial({ color: 0x081226 })
        ));

        // ── 2. Malha lat/long (bem discreta) ───────────────────────────
        const SEG = 96;
        const caminhosMalha = [];
        for (let i = 1; i < 8; i++) {
            const lat = -90 + (i * 180) / 8;
            const r = Math.cos(lat * Math.PI / 180) * R * 1.001;
            const y = Math.sin(lat * Math.PI / 180) * R * 1.001;
            const pts = [];
            for (let s = 0; s <= SEG; s++) {
                const a = (s / SEG) * Math.PI * 2;
                pts.push(new THREE.Vector3(Math.cos(a) * r, y, Math.sin(a) * r));
            }
            caminhosMalha.push(pts);
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
            caminhosMalha.push(pts);
        }
        globo.add(new THREE.LineSegments(
            juntarLinhas(caminhosMalha, false),
            new THREE.LineBasicMaterial({ color: TEAL, transparent: true, opacity: 0.085 })
        ));

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

        // ── 4. Linhas de costa (128 ilhas num único objeto) ────────────
        const caminhosCosta = geo.COSTAS.map(anel => {
            const pts = [];
            for (let i = 0; i < anel.length; i += 2) {
                pts.push(vet(THREE, anel[i + 1], anel[i], R * 1.006));
            }
            return pts;
        });
        globo.add(new THREE.LineSegments(
            juntarLinhas(caminhosCosta, true),
            new THREE.LineBasicMaterial({ color: TEAL, transparent: true, opacity: 0.5 })
        ));

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

        // ── 6. Malha de tráfego entre Regiões ──────────────────────────
        // Rotas que saem de sa-east-1 vêm em coral e mais fortes (é a Região
        // do público daqui); o resto do backbone fica em teal, discreto, para
        // sugerir a rede global sem virar teia.
        const ROTAS = [
            ['sa-east-1', 'us-east-1'],
            ['sa-east-1', 'eu-west-1'],
            ['sa-east-1', 'af-south-1'],
            ['sa-east-1', 'us-west-2'],
            ['us-east-1', 'eu-west-1'],
            ['us-east-1', 'ca-central-1'],
            ['eu-west-1', 'eu-central-1'],
            ['eu-central-1', 'me-south-1'],
            ['me-south-1', 'ap-south-1'],
            ['ap-south-1', 'ap-southeast-1'],
            ['ap-southeast-1', 'ap-northeast-1'],
            ['ap-southeast-1', 'ap-southeast-2'],
            ['us-west-2', 'ap-northeast-1'],
            ['af-south-1', 'ap-south-1'],
        ];

        const pulsos = [];
        const posDe = id => {
            const r = REGIOES.find(x => x.id === id);
            return r ? vet(THREE, r.lat, r.lon, R * 1.01) : null;
        };

        // arcos agrupados por cor: duas chamadas de desenho no total
        const arcosSP = [], arcosRede = [];

        ROTAS.forEach(([a, b], i) => {
            const ini = posDe(a), fim = posDe(b);
            if (!ini || !fim) return;

            const daSP = (a === 'sa-east-1' || b === 'sa-east-1');

            // quanto mais longa a rota, mais alto o arco sobe
            const dist = ini.distanceTo(fim);
            const meio = ini.clone().add(fim).multiplyScalar(0.5)
                .normalize().multiplyScalar(R * (1 + dist * 0.22));
            const curva = new THREE.QuadraticBezierCurve3(ini, meio, fim);

            (daSP ? arcosSP : arcosRede).push(curva.getPoints(56));

            // pulso viajando: é o que dá a leitura de "tráfego"
            const pulso = new THREE.Mesh(
                new THREE.SphereGeometry(daSP ? 0.013 : 0.010, 8, 8),
                new THREE.MeshBasicMaterial({
                    color: daSP ? 0xffb3a0 : 0x9ff0e8,
                    transparent: true, opacity: daSP ? 1 : 0.75,
                })
            );
            pulso.userData = {
                curva,
                t: (i * 0.37) % 1,               // fases espalhadas
                vel: 0.0042 + (i % 4) * 0.0009,  // velocidades diferentes
            };
            globo.add(pulso);
            pulsos.push(pulso);
        });

        globo.add(new THREE.LineSegments(juntarLinhas(arcosSP, false),
            new THREE.LineBasicMaterial({ color: CORAL, transparent: true, opacity: 0.32 })));
        globo.add(new THREE.LineSegments(juntarLinhas(arcosRede, false),
            new THREE.LineBasicMaterial({ color: TEAL, transparent: true, opacity: 0.16 })));

        // ── 7. Atmosfera (fresnel) ─────────────────────────────────────
        // Duas cascas: a interna dá o "anel" nítido rente ao planeta; a
        // externa é um halo largo e fraco, que se dissolve no fundo do site.
        function fazerAtmosfera(raio, forca, expoente, opacidade) {
            return new THREE.Mesh(
                // malha modesta: o halo é um degradê suave, quem faz a borda
                // parecer redonda é a queda do alpha, não a tesselação
                new THREE.SphereGeometry(raio, 48, 32),
                new THREE.ShaderMaterial({
                    transparent: true,
                    side: THREE.BackSide,
                    depthWrite: false,
                    blending: THREE.AdditiveBlending,
                    uniforms: {
                        cor: { value: new THREE.Color(TEAL) },
                        forca: { value: forca },
                        expoente: { value: expoente },
                        opacidade: { value: opacidade },
                    },
                    vertexShader: `
                        varying vec3 vN;
                        varying vec3 vP;
                        void main() {
                            vN = normalize(normalMatrix * normal);
                            vec4 mv = modelViewMatrix * vec4(position, 1.0);
                            vP = -mv.xyz;
                            gl_Position = projectionMatrix * mv;
                        }`,
                    fragmentShader: `
                        uniform vec3 cor;
                        uniform float forca;
                        uniform float expoente;
                        uniform float opacidade;
                        varying vec3 vN;
                        varying vec3 vP;
                        void main() {
                            // fresnel pela direção real de visão: o brilho
                            // acompanha a curvatura em vez de um eixo fixo
                            float f = 1.0 - abs(dot(normalize(vN), normalize(vP)));
                            float i = pow(clamp(f * forca, 0.0, 1.0), expoente);
                            gl_FragColor = vec4(cor * i * opacidade, i * opacidade);
                        }`,
                })
            );
        }

        eixo.add(fazerAtmosfera(R * 1.055, 1.25, 2.2, 0.55)); // anel rente
        eixo.add(fazerAtmosfera(R * 1.34,  1.05, 2.8, 0.32)); // halo difuso

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

                // pulsos correndo pelas rotas, cada um no seu ritmo
                pulsos.forEach(pu => {
                    pu.userData.t = (pu.userData.t + pu.userData.vel) % 1;
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
