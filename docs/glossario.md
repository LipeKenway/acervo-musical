# Glossário de Palavras Mágicas

Dicionário vivo do projeto Acervo Musical.
Cada termo: tradução, analogia do dia a dia e onde vive no projeto.
Regra da casa: palavra nova aprendida = entrada nova aqui.

## Dados e pipeline
- **CDC (Change Data Capture)** — processar só o que mudou desde a última rodada.
  Analogia: extrato do banco (você não reconta o cofre todo dia).
  No projeto: mtime dos arquivos; 3 horas → segundos.
- **Watermark** — o "save" que marca até onde o pipeline já processou.
  Analogia: save do videogame.
  No projeto: Fase 3 (tabela de estado); o legado usava o mtime do CSV (frágil).
- **Bronze / Prata / Ouro (Medallion)** — camadas: foto crua do disco / planilha
  limpa / resumos prontos para BI.
  Analogia: minério bruto → metal refinado → joia na vitrine.
  No projeto: inventario_acervo.csv / acervo_prata.csv / futuros agregados ouro.
- **Drift** — quando a realidade (disco) diverge do inventário (bronze).
  Analogia: mudança de endereço sem avisar o correio.
  No projeto: o caso da pasta " Rubycon", pego pela quarentena.
- **Quarentena** — ala hospitalar: registro que falha vai para lá COM motivo,
  em vez de sujar a planilha. No projeto: quarentena.csv.
- **Reconciliação** — cruzar números de fontes diferentes até a diferença ser
  explicada. Analogia: conferir cupom com a fatura.
  No projeto: o caso dos 80 arquivos (79 PDFs + 1 .mov).
- **Cobertura** — % de registros com um campo preenchido.
  No projeto: MOOD/MOVEMENT 100% em FLAC, M4A e MP3.
- **mtime** — a data de "última modificação" que o sistema operacional carimba
  no arquivo. É a chave do CDC e do drift.

## Processo e qualidade
- **Smoke test / Piloto (--amostra)** — rodar numa amostra minúscula antes do
  run completo. Analogia: provar a comida na colher antes de servir o banquete.
- **Resume / Checkpoint (--completar)** — continuar de onde parou, processando
  só o que falta. Analogia: lista de adesivos (visitar só as casas sem adesivo).
- **Idempotência** — rodar 2x dá o mesmo resultado que rodar 1x.
  Analogia: salvar o despertador de 7h duas vezes não cria dois despertadores.
- **Upsert / Merge** — atualiza se existe, insere se não (Fase 3, Postgres).
- **Replace** — apagar e recriar a tabela inteira a cada carga (ingênuo e
  destrutivo). Dívida do legado.
- **Linter (ruff)** — corretor ortográfico do código.
- **Type hints** — etiquetas "isso é texto, isso é número" nas funções.
- **mypy** — o fiscal que confere se as etiquetas estão certas.
- **pytest** — robô que roda os testes das suas funções.
- **pre-commit** — porteiro que confere o commit antes de ele entrar.
- **CI/CD (GitHub Actions)** — robô na nuvem que roda testes a cada push.
- **gitleaks** — cachorro farejador de senha vazada no código.
- **Dependabot** — bot que avisa quando biblioteca sua fica velha.
- **ADR** — documento do "por que escolhi X e não Y".

## Infra e Docker
- **Container** — programa rodando numa caixa isolada.
  Analogia: kitnet alugada: você usa a cozinha sem mexer na casa do vizinho.
- **docker-compose** — a planta baixa das caixas.
- **Imagem** — o molde de onde as caixas (containers) são fabricadas.
- **Volume / Mount** — a ponte entre o seu disco e a caixa.
- **:ro (read-only)** — vitrine de museu: dá para olhar, o vidro não deixa tocar.
- **Porta** — a porta numerada por onde entra conexão num serviço.
- **Bind (127.0.0.1)** — decidir quem pode bater na porta: 127.0.0.1 = interfone
  só dentro do apartamento; 0.0.0.0 = interfone na calçada.
