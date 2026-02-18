# -*- coding: utf-8 -*-
"""
Fase 4B — Análise qualitativa (PLN): sentimento, temas, LDA e nuvens de palavras.
"""

import logging, re
from collections import Counter

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from textblob import TextBlob
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

import nltk
for _res in ("punkt", "punkt_tab", "stopwords"):
    try:
        nltk.data.find(f"tokenizers/{_res}" if "punkt" in _res else f"corpora/{_res}")
    except LookupError:
        nltk.download(_res, quiet=True)
from nltk.corpus import stopwords

from src.config import (CLEAN_DIR, GRAFICOS_DIR, TABELAS_DIR,
                        EIXOS_TEMATICOS, STOPWORDS_EXTRAS)

logger = logging.getLogger(__name__)

plt.rcParams.update({
    "figure.figsize": (10, 6), "figure.dpi": 150,
    "font.size": 11, "font.family": "serif",
})
sns.set_theme(style="whitegrid", palette="muted")

# ── dicionário de ajuste PT-BR ───────────────────────────────────────────────
_POSITIVAS = {
    "bom","boa","ótimo","ótima","excelente","maravilhoso","maravilhosa",
    "perfeito","perfeita","funciona","útil","prático","prática","rápido",
    "rápida","fácil","recomendo","adorei","amei","parabéns","legal",
    "ajuda","gostei","top","melhor","incrível","eficiente","satisfeito",
}
_NEGATIVAS = {
    "ruim","péssimo","péssima","horrível","terrível","lixo","travando",
    "trava","lento","lenta","bug","erro","falha","demora","horrendo",
    "pior","inútil","decepcion","decepcionou","decepcionante","merda",
    "nojo","funcionou","parou","desinstalei","desinstalar","porcaria",
    "propaganda","anúncio","anúncios","pessimo","pessima","odiei",
}


def _limpar(txt: str) -> str:
    txt = str(txt).lower()
    txt = re.sub(r"http\S+", "", txt)
    txt = re.sub(r"[^a-záàâãéêíóôõúüç\s]", " ", txt)
    return re.sub(r"\s+", " ", txt).strip()


def _sentimento(txt: str) -> tuple[str, float]:
    pol = TextBlob(txt).sentiment.polarity
    words = set(txt.split())
    p = len(words & _POSITIVAS)
    n = len(words & _NEGATIVAS)
    ajuste = (p - n) * 0.15
    pol = max(-1, min(1, pol + ajuste))
    if pol > 0.05:
        return "Positivo", pol
    elif pol < -0.05:
        return "Negativo", pol
    return "Neutro", pol


def _classificar_eixo(txt: str) -> list[str]:
    eixos = []
    for eixo, info in EIXOS_TEMATICOS.items():
        if any(kw in txt for kw in info["keywords"]):
            eixos.append(eixo)
    return eixos if eixos else ["Outros"]


