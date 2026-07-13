"""Helpers e tratamento fonetico compartilhados entre os roteiros de capitulo.

POR QUE MUDOU (leia antes de editar)
------------------------------------
A versao anterior envolvia os termos em ingles em <phoneme alphabet="ipa">.
Isso NAO funciona com Antonio/Francisca: sao vozes neurais de locale unico
(pt-BR) e so realizam o inventario fonetico do proprio idioma. Fonemas que
nao existem em portugues (θ, æ, ɹ, ʊ, ɚ, ŋ...) sao descartados ou aproximados
mal pelo motor -- e o resultado e exatamente o efeito de "letras sumindo"
no meio da palavra.

A abordagem correta para voz de locale unico e a RE-GRAFIA: escrever o termo
com grafemas portugueses, para a voz ler usando apenas sons que ela possui.
O alvo nao e "ingles perfeito" -- e o ingles como um profissional brasileiro
pronuncia, que e justamente o que soa natural para quem escuta.

COMO FUNCIONA
-------------
Os roteiros ja chamam PHON("ipa", "texto") em ~456 lugares, e o IPA anotado
ali esta correto. Entao PHON deixou de emitir a tag <phoneme> e passou a
CONVERTER esse IPA para grafia portuguesa. Nenhum roteiro precisou ser editado.

Ordem de resolucao de cada termo:
  1. RESPELL          -> re-grafia revisada a mao (prioridade; ajuste aqui o
                         que soar estranho ao seu ouvido)
  2. ipa_to_ptbr(ipa) -> transdutor automatico, para todo o resto

REGRAS DE GRAFIA PT-BR QUE O TRANSDUTOR RESPEITA
------------------------------------------------
  * "g" antes de e/i soa /ʒ/  -> para /g/ duro usa "gu"  (gateway -> Gueiuei)
  * "c" antes de e/i soa /s/  -> para /k/ usa "qu"        (check -> tcheque)
  * "s" entre vogais soa /z/  -> para /s/ usa "ss"        (access -> akssess)
  * "h" e MUDO em portugues   -> o /h/ ingles vira "r"    (hub -> rab)
  * "w" nao e nativo          -> vira "u"                 (way -> uei)
  * "th" nao existe           -> vira "t"                 (throughput -> truput)
  * o acento grafico marca a silaba tonica; sem ele o portugues aplica a regra
    padrao e erra a tonica (por isso "Denai" com acento: "Denái")
"""

# ---------------------------------------------------------------------------
# Modo fonetico
#   "respell" (padrao) -> re-grafia em portugues. Use este.
#   "ipa"              -> volta a emitir <phoneme ipa> (comportamento antigo,
#                         mantido apenas para comparacao A/B).
# ---------------------------------------------------------------------------
PHONETIC_MODE = "respell"

SAY = lambda s: f'<say-as interpret-as="characters">{s}</say-as>'
EMPH = lambda s: f'<emphasis level="moderate">{s}</emphasis>'
BRK = lambda ms: f'<break time="{ms}ms"/>'


# ---------------------------------------------------------------------------
# Transdutor IPA -> grafia PT-BR
# ---------------------------------------------------------------------------

# Vogais e ditongos: (forma atona, forma tonica com acento)
_VOWELS = {
    "aɪ": ("ai", "ái"),
    "eɪ": ("ei", "êi"),
    "oʊ": ("ou", "ôu"),
    "aʊ": ("au", "áu"),
    "ɔɪ": ("oi", "ói"),
    "ɪə": ("ia", "ía"),
    "ɛə": ("ea", "éa"),
    "iː": ("i", "í"),
    "uː": ("u", "ú"),
    "ɔː": ("o", "ó"),
    "ɑː": ("a", "á"),
    "ɜr": ("er", "ér"),
    "ɚ": ("er", "ér"),
    "ɝ": ("er", "ér"),
    "ə": ("a", "á"),
    "ɪ": ("i", "í"),
    "ʊ": ("u", "ú"),
    "ɛ": ("e", "é"),
    "æ": ("e", "é"),
    "ʌ": ("a", "á"),
    "ɑ": ("a", "á"),
    "ɔ": ("o", "ó"),
    "ɜ": ("e", "ê"),
    "i": ("i", "í"),
    "u": ("u", "ú"),
    "e": ("e", "ê"),
    "o": ("o", "ô"),
    "a": ("a", "á"),
}

