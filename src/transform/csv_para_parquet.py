r"""CSV -> Parquet particionado por década + upload para o lake (API S3).

Lê a camada prata (acervo_prata.csv), grava Parquet particionado por
década em data/lake/curated/ e sobe tudo para o lake via boto3
(endpoint e bucket vindos do .env: LAKE_ENDPOINT / LAKE_BUCKET).

Zonas do lake (prefixos, não pastas reais):
- raw/      -> cópia imutável do CSV como chegou
- curated/  -> Parquet particionado por década (este script)
- gold/     -> agregados modelados (Fase 3, dbt)

No fim roda o benchmark CSV × Parquet (tamanho, leitura completa e
query agregada via DuckDB) e salva data/exports/benchmark_csv_parquet.csv
— a prova numérica que vai para o README.

Convenção: decada=0 no Parquet significa "sem ano" (null na prata).
Credenciais S3 são dummy: o SeaweedFS local roda sem IAM (ADR-006);
o boto3 só exige valores não vazios para assinar as requisições.

Uso: python src\transform\csv_para_parquet.py
"""

import csv
import os
import time
from pathlib import Path

import boto3  # type: ignore[import-untyped]
import duckdb
import pyarrow as pa  # type: ignore[import-untyped]
import pyarrow.compute as pc  # type: ignore[import-untyped]
import pyarrow.csv as pcsv  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]
from dotenv import load_dotenv

PRATA = Path("data/processed/acervo_prata.csv")
LAKE_LOCAL = Path("data/lake/curated/acervo_prata")
EXPORTS = Path("data/exports")
BENCH = EXPORTS / "benchmark_csv_parquet.csv"

QUERY_BENCH = (
    "SELECT genero, COUNT(*) AS faixas, SUM(tamanho_bytes) AS bytes_totais "
    "FROM {fonte} GROUP BY genero ORDER BY bytes_totais DESC LIMIT 10"
)


def cliente_s3() -> tuple:
    """Cliente S3 apontando para o lake local (ADR-004: mesmo código da F5)."""
    load_dotenv()
    endpoint = os.getenv("LAKE_ENDPOINT", "http://127.0.0.1:8333")
    bucket = os.getenv("LAKE_BUCKET", "acervo-musical")
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id="acervo",
        aws_secret_access_key="acervo-local",
    )
    return s3, bucket


def garantir_bucket(s3, bucket: str) -> None:
    nomes = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    if bucket not in nomes:
        s3.create_bucket(Bucket=bucket)
        print(f"  ✅ bucket criado: {bucket}")
    else:
        print(f"  ✅ bucket já existe: {bucket}")


def subir_arvore(s3, bucket: str, raiz: Path, prefixo: str) -> int:
    """Sobe cada arquivo de raiz para prefixo/, preservando o caminho."""
    n = 0
    for arquivo in sorted(raiz.rglob("*")):
        if arquivo.is_file():
            chave = prefixo + arquivo.relative_to(raiz).as_posix()
            s3.upload_file(str(arquivo), bucket, chave)
            n += 1
    return n


def ler_prata():
    """Lê o CSV da prata e normaliza decada (null -> 0 = 'sem ano')."""
    tabela = pcsv.read_csv(PRATA)
    if tabela.schema.field(0).name.startswith("\ufeff"):
        tabela = tabela.rename_columns([n.lstrip("\ufeff") for n in tabela.schema.names])
    idx = tabela.schema.get_field_index("decada")
    decada = pc.fill_null(tabela.column("decada"), 0).cast(pa.int32())
    return tabela.set_column(idx, "decada", decada)


