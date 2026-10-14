# CloudArena | Padrão oficial de sprites e spritesheets

**Situação:** padrão aprovado em teste local (14/10/2026). Implementação de suporte na branch `feature/cloudarena-sprites-preview`. A publicação e a substituição visual exigem também os PNGs finais no GitHub.

## Identidade visual

- O **herói** ocupa o lado esquerdo da batalha, olhando para a direita.
- Os **inimigos** ficam à direita, olhando para a esquerda.
- Inimigos comuns: fantasia com elementos de AWS/nuvem ligados ao nome e ao domínio.
- Chefes: visual mais épico. Conceito reservado: **Vorgrath, o Corruptor das Arquiteturas Seguras**, para `saa-c03 / secure-architectures`.
- Primeiro inimigo aprovado: **Sentinela da Fortaleza** (`saa-c03 / secure-architectures`), com martelo de energia azul, escudo e símbolos de proteção.
- Herói masculino: guardião de armadura escura/dourada com efeitos ciano. Herói feminino mantém assets legados até haver equivalente aprovado.

## Formato mestre

Cada personagem utiliza **um PNG com 16 poses**, grade 4 colunas × 4 linhas e fundo realmente transparente.

| Linha (índice) | Estado | Frames | Duração total | Final |
|---|---|---|---|---|
| 0 | `idle` | 4 | **1000 ms** | Repete continuamente |
| 1 | `attack` | 4 | **500 ms** | Retorna a idle |
| 2 | `hurt` | 4 | **500 ms** | Retorna a idle |
| 3 | `death` | 4 | **500 ms** | Mantém o último quadro |

Em `idle`, são 250 ms por quadro. Nas demais animações, 125 ms por quadro. Para personagens que não tenham a animação de `victory`, a vitória usa temporariamente uma pose de idle, sem inventar frames inexistentes.

**O tamanho do PNG não é fixo.** O recorte usa os limites da célula em função da largura/altura reais: `x0 = round(col * largura / 4)`, `x1 = round((col + 1) * largura / 4)`; equivalente no eixo Y. Nunca presumir células de 450 × 450 em folhas de outra resolução.

### Margens e enquadramento

- Reserva de 50 px ou mais entre poses na criação artística, sempre que a resolução da folha permitir.
- **Recorte interno do teste aprovado:** remover aproximadamente 15 px à esquerda e à direita de cada célula e 20 px do topo, sempre **dentro dos limites daquela célula**, sem ler pixels adjacentes.
- Abaixar o enquadramento no destino, mantendo o mesmo ponto de apoio dos pés em todos os quadros.
- Fixar o canvas ao mesmo tamanho/posição no DOM; não recriar elementos ao avançar um quadro.
- Evitar extravasamento de espadas, efeitos e mantos para a célula vizinha.
- Se uma pose não couber, revisar a arte/atlas em vez de deslocar o recorte para outra célula.

### Reprodução

1. Pré-carregar e reutilizar o mesmo `Image` para todos os 16 frames.
2. Reproduzir via `canvas.drawImage` e `requestAnimationFrame`, com tempo decorrido real, e não trocando `img.src` a cada quadro.
3. `idle` é o estado permanente padrão e **não pode piscar nem reiniciar por timers concorrentes**.
4. Ação nova interrompe a animação anterior. `attack` e `hurt` regressam a `idle` automaticamente ao completar 500 ms.
5. `death` termina em 500 ms e congela no último quadro.
6. Um elemento de combate removido do DOM deve interromper sua animação para não acumular loops em segundo plano.
7. O impacto deve ocorrer sincronizado ao quadro de ataque, e os controles devem funcionar com imagem ausente (fallback legado).

## Caminhos no projeto

Arquivos **mestres, sem recompressão ou redesenho**, derivados das artes aprovadas no teste local:

- `images/arena/hero/masculino/cloudarena-sheet.png` (herói masculino, 4×4)
- `images/arena/enemies/secure-architectures/sentinela-fortaleza-sheet.png` (inimigo comum, 4×4)

O nome registrado no código continua **Sentinela da Fortaleza**. Os demais inimigos e chefes permanecem com seus próprios nomes e sprites existentes. Não substituir o chefe por Vorgrath até os 16 frames dele estarem aprovados.

## Validação obrigatória antes de publicar

1. PNG existente e carregável pelo navegador; dimensões compatíveis com grade 4×4.
2. Cada animação possui exatamente 4 células, sem invasão de outra linha/coluna.
3. `idle` funciona sozinho por 30 segundos sem flicker, tremor ou múltiplos loops.
4. `attack` e `hurt` rodam por 500 ms, e retornam ao `idle` automaticamente.
5. `death` dura 500 ms e mantém o último frame.
6. Testar renderização em desktop e celular, inclusive mudança de pergunta e navegação entre telas.
7. Conferir que herói feminino, inimigos de outros domínios e chefes não sofreram regressão.
8. Executar validações do projeto (bancos de questões/arena), além de análise sintática de `js/cloudarena.js`.

## Histórico

- 14/10/2026: concept art e 16 poses do novo herói e da Sentinela aprovadas; teste local de tempos e enquadramento aprovado.
- A integração GitHub do código só estará totalmente operacional quando os **dois PNGs mestres** também estiverem versionados nos caminhos documentados.
