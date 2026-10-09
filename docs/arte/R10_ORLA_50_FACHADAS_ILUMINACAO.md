# Project Resort R10 — acabamento costeiro, fachada e estabilidade visual (09/10/2026)

## Objetivo e integridade
A versão R10 deriva da branch R9, sem substituir `main`, alterar GIS congelado, mudar o OSM ou reconstruir o mapa arbitrariamente. Área exata: **2.000 m paralelos à orla × 1.000 m no sentido interior, 2 km²**. Preservados 1.468 footprints de prédios no catálogo (50 detalhados em R7 + 1.418 em R8), 3.731 triângulos nativos de ruas do R7 e 48 árvores georreferenciadas e aprovadas fora do asfalto em R9.

## Mudanças implementadas
1. **Calçadão de Copacabana inspirado no mosaico tradicional**: gerador `Tools/Blender/generate_r10_coastal_details.py`, reaproveita a linha costeira real OSM `way/70574890`, 401 amostras a cada 5m em toda a costa. O derivado autoral ocupa uma faixa provisória de 25,5–38 m da linha da água para não sobrepor as ruas existentes. Três bandas onduladas de pedra escura, pedra clara, bordas e três discretos cordões de espuma resultam em **9 meshes / 3.600 faces** e UV0. Não representar largura de areia/calçadão como levantamento topográfico real.
2. **Mar dinâmico autoral**: `UnityProject/Assets/Shaders/R10_AnimatedOcean.shader` em URP, sem quad uniforme ciano, com camadas de ondulação lenta calculadas por posição mundial e tempo e variação de brilho. **Não é simulação hidrodinâmica nem água fotorrealista**; futuras ondas normais, foam físico e reflexão real dependerão de avaliação de FPS.
3. **150 acabamentos adicionais** na cena derivada: gera e salva materiais URP/Lit por 50 estilos x parede, vidro e cobertura. Aproveita as texturas originais da R7/R8 e usa matizes específicos para famílias cariocas, Art Déco, hotéis e residenciais. Não altera os materiais originais das R7/R8.
4. **Problema da falsa cena preta**: diagnósticos nativos em seis configurações apontaram que capturas de cena via URP em batch mode usando o primeiro quadro saíam excessivamente escuras, mesmo sem sombras. A R10 captura **cinco renderizações reais de aquecimento por enquadramento** antes de extrair pixels, mantendo sombras direcionais suaves com strength 0,18 e impedindo regressão de grandes áreas pretas com um gate de luminosidade na visão central. Nenhum print sintético ou retoque.
5. **Cena independente de QA na Unity**: `Assets/Scenes/R10_Copacabana_Calçada_Mosaico_Mar.unity`, construída por `ResortR10CoastalFinish.Build` a partir da R9. A R10 não é a cena de gameplay definitiva.

## Resultados reproduzidos em dispositivos reais de software
- Blender 5.2.1: `R10_COASTAL_BLENDER_PASS` (9 meshes, 3.600 faces, georreferenciadas, SHA-256 do FBX) e reimportação independente via `Tools/tests/test_r10_coastal_native.py` aprovados.
- Unity 6000.6.2f1, RTX 4060 Ti, D3D11, URP: `RESORT_R10_COPACABANA_PASS` com 9 peças costeiras, 150 variantes de materiais, 48 árvores e 3.731 triângulos de via intactos, shader de mar reconhecido.
- `ResortR10VisualCapture.Run`: cinco PNGs **capturados realmente na Unity** em 1600 × 900 e `R10_VisualNativeQA.json`, com hash para cada imagem e metadados de procedência. A captura 5 agora mostra a peça de mosaico por cima, não um quadrilátero azul de mar; primeira captura aérea usa aquecimento para evitar sombras falsas do cold-start.
- Uma rodada GitHub Actions gera toda a cadeia R7 → R8 → R9 → R10 no runner GitHub, sem PC ligado. A publicação do artefato é condicionada a retorno de todos os scripts reais de Blender.

## Limitações para gates futuros
- **Visual final ainda não aprovado**. Prédios continuam com formas repetitivas, sem as variações de sacadas, volumetria, coroamentos, telhados e vegetação densa de uma produção premium; não chamar de arquitetura documentalmente fiel nem simulação finalizada.
- 2km² ainda carecem de calçadas reais por via, mobiliário urbano, veículos, iluminação noturna e parque completo.
- Mar tem shader procedural animado; sua animação em gameplay, clipping e performance ainda requerem testes de execução em Play mode. A faixa do mosaico é ilustrativa sobre a costa OSM, não a topografia exata.
- Ainda **não** medimos FPS, draw calls, VRAM, LOD, culling, streaming, pathfinding, navegação de personagem ou build Windows/Steam jogável. Evitar afirmações de release ou screenshots fabricadas.

## Próximos gates
R11: fachadas variadas por edifício, volumetria/varandas, piso urbano por tipo, areia texturizada com pedra portuguesa mais autêntica, iluminação diurna por ângulo e LOD. Depois, perfilagem e jogabilidade no mesmo mapa em Unity 6000.6.2f1.

Dados espaciais OSM © OpenStreetMap contributors, ODbL 1.0. O estilo autoral não replica fotografia/cadastro de edifícios específicos.
