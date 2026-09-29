"""Testes das funções derivadas (duração e faixas de bitrate)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ingest.extractor import duracao_legivel
from src.transform.agregados_ouro import grupo_bitrate


def test_duracao_minutos():
    assert duracao_legivel(462) == "7:42"


def test_duracao_com_hora():
    assert duracao_legivel(3725) == "1:02:05"


def test_bitrate_flac():
    assert grupo_bitrate({"container": "FLAC", "bitrate_kbps": "950"}) == "FLAC lossless"


def test_bitrate_mp3_320():
    assert grupo_bitrate({"container": "MP3", "bitrate_kbps": "320"}) == "MP3 257-320+ kbps"


def test_bitrate_mp3_128():
    assert grupo_bitrate({"container": "MP3", "bitrate_kbps": "128"}) == "MP3 ate 128 kbps"


def test_bitrate_m4a():
    assert grupo_bitrate({"container": "M4A", "bitrate_kbps": "220"}) == "M4A/AAC"
