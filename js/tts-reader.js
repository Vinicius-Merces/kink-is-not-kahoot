/**
 * TTS Reader — Web Speech API narrator for trilha pages
 * Engine is abstracted: swap synthEngine for Piper WASM without touching UI
 */
(function () {
    'use strict';

    if (!window.speechSynthesis) return; // browser doesn't support TTS

    // ── State ────────────────────────────────────────────────────────────────
    const state = {
        isOpen: false,
        isPlaying: false,
        isPaused: false,
        rate: 1.0,
        selectedVoiceURI: null,
        paragraphs: [],       // NodeList of readable elements in current chapter
        currentIdx: 0,
        chapterTitle: '',
        chapterId: null,
    };

    // ── DOM ──────────────────────────────────────────────────────────────────
    let bar, triggerBtn, playBtn, stopBtn, prevBtn, nextBtn,
        progressFill, progressInfo, chapterLabel, voiceSelect,
        speedLabel;

    function buildUI() {
        // Trigger pill (always visible)
        triggerBtn = document.createElement('button');
        triggerBtn.className = 'tts-trigger-btn';
        triggerBtn.setAttribute('aria-label', 'Narrar capítulo');
        triggerBtn.innerHTML = '🎧 <span>Narrar</span>';
        document.body.appendChild(triggerBtn);

        // Bottom bar
        bar = document.createElement('div');
        bar.className = 'tts-bar';
        bar.setAttribute('role', 'region');
        bar.setAttribute('aria-label', 'Narrador de texto');
        bar.innerHTML = `
          <div class="tts-bar-inner">
            <span class="tts-chapter-label" id="ttsChapterLabel">—</span>

            <div class="tts-progress-wrap">
              <div class="tts-progress-bar" title="Progresso da leitura">
                <div class="tts-progress-fill" id="ttsProgressFill"></div>
              </div>
              <span class="tts-progress-info" id="ttsProgressInfo">0 / 0</span>
            </div>

            <div class="tts-controls">
              <button class="tts-btn" id="ttsPrevBtn" title="Parágrafo anterior" aria-label="Parágrafo anterior">⏮</button>
              <button class="tts-btn tts-btn-play" id="ttsPlayBtn" title="Play / Pausar" aria-label="Play">▶</button>
              <button class="tts-btn" id="ttsStopBtn" title="Parar" aria-label="Parar">⏹</button>
              <button class="tts-btn" id="ttsNextBtn" title="Próximo parágrafo" aria-label="Próximo parágrafo">⏭</button>
            </div>

            <div class="tts-speed-group">
              <button class="tts-speed-btn" id="ttsSlowerBtn" title="Mais lento">−</button>
              <span class="tts-speed-label" id="ttsSpeedLabel">1.0×</span>
              <button class="tts-speed-btn" id="ttsFasterBtn" title="Mais rápido">+</button>
            </div>

            <select class="tts-voice-select" id="ttsVoiceSelect" aria-label="Voz do narrador"></select>

            <button class="tts-btn tts-btn-close" id="ttsCloseBtn" title="Fechar narrador" aria-label="Fechar narrador">✕</button>
          </div>
        `;
        document.body.appendChild(bar);

        // Cache refs
        playBtn       = document.getElementById('ttsPlayBtn');
        stopBtn       = document.getElementById('ttsStopBtn');
        prevBtn       = document.getElementById('ttsPrevBtn');
        nextBtn       = document.getElementById('ttsNextBtn');
        progressFill  = document.getElementById('ttsProgressFill');
        progressInfo  = document.getElementById('ttsProgressInfo');
        chapterLabel  = document.getElementById('ttsChapterLabel');
        voiceSelect   = document.getElementById('ttsVoiceSelect');
        speedLabel    = document.getElementById('ttsSpeedLabel');

        // Event listeners
        triggerBtn.addEventListener('click', toggleBar);
        document.getElementById('ttsCloseBtn').addEventListener('click', closeBar);
        playBtn.addEventListener('click', togglePlay);
        stopBtn.addEventListener('click', stopReading);
        prevBtn.addEventListener('click', () => jump(-1));
        nextBtn.addEventListener('click', () => jump(1));
        document.getElementById('ttsSlowerBtn').addEventListener('click', () => changeSpeed(-0.25));
        document.getElementById('ttsFasterBtn').addEventListener('click', () => changeSpeed(+0.25));
        voiceSelect.addEventListener('change', () => {
            state.selectedVoiceURI = voiceSelect.value;
            if (state.isPlaying) { stopReading(); startReading(); }
        });
    }

    // ── Voices ───────────────────────────────────────────────────────────────
    function populateVoices() {
        const voices = window.speechSynthesis.getVoices();
        if (!voices.length) return;

        voiceSelect.innerHTML = '';

        // Score function: prefer pt-BR, then pt, then any
        const scored = voices.map(v => {
            let score = 0;
            const lang = v.lang.toLowerCase();
            if (lang === 'pt-br') score = 100;
            else if (lang.startsWith('pt')) score = 80;
            if (v.localService) score += 5;
            if (/francisca|luciana|antonio|camila|leila/i.test(v.name)) score += 20;
            return { v, score };
        }).sort((a, b) => b.score - a.score);

        scored.forEach(({ v }) => {
            const opt = document.createElement('option');
            opt.value = v.voiceURI;
            opt.textContent = `${v.name} (${v.lang})`;
            voiceSelect.appendChild(opt);
        });

        // Restore saved or use best
        const saved = localStorage.getItem('tts_voice');
        const match = saved && voices.find(v => v.voiceURI === saved);
        if (match) voiceSelect.value = match.voiceURI;
        state.selectedVoiceURI = voiceSelect.value;

        // Save preference on change
        voiceSelect.addEventListener('change', () => {
            localStorage.setItem('tts_voice', voiceSelect.value);
        });
    }

    // ── Chapter detection ────────────────────────────────────────────────────
    function detectCurrentChapter() {
        // Use Intersection Observer result if available, else first visible chapter
        const chapters = Array.from(document.querySelectorAll('.trilha-chapter'));
        if (!chapters.length) return null;

        // Find chapter most visible in viewport
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
        state.chapterId = chapter.id;

        // Title from the h2 inside chapter header
        const h2 = chapter.querySelector('.trilha-chapter-header h2');
        state.chapterTitle = h2 ? h2.textContent.trim() : chapter.id;

        // Collect readable elements (exclude code blocks, buttons, qa-question btns)
        const sel = 'h2, h3, p, li:not(.lab-step), td, .qa-answer, .callout-body';
        state.paragraphs = Array.from(chapter.querySelectorAll(sel)).filter(el => {
            if (el.closest('.code-block')) return false;
            if (el.tagName === 'BUTTON') return false;
            if (!el.textContent.trim()) return false;
            return true;
        });

        state.currentIdx = 0;
        chapterLabel.textContent = state.chapterTitle.substring(0, 30);
        updateProgress();
    }

    // ── Read engine (Web Speech API) ─────────────────────────────────────────
    function getCurrentVoice() {
        const voices = window.speechSynthesis.getVoices();
        return voices.find(v => v.voiceURI === state.selectedVoiceURI) || voices[0];
    }

    function speakElement(el) {
        window.speechSynthesis.cancel();

        const text = el.textContent.replace(/\s+/g, ' ').trim();
        if (!text) { advance(); return; }

        // Highlight
        clearHighlight();
        el.classList.add('tts-reading');
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });

        const utter = new SpeechSynthesisUtterance(text);
        utter.voice = getCurrentVoice();
        utter.lang  = 'pt-BR';
        utter.rate  = state.rate;

        utter.onend = () => {
            if (state.isPlaying && !state.isPaused) advance();
        };
        utter.onerror = (e) => {
            if (e.error !== 'interrupted') advance();
        };

        window.speechSynthesis.speak(utter);
    }

    function advance() {
        state.currentIdx++;
        if (state.currentIdx >= state.paragraphs.length) {
            stopReading();
            return;
        }
        updateProgress();
        speakElement(state.paragraphs[state.currentIdx]);
    }

    function startReading() {
        if (!state.paragraphs.length) {
            loadChapter(detectCurrentChapter());
        }
        if (!state.paragraphs.length) return;

        state.isPlaying = true;
        state.isPaused  = false;
        playBtn.textContent = '⏸';
        playBtn.setAttribute('aria-label', 'Pausar');
        triggerBtn.classList.add('tts-active');

        speakElement(state.paragraphs[state.currentIdx]);
        updateProgress();
    }

    function pauseReading() {
        state.isPaused = true;
        state.isPlaying = false;
        window.speechSynthesis.pause();
        playBtn.textContent = '▶';
        playBtn.setAttribute('aria-label', 'Continuar');
    }

    function resumeReading() {
        state.isPlaying = true;
        state.isPaused  = false;
        window.speechSynthesis.resume();
        // If synthesis already ended during pause, restart current
        if (!window.speechSynthesis.speaking) {
            speakElement(state.paragraphs[state.currentIdx]);
        }
        playBtn.textContent = '⏸';
        playBtn.setAttribute('aria-label', 'Pausar');
    }

    function stopReading() {
        window.speechSynthesis.cancel();
        state.isPlaying = false;
        state.isPaused  = false;
        state.currentIdx = 0;
        playBtn.textContent = '▶';
        playBtn.setAttribute('aria-label', 'Play');
        triggerBtn.classList.remove('tts-active');
        clearHighlight();
        updateProgress();
    }

    function togglePlay() {
        if (state.isPlaying) {
            pauseReading();
        } else if (state.isPaused) {
            resumeReading();
        } else {
            startReading();
        }
    }

    function jump(delta) {
        window.speechSynthesis.cancel();
        state.currentIdx = Math.max(0, Math.min(state.paragraphs.length - 1, state.currentIdx + delta));
        updateProgress();
        if (state.isPlaying || state.isPaused) {
            state.isPlaying = true;
            state.isPaused  = false;
            playBtn.textContent = '⏸';
            speakElement(state.paragraphs[state.currentIdx]);
        } else {
            clearHighlight();
            const el = state.paragraphs[state.currentIdx];
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function changeSpeed(delta) {
        state.rate = Math.min(2.5, Math.max(0.5, +(state.rate + delta).toFixed(2)));
        speedLabel.textContent = state.rate.toFixed(1) + '×';
        localStorage.setItem('tts_rate', state.rate);
        // Apply immediately if playing
        if (state.isPlaying) {
            const idx = state.currentIdx;
            stopReading();
            state.currentIdx = idx;
            startReading();
        }
    }

    // ── Progress UI ───────────────────────────────────────────────────────────
    function updateProgress() {
        const total = state.paragraphs.length;
        const cur   = total ? state.currentIdx + 1 : 0;
        const pct   = total ? (state.currentIdx / total) * 100 : 0;
        progressFill.style.width = pct + '%';
        progressInfo.textContent = `${cur} / ${total}`;
    }

    function clearHighlight() {
        document.querySelectorAll('.tts-reading').forEach(el => el.classList.remove('tts-reading'));
    }

    // ── Bar open/close ────────────────────────────────────────────────────────
    function openBar() {
        state.isOpen = true;
        bar.classList.add('tts-open');
        triggerBtn.classList.add('tts-active');
        document.body.classList.add('tts-bar-open');

        // Load chapter on open
        const chapter = detectCurrentChapter();
        if (chapter && chapter.id !== state.chapterId) {
            stopReading();
            loadChapter(chapter);
        }
    }

    function closeBar() {
        state.isOpen = false;
        bar.classList.remove('tts-open');
        document.body.classList.remove('tts-bar-open');
        if (!state.isPlaying) triggerBtn.classList.remove('tts-active');
        stopReading();
    }

    function toggleBar() {
        if (state.isOpen) closeBar(); else openBar();
    }

    // ── Sidebar chapter link click → reload chapter ───────────────────────────
    function bindSidebarLinks() {
        document.querySelectorAll('.trilha-sidebar a[href^="#cap"]').forEach(link => {
            link.addEventListener('click', () => {
                setTimeout(() => {
                    const id = link.getAttribute('href').slice(1);
                    const ch = document.getElementById(id);
                    if (ch && ch.id !== state.chapterId) {
                        stopReading();
                        loadChapter(ch);
                        if (state.isOpen) startReading();
                    }
                }, 200);
            });
        });
    }

    // ── Init ──────────────────────────────────────────────────────────────────
    function init() {
        buildUI();

        // Voices load async in many browsers
        if (window.speechSynthesis.onvoiceschanged !== undefined) {
            window.speechSynthesis.onvoiceschanged = populateVoices;
        }
        populateVoices();

        // Restore speed
        const savedRate = parseFloat(localStorage.getItem('tts_rate'));
        if (savedRate && savedRate >= 0.5 && savedRate <= 2.5) {
            state.rate = savedRate;
            if (speedLabel) speedLabel.textContent = state.rate.toFixed(1) + '×';
        }

        bindSidebarLinks();

        // Keyboard shortcut: Alt+N to toggle play
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
