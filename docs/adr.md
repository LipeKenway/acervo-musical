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