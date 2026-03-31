# 🔥 KINK is not Kahoot

*The rebellious quiz platform that breaks all the rules*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Node.js](https://img.shields.io/badge/Node.js-18.x-green.svg)](https://nodejs.org/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-4.x-black.svg)](https://socket.io/)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat&logo=firebase&logoColor=black)](https://firebase.google.com/)

## 🎯 Sobre o Projeto

**KINK is not Kahoot** é uma plataforma de quizzes interativa em tempo real, construída com **Node.js + Socket.IO** para garantir baixa latência e escalabilidade. Diferente da versão anterior (baseada apenas em Firestore listeners), esta versão utiliza um servidor centralizado que gerencia o estado do jogo em memória, eliminando gargalos e permitindo dezenas de jogadores simultâneos.

**Desenvolvido como projeto de portfólio** para demonstrar habilidades em:
- Node.js + Express + Socket.IO (servidor em tempo real)
- Firebase (Auth, Firestore para persistência)
- JavaScript puro (Vanilla JS) no frontend
- Arquitetura cliente-servidor com WebSockets
- Sistema de pontuação baseado em velocidade
- Player de música com playlists dinâmicas

## ✨ Funcionalidades

### Para Professores (Hosts)
- ✅ Login com Google
- ✅ Criar quizzes ilimitados (sem restrição de caracteres)
- ✅ Adicionar perguntas com 4+ opções e tempo personalizado
- ✅ Editar, excluir e listar quizzes
- ✅ Iniciar sessão ao vivo com código de 6 dígitos (gerado pelo servidor)
- ✅ Ver jogadores conectados em tempo real (via WebSocket)
- ✅ Controlar o fluxo do jogo:
  - Fase de leitura (5s) – alunos veem apenas a pergunta
  - Fase de respostas (tempo definido) – opções aparecem
- ✅ Pontuação baseada em velocidade (1000 × tempo_restante / tempo_limite) – calculada no servidor
- ✅ Ranking em tempo real (parcial e final)
- ✅ Finalizar quiz e exibir ranking final

### Para Alunos (Players)
- ✅ Entrar com código de sala (sem criar conta)
- ✅ Escolher avatar (8 opções)
- ✅ Escolher nickname
- ✅ Ver perguntas em tempo real com fases:
  - Leitura (5s) – apenas a pergunta
  - Respostas – opções com timer
- ✅ Pontuação calculada instantaneamente (via servidor)
- ✅ Ranking parcial entre perguntas e ranking final
- ✅ Player de música integrado (playlists separadas para menu e jogo)

### Player de Música
- 🎵 Detecta automaticamente a página (menu ou jogo) e troca a playlist
- 🎵 Playlist do menu: músicas com vocais (pasta `/assets/music/Index/`)
- 🎵 Playlist do jogo: músicas instrumentais (pasta `/assets/music/instrumental/`)
- 🎵 Controles: play/pause, próximo/anterior, volume, mute
- 🎵 Modo minimizável (círculo com a letra "K" e pulsação)
- 🎵 Atalhos de teclado (Espaço, setas ← → ↑ ↓)
- 🎵 Persistência de última música e volume (separado por tipo de playlist)

## 🚀 Tech Stack

| Camada | Tecnologia |
|--------|------------|
| **Servidor** | Node.js + Express + Socket.IO |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Banco de Dados** | Firebase Firestore (persistência) + memória (estado do jogo) |
| **Autenticação** | Firebase Authentication (Google) |
| **Hospedagem** | SquareCloud (Node.js + arquivos estáticos) |
| **Música** | Áudio nativo do navegador + playlist dinâmica |

## 📁 Estrutura de Pastas
kink-is-not-kahoot/
├── squarecloud.app # Configuração do SquareCloud
├── server.js # Servidor Node.js + Socket.IO
├── package.json # Dependências
├── version.json # Versionamento
├── index.html # Página inicial
├── host.html # Painel do professor
├── player.html # Tela do aluno
├── create-quiz.html # Criar/editar quizzes
├── my-quizzes.html # Lista de quizzes
├── css/ # Estilos
├── js/ # Scripts frontend
│ ├── socket-client.js # Cliente Socket.IO
│ ├── host-socket.js # Lógica do host
│ ├── player-socket.js # Lógica do player
│ └── ... # Outros utilitários
└── assets/ # Músicas, avatares

text

## 🛠️ Como Executar Localmente

### Pré-requisitos
- Node.js 18+
- NPM
- Conta Google (para Firebase)

### Passos

1. **Clone o repositório**
   ```bash
   git clone https://github.com/Vinicius-Merces/Kink.git
   cd Kink
Instale as dependências

bash
npm install
Configure o Firebase

Crie um projeto no Firebase Console

Ative Authentication → método Google

Ative Firestore Database

Copie as credenciais para js/firebase-config.js

(Opcional) Baixe serviceAccountKey.json para persistência dos resultados

Execute localmente

bash
npm start
Acesse http://localhost:3000

Deploy no SquareCloud
Configure o arquivo squarecloud.app na raiz:

plaintext
name = kink-is-not-kahoot
node = 20
main = server.js
memory = 512
Crie um .zip do projeto (excluindo node_modules)

Faça o upload no painel do SquareCloud:

Tipo: Publicação na Web

Arquivo principal: server.js

Inicialização: node server.js

Build: npm install

🎮 Como Jogar
Para Professores (Hosts)
Faça login com sua conta Google

Crie um quiz (título, perguntas, opções, tempo)

Na lista de quizzes, clique no ícone 🎮 para iniciar uma sessão

O servidor gera um código de 6 dígitos

Compartilhe o código com os alunos

Clique em Iniciar Quiz (tela de carregamento de 5s)

Clique em Iniciar Pergunta para cada pergunta:

Leitura (5s) – alunos veem apenas o texto

Respostas (tempo limite) – opções aparecem

Após cada pergunta, o ranking parcial é exibido

Clique em Próxima Pergunta para continuar

Ao final, veja o ranking final e feche a sessão

Para Alunos (Players)
Acesse o link do jogo e digite o código de 6 dígitos

Escolha um avatar e um nickname

Aguarde o professor iniciar o quiz

Durante a pergunta:

Leia a pergunta (5s)

Responda clicando em uma das opções (quanto mais rápido, mais pontos)

Veja seu desempenho no ranking parcial

Ao final, confira o ranking final

🎨 Design e Identidade Visual
Cores principais: #ff6b6b (Rebel Red) e #4ecdc4 (KINK Teal)

Fundo escuro: gradiente de #1a1a2e a #0f3460

Efeito glitch no título principal

Cards com vidro (glassmorphism) e hover com brilho

Player de música flutuante com minimização e indicadores visuais

Totalmente responsivo (mobile, tablet, desktop)

📄 Licença
Distribuído sob a licença GNU General Public License v3.0. Veja o arquivo LICENSE para mais informações.

📬 Contato
Autor: Vinicius Mercês Silva

GitHub: https://github.com/Vinicius-Merces

LinkedIn: https://www.linkedin.com/in/vinicius-merces-dev/

⚠️ Disclaimer: KINK is not Kahoot não é afiliado ao Kahoot. É um projeto independente criado para fins educacionais e de portfólio.

Built with 🔥 for those who dare to be different