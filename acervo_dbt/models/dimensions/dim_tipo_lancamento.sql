-- dim_tipo_lancamento.sql
-- Dimensão de tipos de lançamento (ADR-001: tipo oficial = tag).

with tipos as (
    select
        distinct
        coalesce(tipo_album_tag, tipo_final, '(desconhecido)') as tipo_oficial,
        coalesce(tipo_pasta, '(sem pasta)') as tipo_pasta,
        tipo_origem
    from {{ ref('stg_prata_faixas') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['tipo_oficial', 'tipo_pasta', 'tipo_origem']) }} as tipo_id,
    tipo_oficial,
    tipo_pasta,
    tipo_origem
from tipos