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
  
- subgenero_tag = MOOD (no dialeto do acervo: **Subgenre**); tipo_album_tag =
  MOVEMENTNAME (no dialeto do acervo: **Album Type**); cobertura 100%.


<!-- COLUNAS-AUTO (gerado por agregados_ouro.py; nao editar na mao) -->
**Contrato prata atual: 38 colunas** *(gerado do cabeçalho do acervo_prata.csv em 14/10/2026 19:59)*

`caminho_relativo` · `nome_arquivo` · `genero` · `subgenero_pasta` · `tipo_pasta` · `tipo_final` · `tipo_origem` · `pasta_pai` · `pasta_album` · `pasta_disco` · `titulo` · `artista` · `album` · `album_artista` · `compositor` · `genero_tag` · `subgenero_tag` · `tipo_album_tag` · `data_tag` · `ano` · `decada` · `faixa_n` · `disco_n` · `container` · `formato_tag` · `codec` · `encoder` · `bitrate_kbps` · `modo_bitrate` · `sample_rate_hz` · `bits_por_amostra` · `canais` · `duracao_seg` · `duracao_legivel` · `tamanho_bytes` · `tamanho_mb` · `mtime_iso` · `data_modificacao`
<!-- /COLUNAS-AUTO -->


