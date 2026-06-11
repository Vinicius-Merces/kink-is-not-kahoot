# Gerador de Questões (Gemini)

Ferramenta **local** para gerar, em lote, novas questões para os simulados
AWS (CLF-C02, SAA-C03, DVA-C02) usando a API do Google Gemini, respeitando a
proporção de domínios já definida em `data/exams/{certId}/{level}.json`.

> ⚠️ Esta ferramenta roda **só localmente**. As pastas `node_modules/` e
> `output/` deste diretório estão no `.gitignore` e nunca devem ser
> commitadas. Sua chave de API também nunca deve ser commitada.

## 1. Instalação

```bash
cd scripts/question-generator
npm install
```

## 2. Configurar a API key

Adicione no arquivo `.env` da **raiz do projeto** (ele já está no
`.gitignore`):

```
GEMINI_API_KEY=sua-chave-aqui
```

Opcionalmente, para trocar o modelo padrão (`gemini-2.5-flash`):

```
GEMINI_MODEL=gemini-2.5-pro
```

## 3. Ver o plano antes de gastar requisições

```bash
node generate.js --dry-run
```

Isso mostra, para cada cert/nível, quantas questões já existem por domínio,
quantas faltam para atingir a meta e não chama a API.

## 4. Gerar questões

```bash
# tudo (todos os certs e níveis), meta padrão de 240 por pool
node generate.js

# só uma pool específica
node generate.js --certs=clf-c02 --levels=iniciante

# parâmetros customizados
node generate.js --certs=saa-c03 --levels=avancado --target=240 --batch=10 --delay=15000
```

Parâmetros aceitos (todos opcionais):

| Flag           | Padrão            | Descrição                                                       |
| -------------- | ----------------- | ---------------------------------------------------------------- |
| `--target`     | `240`              | Total de questões desejado por pool (cert + nível)                |
| `--batch`      | `10`               | Quantas questões pedir por chamada à API                          |
| `--delay`      | `15000` (15s)      | Pausa entre chamadas, para respeitar o limite do plano Free       |
| `--retries`    | `3`                | Tentativas por lote em caso de erro/JSON inválido                 |
| `--model`      | `gemini-2.5-flash` | Modelo do Gemini a usar                                           |
| `--certs`      | (todos)            | Filtra por cert(s), separados por vírgula (ex: `clf-c02,saa-c03`) |
| `--levels`     | (todos)            | Filtra por nível(is): `iniciante,medio,avancado`                  |
| `--domains`    | (todos)            | Filtra por domínio(s) específico(s) dentro da pool                |
| `--dry-run`    | -                  | Apenas mostra o plano, não chama a API                            |

O progresso é salvo a cada lote em
`output/{certId}-{level}.generated.json`, então o processo pode ser
interrompido (Ctrl+C) e retomado depois — ele continua de onde parou.

## 5. Revisar e mergear na base oficial

As questões geradas ficam em `output/*.generated.json` para revisão manual
(conferir clareza, corrigir eventuais erros técnicos, etc.). Quando estiver
satisfeito, rode:

```bash
# revisar o que será mergeado, sem alterar nada
node merge.js --dry-run

# mergear tudo que estiver em output/ para data/exams/
node merge.js

# mergear só uma pool específica
node merge.js --certs=clf-c02 --levels=iniciante
```

O merge ignora (deduplica) qualquer questão cujo `id` já exista na pool de
destino, adiciona as novas ao final de `data/exams/{certId}/{level}.json` e
remove o arquivo de staging correspondente.

## Como funciona a distribuição por domínio

A meta de questões por domínio é calculada a partir do peso (`weight`) de
cada domínio definido em `data/exams/{certId}/{level}.json`, usando o método
dos maiores restos (mesma lógica usada para sortear questões nos simulados).
O script gera apenas a diferença entre o que já existe (pool + staging) e a
meta calculada.
