#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pipeline Principal — Infodemiologia de Aplicativos de Saúde na Google Play Store

Executa todas as fases sequencialmente:
  1-2. Coleta de dados (scraping Google Play Store)
  3.   Limpeza e filtragem
  3.5  Seleção interativa dos apps para análise
  4A.  Análise quantitativa (estatística descritiva e correlação)
  4B.  Análise qualitativa (PLN: sentimento, temas, LDA)
  5.   Geração de relatório Word (.docx)
  6.   Conversão automática de todos os CSVs para Word

Uso:
    python pipeline_principal.py                    # executa tudo (com seleção)
    python pipeline_principal.py --sem-selecao      # pula a seleção (usa todos)
    python pipeline_principal.py --reselecionar     # força nova seleção
    python pipeline_principal.py --fase 3           # apenas limpeza
    python pipeline_principal.py --fase 3.5         # apenas seleção interativa
    python pipeline_principal.py --fase 4a 4b       # apenas análises
    python pipeline_principal.py --fase 5           # apenas relatório
    python pipeline_principal.py --fase 6           # apenas conversão CSV→Word
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# garante que a raiz do projeto está no sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import LOG_DIR


def _configurar_log():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"pipeline_{ts}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file), encoding="utf-8"),
        ],
    )
    return logging.getLogger("pipeline")


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de Infodemiologia — Aplicativos de Saúde")
    parser.add_argument(
        "--fase", nargs="*", default=None,
        help="Fases a executar: 1 (coleta) 3 (limpeza) 3.5 (seleção) 4a 4b 5 6. "
             "Se omitido, executa todas.")
    parser.add_argument(
        "--sem-selecao", action="store_true",
        help="Pula a seleção interativa e usa todos os apps limpos.")
    parser.add_argument(
        "--reselecionar", action="store_true",
        help="Força nova seleção interativa mesmo que já exista uma seleção salva.")
    args = parser.parse_args()
    fases = set(f.lower() for f in args.fase) if args.fase else {"1","3","3.5","4a","4b","5","6"}

    # determinar modo de seleção
    if args.sem_selecao:
        modo_selecao = "todos"
    elif args.reselecionar:
        modo_selecao = "interativo"
    else:
        # se já existe seleção salva e a fase não foi explicitamente pedida, carrega
        from src.config import CLEAN_DIR as _CLEAN
        _sel = _CLEAN / "apps_selecionados.csv"
        if _sel.exists() and args.fase and "3.5" not in (args.fase or []):
            modo_selecao = "carregar"
        else:
            modo_selecao = "interativo"

    logger = _configurar_log()
    logger.info("=" * 70)
    logger.info("PIPELINE DE INFODEMIOLOGIA — INÍCIO")
    logger.info(f"Fases selecionadas: {sorted(fases)}")
    logger.info("=" * 70)
    t0 = time.time()

    # ── Fase 1-2: Coleta ──────────────────────────────────────────────────
    if "1" in fases:
        logger.info("▶ FASE 1-2: Coleta de dados")
        from src.coleta import executar_coleta
        df_apps, df_reviews = executar_coleta()
        logger.info(f"  → {len(df_apps)} apps, {len(df_reviews)} reviews coletados")

    # ── Fase 3: Limpeza ──────────────────────────────────────────────────
    if "3" in fases:
        logger.info("▶ FASE 3: Limpeza e filtragem")
        from src.limpeza import executar_limpeza
        df_apps, df_reviews = executar_limpeza()
        logger.info(f"  → {len(df_apps)} apps, {len(df_reviews)} reviews após limpeza")
    # ── Fase 3.5: Seleção ───────────────────────────────────────────
    if "3.5" in fases:
        logger.info("▶ FASE 3.5: Seleção interativa de apps para análise")
        from src.selecao import executar_selecao
        df_sel, df_rev_sel = executar_selecao(modo=modo_selecao)
        logger.info(f"  → {len(df_sel)} apps selecionados, {len(df_rev_sel)} reviews")
    # ── Fase 4A: Quantitativa ────────────────────────────────────────────
    if "4a" in fases:
        logger.info("▶ FASE 4A: Análise quantitativa")
        from src.quantitativa import executar_analise_quantitativa
        executar_analise_quantitativa()

    # ── Fase 4B: Qualitativa ─────────────────────────────────────────────
    if "4b" in fases:
        logger.info("▶ FASE 4B: Análise qualitativa (PLN)")
        from src.qualitativa import executar_analise_qualitativa
        executar_analise_qualitativa()

    # ── Fase 5: Relatório Word ───────────────────────────────────────────
    if "5" in fases:
        logger.info("▶ FASE 5: Geração do relatório Word")
        from src.relatorio import executar_relatorio
        out = executar_relatorio()
        logger.info(f"  → Relatório: {out}")

    # ── Fase 6: Conversão CSV → Word ─────────────────────────────────────
    if "6" in fases:
        logger.info("▶ FASE 6: Conversão automática de CSVs para Word")
        import importlib.util, sys as _sys
        spec = importlib.util.spec_from_file_location(
            "csv_para_word", ROOT / "csv_para_word.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        csvs = mod._coletar_csvs(mod.TABELAS_DIR)
        if csvs:
            saida = mod.gerar_documento_unico(csvs)
            logger.info(f"  → Tabelas Word: {saida}")
        else:
            logger.warning("  → Nenhum CSV encontrado em resultados/tabelas/")

    elapsed = time.time() - t0
    logger.info("=" * 70)
    logger.info(f"PIPELINE CONCLUÍDO em {elapsed/60:.1f} minutos")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
