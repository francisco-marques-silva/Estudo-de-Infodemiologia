# A Onipresença dos Sistemas de Informação em Saúde: Uma Análise da Integração do Ecossistema mHealth via Dispositivos Móveis

Estudo de **Infodemiologia e Infometria** focado na análise de métricas de software e percepção do usuário no ecossistema digital de saúde, com ênfase na integração de Sistemas de Informação em Saúde (SIS) via aplicativos móveis (mHealth) na Google Play Store.

## Conformidade Ética
- **Resolução CNS 510/2016** — Dados secundários de acesso público (dispensa CEP)
- **LGPD (Lei 13.709/2018)** — Nomes de usuários anonimizados via SHA-256
- **Google Play ToS** — Rate limiting ético entre requisições

---

## Estrutura do Projeto

```
├── pipeline_principal.py       # Orquestrador — executa todas as fases
├── csv_para_word.py            # Conversor CSV → Word (.docx)
├── src/
│   ├── __init__.py             # Pacote (versão, autor)
│   ├── config.py               # Configuração centralizada
│   ├── coleta.py               # Fases 1-2: seleção interativa de descritores + scraping
│   ├── lista_coleta.py         # Fase 2.5: lista Word de apps coletados
│   ├── limpeza.py              # Fase 3: filtragem e limpeza
│   ├── selecao.py              # Fase 3.5: seleção interativa de apps via terminal
│   ├── quantitativa.py         # Fase 4A: estatística descritiva e correlação
│   ├── qualitativa.py          # Fase 4B: PLN, sentimento, temas, LDA
│   └── relatorio.py            # Fase 5: relatório Word (.docx)
├── requirements.txt
├── .gitignore
├── README.md
├── dados/                      # (gerado) dados brutos e limpos
│   ├── brutos/
│   ├── reviews/
│   └── limpos/
├── resultados/                 # (gerado) gráficos, tabelas, relatórios
│   ├── graficos/
│   ├── tabelas/
│   ├── tabelas_word/
│   └── relatorios/
└── logs/                       # (gerado) logs de execução
```

---

## Instalação

```bash
# Clonar o repositório
git clone <url-do-repositorio>
cd <pasta-do-projeto>

# Criar ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / Mac

# Instalar dependências
pip install -r requirements.txt
```

---

## Uso

### Pipeline completo (com seleção interativa de descritores e apps)

```bash
python pipeline_principal.py
```

### Usando descritores padrão (sem edição interativa)

```bash
python pipeline_principal.py --descritores-padrao
```

### Fases individuais

```bash
python pipeline_principal.py --fase 1          # Coleta (com seleção de descritores)
python pipeline_principal.py --fase 2.5        # Lista Word de revisão
python pipeline_principal.py --fase 3          # Limpeza
python pipeline_principal.py --fase 3.5        # Seleção interativa de apps
python pipeline_principal.py --fase 4a         # Quantitativa
python pipeline_principal.py --fase 4b         # Qualitativa (PLN)
python pipeline_principal.py --fase 5          # Relatório Word
python pipeline_principal.py --fase 6          # Conversão CSV → Word
python pipeline_principal.py --fase 3 3.5 4a 4b 5 6  # Limpeza → Análise → Relatório
```

### Opções de seleção de apps

```bash
python pipeline_principal.py --sem-selecao     # Usa todos os apps (sem perguntar)
python pipeline_principal.py --reselecionar    # Força nova seleção interativa
```

---

## Pipeline — Fases

| Fase | Módulo | Descrição |
|------|--------|-----------|
| **1** | `src/coleta.py` | **Seleção de Descritores** — O usuário revisa, adiciona ou remove palavras-chave via terminal |
| **1-2** | `src/coleta.py` | **Extração (Mining)** — Busca na Play Store e extrai metadados + até 200 reviews/app |
| **2.5** | `src/lista_coleta.py` | Gera documento Word com todos os apps coletados para revisão manual |
| **3** | `src/limpeza.py` | **Data Cleaning** — Remove duplicatas, filtra categorias, ≥1.000 instalações, classifica desenvolvedores |
| **3.5** | `src/selecao.py` | **Seleção Interativa** — O usuário escolhe via terminal quais apps entram na análise |
| **4A** | `src/quantitativa.py` | Estatística descritiva; Correlação de Pearson; gráficos de distribuição |
| **4B** | `src/qualitativa.py` | Sentimento (TextBlob + dicionário PT-BR); 5 eixos temáticos; LDA; WordCloud |
| **5** | `src/relatorio.py` | Relatório Word completo com metodologia, resultados e interpretações |
| **6** | `csv_para_word.py` | Conversão de CSVs para tabelas Word formatadas |

### Eixos Temáticos (Fase 4B)
1. **Interoperabilidade e Integração de Dados** — Sincronização, API, prontuários
2. **Segurança da Informação e Privacidade** — LGPD, criptografia, vazamentos
3. **Usabilidade e Experiência do Usuário (UX)** — Interface, navegação, acessibilidade
4. **Funcionalidade e Estabilidade Técnica** — Bugs, crashes, erros
5. **Desempenho e Infraestrutura** — Lentidão, memória, bateria, servidor

---

## Saídas Geradas

### Tabelas (CSV)
- `estatistica_descritiva.csv` — Métricas descritivas completas
- `correlacoes.csv` — Coeficientes de Pearson e Spearman
- `distribuicao_desenvolvedor.csv` — Contagem por tipo de desenvolvedor
- `top_20_apps.csv` — Apps mais instalados
- `distribuicao_tematica.csv` — Frequência por eixo temático
- `sentimentos.csv` — Distribuição de sentimentos
- `topicos_lda.csv` — Tópicos LDA com palavras-chave
- `frequencia_palavras.csv` — Top 30 palavras

### Gráficos (PNG)
- Correlação atualização × score, matriz de correlação
- Distribuição de scores e instalações (log)
- Boxplot por tipo de desenvolvedor
- Distribuição temporal de atualizações
- Sentimentos (barras + pizza), histograma de polaridade
- Distribuição temática, sentimento × tema
- Heatmap LDA
- Nuvens de palavras (geral, positivo, negativo)
- Frequência de palavras (top 30)

### Relatório Word (.docx)
- Capa, sumário, introdução, metodologia detalhada
- Resultados quantitativos e qualitativos com interpretação automática
- Gráficos embutidos no documento
- Lista completa de aplicativos incluídos (Apêndice A)
- Discussão, limitações e referências

---

## Licença
Este é um projeto acadêmico. Os dados analisados são públicos.
