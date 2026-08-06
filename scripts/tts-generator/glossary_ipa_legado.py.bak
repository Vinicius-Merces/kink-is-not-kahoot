"""Helpers e termos foneticos compartilhados entre os roteiros de capitulo.

So recebem tratamento fonetico termos em ingles de risco real de erro
(palavras curtas que podem ser lidas como portugues, ou expressoes-chave
repetidas). Termos ja bem incorporados ao jargao tecnico em PT-BR (Lambda,
backup, snapshot, container, deploy) ficam em texto puro.
"""

SAY = lambda s: f'<say-as interpret-as="characters">{s}</say-as>'
EMPH = lambda s: f'<emphasis level="moderate">{s}</emphasis>'
BRK = lambda ms: f'<break time="{ms}ms"/>'
PHON = lambda ipa, text: f'<phoneme alphabet="ipa" ph="{ipa}">{text}</phoneme>'

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
