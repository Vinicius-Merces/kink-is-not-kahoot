/**
 * Audio Reader — player de narração pré-gravada (Azure Neural TTS) para as trilhas
 * Toca arquivos de áudio reais por capítulo, com Media Session API para
 * controle em segundo plano (tela bloqueada) no celular.
 */
(function () {
    'use strict';

    const AUDIO_MANIFEST = {
        cap1: 'assets/narracao/saa-c03/cap01.mp3',
        cap2: 'assets/narracao/saa-c03/cap02.mp3',
        cap3: 'assets/narracao/saa-c03/cap03.mp3',
        cap4: 'assets/narracao/saa-c03/cap04.mp3',
        cap5: 'assets/narracao/saa-c03/cap05.mp3',
        cap6: 'assets/narracao/saa-c03/cap06.mp3',
    };

    const state = {
        isOpen: false,
        rate: 1.0,
        chapterId: null,
        chapterTitle: '',
    };

    let audioEl, bar, triggerBtn, playBtn, progressBarEl,
        progressFill, progressInfo, chapterLabel, speedLabel;

    function buildUI() {
        triggerBtn = document.createElement('button');
        triggerBtn.className = 'tts-trigger-btn';
        triggerBtn.setAttribute('aria-label', 'Narração do capítulo');
        triggerBtn.innerHTML = '🎧 <span>Narração</span>';
        document.body.appendChild(triggerBtn);

        bar = document.createElement('div');
        bar.className = 'tts-bar';
        bar.setAttribute('role', 'region');
        bar.setAttribute('aria-label', 'Narrador de áudio');
        bar.innerHTML = `
          <div class="tts-bar-inner">
            <span class="tts-chapter-label" id="ttsChapterLabel">—</span>

            <div class="tts-progress-wrap">
              <div class="tts-progress-bar" id="ttsProgressBar" title="Progresso da narração">
                <div class="tts-progress-fill" id="ttsProgressFill"></div>
              </div>
              <span class="tts-progress-info" id="ttsProgressInfo">0:00 / 0:00</span>
            </div>

            <div class="tts-controls">
              <button class="tts-btn" id="ttsPrevBtn" title="Voltar 15s" aria-label="Voltar 15 segundos">⏮</button>
              <button class="tts-btn tts-btn-play" id="ttsPlayBtn" title="Play / Pausar" aria-label="Play">▶</button>
              <button class="tts-btn" id="ttsNextBtn" title="Avançar 15s" aria-label="Avançar 15 segundos">⏭</button>
            </div>

            <div class="tts-speed-group">
              <button class="tts-speed-btn" id="ttsSlowerBtn" title="Mais lento">−</button>
              <span class="tts-speed-label" id="ttsSpeedLabel">1.0×</span>
              <button class="tts-speed-btn" id="ttsFasterBtn" title="Mais rápido">+</button>
            </div>

            <button class="tts-btn tts-btn-close" id="ttsCloseBtn" title="Fechar narrador" aria-label="Fechar narrador">✕</button>
          </div>
        `;
        document.body.appendChild(bar);

        audioEl = document.createElement('audio');
        audioEl.preload = 'none';
        document.body.appendChild(audioEl);

        playBtn       = document.getElementById('ttsPlayBtn');
        progressBarEl = document.getElementById('ttsProgressBar');
        progressFill  = document.getElementById('ttsProgressFill');
        progressInfo  = document.getElementById('ttsProgressInfo');
        chapterLabel  = document.getElementById('ttsChapterLabel');
        speedLabel    = document.getElementById('ttsSpeedLabel');

        triggerBtn.addEventListener('click', toggleBar);
        document.getElementById('ttsCloseBtn').addEventListener('click', closeBar);
        playBtn.addEventListener('click', togglePlay);
        document.getElementById('ttsPrevBtn').addEventListener('click', () => seekBy(-15));
        document.getElementById('ttsNextBtn').addEventListener('click', () => seekBy(15));
        document.getElementById('ttsSlowerBtn').addEventListener('click', () => changeSpeed(-0.25));
        document.getElementById('ttsFasterBtn').addEventListener('click', () => changeSpeed(+0.25));
        progressBarEl.addEventListener('click', onProgressBarClick);

        audioEl.addEventListener('play', onPlay);
        audioEl.addEventListener('pause', onPause);
        audioEl.addEventListener('ended', onEnded);
        audioEl.addEventListener('timeupdate', updateProgress);
        audioEl.addEventListener('loadedmetadata', updateProgress);
    }

    function formatTime(seconds) {
        if (!isFinite(seconds) || seconds < 0) return '0:00';
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m}:${s.toString().padStart(2, '0')}`;
    }

    function updateProgress() {
        const total = audioEl.duration || 0;
        const cur = audioEl.currentTime || 0;
        progressFill.style.width = (total ? (cur / total) * 100 : 0) + '%';
        progressInfo.textContent = `${formatTime(cur)} / ${formatTime(total)}`;
    }

    function onProgressBarClick(e) {
        if (!audioEl.duration || !isFinite(audioEl.duration)) return;
        const rect = progressBarEl.getBoundingClientRect();
        const pct = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
        audioEl.currentTime = pct * audioEl.duration;
    }

    function seekBy(deltaSeconds) {
        if (!audioEl.duration) return;
        audioEl.currentTime = Math.max(0, Math.min(audioEl.duration, audioEl.currentTime + deltaSeconds));
    }

    function onPlay() {
        playBtn.textContent = '⏸';
        playBtn.setAttribute('aria-label', 'Pausar');
        triggerBtn.classList.add('tts-active');
        updateMediaSessionMetadata();
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'playing';
    }

    function onPause() {
        playBtn.textContent = '▶';
        playBtn.setAttribute('aria-label', 'Play');
        if ('mediaSession' in navigator) navigator.mediaSession.playbackState = 'paused';
    }

    function onEnded() {
        triggerBtn.classList.remove('tts-active');
    }

    function togglePlay() {
        if (!audioEl.src) return;
        if (audioEl.paused) audioEl.play(); else audioEl.pause();
    }

    function changeSpeed(delta) {
        state.rate = Math.min(2.5, Math.max(0.5, +(state.rate + delta).toFixed(2)));
        audioEl.playbackRate = state.rate;
        speedLabel.textContent = state.rate.toFixed(1) + '×';
        localStorage.setItem('tts_rate', state.rate);
    }

    // ── Chapter detection (mesma lógica de antes) ───────────────────────────
    function detectCurrentChapter() {
        const chapters = Array.from(document.querySelectorAll('.trilha-chapter'));
        if (!chapters.length) return null;
        let best = null, bestRatio = -1;
        chapters.forEach(ch => {
            const r = ch.getBoundingClientRect();
            const visible = Math.min(r.bottom, window.innerHeight) - Math.max(r.top, 0);
            if (visible > bestRatio) { bestRatio = visible; best = ch; }
        });
        return best;
    }

    function loadChapter(chapter) {
        if (!chapter) return;
        const wasPlaying = !audioEl.paused;
        state.chapterId = chapter.id;

        const h2 = chapter.querySelector('.trilha-chapter-header h2');
        state.chapterTitle = h2 ? h2.textContent.trim() : chapter.id;

        const src = AUDIO_MANIFEST[state.chapterId];
        if (src) {
            audioEl.src = src;
            audioEl.playbackRate = state.rate;
            playBtn.disabled = false;
            triggerBtn.classList.remove('tts-unavailable');
            chapterLabel.textContent = state.chapterTitle.substring(0, 30);
            if (wasPlaying) audioEl.play();
        } else {
            audioEl.removeAttribute('src');
            playBtn.disabled = true;
            triggerBtn.classList.add('tts-unavailable');
            chapterLabel.textContent = state.chapterTitle.substring(0, 24) + ' (em breve)';
        }
        updateProgress();
        updateMediaSessionMetadata();
    }

    function updateMediaSessionMetadata() {
        if (!('mediaSession' in navigator)) return;
        navigator.mediaSession.metadata = new MediaMetadata({
            title: state.chapterTitle || 'Trilha SAA-C03',
            artist: 'Apostila — Narração',
            album: 'Trilha SAA-C03',
        });
    }

    // ── Bar open/close ────────────────────────────────────────────────────
    function openBar() {
        state.isOpen = true;
        bar.classList.add('tts-open');
        triggerBtn.classList.add('tts-active');
        document.body.classList.add('tts-bar-open');

        const chapter = detectCurrentChapter();
        if (chapter && chapter.id !== state.chapterId) {
            loadChapter(chapter);
        }
    }

    function closeBar() {
        state.isOpen = false;
        bar.classList.remove('tts-open');
        document.body.classList.remove('tts-bar-open');
        if (audioEl.paused) triggerBtn.classList.remove('tts-active');
    }

    function toggleBar() {
        if (state.isOpen) closeBar(); else openBar();
    }

    function bindSidebarLinks() {
        document.querySelectorAll('.trilha-sidebar a[href^="#cap"]').forEach(link => {
            link.addEventListener('click', () => {
                setTimeout(() => {
                    const id = link.getAttribute('href').slice(1);
                    const ch = document.getElementById(id);
                    if (ch && ch.id !== state.chapterId) {
                        loadChapter(ch);
                    }
                }, 200);
            });
        });
    }

    function init() {
        buildUI();

        const savedRate = parseFloat(localStorage.getItem('tts_rate'));
        if (savedRate && savedRate >= 0.5 && savedRate <= 2.5) {
            state.rate = savedRate;
            speedLabel.textContent = state.rate.toFixed(1) + '×';
        }

        bindSidebarLinks();

        if ('mediaSession' in navigator) {
            navigator.mediaSession.setActionHandler('play', () => audioEl.play());
            navigator.mediaSession.setActionHandler('pause', () => audioEl.pause());
            navigator.mediaSession.setActionHandler('seekbackward', () => seekBy(-15));
            navigator.mediaSession.setActionHandler('seekforward', () => seekBy(15));
        }

        document.addEventListener('keydown', e => {
            if (e.altKey && e.key === 'n') { e.preventDefault(); if (state.isOpen) togglePlay(); }
            if (e.altKey && e.key === 'r') { e.preventDefault(); toggleBar(); }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
