# Acervo Musical — Engenharia de Dados

Pipeline de dados sobre uma biblioteca musical pessoal:
**110.731 faixas | 912,89 GB | 311,3 dias de áudio**.

## O que é
Projeto de engenharia de dados que trata uma coleção pessoal de
110k+ arquivos de áudio (MP3/M4A/FLAC) como um produto de dados:
da varredura do disco até resumos prontos para BI, com qualidade
de dados, documentação viva e decisões registradas como ADRs.

## Arquitetura atual (medallion)

    F:\Acervo (Musicas) --scan-->  bronze  (inventario_acervo.csv)
    bronze --mutagen-->           prata   (acervo_prata.csv + quarentena)
    prata --agregados-->          ouro    (CSVs p/ Excel/BI + evolução)

- `src/ingest/scanner.py` — foto do disco (somente leitura), capas/scans
- `src/ingest/extractor.py` — tags (ID3/MP4/Vorbis), `--amostra`, `--completar`, quarentena
- `src/ingest/reconciliador.py` — taxonomia pasta × tag (99,6% de concordância)
- `src/transform/agregados_ouro.py` — resumos e snapshot de storage

## Números
- 110.731 faixas | 912,89 GB | 311,3 dias de áudio
- MP3 69,6% do peso (quase todo 257–320 kbps) | M4A 29,8% | FLAC 0,6%
- Cobertura de tags MOOD/MOVEMENT: 100% nos três containers
- Reconciliação pasta × tag: 99,6% (fila de revisão documentada, ADR-002)

## Docs vivas
`docs/hierarquia.md` · `docs/dicionario_de_dados.md` · `docs/glossario.md` ·
`docs/stack.md` · ADRs dentro da hierarquia

## Roadmap
FASE 1 testes/CI → FASE 2 Parquet/MinIO/DuckDB → FASE 3 Postgres/dbt →
FASE 4 Airflow/observabilidade → FASE 5 AWS/Terraform

## Como rodar
    python -m venv .venv
    pip install -r requirements.txt
    copy .env.example .env   (preencha MUSIC_LIBRARY_PATH)
    python src\ingest\scanner.py
    python src\ingest\extractor.py
    python src\transform\agregados_ouro.py

## Segurança
Segredos apenas em `.env` (fora do Git); biblioteca montada como
somente leitura; nenhum arquivo de áudio sobe para o repositório.