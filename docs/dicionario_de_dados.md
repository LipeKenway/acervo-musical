# Dicionário de Dados — camada prata

Equivalência entre colunas do Mp3tag (ferramenta de tagging do acervo)
e o contrato prata (acervo_prata.csv). Bronze mantém valores exatos
(bytes, mtime ISO); prata adiciona derivados legíveis.

Notas:
- modo_bitrate: nativo no MP3 (bitrate_mode); em M4A/FLAC derivado
  do encoder (ex.: "VBR mode 5").
- formato_tag: ID3 v2.3 não suporta TMOO/MVNM (só v2.4) — nulls
  esperados em MP3 antigos são diagnóstico, não bug.
- subgenero_tag = MOOD; tipo_album_tag = MOVEMENTNAME (padrão Mp3tag).

- **tipo_final** — tipo de lançamento oficial da linha: vem da pasta
  quando ela tem tipo; vem da tag nas famílias de dialeto livre.
- **tipo_origem** — de onde o tipo_final veio: "pasta" ou "tag".