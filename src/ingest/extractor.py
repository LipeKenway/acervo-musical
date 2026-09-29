"""
Extrator de metadados (camada prata) v1.2.

Lê o inventário bronze, abre cada áudio com mutagen e grava:
- data/processed/acervo_prata.csv        (contrato prata, legível p/ Excel)
- data/processed/quarentena.csv          (falhas com motivo)
- data/exports/relatorio_conflitos.csv   (anomalias pós-tradução)
- data/exports/historico_armazenamento.csv (snapshot p/ gráficos)

Taxonomia (docs/hierarquia.md):
- Demais gêneros: genero / subgenero / tipo_na_pasta / artista / release
- Mixes & Lives: genero / subgenero (DJ Mix, Live Set, Studio Mix) /
  artista / release — o tipo de lançamento vive SÓ na tag MOVEMENTNAME.

Modo SOMENTE LEITURA na biblioteca.

"""

import csv
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import mutagen
from dotenv import load_dotenv

BRONZE = Path("data/processed/inventario_acervo.csv")
PRATA = Path("data/processed/acervo_prata.csv")
QUARENTENA = Path("data/processed/quarentena.csv")
CONFLITOS = Path("data/exports/relatorio_conflitos.csv")
HISTORICO = Path("data/exports/historico_armazenamento.csv")

SEM_TIPO = "(sem tipo na pasta)"

TIPOS_LANCAMENTO = {
    "albums", "album", "singles", "single", "eps", "ep",
    "compilations", "compilation", "collections", "collection",
    "mixtapes", "mixtape", "lives", "live", "remixes", "remix",
}

TIPO_CANONICO = {
    "album": "Albums", "albums": "Albums",
    "ep": "EP", "eps": "EP",
    "single": "Singles", "singles": "Singles",
    "compilation": "Compilations", "compilations": "Compilations",
    "collection": "Collections", "collections": "Collections",
    "mixtape": "Mixtapes", "mixtapes": "Mixtapes",
    "live": "Lives", "lives": "Lives",
    "remix": "Remixes", "remixes": "Remixes",
}

REGEX_DISCO = re.compile(r"^(cd|disc|disco)\s*\d+$", re.IGNORECASE)

# Dialeto pasta -> dialeto tag (gêneros com tipo na pasta)
MAPA_PASTA_TAG = {
    "Albums": "Album",
    "EP": "EP",
    "Singles": "Single",
    "Compilations": "Compilation",
    "Collections": "Collection",
    "Mixtapes": "Mixtape",
    "Lives": "Live Album",
}

# Mixes & Lives: subgênero (pasta/MOOD) -> tipo esperado na tag
MAPA_SUBGENERO_TAG = {
    "dj mix": "DJ Set",
    "live set": "Live Album",
    "studio mix": "Continuous Mix",
}

CHAVES_TAGS = {
    "titulo": ("©nam", "TIT2", "TITLE", "Title"),
    "artista": ("©ART", "TPE1", "ARTIST", "Author"),
    "album": ("©alb", "TALB", "ALBUM", "WM/AlbumTitle"),
    "album_artista": ("aART", "TPE2", "ALBUMARTIST"),
    "compositor": ("©wrt", "TCOM", "COMPOSER"),
    "genero_tag": ("©gen", "TCON", "GENRE", "WM/Genre"),
    "subgenero_tag": ("©moo", "----:com.apple.iTunes:MOOD", "TMOO", "MOOD", "WM/Mood"),
    "tipo_album_tag": ("©mvn", "----:com.apple.iTunes:MOVEMENTNAME", "MVNM", "MOVEMENTNAME", "WM/MovementName"),
    "data_tag": ("©day", "TDRC", "TYER", "DATE", "WM/Year"),
    "faixa": ("trkn", "TRCK", "TRACKNUMBER", "WM/TrackNumber"),
    "disco": ("disk", "TPOS", "DISCNUMBER"),
    "encoder": ("©too", "TENC", "ENCODEDBY", "ENCODED_BY"),
}