def main() -> None:
    s3, bucket = cliente_s3()
    garantir_bucket(s3, bucket)

    print(f"\nLendo prata: {PRATA}")
    tabela = ler_prata()
    print(f"  {tabela.num_rows:,} linhas | {tabela.num_columns} colunas")

    print(f"\nEscrevendo Parquet particionado por década em {LAKE_LOCAL} ...")
    LAKE_LOCAL.mkdir(parents=True, exist_ok=True)
    pq.write_to_dataset(
        tabela,
        root_path=str(LAKE_LOCAL),
        partition_cols=["decada"],
        compression="snappy",
        existing_data_behavior="overwrite_or_ignore",
    )
    arquivos_parquet = sorted(LAKE_LOCAL.rglob("*.parquet"))
    decadas = sorted({p.parent.name for p in arquivos_parquet})
    print(f"  ✅ {len(arquivos_parquet)} arquivos Parquet em {len(decadas)} partições")
    print(f"  partições: {', '.join(decadas)}")

    print("\nSubindo para o lake (API S3)...")
    s3.upload_file(str(PRATA), bucket, "raw/acervo_prata.csv")
    n_curated = subir_arvore(s3, bucket, LAKE_LOCAL, "curated/acervo_prata/")
    print(f"  ✅ raw: 1 objeto | curated: {n_curated:,} objetos")

    print("\n=== BENCHMARK CSV × PARQUET ===")
    mb_csv = PRATA.stat().st_size / 1024**2
    mb_parquet = sum(p.stat().st_size for p in arquivos_parquet) / 1024**2
    print(f"Tamanho:          CSV {mb_csv:,.1f} MB | Parquet {mb_parquet:,.1f} MB ({mb_csv / mb_parquet:.1f}x menor)")

    t0 = time.perf_counter()
    pcsv.read_csv(PRATA)
    t_leitura_csv = time.perf_counter() - t0
    t0 = time.perf_counter()
    pq.read_table(str(LAKE_LOCAL))
    t_leitura_parquet = time.perf_counter() - t0
    print(
        f"Leitura completa: CSV {t_leitura_csv:.2f}s | Parquet {t_leitura_parquet:.2f}s "
        f"({t_leitura_csv / t_leitura_parquet:.1f}x mais rápido)"
    )

    con = duckdb.connect()
    glob_parquet = LAKE_LOCAL.as_posix() + "/*/*.parquet"
    t0 = time.perf_counter()
    con.execute(QUERY_BENCH.format(fonte=f"read_csv_auto('{PRATA.as_posix()}')")).fetchall()
    t_query_csv = time.perf_counter() - t0
    t0 = time.perf_counter()
    con.execute(QUERY_BENCH.format(fonte=f"read_parquet('{glob_parquet}', hive_partitioning=1)")).fetchall()
    t_query_parquet = time.perf_counter() - t0
    print(
        f"Query DuckDB:     CSV {t_query_csv:.2f}s | Parquet {t_query_parquet:.2f}s "
        f"({t_query_csv / t_query_parquet:.1f}x mais rápido)"
    )

    resumo = con.execute(
        "SELECT decada, COUNT(*) AS faixas FROM read_parquet("
        f"'{glob_parquet}', hive_partitioning=1) GROUP BY decada ORDER BY decada"
    ).fetchall()
    print("\nFaixas por década (partições hive lidas pelo DuckDB):")
    for decada, faixas in resumo:
        print(f"  {decada:<8} {faixas:>8,}")

    EXPORTS.mkdir(parents=True, exist_ok=True)
    with BENCH.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["metrica", "csv", "parquet", "ganho"])
        w.writerow(
            [
                "tamanho_mb",
                f"{mb_csv:.1f}",
                f"{mb_parquet:.1f}",
                f"{mb_csv / mb_parquet:.1f}x menor",
            ]
        )
        w.writerow(
            [
                "leitura_completa_s",
                f"{t_leitura_csv:.2f}",
                f"{t_leitura_parquet:.2f}",
                f"{t_leitura_csv / t_leitura_parquet:.1f}x mais rapido",
            ]
        )
        w.writerow(
            [
                "query_duckdb_s",
                f"{t_query_csv:.2f}",
                f"{t_query_parquet:.2f}",
                f"{t_query_csv / t_query_parquet:.1f}x mais rapido",
            ]
        )
    print(f"\nBenchmark salvo em: {BENCH}")


if __name__ == "__main__":
    main()
