#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pipeline Principal — A Onipresença dos Sistemas de Informação em Saúde:
Uma Análise da Integração do Ecossistema mHealth via Dispositivos Móveis

Executa todas as fases sequencialmente:
  1.   Seleção interativa de descritores (palavras-chave) via terminal
  1-2. Coleta de dados (scraping Google Play Store)
  2.5  Lista Word de TODOS os apps coletados (para revisão manual)
  3.   Limpeza e filtragem (critérios de inclusão/exclusão)
  3.5  Seleção interativa dos apps para análise via terminal
  4A.  Análise quantitativa (estatística descritiva e correlação de Pearson)
  4B.  Análise qualitativa (PLN: sentimento, temas, LDA)
  5.   Geração de relatório Word (.docx)
  6.   Conversão automática de todos os CSVs para Word

Uso:
    python pipeline_principal.py                    # executa tudo (interativo)
    python pipeline_principal.py --sem-selecao      # pula seleção de apps (usa todos)
    python pipeline_principal.py --reselecionar     # força nova seleção de apps
    python pipeline_principal.py --descritores-padrao  # usa descritores padrão (não interativo)
    python pipeline_principal.py --fase 1           # apenas coleta (com seleção de descritores)
    python pipeline_principal.py --fase 2.5         # apenas lista Word de revisão
    python pipeline_principal.py --fase 3           # apenas limpeza
    python pipeline_principal.py --fase 3.5         # apenas seleção interativa de apps
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
        description="Pipeline — Sistemas de Informação em Saúde via mHealth")
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
    parser.add_argument(
        "--descritores-padrao", action="store_true",
        help="Usa os descritores padrão sem edição interativa.")
    args = parser.parse_args()
    fases = set(f.lower() for f in args.fase) if args.fase else {"1","2.5","3","3.5","4a","4b","5","6"}

    # determinar modo de seleção de apps
    if args.sem_selecao:
        modo_selecao = "todos"
    elif args.reselecionar:
        modo_selecao = "interativo"
    else:
        from src.config import CLEAN_DIR as _CLEAN
        _sel = _CLEAN / "apps_selecionados.csv"
        if _sel.exists() and args.fase and "3.5" not in (args.fase or []):
            modo_selecao = "carregar"
        else:
            modo_selecao = "interativo"

    # determinar modo de seleção de descritores
    modo_descritores = "padrao" if args.descritores_padrao else "interativo"

    logger = _configurar_log()
    logger.info("=" * 70)
    logger.info("PIPELINE — SISTEMAS DE INFORMAÇÃO EM SAÚDE / mHealth")
    logger.info(f"Fases selecionadas: {sorted(fases)}")
    logger.info("=" * 70)
    t0 = time.time()

    # ── Fase 1-2: Coleta ──────────────────────────────────────────────────
    if "1" in fases:
        logger.info("▶ FASE 1-2: Seleção de descritores + Coleta de dados")
        from src.coleta import executar_coleta
        df_apps, df_reviews = executar_coleta(modo_descritores=modo_descritores)
        logger.info(f"  → {len(df_apps)} apps, {len(df_reviews)} reviews coletados")

    # ── Fase 2.5: Lista Word para revisão ────────────────────────────────
    if "2.5" in fases:
        logger.info("▶ FASE 2.5: Geração da lista Word de apps para revisão")
        from src.lista_coleta import executar_lista_coleta
        # passa o df_apps coletado nesta execução, se disponível
        _df_brutos = df_apps if "1" in fases and "df_apps" in dir() else None
        out25 = executar_lista_coleta(_df_brutos)
        logger.info(f"  → Lista gerada: {out25}")

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
