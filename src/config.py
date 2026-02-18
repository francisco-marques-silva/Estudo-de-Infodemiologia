# -*- coding: utf-8 -*-
"""
Configurações centralizadas do projeto.
Todos os caminhos, parâmetros e constantes ficam aqui.
"""

from pathlib import Path
from datetime import datetime, timedelta

# ==============================================================================
# CAMINHOS
# ==============================================================================

ROOT_DIR     = Path(__file__).resolve().parent.parent
SRC_DIR      = ROOT_DIR / "src"
DATA_DIR     = ROOT_DIR / "dados"
RAW_DIR      = DATA_DIR / "brutos"
REVIEWS_DIR  = DATA_DIR / "reviews"
CLEAN_DIR    = DATA_DIR / "limpos"
RESULTS_DIR  = ROOT_DIR / "resultados"
GRAFICOS_DIR = RESULTS_DIR / "graficos"
TABELAS_DIR  = RESULTS_DIR / "tabelas"
RELATORIO_DIR = RESULTS_DIR / "relatorios"
LOG_DIR      = ROOT_DIR / "logs"

# Criar diretórios se não existirem
for _d in [RAW_DIR, REVIEWS_DIR, CLEAN_DIR, GRAFICOS_DIR, TABELAS_DIR,
           RELATORIO_DIR, LOG_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# PARÂMETROS DE COLETA (Fases 1+2)
# ==============================================================================

DESCRITORES = [
    "e-SUS",
    "MySUS",
    "ConecteSUS",
    "prontuário eletrônico",
    "vigilância epidemiológica",
    "saúde pública Brasil",
    "telemedicina SUS",
    "vacina SUS",
    "agente comunitário saúde",
    "telessaúde Brasil",
]

CATEGORIAS_ALVO  = ["MEDICAL", "HEALTH_AND_FITNESS"]
MAX_RESULTADOS   = 30     # apps por descritor
MAX_REVIEWS      = 100    # comentários por app
IDIOMA           = "pt_BR"
PAIS             = "br"
SLEEP_BUSCA      = 1.0    # segundos entre buscas
SLEEP_APP        = 0.8    # segundos entre extração de apps

# ==============================================================================
# PARÂMETROS DE FILTRAGEM (Fase 3)
# ==============================================================================

MIN_INSTALACOES        = 1_000
MESES_OBSOLESCENCIA    = 24
DATA_REFERENCIA        = datetime.now()
DATA_CORTE_ATUALIZACAO = DATA_REFERENCIA - timedelta(days=MESES_OBSOLESCENCIA * 30)

# Palavras-chave de inclusão temática
KEYWORDS_INCLUSAO = [
    "prontuário", "prontuario", "ehr", "electronic health",
    "sus", "datasus", "e-sus", "esus",
    "ministério da saúde", "ministerio da saude",
    "secretaria de saúde", "secretaria de saude",
    "ubs", "atenção básica", "atencao basica",
    "vigilância", "vigilancia", "epidemiológ",
    "telemedicina", "teleconsulta", "telessaúde", "telessaude",
    "saúde digital", "saude digital",
    "interoperab", "hl7", "fhir", "api saúde", "api saude",
    "vacinação", "vacinacao", "imunização", "imunizacao",
    "samu", "caps", "cnes", "sinan", "sinasc", "sim ",
    "farmácia popular", "farmacia popular",
    "agente comunitário", "agente comunitario",
    "acs ", "estratégia saúde família",
    "saúde pública", "saude publica", "public health",
    "hospital", "clínic", "clinic", "laborat",
    "diagnóstico", "diagnostico",
    "prescrição", "prescricao", "receita médica",
    "hemograma", "exame", "laudo",
    "enfermagem", "medical record",
    "conecte sus", "meu sus digital", "conect sus",
]

# Palavras-chave de exclusão (fitness recreativo)
KEYWORDS_EXCLUSAO_TITULO = [
    "academia", "gym", "workout", "fitness tracker",
    "dieta", "emagrecer", "perder peso", "caloria",
    "yoga", "meditação", "meditacao", "mindfulness",
    "corrida", "running", "step counter", "pedômetro",
    "musculação", "musculacao", "treino",
    "receita culinária", "receita culinaria",
]

# Classificação de desenvolvedores
KEYWORDS_GOV = [
    "ministério", "ministerio", "secretaria", "governo",
    "prefeitura", "municipal", "estadual", "federal",
    "datasus", "sus", "fiocruz", "anvisa", "ans",
    "universidade", "university", "usp", "unicamp", "ufmg",
    "instituto", "fundação", "fundacao",
]

# ==============================================================================
# EIXOS TEMÁTICOS (Fase 4B)
# ==============================================================================

EIXOS_TEMATICOS = {
    "Interoperabilidade": {
        "keywords": [
            "sincroniz", "sincronia", "integra", "dados não",
            "dados nao", "conectar", "conexão", "conexao",
            "importar", "exportar", "transferir", "transferência",
            "api", "servidor", "offline", "online",
            "não carrega", "nao carrega", "não sincroniz",
            "nao sincroniz", "perdi dados", "perdi os dados",
            "não atualiza", "nao atualiza", "desconect",
            "compatível", "compativel", "incompatível", "incompativel",
            "vincular", "cadastro", "login", "autenticação",
        ],
        "cor": "#1565C0",
    },
    "Segurança e Privacidade": {
        "keywords": [
            "segurança", "seguranca", "privacidade", "dados pessoais",
            "lgpd", "proteção", "protecao", "vazamento", "vazar",
            "senha", "criptograf", "hack", "roubar", "roubaram",
            "permissão", "permissao", "acesso indevido",
            "informação pessoal", "informacao pessoal",
            "confiável", "confiavel", "desconfi",
            "expor", "exposição", "dados sensíveis", "dados sensiveis",
        ],
        "cor": "#C62828",
    },
    "Usabilidade (UX)": {
        "keywords": [
            "difícil", "dificil", "complicad", "confus",
            "interface", "tela", "botão", "botao", "menu",
            "intuitiv", "layout", "design", "visual",
            "não encontr", "nao encontr", "cadê", "cade",
            "onde fica", "como faz", "como faço",
            "navegação", "navegacao", "acessibilidad",
            "letra pequena", "não consigo", "nao consigo",
            "complicado de usar", "difícil de usar",
            "ux", "experiência", "experiencia", "usabilidad",
        ],
        "cor": "#F57F17",
    },
    "Funcionalidade e Bugs": {
        "keywords": [
            "bug", "erro", "crash", "trava", "travando",
            "fecha sozinho", "fechou", "parou", "parar de funcionar",
            "não funciona", "nao funciona", "não abre", "nao abre",
            "problema", "falha", "defeito", "quebr",
            "atualização quebrou", "atualizacao quebrou",
            "não responde", "nao responde", "congelou", "congela",
            "lixo", "péssimo", "pessimo", "horrível", "horrivel",
            "inútil", "inutil", "porcaria",
        ],
        "cor": "#6A1B9A",
    },
    "Desempenho": {
        "keywords": [
            "lento", "lentidão", "lentidao", "demora",
            "pesado", "memória", "memoria", "bateria",
            "consumo", "espaço", "espaco", "armazenamento",
            "carregando", "loading", "travando", "lag",
            "otimiz", "rápido", "rapido", "veloz",
            "internet", "banda", "wifi", "3g", "4g", "5g",
        ],
        "cor": "#2E7D32",
    },
}

# ==============================================================================
# PLN
# ==============================================================================

STOPWORDS_EXTRAS = {
    "app", "aplicativo", "aplicação", "aplicacao", "muito", "mais",
    "ainda", "aqui", "lá", "la", "pra", "pro", "pelo", "pela",
    "tá", "ta", "tô", "to", "ai", "aí", "né", "ne", "gente",
    "coisa", "coisas", "vez", "vezes", "dia", "dias", "ter",
    "ser", "fazer", "pode", "vai", "vou", "está", "esta",
    "esse", "essa", "isso", "isto", "dele", "dela",
}
