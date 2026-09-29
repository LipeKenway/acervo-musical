# ADRs — Decisões de Arquitetura

## ADR-003 — Estratégia de CI e governança da main
- Contexto: FASE 1 pede portão de qualidade; repo público individual
  em fase de construção rápida.
- Decisão: CI com dois jobs (qualidade: ruff+pytest; seguranca:
  pip-audit+gitleaks). Dependabot semanal (pip + github-actions).
  Branch protection ADIADA até o ritmo acalmar (Fases 3/4).
  Regras "S" do ruff adiadas; o job de segurança é coberto por
  pip-audit + gitleaks.
- Consequência: push direto ainda possível (velocidade); risco
  mitigado por porteiro local (pre-commit) + CI + revisão dos PRs.
- Nota: ADR-001/002 vivem em docs/hierarquia.md (dados); novos ADRs
  nascem aqui.

## ADR-004 — Cliente do lake: boto3 com endpoint_url
- Contexto: FASE 2 precisa falar com MinIO; Fase 5 vai falar com S3 real.
- Decisão: usar boto3 com `endpoint_url` apontando para o MinIO, em vez
  da biblioteca `minio`.
- Consequência: o código de upload da FASE 2 é o MESMO da Fase 5
  (só muda o endpoint) — treino idêntico ao production, sem retrabalho.