# Consoantes (chaves multi-caractere sao testadas primeiro)
_CONSONANTS = {
    "tʃ": "tch",
    "dʒ": "dj",
    "ʃ": "ch",
    "ʒ": "j",
    "θ": "t",   # nao existe em PT: aproximacao usual
    "ð": "d",
    "ŋ": "n",
    "h": "r",   # /h/ ingles = "r" inicial do portugues (aspirado)
    "ɹ": "r",
    "r": "r",
    "w": "u",
    "j": "i",
    "ɡ": "g",
    "g": "g",
    "k": "k",   # resolvido depois em c/qu/que conforme o contexto
    "s": "s",   # resolvido depois em s/ss conforme o contexto
    "p": "p", "b": "b", "t": "t", "d": "d", "f": "f", "v": "v",
    "m": "m", "n": "n", "l": "l", "z": "z", "x": "ks",
}


def _tokenize_ipa(ipa: str):
    """Quebra a string IPA em tuplas (tipo, simbolo, tonico)."""
    out = []
    i = 0
    stress_next = False
    keys = sorted(
        list(_VOWELS.keys()) + list(_CONSONANTS.keys()), key=len, reverse=True
    )
    while i < len(ipa):
        ch = ipa[i]
        if ch == "\u02c8":        # tonica primaria
            stress_next = True
            i += 1
            continue
        if ch in ("\u02cc", "."):  # tonica secundaria / separador: ignora
            i += 1
            continue
        if ch == " ":
            out.append(("space", " ", False))
            i += 1
            continue
        for k in keys:
            if ipa.startswith(k, i):
                if k in _VOWELS:
                    out.append(("v", k, stress_next))
                    stress_next = False   # a tonica cai na 1a vogal apos o acento
                else:
                    out.append(("c", k, False))
                i += len(k)
                break
        else:
            i += 1   # simbolo desconhecido: descarta
    return out


def ipa_to_ptbr(ipa: str) -> str:
    """Converte IPA (ingles) em grafia portuguesa aproximada."""
    tokens = _tokenize_ipa(ipa)
    out = []

    for idx, (kind, sym, stressed) in enumerate(tokens):
        if kind == "space":
            out.append(" ")
            continue

        if kind == "v":
            atona, tonica = _VOWELS[sym]
            out.append(tonica if stressed else atona)
            continue

        graph = _CONSONANTS[sym]

        nxt = tokens[idx + 1] if idx + 1 < len(tokens) else None
        nxt_is_vowel = nxt is not None and nxt[0] == "v"
        nxt_front = False
        if nxt_is_vowel:
            nxt_graph = _VOWELS[nxt[1]][1 if nxt[2] else 0]
            nxt_front = nxt_graph[0] in "eiéêí"

        prev = tokens[idx - 1] if idx > 0 else None
        prev_is_vowel = prev is not None and prev[0] == "v"

        if graph == "k":
            if nxt_front:
                graph = "qu"       # /k/ antes de e,i -> "qu"
            elif nxt_is_vowel:
                graph = "c"        # /k/ antes de a,o,u -> "c"
            elif nxt is None or nxt[0] == "space":
                graph = "que"      # /k/ final -> "que" (evita "c" solto)
            else:
                graph = "c"

        elif graph == "g":
            if nxt_front:
                graph = "gu"       # /g/ antes de e,i -> "gu"

        elif graph == "s":
            if prev_is_vowel and nxt_is_vowel:
                graph = "ss"       # /s/ entre vogais -> "ss" (senao vira /z/)

        out.append(graph)

    word = "".join(out)

    # Limpeza: encontros que o portugues nao le (ou le mal)
    for bad, good in (
        ("cch", "kch"),    # detection: "ditecchan" -> "ditekchan"
        ("djd", "djed"),   # managed:   "menidjd"   -> "menidjed"
        ("ktd", "kted"),
        ("uu", "u"),
        ("ii", "i"),
        ("cc", "c"),
    ):
        word = word.replace(bad, good)
    return word


