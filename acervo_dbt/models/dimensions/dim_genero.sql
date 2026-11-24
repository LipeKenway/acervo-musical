-- dim_genero.sql
-- Dimensão de gêneros e subgêneros.

with generos as (
    select
        distinct
        coalesce(genero, '(desconhecido)') as nome_genero,
        coalesce(subgenero_pasta, '(sem subgênero)') as nome_subgenero,
        coalesce(subgenero_tag, '(sem tag)') as subgenero_tag
    from {{ ref('stg_prata_faixas') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['nome_genero', 'nome_subgenero', 'subgenero_tag']) }} as genero_id,
    nome_genero,
    nome_subgenero,
    subgenero_tag
from generos