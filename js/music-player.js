// Music Player - KINK Style
class MusicPlayer {
    constructor() {
        this.audio = new Audio();
        this.currentTrackIndex = 0;
        this.isPlaying = false;
        this.volume = 0.5;
        this.playlist = [];
        this.init();
    }

    init() {
    // Carregar playlist do localStorage ou usar padrão
    this.loadPlaylist();
    this.setupAudioEvents();
    this.createPlayerUI();
    this.setupKeyboardShortcuts();
    
    // Tentar auto-play quando o usuário interagir com a página
    this.setupAutoPlay();
    }

    setupAutoPlay() {
        // Verificar se já está tocando
        const wasPlaying = localStorage.getItem('kink_was_playing');
        
        // Tentar iniciar auto-play imediatamente (pode ser bloqueado pelo navegador)
        this.audio.play().then(() => {
            this.isPlaying = true;
            this.updatePlayButton();
            console.log('🎵 Auto-play iniciado com sucesso!');
        }).catch(e => {
            console.log('🎵 Auto-play bloqueado pelo navegador. Aguardando interação do usuário.');
            // Se bloqueado, aguardar clique do usuário na página
            this.waitForUserInteraction();
        });
    }

    waitForUserInteraction() {
        const startPlayback = () => {
            this.audio.play().then(() => {
                this.isPlaying = true;
                this.updatePlayButton();
                console.log('🎵 Playback iniciado após interação do usuário');
            }).catch(e => console.log('Erro ao iniciar playback:', e));
            
            // Remover listeners após primeira interação
            document.removeEventListener('click', startPlayback);
            document.removeEventListener('keydown', startPlayback);
            document.removeEventListener('touchstart', startPlayback);
        };
        
        // Aguardar qualquer interação do usuário
        document.addEventListener('click', startPlayback);
        document.addEventListener('keydown', startPlayback);
        document.addEventListener('touchstart', startPlayback);
    }

    updatePlayButton() {
        const playPauseBtn = document.getElementById('playPauseBtn');
        if (playPauseBtn) {
            playPauseBtn.innerHTML = this.isPlaying ? '<span>⏸️</span>' : '<span>▶️</span>';
        }
    }

    loadPlaylist() {
        // Playlist padrão (adicione suas músicas aqui)
        const defaultPlaylist = [
            {
                id: 'track1',
                title: 'KINK Theme',
                artist: 'KINK Original',
                url: '/assets/music/musely-Kink Is Not Kahoot.mp3',
                cover: '🎵',
                duration: '3:09'
            },
            {
                id: 'track2',
                title: 'Rebel Rhythm',
                artist: 'KINK Original',
                url: '/assets/music/musely-Kink Is Not Kahoot(1).mp3',
                cover: '🎸',
                duration: '3:09'
            },
            
        ];

        // Tentar carregar do localStorage
        const savedPlaylist = localStorage.getItem('kink_playlist');
        if (savedPlaylist) {
            this.playlist = JSON.parse(savedPlaylist);
        } else {
            this.playlist = defaultPlaylist;
            this.savePlaylist();
        }

        // Carregar última música tocada
        const lastTrack = localStorage.getItem('kink_last_track');
        if (lastTrack) {
            this.currentTrackIndex = parseInt(lastTrack);
        }
        
        // Carregar volume salvo
        const savedVolume = localStorage.getItem('kink_volume');
        if (savedVolume !== null) {
            this.volume = parseFloat(savedVolume);
            this.audio.volume = this.volume;
        }
    }

    savePlaylist() {
        localStorage.setItem('kink_playlist', JSON.stringify(this.playlist));
    }

    setupAudioEvents() {
        this.audio.addEventListener('ended', () => {
            this.nextTrack();
        });

        this.audio.addEventListener('timeupdate', () => {
            this.updateProgress();
        });

        this.audio.addEventListener('loadedmetadata', () => {
            this.updateDuration();
        });
    }

