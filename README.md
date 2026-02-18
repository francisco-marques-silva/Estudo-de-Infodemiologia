# Infodemiologia — Aplicativos de Saúde na Google Play Store

Estudo observacional de **Infodemiologia/Infometria** com análise de sentimentos e mineração de texto sobre aplicativos de saúde na Google Play Store brasileira.

## Conformidade Ética
- **Resolução CNS 510/2016** — Dados secundários de acesso público (dispensa CEP)
- **LGPD (Lei 13.709/2018)** — Nomes de usuários anonimizados via SHA-256
- **Google Play ToS** — Rate limiting ético entre requisições

---

## Estrutura do Projeto

```
├── pipeline_principal.py       # Orquestrador — executa todas as fases
├── src/
│   ├── __init__.py             # Pacote (versão, autor)
│   ├── config.py               # Configuração centralizada
│   ├── coleta.py               # Fases 1-2: scraping da Play Store
│   ├── limpeza.py              # Fase 3: filtragem e limpeza
│   ├── quantitativa.py         # Fase 4A: estatística e correlação
│   ├── qualitativa.py          # Fase 4B: PLN, sentimento, LDA
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

```bash
# Pipeline completo (coleta → limpeza → análise → relatório Word)
python pipeline_principal.py

# Fases individuais
python pipeline_principal.py --fase 1          # Coleta
python pipeline_principal.py --fase 3          # Limpeza
python pipeline_principal.py --fase 4a         # Quantitativa
python pipeline_principal.py --fase 4b         # Qualitativa (PLN)
python pipeline_principal.py --fase 5          # Relatório Word
python pipeline_principal.py --fase 3 4a 4b 5  # Limpeza + Análises + Relatório
```

---

## Fases do Pipeline

| Fase | Módulo | Descrição |
|------|--------|-----------|
| 1-2 | `src/coleta.py` | Busca por 10 descritores na Play Store; extrai metadados + até 200 reviews/app; anonimiza usernames (LGPD) |
| 3 | `src/limpeza.py` | Remove duplicatas e categorias irrelevantes; filtra ≥1.000 instalações e atualização ≤24 meses; classifica desenvolvedores |
| 4A | `src/quantitativa.py` | Estatística descritiva; Pearson/Spearman (atualização × score); gráficos de distribuição e correlação |
| 4B | `src/qualitativa.py` | Sentimento (TextBlob + dicionário PT-BR); 5 eixos temáticos; LDA (5 tópicos); WordCloud; frequência de palavras |
| 5 | `src/relatorio.py` | Gera documento Word com capa, metodologia, resultados interpretativos, gráficos inline e lista de apps |

### Eixos Temáticos
1. **Interoperabilidade** — Sincronização e integração de dados
2. **Segurança e Privacidade** — Proteção de dados pessoais
3. **Usabilidade (UX)** — Facilidade de uso da interface
4. **Funcionalidade e Bugs** — Erros, travamentos, crashes
5. **Desempenho** — Lentidão, consumo de bateria/memória

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
