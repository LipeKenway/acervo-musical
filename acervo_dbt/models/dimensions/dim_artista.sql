-- dim_artista.sql
-- Dimensão de artistas (surrogate key + natural key).

with artistas as (
    select
        distinct
        coalesce(artista, '(desconhecido)') as nome_artista,
        coalesce(album_artista, '(desconhecido)') as nome_album_artista
    from {{ ref('stg_prata_faixas') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['nome_artista', 'nome_album_artista']) }} as artista_id,
    nome_artista,
    nome_album_artista
from artistas