"""Roteiro DVA-C02 Capitulo 13 — Elastic Beanstalk para desenvolvedores."""

from glossary import SAY, EMPH, BRK, PHON

BEANSTALK = PHON("ˈbinstɔk", "Beanstalk")
ALL_AT_ONCE = PHON("ɔl æt wʌns", "all at once")
ROLLING = PHON("ˈroʊlɪŋ", "rolling")
ADDITIONAL_BATCH = PHON("ˈroʊlɪŋ wɪð əˈdɪʃənəl bætʃ", "rolling with additional batch")
IMMUTABLE = PHON("ɪˈmjutəbəl", "immutable")
TRAFFIC_SPLITTING = PHON("ˈtræfɪk ˈsplɪtɪŋ", "traffic splitting")
BLUE_GREEN = PHON("blu ɡrin", "blue green")
SWAP = PHON("swɑp", "swap")
CNAME = PHON("si neɪm", "CNAME")
EBEXTENSIONS = PHON("i bi ɪkˈstɛnʃənz", ".ebextensions")
CRON_YAML = PHON("krɑn ˈjæməl", "cron.yaml")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo treze: Elastic {BEANSTALK} para desenvolvedores. Uma "
            f"tabela decide quase tudo aqui: as políticas de deployment — "
            f"downtime, capacidade e velocidade de rollback."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- Politicas ----
    {
        "voice": "antonio",
        "text": (
            f"A tabela sagrada das políticas. {ALL_AT_ONCE}: derruba tudo e "
            f"sobe a nova — TEM downtime; rollback é redeploy manual. "
            f"{ROLLING}: atualiza em lotes — sem downtime, mas capacidade "
            f"REDUZIDA durante o deploy, e rollback lento. "
            f"{ADDITIONAL_BATCH}: um lote extra primeiro — capacidade total "
            f"mantida."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} {IMMUTABLE}: sobe um conjunto NOVO de instâncias em "
            f"paralelo — capacidade total, e o rollback é rápido e seguro: "
            f"descarta as novas. {TRAFFIC_SPLITTING}: o canário do "
            f"{BEANSTALK} — uma porcentagem do tráfego vai às instâncias "
            f"novas antes de completar. E {BLUE_GREEN}: ambiente clone com "
            f"{SWAP} de {CNAME} — rollback INSTANTÂNEO, é só trocar de volta."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- ebextensions ----
    {
        "voice": "francisca",
        "text": (
            f"Customização: arquivos ponto config em {SAY('YAML')} dentro da "
            f"pasta {EBEXTENSIONS} na raiz do pacote — variáveis de ambiente, "
            f"pacotes do sistema, comandos e recursos extras. Cron em worker "
            f"environment via {CRON_YAML}. E o aviso de arquitetura: o "
            f"{BEANSTALK} por baixo é CloudFormation — deletar o ambiente "
            f"DESTRÓI os recursos dele; banco de produção vive FORA do "
            f"ambiente, conectado por variáveis."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: deploy sem downtime, sem custo extra de "
            f"instâncias, aceitando capacidade reduzida?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"{ROLLING} — lotes sem instâncias adicionais; o custo é operar com menos capacidade.",
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: instalar um pacote do sistema e definir variáveis em "
            f"todas as instâncias?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": f"Arquivo ponto config na pasta {EBEXTENSIONS} do bundle da aplicação.",
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: por que NÃO criar o {SAY('RDS')} de produção dentro do "
            f"ambiente {BEANSTALK}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"O ciclo de vida do banco fica acoplado ao ambiente — terminar o "
            f"ambiente destrói o banco. Produção usa {SAY('RDS')} externo."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo treze. No próximo e último, "
            f"troubleshooting, otimização e a tabela mestre do {SAY('DVA')}. "
            f"Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
