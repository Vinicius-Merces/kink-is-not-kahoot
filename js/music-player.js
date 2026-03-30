// Music Player - KINK Style (Playlists Separadas por Página)
class MusicPlayer {
    constructor() {
        this.audio = new Audio();
        this.currentTrackIndex = 0;
        this.isPlaying = false;
        this.volume = 0.6;
        this.currentPlaylist = [];
        this.playlistType = 'menu'; // 'menu' ou 'game'
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

    // Detecta qual página estamos para escolher a playlist certa
    detectPageType() {
        const path = window.location.pathname.toLowerCase();
        
        if (path.includes('host.html') || path.includes('player.html')) {
            this.playlistType = 'game';     // Instrumental durante o jogo
        } else {
            this.playlistType = 'menu';     // Playlist normal na tela inicial
        }
        
        console.log(`🎵 MusicPlayer: Modo ${this.playlistType} detectado`);
    }

    loadPlaylist() {
        // Playlist Menu (Tela inicial - mais energética)
        const menuPlaylist = [
            {
                id: 'menu1',
                title: 'KINK Theme',
                artist: 'KINK Original',
                url: '/assets/music/Index/KINK - Ta pronto pro jogo.mp3',
                cover: '🎵',
                duration: '2:34'
            },
            {
                id: 'menu2',
                title: 'Rebel Rhythm',
                artist: 'KINK Original',
                url: '/assets/music/Index/KINK - EletroVibe.mp3',
                cover: '⚡',
                duration: '2:09'
            },
            {
                id: 'menu3',
                title: 'Yeah! KINK',
                artist: 'KINK Original',
                url: '/assets/music/Index/KINK - Yeah!.mp3',
                cover: '⚛️',
                duration: '2:24'
            },
            {
                id: 'menu4',
                title: 'Just KINK',
                artist: 'KINK Original',
                url: '/assets/music/Index/KINK - Pulsating Vibe.mp3',
                cover: '⚛️',
                duration: '2:13'
            },
            // Adicione mais músicas "com vocais" aqui se quiser
        ];

        // Playlist Game (Host + Player) - Instrumental recomendada
        const gamePlaylist = [
            {
                id: 'game1',
                title: 'Epic Tension',
                artist: 'KINK Original',
                url: '/assets/music/instrumental/KINK - Play! 2.mp3',   // ← coloque suas músicas instrumentais aqui
                cover: '⚡',
                duration: '2:51'
            },
            {
                id: 'game2',
                title: 'Quiz Pulse',
                artist: 'KINK Original',
                url: '/assets/music/instrumental/KINK - Quiz Lobby Cipher 2.mp3',
                cover: '🎯',
                duration: '2:16'
            },
            {
                id: 'game3',
                title: 'Background Lo-Fi',
                artist: 'KINK Original',
                url: '/assets/music/instrumental/KINK - Lofi Session.mp3',
                cover: '🎷🎼',
                duration: '2:08'
            },
            {
                id: 'game4',
                title: 'Quizz Lo-Fi',
                artist: 'KINK Original',
                url: '/assets/music/instrumental/KINK - Lofi Session 2.mp3',
                cover: '🎹🎸',
                duration: '1:48'
            },
            {
                id: 'game5',
                title: 'Epic Suspense',
                artist: 'KINK Original',
                url: '/assets/music/instrumental/KINK - Dark drama.mp3',
                cover: '🎹',
                duration: '1:50'
            },
            {
                id: 'game6',
                title: 'Epic Answers',
                artist: 'KINK Original',
                url: '/assets/music/instrumental/KINK - Play!.mp3',
                cover: '☯️',
                duration: '2:42'
            },
            {
                id: 'game7',
                title: 'KINK Drama',
                artist: 'KINK Original',
                url: '/assets/music/instrumental/KINK - Dark drama 2.mp3',
                cover: '⚛️',
                duration: '2:14'
            },
            {
                id: 'game8',
                title: 'Be KINK',
                artist: 'KINK Original',
                url: '/assets/music/instrumental/KINK - Quiz Lobby Cipher.mp3',
                cover: '🪯',
                duration: '1:36'
            }
            // Adicione quantas quiser
        ];

        this.currentPlaylist = (this.playlistType === 'game') ? gamePlaylist : menuPlaylist;

        // Carregar volume salvo
        const savedVolume = localStorage.getItem('kink_volume');
        if (savedVolume !== null) {
            this.volume = parseFloat(savedVolume);
            this.audio.volume = this.volume;
        }

        // Carregar última faixa (por tipo de playlist)
        const lastTrackKey = `kink_last_track_${this.playlistType}`;
        const lastTrack = localStorage.getItem(lastTrackKey);
        if (lastTrack !== null) {
            this.currentTrackIndex = parseInt(lastTrack);
        }
    }

    setupAudioEvents() {
        this.audio.addEventListener('ended', () => this.nextTrack());
        this.audio.addEventListener('timeupdate', () => this.updateProgress());
        this.audio.addEventListener('loadedmetadata', () => this.updateDuration());
    }

    createPlayerUI() {
        if (document.getElementById('kinkMusicPlayer')) return;

        const playerHTML = `
            <div id="kinkMusicPlayer" class="music-player">
                <div class="player-toggle" id="playerToggle">
                    <div class="player-icon" id="playPauseBtn">▶️</div>
                    <div class="player-info">
                        <div class="player-title" id="currentTitle">Carregando...</div>
                        <div class="player-artist" id="currentArtist">KINK Music</div>
                    </div>
                    <div class="player-controls">
                        <button id="prevBtn" title="Anterior">⏮️</button>
                        <button id="nextBtn" title="Próxima">⏭️</button>
                        <button id="playlistBtn" title="Playlist">📋</button>
                    </div>
                    <div class="player-volume">
                        <span class="player-volume-icon" id="volumeIcon">🔊</span>
                        <input type="range" id="volumeSlider" min="0" max="1" step="0.01" value="${this.volume}">
                    </div>
                </div>
                
                <div id="playlistPanel" class="playlist-panel">
                    <div class="playlist-header">
                        <h4>${this.playlistType === 'game' ? 'Música de Jogo (Instrumental)' : 'Playlist KINK'}</h4>
                        <span class="playlist-close" id="closePlaylist">✕</span>
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
        const playPauseBtn = document.getElementById('playPauseBtn');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const playlistBtn = document.getElementById('playlistBtn');
        const closePlaylist = document.getElementById('closePlaylist');
        const volumeSlider = document.getElementById('volumeSlider');

        if (playPauseBtn) playPauseBtn.addEventListener('click', () => this.togglePlay());
        if (prevBtn) prevBtn.addEventListener('click', () => this.prevTrack());
        if (nextBtn) nextBtn.addEventListener('click', () => this.nextTrack());
        if (playlistBtn) playlistBtn.addEventListener('click', () => this.togglePlaylist());
        if (closePlaylist) closePlaylist.addEventListener('click', () => this.togglePlaylist(false));
        if (volumeSlider) volumeSlider.addEventListener('input', (e) => this.setVolume(e.target.value));
    }

    renderPlaylist() {
        const playlistList = document.getElementById('playlistList');
        if (!playlistList) return;

        playlistList.innerHTML = this.currentPlaylist.map((track, index) => `
            <div class="playlist-item ${index === this.currentTrackIndex ? 'active' : ''}" data-index="${index}">
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
            });
        });
    }

    loadTrack(index) {
        if (!this.currentPlaylist[index]) return;
        
        const track = this.currentPlaylist[index];
        this.currentTrackIndex = index;
        this.audio.src = track.url;
        this.audio.load();

        document.getElementById('currentTitle').textContent = track.title;
        document.getElementById('currentArtist').textContent = track.artist;

        // Salvar última faixa por tipo de playlist
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
            document.getElementById('playPauseBtn').innerHTML = '⏸️';
        }).catch(e => console.log('Playback bloqueado:', e));
    }

    pause() {
        this.audio.pause();
        this.isPlaying = false;
        document.getElementById('playPauseBtn').innerHTML = '▶️';
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
        localStorage.setItem('kink_volume', this.volume);
    }

    togglePlaylist(show) {
        const panel = document.getElementById('playlistPanel');
        if (panel) {
            show === undefined ? panel.classList.toggle('show') : 
            show ? panel.classList.add('show') : panel.classList.remove('show');
        }
    }

    updateProgress() {
        // Pode expandir depois com barra de progresso
    }

    updateDuration() {
        // Opcional
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            switch(e.key) {
                case ' ': e.preventDefault(); this.togglePlay(); break;
                case 'ArrowRight': e.preventDefault(); this.nextTrack(); break;
                case 'ArrowLeft': e.preventDefault(); this.prevTrack(); break;
            }
        });
    }

    setupAutoPlay() {
        const wasPlaying = localStorage.getItem('kink_was_playing') === 'true';
        
        this.audio.play().then(() => {
            this.isPlaying = true;
            document.getElementById('playPauseBtn').innerHTML = '⏸️';
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
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        window.musicPlayer = new MusicPlayer();
    }, 200);
});