# Project Resort R8 — eliminar prédios sem acabamento no mapa de 2 km x 1 km

## Orientação imutável
O mapa georreferenciado usa 2.000 metros paralelos à orla de Copacabana e 1.000 metros em direção ao interior (2 km²). O arquivo congelado `geo/procedural/R4_SOURCE_FRAME.json` já possui exatamente essas medidas e rotação costeira de 46°. Não existem 2.000 metros para dentro da cidade.

## Correção da R7
A cena R7 gerava somente 50 prédios 3D detalhados, mas mantinha aproximadamente 1.418 massas sem janelas do modelo GIS de origem. Aplicar URP/Lit a essas massas não basta: elas continuam parecendo caixas sem acabamento.

A R8 trata todos os edifícios: preserva integralmente os 50 detalhados e converte os outros 1.418 para sete categorias de malha por estilo (wall, shadow, glass, trim, roof, metal, stone). O gerador lê os anéis reais de cada imóvel, a altura do catálogo e o estilo já atribuído; adiciona fachadas com portas, janelas, peitoris, caixilhos, coroamento e cobertura sem deslocar o polígono OSM. São 50 estilos em 10 famílias arquitetônicas. UV0 é projetado por face.

A geração de R8 não move ou recalcula ruas. O script Unity mantém exatamente os 3.731 triângulos originais de vias e elimina **somente** os triângulos de massas antigas de edifícios no derivado da cena R8. Os materiais URP/Lit PBR dos 50 estilos são reutilizados na R8; ausência de material, UV0 ou ID semântico aborta a construção. O R7 original e a cena R7 ficam preservados.

## Medições do primeiro lote local Blender 5.2.1
- 1.418 prédios de fundo e 50 edifícios R7 = 1.468.
- 50 estilos; 350 meshes de fundo com 7 categorias semânticas.
- 182.847 aberturas/painéis de janelas gerados; 893.682 faces no FBX R8.
- FBX R8 corrigido: 46.643.404 bytes; arquivo derivado não modifica fonte geográfica.
- Reimportação do mesmo FBX real no Blender 5.2.1: 350/350 meshes reconhecidas, UV0 finito, 50 estilos, 893.682 faces e origem geográfica consistente. PASS.
- **Defeito real identificado por 3 capturas nativas:** todos os 1.468 anéis OSM eram horários e as paredes R8 estavam viradas para dentro. Corrigido o winding externo para CW e CCW; regressão geométrica 1/1, reimportação Blender 350/350 e 13/13 contratos R7 passaram.
- Teste Unity **6000.6.2f1, NVIDIA RTX 4060 Ti, Direct3D11** após o patch: `RESORT_R8_NO_BLANK_PASS buildings=1468 backgrounds=1418 renderers=350 styles=50 roadTriangles=3731 windows=182847`, exit code 0, zero UV0 ausentes, zero shaders incorretos.
- Capturas reais Unity após corrigir o winding: `ArtSource/Previews/R8_01_Dense_City_RealUnity.png`, `R8_02_Orla_Aerial_RealUnity.png`, `R8_03_Facades_Rooftops_RealUnity.png`. `ArtSource/Previews/R8_VisualNativeQA.json` tem hashes, GPU e procedência; o resultado não é print sintético.
- Os prédios já aparecem inteiros e com vidraças/caixilhos, mas a cena ainda precisa de solo/calçadas/praia/vegetação, materiais mais ricos e refinamento estilístico. Aceitação artística final e FPS **NÃO aprovados**. As fachadas são paramétricas, não réplicas cadastrais de imóveis reais.

## Fluxo GitHub-first
O workflow `.github/workflows/r8-full-city-2x1.yml` gera novamente os 50 FBX R7, verifica a máscara original de ruas, monta a cena R7, produz o FBX dos 1.418 remanescentes, reimporta no Blender e publica os artefatos validados. Não exige o PC ligado para gerar assets. Para validação visual final e captura por GPU real, transferir os artefatos para uma cópia de QA e executar `ResortR7FacadeFinish.Build`, `ResortR8FullCityFinish.Build` e o capturador R8. Nunca substituir GIS original por arquivo derivado, nem considerar render Blender como imagem do jogo.

## Licença e limites
Os footprints, vias, posições e alturas atribuídas vêm de dados OpenStreetMap (© OpenStreetMap contributors — ODbL 1.0). Nem todas as alturas ou tipologias correspondem a levantamento cadastral de campo. O kit é autoral e estilizado; prioriza geografia coerente e eliminação dos blocos genéricos.
