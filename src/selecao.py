# -*- coding: utf-8 -*-
"""
Fase 3.5 — Seleção interativa de aplicativos para análise.

Exibe a lista de apps limpos em uma tabela numerada e permite ao usuário
escolher quais incluir antes que as fases de análise sejam executadas.

Os arquivos de saída são salvos como:
  dados/limpos/apps_selecionados.csv
  dados/limpos/reviews_selecionados.csv

As fases 4A/4B usam esses arquivos quando existirem.
"""

import logging
import shutil
from pathlib import Path

import pandas as pd

from src.config import CLEAN_DIR

logger = logging.getLogger(__name__)

# Colunas exibidas na tabela de seleção (as que existirem no CSV)
COLS_EXIBIR = [
    "appId", "title", "developer", "tipo_desenvolvedor",
    "score", "instalacoes_num", "genreId",
]

# Nomes legíveis para exibição
ALIAS = {
    "appId":              "App ID",
    "title":              "Nome",
    "developer":          "Desenvolvedor",
    "tipo_desenvolvedor": "Tipo Dev.",
    "score":              "Nota",
    "instalacoes_num":    "Instalações",
    "genreId":            "Categoria",
}


# ─────────────────────────────────────────────────────────────────────────────
def _carregar_limpos() -> tuple[pd.DataFrame, pd.DataFrame]:
    csv_a = sorted(CLEAN_DIR.glob("apps_limpos_*.csv"), reverse=True)
    csv_r = sorted(CLEAN_DIR.glob("reviews_limpos_*.csv"), reverse=True)
    if not csv_a:
        raise FileNotFoundError(f"Nenhum arquivo apps_limpos_*.csv em {CLEAN_DIR}")
    df_a = pd.read_csv(csv_a[0], encoding="utf-8-sig")
    df_r = pd.read_csv(csv_r[0], encoding="utf-8-sig") if csv_r else pd.DataFrame()
    return df_a, df_r


def _exibir_tabela(df: pd.DataFrame) -> None:
    """Imprime a tabela numerada de apps no console."""
    cols = [c for c in COLS_EXIBIR if c in df.columns]
    df_show = df[cols].copy()
    df_show.rename(columns={c: ALIAS.get(c, c) for c in cols}, inplace=True)

    # formata instalações
    if "Instalações" in df_show.columns:
        df_show["Instalações"] = df_show["Instalações"].apply(
            lambda x: f"{int(x):,}" if pd.notna(x) else "?"
        )
    # formata nota
    if "Nota" in df_show.columns:
        df_show["Nota"] = df_show["Nota"].apply(
            lambda x: f"{x:.1f}" if pd.notna(x) else "?"
        )
    # trunca colunas longas
    for col in ["Nome", "Desenvolvedor", "App ID"]:
        if col in df_show.columns:
            df_show[col] = df_show[col].str.slice(0, 40)

    # largura do terminal
    term_w = shutil.get_terminal_size(fallback=(120, 40)).columns
    sep = "─" * min(term_w, 130)

    print()
    print(sep)
    print("  LISTA DE APLICATIVOS APÓS FILTRAGEM")
    print(sep)

    # cabeçalho com índice
    idx_w  = 4
    col_ws = {}
    for col in df_show.columns:
        max_len = max(df_show[col].astype(str).map(len).max(), len(col))
        col_ws[col] = min(max_len + 2, 42)

    header = f"{'Nº':>{idx_w}} "
    header += " ".join(f"{col:<{col_ws[col]}}" for col in df_show.columns)
    print(header)
    print("─" * min(len(header) + 4, 130))

    for i, (_, row) in enumerate(df_show.iterrows(), start=1):
        line = f"{i:>{idx_w}} "
        line += " ".join(f"{str(row[col]):<{col_ws[col]}}" for col in df_show.columns)
        print(line)

    print(sep)
    print(f"  Total: {len(df)} aplicativo(s)")
    print(sep)


def _parse_entrada(entrada: str, total: int) -> set[int]:
    """
    Converte string de entrada em conjunto de índices 1-based.
    Aceita: '1 3 5', '1,3,5', '2-6', '1-3 7 9-11'
    Retorna conjunto de índices válidos.
    """
    indices: set[int] = set()
    # unifica separadores
    tokens = entrada.replace(",", " ").split()
    for tok in tokens:
        if "-" in tok:
            partes = tok.split("-")
            if len(partes) == 2:
                try:
                    a, b = int(partes[0]), int(partes[1])
                    indices.update(range(a, b + 1))
                except ValueError:
                    print(f"  Entrada ignorada: '{tok}'")
        else:
            try:
                indices.add(int(tok))
            except ValueError:
                print(f"  Entrada ignorada: '{tok}'")
    # limitar ao intervalo válido
    return {i for i in indices if 1 <= i <= total}


