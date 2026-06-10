// Music Player KINK - VERSÃO MELHORADA 2.1
// Visual intuitivo + Funcionalidades expandidas
// Mantém separação de playlists (Menu vs Game)

class MusicPlayer {
    constructor() {
        this.audio = new Audio();
        this.currentTrackIndex = 0;
        this.isPlaying = false;
        this.isMuted = false;
        this.volume = 0.6;
        this.lastVolume = 0.6;
        this.currentTime = 0;
        this.duration = 0;
        this.playlist = [];
        this.currentPlaylist = [];
        this.playlistType = 'menu';
        this.isMinimized = true;
        this.init();
    }

    init() {
        this.detectPageType();
        this.loadPlaylist();
        this.setupAudioEvents();
        this.createPlayerUI();
        this.setupKeyboardShortcuts();
        this.setupAutoPlay();
    }

    detectPageType() {
        const path = window.location.pathname.toLowerCase();
        if (path.includes('host.html') || path.includes('player.html')) {
            this.playlistType = 'game';
        } else if (path.includes('simulados.html') || path.includes('historico.html')) {
            this.playlistType = 'simulado';
        } else {
            this.playlistType = 'menu';
        }
        console.log(`🎵 MusicPlayer: Modo ${this.playlistType} detectado`);
    }

    loadPlaylist() {
        const menuPlaylist = [
            { id: 'menu1', title: 'KINK Theme', artist: 'KINK Original', url: '/assets/music/Index/KINK - Ta pronto pro jogo.mp3', cover: '🎵', duration: '2:34' },
            { id: 'menu2', title: 'Rebel Rhythm', artist: 'KINK Original', url: '/assets/music/Index/KINK - EletroVibe.mp3', cover: '⚡', duration: '2:09' },
            { id: 'menu3', title: 'Yeah! KINK', artist: 'KINK Original', url: '/assets/music/Index/KINK - Yeah!.mp3', cover: '⚛️', duration: '2:24' },
            { id: 'menu4', title: 'Just KINK', artist: 'KINK Original', url: '/assets/music/Index/KINK - Pulsating Vibe.mp3', cover: '⚛️', duration: '2:13' }
        ];
        const gamePlaylist = [
            { id: 'game1', title: 'Epic Tension', artist: 'KINK Original', url: '/assets/music/instrumental/KINK - Play! 2.mp3', cover: '⚡', duration: '2:51' },
            { id: 'game2', title: 'Quiz Pulse', artist: 'KINK Original', url: '/assets/music/instrumental/KINK - Quiz Lobby Cipher 2.mp3', cover: '🎯', duration: '2:16' },
            { id: 'game3', title: 'Background Lo-Fi', artist: 'KINK Original', url: '/assets/music/instrumental/KINK - Lofi Session.mp3', cover: '🎷🎼', duration: '2:08' },
            { id: 'game4', title: 'Quizz Lo-Fi', artist: 'KINK Original', url: '/assets/music/instrumental/KINK - Lofi Session 2.mp3', cover: '🎹🎸', duration: '1:48' },
            { id: 'game5', title: 'Epic Suspense', artist: 'KINK Original', url: '/assets/music/instrumental/KINK - Dark drama.mp3', cover: '🎹', duration: '1:50' },
            { id: 'game6', title: 'Epic Answers', artist: 'KINK Original', url: '/assets/music/instrumental/KINK - Play!.mp3', cover: '☯️', duration: '2:42' },
            { id: 'game7', title: 'KINK Drama', artist: 'KINK Original', url: '/assets/music/instrumental/KINK - Dark drama 2.mp3', cover: '⚛️', duration: '2:14' },
            { id: 'game8', title: 'Be KINK', artist: 'KINK Original', url: '/assets/music/instrumental/KINK - Quiz Lobby Cipher.mp3', cover: '🪯', duration: '1:36' }
        ];
        // Simulados usam a mesma trilha instrumental/calma do modo jogo
        this.currentPlaylist = (this.playlistType === 'game' || this.playlistType === 'simulado') ? gamePlaylist : menuPlaylist;

        const savedVolume = localStorage.getItem('kink_volume');
        if (savedVolume !== null) {
            this.volume = parseFloat(savedVolume);
            this.audio.volume = this.volume;
        }

        const lastTrackKey = `kink_last_track_${this.playlistType}`;
        const lastTrack = localStorage.getItem(lastTrackKey);
        this.currentTrackIndex = (lastTrack !== null && lastTrack < this.currentPlaylist.length) ? parseInt(lastTrack) : 0;
    }

    getModeBadgeText() {
        if (this.playlistType === 'game') return '🎮 Jogo';
        if (this.playlistType === 'simulado') return '🎓 Simulado';
        return '🎵 Menu';
    }

