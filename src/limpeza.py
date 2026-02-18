# -*- coding: utf-8 -*-
"""
Fase 3 — Filtragem e limpeza de dados.
Critérios alinhados ao estudo: Sistemas de Informação em Saúde / mHealth.
"""

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

from src.config import (
    RAW_DIR, REVIEWS_DIR, CLEAN_DIR,
    CATEGORIAS_ALVO, MIN_INSTALACOES, DATA_CORTE_ATUALIZACAO,
    KEYWORDS_INCLUSAO, KEYWORDS_EXCLUSAO_TITULO, KEYWORDS_GOV,
)

logger = logging.getLogger(__name__)


def _contem(texto: str, keywords: list[str]) -> bool:
    if not isinstance(texto, str):
        return False
    t = texto.lower()
    return any(k.lower() in t for k in keywords)


def _carregar_brutos() -> tuple[pd.DataFrame, pd.DataFrame]:
    csvs_a = sorted(RAW_DIR.glob("apps_brutos_*.csv"), reverse=True)
    csvs_r = sorted(REVIEWS_DIR.glob("reviews_brutos_*.csv"), reverse=True)
    if not csvs_a:
        raise FileNotFoundError(f"Nenhum arquivo de apps em {RAW_DIR}")
    df_a = pd.read_csv(csvs_a[0], encoding="utf-8-sig")
    df_r = pd.read_csv(csvs_r[0], encoding="utf-8-sig") if csvs_r else pd.DataFrame()
    logger.info(f"Brutos carregados: {len(df_a)} apps, {len(df_r)} reviews")
    return df_a, df_r


def executar_limpeza() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica todos os filtros e retorna (df_apps, df_reviews) limpos."""
    logger.info("=" * 60)
    logger.info("FASE 3 — Filtragem e Limpeza")
    logger.info("=" * 60)

    df, df_r = _carregar_brutos()
    total_bruto = len(df)
    total_rev_bruto = len(df_r)
    etapas = []

    # 1. Duplicatas
    antes = len(df)
    df = df.drop_duplicates(subset=["appId"], keep="first")
    etapas.append(("Remoção de duplicatas", antes, len(df)))

    # 2. Categoria
    antes = len(df)
    df = df[df["genreId"].isin(CATEGORIAS_ALVO)].copy()
    etapas.append(("Filtro por categoria", antes, len(df)))

    # 3. Instalações
    antes = len(df)
    df["instalacoes_num"] = pd.to_numeric(
        df.get("realInstalls", df.get("minInstalls", 0)), errors="coerce"
    ).fillna(0)
    df = df[df["instalacoes_num"] >= MIN_INSTALACOES].copy()
    etapas.append((f"Instalações >= {MIN_INSTALACOES:,}", antes, len(df)))

    # 4. Atualização
    antes = len(df)
    df["updated_dt"] = pd.to_datetime(df["updated"], unit="s", errors="coerce")
    if "lastUpdatedOn" in df.columns:
        mask = df["updated_dt"].isna()
        df.loc[mask, "updated_dt"] = pd.to_datetime(
            df.loc[mask, "lastUpdatedOn"], errors="coerce")
    df = df[df["updated_dt"] >= DATA_CORTE_ATUALIZACAO].copy()
    etapas.append(("Atualização < 24 meses", antes, len(df)))

    # 5. Relevância temática
    antes = len(df)
    df["_texto"] = (df["title"].fillna("") + " " +
                    df["summary"].fillna("") + " " +
                    df["description"].fillna(""))
    mask_inc = df["_texto"].apply(lambda x: _contem(x, KEYWORDS_INCLUSAO))
    mask_exc = df["title"].apply(lambda x: _contem(x, KEYWORDS_EXCLUSAO_TITULO))
    df = df[mask_inc & ~mask_exc].copy()
    df.drop(columns=["_texto"], inplace=True)
    etapas.append(("Relevância temática", antes, len(df)))

    # 6. Classificação de desenvolvedor (3 categorias)
    _KEYWORDS_GOVERNO = [
        "ministério", "ministerio", "secretaria", "governo",
        "prefeitura", "municipal", "estadual", "federal",
        "datasus", "sus", "fiocruz", "anvisa", "ans",
    ]
    _KEYWORDS_INST = [
        "universidade", "university", "usp", "unicamp", "ufmg",
        "instituto", "fundação", "fundacao", "hospital", "associação",
        "crm", "cfm", "cfn", "coren", "cfp", "unimed", "einstein",
    ]

    def _classificar_dev(dev):
        if not isinstance(dev, str):
            return "Comercial"
        d = dev.lower()
        if any(k in d for k in _KEYWORDS_GOVERNO):
            return "Governamental"
        if any(k in d for k in _KEYWORDS_INST):
            return "Institucional"
        return "Comercial"

    df["tipo_desenvolvedor"] = df["developer"].apply(_classificar_dev)

    # 7. Ordenar
    df = df.sort_values("instalacoes_num", ascending=False).reset_index(drop=True)

    # 8. Filtrar reviews
    ids_validos = set(df["appId"])
    if len(df_r):
        df_r = df_r[df_r["appId"].isin(ids_validos)].copy()

    # Salvar
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(CLEAN_DIR / f"apps_limpos_{ts}.csv", index=False, encoding="utf-8-sig")
    df_r.to_csv(CLEAN_DIR / f"reviews_limpos_{ts}.csv", index=False, encoding="utf-8-sig")

    # Relatório textual
    linhas = ["RELATÓRIO DE LIMPEZA", "=" * 40,
              f"Data: {datetime.now().isoformat()}",
              f"Apps brutos: {total_bruto}",
              f"Apps após filtros: {len(df)}",
              f"Reviews brutos: {total_rev_bruto}",
              f"Reviews após filtros: {len(df_r)}",
              "", "ETAPAS:"]
    for nome, a, d in etapas:
        linhas.append(f"  {nome}: {a} → {d}")
    (CLEAN_DIR / "relatorio_limpeza.txt").write_text(
        "\n".join(linhas), encoding="utf-8")

    for nome, a, d in etapas:
        logger.info(f"  {nome}: {a} → {d}")
    logger.info(f"Resultado: {len(df)} apps, {len(df_r)} reviews")
    return df, df_r


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    executar_limpeza()
