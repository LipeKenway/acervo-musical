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