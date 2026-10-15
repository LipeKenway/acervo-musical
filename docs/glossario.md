# Glossário do Acervo Musical

Glossário vivo do projeto. Regra da casa: palavra nova que entra no
vocabulário vira entrada aqui, com tradução de júnior para júnior.

## Camadas e formatos

- **Bronze / prata / ouro (medallion)** — três camadas de refinamento:
  bronze é a foto crua do disco; prata é a tabela limpa e reconciliada;
  ouro são os resumos prontos para BI. Analogia: minério → lingote →
  joia.
- **Parquet** — formato de arquivo colunar: guarda os dados por coluna
  (não por linha), comprime melhor e lê só o que a query precisa.
  Analogia: fichário organizado por campo, em vez de fichas inteiras.
- **CSV utf-8-sig** — planilha de texto com BOM: legível no Excel sem
  virar hieróglifo; é o formato das camadas bronze/prata/ouro em CSV.
- **Snappy** — compressão rápida que o Parquet usa por padrão: troca
  alguns pontos de razão de compressão por muita velocidade.

## Lake e object storage

- **Object storage** — armazenamento que trata tudo como objeto com
  chave (caminho), sem sistema de arquivos por baixo. Analogia:
  guarda-volumes com ticket, em vez de estante com prateleiras.
- **Bucket** — a caixa principal dentro do object storage; aqui,
  `acervo-musical`.
- **Prefixo** — o "começo do caminho" da chave; é assim que nascem as
  zonas e pastas lógicas sem existir pasta de verdade.
- **Zonas do lake (raw/curated/gold)** — raw é a cópia imutável de como
  chegou; curated é o Parquet limpo e particionado; gold são os
  agregados modelados. É o medallion morando no object storage.
- **Endpoint** — o endereço (URL) onde o serviço S3 atende; o boto3 usa
  `endpoint_url` para falar com o lake local em vez da AWS.
- **boto3** — a biblioteca oficial da AWS para Python; treinada no
  SeaweedFS local, usada de verdade na Fase 5 (ADR-004).
- **MinIO** — o S3 caseiro original do projeto; arquivado pelo upstream
  em 2026 (Docker Hub sem imagem, quay restrito, CDN com 410 Gone).
  Hoje é peça de museu (ADR-006).
- **SeaweedFS** — o substituto ativo do MinIO: binário único, API S3,
  nosso lake local. Analogia: o mesmo guarda-volumes, outro fabricante.
- **EOL (end-of-life)** — quando uma ferramenta para de receber
  manutenção. O MinIO OSS teve EOL no meio da Fase 2; a resposta foi
  ADR + fallback ativo, não pânico.

## Particionamento e consulta

- **Particionamento hive** — pastas `coluna=valor/` (ex.:
  `decada=1990/`) que os engines leem como coluna; organiza o endereço
  dos dados, não o conteúdo.
- **Partition pruning** — quando a query filtra pela coluna
  particionada, o engine abre só as pastas daquele valor e poda o
  resto. Analogia: ir direto na gaveta certa do fichário.
- **DuckDB** — banco analítico embutido (sem servidor): SQL direto em
  Parquet/CSV/arquivos. Analogia: um motor de query que mora dentro do
  seu Python.
- **Hive partitioning no DuckDB** — a flag que faz o DuckDB reconstruir
  a coluna de partição a partir do nome das pastas.

## Qualidade de dados

- **Quarentena** — ala hospitalar: arquivo que falhou na extração vai
  para lá com o motivo escrito, sem sujar a prata.
- **CDC por mtime** — change data capture caseiro: só reprocessa o que
  mudou no disco desde a última foto.
- **Reconciliação pasta × tag** — o reconciliador compara a taxonomia
  das pastas com as tags Mp3tag e produz a fila de revisão humana.
- **Fila de revisão humana** — os casos em que pasta e tag discordam e
  só você (dono do acervo) pode decidir.
- **Cobertura** — percentual de linhas com tag preenchida (Subgenre /
  Album Type); 100% nos três containers.

## Orquestração e warehouse (Fases 3-4)

- **Watermark** — marca d'água de estado: "até onde o pipeline já foi";
  base do CDC incremental da Fase 3.
- **Star schema** — modelagem dimensional: tabelas dim_* (quem/onde)
  girando em torno da fact_* (o que aconteceu).
- **dbt** — SQL com versionamento, testes e linhagem; o dono do ouro na
  Fase 3.
- **Airflow / DAG / TaskFlow** — orquestrador: agenda, retries e
  histórico; TaskFlow é a API de decorators que usaremos na Fase 4.

## CI e colaboração

- **Personal Access Token (PAT)** — crachá de visitante do GitHub:
  substitui a senha no push, com escopo e prazo, cancelável sem trocar
  a fechadura.
- **Runner** — a máquina alugada que executa o workflow (ubuntu-latest).
- **Pull request (PR)** — "fiz numa branch separada, pode entrar na
  main?". Até o Dependabot abre PRs; você revisa e mergeia.
- **pip-audit** — cruza suas bibliotecas com o catálogo público de
  falhas conhecidas (CVEs).
- **Branch protection** — regra que só deixa a main receber código
  aprovado e verde. Adiada por decisão (ADR-003).
- **Badge** — o selinho no README mostrando o status do CI ao mundo.

## Git e recuperação

- **Clone** — baixar o repositório com todo o histórico numa máquina
  nova. Analogia: receber a cópia completa do caderno, não só a última
  página.
- **Rebase (git pull --rebase)** — reaplicar seus commits em cima dos
  que chegaram do remoto, mantendo a história em linha reta.
- **Credential Manager** — o cofre do Windows que guarda seu token
  para você não digitar senha em todo push.
- **Settings Sync** — o VS Code sincroniza extensões e configurações
  pelo GitHub; formatar o PC não custa mais o setup.
- **PAT com validade** — crachá com data de expiração: token vencido
  não abre a porta; gerar outro é rotina saudável (30 dias).
- **Stop-parsing token (--%)** — diz ao PowerShell: "repasse tudo
  literalmente ao executável, sem interpretar nada". Salvou nossas
  flags do weed (`-ip.bind` tinha virado "-ip" + ".bind=...").

## Docs vivas

- **ADR (Architecture Decision Record)** — registro curto de uma
  decisão: contexto, decisão, consequência. Memória do "porquê".
- **Doc gerada (blocos marcados)** — trecho de doc reescrito pelo
  pipeline entre marcadores HTML (NUMEROS-AUTO, COLUNAS-AUTO); o
  gerador só toca entre eles, a prosa fora é sagrada.
- **Snapshot datado** — número publicado com data de validade explícita:
  "isto era verdade em 14/10/2026 19:59".