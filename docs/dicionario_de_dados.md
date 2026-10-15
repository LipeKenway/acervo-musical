# Dicionário de Dados — camada prata

Equivalência entre colunas do Mp3tag (ferramenta de tagging do acervo)
e o contrato prata (`acervo_prata.csv`). Bronze mantém valores exatos
(bytes, mtime ISO); prata adiciona derivados legíveis.

## Notas técnicas

- **`modo_bitrate`**: nativo no MP3 (`bitrate_mode`); em M4A/FLAC
  derivado do encoder (ex.: "VBR mode 5").
- **`formato_tag`**: ID3 v2.3 não suporta TMOO/MVNM (só v2.4) —
  `null`s esperados em MP3 antigos são **diagnóstico, não bug**.
- **`bitrate_kbps` no FLAC**: o mutagen reporta ~793 kbps (realista
  para 16-bit/44,1 kHz lossless); lossless não é "sem bitrate".

## Ponte pasta ↔ tag (ADR-001)

- **`tipo_final`** — tipo de lançamento oficial da linha: vem da pasta
  quando ela tem tipo; vem da tag nas famílias de dialeto livre
  (Soundtrack, Mixes & Lives).
- **`tipo_origem`** — de onde o `tipo_final` veio: `"pasta"` ou `"tag"`.

## Ponte tag ↔ dialeto do acervo

- **`subgenero_tag`** = MOOD (no dialeto do acervo: **Subgenre**);
  **`tipo_album_tag`** = MOVEMENTNAME (no dialeto do acervo: **Album Type**);
  cobertura 100% nos três containers.

Vitrine (`README.md`) e dicionário falam a língua do acervo
(Subgenre/Album Type); código e chave de tag continuam técnicos.

<!-- COLUNAS-AUTO (gerado por agregados_ouro.py; nao editar na mao) -->
**(bloco gerado: contrato prata atual)**
<!-- /COLUNAS-AUTO -->