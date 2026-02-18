# -*- coding: utf-8 -*-
"""
Fases 1 + 2 — Seleção interativa de descritores, busca e extração de metadados/reviews.

Fase 1:  O usuário pode revisar, adicionar ou remover palavras-chave de busca
         (descritores) via terminal antes da coleta começar.
Fase 2:  Extração automatizada de metadados e avaliações de cada app encontrado.
"""

import shutil
import time
import json
import logging
from datetime import datetime

import pandas as pd
from tqdm import tqdm
from google_play_scraper import search, app as gps_app, reviews, Sort

from src.config import (
    DESCRITORES, DESCRITORES_PADRAO, MAX_RESULTADOS, MAX_REVIEWS,
    IDIOMA, PAIS, SLEEP_BUSCA, SLEEP_APP,
    RAW_DIR, REVIEWS_DIR, LOG_DIR,
)

logger = logging.getLogger(__name__)


# ── seleção interativa de descritores ─────────────────────────────────────────

def selecionar_descritores(modo: str = "interativo") -> list[str]:
    """
    Exibe os descritores padrão e permite ao usuário editá-los via terminal.

    Parâmetros
    ----------
    modo : str
        'interativo' → mostra e permite editar (padrão)
        'padrao'     → usa os descritores padrão sem perguntar

    Retorna
    -------
    Lista de descritores selecionados.
    """
    descritores = list(DESCRITORES_PADRAO)

    if modo == "padrao":
        return descritores

    term_w = shutil.get_terminal_size(fallback=(120, 40)).columns
    sep = "═" * min(term_w, 80)

    print()
    print(sep)
    print("  FASE 1 — SELEÇÃO DE DESCRITORES (PALAVRAS-CHAVE)")
    print(sep)
    print()
    print("  Os descritores abaixo serão usados para buscar aplicativos")
    print("  na Google Play Store. Eles estão alinhados ao tema:")
    print("  'Sistemas de Informação em Saúde / mHealth'")
    print()

    _exibir_descritores(descritores)

    print("""
  OPÇÕES:
  ┌──────────────────────────────────────────────────────────────────────┐
  │  Enter (vazio)   → ACEITAR todos os descritores acima               │
  │  + termo         → ADICIONAR novo descritor                         │
  │    Ex: + saúde mental SIS                                           │
  │  - número(s)     → REMOVER descritor(es) pelo número                │
  │    Ex: - 3 7 12                                                     │
  │  = lista         → SUBSTITUIR TODOS por nova lista (sep. por ;)     │
  │    Ex: = mHealth; prontuário; e-SUS; telemedicina                   │
  │  ok              → CONFIRMAR e iniciar coleta                       │
  └──────────────────────────────────────────────────────────────────────┘""")

    while True:
        try:
            entrada = input("\n> Descritores: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Usando descritores padrão.")
            break

        if not entrada or entrada.lower() in ("ok", "confirmar"):
            break

        # ── adicionar ─────────────────────────────────────────────────
        if entrada.startswith("+"):
            novo = entrada[1:].strip()
            if novo and novo not in descritores:
                descritores.append(novo)
                print(f"  ✔ Adicionado: '{novo}'")
            elif novo in descritores:
                print(f"  ⚠ '{novo}' já existe na lista.")
            else:
                print("  ⚠ Nenhum termo informado.")
            _exibir_descritores(descritores)
            continue

        # ── remover ───────────────────────────────────────────────────
        if entrada.startswith("-"):
            nums = entrada[1:].strip().replace(",", " ").split()
            removidos = []
            for n in nums:
                try:
                    idx = int(n) - 1
                    if 0 <= idx < len(descritores):
                        removidos.append(descritores[idx])
                except ValueError:
                    pass
            for r in removidos:
                descritores.remove(r)
                print(f"  ✔ Removido: '{r}'")
            if not removidos:
                print("  ⚠ Nenhum número válido.")
            _exibir_descritores(descritores)
            continue

        # ── substituir tudo ───────────────────────────────────────────
        if entrada.startswith("="):
            novos = [d.strip() for d in entrada[1:].split(";") if d.strip()]
            if novos:
                descritores = novos
                print(f"  ✔ Lista substituída ({len(descritores)} descritores).")
                _exibir_descritores(descritores)
            else:
                print("  ⚠ Lista vazia. Use ponto-e-vírgula como separador.")
            continue

        print("  ⚠ Comando não reconhecido. Use +, -, =, ou Enter.")

    # atualizar a variável global para que o pipeline use os descritores escolhidos
    DESCRITORES.clear()
    DESCRITORES.extend(descritores)

    print(f"\n  ✔ {len(descritores)} descritor(es) confirmados para a busca.")
    print()
    return descritores


def _exibir_descritores(descritores: list[str]) -> None:
    """Imprime a lista numerada de descritores."""
    print()
    for i, d in enumerate(descritores, 1):
        print(f"  {i:>3}. {d}")
    print(f"\n  Total: {len(descritores)} descritor(es)")


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

def executar_coleta(modo_descritores: str = "interativo") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Executa Fases 1+2 e retorna (df_apps, df_reviews).

    Parâmetros
    ----------
    modo_descritores : str
        'interativo' → permite ao usuário editar descritores via terminal
        'padrao'     → usa descritores padrão sem perguntar
    """
    # ── Fase 1: Seleção de descritores ────────────────────────────────────
    descritores = selecionar_descritores(modo=modo_descritores)

    inicio = datetime.now()
    logger.info("=" * 60)
    logger.info("FASES 1+2 — Coleta de Dados na Play Store")
    logger.info(f"Início: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Descritores: {len(descritores)}")
    logger.info("=" * 60)

    # Registrar sessão
    meta = {
        "data_coleta": inicio.isoformat(),
        "descritores": descritores,
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
    for desc in tqdm(descritores, desc="Descritores"):
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
