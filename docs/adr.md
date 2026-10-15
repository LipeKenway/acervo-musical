# ADRs — Decisões de Arquitetura

Registro curto de decisões: contexto (por que), decisão (o quê),
consequência (o que muda). Memória institucional do projeto.

Nota: ADR-001 (fonte de verdade para tipo de lançamento) e ADR-002
(política de movimentação de pastas) vivem em docs/hierarquia.md,
pois são decisões de dado. ADRs de engenharia/infra nascem aqui.

## ADR-003 — Estratégia de CI e governança da main

- Contexto: FASE 1 pede portão de qualidade; repo público individual
  em fase de construção rápida.
- Decisão: CI com dois jobs (qualidade: ruff+pytest+mypy;
  seguranca: pip-audit+gitleaks). Dependabot semanal (pip +
  github-actions). Branch protection ADIADA até o ritmo acalmar
  (Fases 3/4). Regras "S" do ruff adiadas; o job de segurança é
  coberto por pip-audit + gitleaks.
- Consequência: push direto ainda possível (velocidade); risco
  mitigado por porteiro local (pre-commit) + CI + revisão dos PRs.

## ADR-004 — Cliente do lake: boto3 com endpoint_url

- Contexto: FASE 2 precisa falar com o lake S3 local; Fase 5 vai
  falar com S3 real da AWS.
- Decisão: usar boto3 com `endpoint_url` apontando para o lake local
  (SeaweedFS hoje), em vez de bibliotecas específicas de vendor
  (ex.: `minio`).
- Consequência: o código de upload da FASE 2 é o MESMO da Fase 5
  (só muda o endpoint) — treino idêntico ao production, sem
  retrabalho. Endpoint e bucket vêm de variáveis genéricas
  (LAKE_ENDPOINT / LAKE_BUCKET), sem nome de fabricante no código.

## ADR-005 — Setup pós-format: o PC é descartável

- Contexto: format apagou venv, .env, extensões e os dados
  gitignored (bronze/prata/ouro em CSV).
- Decisão: tratar o PC como descartável: código e docs vivem no
  GitHub; setup vive no Settings Sync; segredos no .env (com
  .env.example como molde); dados regeneráveis vivem no pipeline.
- Consequência: recuperação completa em ~30 min + tempo de
  extractor; nenhuma perda única. Séries temporais
  (historico/evolucao) reiniciam após format — custo aceito para
  dados gitignored.

## ADR-006 — Lake local: SeaweedFS após o EOL do MinIO OSS

- Contexto: em out/2026, ao subir a FASE 2, o MinIO open-source
  mostrou sinais de arquivamento em cascata: imagem sumiu do Docker
  Hub ("repository does not exist"), quay.io recusou pull anônimo
  (401 Unauthorized), e o CDN oficial respondeu 410 Gone ("these
  files are no longer served"). Pulls de controle (postgres:16-alpine
  no Docker Hub; quay.io/prometheus/busybox) passaram sem problema,
  provando Docker e rede saudáveis — restrição era específica do
  repo minio/minio. O último release no GitHub (out/2025, um fix
  de CVE) oferece só código-fonte, sem binário Windows.
- Decisão: SeaweedFS (projeto ativo, binário único, API S3
  compatível) como lake local. Binário baixado do CDN oficial
  (dl.min.io -> github.com/seaweedfs/seaweedfs/releases), escutando
  em 127.0.0.1:8333 (API S3) e 8888 (UI), com endpoint e bucket
  vindo de variáveis genéricas (LAKE_ENDPOINT / LAKE_BUCKET). Sem
  IAM/criptografia por ser treino local com dados regeneráveis — o
  S3 real (Fase 5) traz ambos nativamente.
- Consequência: o princípio do ADR-004 permanece intacto (boto3 com
  endpoint_url; só muda o endpoint). docker-compose.yml permanece
  no repo como caminho preferencial e pode ser retestado em fases
  posteriores.
- Lição: dependências morrem no meio do projeto; a resposta é ADR +
  fallback ativo, não pânico. War story pronta: "upstream EOL no
  meio da Fase 2; avaliei alternativas (LocalStack, SeaweedFS,
  Garage, só filesystem) e escolhi SeaweedFS com decisão
  registrada".

## ADR-007 — Lake local sem criptografia/IAM

- Contexto: SeaweedFS subiu sem signing key para STS e sem
  passphrase de KEK (avisos SSE-S3 e IAM no log).
- Decisão: aceitar o estado para treino local, mitigado por bind
  em 127.0.0.1 (interfone do apartamento) + dados regeneráveis +
  segredos dummy. S3 real na Fase 5 traz SSE e IAM nativamente.
- Consequência: risco controlado para o ambiente de treino;
  documentado para não virar "padrão esquecido".