- **healthcheck** — o teste de "estou vivo" que o container responde de tempos
  em tempos.
- **depends_on: service_healthy** — só subir quando o dependente responder
  "estou vivo". Analogia: abrir o restaurante só com o gás aceso.
- **Âncoras YAML (& / <<:)** — bloco reutilizável para não copiar-colar no compose.
- **Variável de ambiente** — recado de configuração que só o serviço lê.
- **.env** — o cofre local das variáveis; o Git não enxerga.
- **restart: unless-stopped** — a geladeira que religa sozinha após cair a luz.
- **Executor (LocalExecutor)** — o modelo de turno: quem executa as tarefas
  (LocalExecutor = na cozinha da sua própria máquina).
- **Fernet** — criptografia nativa do Airflow para Connections.

## Orquestração (Airflow)
- **DAG** — a receita: passos ordenados, sentido único, sem loops.
- **Scheduler** — o gerente que lê a receita e libera os pratos na hora certa.
- **Worker** — o cozinheiro que executa.
- **Webserver** — a recepção: o painel onde você vê tudo.
- **XCom** — post-it entre tarefas (dado pequeno).
- **TaskFlow API** — escrever DAGs como funções Python que passam valores.
- **catchup=False** — o jornaleiro esperto: não deixa pilha de jornais velhos
  quando você passa dias fora.
- **on_failure_callback** — a cláusula "se quebrar, avisa fulano" do contrato.

## Formatos e armazenamento
- **CSV utf-8-sig** — planilha de texto que o Excel abre sem quebrar acentos.
- **Parquet** — formato colunar comprimido: menor e mais rápido que CSV.
  Analogia: arquivo organizado por assunto, não por ordem de chegada.
- **pyarrow** — a biblioteca que lê/escreve Parquet.
- **DuckDB** — banco que mora dentro do Python; SQL direto em Parquet.
- **MinIO** — S3 caseiro: armazenamento de objeto local, de graça.
- **S3** — armazenamento da AWS (Fase 5; só metadados, nunca o áudio).
- **Star schema** — um sol (tabela de fatos) com planetas em volta (dimensões).
- **dbt** — SQL como código de engenharia: versionado, testado, documentado.

## Áudio (o seu domínio)
- **Tag** — a carteira de identidade dentro do arquivo de áudio.
- **ID3 v2.3 / v2.4** — as "gerações" de tags do MP3; a v2.3 não tem MOOD/MOVEMENT.
- **MOOD / MOVEMENTNAME** — os campos que você adotou como subgênero e tipo de álbum.
- **Bitrate (kbps)** — quantos bits por segundo o áudio usa (320 = mais denso).
- **CBR / VBR / ABR** — bitrate constante / variável / adaptável.
- **Sample rate (Hz)** — "fotos" do som por segundo (44100 = padrão CD).
- **Bits por amostra** — a precisão de cada foto (16/24 bits no FLAC).
- **Codec** — o empacotamento do áudio (AAC, FLAC, MP3...).
- **mutagen** — a biblioteca Python que lê todas essas identidades.

## Segurança e carreira
- **Menor privilégio** — dar a cada usuário só a chave mínima que ele precisa.
- **Service account** — usuário dedicado de um sistema (app escreve; BI só lê).
- **Pseudonimização (SHA-256)** — transformar o caminho numa impressão digital
  irreconhecível.
- **RPO / RTO** — quanto de dado você aceita perder / quanto tempo aceita ficar
  fora do ar.
- **3-2-1** — 3 cópias, 2 mídias, 1 fora de casa.
- **Restore testado** — backup que nunca foi restaurado é promessa, não backup.
- **Audit log** — o caderno de quem mudou o quê, e quando.
- **Observabilidade / métricas** — sinais vitais do pipeline.
- **Budgets** — o alerta de cobrança (o guarda-chuva da nuvem).
- **IaC / Terraform** — infraestrutura por código, não por cliques.
- **War story** — um problema real resolvido, contado como história de entrevista.