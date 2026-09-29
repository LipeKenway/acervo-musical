"""Testes unitários da classificação de hierarquia (extractor)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ingest.extractor import SEM_TIPO, classificar


def test_album_padrao():
    r = classificar(["Electronic", "Glitch Hop", "Albums", "Only Diamonds"])
    assert r["genero"] == "Electronic"
    assert r["subgenero_pasta"] == "Glitch Hop"
    assert r["tipo_pasta"] == "Albums"
    assert r["pasta_album"] == "Only Diamonds"
    assert r["pasta_pai"] is None
    assert r["pasta_disco"] is None


def test_com_disco():
    r = classificar(["Ambient", "Berlin School", "Albums", "Rubycon", "CD 1"])
    assert r["pasta_album"] == "Rubycon"
    assert r["pasta_disco"] == "CD 1"


def test_mixes_and_lives_sem_tipo_na_pasta():
    r = classificar(["Mixes & Lives", "DJ Mix", "Virtual Self", "Release"])
    assert r["tipo_pasta"] == SEM_TIPO
    assert r["subgenero_pasta"] == "DJ Mix"
    assert r["pasta_pai"] == "Virtual Self"
    assert r["pasta_album"] == "Release"


def test_singular_vira_canonico():
    r = classificar(["Rock", "Punk", "Album", "X"])
    assert r["tipo_pasta"] == "Albums"


def test_trim_de_espacos():
    r = classificar(["Rock", "Punk", "Albums", "  X  "])
    assert r["pasta_album"] == "X"


def test_ep_permanece_singular():
    r = classificar(["Electronic", "House", "EP", "x"])
    assert r["tipo_pasta"] == "EP"