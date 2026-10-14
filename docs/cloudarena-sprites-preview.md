# CloudArena: prévia de sprites

Esta branch prepara o motor do CloudArena para o novo herói masculino (4 quadros por estado) e animações de 4 quadros da Sentinela da Fortaleza, inimigo comum SAA-C03 / secure-architectures.

## Assets necessários

Os arquivos binários foram entregues como pacote ZIP nesta conversa; eles **ainda precisam ser copiados para a branch** antes de publicar uma prévia online:

- `images/arena/hero/masculino/{idle,attack,hurt,death,victory}.png`
- `images/arena/hero/masculino/atlas.json`
- `images/arena/enemies/secure-architectures/{idle,attack,hurt,death}.png`
- `images/arena/enemies/secure-architectures/atlas.json`

As folhas têm 4 células de 450×450 cada (1800×450), contendo pelo menos 50 px de margem transparente por célula. A animação `victory` do herói é temporária.

## Chefe Vorgrath

O conceito do chefe foi aprovado visualmente, mas não existe um spritesheet final de 16 poses pronto para integração. Não renomear ou substituir o chefe existente até que os 16 frames sejam gerados e aprovados.

## Testes antes de deploy

1. Copiar os arquivos PNG e atlas.json para os caminhos acima.
2. Testar o HTML de prévia local incluído no ZIP fornecido na conversa.
3. Abrir a SAA-C03 e verificar a Sentinela nos quatro estados.
4. Conferir se herói e inimigo não apresentam recorte, pulos de alinhamento ou sobreposição de frames.
5. Corrigir o timing do golpe e a animação de vitória, se necessário.

Esta branch não altera o banco de questões e não publica em produção.