    getPlaylistTitleText() {
        if (this.playlistType === 'game') return '🎮 Playlist de Jogo';
        if (this.playlistType === 'simulado') return '🎓 Playlist de Estudo';
        return '🎵 Playlist KINK';
    }

    setupAudioEvents() {
        this.audio.addEventListener('ended', () => this.nextTrack());
        this.audio.addEventListener('timeupdate', () => this.updateProgress());
        this.audio.addEventListener('loadedmetadata', () => {
            this.duration = this.audio.duration;
            this.updateDuration();
        });
        this.audio.addEventListener('play', () => localStorage.setItem('kink_was_playing', 'true'));
        this.audio.addEventListener('pause', () => localStorage.setItem('kink_was_playing', 'false'));
    }

    setupAutoPlay() {
        this.loadTrack(this.currentTrackIndex);
        this.audio.play().then(() => {
            this.isPlaying = true;
            this.updatePlayButton();
        }).catch(() => {
            console.log('🎵 Auto-play bloqueado. Aguardando interação...');
            const startOnClick = () => {
                this.play();
                document.removeEventListener('click', startOnClick);
                document.removeEventListener('touchstart', startOnClick);
            };
            document.addEventListener('click', startOnClick);
            document.addEventListener('touchstart', startOnClick);
        });
    }

    updatePlayButton() {
        const playPauseBtn = document.getElementById('playPauseBtn');
        const player = document.getElementById('kinkMusicPlayer');
        if (playPauseBtn) playPauseBtn.innerHTML = this.isPlaying ? '⏸️' : '▶️';
        if (player) {
            if (this.isPlaying) {
                player.classList.remove('paused');
                player.classList.add('playing');
            } else {
                player.classList.remove('playing');
                player.classList.add('paused');
            }
        }
    }

