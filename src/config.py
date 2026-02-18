# -*- coding: utf-8 -*-
"""
Configurações centralizadas do projeto.
Título: A Onipresença dos Sistemas de Informação em Saúde: Uma Análise da
        Integração do Ecossistema mHealth via Dispositivos Móveis.
Todos os caminhos, parâmetros e constantes ficam aqui.
"""

from pathlib import Path
from datetime import datetime, timedelta

# ==============================================================================
# METADADOS DO PROJETO
# ==============================================================================

TITULO_PROJETO = (
    "A Onipresença dos Sistemas de Informação em Saúde: "
    "Uma Análise da Integração do Ecossistema mHealth via Dispositivos Móveis"
)
SUBTITULO_PROJETO = (
    "Estudo de Infodemiologia e Infometria — Análise de Métricas de Software "
    "e Percepção do Usuário no Ecossistema Digital de Saúde"
)

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

# Descritores padrão — focados em Sistemas de Informação em Saúde (SIS)
# O usuário pode adicionar/remover descritores interativamente na Fase 1.
DESCRITORES_PADRAO = [
    # ── SIS / Prontuário Eletrônico ───
    "prontuário eletrônico saúde",
    "sistema informação saúde",
    "electronic health record",
    "EHR saúde Brasil",
    "health information system",
    # ── Sistemas Governamentais / SUS ───
    "e-SUS",
    "ConecteSUS",
    "Meu SUS Digital",
    "DATASUS",
    "SISAB",
    "CNES saúde",
    # ── Interoperabilidade e Integração ───
    "interoperabilidade saúde",
    "HL7 FHIR saúde",
    "integração prontuário",
    "API saúde",
    # ── mHealth / Saúde Digital ───
    "mHealth Brasil",
    "saúde digital",
    "telemedicina",
    "telessaúde",
    "teleconsulta",
    # ── Vigilância e Gestão ───
    "vigilância epidemiológica",
    "gestão hospitalar",
    "farmácia hospitalar sistema",
    "laboratório saúde sistema",
    "SINAN vigilância",
]

# Cópia mutável usada em runtime (pode ser alterada interativamente)
DESCRITORES = list(DESCRITORES_PADRAO)

CATEGORIAS_ALVO  = ["MEDICAL", "HEALTH_AND_FITNESS"]
MAX_RESULTADOS   = 30     # apps por descritor
MAX_REVIEWS      = 200    # comentários por app
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

# Palavras-chave de inclusão temática — foco em SIS e integração mHealth
KEYWORDS_INCLUSAO = [
    # ── Prontuário / EHR ───
    "prontuário", "prontuario", "ehr", "electronic health",
    "medical record", "registro eletrônico", "registro eletronico",
    # ── SUS / Gov ───
    "sus", "datasus", "e-sus", "esus", "conecte sus", "conect sus",
    "meu sus digital", "sisab", "sigtap",
    "ministério da saúde", "ministerio da saude",
    "secretaria de saúde", "secretaria de saude",
    # ── Interoperabilidade / API / Integração ───
    "interoperab", "hl7", "fhir", "api saúde", "api saude",
    "integração", "integracao", "sincroniz", "sincroniza",
    "conectividade", "padrão aberto", "padrao aberto",
    "openehr", "dicom",
    # ── Sistemas de Informação ───
    "sistema de informação", "sistema de informacao",
    "information system", "cnes", "sinan", "sinasc",
    "sim ", "sivep", "sipni", "sisvan", "siab",
    "gestão hospitalar", "gestao hospitalar",
    "gestão clínica", "gestao clinica",
    # ── mHealth / Saúde Digital ───
    "mhealth", "m-health", "saúde digital", "saude digital",
    "telemedicina", "teleconsulta", "telessaúde", "telessaude",
    # ── Atenção à Saúde ───
    "ubs", "atenção básica", "atencao basica",
    "vigilância", "vigilancia", "epidemiológ",
    "vacinação", "vacinacao", "imunização", "imunizacao",
    "samu", "caps",
    "farmácia popular", "farmacia popular",
    "agente comunitário", "agente comunitario",
    "estratégia saúde família",
    "saúde pública", "saude publica", "public health",
    # ── Clínico / Hospitalar ───
    "hospital", "clínic", "clinic", "laborat",
    "diagnóstico", "diagnostico",
    "prescrição", "prescricao", "receita médica",
    "hemograma", "exame", "laudo",
    "enfermagem",
]