    createPlayerUI() {
        // Verificar se já existe
        if (document.getElementById('kinkMusicPlayer')) return;

        const playerHTML = `
            <div id="kinkMusicPlayer" class="music-player">
                <div class="player-toggle" id="playerToggle">
                    <div class="player-icon" id="playPauseBtn">
                        <span>▶️</span>
                    </div>
                    <div class="player-info">
                        <div class="player-title" id="currentTitle">KINK Theme</div>
                        <div class="player-artist" id="currentArtist">KINK Original</div>
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
                        <h4>Playlist KINK</h4>
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
        const volumeIcon = document.getElementById('volumeIcon');
        const playerToggle = document.getElementById('playerToggle');

        if (playPauseBtn) playPauseBtn.addEventListener('click', () => this.togglePlay());
        if (prevBtn) prevBtn.addEventListener('click', () => this.prevTrack());
        if (nextBtn) nextBtn.addEventListener('click', () => this.nextTrack());
        if (playlistBtn) playlistBtn.addEventListener('click', () => this.togglePlaylist());
        if (closePlaylist) closePlaylist.addEventListener('click', () => this.togglePlaylist(false));
        if (volumeSlider) volumeSlider.addEventListener('input', (e) => this.setVolume(e.target.value));
        if (volumeIcon) volumeIcon.addEventListener('click', () => this.toggleMute());
        
        // Fechar playlist ao clicar fora
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('playlistPanel');
            const btn = document.getElementById('playlistBtn');
            if (panel && btn && !panel.contains(e.target) && !btn.contains(e.target)) {
                panel.classList.remove('show');
            }
        });
    }

    renderPlaylist() {
        const playlistList = document.getElementById('playlistList');
        if (!playlistList) return;

        playlistList.innerHTML = this.playlist.map((track, index) => `
            <div class="playlist-item ${index === this.currentTrackIndex ? 'active' : ''}" data-index="${index}">
                <div class="playlist-item-cover">${track.cover || '🎵'}</div>
                <div class="playlist-item-info">
                    <div class="playlist-item-title">${track.title}</div>
                    <div class="playlist-item-artist">${track.artist || 'KINK'}</div>
                </div>
                <div class="playlist-item-duration">${track.duration || '2:30'}</div>
            </div>
        `).join('');

        // Adicionar event listeners
        document.querySelectorAll('.playlist-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.playTrack(index);
            });
        });
    }

    loadTrack(index) {
        if (!this.playlist[index]) return;
        
        const track = this.playlist[index];
        this.currentTrackIndex = index;
        this.audio.src = track.url;
        this.audio.load();
        
        // Atualizar UI
        const titleElem = document.getElementById('currentTitle');
        const artistElem = document.getElementById('currentArtist');
        if (titleElem) titleElem.textContent = track.title;
        if (artistElem) artistElem.textContent = track.artist || 'KINK';
        
        // Salvar última música
        localStorage.setItem('kink_last_track', index);
        
        // Atualizar playlist ativa
        this.renderPlaylist();
        
        // Se estava tocando, continuar
        if (this.isPlaying) {
            this.audio.play().catch(e => console.log('Playback automático bloqueado:', e));
        }
    }

    playTrack(index) {
        this.loadTrack(index);
        this.play();
    }

    togglePlay() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }

    play() {
        this.audio.play().then(() => {
            this.isPlaying = true;
            const playPauseBtn = document.getElementById('playPauseBtn');
            if (playPauseBtn) playPauseBtn.innerHTML = '<span>⏸️</span>';
        }).catch(e => {
            console.log('Erro ao reproduzir:', e);
            this.isPlaying = false;
        });
    }

    pause() {
        this.audio.pause();
        this.isPlaying = false;
        const playPauseBtn = document.getElementById('playPauseBtn');
        if (playPauseBtn) playPauseBtn.innerHTML = '<span>▶️</span>';
    }

    nextTrack() {
        let nextIndex = this.currentTrackIndex + 1;
        if (nextIndex >= this.playlist.length) {
            nextIndex = 0;
        }
        this.playTrack(nextIndex);
    }

    prevTrack() {
        let prevIndex = this.currentTrackIndex - 1;
        if (prevIndex < 0) {
            prevIndex = this.playlist.length - 1;
        }
        this.playTrack(prevIndex);
    }

    setVolume(value) {
        this.volume = parseFloat(value);
        this.audio.volume = this.volume;
        localStorage.setItem('kink_volume', this.volume);
        
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
        }
    }

    togglePlaylist(show) {
        const panel = document.getElementById('playlistPanel');
        if (panel) {
            if (show === undefined) {
                panel.classList.toggle('show');
            } else if (show) {
                panel.classList.add('show');
            } else {
                panel.classList.remove('show');
            }
        }
    }

    updateProgress() {
        // Você pode adicionar uma barra de progresso se quiser
        if (this.audio.duration) {
            const progress = (this.audio.currentTime / this.audio.duration) * 100;
            // Atualizar barra de progresso se existir
        }
    }

    updateDuration() {
        // Atualizar duração na playlist
        if (this.audio.duration) {
            const minutes = Math.floor(this.audio.duration / 60);
            const seconds = Math.floor(this.audio.duration % 60);
            const duration = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (this.playlist[this.currentTrackIndex]) {
                this.playlist[this.currentTrackIndex].duration = duration;
                this.renderPlaylist();
            }
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
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    this.setVolume(Math.max(0, this.volume - 0.1));
                    break;
            }
        });
    }

    // Método para adicionar música à playlist
    addTrack(track) {
        this.playlist.push(track);
        this.savePlaylist();
        this.renderPlaylist();
    }

    // Método para remover música da playlist
    removeTrack(index) {
        if (index >= 0 && index < this.playlist.length) {
            this.playlist.splice(index, 1);
            this.savePlaylist();
            
            if (this.currentTrackIndex >= this.playlist.length) {
                this.currentTrackIndex = 0;
            }
            
            if (this.currentTrackIndex === index) {
                this.loadTrack(this.currentTrackIndex);
            }
            
            this.renderPlaylist();
        }
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    // Aguardar um pouco para garantir que o body está pronto
    setTimeout(() => {
        window.musicPlayer = new MusicPlayer();
    }, 100);
});