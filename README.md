# 🔥 KINK is not Kahoot

*The rebellious quiz platform that breaks all the rules*

[![Node.js](https://img.shields.io/badge/Node.js-18.x-green.svg)](https://nodejs.org/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-4.x-black.svg)](https://socket.io/)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat&logo=firebase&logoColor=black)](https://firebase.google.com/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## 🎯 Sobre o Projeto

**KINK is not Kahoot** é uma plataforma de quizzes interativa em tempo real, construída com **Node.js + Socket.IO** para garantir baixa latência e escalabilidade. Um servidor centralizado gerencia o estado do jogo em memória, eliminando gargalos e permitindo dezenas de jogadores simultâneos.

Além do modo "quiz ao vivo" no estilo Kahoot, o projeto inclui **Simulados AWS** (CLF-C02, SAA-C03, DVA-C02) com banco de questões próprio e **Trilhas de Estudo** completas (apostilas) para as certificações AWS Solutions Architect Associate e Data Engineer Associate.

**Desenvolvido como projeto de portfólio** para demonstrar habilidades em:
- Node.js + Express + Socket.IO (servidor em tempo real)
- Firebase (Auth, Firestore para persistência)
- JavaScript puro (Vanilla JS) no frontend
- Arquitetura cliente-servidor com WebSockets
- Sistema de pontuação baseado em velocidade
- Geração de conteúdo educacional (simulados e trilhas de estudo AWS)
- Acessibilidade (ARIA, navegação por teclado, leitores de tela)

## ✨ Funcionalidades

### 🎮 Quiz em Tempo Real

**Para Professores (Hosts)**
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
- ✅ Histórico de sessões finalizadas

**Para Alunos (Players)**
- ✅ Entrar com código de sala (sem criar conta)
- ✅ Escolher avatar (8 opções) e nickname
- ✅ Ver perguntas em tempo real com fases de leitura e resposta
- ✅ Pontuação calculada instantaneamente (via servidor)
- ✅ Ranking parcial entre perguntas e ranking final

### 🎓 Simulados AWS

- 📝 Modo solo: simulados com proporção oficial de domínios por certificação (CLF-C02, SAA-C03, DVA-C02), 3 níveis de dificuldade (iniciante/médio/avançado) e quantidade de questões configurável
- 🎓 Modo professor (ao vivo): cria sala com código, alunos entram pelo player e votam em tempo real, com distribuição de respostas da turma
- 📊 Resultado detalhado por domínio, revisão de questões com explicações

### 📚 Trilhas de Estudo

- 📖 Apostilas completas para **SAA-C03** (Solutions Architect Associate) e **DEA-C01** (Data Engineer Associate)
- 🧭 Navegação por sidebar com scroll-spy, accordions de perguntas e respostas, barra de progresso de leitura
- 🗂️ Glossário de siglas e plano de estudos semanal

### 🎨 Visual & Acessibilidade

- 🌌 Tema visual unificado em todas as páginas: aurora animada, grid "data floor", ícones flutuantes (cloud/data) e canvas de partículas
- ✨ Animações de scroll-reveal com progressive enhancement (degrada graciosamente sem JS) e suporte a `prefers-reduced-motion`
- ♿ Telas de jogo (host/player) com foco em acessibilidade: ARIA labels, `aria-live`, navegação por teclado e skip links
- 📱 Totalmente responsivo (mobile, tablet, desktop)

### 🎵 Player de Música

- 🎵 Detecta automaticamente a página (menu ou jogo) e troca a playlist
- 🎵 Playlist do menu: músicas com vocais (`/assets/music/Index/`)
- 🎵 Playlist do jogo: músicas instrumentais (`/assets/music/instrumental/`)
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

```
kink-is-not-kahoot/
├── server.js               # Servidor Node.js + Socket.IO
├── package.json            # Dependências
├── version.json            # Versionamento
├── squarecloud.app         # Configuração do SquareCloud
├── index.html              # Página inicial (+ seção "Sobre mim")
├── host.html                # Painel do professor (quiz ao vivo)
├── player.html               # Tela do aluno (quiz ao vivo)
├── create-quiz.html         # Criar/editar quizzes
├── my-quizzes.html           # Lista de quizzes
├── historico.html            # Histórico de sessões
├── simulados.html            # Simulados AWS (solo e ao vivo)
├── trilha.html               # Hub das trilhas de estudo
├── trilha-saa.html           # Apostila SAA-C03
├── trilha-dea.html           # Apostila DEA-C01
├── css/                      # Estilos (style, components, landing-fx, trilha, ...)
├── js/                       # Scripts do frontend
│   ├── socket-client.js       # Cliente Socket.IO
│   ├── host-socket.js          # Lógica do host
│   ├── player-socket.js        # Lógica do player
│   ├── landing-fx.js           # Efeitos visuais + scroll-reveal
│   ├── music-player.js         # Player de música
│   └── ...                     # Outros utilitários
├── data/exams/               # Banco de questões dos simulados (por cert. e nível)
├── images/badges/            # Badges/certificações exibidas no "Sobre mim"
├── assets/music/             # Trilhas sonoras (menu e jogo)
└── scripts/question-generator/ # Ferramenta local de geração de questões (Gemini)
```

## 🛠️ Como Executar Localmente

### Pré-requisitos
- Node.js 18+
- NPM
- Conta Google (para Firebase)

### Passos

1. **Clone o repositório**
   ```bash
   git clone https://github.com/Vinicius-Merces/kink-is-not-kahoot.git
   cd kink-is-not-kahoot
   ```

2. **Instale as dependências**
   ```bash
   npm install
   ```

3. **Configure o Firebase**
   - Crie um projeto no [Firebase Console](https://console.firebase.google.com/)
   - Ative **Authentication** → método Google
   - Ative o **Firestore Database**
   - Copie as credenciais web para `js/firebase-config.js`
   - *(Opcional)* Configure as credenciais do Firebase Admin para persistência dos resultados:
     - Gere uma nova chave em **Configurações do Projeto → Contas de Serviço → Gerar nova chave privada**
     - ⚠️ **NUNCA versione esse arquivo.** Use uma das opções abaixo:
       - **Local**: salve como `serviceAccountKey.json` na raiz do projeto (já está no `.gitignore`)
       - **Produção (recomendado)**: defina a variável de ambiente `FIREBASE_SERVICE_ACCOUNT_BASE64` com o JSON da service account codificado em Base64 (gere com `node scripts/print-firebase-env.js`, veja `.env.example`)

4. **Execute localmente**
   ```bash
   npm start
   ```
   Acesse `http://localhost:3000`

### Deploy no SquareCloud

1. Configure o arquivo `squarecloud.app` na raiz:
   ```
   name = kink-is-not-kahoot
   node = 20
   main = server.js
   memory = 512
   ```
2. No painel do SquareCloud, defina a variável de ambiente `FIREBASE_SERVICE_ACCOUNT_BASE64` com o valor gerado por `node scripts/print-firebase-env.js` (não envie `serviceAccountKey.json` no .zip)
3. Crie um `.zip` do projeto (excluindo `node_modules`)
4. Faça o upload no painel do SquareCloud:
   - Tipo: Publicação na Web
   - Arquivo principal: `server.js`
   - Inicialização: `node server.js`
   - Build: `npm install`

## 🧰 Scripts Úteis

- `npm start` — inicia o servidor (`server.js`)
- `npm run dev` — inicia com `nodemon` (auto-reload)
- `npm run update-version` — atualiza `version.json`
- `scripts/question-generator/` — ferramenta **local** para gerar novas questões dos simulados AWS via API do Google Gemini (veja `scripts/question-generator/README.md`)

## 🎮 Como Jogar

### Para Professores (Hosts)
1. Faça login com sua conta Google
2. Crie um quiz (título, perguntas, opções, tempo)
3. Na lista de quizzes, clique no ícone 🎮 para iniciar uma sessão
4. O servidor gera um código de 6 dígitos — compartilhe com os alunos
5. Clique em **Iniciar Quiz** (tela de carregamento de 5s)
6. Para cada pergunta, clique em **Iniciar Pergunta**:
   - Leitura (5s) – alunos veem apenas o texto
   - Respostas (tempo limite) – opções aparecem
7. Após cada pergunta, o ranking parcial é exibido — clique em **Próxima Pergunta** para continuar
8. Ao final, veja o ranking final e encerre a sessão

### Para Alunos (Players)
1. Acesse o link do jogo e digite o código de 6 dígitos
2. Escolha um avatar e um nickname
3. Aguarde o professor iniciar o quiz
4. Durante a pergunta: leia (5s) e responda (quanto mais rápido, mais pontos)
5. Veja seu desempenho no ranking parcial e, ao final, no ranking final

## 🎨 Design e Identidade Visual

- Cores principais: `#ff6b6b` (Rebel Red) e `#4ecdc4` (KINK Teal)
- Fundo escuro: gradiente de `#1a1a2e` a `#0f3460`, com aurora animada e grid "data floor"
- Efeito glitch no título principal
- Cards com vidro (glassmorphism), hover com brilho e ícones flutuantes temáticos (cloud/data)
- Player de música flutuante com minimização e indicadores visuais
- Totalmente responsivo (mobile, tablet, desktop)

## 📄 Licença

Distribuído sob a licença **GNU General Public License v3.0**.

## 📬 Contato

**Vinicius Mercês Silva** — Especialista em Produtos e Instrutor Técnico, em transição para Cloud Computing, Linux, Análise de Dados e Desenvolvimento de Software (cursando AWS Cloud Practitioner).

- GitHub: [github.com/Vinicius-Merces](https://github.com/Vinicius-Merces)
- LinkedIn: [linkedin.com/in/vinicius-merces-aws-dev](https://www.linkedin.com/in/vinicius-merces-aws-dev)

---

⚠️ **Disclaimer**: KINK is not Kahoot não é afiliado ao Kahoot. É um projeto independente criado para fins educacionais e de portfólio.

Built with 🔥 for those who dare to be different
