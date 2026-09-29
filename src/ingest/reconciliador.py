r"""Reconciliador de taxonomia (pasta x tag).

Relê a camada prata (segundos) e regenera o relatório de anomalias
com as CONVENÇÕES calibradas pelo dono do acervo:

- Soundtrack e Mixes & Lives: dialeto livre (a tag é a identidade;
  a pasta não é checada).
- Demais gêneros: pasta e tag devem concordar após tradução;
  o que sobrar = fila de revisão humana, COM caminho de exemplo.

Uso: python src/ingest/reconciliador.py
"""

import csv
from collections import defaultdict
from pathlib import Path

PRATA = Path("data/processed/acervo_prata.csv")
CONFLITOS = Path("data/exports/relatorio_conflitos.csv")

# Gêneros de dialeto livre: a tag manda, a pasta não é checada.
GENEROS_LIVRES = {"Soundtrack", "Mixes & Lives"}

# Dialeto pasta -> dialeto tag (somente gêneros com checagem)
MAPA_PASTA_TAG = {
    "Albums": "Album",
    "EP": "EP",
    "Singles": "Single",
    "Compilations": "Compilation",
    "Collections": "Collection",
    "Mixtapes": "Mixtape",
    "Lives": "Live Album",
}


def main() -> None:
    with PRATA.open(encoding="utf-8-sig") as fh:
        linhas = list(csv.DictReader(fh))

    total = len(linhas)
    ok = 0
    livres = 0
    fila = defaultdict(lambda: [0, ""])

    for linha in linhas:
        genero = linha["genero"]
        real = (linha["tipo_album_tag"] or "").strip()

        if genero in GENEROS_LIVRES:
            livres += 1  # tag é a identidade; sem checagem de pasta
            continue

        esperada = MAPA_PASTA_TAG.get(linha["tipo_pasta"])
        if not esperada or not real:
            ok += 1
            continue
        if real.lower() == esperada.lower():
            ok += 1
            continue

        chave = (genero, linha["tipo_pasta"], real)
        fila[chave][0] += 1
        if not fila[chave][1]:
            fila[chave][1] = linha["caminho_relativo"]

    CONFLITOS.parent.mkdir(parents=True, exist_ok=True)
    with CONFLITOS.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["genero", "tipo_pasta", "tipo_tag", "qtd", "exemplo"])
        for (g, tp, tt), (qtd, exemplo) in sorted(
            fila.items(), key=lambda kv: -kv[1][0]
        ):
            w.writerow([g, tp, tt, qtd, exemplo])

    print(f"Prata: {total:,} linhas")
    print(f"✅ OK (pasta e tag concordam): {ok:,}")
    print(f"🎨 Dialeto livre (Soundtrack + Mixes & Lives): {livres:,}")
    print(f"🎯 Fila de revisão humana: {sum(v[0] for v in fila.values()):,} "
          f"({len(fila)} combinações)")
    print(f"\nRelatório com exemplos em: {CONFLITOS}\n")

    print("Fila de revisão (top 15):")
    for (g, tp, tt), (qtd, exemplo) in sorted(
        fila.items(), key=lambda kv: -kv[1][0]
    )[:15]:
        print(f"  {qtd:>6,}  {g} | pasta={tp} | tag={tt}")
        print(f"          ex.: {exemplo[:95]}")


if __name__ == "__main__":
    main()
