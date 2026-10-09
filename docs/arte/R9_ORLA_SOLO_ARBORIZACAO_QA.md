# Project Resort R9 — Solo urbano, orla OSM e arborização

## Proteções geográficas
O mapa jogável permanece **2.000 m paralelos à orla × 1.000 m de profundidade = 2 km²**. Referência local EPSG:32723, alinhamento costeiro 46 graus, `R4_SOURCE_FRAME.json` preservado. R7: 50 prédios 3D com acabamento. R8: outros 1.418 gerados; total 1.468 com geometrias de fachada, janelas e coberturas. Original GIS, R7 e R8 continuam intocados pela R9.

## Pipeline procedural reproduzível sem PC
`.github/workflows/r9-urban-environment.yml` executa Blender verdadeiro no GitHub Actions, primeiro recompõe e reimporta a cena R7/OSM e as fachadas R8, depois usa a linha costeira OSM `way/70574890` amostrada em **201 posições**, produz cidade plana com texturização URP própria e modela mar, faixa de areia ilustrativa de 42 metros contados da linha costeira, e parques/jardins/gramados/lagoas mapeados. A praia não pretende ser delimitação cartográfica exata, pois o OSM não define todas as bordas reais de areia.

### Árvores
Foram detectados 632 nós de árvore no snapshot OSM, 446 elegíveis nos guardas GIS. A R9 seleciona 120 candidatos reais e cruza suas coordenadas com os **3.731 triângulos originais de ruas**, impondo afastamento de 1,25m do polígono de asfalto. Seleciona exatamente **48 árvores não invasoras** sem deslocar árvores para posições inventadas. Na comparação com a lista R6 anterior, 7 nós foram substituídos por outros nós reais, devido ao teste contra geometria viária e margem de segurança. Restam limitações: não há levantamento topográfico, redes elétricas subterrâneas nem pontos exatos de canteiro; a geolocalização OSM é a única fonte.

O kit autoral de árvores R6 foi mantido como base estrutural e enriquecido em R9 com **geometria orgânica densa de folhas de dupla face** e tons variados, preservando semânticas de 4 materiais por árvore, em vez das copas esparsas observadas na primeira captura. Há dois estilos tropicais derivados do kit (sem inferir espécie botânica real); 48 posições reais, os outros modelos de palmeira e arbusto não são colocados onde não há identificação OSM.

### Terreno e materiais
A R9 elimina o piso azul vazio por um plano dentro dos limites do mapa e materiais URP/Lit próprios para pavimento, asfalto, mar, areia e verde. Os objetos de superfície recebem cores e texturas determinísticas e os edifícios preservam os materiais PBR da R7/R8. As faces de mar/areia seguem coordenadas do OSM em um visual exterior ao recorte jogável; 19 formas mapeadas de parque/grama/água foram incorporadas. Efeitos, mar plano e solo ainda são provisórios; não afirmar realismo final.

## Gates técnicos realizados no PC, não apenas checks estáticos
- Blender 5.2.1 LTS: geração e reimportação do FBX de ambiente, **70 meshes** sendo **48 árvores e 22 superfícies**, com quatro materiais por árvore, passes nativos.
- Seleção OSM x malha original de ruas: 48 pontos aprovados fora dos polígonos viários e da margem de 1,25m, check real em 3.731 triângulos.
- Unity 6000.6.2f1, NVIDIA RTX 4060 Ti, Direct3D11: R9 abriu cópia da R8, validou roadTriangles=3731, trees=48, surfaces=22, parksAndWater=19, coast=201, zero UV0 ausentes nas superfícies e zero slots inesperados. Arquivos `ArtSource/Previews/R9_UnityEnvironmentQA.json` e `R9_VisualNativeQA.json` documentam.
- Prints PNG guardados em `ArtSource/Previews/R9_*_RealUnity.png` são CAPTURAS REAIS da Unity, não imagens geradas artificialmente.
- **Bloqueios de produção:** ainda não foram medidos FPS, memória, pathfinding, streaming de 2km² ou jogabilidade. Aceitação artística final pendente. O pavimento é um plano simplificado, fachadas ainda podem estar repetitivas e o mar não tem animação realista. A captura aérea R9_01 mostra um setor muito escuro, apesar das correções de sombra; **não aprovar a iluminação final** até resolver esse contraste pela causa real. Sombras no plano pavimentado foram desativadas TEMPORARIAMENTE para QA, exigindo solução posterior com iluminação e contato realistas. Não liberar EXE Steam antes do gate.

## Fontes e licenças
Dados OpenStreetMap © OpenStreetMap contributors, ODbL 1.0. OSM material congelado em `geo/data/copacabana.osm.gz`, sem geometrias falsas como se fossem prédio histórico georreferenciado. Kit 3D procedural autoral.
