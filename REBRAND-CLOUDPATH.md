# Rebrand: KINK is not Kahoot → CloudPath

**Virada: 17/07/2026** · Novo endereço: `cloudpath.squareweb.app`

A paleta **não muda** (`#ff6b6b` coral + `#4ecdc4` teal) — o logo novo já usa exatamente essas cores.

---

## Base já implementada ✅

| Item | Onde |
|---|---|
| Logo e ícone (otimizados p/ web) | `images/branding/` — logo 720px/77KB, ícone 512/192/180/32/16 |
| Módulo central de marca | `js/branding.js` — nome, tagline, domínio, data da virada |
| Migração segura de `localStorage` | `js/branding.js` → `migrateStorage()` |
| Card de aviso na landing | `index.html` + `css/branding.css` |
| Logo na navbar, hero, tela do aluno e marca d'água | `css/branding.css` + `js/branding.js` |
| Símbolo da nuvem isolado (transparente) | `images/branding/cloudpath-mark.png` |
| Playlist gerada a partir do disco | `scripts/rebuild_playlist.py` |

### 👀 Preview antes do dia 17

Abra qualquer página com **`?brand=cloudpath`** — ex.: `localhost:3000/index.html?brand=cloudpath`.
Mostra a marca nova (logo, tagline, marca d'água) sem mexer na data. `?brand=kink` força a antiga.

### Como a virada acontece

`js/branding.js` tem **uma constante**:

```js
const CUTOVER = new Date('2026-07-17T00:00:00-03:00');
```

Quando essa data chega, o site **troca a marca sozinho** — navbar, título da aba, hero e tagline — e o card de aviso se remove. Não precisa de deploy no dia. Para antecipar ou adiar, muda a data.

> Isso é a *base*. O texto "KINK" continua no HTML como fallback (se o JS não carregar, o site não fica sem nome). A limpeza final do HTML é a etapa 2, abaixo.

---

## ⚠️ Armadilha: as chaves de `localStorage`

O progresso das trilhas e o streak vivem em **`kink_study_progress_v1`**.

**Renomear essa chave direto = todo usuário perde o progresso salvo.**

Por isso `migrateStorage()` **copia** `kink_*` → `cloudpath_*` (não move) e `storageGet()` lê a chave nova com *fallback* na antiga. Rollback continua seguro. Só remova as chaves `kink_*` depois de alguns meses de convivência.

Chaves afetadas:
- `kink_study_progress_v1` ← **o progresso de estudo**
- `kink_volume`, `kink_was_playing`, `kink_last_track_*` (player)
- `kink_version`, `kink_update_deferred_*` (checagem de versão)

---

## ✅ O que já está automático no dia 17

`js/branding.js` está nas **13 páginas**. Na virada, troca sozinho:
navbar, tela do aluno, título da aba, hero, rodapé, favicon, ícone do iOS e o manifest do PWA.

**Mas "só trocar o link" NÃO basta.** Veja o checklist abaixo.

---

## 🚨 Checklist do dia 17 (nesta ordem)

### 1. Firebase — 1 clique obrigatório (o resto fica legado)

**Decisão tomada:** o código do Firebase (`projectId`, `authDomain`, `storageBucket`)
**fica como legado permanente**. Roda escondido, ninguém vê, e o ID de projeto é imutável
de qualquer forma. Não se gasta tempo com isso.

**MAS há uma exceção que NÃO é código, e sim configuração de console — e é obrigatória:**

> Console do Firebase → **Authentication → Settings → Authorized domains** →
> adicionar **`cloudpath.squareweb.app`**

Sem isso o **login com Google não funciona** no domínio novo. Não é estética, é função.
30 segundos de clique. É o item mais fácil de esquecer e o mais caro de esquecer.

### 2. SquareCloud
- Criar/apontar o domínio `cloudpath.squareweb.app`
- **Manter `kink.squareweb.app` redirecionando** por alguns meses — quem já instalou o PWA
  e quem tem o link salvo continua chegando

### 3. Rename permanente do código
```bash
python3 scripts/rebrand.py --dry-run   # confere
python3 scripts/rebrand.py             # aplica (100 substituições)
```
Por que isso importa mesmo com o `branding.js`: o JS troca o que aparece na TELA,
mas o **código-fonte continua dizendo KINK**. Preview de link no WhatsApp/LinkedIn e
buscadores leem o HTML cru — não o DOM depois do JS. Sem esse passo, compartilhar o link
mostra "KINK is not Kahoot".

### 3b. Auditar o que sobrou
```bash
python3 scripts/rebrand_audit.py
```
Classifica **toda** ocorrência restante de KINK/Kahoot em 4 categorias. O objetivo não é
zerar — é garantir que nada **visível** ficou para trás. Meta: `🟢 TROCAR — 0`.

| | o que é | ação |
|---|---|---|
| 🔴 **NÃO TOCAR** (22) | `projectId` do Firebase, chaves `kink_*`, nomes dos MP3 | **deixar como está** |
| 🟡 opcional (465) | variáveis CSS `--kink-*`, `@keyframes`, nome do repo | quando quiser |
| 🔵 comentário | cabeçalhos de código, README | cosmético |
| 🟢 **TROCAR** | texto que o usuário lê | **precisa estar zerado** |

### ⛔ Os três que NUNCA devem ser renomeados

1. **`projectId: "kink-is-not-kahoot"`** (`js/firebase-config.js`) — o ID do projeto Firebase é
   **imutável**. Renomear no código aponta o app para um projeto inexistente: login, Firestore e
   Storage morrem juntos.
2. **`kink_study_progress_v1`** e demais chaves `kink_*` — apagariam o progresso salvo dos usuários.
   Quem cuida disso é o `migrateStorage()` (copia, não move).
3. **`/assets/music/Index/KINK - *.mp3`** — é o **nome do arquivo em disco**, não texto. Renomear no
   código silencia o player. (O `rebrand.py` troca `title`/`artist` e preserva a `url` de propósito.)

### 3c. Trilha sonora nova

⚠️ **Os nomes dos MP3 vieram com maiúscula inconsistente** (`CloudPath Jam` vs `Cloudpath Me Chama`).
O SquareCloud roda **Linux**, onde nome de arquivo diferencia maiúscula de minúscula: se o código
apontar para `CloudPath Me Chama.mp3` e o arquivo for `Cloudpath...`, a música **toca no Windows e
dá 404 em produção**.

Solução: não digitar nome de arquivo nenhum. O script lê a pasta e usa o nome exato do disco.

```bash
# 1. Coloque os MP3 novos na pasta e apague os do KINK
# 2. Padronize a grafia dos arquivos
python3 scripts/rebuild_playlist.py --normalize --dry-run
python3 scripts/rebuild_playlist.py --normalize
```
Ele também ignora automaticamente qualquer faixa com "KINK" no nome, e dá títulos a partir
do nome do arquivo (personalize no dict `TITULOS` se quiser algo mais bonito que "Jam"/"Neon").

### 4. Depois de rodar o script
- Remover o card de aviso do `index.html` (`#rebrandNotice`)
- Manter o `js/branding.js` (a migração de localStorage ainda serve)
- Atualizar o `README.md`

---

## ✅ Funções verificadas (não quebram com a troca de domínio)

Auditei o que costuma quebrar num rebrand de domínio:

| função | estado | por quê |
|---|---|---|
| **API / CORS** | ✅ seguro | `server.js` usa `origin: "*"` — sem lista branca de domínio |
| **Socket.IO (quiz ao vivo)** | ✅ seguro | cliente usa `io({})` — conecta na mesma origem, sem URL fixa |
| **Service worker** | ✅ ajustado | é *network-first*, então respeita o redirect. O `rebrand.py` troca o nome do cache (`kink-cache-v1` → `cloudpath-cache-v1`), invalidando assets e ícones velhos de propósito |
| **Login com Google** | ⚠️ **exige o passo 1** | sem o domínio autorizado, quebra |
| **Progresso / streak** | ✅ seguro | `migrateStorage()` copia as chaves em vez de mover |
| **Player de música** | ✅ seguro | `rebrand.py` troca `title`/`artist` e preserva as URLs dos MP3 |

**PWA já instalado:** quem instalou pelo endereço antigo continua com o app antigo apontando
para `kink.squareweb.app`. Com o redirect ativo ele continua funcionando, mas o ícone e o nome
só atualizam se reinstalar. Por isso: **manter o redirect por alguns meses**.

---

## Etapa 2 — limpeza opcional (sem pressa)

### Texto visível (~60 ocorrências)
- [ ] `<title>` das 12 páginas: `... - KINK is not Kahoot` → `... - CloudPath`
- [ ] `<meta name="apple-mobile-web-app-title" content="KINK">` → `CloudPath`
- [ ] Navbar de todas as páginas: `<h2 class="glitch-mini">KINK</h2>` + `<span>is not Kahoot</span>`
- [ ] Hero da `index.html`: `<h1 class="glitch" data-text="KINK">` + tagline
- [ ] `manifest.json`: `name`, `short_name`, ícones → `images/branding/cloudpath-icon-*.png`
- [ ] Favicons (`<link rel="icon">`) → ícone novo
- [ ] Player de música: círculo minimizado mostra a letra **"K"** → trocar por "C" ou pelo ícone
- [ ] Disclaimer do rodapé ("não é afiliado ao Kahoot") — **remover**: sem a menção ao Kahoot, o disclaimer perde a razão de existir
- [ ] `README.md`: título, descrição, badges

### Nomes internos (~500 ocorrências) — **opcional, baixa prioridade**
- [ ] Variáveis CSS `--kink-teal`, `--kink-space-md`, `--kink-transition`... → `--cp-*`
  - Ninguém vê. Só renomeie com busca-e-substitui global e teste visual completo depois.
  - **Não é pré-requisito da virada.** Cosmético de código.

### Infraestrutura
- [ ] SquareCloud: novo domínio `cloudpath.squareweb.app`
- [ ] Manter `kink.squareweb.app` **redirecionando** por alguns meses (links antigos, PWA instalado)
- [ ] `squarecloud.app`: campo `name`
- [ ] Repositório GitHub: renomear (o GitHub redireciona a URL antiga automaticamente)
- [ ] Firebase: `authDomain` e domínios autorizados no console

---

## Nome e posicionamento

"KINK is not Kahoot" era piada de projeto pessoal. **CloudPath** descreve o que a plataforma virou: trilhas de estudo + simulados para certificações AWS. Some a dependência de explicar o que a plataforma *não* é.

Tagline sugerida: **"Sua trilha para a nuvem"**.
