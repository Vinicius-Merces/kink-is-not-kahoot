# ☁️ CloudPath

*Sua trilha para a nuvem — trilhas de estudo, simulados e quizzes AWS em tempo real*

> **Nota:** este projeto nasceu como **KINK is not Kahoot** e virou **CloudPath** em 17/07/2026.
> O repositório mantém o nome antigo por histórico; o produto e o domínio são CloudPath
> ([cloudpath.squareweb.app](https://cloudpath.squareweb.app)).

[![Node.js](https://img.shields.io/badge/Node.js-18.x-green.svg)](https://nodejs.org/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-4.x-black.svg)](https://socket.io/)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat&logo=firebase&logoColor=black)](https://firebase.google.com/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Validar bancos](https://github.com/Vinicius-Merces/kink-is-not-kahoot/actions/workflows/validate-banks.yml/badge.svg)](https://github.com/Vinicius-Merces/kink-is-not-kahoot/actions/workflows/validate-banks.yml)

## 🎯 Sobre o Projeto

**CloudPath** é uma plataforma de estudos para certificações AWS com quizzes interativos em tempo real, construída com **Node.js + Socket.IO** para garantir baixa latência e escalabilidade. Um servidor centralizado gerencia o estado do jogo em memória, eliminando gargalos e permitindo dezenas de jogadores simultâneos.

Além do modo "quiz ao vivo" no estilo Kahoot, o projeto inclui **Simulados AWS** com **1.833 questões próprias** (CLF-C02, SAA-C03, DVA-C02, DEA-C01) e **Trilhas de Estudo** completas (apostilas) com narração em áudio para as certificações AWS.

**Desenvolvido como projeto de portfólio** para demonstrar habilidades em:
- Node.js + Express + Socket.IO (servidor em tempo real)
- Firebase (Auth, Firestore para persistência)
- JavaScript puro (Vanilla JS) no frontend
- Arquitetura cliente-servidor com WebSockets
- Sistema de pontuação baseado em velocidade
- Geração de conteúdo educacional (simulados e trilhas de estudo AWS)
- Acessibilidade (ARIA, navegação por teclado, leitores de tela)
- Pipeline de dados em Python (rotulagem, validação e CI dos bancos de questões)
- Síntese de voz (Azure Speech + SSML) com tratamento fonético para termos em inglês
- CI com GitHub Actions (validação automática dos bancos a cada push)

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

**Banco próprio de 1.833 questões**, com explicação em cada uma e distribuição fiel aos pesos oficiais de domínio de cada exame:

| Certificação | Questões | Trilha |
|---|---|---|
| **CLF-C02** Cloud Practitioner | 443 | — |
| **SAA-C03** Solutions Architect Associate | 868 | 21 capítulos |
| **DVA-C02** Developer Associate | 412 | 14 capítulos |
| **DEA-C01** Data Engineer Associate | 110 | 13 capítulos |

- 📝 **Modo solo**: proporção oficial de domínios, 3 níveis (iniciante/médio/avançado) e quantidade configurável
- 🎓 **Modo professor (ao vivo)**: sala com código, alunos votam em tempo real, distribuição de respostas da turma
- ⏱️ **Modo prova real**: cronômetro de 2 min/questão, marcação para revisão e tela de conferência antes de entregar — simula a experiência da Pearson VUE
- 🔁 **Revisar meus erros**: monta um simulado só com as questões erradas nas tentativas anteriores
- 🎯 **Desempenho por tema**: 1.390 questões rotuladas por tópico (não só por domínio). O resultado mostra o aproveitamento em cada tema e leva direto à prática focada no ponto fraco
- ☑️ **Questões multi-resposta** (43): "Selecione DUAS alternativas", como no exame real
- 📊 Revisão completa com explicação por alternativa e link para o capítulo correspondente da trilha

### 📈 Meu Progresso

- Cartões de desempenho: simulados feitos, melhor nota, média das últimas 5, aprovações e streak de estudo
- Gráfico de evolução da pontuação com linha de corte nos 70%
- Desempenho acumulado por domínio e ranking dos **temas a reforçar**
- Progresso de leitura das trilhas (capítulos concluídos)

### 📚 Trilhas de Estudo

- 📖 Apostilas completas para **SAA-C03** (21 capítulos), **DVA-C02** (14) e **DEA-C01** (13)
- 🎧 **Narração em áudio** dos capítulos (Azure Speech, duas vozes alternadas) para estudo passivo
- 📊 **Diagramas SVG** dos conceitos que texto sozinho não resolve: fluxo VPC, modos de invocação do Lambda, pipeline Kinesis→Firehose→S3→Athena, camadas do data lake, anatomia MPP do Redshift, entre outros
- 🎯 **CTA de prática** ao fim de cada capítulo: abre um simulado focado exatamente no tema lido
- ✅ Marcação de capítulo concluído, com progresso sincronizado entre dispositivos (Firestore)
- 🧭 Navegação por sidebar com scroll-spy, busca no conteúdo, accordions de Q&A e barra de progresso de leitura
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
| **Conteúdo/Dados** | Python (rotulagem por tema, validação dos bancos) |
| **Narração** | Azure Speech (SSML, vozes pt-BR) + tratamento fonético |
| **CI** | GitHub Actions (valida bancos e sintaxe a cada push) |

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
├── progresso.html            # Dashboard de progresso do aluno
├── trilha.html               # Hub das trilhas de estudo
├── trilha-saa.html           # Apostila SAA-C03 (21 capítulos)
├── trilha-dva.html           # Apostila DVA-C02 (14 capítulos)
├── trilha-dea.html           # Apostila DEA-C01 (13 capítulos)
├── css/                      # Estilos (style, components, landing-fx, trilha, ...)
├── js/                       # Scripts do frontend
│   ├── socket-client.js       # Cliente Socket.IO
│   ├── host-socket.js          # Lógica do host
│   ├── player-socket.js        # Lógica do player
│   ├── simulados.js            # Simulados (modos prova/estudo/erros/prova real)
│   ├── progresso.js            # Dashboard de progresso
│   ├── study-progress.js       # Progresso das trilhas + sync Firestore
│   ├── tts-reader.js           # Player da narração dos capítulos
│   ├── landing-fx.js           # Efeitos visuais + scroll-reveal
│   ├── music-player.js         # Player de música
│   └── ...                     # Outros utilitários
├── data/exams/               # Banco de questões (por certificação e nível)
├── assets/narracao/          # MP3s da narração das trilhas
├── assets/music/             # Trilhas sonoras (menu e jogo)
├── images/badges/            # Badges/certificações exibidas no "Sobre mim"
├── .github/workflows/        # CI: validação dos bancos a cada push
└── scripts/
    ├── validate_banks.py       # Validador dos bancos (roda no CI)
    ├── question-generator/     # Geração de questões (Gemini) — local
    ├── topic-tagger/           # Rotulagem das questões por tema (tag_saa/dva/dea.py)
    └── tts-generator/          # Narração: roteiros + Azure Speech + tratamento fonético
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
- `python3 scripts/validate_banks.py` — **valida todos os bancos de questões** (JSON, gabarito no intervalo, explicação sincronizada com as alternativas, rótulos de tema, IDs únicos, distribuição das respostas). Roda automaticamente no CI a cada push.
- `scripts/question-generator/` — geração de questões via API do Google Gemini (local)
- `scripts/topic-tagger/` — rotulagem das questões por tema (`tag_saa.py`, `tag_dva.py`, `tag_dea.py`)
- `scripts/tts-generator/` — geração da narração das trilhas (veja abaixo)

## 🎧 Narração das Trilhas (TTS)

Os capítulos das apostilas têm áudio gerado com **Azure Speech (SSML, vozes pt-BR alternadas)**.

O roteiro **não é o HTML lido em voz alta**: blocos de código são parafraseados, tabelas viram comparações fluidas e os checkpoints viram diálogo entre as duas vozes.

**O problema interessante — inglês numa voz pt-BR.** Vozes neurais de locale único só realizam o inventário fonético do próprio idioma. Marcar os termos com `<phoneme alphabet="ipa">` **não funciona**: fonemas inexistentes em português (θ, æ, ɹ, ʊ) são descartados pelo motor, e a palavra sai truncada. A solução é a **re-grafia**: escrever o termo com grafemas portugueses, para a voz usar apenas sons que ela possui.

| termo | re-grafia | como o português lê |
|---|---|---|
| gateway | `Guêituei` | /gˈejtwej/ |
| Deny | `Denái` | /denˈaj/ |
| bucket | `Báquet` | /bˈaket/ |

O `glossary.py` converte automaticamente o IPA anotado nos roteiros para grafia portuguesa (respeitando as regras do PT-BR: "gu" antes de e/i para /g/ duro, "qu" para /k/, "ss" entre vogais, "h" mudo...), com um dicionário de exceções revisadas à mão.

```bash
python3 scripts/tts-generator/check_respell.py      # valida a grafia (não precisa de chave)
python3 scripts/tts-generator/preview_phonetics.py  # tabela: como cada termo será falado
python3 scripts/tts-generator/test_pronuncia.py     # gera 1 MP3 curto de teste (precisa da chave Azure)
python3 scripts/tts-generator/generate.py cap01_script cap01.mp3
```

Estado atual da narração e o que falta regravar: veja **`BACKLOG-NARRACAO.md`**.

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

- Cores principais: `#ff6b6b` (Coral) e `#4ecdc4` (Teal) — as mesmas do logo CloudPath
- Fundo escuro profundo (`#060b16` → `#0f2138`) com aurora sutil e grid "data floor"
- Tipografia: Space Grotesk (títulos), Montserrat (texto) e JetBrains Mono (chips estilo console AWS)
- Navbar em grupos (Estudar · Quizzes · Desempenho) com dropdowns acessíveis e gaveta no mobile
- Cards com vidro (glassmorphism) e hover com brilho
- Player de música flutuante com minimização e indicadores visuais
- Totalmente responsivo (mobile, tablet, desktop)

## 📄 Licença

Distribuído sob a licença **GNU General Public License v3.0**.

## 📬 Contato

**Vinicius Mercês Silva** — Profissional de TI com mais de 9 anos em suporte técnico e soluções de impressão corporativa, graduado em Análise e Desenvolvimento de Sistemas. Atua com Cloud Computing, Linux, dados e desenvolvimento de software.

**AWS Certified Cloud Practitioner (CLF-C02)** · Egresso do **AWS re/Start** (Escola da Nuvem)

- GitHub: [github.com/Vinicius-Merces](https://github.com/Vinicius-Merces)
- LinkedIn: [linkedin.com/in/vinicius-merces-aws-dev](https://www.linkedin.com/in/vinicius-merces-aws-dev)

---

⚠️ **Disclaimer**: CloudPath não é afiliado à AWS nem ao Kahoot. É um projeto independente criado para fins educacionais e de portfólio.

☁️ Built for the climb — sa-east-1
