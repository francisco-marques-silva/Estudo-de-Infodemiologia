# -*- coding: utf-8 -*-
"""
Fase 4A — Análise quantitativa: estatística descritiva e correlação.
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import CLEAN_DIR, GRAFICOS_DIR, TABELAS_DIR

logger = logging.getLogger(__name__)

plt.rcParams.update({
    "figure.figsize": (10, 6), "figure.dpi": 150,
    "font.size": 11, "font.family": "serif",
})
sns.set_theme(style="whitegrid", palette="muted")


def _carregar() -> tuple[pd.DataFrame, pd.DataFrame]:
    csv_a = sorted(CLEAN_DIR.glob("apps_limpos_*.csv"), reverse=True)
    csv_r = sorted(CLEAN_DIR.glob("reviews_limpos_*.csv"), reverse=True)
    if not csv_a:
        raise FileNotFoundError(f"Sem dados limpos em {CLEAN_DIR}")
    df = pd.read_csv(csv_a[0], encoding="utf-8-sig")
    df_r = pd.read_csv(csv_r[0], encoding="utf-8-sig") if csv_r else pd.DataFrame()
    for c in ["score", "instalacoes_num", "ratings", "reviews_count"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "updated_dt" in df.columns:
        df["updated_dt"] = pd.to_datetime(df["updated_dt"], errors="coerce")
    elif "updated" in df.columns:
        df["updated_dt"] = pd.to_datetime(df["updated"], unit="s", errors="coerce")
    return df, df_r


def executar_analise_quantitativa() -> pd.DataFrame:
    """Pipeline da Fase 4A."""
    logger.info("=" * 60)
    logger.info("FASE 4A — Análise Quantitativa")
    logger.info("=" * 60)

    df, _ = _carregar()

    # ── métricas de manutenção ────────────────────────────────────────────────
    agora = pd.Timestamp.now()
    df["dias_desde_atualizacao"] = (agora - df["updated_dt"]).dt.days
    if "released" in df.columns:
        df["released_dt"] = pd.to_datetime(df["released"], errors="coerce",
                                            format="mixed", dayfirst=False)

    # ── 1. estatística descritiva ─────────────────────────────────────────────
    metricas = [m for m in ["score","instalacoes_num","ratings","reviews_count"]
                if m in df.columns]
    desc = df[metricas].describe().T
    desc["mediana"] = df[metricas].median()
    desc["CV (%)"] = (desc["std"] / desc["mean"] * 100).round(2)
    desc["assimetria"] = df[metricas].skew()
    desc["curtose"] = df[metricas].kurtosis()
    rename_idx = {"score": "Nota Média", "instalacoes_num": "Instalações",
                  "ratings": "Avaliações", "reviews_count": "Comentários"}
    desc.rename(index=rename_idx, inplace=True)
    desc.to_csv(TABELAS_DIR / "estatistica_descritiva.csv", encoding="utf-8-sig")
    logger.info(f"Estatística descritiva salva")

    # ── 2. correlações ────────────────────────────────────────────────────────
    df_c = df[["dias_desde_atualizacao","score","instalacoes_num","ratings"]].dropna()
    resultados_corr = []
    if len(df_c) >= 5:
        r, p = stats.pearsonr(df_c["dias_desde_atualizacao"], df_c["score"])
        rho, p_sp = stats.spearmanr(df_c["dias_desde_atualizacao"], df_c["score"])
        resultados_corr.append({
            "Variáveis": "Dias desde atualização × Score",
            "Pearson (r)": round(r,4), "p-valor (Pearson)": round(p,4),
            "Significativo (p<0.05)": "Sim" if p<0.05 else "Não",
            "Spearman (ρ)": round(rho,4), "p-valor (Spearman)": round(p_sp,4),
        })
        r2, p2 = stats.pearsonr(df_c["instalacoes_num"], df_c["score"])
        resultados_corr.append({
            "Variáveis": "Instalações × Score",
            "Pearson (r)": round(r2,4), "p-valor (Pearson)": round(p2,4),
            "Significativo (p<0.05)": "Sim" if p2<0.05 else "Não",
        })

        # gráfico dispersão
        fig, ax = plt.subplots()
        ax.scatter(df_c["dias_desde_atualizacao"], df_c["score"],
                   alpha=.6, s=50, c="#1976D2", edgecolors="w", linewidth=.5)
        z = np.polyfit(df_c["dias_desde_atualizacao"], df_c["score"], 1)
        xs = np.sort(df_c["dias_desde_atualizacao"])
        ax.plot(xs, np.poly1d(z)(xs), "--", color="#D32F2F", lw=2,
                label=f"r={r:.3f}, p={p:.3f}")
        ax.set_xlabel("Dias desde a última atualização")
        ax.set_ylabel("Nota média (Score)")
        ax.set_title("Correlação: Atualização × Satisfação", fontweight="bold")
        ax.legend(); plt.tight_layout()
        fig.savefig(GRAFICOS_DIR / "correlacao_atualizacao_score.png")
        plt.close(fig)

        # matriz
        fig, ax = plt.subplots(figsize=(8,6))
        cm = df_c.corr()
        ren = {"dias_desde_atualizacao":"Dias s/ Atualiz.","score":"Score",
               "instalacoes_num":"Instalações","ratings":"Avaliações"}
        cm.rename(index=ren, columns=ren, inplace=True)
        mask = np.triu(np.ones_like(cm, dtype=bool), k=1)
        sns.heatmap(cm, mask=mask, annot=True, fmt=".3f", cmap="RdBu_r",
                    center=0, square=True, ax=ax, linewidths=.5)
        ax.set_title("Matriz de Correlação", fontweight="bold")
        plt.tight_layout()
        fig.savefig(GRAFICOS_DIR / "matriz_correlacao.png"); plt.close(fig)

    pd.DataFrame(resultados_corr).to_csv(
        TABELAS_DIR / "correlacoes.csv", index=False, encoding="utf-8-sig")

    # ── 3. distribuição por desenvolvedor ─────────────────────────────────────
    if "tipo_desenvolvedor" in df.columns:
        cnt = df["tipo_desenvolvedor"].value_counts()
        pct = (cnt / cnt.sum() * 100).round(1)
        tab = pd.DataFrame({"Frequência": cnt, "Percentual (%)": pct})
        tab.to_csv(TABELAS_DIR / "distribuicao_desenvolvedor.csv", encoding="utf-8-sig")

        fig, ax = plt.subplots(figsize=(8,6))
        cnt.plot.pie(ax=ax, autopct="%1.1f%%", startangle=90,
                     colors=["#2196F3","#FF9800","#9E9E9E"][:len(cnt)])
        ax.set_ylabel(""); ax.set_title("Tipo de Desenvolvedor", fontweight="bold")
        plt.tight_layout()
        fig.savefig(GRAFICOS_DIR / "distribuicao_desenvolvedor.png"); plt.close(fig)

    # ── 4. gráficos de distribuição ───────────────────────────────────────────
    if "score" in df.columns:
        fig, ax = plt.subplots()
        df["score"].dropna().hist(bins=20, ax=ax, color="#42A5F5", edgecolor="w")
        ax.axvline(df["score"].mean(), color="red", ls="--", lw=2,
                   label=f"Média: {df['score'].mean():.2f}")
        ax.axvline(df["score"].median(), color="green", ls="-.", lw=2,
                   label=f"Mediana: {df['score'].median():.2f}")
        ax.set_xlabel("Score"); ax.set_ylabel("Frequência")
        ax.set_title("Distribuição das Notas", fontweight="bold"); ax.legend()
        plt.tight_layout()
        fig.savefig(GRAFICOS_DIR / "distribuicao_scores.png"); plt.close(fig)

    if "instalacoes_num" in df.columns:
        fig, ax = plt.subplots()
        df["instalacoes_num"].dropna().apply(np.log10).hist(
            bins=20, ax=ax, color="#AB47BC", edgecolor="w")
        ax.set_xlabel("log10(Instalações)"); ax.set_ylabel("Frequência")
        ax.set_title("Distribuição de Instalações (log)", fontweight="bold")
        plt.tight_layout()
        fig.savefig(GRAFICOS_DIR / "distribuicao_instalacoes_log.png"); plt.close(fig)

    if "tipo_desenvolvedor" in df.columns and "score" in df.columns:
        fig, ax = plt.subplots()
        df.boxplot(column="score", by="tipo_desenvolvedor", ax=ax)
        ax.set_xlabel("Tipo de Desenvolvedor"); ax.set_ylabel("Score")
        ax.set_title("Score por Tipo de Desenvolvedor", fontweight="bold")
        plt.suptitle(""); plt.tight_layout()
        fig.savefig(GRAFICOS_DIR / "boxplot_score_desenvolvedor.png"); plt.close(fig)

    # ── 5. top apps ───────────────────────────────────────────────────────────
    cols = [c for c in ["title","developer","tipo_desenvolvedor","score",
                        "instalacoes_num","ratings","updated_dt","genreId"]
            if c in df.columns]
    top = df.nlargest(20, "instalacoes_num")[cols].copy()
    top["instalacoes_num"] = top["instalacoes_num"].apply(lambda x: f"{x:,.0f}")
    top.to_csv(TABELAS_DIR / "top_20_apps.csv", index=False, encoding="utf-8-sig")

    # ── 6. temporal ───────────────────────────────────────────────────────────
    if "updated_dt" in df.columns:
        dt = df.dropna(subset=["updated_dt"]).copy()
        dt["mes_upd"] = dt["updated_dt"].dt.to_period("M")
        cnt_m = dt["mes_upd"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(12,6))
        cnt_m.plot(kind="bar", ax=ax, color="#66BB6A", edgecolor="w")
        ax.set_xlabel("Mês"); ax.set_ylabel("Apps atualizados")
        ax.set_title("Distribuição Temporal das Atualizações", fontweight="bold")
        ax.tick_params(axis="x", rotation=45); plt.tight_layout()
        fig.savefig(GRAFICOS_DIR / "atualizacoes_por_mes.png"); plt.close(fig)

    logger.info("Fase 4A concluída.")
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    executar_analise_quantitativa()
