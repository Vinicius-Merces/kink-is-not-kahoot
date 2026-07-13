# Backlog de narração (TTS) — estado real

> Este arquivo existe para o descompasso entre **conteúdo** e **áudio** não se perder.
> Atualize sempre que mexer em capítulo que já tenha MP3.

## Fato que domina tudo

A correção de pronúncia (re-grafia PT-BR no `glossary.py`) **invalida os 20 MP3s
atuais do SAA**. Eles têm:

- termos em inglês mal pronunciados (fonemas descartados pela voz pt-BR);
- o bug do `RAM`, cujo IPA soletrava **S-A-M** — o áudio publicado diz "SAM".

Ou seja: **todo áudio do SAA será regerado de qualquer forma.** A pergunta
"o conteúdo mudou?" não decide *se* regera — decide apenas se o **roteiro
precisa ser reescrito antes**.

## Matriz de regeneração

### A) Roteiro OK — só regerar o áudio (pronúncia)
Rodar `generate.py` sem tocar no texto.

| Trilha | Capítulos | Qtd |
|---|---|---|
| SAA | 1, 2, 5, 10, 11, 13, 14, 15, 16, 18, 19 | 11 |

### B) Roteiro precisa ser EDITADO (conteúdo mudou) e depois regerado

| Cap | Por que mudou |
|---|---|
| SAA 3 | conteúdo novo adicionado (Parte 1) |
| SAA 4 | **diagrama novo** (VPC) |
| SAA 6 | **diagrama novo** (alta disponibilidade) |
| SAA 7 | **diagrama novo** (DR) |
| SAA 8 | conteúdo novo adicionado (Parte 1) |
| SAA 9 | conteúdo novo adicionado (Parte 1) |
| SAA 12 | conteúdo novo adicionado (Parte 1) |
| SAA 17 | conteúdo novo **+ diagrama** (híbrido) |
| SAA 20 | conferir: marcado como desatualizado no backlog anterior |

**9 capítulos.**

### C) Roteiro NOVO (nunca teve áudio)

| Trilha | Capítulos | Qtd | Observação |
|---|---|---|---|
| SAA | 21 | 1 | capítulo novo: "Cenários integrados" |
| DEA | 1–13 | 13 | diagramas nos caps 2, 5, 6 |
| DVA | 1–14 | 14 | diagramas nos caps 2, 8, 10 |

**28 capítulos.**

---

## Decisão editorial pendente: como narrar um diagrama

Um SVG não se lê em voz alta. Há 10 diagramas no total (SAA 4, DVA 3, DEA 3).
Três caminhos:

1. **Ignorar** — o áudio não menciona o diagrama. Simples, mas o áudio fica
   mais pobre exatamente nos pontos onde o visual foi criado *porque* o
   conceito é difícil só com palavras.
2. **Referenciar** — "veja o diagrama na tela". Ruim para áudio passivo
   (fone no ônibus, que é o caso de uso real).
3. **Descrever em prosa falada** (recomendado) — 20–40s por diagrama,
   convertendo a estrutura visual em explicação linear. Ex.: os três modos de
   invocação do Lambda viram "no modo síncrono, quem chama espera a resposta e
   o erro volta pra ele; no assíncrono, o Lambda enfileira, tenta duas vezes e
   manda pra DLQ; no event source mapping, o Lambda faz polling e um lote ruim
   trava o shard". Bônus: melhora acessibilidade para quem usa leitor de tela.

**Recomendação: opção 3.** Custa mais roteiro, mas é o único caminho em que o
áudio continua sendo autossuficiente.

---

## Regras editoriais dos roteiros (herdadas — manter)

- Blocos de código JSON/CLI: **parafraseados**, nunca lidos literalmente.
- Tabelas: convertidas em comparações fluidas, não lidas célula a célula.
- Lab prático: menção breve (não serve para áudio passivo).
- Checkpoint: vira diálogo (Francisca pergunta / Antonio responde).
- Siglas (IAM, STS, VPC, KMS...): `SAY()` → soletradas.
- Termos em inglês: `PHON()` → re-grafia PT-BR (ver `glossary.py`).

## Ordem sugerida

1. **Validar a pronúncia primeiro** (`test_pronuncia.py`) — nada de regerar 20
   capítulos antes do teste de ouvido de 40 segundos.
2. **Lote SAA** (11 regerações + 9 edições + cap 21) — é a prova de setembro.
3. **Lote DEA** (13 roteiros) — prova de novembro.
4. **Lote DVA** (14 roteiros).
