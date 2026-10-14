r"""Agregados ouro — resumos Excel/BI + docs auto-atualizadas.

Relê a camada prata e produz, em data/exports/:
- ouro_genero.csv / ouro_container.csv / ouro_genero_container.csv
- ouro_bitrate.csv / ouro_decada.csv / ouro_evolucao_storage.csv

E reescreve blocos marcados (entre comentários HTML) em 3 docs:
- README.md                   -> NUMEROS-AUTO (números do acervo)
- docs/stack.md               -> NUMEROS-AUTO (linha de números)
- docs/dicionario_de_dados.md -> COLUNAS-AUTO (contrato prata)

Regra: o gerador só toca ENTRE marcadores; a prosa fora é sagrada.
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
CONFLITOS = EXPORTS / "relatorio_conflitos.csv"
README = Path("README.md")
STACK = Path("docs/stack.md")
DICIONARIO = Path("docs/dicionario_de_dados.md")

MARCA_INI = "<!-- NUMEROS-AUTO (gerado por agregados_ouro.py; nao editar na mao) -->"
MARCA_FIM = "<!-- /NUMEROS-AUTO -->"
MARCA_DIC_INI = "<!-- COLUNAS-AUTO (gerado por agregados_ouro.py; nao editar na mao) -->"
MARCA_DIC_FIM = "<!-- /COLUNAS-AUTO -->"

GB = 1024**3


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

    def __init__(self) -> None:
        self.dados: defaultdict = defaultdict(lambda: [0, 0.0, 0.0])

    def soma(self, chave, linha: dict) -> None:
        acc = self.dados[chave]
        acc[0] += 1
        acc[1] += float(linha["tamanho_bytes"] or 0)
        acc[2] += float(linha["duracao_seg"] or 0)

    def linhas(self, nomes_chave):
        if isinstance(nomes_chave, str):
            nomes_chave = [nomes_chave]
        saida = []
        for chave, (qtd, bytes_, seg) in sorted(self.dados.items(), key=lambda kv: -kv[1][1]):
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


def _reescrever_bloco(caminho: Path, ini: str, fim: str, bloco: list) -> bool:
    """Troca só o trecho entre marcadores; o resto do arquivo fica intocado."""
    texto = caminho.read_text(encoding="utf-8")
    i = texto.find(ini)
    f = texto.find(fim)
    if i == -1 or f == -1:
        return False
    novo = texto[:i] + "\n".join(bloco) + "\n" + texto[f + len(fim) :]
    caminho.write_text(novo, encoding="utf-8")
    return True


def atualizar_docs(
    total: int,
    total_bytes: float,
    total_seg: float,
    por_container: "Acumulador",
    cobertura: dict,
    fila_qtd: int,
    colunas: list,
) -> None:
    """Reescreve os blocos gerados do README, do stack e do dicionário."""
    gb_total = total_bytes / GB
    quando = f"{datetime.now():%d/%m/%Y %H:%M}"

    readme = [
        MARCA_INI,
        f"**{total:,} faixas | {gb_total:.2f} GB | {duracao_legivel(total_seg)} de áudio** *(snapshot de {quando})*",
        "",
    ]
    for linha in por_container.linhas("container"):
        pct = linha["tamanho_gb"] / gb_total * 100
        readme.append(
            f"- {linha['container']}: {linha['qtd_faixas']:,} faixas | "
            f"{linha['tamanho_gb']:.2f} GB | {pct:.1f}% do peso"
        )
    for container, (t, com_sub, com_tipo) in sorted(cobertura.items()):
        readme.append(f"- Cobertura em {container}: Subgenre {com_sub / t:.1%} | Album Type {com_tipo / t:.1%}")
    concordancia = (total - fila_qtd) / total * 100 if total else 0.0
    readme.append(f"- Reconciliação pasta × tag: {concordancia:.1f}% (fila de revisão: {fila_qtd} casos, ADR-002)")
    readme.append(MARCA_FIM)

    stack = [
        MARCA_INI,
        f"Números: {total:,} faixas | {gb_total:.2f} GB | "
        f"{duracao_legivel(total_seg)} de áudio (snapshot de {quando}; "
        "detalhes no README)",
        MARCA_FIM,
    ]

    dicionario = [
        MARCA_DIC_INI,
        f"**Contrato prata atual: {len(colunas)} colunas** *(gerado do cabeçalho do acervo_prata.csv em {quando})*",
        "",
        " · ".join(f"`{c}`" for c in colunas),
        MARCA_DIC_FIM,
    ]

    for caminho, mi, mf, bloco in [
        (README, MARCA_INI, MARCA_FIM, readme),
        (STACK, MARCA_INI, MARCA_FIM, stack),
        (DICIONARIO, MARCA_DIC_INI, MARCA_DIC_FIM, dicionario),
    ]:
        ok = _reescrever_bloco(caminho, mi, mf, bloco)
        print(f"  {'✅' if ok else '⚠'} {caminho}: {'bloco atualizado' if ok else 'sem marcadores, pulado'}")


def main() -> None:
    with PRATA.open(encoding="utf-8-sig") as fh:
        leitor = csv.DictReader(fh)
        colunas = list(leitor.fieldnames or [])
        prata = list(leitor)

    print(f"Prata lida: {len(prata):,} linhas\nGerando agregados ouro...")

    por_genero = Acumulador()
    por_container = Acumulador()
    por_genero_container = Acumulador()
    por_bitrate = Acumulador()
    por_decada = Acumulador()
    cobertura: dict = {}

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
        cov = cobertura.setdefault(linha["container"], [0, 0, 0])
        cov[0] += 1
        cov[1] += 1 if (linha["subgenero_tag"] or "").strip() else 0
        cov[2] += 1 if (linha["tipo_album_tag"] or "").strip() else 0

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

    run_ts = datetime.now().isoformat(timespec="seconds")
    nova = not EVOLUCAO.exists()
    with EVOLUCAO.open("a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if nova:
            w.writerow(["run_ts", "genero", "container", "qtd_faixas", "tamanho_gb"])
        for (g, c), (qtd, bytes_, _seg) in sorted(por_genero_container.dados.items()):
            w.writerow([run_ts, g, c, qtd, round(bytes_ / GB, 2)])
    print("  ✅ ouro_evolucao_storage.csv (snapshot anexado)")

    fila_qtd = 0
    if CONFLITOS.exists():
        with CONFLITOS.open(encoding="utf-8-sig") as fh:
            fila_qtd = sum(int(r["qtd"]) for r in csv.DictReader(fh))

    atualizar_docs(len(prata), total_bytes, total_seg, por_container, cobertura, fila_qtd, colunas)

    print("\n=== RESUMO GERAL ===")
    print(f"Faixas: {len(prata):,}")
    print(f"Tamanho: {total_bytes / GB:.2f} GB")
    print(f"Duração total: {duracao_legivel(total_seg)}")


if __name__ == "__main__":
    main()
