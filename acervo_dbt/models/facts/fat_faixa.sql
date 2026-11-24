-- fat_faixa.sql
-- Tabela de fatos: as faixas com FKs para todas as dimensões.
-- Regra de ouro do join: espelhar EXATAMENTE o coalesce usado na
-- construção da dim, senão linhas com NULL caem fora da estrela.

select
    f.path_hash,
    f.raiz,
    f.caminho_relativo,
    f.nome_arquivo,
    a.artista_id,
    al.album_id,
    g.genero_id,
    t.tipo_id,
    d.decada_id,
    f.titulo,
    f.ano,
    f.container,
    f.formato_tag,
    f.bitrate_kbps,
    f.modo_bitrate,
    f.sample_rate_hz,
    f.bits_por_amostra,
    f.canais,
    f.duracao_seg,
    f.tamanho_bytes,
    f.mtime_iso
from {{ ref('stg_prata_faixas') }} f
left join {{ ref('dim_artista') }} a
    on coalesce(f.artista, '(desconhecido)') = a.nome_artista
    and coalesce(f.album_artista, '(desconhecido)') = a.nome_album_artista
left join {{ ref('dim_album') }} al
    on coalesce(f.album, '(desconhecido)') = al.nome_album
    and coalesce(f.pasta_album, '(desconhecido)') = al.pasta_album
    and coalesce(f.pasta_disco, '(sem disco)') = al.pasta_disco
left join {{ ref('dim_genero') }} g
    on coalesce(f.genero, '(desconhecido)') = g.nome_genero
    and coalesce(f.subgenero_pasta, '(sem subgênero)') = g.nome_subgenero
    and coalesce(f.subgenero_tag, '(sem tag)') = g.subgenero_tag
left join {{ ref('dim_tipo_lancamento') }} t
    on coalesce(f.tipo_album_tag, f.tipo_final, '(desconhecido)') = t.tipo_oficial
    and coalesce(f.tipo_pasta, '(sem pasta)') = t.tipo_pasta
    and f.tipo_origem = t.tipo_origem
left join {{ ref('dim_decada') }} d
    on coalesce(f.decada, 0) = d.decada_valor