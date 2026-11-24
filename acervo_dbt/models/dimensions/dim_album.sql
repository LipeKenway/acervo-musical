-- dim_album.sql
-- Dimensão de álbuns.

with albuns as (
    select
        distinct
        coalesce(album, '(desconhecido)') as nome_album,
        coalesce(pasta_album, '(desconhecido)') as pasta_album,
        coalesce(pasta_disco, '(sem disco)') as pasta_disco
    from {{ ref('stg_prata_faixas') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['nome_album', 'pasta_album', 'pasta_disco']) }} as album_id,
    nome_album,
    pasta_album,
    pasta_disco
from albuns