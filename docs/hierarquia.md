# Hierarquia do Acervo (F:\Acervo (Musicas))

Taxonomia oficial das pastas, usada pelo scanner e pelo modelo de dados.

## Padrão geral
genero / [subgenero_ou_midia] / tipo_lancamento / [pasta_album] / [pasta_disco] / arquivo

## Níveis
1. Gênero (ou macro-gênero): Experimental, Soundtrack, Dance, ...
2. Subgênero ou mídia (OPCIONAL): Glitch Hop, Games, Film, Anime, ...
3. Tipo de lançamento: Albums, Singles, EPs, Mixtapes, Compilation, Collection, ...
4. Pasta do álbum/artista (opcional)
5. Pasta de disco (opcional, dentro do álbum)

## Regras confirmadas
- Nada solto nos níveis de gênero e subgênero.
- Singles: faixas soltas direto no nível de tipo (é o propósito da pasta).
- Nem todo gênero tem subgênero (profundidade variável).
- Pastas de disco (CD 1, CD 2, Disc 1) existem DENTRO de pastas de álbum,
  apenas nos tipos Albums/Compilations e afins.
- Mixtapes, Collections, EPs e Singles NUNCA têm subpastas de disco.
- Soundtrack: nível 2 é a mídia (Games, Film, Anime).
- Nomes exóticos de pasta são válidos (ex.: "&&&&&").

## Detecção de pasta de disco (regex, case-insensitive)
^(CD|Disc|Disco)\s*\d+$

## Vocabulário de tipos de lançamento
Albums, Album, Singles, Single, EPs, EP, Compilations, Compilation,
Collections, Collection, Mixtapes, Mixtape, Lives, Live, Remixes, Remix

## Saídas do scanner v2
- data/processed/inventario_acervo.csv (inventário bronze)
- Relatório de tipos desconhecidos (calibra o vocabulário)
- Relatório de extensões ignoradas (reconciliação de contagens)

## Dois dialetos, uma taxonomia (pastas x tags)

### Gêneros com tipo na pasta
- Pastas (plural, exceto EP): Albums, EP, Singles, Mixtapes,
  Compilations, Collections
- Tags (MOVEMENTNAME): Album, EP, Single, Mixtape, Compilation, Collection
- Tradução: Albums->Album | EP->EP | Singles->Single |
  Mixtapes->Mixtape | Compilations->Compilation | Collections->Collection

### Mixes & Lives (tipo NÃO existe na pasta)
- L1 gênero: Mixes & Lives
- L2 subgênero (pasta e MOOD): DJ Mix, Live Set, Studio Mix
- Tipo de lançamento somente na tag MOVEMENTNAME:
  DJ Mix->DJ Set | Live Set->Live Album | Studio Mix->Continuous Mix
- Prata registra tipo_origem="tag" nessas linhas.

Diferença de dialeto NÃO é conflito. O relatorio_conflitos.csv
registra apenas anomalias pós-tradução — fila de revisão humana.

### ADR-001 — Fonte de verdade para tipo de lançamento
- Contexto: 577 faixas (0,52%) com pasta e tag discordando
  (ex.: compilação arquivada em Albums, tag=Compilation).
- Decisão:
  - Prata: tipo_final continua vindo da PASTA (organização física,
    estável, usada para particionamento).
  - Ouro (Fase 3, dbt): tipo oficial = TAG (identidade semântica,
    curada no Mp3tag, cobertura 100%).
  - relatorio_conflitos.csv = fila de higiene física, não erro de pipeline.
- Consequência: nenhuma re-execução cara agora; a fila encolhe
  conforme as correções de pasta/tag ao longo do tempo.

  ### Dialeto livre (confirmado pelo dono do acervo)
- Soundtrack e Mixes & Lives: a tag é a identidade do tipo de
  lançamento; a pasta NÃO é checada pelo reconciliador.
- Regra viva em src/ingest/reconciliador.py (GENEROS_LIVRES).

### Política de movimentação de pastas (ADR-002)
- Não fazer mutirão: o dado já está certo via tag (ouro usa tag).
- Mover pasta sem extração completa gera linhas fantasmas
  (caminho velho + caminho novo da mesma faixa).
- Higiene orgânica: corrigir pastas quando já estiver no Mp3tag.
- Mutirão só com: mover tudo -> scanner -> extração completa.