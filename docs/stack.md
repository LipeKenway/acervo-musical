# Stack do Projeto Acervo Musical

Inventário vivo de linguagens, ferramentas e práticas.
Status: ✅ em uso | ⏳ roadmap (fase) | 🧊 legado | 🚫 fora de escopo | ⏸️ adiada por ADR

Números: 110.731 faixas | 912,89 GB | 311,3 dias de áudio
Repo público: github.com/LipeKenway/acervo-musical

## 1. Linguagens
| Ferramenta | Uso | Status |
|---|---|---|
| Python 3 | scanner, extractor, reconciliador, agregados, testes | ✅ |
| SQL | DuckDB (F2), dbt/Postgres (F3) | ⏳ F2/F3 |
| PowerShell | automação local | ✅ |
| YAML | compose, Actions, pre-commit | ✅ |
| Markdown | docs, ADRs, README | ✅ |

## 2. Bibliotecas Python
| Biblioteca | Uso | Status |
|---|---|---|
| mutagen | metadados ID3/MP4/Vorbis/ASF | ✅ |
| python-dotenv | segredos via .env | ✅ |
| pyarrow | leitura/escrita Parquet | ⏳ F2 |
| duckdb | SQL direto em Parquet | ⏳ F2 |
| boto3 | API S3 (MinIO na F2, S3 real na F5) | ⏳ F2 |
| stdlib (os, csv, pathlib, re, collections, datetime, time) | scanner/relatórios | ✅ |

## 3. Armazenamento e formatos
| Ferramenta | Uso | Status |
|---|---|---|
| CSV utf-8-sig | bronze/prata/ouro legíveis (Excel) | ✅ |
| Parquet | lake colunar particionado por década | ⏳ F2 |
| MinIO | S3 local (zonas raw/curated/gold) | ⏳ F2 |
| Amazon S3 | lake real (só metadados) | ⏳ F5 |
| Postgres | warehouse com star schema | ⏳ F3 |
| DuckDB | análise/benchmark CSV × Parquet | ⏳ F2 |
| MariaDB + SQL Server | prova multi-banco do v1 | 🧊 |

## 4. Orquestração, infra e CI/CD
| Ferramenta | Uso | Status |
|---|---|---|
| Docker Desktop / compose | caixas isoladas; planta das caixas | ✅ |
| Personal Access Token (PAT) | push sem senha | ✅ |
| GitHub Actions | CI: jobs qualidade + seguranca | ✅ |
| Dependabot | vigia semanal (pip + actions); 2 PRs mergeados | ✅ |
| pre-commit | porteiro local (ruff + gitleaks) | ✅ |
| Airflow TaskFlow | orquestração com retries e histórico | ⏳ F4 |
| Terraform | IaC do S3 | ⏳ F5 |

## 5. Qualidade, testes e segurança
| Ferramenta/Prática | Uso | Status |
|---|---|---|
| pytest | 12 testes de hierarquia e derivados | ✅ |
| ruff | linter/corretor | ✅ |
| mypy | fiscal de tipos (src/ limpo) | ✅ |
| gitleaks | farejador de segredos (local + CI) | ✅ |
| pip-audit | falhas conhecidas nas dependências (CI) | ✅ |
| type hints + docstrings | contrato legível | ✅ |
| quarentena | ala hospitalar com motivo | ✅ |
| reconciliação de contagens | bronze × prata × doc | ✅ |
| validação pasta × tag | reconciliador, 99,6% concordância | ✅ |
| dicionário de dados | Mp3tag ↔ prata | ✅ |
| smoke test (--amostra) / resume (--completar) | piloto e checkpoint | ✅ |
| dbt tests / service accounts | gold e menor privilégio | ⏳ F3 |
| Fernet / audit_log / backup testado | ⏳ F4 |
| branch protection | ⏸️ adiada (ADR-003) |

## 6. BI e observabilidade
| Ferramenta | Uso | Status |
|---|---|---|
| agregados ouro (6 CSVs) | resumos Excel/BI | ✅ |
| ouro_evolucao_storage.csv | série temporal do storage | ✅ |
| historico_armazenamento.csv | snapshots por run | ✅ |
| Metabase / metricas_execucao / Telegram | ⏳ F3/F4 |

## 7. Conceitos e práticas (coração do currículo)
ETL • CDC por mtime • medallion (bronze/prata/ouro) • lakehouse/Parquet
particionado • star schema • idempotência/upsert • data quality
(quarentena, reconciliação, cobertura) • governança (dicionário, ADRs) •
CI/CD • IaC • observabilidade • segurança (segredos, menor privilégio) •
backup 3-2-1/RPO/RTO • war stories

## 8. Fora de escopo — e por quê
Kubernetes/Spark/Databricks (overengineering) • Kafka/Redis (Projeto 3) •
Great Expectations/Soda (dbt basta) • DVC • MWAA/Composer (caro) •
Power BI (Metabase cobre) • multi-nuvem • subir 912 GB de áudio

## 9. Tradução para currículo
Headline: "Engenharia de Dados | Pipeline batch + CDC sobre 110k arquivos |
Python • Airflow • dbt • AWS"
Bullets novos da FASE 1:
- CI completo (pytest + ruff + mypy + pip-audit + gitleaks) em GitHub
  Actions, com Dependabot ativo e PRs revisados.
- Portão de qualidade local (pre-commit) + remoto (CI) em repo público
  sem segredos.