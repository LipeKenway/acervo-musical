# Stack do Projeto Acervo Musical

Inventário de linguagens, ferramentas e práticas do projeto.
Status: ✅ em uso | ⏳ roadmap (fase) | 🧊 legado (referência) | 🚫 fora de escopo (justificado)

Números do acervo: 110k+ faixas | 11.201 álbuns | 912,61 GB | 311 dias de áudio

## 1. Linguagens
| Linguagem | Uso no projeto | Status |
|---|---|---|
| Python 3 | Scanner, extrator, DAGs, testes, scripts de carga | ✅ |
| SQL | Análise (DuckDB), modelagem gold (dbt/Postgres) | ⏳ F2/F3 |
| PowerShell | Automação local no Windows (setup, ops) | ✅ |
| YAML | docker-compose, GitHub Actions, projeto dbt | ⏳ F1/F2 |
| Markdown | README, docs, ADRs, dicionário de dados | ✅ |

## 2. Bibliotecas Python
| Biblioteca | Uso | Status |
|---|---|---|
| mutagen | Metadados de áudio: ID3v2.3/v2.4 (MP3), MP4/iTunes (M4A/AAC), Vorbis (FLAC), ASF (WMA) | ✅ |
| python-dotenv | Segredos via `.env` (fora do Git) | ✅ |
| pyarrow | Leitura/escrita Parquet | ⏳ F2 |
| boto3 | Integração S3 | ⏳ F5 |
| stdlib (os, csv, pathlib, re, collections, datetime, time) | Scanner, inventários, relatórios | ✅ |

## 3. Armazenamento e formatos
| Ferramenta | Uso | Status |
|---|---|---|
| CSV (utf-8-sig) | Bronze/prata e entregáveis legíveis (Excel) | ✅ |
| Parquet | Formato colunar do lake | ⏳ F2 |
| MinIO | S3 local (lake raw/curated/gold) | ⏳ F2 |
| Amazon S3 | Lake real em nuvem (só metadados) | ⏳ F5 |
| Postgres | Warehouse com star schema | ⏳ F3 |
| DuckDB | Análise/benchmark sobre Parquet, SQL avançado | ⏳ F2 |
| MariaDB + SQL Server | Prova multi-banco do v1 | 🧊 |

## 4. Orquestração, infra e CI/CD
| Ferramenta | Uso | Status |
|---|---|---|
| Docker / Docker Compose | Serviços isolados (Airflow, bancos, MinIO, Metabase) | ⏳ (instalado) |
| Apache Airflow (TaskFlow API) | Orquestração com retries, backoff e histórico | ⏳ F4 |
| GitHub Actions | CI: pytest + ruff + mypy + gitleaks a cada PR | ⏳ F1 |
| pre-commit | Bloqueio local antes do commit (ruff, gitleaks) | ⏳ F1 |
| Terraform | IaC: bucket S3, lifecycle, block-public, SSE | ⏳ F5 |
| Dependabot | Monitoramento de dependências | ⏳ F1 |

## 5. Qualidade, testes e segurança
| Ferramenta/Prática | Uso | Status |
|---|---|---|
| pytest | Testes unitários das funções de limpeza | ⏳ F1 |
| ruff + mypy | Lint, regras de segurança e type checking | ⏳ F1 |
| gitleaks | Bloqueio de segredos em commits | ⏳ F1 |
| Type hints + docstrings | Contrato de código legível | ⏳ F1 (parcial ✅) |
| Quarentena de registros | Registro ruim não entra no banco; cai com motivo | ✅ |
| Reconciliação de contagens | Bronze vs legado vs relatórios (caso dos 80 arquivos) | ✅ |
| Validação cruzada pasta × tag | Dialetos de taxonomia (MOOD/MOVEMENTNAME) | ✅ |
| Dicionário de dados | Mp3tag ↔ camada prata documentado | ✅ |
| dbt tests (unique, not_null, accepted_values) | Qualidade na camada gold | ⏳ F3 |
| Menor privilégio / service accounts | app DML, bi só SELECT | ⏳ F3 |
| Fernet (Airflow) | Criptografia de Connections | ⏳ F4 |
| Mounts `:ro`, bind 127.0.0.1, chmod 750 | Endurecimento Docker/host | ⏳ F0/F2 |
| Pseudonimização (SHA-256 de caminhos) | Privacidade no warehouse | ⏳ F3 |

