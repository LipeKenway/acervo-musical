r"""Scanner v2 da biblioteca musical (multi-raiz, ADR-009).
Classifica cada arquivo de áudio na hierarquia oficial
(gênero / subgênero / tipo / álbum / disco), grava o inventário
bronze em CSV e produz relatório de capas/scans por pasta.
O acervo pode morar em várias raízes (MUSIC_LIBRARY_PATHS no .env);
cada linha bronze ganha a coluna `raiz` (letra do drive), e o
relatório de imagens prefixa as pastas com a raiz (f/..., d/...).
Modo SOMENTE LEITURA na biblioteca.

Uso: python src\ingest\scanner.py
"""

import csv
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.ingest.raizes import raizes_do_acervo  # noqa: E402

EXTENSOES_AUDIO = {
    ".mp3",
    ".flac",
    ".wav",
    ".m4a",
    ".aac",
    ".ogg",
    ".opus",
    ".wma",
    ".aiff",
}
EXTENSOES_IMAGEM = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".tiff",
    ".webp",
}
TIPOS_LANCAMENTO = {
    "albums",
    "album",
    "singles",
    "single",
    "eps",
    "ep",
    "compilations",
    "compilation",
    "collections",
    "collection",
    "mixtapes",
    "mixtape",
    "lives",
    "live",
    "remixes",
    "remix",
}
REGEX_DISCO = re.compile(r"^(cd|disc|disco)\s*\d+$", re.IGNORECASE)
CSV_INVENTARIO = Path("data/processed/inventario_acervo.csv")
CSV_IMAGENS = Path("data/processed/relatorio_imagens.csv")


def classificar_caminho(partes: list[str]) -> dict:
    """Classifica as pastas do caminho relativo na hierarquia oficial."""
    idx_tipo = next(
        (i for i, p in enumerate(partes) if p.lower() in TIPOS_LANCAMENTO),
        None,
    )
    if idx_tipo is None:
        return {
            "genero": partes[0] if partes else "(raiz)",
            "subgenero": "/".join(partes[1:]) or None,
            "tipo_lancamento": "(desconhecido)",
            "pasta_album": None,
            "pasta_disco": None,
        }
    cadeia = partes[:idx_tipo]
    resto = partes[idx_tipo + 1 :]
    pasta_album = None
    pasta_disco = None
    if len(resto) >= 2:
        pasta_album = resto[0]
        pasta_disco = "/".join(resto[1:])
    elif len(resto) == 1:
        if REGEX_DISCO.match(resto[0]):
            pasta_disco = resto[0]
        else:
            pasta_album = resto[0]
    return {
        "genero": cadeia[0] if cadeia else "(raiz)",
        "subgenero": "/".join(cadeia[1:]) or None,
        "tipo_lancamento": partes[idx_tipo],
        "pasta_album": pasta_album,
        "pasta_disco": pasta_disco,
    }


def escanear(pasta_raiz: Path, rotulo: str):
    """Varre UMA raiz: inventário de áudios (+raiz) e imagens prefixadas."""
    linhas = []
    ext_ignoradas: Counter[str] = Counter()
    tipos_desconhecidos: Counter[str] = Counter()
    img_qtd_genero: Counter[str] = Counter()
    img_bytes_genero: Counter[str] = Counter()
    img_qtd_pasta: Counter[str] = Counter()
    img_bytes_pasta: Counter[str] = Counter()
    img_genero_pasta: dict[str, str] = {}
    for pasta_atual, _subpastas, arquivos in os.walk(pasta_raiz):
        for nome in arquivos:
            arquivo = Path(pasta_atual) / nome
            ext = arquivo.suffix.lower()
            if ext not in EXTENSOES_AUDIO:
                ext_ignoradas[ext or "(sem extensao)"] += 1
                if ext in EXTENSOES_IMAGEM:
                    tamanho = arquivo.stat().st_size
                    partes_pasta = list(arquivo.relative_to(pasta_raiz).parent.parts)
                    genero = partes_pasta[0] if partes_pasta else "(raiz)"
                    pasta = f"{rotulo}/" + ("/".join(partes_pasta) or "(raiz)")
                    img_qtd_genero[genero] += 1
                    img_bytes_genero[genero] += tamanho
                    img_qtd_pasta[pasta] += 1
                    img_bytes_pasta[pasta] += tamanho
                    img_genero_pasta[pasta] = genero
                continue
            stats = arquivo.stat()
            partes = list(arquivo.relative_to(pasta_raiz).parent.parts)
            info = classificar_caminho(partes)
            if info["tipo_lancamento"] == "(desconhecido)":
                tipos_desconhecidos["/".join(partes) or "(raiz)"] += 1
            linhas.append(
                {
                    "raiz": rotulo,
                    "caminho_relativo": str(arquivo.relative_to(pasta_raiz)),
                    "genero": info["genero"],
                    "subgenero": info["subgenero"],
                    "tipo_lancamento": info["tipo_lancamento"],
                    "pasta_album": info["pasta_album"],
                    "pasta_disco": info["pasta_disco"],
                    "nome_arquivo": nome,
                    "extensao": ext,
                    "tamanho_bytes": stats.st_size,
                    "mtime_iso": datetime.fromtimestamp(stats.st_mtime).isoformat(timespec="seconds"),
                }
            )
    relatorio_imagens = [
        {
            "pasta": pasta,
            "genero": img_genero_pasta[pasta],
            "qtd_imagens": img_qtd_pasta[pasta],
            "tamanho_bytes": tamanho,
        }
        for pasta, tamanho in sorted(img_bytes_pasta.items(), key=lambda kv: kv[1], reverse=True)
    ]
    return (
        linhas,
        ext_ignoradas,
        tipos_desconhecidos,
        {
            "qtd_genero": img_qtd_genero,
            "bytes_genero": img_bytes_genero,
            "por_pasta": relatorio_imagens,
            "qtd_total": sum(img_qtd_pasta.values()),
            "bytes_total": sum(img_bytes_pasta.values()),
        },
    )


