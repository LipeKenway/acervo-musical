r"""Consultas DuckDB no lake Parquet — as primeiras queries SQL de verdade.

Lê a zona curated (Parquet particionado por década, espelho local do
lake) e roda queries analíticas reais, imprimindo tabelas legíveis.
Na Fase 5, o mesmo SQL roda com o httpfs do DuckDB apontando para o
S3 real; por ora, lemos o espelho local (mesmo formato, mesmo hive).

Uso: python src\transform\consultas_duckdb.py
"""

from pathlib import Path

import duckdb

LAKE_LOCAL = Path("data/lake/curated/acervo_prata")
FONTE = f"read_parquet('{LAKE_LOCAL.as_posix()}/*/*.parquet', hive_partitioning=1)"

CONSULTAS = [
    (
        "Top 10 gêneros por peso",
        f"""
        SELECT genero,
               COUNT(*) AS faixas,
               ROUND(SUM(tamanho_bytes) / 1024**3, 2) AS gb
        FROM {FONTE}
        GROUP BY genero
        ORDER BY gb DESC
        LIMIT 10
    """,
    ),
    (
        "Evolução por década",
        f"""
        SELECT decada,
               COUNT(*) AS faixas,
               ROUND(SUM(duracao_seg) / 86400, 1) AS dias_de_audio
        FROM {FONTE}
        GROUP BY decada
        ORDER BY decada
    """,
    ),
    (
        "Top 10 Subgenre (tag MOOD)",
        f"""
        SELECT subgenero_tag AS subgenre, COUNT(*) AS faixas
        FROM {FONTE}
        GROUP BY subgenero_tag
        ORDER BY faixas DESC
        LIMIT 10
    """,
    ),
    (
        "Album Type (tag MOVEMENTNAME)",
        f"""
        SELECT tipo_album_tag AS album_type, COUNT(*) AS faixas
        FROM {FONTE}
        GROUP BY tipo_album_tag
        ORDER BY faixas DESC
    """,
    ),
    (
        "Container: peso e bitrate médio",
        f"""
        SELECT container,
               COUNT(*) AS faixas,
               ROUND(AVG(bitrate_kbps), 0) AS bitrate_medio,
               ROUND(SUM(tamanho_bytes) / 1024**3, 2) AS gb
        FROM {FONTE}
        GROUP BY container
        ORDER BY gb DESC
    """,
    ),
]


def main() -> None:
    con = duckdb.connect()
    for titulo, sql in CONSULTAS:
        print(f"\n=== {titulo} ===")
        resultado = con.execute(sql)
        colunas = [d[0] for d in resultado.description]
        print(" | ".join(colunas))
        for linha in resultado.fetchall():
            print(" | ".join(str(c) for c in linha))
    print()


if __name__ == "__main__":
    main()