# ---------------------------------------------------------------------------
# RESPELL: re-grafias revisadas a mao (prioridade sobre o transdutor).
#
# ESTE E O UNICO LUGAR QUE VOCE PRECISA TOCAR para afinar a pronuncia.
# A chave e o TEXTO em ingles como aparece no roteiro (case-insensitive).
# ---------------------------------------------------------------------------
RESPELL = {
    # --- curtos e de alto risco (em PT mudariam completamente de som) ---
    "deny": "Denái",
    "allow": "Aláu",
    "role": "rôu",
    "roles": "rôus",
    "github": "Guitchi Rábi",

    # --- servicos e recursos AWS mais falados ---
    "gateway": "Guêituei",
    "nat gateway": "Nét Guêituei",
    "transit gateway": "Trânzit Guêituei",
    "internet gateway": "Ínternet Guêituei",
    "dynamodb": "Dáinamou D B",
    "auto scaling": "Ôto Isquêilin",
    "load balancer": "Lôud Bálanser",
    "load balancers": "Lôud Bálansers",
    "target group": "Târguet Grúpe",
    "launch template": "Lóntch Têmpleit",
    "placement group": "Plêismant Grúpe",
    "user pool": "Iúzer Púl",
    "identity pool": "Aidêntiti Púl",
    "identity center": "Aidêntiti Cênter",
    "secrets manager": "Sícrets Mánadjer",
    "access analyzer": "Ákssess Ánalaizer",
    "trusted advisor": "Trâstid Ádvaizer",
    "savings plans": "Sêivings Plâns",
    "read replica": "Ríd Réplica",
    "opensearch": "Ôupen Sârtch",
    "privatelink": "Práivat Línque",
    "peering": "Píerin",
    "subnet": "Sâbnet",
    "endpoint": "Êndpoint",
    "throughput": "Trúput",
    "workload": "Uârklôud",
    "failover": "Fêilôuver",
    "cold start": "Côud Istárte",
    "provisioned concurrency": "Províjand Concârensi",
    "health check": "Rélf Tchéque",
    "sticky sessions": "Istíqui Séchans",
    "cross-zone": "Cróss Zôun",
    "lifecycle hook": "Láifsaikou Rúque",
    "warm standby": "Uórm Istêndbai",
    "standby": "Istêndbai",
    "pilot light": "Páilot Láite",
    "spot": "Ispóte",
    "sidecar": "Sáidcar",
    "service discovery": "Sârvis Discâveri",
    "trust policy": "Trâst Pólissi",
    "permission set": "Permíchan Sét",
    "permission boundary": "Permíchan Báundari",
    "instance profile": "Ínstans Prôufail",
    "execution role": "Eksequiúchan rôu",
    "active directory": "Áctiv Dairéctori",
    "event source": "Ivênt Sórs",
    "scale-in": "isquêil ín",
    "scale-out": "isquêil áut",
    "backup and restore": "Bécape end Ristór",

    # --- CORRECAO DE BUG: o IPA do roteiro soletrava S-A-M em vez de R-A-M ---
    "ram": "Rám",

    # --- termos frequentes promovidos do transdutor para revisao manual ---
    "sigv4": "Síg Vi Fór",
    "throttling": "Trótlin",
    "routing policy": "Rátin Pólissi",
    "control plane": "Cantrôul Pleine",
    "data plane": "Dêita Pleine",
    "exactly-once": "Igzéctli Uans",
    "at-least-once": "Ét Líst Uans",
    "websocket": "Uéb Sóquet",
    "transfer family": "Trénsfer Fémili",
    "target tracking": "Târguet Tréquin",
    "step scaling": "Stép Isquêilin",
    "network firewall": "Nétuerk Fáiaruol",
    "kinesis data streams": "Quinéssis Dêita Strims",
    "graviton": "Grévitan",
    "global database": "Glôubal Dêitabeis",
    "fault tolerance": "Fólt Tólerans",
    "app runner": "Épe Râner",
    "bastion host": "Béstian Rôust",
    "bucket": "Báquet",
    "quicksight": "Cuíque Sáite",
}


def PHON(ipa: str, text: str) -> str:
    """Rende um termo em ingles de modo que a voz pt-BR consiga pronuncia-lo.

    Mantem a MESMA assinatura de antes, entao os ~456 usos espalhados pelos
    roteiros continuam funcionando sem nenhuma edicao.
    """
    if PHONETIC_MODE == "ipa":   # comportamento legado, so para comparacao A/B
        return f'<phoneme alphabet="ipa" ph="{ipa}">{text}</phoneme>'

    override = RESPELL.get(text.strip().lower())
    if override:
        return override
    return ipa_to_ptbr(ipa)