## 6. BI e observabilidade
| Ferramenta | Uso | Status |
|---|---|---|
| Metabase | Dashboards, anomalias, Wrapped pessoal | ⏳ F3/F4 |
| Tabela `metricas_execucao` | Sinais vitais de cada run | ⏳ F4 |
| Bot Telegram (webhook) | Alerta de falha da DAG | ⏳ F4 |
| `audit_log` | Trilha de auditoria das cargas | ⏳ F4 |
| `historico_armazenamento.csv` | Snapshot de uso de storage p/ gráficos | ✅ |
| pg_dump + restore testado (3-2-1, RPO/RTO) | Backup que existe de verdade | ⏳ F4 |

## 7. Conceitos e práticas (o coração do currículo)
ETL/ELT • CDC incremental (watermark por mtime) • Arquitetura medallion
(bronze/prata/ouro) • Lakehouse/Parquet particionado • Star schema (Kimball)
• Idempotência e upsert/merge • Particionamento por década • Data quality
(quarentena, reconciliação, cobertura de tags) • Governança (dicionário de
dados, classificação) • CI/CD • IaC • Observabilidade (métricas, alertas,
audit trail) • Segurança (segredos, menor privilégio, criptografia) •
Backup/recuperação (3-2-1, RPO/RTO) • ADRs • War stories documentadas

## 8. Fora de escopo — e por quê (maturidade também é skill)
| Item | Motivo |
|---|---|
| Kubernetes, Spark, Databricks | Overengineering para o volume atual |
| Kafka, Redis | Pertencem ao Projeto 3 |
| Great Expectations / Soda | Testes do dbt resolvem |
| DVC | Amostra reproduzível + ADR bastam |
| MWAA / Composer | Custo desnecessário |
| Power BI | Metabase cobre |
| Multi-cloud | Foco e profundidade > coleção de siglas |
| Subir 912 GB de áudio | Só metadados vão pra nuvem (regra de ouro) |

## 9. Tradução para currículo e LinkedIn

Headline sugerida:
"Engenharia de Dados | Pipeline batch + CDC sobre 110k arquivos |
Python • Airflow • dbt • AWS"

Bullets estilo experiência (só usar o que já estiver concluído):
- Pipeline ETL de 110k+ arquivos de áudio (912 GB) com processamento
  incremental (CDC por mtime): runtime de ~3h reduzido para segundos.
- Extração de metadados em escala (ID3v2.3/v2.4, MP4/iTunes, Vorbis, ASF)
  com quarentena, reconciliação de contagens e relatórios de qualidade.
- Camadas bronze/prata/ouro (medallion) com inventário colunar em Parquet
  sobre object storage (MinIO/S3).
- Star schema (Kimball) modelado em dbt com testes de dados
  (unique, not_null, accepted_values).
- Orquestração Airflow (TaskFlow) com retries, métricas de execução e
  alerta de falha via Telegram.
- CI/CD com GitHub Actions (pytest, ruff, mypy, gitleaks) e gestão de
  segredos (.env, Parameter Store); repo público sem vazamentos.
- Infra em nuvem via Terraform com guardrail de custo (AWS Budgets).

War stories por ferramenta (para entrevista):
- CDC/mtime: gargalo de I/O de 2-3h → segundos.
- Pandas: falso positivo do "null" (Astrophysics) → keep_default_na=False.
- ID3: ano nulo no BI → diagnóstico TYER vs TDRC → substituição por M4A.
- Docker: container sem acesso ao banco → networking + permissões.
- Idempotência: replace ingênuo → evolução para merge/upsert.
- Segurança: os 5 riscos encontrados e corrigidos no v1.