# ─────────────────────────────────────────────────────────────────────────────
def executar_selecao(modo: str = "interativo") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Exibe a lista de apps limpos e permite seleção interativa.

    Parâmetros
    ----------
    modo : str
        'interativo' → prompt no terminal (padrão)
        'todos'      → seleciona todos sem perguntar
        'carregar'   → carrega seleção já salva (apps_selecionados.csv)

    Retorna
    -------
    (df_apps_sel, df_reviews_sel)
    """
    logger.info("=" * 60)
    logger.info("FASE 3.5 — Seleção de Aplicativos para Análise")
    logger.info("=" * 60)

    # ── modo 'carregar': reutilizar seleção anterior ──────────────────────
    sel_path   = CLEAN_DIR / "apps_selecionados.csv"
    rev_sel_path = CLEAN_DIR / "reviews_selecionados.csv"
    if modo == "carregar":
        if sel_path.exists():
            df_sel = pd.read_csv(sel_path, encoding="utf-8-sig")
            df_rev_sel = (pd.read_csv(rev_sel_path, encoding="utf-8-sig")
                          if rev_sel_path.exists() else pd.DataFrame())
            logger.info(f"  Seleção carregada: {len(df_sel)} apps")
            return df_sel, df_rev_sel
        else:
            logger.warning("  Nenhuma seleção prévia encontrada → usando todos")
            modo = "todos"

    df_apps, df_rev = _carregar_limpos()
    total = len(df_apps)

    # ── modo 'todos': pula interação ──────────────────────────────────────
    if modo == "todos":
        df_apps.to_csv(sel_path, index=False, encoding="utf-8-sig")
        if not df_rev.empty:
            df_rev.to_csv(rev_sel_path, index=False, encoding="utf-8-sig")
        logger.info(f"  Todos os {total} apps selecionados automaticamente")
        return df_apps, df_rev

    # ── modo 'interativo' ─────────────────────────────────────────────────
    _exibir_tabela(df_apps)

    print("""
COMO SELECIONAR:
  ┌─────────────────────────────────────────────────────────────────────┐
  │  • Enter (vazio)     → manter TODOS os aplicativos                 │
  │  • Números por vírgula/espaço → INCLUIR apenas esses               │
  │    Ex.: 1 3 5                                                       │
  │  • Faixas com hífen → INCLUIR faixa                                │
  │    Ex.: 1-10 15 20-25                                               │
  │  • Digite 'excluir' e os números → REMOVER da lista completa       │
  │    Ex.: excluir 4 7 12                                              │
  └─────────────────────────────────────────────────────────────────────┘""")

    while True:
        try:
            entrada = input("\n> Sua seleção: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Interrompido — usando todos os apps.")
            entrada = ""

        # ── Enter: aceitar todos ──────────────────────────────────────────
        if not entrada:
            indices_sel = set(range(1, total + 1))
            print(f"\n  ✔ Todos os {total} apps incluídos.")
            break

        # ── modo exclusão ─────────────────────────────────────────────────
        if entrada.lower().startswith("excluir"):
            resto = entrada[len("excluir"):].strip()
            excluir = _parse_entrada(resto, total)
            if not excluir:
                print("  Nenhum número válido informado para exclusão. Tente novamente.")
                continue
            indices_sel = set(range(1, total + 1)) - excluir
            if not indices_sel:
                print("  Isso excluiria todos os apps. Tente novamente.")
                continue
            print(f"\n  ✔ {len(indices_sel)} apps incluídos "
                  f"(excluídos: {sorted(excluir)}).")
            break

        # ── modo inclusão explícita ───────────────────────────────────────
        indices_sel = _parse_entrada(entrada, total)
        if not indices_sel:
            print("  Nenhum número válido reconhecido. Tente novamente.")
            continue
        print(f"\n  ✔ {len(indices_sel)} apps selecionados: {sorted(indices_sel)}")

        # confirmação
        try:
            conf = input("  Confirmar? [S/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            conf = "s"
        if conf in ("", "s", "sim", "y", "yes"):
            break
        print("  Seleção cancelada. Tente novamente.")

    # ── filtrar dataframes ────────────────────────────────────────────────
    idx_list = sorted(indices_sel)
    df_sel = df_apps.iloc[[i - 1 for i in idx_list]].reset_index(drop=True)

    ids_validos = set(df_sel["appId"]) if "appId" in df_sel.columns else set()
    df_rev_sel  = (df_rev[df_rev["appId"].isin(ids_validos)].reset_index(drop=True)
                   if not df_rev.empty and "appId" in df_rev.columns
                   else df_rev.copy())

    # exibir resumo dos selecionados
    print()
    print("─" * 60)
    print("  APPS SELECIONADOS PARA ANÁLISE")
    print("─" * 60)
    for i, (_, row) in enumerate(df_sel.iterrows(), start=1):
        title = str(row.get("title", row.get("appId", "?")))[:50]
        nota  = f"{row['score']:.1f}" if pd.notna(row.get("score")) else "?"
        print(f"  {i:>3}. {title:<50}  nota={nota}")
    print("─" * 60)
    print(f"  {len(df_sel)} apps · {len(df_rev_sel):,} avaliações")
    print("─" * 60)

    # ── salvar seleção ────────────────────────────────────────────────────
    df_sel.to_csv(sel_path, index=False, encoding="utf-8-sig")
    df_rev_sel.to_csv(rev_sel_path, index=False, encoding="utf-8-sig")

    logger.info(f"  Seleção salva: {len(df_sel)} apps, {len(df_rev_sel)} reviews")
    logger.info(f"  → {sel_path}")
    return df_sel, df_rev_sel


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    executar_selecao()
