"""Raízes do acervo (multi-HD) — configuração vinda do .env (ADR-009).

O acervo pode morar em mais de um caminho (HD externo + partição
interna, por exemplo). O .env declara todos em MUSIC_LIBRARY_PATHS,
separados por ';'. Cada raiz ganha um rótulo estável: a letra do
drive em minúscula (f, d, ...), que vira a coluna `raiz` da bronze.
"""

import os
from pathlib import Path


def raizes_do_acervo() -> list[tuple[str, Path]]:
    """Retorna [(rotulo, caminho)] na ordem declarada no .env."""
    bruto = os.getenv("MUSIC_LIBRARY_PATHS", "").strip()
    if not bruto:  # fallback: .env antigo com uma raiz só
        bruto = os.getenv("MUSIC_LIBRARY_PATH", "").strip()
    if not bruto:
        raise SystemExit("Erro: MUSIC_LIBRARY_PATHS vazio no .env")
    raizes: list[tuple[str, Path]] = []
    rotulos: set[str] = set()
    for trecho in bruto.split(";"):
        trecho = trecho.strip()
        if not trecho:
            continue
        caminho = Path(trecho)
        if not caminho.is_dir():
            raise SystemExit(f"Erro: raiz inválida no .env: {caminho}")
        rotulo = caminho.drive.rstrip(":").lower() or caminho.name.lower()
        while rotulo in rotulos:
            rotulo += str(len(raizes))
        rotulos.add(rotulo)
        raizes.append((rotulo, caminho))
    if not raizes:
        raise SystemExit("Erro: MUSIC_LIBRARY_PATHS sem caminhos válidos")
    return raizes