MAPA_CONTAINER = {
    "MP3": "MP3", "MP4": "M4A", "FLAC": "FLAC", "OggVorbis": "OGG",
    "WMA": "WMA", "Wave": "WAV", "AAC": "AAC",
}

MAPA_FORMATO_TAG = {"MP4Tags": "MP4", "VComment": "Vorbis", "ASF": "ASF"}

CAMPOS_PRATA = [
    "caminho_relativo", "nome_arquivo",
    "genero", "subgenero_pasta", "tipo_pasta", "tipo_final", "tipo_origem",
    "pasta_pai", "pasta_album", "pasta_disco",
    "titulo", "artista", "album", "album_artista", "compositor",
    "genero_tag", "subgenero_tag", "tipo_album_tag",
    "data_tag", "ano", "decada", "faixa_n", "disco_n",
    "container", "formato_tag", "codec", "encoder",
    "bitrate_kbps", "modo_bitrate",
    "sample_rate_hz", "bits_por_amostra", "canais",
    "duracao_seg", "duracao_legivel", "tamanho_bytes", "tamanho_mb",
    "mtime_iso", "data_modificacao",
]


def _texto(valor):
    if hasattr(valor, "text"):
        valor = valor.text
    if isinstance(valor, (list, tuple)):
        if not valor:
            return None
        valor = valor[0]
    if isinstance(valor, tuple):
        valor = valor[0]
    if isinstance(valor, bytes):
        valor = valor.decode("utf-8", "replace")
    s = str(valor).strip()
    return s or None


def pegar_tag(tags, campo: str):
    if tags is None:
        return None
    for chave in CHAVES_TAGS[campo]:
        try:
            valor = tags.get(chave)
        except Exception:
            valor = None
        if valor:
            t = _texto(valor)
            if t:
                return t
    return None


def pegar_numero(tags, campo: str):
    t = pegar_tag(tags, campo)
    if not t:
        return None
    t = t.split("/")[0].strip()
    return int(t) if t.isdigit() else None


def _pastas_finais(resto: list[str]):
    """Deriva pasta_pai / pasta_album / pasta_disco do trecho final."""
    pasta_pai = pasta_album = pasta_disco = None
    if resto:
        if REGEX_DISCO.match(resto[-1]):
            pasta_disco = resto[-1]
            meio = resto[:-1]
            if meio:
                pasta_album = meio[-1]
                pasta_pai = meio[0] if len(meio) > 1 else None
        else:
            pasta_album = resto[-1]
            pasta_pai = resto[0] if len(resto) > 1 else None
    return pasta_pai, pasta_album, pasta_disco


def classificar(partes: list[str]) -> dict:
    """Classifica o caminho relativo na hierarquia oficial."""
    partes = [p.strip() for p in partes]
    idx = next(
        (i for i, p in enumerate(partes) if p.lower() in TIPOS_LANCAMENTO),
        None,
    )

    if idx is None:
        # Famílias sem tipo na pasta (ex.: Mixes & Lives):
        # L1 = gênero, L2 = subgênero, restante = artista/release.
        pai, album, disco = _pastas_finais(partes[2:])
        return {
            "genero": partes[0] if partes else "(raiz)",
            "subgenero_pasta": partes[1] if len(partes) > 1 else None,
            "tipo_pasta": SEM_TIPO,
            "pasta_pai": pai,
            "pasta_album": album,
            "pasta_disco": disco,
        }

    cadeia = partes[:idx]
    pai, album, disco = _pastas_finais(partes[idx + 1:])
    return {
        "genero": cadeia[0] if cadeia else "(raiz)",
        "subgenero_pasta": "/".join(cadeia[1:]) or None,
        "tipo_pasta": TIPO_CANONICO[partes[idx].lower()],
        "pasta_pai": pai,
        "pasta_album": album,
        "pasta_disco": disco,
    }