    createPlayerUI() {
        if (document.getElementById('kinkMusicPlayer')) return;

        const playerHTML = `
            <div id="kinkMusicPlayer" class="music-player-v2 ${this.isPlaying ? 'playing' : 'paused'}">
                <!-- PLAYER EXPANDIDO -->
                <div class="player-expanded" id="playerExpanded" style="display: ${this.isMinimized ? 'none' : 'flex'};">
                    <!-- Cabeçalho -->
                    <div class="player-header">
                        <div class="player-mode-badge">${this.getModeBadgeText()}</div>
                        <button id="minimizeBtn" class="minimize-btn" title="Minimizar (M)">−</button>
                    </div>

                    <!-- Capa da música -->
                    <div class="player-artwork">
                        <div class="artwork-emoji" id="artworkEmoji">🎵</div>
                        <div class="artwork-animation"></div>
                    </div>

                    <!-- Informações da track -->
                    <div class="player-track-info">
                        <h3 class="track-title" id="currentTitle">Carregando...</h3>
                        <p class="track-artist" id="currentArtist">KINK Music</p>
                    </div>

                    <!-- Barra de progresso -->
                    <div class="player-progress-section">
                        <div class="progress-time" id="currentTime">0:00</div>
                        <input type="range" id="progressBar" class="progress-bar" min="0" max="100" value="0">
                        <div class="progress-time" id="totalDuration">0:00</div>
                    </div>

                    <!-- Controles principais -->
                    <div class="player-controls-main">
                        <button id="prevBtn" class="control-btn" title="Anterior (←)">⏮️</button>
                        <button id="playPauseBtn" class="control-btn play-pause" title="Play/Pause (Espaço)">▶️</button>
                        <button id="nextBtn" class="control-btn" title="Próxima (→)">⏭️</button>
                    </div>

                    <!-- Volume e outras funções -->
                    <div class="player-controls-secondary">
                        <div class="volume-control">
                            <span class="volume-icon" id="volumeIcon">🔊</span>
                            <input type="range" id="volumeSlider" class="volume-slider" min="0" max="1" step="0.01" value="${this.volume}">
                        </div>
                        <div class="secondary-buttons">
                            <button id="repeatBtn" class="secondary-btn" title="Repetição">🔁</button>
                            <button id="playlistBtn" class="secondary-btn" title="Playlist">📋</button>
                        </div>
                    </div>
                </div>

                <!-- PLAYER MINIMIZADO -->
                <div class="player-minimized" id="playerMinimized" style="display: ${this.isMinimized ? 'flex' : 'none'};">
                    <div class="minimized-icon" id="minimizedIcon">🎵</div>
                    <div class="minimized-info">
                        <div class="minimized-title" id="minimizedTitle">Carregando...</div>
                        <div class="minimized-time" id="minimizedTime">0:00 / 0:00</div>
                    </div>
                    <button id="minimizedPlayPause" class="minimized-play">▶️</button>
                    <button id="expandBtn" class="expand-btn" title="Expandir">+</button>
                </div>

                <!-- PAINEL DE PLAYLIST -->
                <div id="playlistPanel" class="playlist-panel" style="display: none;">
                    <div class="playlist-header">
                        <h4>${this.getPlaylistTitleText()}</h4>
                        <button class="playlist-close" id="closePlaylist">✕</button>
                    </div>
                    <div class="playlist-list" id="playlistList"></div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', playerHTML);
        this.bindEvents();
        this.renderPlaylist();
        this.loadTrack(this.currentTrackIndex);
    }

    bindEvents() {
        // Controles principais
        const playPauseBtn = document.getElementById('playPauseBtn');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const playlistBtn = document.getElementById('playlistBtn');
        const closePlaylist = document.getElementById('closePlaylist');
        const volumeSlider = document.getElementById('volumeSlider');
        const volumeIcon = document.getElementById('volumeIcon');
        const minimizeBtn = document.getElementById('minimizeBtn');
        const expandBtn = document.getElementById('expandBtn');
        const progressBar = document.getElementById('progressBar');
        const repeatBtn = document.getElementById('repeatBtn');

        // Minimizado
        const minimizedPlayPause = document.getElementById('minimizedPlayPause');

        // Evento cliques
        if (playPauseBtn) playPauseBtn.addEventListener('click', () => this.togglePlay());
        if (prevBtn) prevBtn.addEventListener('click', () => this.prevTrack());
        if (nextBtn) nextBtn.addEventListener('click', () => this.nextTrack());
        if (playlistBtn) playlistBtn.addEventListener('click', () => this.togglePlaylist());
        if (closePlaylist) closePlaylist.addEventListener('click', () => this.togglePlaylist(false));
        if (volumeSlider) volumeSlider.addEventListener('input', (e) => this.setVolume(e.target.value));
        if (volumeIcon) volumeIcon.addEventListener('click', () => this.toggleMute());
        if (minimizeBtn) minimizeBtn.addEventListener('click', () => this.toggleMinimize());
        if (expandBtn) expandBtn.addEventListener('click', () => this.toggleMinimize());
        if (progressBar) progressBar.addEventListener('input', (e) => this.seek(e.target.value));
        if (repeatBtn) repeatBtn.addEventListener('click', () => this.toggleRepeat());
        if (minimizedPlayPause) minimizedPlayPause.addEventListener('click', () => this.togglePlay());

        // Fechar playlist ao clicar fora
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('playlistPanel');
            const btn = document.getElementById('playlistBtn');
            if (panel && btn && !panel.contains(e.target) && !btn.contains(e.target)) {
                this.togglePlaylist(false);
            }
        });
    }

    renderPlaylist() {
        const playlistList = document.getElementById('playlistList');
        if (!playlistList) return;
        
        playlistList.innerHTML = this.currentPlaylist.map((track, index) => `
            <div class="playlist-item ${index === this.currentTrackIndex ? 'active' : ''}" data-index="${index}">
                <div class="playlist-index">${String(index + 1).padStart(2, '0')}</div>
                <div class="playlist-item-cover">${track.cover || '🎵'}</div>
                <div class="playlist-item-info">
                    <div class="playlist-item-title">${track.title}</div>
                    <div class="playlist-item-artist">${track.artist}</div>
                </div>
                <div class="playlist-item-duration">${track.duration || '--:--'}</div>
            </div>
        `).join('');

        document.querySelectorAll('.playlist-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.playTrack(index);
                this.togglePlaylist(false);
            });
        });
    }

    loadTrack(index) {
        if (!this.currentPlaylist[index]) return;
        const track = this.currentPlaylist[index];
        this.currentTrackIndex = index;
        this.audio.src = track.url;
        this.audio.load();

        // Atualizar UI expandida
        document.getElementById('currentTitle').textContent = track.title;
        document.getElementById('currentArtist').textContent = track.artist || 'KINK';
        document.getElementById('artworkEmoji').textContent = track.cover || '🎵';

        // Atualizar UI minimizada
        document.getElementById('minimizedTitle').textContent = track.title;
        document.getElementById('minimizedIcon').textContent = track.cover || '🎵';

        localStorage.setItem(`kink_last_track_${this.playlistType}`, index);
        this.renderPlaylist();
        
        if (this.isPlaying) {
            this.audio.play().catch(() => {});
        }
    }

    playTrack(index) {
        this.loadTrack(index);
        this.play();
    }

    togglePlay() {
        this.isPlaying ? this.pause() : this.play();
    }

    play() {
        this.audio.play().then(() => {
            this.isPlaying = true;
            this.updatePlayButton();
            localStorage.setItem('kink_was_playing', 'true');
        }).catch(e => console.log('Erro ao reproduzir:', e));
    }

    pause() {
        this.audio.pause();
        this.isPlaying = false;
        this.updatePlayButton();
        localStorage.setItem('kink_was_playing', 'false');
    }

    nextTrack() {
        let next = this.currentTrackIndex + 1;
        if (next >= this.currentPlaylist.length) next = 0;
        this.playTrack(next);
    }

    prevTrack() {
        let prev = this.currentTrackIndex - 1;
        if (prev < 0) prev = this.currentPlaylist.length - 1;
        this.playTrack(prev);
    }

    setVolume(value) {
        this.volume = parseFloat(value);
        this.audio.volume = this.volume;
        this.isMuted = this.volume === 0;
        localStorage.setItem('kink_volume', this.volume);
        this.updateVolumeIcon();
    }

    updateVolumeIcon() {
        const volumeIcon = document.getElementById('volumeIcon');
        if (volumeIcon) {
            if (this.volume === 0) volumeIcon.textContent = '🔇';
            else if (this.volume < 0.3) volumeIcon.textContent = '🔈';
            else if (this.volume < 0.7) volumeIcon.textContent = '🔉';
            else volumeIcon.textContent = '🔊';
        }
    }

    toggleMute() {
        if (this.volume > 0) {
            this.lastVolume = this.volume;
            this.setVolume(0);
        } else {
            this.setVolume(this.lastVolume || 0.5);
            document.getElementById('volumeSlider').value = this.lastVolume || 0.5;
        }
    }

    seek(percent) {
        const duration = this.audio.duration;
        if (duration) {
            this.audio.currentTime = (percent / 100) * duration;
        }
    }

    updateProgress() {
        this.currentTime = this.audio.currentTime;
        const duration = this.audio.duration || 0;
        const progressPercent = duration ? (this.currentTime / duration) * 100 : 0;

        document.getElementById('progressBar').value = progressPercent;
        document.getElementById('currentTime').textContent = this.formatTime(this.currentTime);
        document.getElementById('minimizedTime').textContent = `${this.formatTime(this.currentTime)} / ${this.formatTime(duration)}`;
    }

    updateDuration() {
        const duration = this.audio.duration || 0;
        document.getElementById('totalDuration').textContent = this.formatTime(duration);
    }

    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${String(secs).padStart(2, '0')}`;
    }