# ---------------------------------------------------------------------------
# Constantes compartilhadas (nomes preservados: varios roteiros as importam)
# ---------------------------------------------------------------------------
ROLE = PHON("ɹoʊl", "role")
DENY = PHON("dɪˈnaɪ", "Deny")
ALLOW = PHON("əˈlaʊ", "Allow")
GITHUB = PHON("ˈɡɪthʌb", "GitHub")
IDENTITY_CENTER = PHON("aɪˈdɛntɪti ˈsɛnɚ", "Identity Center")
INSTANCE_PROFILE = PHON("ˈɪnstəns ˈproʊfaɪl", "Instance Profile")
TRUST_POLICY = PHON("trʌst ˈpɑləsi", "trust policy")
ACCESS_ANALYZER = PHON("ˈæksɛs ˈænəlaɪzɚ", "Access Analyzer")
SECRETS_MANAGER = PHON("ˈsikrəts ˈmænɪdʒɚ", "Secrets Manager")
USER_POOL = PHON("ˈjuzɚ pul", "User Pool")
IDENTITY_POOL = PHON("aɪˈdɛntɪti pul", "Identity Pool")
ACTIVE_DIRECTORY = PHON("ˈæktɪv dɪˈrɛktəri", "Active Directory")
DYNAMODB = PHON("ˈdaɪnəmoʊ diˈbi", "DynamoDB")
AUTO_SCALING = PHON("ˈɔtoʊ ˈskeɪlɪŋ", "Auto Scaling")
LOAD_BALANCER = PHON("loʊd ˈbælənsɚ", "Load Balancer")
LOAD_BALANCERS = PHON("loʊd ˈbælənsɚz", "Load Balancers")
PERMISSION_SET = PHON("pɚˈmɪʃən sɛt", "Permission Set")
PERMISSION_BOUNDARY = PHON("pɚˈmɪʃən ˈbaʊndri", "permission boundary")
EXECUTION_ROLE = PHON("ˌɛksəˈkjuʃən ɹoʊl", "execution role")
LAUNCH_TEMPLATE = PHON("lɔntʃ ˈtɛmplət", "Launch Template")
TARGET_GROUP = PHON("ˈtɑrɡət ɡrup", "Target Group")
SPOT = PHON("spɑt", "Spot")
SCALE_IN = PHON("skeɪl ɪn", "scale-in")
SCALE_OUT = PHON("skeɪl aʊt", "scale-out")
HEALTH_CHECK = PHON("hɛlθ tʃɛk", "health check")
STICKY_SESSIONS = PHON("ˈstɪki ˈsɛʃənz", "sticky sessions")
CROSS_ZONE = PHON("krɔs zoʊn", "cross-zone")
PLACEMENT_GROUP = PHON("ˈpleɪsmənt ɡrup", "Placement Group")
LIFECYCLE_HOOK = PHON("ˈlaɪfsaɪkəl hʊk", "lifecycle hook")
WORKLOAD = PHON("ˈwɜrkloʊd", "workload")
ENDPOINT = PHON("ˈɛndpɔɪnt", "endpoint")
GATEWAY = PHON("ˈɡeɪtweɪ", "gateway")
THROUGHPUT = PHON("ˈθruːpʊt", "throughput")
FAILOVER = PHON("ˈfeɪloʊvɚ", "failover")
STANDBY = PHON("ˈstændbaɪ", "standby")
WARM_STANDBY = PHON("wɔrm ˈstændbaɪ", "warm standby")
PILOT_LIGHT = PHON("ˈpaɪlət laɪt", "pilot light")
BACKUP_AND_RESTORE = PHON("ˈbækʌp ænd rɪˈstɔr", "backup and restore")
COLD_START = PHON("koʊld stɑrt", "cold start")
PROVISIONED_CONCURRENCY = PHON("prəˈvɪʒənd kənˈkɜrənsi", "provisioned concurrency")
EVENT_SOURCE = PHON("ɪˈvɛnt sɔrs", "event source")
DESTINATION = PHON("ˌdɛstəˈneɪʃən", "destination")
SIDECAR = PHON("ˈsaɪdkɑr", "sidecar")
SERVICE_DISCOVERY = PHON("ˈsɜrvɪs dɪˈskʌvəri", "service discovery")