# ────────────────────────────────────────────────────────────────────────────
def executar_analise_qualitativa() -> pd.DataFrame:
    logger.info("=" * 60)
    logger.info("FASE 4B — Análise Qualitativa (PLN)")
    logger.info("=" * 60)

    # Prefere seleção manual quando existir
    rev_sel = CLEAN_DIR / "reviews_selecionados.csv"
    if rev_sel.exists():
        df = pd.read_csv(rev_sel, encoding="utf-8-sig")
        logger.info("Usando reviews_selecionados.csv (seleção manual)")
    else:
        csv_files = sorted(CLEAN_DIR.glob("reviews_limpos_*.csv"), reverse=True)
        if not csv_files:
            raise FileNotFoundError(f"Sem reviews limpos em {CLEAN_DIR}")
        df = pd.read_csv(csv_files[0], encoding="utf-8-sig")
        logger.info(f"Usando {csv_files[0].name}")
    df = df.dropna(subset=["content"]).copy()
    logger.info(f"Reviews para PLN: {len(df)}")

    # ── 1. pré-processamento ──────────────────────────────────────────────
    df["texto_limpo"] = df["content"].apply(_limpar)
    df = df[df["texto_limpo"].str.len() > 10].copy()
    logger.info(f"Reviews após limpeza mínima: {len(df)}")

    # ── 2. sentimento ─────────────────────────────────────────────────────
    sent = df["texto_limpo"].apply(_sentimento)
    df["sentimento"] = sent.apply(lambda x: x[0])
    df["polaridade"] = sent.apply(lambda x: x[1])

    cnt = df["sentimento"].value_counts()
    pct = (cnt / cnt.sum() * 100).round(1)
    tab_sent = pd.DataFrame({"Frequência": cnt, "Percentual (%)": pct})
    tab_sent.to_csv(TABELAS_DIR / "sentimentos.csv", encoding="utf-8-sig")
    logger.info(f"Sentimentos: {dict(cnt)}")

    # gráfico
    cores = {"Positivo":"#4CAF50","Neutro":"#FFC107","Negativo":"#F44336"}
    fig, axes = plt.subplots(1, 2, figsize=(14,6))
    cnt.plot.bar(ax=axes[0], color=[cores.get(c,"gray") for c in cnt.index],
                 edgecolor="w")
    axes[0].set_title("Distribuição de Sentimentos", fontweight="bold")
    axes[0].set_ylabel("Frequência"); axes[0].tick_params(axis="x", rotation=0)
    cnt.plot.pie(ax=axes[1], autopct="%1.1f%%", startangle=90,
                 colors=[cores.get(c,"gray") for c in cnt.index])
    axes[1].set_ylabel(""); axes[1].set_title("Proporção", fontweight="bold")
    plt.tight_layout()
    fig.savefig(GRAFICOS_DIR / "sentimentos.png"); plt.close(fig)

    # polaridade histograma
    fig, ax = plt.subplots()
    df["polaridade"].hist(bins=40, ax=ax, color="#64B5F6", edgecolor="w")
    ax.axvline(0, color="red", ls="--", lw=2)
    ax.set_xlabel("Polaridade"); ax.set_ylabel("Frequência")
    ax.set_title("Distribuição da Polaridade dos Sentimentos", fontweight="bold")
    plt.tight_layout()
    fig.savefig(GRAFICOS_DIR / "distribuicao_polaridade.png"); plt.close(fig)

    # ── 3. classificação temática ─────────────────────────────────────────
    temas = df["texto_limpo"].apply(_classificar_eixo)
    tema_exploded = temas.explode()
    cnt_t = tema_exploded.value_counts()
    pct_t = (cnt_t / len(df) * 100).round(1)
    tab_t = pd.DataFrame({"Frequência": cnt_t, "Percentual (%)": pct_t})
    tab_t.to_csv(TABELAS_DIR / "distribuicao_tematica.csv", encoding="utf-8-sig")

    cores_eixo = {e: info["cor"] for e, info in EIXOS_TEMATICOS.items()}
    cores_eixo["Outros"] = "#9E9E9E"
    fig, ax = plt.subplots(figsize=(12,6))
    bar_colors = [cores_eixo.get(t, "#9E9E9E") for t in cnt_t.index]
    cnt_t.plot.barh(ax=ax, color=bar_colors, edgecolor="w")
    ax.set_xlabel("Menções"); ax.set_title("Distribuição Temática", fontweight="bold")
    ax.invert_yaxis(); plt.tight_layout()
    fig.savefig(GRAFICOS_DIR / "distribuicao_tematica.png"); plt.close(fig)

    # ── 4. sentimento × tema ──────────────────────────────────────────────
    rows = []
    for idx, eixos in temas.items():
        for e in eixos:
            rows.append({"eixo": e, "sentimento": df.loc[idx, "sentimento"],
                         "polaridade": df.loc[idx, "polaridade"]})
    df_tema = pd.DataFrame(rows)
    if len(df_tema) > 0:
        cross = pd.crosstab(df_tema["eixo"], df_tema["sentimento"])
        cross.to_csv(TABELAS_DIR / "sentimento_por_tema.csv", encoding="utf-8-sig")

        fig, ax = plt.subplots(figsize=(12,7))
        cross.plot.barh(stacked=True, ax=ax,
                        color=[cores.get(c,"gray") for c in cross.columns])
        ax.set_xlabel("Menções"); ax.set_title("Sentimento por Eixo Temático",
                                                fontweight="bold")
        ax.invert_yaxis(); ax.legend(title="Sentimento"); plt.tight_layout()
        fig.savefig(GRAFICOS_DIR / "sentimento_por_tema.png"); plt.close(fig)

    # ── 5. LDA (topic modeling) ───────────────────────────────────────────
    stops = list(STOPWORDS_EXTRAS | set(stopwords.words("portuguese")))
    vec = CountVectorizer(max_features=2000, min_df=3, max_df=0.9,
                          stop_words=stops)
    dtm = vec.fit_transform(df["texto_limpo"])
    n_topics = 5
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42,
                                     max_iter=20, learning_method="online")
    lda.fit(dtm)
    feat = vec.get_feature_names_out()
    topics_out = []
    for i, comp in enumerate(lda.components_):
        top_w = [feat[j] for j in comp.argsort()[-10:][::-1]]
        topics_out.append({"Tópico": f"Tópico {i+1}", "Palavras-chave": ", ".join(top_w)})
    pd.DataFrame(topics_out).to_csv(TABELAS_DIR / "topicos_lda.csv",
                                    index=False, encoding="utf-8-sig")
    logger.info(f"LDA: {n_topics} tópicos extraídos")

    # heatmap LDA
    fig, ax = plt.subplots(figsize=(14,6))
    top_n = 10
    mat = np.zeros((n_topics, top_n))
    wlabs = []
    for i, comp in enumerate(lda.components_):
        top_idx = comp.argsort()[-top_n:][::-1]
        if i == 0:
            wlabs = [feat[j] for j in top_idx]
        mat[i] = comp[top_idx] / comp.sum()
    sns.heatmap(mat, annot=True, fmt=".3f", cmap="YlOrRd",
                xticklabels=wlabs,
                yticklabels=[f"Tópico {i+1}" for i in range(n_topics)], ax=ax)
    ax.set_title("Pesos LDA — Tópico × Palavras", fontweight="bold")
    plt.tight_layout()
    fig.savefig(GRAFICOS_DIR / "lda_heatmap.png"); plt.close(fig)

    # ── 6. nuvem de palavras ──────────────────────────────────────────────
    for label, sub in [("geral", df), ("positivo", df[df["sentimento"]=="Positivo"]),
                       ("negativo", df[df["sentimento"]=="Negativo"])]:
        txt = " ".join(sub["texto_limpo"].tolist())
        if len(txt) < 20:
            continue
        wc = WordCloud(width=1200, height=600, max_words=150,
                       background_color="white", colormap="viridis",
                       stopwords=stops, collocations=False).generate(txt)
        fig, ax = plt.subplots(figsize=(14,7))
        ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
        ax.set_title(f"Nuvem de Palavras — {label.title()}", fontweight="bold")
        plt.tight_layout()
        fig.savefig(GRAFICOS_DIR / f"wordcloud_{label}.png"); plt.close(fig)

    # ── 7. frequência de palavras ─────────────────────────────────────────
    all_words = " ".join(df["texto_limpo"]).split()
    all_words = [w for w in all_words if len(w)>2 and w not in stops]
    freq = Counter(all_words).most_common(30)
    df_freq = pd.DataFrame(freq, columns=["Palavra","Frequência"])
    df_freq.to_csv(TABELAS_DIR / "frequencia_palavras.csv",
                   index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(12,8))
    df_freq.set_index("Palavra").plot.barh(ax=ax, color="#7E57C2", edgecolor="w",
                                            legend=False)
    ax.invert_yaxis(); ax.set_xlabel("Frequência")
    ax.set_title("30 Palavras Mais Frequentes", fontweight="bold")
    plt.tight_layout()
    fig.savefig(GRAFICOS_DIR / "frequencia_palavras.png"); plt.close(fig)

    # ── salvar reviews anotados ───────────────────────────────────────────
    df["eixos"] = temas.apply(lambda x: "; ".join(x) if isinstance(x, list) else str(x))
    df.to_csv(TABELAS_DIR / "reviews_anotados.csv", index=False, encoding="utf-8-sig")
    logger.info("Fase 4B concluída.")
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    executar_analise_qualitativa()