def main() -> None:
    load_dotenv()
    raizes = raizes_do_acervo()
    print(f"Escaneando (somente leitura): {len(raizes)} raiz(es)\n")
    linhas: list[dict] = []
    ext_ignoradas: Counter[str] = Counter()
    tipos_desconhecidos: Counter[str] = Counter()
    img_qtd_genero: Counter[str] = Counter()
    img_bytes_genero: Counter[str] = Counter()
    por_pasta: list[dict] = []
    qtd_img = 0
    bytes_img = 0
    for rotulo, raiz_path in raizes:
        linhas_raiz, ext, tipos, imagens = escanear(raiz_path, rotulo)
        gb_raiz = sum(item["tamanho_bytes"] for item in linhas_raiz) / 1024**3
        print(f"  [{rotulo}] {raiz_path} -> {len(linhas_raiz):,} áudios | {gb_raiz:.2f} GB")
        linhas.extend(linhas_raiz)
        ext_ignoradas.update(ext)
        tipos_desconhecidos.update(tipos)
        img_qtd_genero.update(imagens["qtd_genero"])
        img_bytes_genero.update(imagens["bytes_genero"])
        por_pasta.extend(imagens["por_pasta"])
        qtd_img += imagens["qtd_total"]
        bytes_img += imagens["bytes_total"]
    if not linhas:
        raise SystemExit("Erro: nenhuma faixa encontrada nas raízes do .env")
    por_pasta.sort(key=lambda item: item["tamanho_bytes"], reverse=True)
    imagens = {
        "qtd_genero": img_qtd_genero,
        "bytes_genero": img_bytes_genero,
        "por_pasta": por_pasta,
        "qtd_total": qtd_img,
        "bytes_total": bytes_img,
    }
    print()
    CSV_INVENTARIO.parent.mkdir(parents=True, exist_ok=True)
    with CSV_INVENTARIO.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
        writer.writeheader()
        writer.writerows(linhas)
    with CSV_IMAGENS.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["pasta", "genero", "qtd_imagens", "tamanho_bytes"])
        writer.writeheader()
        writer.writerows(imagens["por_pasta"])
    por_tipo = Counter(linha["tipo_lancamento"] for linha in linhas)
    total_gb = sum(linha["tamanho_bytes"] for linha in linhas) / 1024**3
    print(f"Arquivos de áudio: {len(linhas):,} | {total_gb:.2f} GB")
    print(f"Inventário gravado em: {CSV_INVENTARIO}\n")
    print("Por tipo de lançamento:")
    for tipo, qtd in por_tipo.most_common():
        print(f"  {tipo:<20} {qtd:>8,}")
    gb_img = imagens["bytes_total"] / 1024**3
    print(f"\nCapas/scans: {imagens['qtd_total']:,} imagens | {gb_img:.2f} GB")
    print(f"Relatório por pasta em: {CSV_IMAGENS}")
    print("\nImagens por gênero (top 10 por tamanho):")
    for genero, _ in imagens["bytes_genero"].most_common(10):
        gb = imagens["bytes_genero"][genero] / 1024**3
        print(f"  {genero:<20} {imagens['qtd_genero'][genero]:>8,} imagens {gb:>7.2f} GB")
    print("\nPastas com mais imagens (top 15):")
    for linha in imagens["por_pasta"][:15]:
        gb = linha["tamanho_bytes"] / 1024**3
        print(f"  {gb:>6.2f} GB  {linha['qtd_imagens']:>5,} img  {linha['pasta']}")
    print("\nExtensões ignoradas (top 15):")
    for ext, qtd in ext_ignoradas.most_common(15):
        print(f"  {ext:<20} {qtd:>8,}")
    if tipos_desconhecidos:
        print("\n⚠ Caminhos sem tipo conhecido (top 10):")
        for caminho, qtd in tipos_desconhecidos.most_common(10):
            print(f"  {qtd:>6,}  {caminho}")
    else:
        print("\n✅ Nenhum caminho fora do vocabulário.")


if __name__ == "__main__":
    main()
