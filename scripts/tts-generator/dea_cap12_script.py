"""Roteiro DEA-C01 Capitulo 12 — Analise, SQL e visualizacao."""

from glossary import SAY, EMPH, BRK, PHON

QUICKSIGHT = PHON("ˈkwɪksaɪt", "QuickSight")
SPICE = PHON("spaɪs", "SPICE")
DIRECT_QUERY = PHON("dɪˈrɛkt ˈkwɪri", "direct query")
ROW_NUMBER = PHON("roʊ ˈnʌmbɚ", "ROW_NUMBER")
LAG = PHON("læɡ", "LAG")
LEAD = PHON("lid", "LEAD")
PIVOT = PHON("ˈpɪvət", "PIVOT")
CTE = PHON("si ti i", "CTE")
CTES = PHON("si ti iz", "CTEs")
DATABREW = PHON("ˈdeɪtəbru", "DataBrew")
DATA_WRANGLER = PHON("ˈdeɪtə ˈræŋɡlɚ", "Data Wrangler")
ROLLING_AVERAGE = PHON("ˈroʊlɪŋ ˈævrɪdʒ", "rolling average")
HAVING = PHON("ˈhævɪŋ", "HAVING")
COALESCE_FN = PHON("ˌkoʊəˈlɛs", "COALESCE")
RLS = PHON("ɛr ɛl ɛs", "row-level security")

BLOCKS = [
    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Capítulo doze: análise, {SAY('SQL')} e visualização. O domínio "
            f"três dedica uma task inteira a isso — é onde o {SAY('DEA')} testa "
            f"se você consome o dado que o pipeline produziu."
        ),
    },
    {"voice": "francisca", "text": BRK(800)},

    # ---- SQL analitico ----
    {
        "voice": "antonio",
        "text": (
            f"{SAY('SQL')} analítico — os padrões que a prova lê com você. Joins "
            f"múltiplos com group by e {HAVING} — o filtro DEPOIS da agregação. "
            f"{CTES}, o WITH, encadeando etapas legíveis — a base do "
            f"{SAY('ELT')}. E as window functions: {ROW_NUMBER} over partition "
            f"by, ordenando pela data decrescente e filtrando linha um — o "
            f"padrão de DEDUPLICAÇÃO mantendo o registro mais recente."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} A {ROLLING_AVERAGE} — média móvel, citada nominalmente "
            f"no exam guide: average over com rows between seis preceding and "
            f"current row — a média dos últimos sete dias. {LAG} e {LEAD} "
            f"comparam com a linha anterior ou seguinte — variação dia a dia. E "
            f"{PIVOT} transforma linhas em colunas — no Redshift e no Athena, ou "
            f"com case when mais agregação."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Limpeza ----
    {
        "voice": "francisca",
        "text": (
            f"Limpeza de dados — onde fazer. {DATABREW} para limpeza visual sem "
            f"código, com perfil automático do dataset. Glue e Spark para "
            f"limpeza em escala dentro do pipeline. {SAY('SQL')} no Athena ou "
            f"Redshift para limpeza declarativa — case, {COALESCE_FN}, trim, "
            f"cast. Lambda para validação leve por registro. E o SageMaker "
            f"{DATA_WRANGLER} quando o destino é machine learning."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- QuickSight ----
    {
        "voice": "antonio",
        "text": (
            f"{QUICKSIGHT} — o {SAY('BI')} da {SAY('AWS')}. A decisão central: "
            f"{SPICE} versus {DIRECT_QUERY}. O {SPICE} é a engine in-memory — "
            f"dashboards rápidos, alivia a fonte, dados atualizados por refresh "
            f"agendado. {DIRECT_QUERY} consulta a fonte a cada visual — sempre "
            f"atual, mas cada refresh re-escaneia e re-cobra. A pegadinha: "
            f"'dashboard sobre o Athena ficou caro' — resposta: importar para o "
            f"{SPICE}."
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{BRK(400)} Mais três pontos: {RLS} — cada vendedor vê só a própria "
            f"região NO DASHBOARD, por regras de usuário no dataset. A edição "
            f"Enterprise traz {RLS}, conexão com {SAY('VPC')} e embedding. E os "
            f"tipos de visual: linha para tendência temporal, barra para "
            f"comparação entre categorias, heatmap para duas dimensões, scatter "
            f"para correlação, e {SAY('KPI')} para número contra meta — com "
            f"alertas de threshold e detecção de anomalias nativa."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    # ---- Notebooks ----
    {
        "voice": "francisca",
        "text": (
            f"Exploração com notebooks: Athena for Apache Spark — notebook "
            f"PySpark serverless que inicia em segundos, exploração sem cluster. "
            f"Jupyter e SageMaker para Python livre e preparação de features. "
            f"{SAY('EMR')} Studio para notebooks sobre clusters grandes. "
            f"'Cientistas querem explorar o lake com Spark, sem infraestrutura': "
            f"Athena Spark."
        ),
    },
    {"voice": "francisca", "text": BRK(1000)},

    # ---- Checkpoint ----
    {
        "voice": "francisca",
        "text": (
            f"Revisão. Primeira: remover duplicatas mantendo o registro mais "
            f"recente de cada chave, via {SAY('SQL')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{ROW_NUMBER} over partition by chave, order by data decrescente — "
            f"e filtrar linha igual a um."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Segunda: dashboard do {QUICKSIGHT} sobre o Athena ficou caro — "
            f"cada visual re-escaneia o {SAY('S3')}?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"Importar o dataset para o {SPICE} com refresh agendado — os "
            f"visuais servem da memória."
        ),
    },
    {"voice": "antonio", "text": BRK(600)},
    {
        "voice": "francisca",
        "text": (
            f"Terceira: cada gerente regional deve ver apenas os dados da "
            f"própria região no mesmo dashboard?{BRK(800)}"
        ),
    },
    {
        "voice": "antonio",
        "text": (
            f"{RLS} do {QUICKSIGHT} por regras de usuário. Se a restrição "
            f"precisa valer em QUALQUER ferramenta, aí é Lake Formation."
        ),
    },
    {"voice": "antonio", "text": BRK(1000)},

    {
        "voice": "francisca", "style": "cheerful",
        "text": (
            f"Isso encerra o capítulo doze. No próximo, operações, monitoramento "
            f"e qualidade de dados. Até lá!"
        ),
    },
    {"voice": "francisca", "text": BRK(1500)},
]
