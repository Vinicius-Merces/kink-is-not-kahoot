# CloudArena | Implementação de sprites (branch de preview)

O padrão completo está em [cloudarena-sprites.md](cloudarena-sprites.md).

## Implementado em código

- Herói masculino: tentativa de carregar `images/arena/hero/masculino/cloudarena-sheet.png`, com fallback seguro para o atlas masculino antigo enquanto o arquivo aprovado não estiver presente.
- Sentinela da Fortaleza: animação 4×4 via `images/arena/enemies/secure-architectures/sentinela-fortaleza-sheet.png`, com fallback para a representação antiga em caso de arquivo ausente.
- Player em canvas com imagem pré-carregada; idle 1 segundo; attack, hurt e death 500 ms.
- Recorte calculado pelas dimensões reais do PNG e insets de 15 px nas laterais e 20 px no topo.
- Layout responsivo para os novos canvas.

## Pendente para integração visual real

**Os dois PNGs aprovados nesta conversa ainda precisam entrar no GitHub.** O conector de escrita conseguiu alterar código e documentação, mas não transferiu automaticamente os binários existentes no contêiner desta conversa. Não considerar a substituição visual concluída antes de confirmar os arquivos no repositório.

O arquivo de teste aprovado nesta conversa, `cloudarena_teste_corrigido_v2.zip`, contém `assets/hero_sheet.png` e `assets/enemy_sheet.png`. Existe um instalador no repositório:

```bash
python scripts/install_cloudarena_art.py /caminho/para/cloudarena_teste_corrigido_v2.zip
```

Esse comando instala as duas imagens nos caminhos usados pelo código; **não** cria commit ou deploy automaticamente. Depois, testar o carregamento real em uma branch de preview.

## Chefe

O conceito visual **Vorgrath, o Corruptor das Arquiteturas Seguras**, fica reservado. O chefe atual não foi substituído porque não há spritesheet aprovado de 16 frames para ele.

## Publicação

Nenhum merge nem deploy deve ser feito antes de conferir PNGs, renderização, falhas de rede, mobile e compatibilidade dos demais personagens.
