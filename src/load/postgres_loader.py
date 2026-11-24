r"""Carga prata -> Postgres (FASE 3): upsert idempotente + watermark.

Lê acervo_prata.csv e carrega em public.prata_faixas com UPSERT
(ON CONFLICT path_hash DO UPDATE): rerodar nunca duplica.
A chave natural é path_hash = sha256(raiz|caminho_relativo) —
pseudonimização do caminho (checklist da FASE 3) e garantia de que
a mesma faixa em duas raízes nunca colide (ADR-009).

Incremento real: a tabela pipeline_state guarda o watermark
(maior mtime_iso já carregado); cada run processa só linhas com
mtime_iso > watermark. Segundo run seguido = 0 linhas.

Credenciais: POSTGRES_USER/PASSWORD/DB do .env (bind 127.0.0.1).
Service accounts (acervo_app / acervo_bi) entram no passo 5 da FASE 3.

Uso: python src\load\postgres_loader.py
"""

import csv
import hashlib
import os
from pathlib import Path

import psycopg2  # type: ignore[import-untyped]
from dotenv import load_dotenv
from psycopg2.extras import execute_values  # type: ignore[import-untyped]

PRATA = Path("data/processed/acervo_prata.csv")
ETAPA = "prata_faixas"

COLUNAS = [
    "path_hash",
    "raiz",
    "caminho_relativo",
    "nome_arquivo",
    "genero",
    "subgenero_pasta",
    "tipo_pasta",
    "tipo_final",
    "tipo_origem",
    "pasta_album",
    "pasta_disco",
    "titulo",
    "artista",
    "album",
    "album_artista",
    "genero_tag",
    "subgenero_tag",
    "tipo_album_tag",
    "ano",
    "decada",
    "container",
    "formato_tag",
    "bitrate_kbps",
    "modo_bitrate",
    "sample_rate_hz",
    "bits_por_amostra",
    "canais",
    "duracao_seg",
    "tamanho_bytes",
    "mtime_iso",
]

DDL = """
CREATE TABLE IF NOT EXISTS pipeline_state (
    etapa         TEXT PRIMARY KEY,
    watermark     TEXT NOT NULL,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS prata_faixas (
    path_hash        CHAR(64) PRIMARY KEY,
    raiz             TEXT NOT NULL,
    caminho_relativo TEXT NOT NULL,
    nome_arquivo     TEXT,
    genero           TEXT,
    subgenero_pasta  TEXT,
    tipo_pasta       TEXT,
    tipo_final       TEXT,
    tipo_origem      TEXT,
    pasta_album      TEXT,
    pasta_disco      TEXT,
    titulo           TEXT,
    artista          TEXT,
    album            TEXT,
    album_artista    TEXT,
    genero_tag       TEXT,
    subgenero_tag    TEXT,
    tipo_album_tag   TEXT,
    ano              INTEGER,
    decada           INTEGER,
    container        TEXT,
    formato_tag      TEXT,
    bitrate_kbps     INTEGER,
    modo_bitrate     TEXT,
    sample_rate_hz   INTEGER,
    bits_por_amostra INTEGER,
    canais           INTEGER,
    duracao_seg      DOUBLE PRECISION,
    tamanho_bytes    BIGINT,
    mtime_iso        TEXT
);
"""


def path_hash(raiz: str, caminho_relativo: str) -> str:
    """Impressão digital do caminho: sha256(raiz|relativo) (ADR-009)."""
    return hashlib.sha256(f"{raiz}|{caminho_relativo}".encode("utf-8")).hexdigest()


def _int(valor: str | None) -> int | None:
    try:
        return int(float(valor or ""))
    except ValueError:
        return None


def _float(valor: str | None) -> float | None:
    try:
        return float(valor or "")
    except ValueError:
        return None


def linha_sql(linha: dict) -> tuple:
    """Converte uma linha da prata na tupla na ordem de COLUNAS."""
    return (
        path_hash(linha["raiz"], linha["caminho_relativo"]),
        linha["raiz"],
        linha["caminho_relativo"],
        linha["nome_arquivo"],
        linha["genero"],
        linha["subgenero_pasta"],
        linha["tipo_pasta"],
        linha["tipo_final"],
        linha["tipo_origem"],
        linha["pasta_album"],
        linha["pasta_disco"],
        linha["titulo"],
        linha["artista"],
        linha["album"],
        linha["album_artista"],
        linha["genero_tag"],
        linha["subgenero_tag"],
        linha["tipo_album_tag"],
        _int(linha["ano"]),
        _int(linha["decada"]),
        linha["container"],
        linha["formato_tag"],
        _int(linha["bitrate_kbps"]),
        linha["modo_bitrate"],
        _int(linha["sample_rate_hz"]),
        _int(linha["bits_por_amostra"]),
        _int(linha["canais"]),
        _float(linha["duracao_seg"]),
        _int(linha["tamanho_bytes"]),
        linha["mtime_iso"],
    )


def main() -> None:
    load_dotenv()
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute(
                "SELECT watermark FROM pipeline_state WHERE etapa = %s",
                (ETAPA,),
            )
            row = cur.fetchone()
            watermark = row[0] if row else "0000-00-00T00:00:00"

    with PRATA.open(encoding="utf-8-sig") as fh:
        prata = list(csv.DictReader(fh))
    pendentes = [linha for linha in prata if (linha["mtime_iso"] or "") > watermark]
    print(f"Prata: {len(prata):,} linhas | watermark atual: {watermark}")
    print(f"Pendentes (mtime > watermark): {len(pendentes):,}")

    if pendentes:
        valores = [linha_sql(linha) for linha in pendentes]
        set_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in COLUNAS if c != "path_hash")
        sql = (
            f"INSERT INTO prata_faixas ({', '.join(COLUNAS)}) VALUES %s "
            f"ON CONFLICT (path_hash) DO UPDATE SET {set_clause}"
        )
        with conn:
            with conn.cursor() as cur:
                execute_values(cur, sql, valores, page_size=1000)
                novo_wm = max(linha["mtime_iso"] for linha in pendentes)
                cur.execute(
                    "INSERT INTO pipeline_state (etapa, watermark) "
                    "VALUES (%s, %s) "
                    "ON CONFLICT (etapa) DO UPDATE SET "
                    "watermark = EXCLUDED.watermark, atualizado_em = now()",
                    (ETAPA, novo_wm),
                )
        print(f"✅ upsert de {len(valores):,} linhas | watermark -> {novo_wm}")
    else:
        print("✅ nada a carregar (idempotência: rerodar não duplica)")

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM prata_faixas")
        total = cur.fetchone()[0]
    print(f"prata_faixas no Postgres: {total:,} linhas")
    conn.close()


if __name__ == "__main__":
    main()
