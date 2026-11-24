-- stg_prata_faixas.sql
-- View que normaliza a prata_faixas para consumo pelo star schema.
-- Aplica o ADR-001: tipo oficial = tag (quando disponível), senão pasta.

with source as (
    select * from {{ source('raw', 'prata_faixas') }}
),

normalized as (
    select
        path_hash,
        raiz,
        caminho_relativo,
        nome_arquivo,
        genero,
        subgenero_pasta,
        tipo_pasta,
        tipo_final,
        tipo_origem,
        pasta_album,
        pasta_disco,
        titulo,
        artista,
        album,
        album_artista,
        genero_tag,
        subgenero_tag,
        tipo_album_tag,
        ano,
        decada,
        container,
        formato_tag,
        bitrate_kbps,
        modo_bitrate,
        sample_rate_hz,
        bits_por_amostra,
        canais,
        duracao_seg,
        tamanho_bytes,
        mtime_iso
    from source
)

select * from normalized