    togglePlaylist(show) {
        const panel = document.getElementById('playlistPanel');
        if (panel) {
            if (show === undefined) panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
            else panel.style.display = show ? 'block' : 'none';
        }
    }

    toggleMinimize() {
        this.isMinimized = !this.isMinimized;
        const expanded = document.getElementById('playerExpanded');
        const minimized = document.getElementById('playerMinimized');

        if (expanded && minimized) {
            expanded.style.display = this.isMinimized ? 'none' : 'flex';
            minimized.style.display = this.isMinimized ? 'flex' : 'none';
        }
    }

    toggleRepeat() {
        // Placeholder para adicionar funcionalidade de repetição
        const repeatBtn = document.getElementById('repeatBtn');
        if (repeatBtn) {
            repeatBtn.classList.toggle('active');
            console.log('🔁 Repetição alternada');
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            switch(e.key) {
                case ' ': 
                    e.preventDefault(); 
                    this.togglePlay(); 
                    break;
                case 'ArrowRight': 
                    e.preventDefault(); 
                    this.nextTrack(); 
                    break;
                case 'ArrowLeft': 
                    e.preventDefault(); 
                    this.prevTrack(); 
                    break;
                case 'ArrowUp': 
                    e.preventDefault(); 
                    this.setVolume(Math.min(1, this.volume + 0.1));
                    document.getElementById('volumeSlider').value = Math.min(1, this.volume + 0.1);
                    break;
                case 'ArrowDown': 
                    e.preventDefault(); 
                    this.setVolume(Math.max(0, this.volume - 0.1));
                    document.getElementById('volumeSlider').value = Math.max(0, this.volume - 0.1);
                    break;
                case 'm':
                case 'M':
                    this.toggleMinimize();
                    break;
            }
        });
    }

    reloadPlaylist() {
        this.detectPageType();
        this.loadPlaylist();
        this.currentTrackIndex = 0;
        this.loadTrack(0);
        this.renderPlaylist();
        const playlistHeader = document.querySelector('#playlistPanel h4');
        if (playlistHeader) {
            playlistHeader.textContent = this.getPlaylistTitleText();
        }
        const modeBadge = document.querySelector('.player-mode-badge');
        if (modeBadge) {
            modeBadge.textContent = this.getModeBadgeText();
        }
    }
}

// Inicializar quando DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        window.musicPlayer = new MusicPlayer();
    }, 200);
});
