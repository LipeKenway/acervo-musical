-- dim_decada.sql
-- Dimensão de décadas.

with decadas as (
    select
        distinct
        coalesce(decada, 0) as decada_valor
    from {{ ref('stg_prata_faixas') }}
)

select
    decada_valor as decada_id,
    decada_valor,
    case
        when decada_valor = 0 then '(sem ano)'
        else cast(decada_valor as varchar)
    end as decada_label
from decadas