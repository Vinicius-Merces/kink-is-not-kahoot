/* CloudArena: explicit atlases, cached decoding, one renderer per fighter. */
(function (root) {
    'use strict';
    const images = new Map();
    function loadImage(url) {
        if (!images.has(url)) {
            const promise = (async () => {
                const image = new Image();
                image.src = url;
                await image.decode();
                if (!image.naturalWidth || !image.naturalHeight) throw new Error('Imagem inválida: ' + url);
                return image;
            })().catch(error => { images.delete(url); throw error; });
            images.set(url, promise);
        }
        return images.get(url);
    }
    class ArenaSprite {
        constructor(variant) {
            this.variant = variant;
            this.images = {};
            this.canvas = null;
            this._raf = null;
            this._generation = 0;
            this._requested = null;
            this.isReady = false;
        }
        load() {
            if (this._loading) return this._loading;
            this._loading = Promise.all(Object.entries(this.variant.animations).map(async ([state, spec]) => {
                const image = await loadImage(spec.url);
                for (const [x,y,w,h] of spec.frames) {
                    if (x < 0 || y < 0 || w <= 0 || h <= 0 || x+w > image.naturalWidth || y+h > image.naturalHeight) {
                        throw new Error('Recorte fora da imagem: ' + spec.url);
                    }
                }
                this.images[state] = image;
            })).then(() => {
                this.isReady = true;
                if (this._requested) {
                    const [name, opts] = this._requested;
                    this._requested = null;
                    this.play(name, opts);
                }
                return this;
            }).catch(error => { this._loading = null; throw error; });
            return this._loading;
        }
        attach(canvas) {
            if (this.canvas === canvas) return;
            this.stop();
            this.canvas = canvas;
            this.ctx = canvas.getContext('2d');
            this.ctx.imageSmoothingEnabled = true;
        }
        stop() {
            this._generation++;
            this._requested = null;
            if (this._raf !== null) cancelAnimationFrame(this._raf);
            this._raf = null;
        }
        drawFrame(name, frame) {
            const spec = this.variant.animations[name];
            if (!spec || !this.images[name] || !this.canvas) return;
            const [x,y,w,h] = spec.frames[frame];
            const scale = Math.min(this.canvas.width/w, this.canvas.height/h);
            this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);
            this.ctx.drawImage(this.images[name], x,y,w,h,
                (this.canvas.width-w*scale)/2,(this.canvas.height-h*scale)/2,w*scale,h*scale);
        }
        play(name, opts = {}) {
            if (!this.variant.animations[name] || !this.canvas) return false;
            if (!this.isReady) {
                this._requested = [name, opts]; // late decode never replaces a hit with idle
                return true;
            }
            this.stop();
            const generation = this._generation;
            const spec = this.variant.animations[name];
            const total = spec.frames.length;
            const duration = spec.duration;
            const started = performance.now();
            let previous = -1;
            const tick = time => {
                if (generation !== this._generation || !this.canvas.isConnected) return;
                const elapsed = Math.max(0,time-started);
                const complete = elapsed >= duration;
                const frame = complete && !opts.loop ? total-1 : Math.min(total-1,Math.floor((elapsed%duration)/duration*total));
                if (frame !== previous) {
                    previous = frame;
                    this.drawFrame(name,frame);
                    if (opts.onFrame) opts.onFrame(frame,total);
                }
                if (complete && !opts.loop) {
                    this._raf = null;
                    if (opts.onComplete) opts.onComplete();
                } else this._raf = requestAnimationFrame(tick);
            };
            tick(started);
            return true;
        }
    }
    let catalogPromise;
    root.CloudArenaSprites = {
        ArenaSprite,
        loadCatalog() {
            if (!catalogPromise) catalogPromise = fetch('images/arena/v2/catalog.json?v=20261019')
                .then(res => { if (!res.ok) throw new Error('Catálogo de sprites indisponível'); return res.json(); })
                .catch(error => { catalogPromise = null; throw error; });
            return catalogPromise;
        },
    };
})(typeof window !== 'undefined' ? window : globalThis);
