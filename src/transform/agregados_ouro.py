r"""Agregados ouro — resumos prontos para Excel/BI.

Relê a camada prata e produz, em data/exports/:
- ouro_genero.csv            (qtd, GB e duração por gênero)
- ouro_container.csv         (MP3 vs M4A vs FLAC: qtd, GB, % do peso)
- ouro_genero_container.csv  (cruzado: onde mora o peso)
- ouro_bitrate.csv           (128/192/256/320 kbps vs lossless)
- ouro_decada.csv            (qtd, GB e duração por década)
- ouro_evolucao_storage.csv  (snapshot append-only p/ gráfico do HD)

Um dono por artefato: o ouro NUNCA escreve na prata/bronze.
Uso: python src\transform\agregados_ouro.py
"""

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PRATA = Path("data/processed/acervo_prata.csv")
EXPORTS = Path("data/exports")
EVOLUCAO = EXPORTS / "ouro_evolucao_storage.csv"

GB = 1024 ** 3


def grupo_bitrate(linha: dict) -> str:
    """Agrupa o bitrate em faixas legíveis para análise."""
    container = linha["container"]
    if container == "FLAC":
        return "FLAC lossless"
    if container != "MP3":
        return "M4A/AAC"
    try:
        k = int(float(linha["bitrate_kbps"] or 0))
    except ValueError:
        return "MP3 sem bitrate"
    if k <= 128:
        return "MP3 ate 128 kbps"
    if k <= 192:
        return "MP3 129-192 kbps"
    if k <= 256:
        return "MP3 193-256 kbps"
    return "MP3 257-320+ kbps"


def duracao_legivel(seg: float) -> str:
    dias = seg / 86400
    if dias >= 1:
        return f"{dias:.1f} dias"
    return f"{seg / 3600:.1f} horas"


class Acumulador:
    """Soma qtd, bytes e segundos para cada chave que aparecer."""

    def __init__(self):
        self.dados = defaultdict(lambda: [0, 0.0, 0.0])

    def soma(self, chave, linha: dict) -> None:
        acc = self.dados[chave]
        acc[0] += 1
        acc[1] += float(linha["tamanho_bytes"] or 0)
        acc[2] += float(linha["duracao_seg"] or 0)

    def linhas(self, nomes_chave):
        if isinstance(nomes_chave, str):
            nomes_chave = [nomes_chave]
        saida = []
        for chave, (qtd, bytes_, seg) in sorted(
            self.dados.items(), key=lambda kv: -kv[1][1]
        ):
            if not isinstance(chave, tuple):
                chave = (chave,)
            saida.append(
                {
                    **dict(zip(nomes_chave, chave)),
                    "qtd_faixas": qtd,
                    "tamanho_gb": round(bytes_ / GB, 2),
                    "duracao": duracao_legivel(seg),
                }
            )
        return saida


def escrever(nome: str, nomes_chave, linhas) -> None:
    if isinstance(nomes_chave, str):
        nomes_chave = [nomes_chave]
    campos = list(nomes_chave) + ["qtd_faixas", "tamanho_gb", "duracao"]
    with (EXPORTS / nome).open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    print(f"  ✅ {nome} ({len(linhas)} linhas)")


def main() -> None:
    with PRATA.open(encoding="utf-8-sig") as fh:
        prata = list(csv.DictReader(fh))

    print(f"Prata lida: {len(prata):,} linhas\nGerando agregados ouro...")

    por_genero = Acumulador()
    por_container = Acumulador()
    por_genero_container = Acumulador()
    por_bitrate = Acumulador()
    por_decada = Acumulador()

    total_bytes = 0.0
    total_seg = 0.0

    for linha in prata:
        total_bytes += float(linha["tamanho_bytes"] or 0)
        total_seg += float(linha["duracao_seg"] or 0)
        por_genero.soma(linha["genero"], linha)
        por_container.soma(linha["container"], linha)
        por_genero_container.soma((linha["genero"], linha["container"]), linha)
        por_bitrate.soma(grupo_bitrate(linha), linha)
        por_decada.soma(str(linha["decada"] or "(sem ano)"), linha)

    EXPORTS.mkdir(parents=True, exist_ok=True)
    escrever("ouro_genero.csv", "genero", por_genero.linhas("genero"))
    escrever("ouro_container.csv", "container", por_container.linhas("container"))
    escrever(
        "ouro_genero_container.csv",
        ["genero", "container"],
        por_genero_container.linhas(["genero", "container"]),
    )
    escrever("ouro_bitrate.csv", "faixa_bitrate", por_bitrate.linhas("faixa_bitrate"))
    escrever("ouro_decada.csv", "decada", por_decada.linhas("decada"))

    # Snapshot append-only: a série temporal do seu gráfico de storage
    run_ts = datetime.now().isoformat(timespec="seconds")
    nova = not EVOLUCAO.exists()
    with EVOLUCAO.open("a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if nova:
            w.writerow(["run_ts", "genero", "container", "qtd_faixas", "tamanho_gb"])
        for (g, c), (qtd, bytes_, _seg) in sorted(por_genero_container.dados.items()):
            w.writerow([run_ts, g, c, qtd, round(bytes_ / GB, 2)])
    print("  ✅ ouro_evolucao_storage.csv (snapshot anexado)")

    print("\n=== RESUMO GERAL ===")
    print(f"Faixas: {len(prata):,}")
    print(f"Tamanho: {total_bytes / GB:.2f} GB")
    print(f"Duração total: {duracao_legivel(total_seg)}")
    print("\nPeso por container:")
    for linha in por_container.linhas("container"):
        pct = linha["tamanho_gb"] / (total_bytes / GB) * 100
        print(
            f"  {linha['container']:<6} {linha['qtd_faixas']:>7,} faixas | "
            f"{linha['tamanho_gb']:>7.2f} GB | {pct:>5.1f}% do peso"
        )


if __name__ == "__main__":
    main()