def duracao_legivel(seg) -> str:
    seg = int(seg or 0)
    h, resto = divmod(seg, 3600)
    m, s = divmod(resto, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def formato_tag(arq):
    tags = arq.tags
    if tags is None:
        return None
    versao = getattr(tags, "version", None)
    if versao:
        return f"ID3 v{versao[0]}.{versao[1]}"
    return MAPA_FORMATO_TAG.get(type(tags).__name__, type(tags).__name__)


def dados_tecnicos(arq) -> dict:
    info = arq.info
    container = MAPA_CONTAINER.get(type(arq).__name__, type(arq).__name__)

    encoder = pegar_tag(arq.tags, "encoder") if arq.tags else None
    if not encoder:
        encoder = getattr(info, "encoder_info", None)
    if not encoder:
        vendor = getattr(arq.tags, "vendor", None)
        if vendor:
            encoder = _texto(vendor)

    modo = getattr(info, "bitrate_mode", None)
    if not modo and encoder:
        up = encoder.upper()
        modo = "VBR" if "VBR" in up else ("CBR" if "CBR" in up else None)

    return {
        "container": container,
        "codec": getattr(info, "codec", None)
        or getattr(info, "codec_description", None)
        or container,
        "encoder": encoder,
        "bitrate_kbps": round(info.bitrate / 1000) if getattr(info, "bitrate", None) else None,
        "modo_bitrate": modo,
        "sample_rate_hz": getattr(info, "sample_rate", None),
        "bits_por_amostra": getattr(info, "bits_per_sample", None),
        "canais": getattr(info, "channels", None),
        "duracao_seg": round(info.length, 2) if getattr(info, "length", None) else None,
    }


def main() -> None:
    load_dotenv()
    raiz = Path(os.getenv("MUSIC_LIBRARY_PATH", ""))
    if not raiz.is_dir():
        raise SystemExit("Erro: MUSIC_LIBRARY_PATH inválido no .env")

    with BRONZE.open(encoding="utf-8") as fh:
        bronze = list(csv.DictReader(fh))

    eh_amostra = "--amostra" in sys.argv
    if eh_amostra:
        n = int(sys.argv[sys.argv.index("--amostra") + 1])
        bronze = bronze[:n]
        print(f"=== MODO AMOSTRA: somente {n} linhas ===\n")

    total = len(bronze)
    print(f"Extraindo metadados de {total:,} arquivos (somente leitura)...\n")

    linhas_prata = []
    quarentena = []
    conflitos = Counter()
    cobertura = {}
    historico = Counter()
    origens = Counter()
    sem_tipo_generos = Counter()
    inicio = time.time()

    for i, row in enumerate(bronze, 1):
        caminho = raiz / row["caminho_relativo"]
        try:
            arq = mutagen.File(caminho)
            if arq is None:
                raise ValueError("mutagen nao reconheceu o formato")
            tags = arq.tags
            tec = dados_tecnicos(arq)
            info_pasta = classificar(list(Path(row["caminho_relativo"]).parent.parts))

            data_tag = pegar_tag(tags, "data_tag")
            ano = int(data_tag[:4]) if data_tag and data_tag[:4].isdigit() else None
            tipo_tag = pegar_tag(tags, "tipo_album_tag")
            sub_tag = pegar_tag(tags, "subgenero_tag")
            tamanho_bytes = int(row["tamanho_bytes"])

            if info_pasta["tipo_pasta"] != SEM_TIPO:
                tipo_final = info_pasta["tipo_pasta"]
                tipo_origem = "pasta"
                esperado = MAPA_PASTA_TAG.get(tipo_final)
            else:
                tipo_final = tipo_tag
                tipo_origem = "tag"
                esperado = MAPA_SUBGENERO_TAG.get(
                    (info_pasta["subgenero_pasta"] or "").lower()
                )
                sem_tipo_generos[info_pasta["genero"]] += 1

            origens[tipo_origem] += 1

            cov = cobertura.setdefault(tec["container"], [0, 0, 0])
            cov[0] += 1
            cov[1] += 1 if sub_tag else 0
            cov[2] += 1 if tipo_tag else 0

            if esperado and tipo_tag and tipo_tag.lower() != esperado.lower():
                conflitos[(info_pasta["genero"], info_pasta["subgenero_pasta"] or info_pasta["tipo_pasta"], tipo_tag)] += 1

            historico[(info_pasta["genero"], tec["container"])] += 1

            linhas_prata.append({
                "caminho_relativo": row["caminho_relativo"],
                "nome_arquivo": row.get("nome_arquivo") or caminho.name,
                **info_pasta,
                "tipo_final": tipo_final,
                "tipo_origem": tipo_origem,
                "titulo": pegar_tag(tags, "titulo"),
                "artista": pegar_tag(tags, "artista"),
                "album": pegar_tag(tags, "album"),
                "album_artista": pegar_tag(tags, "album_artista"),
                "compositor": pegar_tag(tags, "compositor"),
                "genero_tag": pegar_tag(tags, "genero_tag"),
                "subgenero_tag": sub_tag,
                "tipo_album_tag": tipo_tag,
                "data_tag": data_tag,
                "ano": ano,
                "decada": (ano // 10) * 10 if ano else None,
                "faixa_n": pegar_numero(tags, "faixa"),
                "disco_n": pegar_numero(tags, "disco"),
                "formato_tag": formato_tag(arq),
                **tec,
                "duracao_legivel": duracao_legivel(tec["duracao_seg"]),
                "tamanho_bytes": tamanho_bytes,
                "tamanho_mb": round(tamanho_bytes / 1024 ** 2, 1),
                "mtime_iso": row["mtime_iso"],
                "data_modificacao": row["mtime_iso"][:10],
            })
        except Exception as exc:
            quarentena.append({
                "caminho_relativo": row["caminho_relativo"],
                "motivo": f"{type(exc).__name__}: {exc}",
            })

        if i % 5000 == 0:
            print(f"  {i:>7,}/{total:,}  ({time.time() - inicio:.0f}s)")

    PRATA.parent.mkdir(parents=True, exist_ok=True)
    with PRATA.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS_PRATA)
        w.writeheader()
        w.writerows(linhas_prata)

    with QUARENTENA.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["caminho_relativo", "motivo"])
        w.writeheader()
        w.writerows(quarentena)

    CONFLITOS.parent.mkdir(parents=True, exist_ok=True)
    with CONFLITOS.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["genero", "subgenero_ou_tipo_pasta", "tipo_tag", "qtd"])
        for (g, sp, tt), qtd in conflitos.most_common():
            w.writerow([g, sp, tt, qtd])

    if not eh_amostra:
        run_ts = datetime.now().isoformat(timespec="seconds")
        nova = not HISTORICO.exists()
        with HISTORICO.open("a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            if nova:
                w.writerow(["run_ts", "genero", "container", "qtd_arquivos"])
            for (g, c), qtd in sorted(historico.items()):
                w.writerow([run_ts, g, c, qtd])

    print(f"\n✅ Prata: {len(linhas_prata):,} linhas em {PRATA}")
    print(f"⚠ Quarentena: {len(quarentena):,} arquivos em {QUARENTENA}")

    print(f"\nOrigem do tipo final: pasta={origens['pasta']:,} | tag={origens['tag']:,}")
    if sem_tipo_generos:
        print("Gêneros sem tipo na pasta (tipo vem da tag):")
        for g, qtd in sem_tipo_generos.most_common():
            print(f"  {g:<20} {qtd:>8,}")

    print("\nCobertura de tags por container (subgênero / tipo álbum):")
    for container, (t, com_mood, com_mov) in sorted(cobertura.items()):
        print(
            f"  {container:<6} {t:>7,} arquivos | "
            f"MOOD {com_mood / t:>6.1%} | MOVEMENT {com_mov / t:>6.1%}"
        )

    if conflitos:
        print("\nAnomalias pós-tradução (fila de revisão, top 10):")
        for (g, sp, tt), qtd in conflitos.most_common(10):
            print(f"  {qtd:>6,}  {g} | {sp} | tag={tt}")

    print(f"\nTempo total: {time.time() - inicio:.0f}s")


if __name__ == "__main__":
    main()