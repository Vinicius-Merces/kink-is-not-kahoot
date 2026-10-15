# CloudArena | Padrão oficial de sprites e spritesheets

**Situação:** padrão aprovado em teste local (14/10/2026). Implementação de suporte na branch `feature/cloudarena-sprites-preview`. A publicação e a substituição visual exigem também os PNGs finais no GitHub.

## Identidade visual

- O **herói** ocupa o lado esquerdo da batalha, olhando para a direita.
- Os **inimigos** ficam à direita, olhando para a esquerda.
- Inimigos comuns: fantasia com elementos de AWS/nuvem ligados ao nome e ao domínio.
- Chefes: visual mais épico. Conceito reservado: **Vorgrath, o Corruptor das Arquiteturas Seguras**, para `saa-c03 / secure-architectures`.
- Primeiro inimigo aprovado: **Sentinela GuardDuty** (`saa-c03 / secure-architectures`), com lança de energia azul, escudo e símbolos de proteção.
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

O nome registrado no código é **Sentinela GuardDuty**, recuperado da pool legada. Os demais inimigos e chefes permanecem com seus próprios nomes e sprites existentes. Não substituir o chefe por Vorgrath até os 16 frames dele estarem aprovados.

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


## Vitória do herói masculino (extensão aprovada)

Além dos 16 frames padrão, o herói masculino utiliza uma animação extra de **vitória** com quatro quadros dispostos em uma linha horizontal, em `images/arena/hero/masculino/victory.png`.

- Duração total: **1000 ms** (250 ms por quadro).
- Gatilho: `animateHero('victory')` ao vencer o encontro.
- Estado final: retorna ao `idle` por meio de `onComplete`.
- O PNG original aprovado tem resolução **2172 × 724 px**, com transparência RGBA.
- O carregamento é opcional: falha do arquivo da vitória não deve bloquear ataque, defesa ou morte do herói. Enquanto o PNG não estiver presente, o renderer mantém a pose de idle como fallback.
- O recorte segue o padrão geral de 15 px internos em cada lateral e 20 px no topo, mas com **uma única linha** em vez de quatro.

**Status dos arquivos:** o PNG aprovado de 2172 × 724 px está versionado no caminho acima. O arquivo legado de 361 × 150 px não deve ser usado como animação de vitória do renderer 4×1.


## Segundo inimigo comum: Arquimago das Chaves

A arena SAA-C03, domínio `secure-architectures`, usa temporariamente somente os quatro inimigos comuns já aprovados para a fase de testes:

- **Sentinela GuardDuty**, com escudo e lança azul.
- **Sentinela Multi-AZ**, com escudo e martelo de energia.
- **Arquimago das Chaves**, com cajado de cristal e magia de autenticação, voltado para a esquerda.
- **Guardião de Permissões**, com espada-chave e selo holográfico de políticas, voltado para a esquerda.

O `js/cloudarena.js` alterna somente entre os quatro nos encontros regulares. Os chefes continuam independentes. A variação fica fixa durante cada encontro e cada personagem só entra na rotação depois que seu PNG foi carregado. Novos inimigos podem ser acrescentados posteriormente na mesma lista.

**Spritesheets e temporização:** os três arquivos usam grade de 4×4 e fundo transparente. O renderer calcula as células usando as dimensões reais de cada PNG. `idle` tem quatro frames e fecha o loop em 1 segundo; `attack`, `hurt` e `death` têm quatro frames e duram 0,5 segundo cada. `attack` e `hurt` retornam ao `idle`; `death` segura no último quadro.

Caminhos dos assets:

- `images/arena/enemies/secure-architectures/sentinela-fortaleza-sheet.png`
- `images/arena/enemies/secure-architectures/sentinela-cloudshield-sheet.png`
- `images/arena/enemies/secure-architectures/arquimago-chaves-sheet.png`
- `images/arena/enemies/secure-architectures/guardiao-permissoes-sheet.png`

**Situação de publicação:** os três PNGs finais transparentes estão versionados na `main`. O Arquimago usa a última arte aprovada, orientada para a esquerda; a prancha de apresentação com fundo e rótulos não é carregada pelo site. A rotação considera somente variantes cujo asset foi carregado e mantém chefes fora dessa lista.
