# -*- coding: utf-8 -*-
"""
Fases 1 + 2 — Busca de descritores e extração de metadados/reviews.
"""

import time
import json
import logging
from datetime import datetime

import pandas as pd
from tqdm import tqdm
from google_play_scraper import search, app as gps_app, reviews, Sort

from src.config import (
    DESCRITORES, MAX_RESULTADOS, MAX_REVIEWS,
    IDIOMA, PAIS, SLEEP_BUSCA, SLEEP_APP,
    RAW_DIR, REVIEWS_DIR, LOG_DIR,
)

logger = logging.getLogger(__name__)


# ── helpers ───────────────────────────────────────────────────────────────────

def _extrair_app(app_id: str) -> dict | None:
    try:
        d = gps_app(app_id, lang=IDIOMA, country=PAIS)
        return {
            "appId": d.get("appId"),
            "title": d.get("title"),
            "summary": d.get("summary"),
            "description": d.get("description"),
            "installs": d.get("installs"),
            "realInstalls": d.get("realInstalls", 0),
            "minInstalls": d.get("minInstalls", 0),
            "score": d.get("score"),
            "ratings": d.get("ratings"),
            "reviews_count": d.get("reviews"),
            "histogram": str(d.get("histogram")),
            "price": d.get("price"),
            "free": d.get("free"),
            "developer": d.get("developer"),
            "developerId": d.get("developerId"),
            "developerEmail": d.get("developerEmail"),
            "developerWebsite": d.get("developerWebsite"),
            "genre": d.get("genre"),
            "genreId": d.get("genreId"),
            "contentRating": d.get("contentRating"),
            "adSupported": d.get("adSupported"),
            "released": d.get("released"),
            "updated": d.get("updated"),
            "lastUpdatedOn": d.get("lastUpdatedOn"),
            "version": d.get("version"),
            "androidVersion": d.get("androidVersion"),
            "androidVersionText": d.get("androidVersionText"),
            "size": d.get("size"),
            "url": d.get("url"),
            "privacyPolicy": d.get("privacyPolicy"),
            "icon": d.get("icon"),
            "data_extracao": datetime.now().isoformat(),
        }
    except Exception:
        return None


def _extrair_reviews(app_id: str) -> list[dict]:
    try:
        revs, _ = reviews(
            app_id, lang=IDIOMA, country=PAIS,
            sort=Sort.NEWEST, count=MAX_REVIEWS,
        )
        return [
            {
                "appId": app_id,
                "userName_hash": hash(r.get("userName", "")),
                "content": r.get("content"),
                "score": r.get("score"),
                "thumbsUpCount": r.get("thumbsUpCount"),
                "reviewCreatedVersion": r.get("reviewCreatedVersion"),
                "at": r.get("at").isoformat() if r.get("at") else None,
                "replyContent": r.get("replyContent"),
                "repliedAt": (r.get("repliedAt").isoformat()
                              if r.get("repliedAt") else None),
                "data_extracao": datetime.now().isoformat(),
            }
            for r in revs
        ]
    except Exception:
        return []


# ── pipeline ──────────────────────────────────────────────────────────────────

def executar_coleta() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Executa Fases 1+2 e retorna (df_apps, df_reviews)."""
    inicio = datetime.now()
    logger.info("=" * 60)
    logger.info("FASES 1+2 — Coleta de Dados na Play Store")
    logger.info(f"Início: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Registrar sessão
    meta = {
        "data_coleta": inicio.isoformat(),
        "descritores": DESCRITORES,
        "n_hits_busca": MAX_RESULTADOS,
        "n_reviews": MAX_REVIEWS,
        "idioma": IDIOMA,
        "pais": PAIS,
    }
    with open(RAW_DIR / "metadados_sessao.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Fase 1 — busca
    logger.info("── FASE 1: Busca de appIds ──")
    ids: set[str] = set()
    for desc in tqdm(DESCRITORES, desc="Descritores"):
        try:
            res = search(desc, lang=IDIOMA, country=PAIS, n_hits=MAX_RESULTADOS)
            novos = {r["appId"] for r in res}
            ids.update(novos)
            logger.info(f"  '{desc}' → {len(novos)} (total único: {len(ids)})")
        except Exception as e:
            logger.warning(f"  Erro em '{desc}': {e}")
        time.sleep(SLEEP_BUSCA)

    logger.info(f"Total de appIds únicos: {len(ids)}")

    # Fase 2 — extração
    logger.info("── FASE 2: Extração de metadados e reviews ──")
    apps_reg, revs_reg = [], []
    for app_id in tqdm(ids, desc="Extraindo apps"):
        m = _extrair_app(app_id)
        if m:
            apps_reg.append(m)
            r = _extrair_reviews(app_id)
            revs_reg.extend(r)
        time.sleep(SLEEP_APP)

    df_apps = pd.DataFrame(apps_reg)
    df_reviews = pd.DataFrame(revs_reg)

    # Salvar brutos
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    df_apps.to_csv(RAW_DIR / f"apps_brutos_{ts}.csv",
                   index=False, encoding="utf-8-sig")
    df_reviews.to_csv(REVIEWS_DIR / f"reviews_brutos_{ts}.csv",
                      index=False, encoding="utf-8-sig")

    logger.info(f"Coleta concluída: {len(df_apps)} apps, "
                f"{len(df_reviews)} reviews ({datetime.now() - inicio})")
    return df_apps, df_reviews


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    executar_coleta()