# Palavras-chave de exclusão (fitness recreativo / sem relação com SIS)
KEYWORDS_EXCLUSAO_TITULO = [
    "academia", "gym", "workout", "fitness tracker",
    "dieta", "emagrecer", "perder peso", "caloria",
    "yoga", "meditação", "meditacao", "mindfulness",
    "corrida", "running", "step counter", "pedômetro",
    "musculação", "musculacao", "treino",
    "receita culinária", "receita culinaria",
    "personal trainer", "bodybuilding",
    "sleep tracker", "ciclo menstrual",
]

# Classificação de desenvolvedores (3 categorias)
KEYWORDS_GOV = [
    "ministério", "ministerio", "secretaria", "governo",
    "prefeitura", "municipal", "estadual", "federal",
    "datasus", "sus", "fiocruz", "anvisa", "ans",
    "universidade", "university", "usp", "unicamp", "ufmg",
    "instituto", "fundação", "fundacao",
]

# ==============================================================================
# EIXOS TEMÁTICOS (Fase 4B) — Dimensões da Integração mHealth/SIS
# ==============================================================================

EIXOS_TEMATICOS = {
    "Interoperabilidade e Integração de Dados": {
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
            "interoperab", "fhir", "hl7", "banco de dados",
            "prontuário", "prontuario", "registro",
            "migrar", "migração", "backup",
        ],
        "cor": "#1565C0",
    },
    "Segurança da Informação e Privacidade": {
        "keywords": [
            "segurança", "seguranca", "privacidade", "dados pessoais",
            "lgpd", "proteção", "protecao", "vazamento", "vazar",
            "senha", "criptograf", "hack", "roubar", "roubaram",
            "permissão", "permissao", "acesso indevido",
            "informação pessoal", "informacao pessoal",
            "confiável", "confiavel", "desconfi",
            "expor", "exposição", "dados sensíveis", "dados sensiveis",
            "autenticação", "autenticacao", "token", "biometria",
            "certificado digital", "assinatura digital",
        ],
        "cor": "#C62828",
    },
    "Usabilidade e Experiência do Usuário (UX)": {
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
            "tutorial", "ajuda", "manual",
        ],
        "cor": "#F57F17",
    },
    "Funcionalidade e Estabilidade Técnica": {
        "keywords": [
            "bug", "erro", "crash", "trava", "travando",
            "fecha sozinho", "fechou", "parou", "parar de funcionar",
            "não funciona", "nao funciona", "não abre", "nao abre",
            "problema", "falha", "defeito", "quebr",
            "atualização quebrou", "atualizacao quebrou",
            "não responde", "nao responde", "congelou", "congela",
            "lixo", "péssimo", "pessimo", "horrível", "horrivel",
            "inútil", "inutil", "porcaria",
            "instável", "instavel", "versão", "versao",
        ],
        "cor": "#6A1B9A",
    },
    "Desempenho e Infraestrutura": {
        "keywords": [
            "lento", "lentidão", "lentidao", "demora",
            "pesado", "memória", "memoria", "bateria",
            "consumo", "espaço", "espaco", "armazenamento",
            "carregando", "loading", "travando", "lag",
            "otimiz", "rápido", "rapido", "veloz",
            "internet", "banda", "wifi", "3g", "4g", "5g",
            "servidor fora", "indisponível", "indisponivel",
            "tempo de resposta", "timeout",
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
