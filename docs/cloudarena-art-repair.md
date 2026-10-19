# CloudArena: correção dos sprites, 19/10/2026

## Causas verificadas

- Imagens legadas eram solicitadas enquanto o canvas ainda decodificava; eventos de erro posteriores reabriam o emoji mesmo com a arte carregada.
- Os bosses não tinham renderer nem arquivos associados. Aion e Mnemósine estavam apenas nas prévias.
- Faltava a pool 11–20. Havia quatro, não cinco, inimigos na primeira pool.
- Os cinco WebPs mecha e o PNG publicado de Permissões estavam corrompidos.
- O Draco publicado era uma prancha 4×1, interpretada como 4×4.
- O PNG publicado do Arquimago já continha uma faixa transparente cortando o corpo. O original aprovado recuperado está inteiro.
- Recortes fixos e escala CSS de boss podiam cortar ou deformar os sprites.

## Implementação

- Catálogo `images/arena/v2/catalog.json`: 20 comuns (5 por faixa 1–10, 11–20, 21–30 e 31–40) e bosses Vorgrath (10), Nexarion (20), Aion (30), Mnemósine (40).
- Depois do nível 40, reutiliza o catálogo aprovado; não inventa novos personagens e não solicita placeholders legados. As outras certificações também usam o catálogo enquanto não têm artes exclusivas.
- Uma superfície canvas por inimigo, cache de decode e preservação do campo de batalha entre perguntas. Sem troca para `img`/emoji durante dano.
- Retângulos explícitos, proporção preservada e padding transparente. A geração técnica não modifica os originais aprovados. O Draco foi refeito com referência à arte aprovada para completar as quatro ações ausentes na prancha antiga.
- Idle 1 segundo; ações 0,5 segundo. O hurt de Nexarion mantém os quatro frames por fase aprovados; demais ações de boss têm oito.
- Primeira derrota do boss inicia enrage, restaura HP e rounds; segunda fase usa ataque padrão/pesado com escolha aleatória 50/50; só a derrota final concede vitória.
- Balanceamento progressivo: sempre duas fases (normal e enraged). Níveis 10/20/30/40 usam 1/2/3/4 rodadas por fase, respectivamente (2/4/6/8 perguntas totais). Depois do 40 mantém o teto de quatro rodadas por fase. O Modo Desafio preserva seus valores próprios. Encontros antigos salvos adotam a nova duração sem perder a fase atual.
- A fase e a identidade visual do encontro são mantidas na retomada. Entrada/saída de tela cancela loops; controles ficam bloqueados durante a resolução de ações.

## Verificação reproduzível

```sh
node --check js/cloudarena.js
node --check js/cloudarena-sprites.js
node tests/arena-sprites.test.cjs
node tests/arena-combat.test.cjs
python scripts/validate_arena_catalog.py
```

Galeria manual: `/tests/cloudarena-art-review.html`, incluindo estados enraged e death.

Os testes Node usam relógio/canvas simulados, não equivalem a uma sessão real em navegador. A conferência visual das folhas foi feita com imagens de contato. Verificar a galeria no desktop/celular e o combate em produção após o deploy SquareCloud.
