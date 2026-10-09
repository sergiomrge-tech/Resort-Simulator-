# R5 — Implantação automática e segura de 50 fachadas reais em Copacabana

## Checkpoint validado — Blender + Unity Editor DX11 (08/10/2026)

**Implementação técnica concluída no piloto de 50 prédios.** A [execução GitHub Actions R5](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37868085440) gerou um FBX consolidado real do mapa com apenas os 50 volumes antigos removidos: 763 faces de edifícios retiradas, 0 faces de rua retiradas, 3.731 faces originais de vias preservadas, 577.770 polígonos das novas fachadas. Foram comparadas também as coordenadas do BlenderGIS real (matriz original rotacionada 46°), e os hashes dos originais foram preservados.

**Validação local nativa, em uma cópia separada na unidade D:** a Unity 6.6.2f1 importou o FBX na API nativa do Editor e confirmou 50 IDs distintos, 370 renderizadores detalhados, 1.181.354 triângulos no FBX derivado. A cena QA foi salva em `UnityProject/Assets/Scenes/R5_Copacabana_50_Predios_EditorQA.unity`. Duas capturas **reais Unity Camera.Render com Direct3D11** foram feitas e versionadas:
- [Câmera ampla — QA técnico](../../ArtSource/Previews/R5_Unity_DX11_City_Overview_Real_QA.png)
- [Câmera aproximada — QA técnico](../../ArtSource/Previews/R5_Unity_DX11_Facade_Closeup_Real_QA.png)
- [Relatório nativo Unity com SHA256 e limites](../../ArtSource/Previews/R5_Unity_DX11_Native_QA.json)

**Gate visual: PENDENTE.** As capturas reais mostram que as fachadas novas têm janelas/sacadas estruturais, mas os 1.418 prédios restantes ainda são massas brancas e o acabamento das fachadas novas não atende ao objetivo de *Realismo Estilizado Premium*. A renderização DX11 não substitui uma avaliação de texturas, materiais URP, calçadas, areia, paisagismo, iluminação ou FPS. Não dizer que 1.468 prédios já têm fachadas premium; não afirmar executável/Steam build pronto.

**Próximas melhorias:** materiais PBR por estilo e região, adição real de superfícies/calçadas sem comprometer geografia, LOD agressivo fora da vista de pedestre, streaming por quarteirão e benchmarks Unity. Substituição massiva dos 1.418 prédios **não deve acontecer** antes de provar memória e desempenho. A fase 2 de quiosque/economia/NPCs segue arquivada para após o gate visual.


**Objetivo:** construir uma **cópia geográfica derivada do mapa atual**, substituindo as volumetrias antigas dos **50 OSM ways** cujos modelos reais FBX estão na biblioteca R4. Nenhum arquivo do mapa original é modificado.

## Processo

1. Ler a fonte GIS original `geo/data/copacabana.osm.gz` e o quadro geográfico imutável `geo/procedural/R4_SOURCE_FRAME.json` (2.000 × 1.000 metros, 46°), o catálogo dos 1.468 edifícios e o manifesto real dos 50 FBX exportados.
2. No gerador GIS original restaurado de R3 (`Tools/geo/r5_original_osm_pipeline.py`), reconstruir o OBJ completo e uma cópia que **omite exatamente** os 50 IDs de edifício da biblioteca R4. Omitir edifícios de R3 seria um erro — são elementos especiais reservados, fora do conjunto de 50.
3. Em `Tools/geo/r5_mask_city_50.py`, comparar matematicamente **todos os triângulos originais** por coordenadas e material. Reprovar se uma única face de rua, prédio não selecionado ou geografia costeira sofrer alteração.
4. Abrir o BlenderGIS original e comparar o OBJ regenerado com a malha Blender, aplicando a **matriz de rotação original de 46°**; reprovar divergências, mesmo que o número de faces coincida.
5. Importar os 50 FBX gerados pelo R4.1 e posicionar cada um no centro OSM original, transformado pela matriz GIS correta. Exportar um **novo FBX consolidado** com a cidade preservada e apenas os 50 antigos omitidos.
6. Renderizar uma captura **real Blender Cycles** em um ponto geográfico do próprio lote, com registro SHA256 e relatório dos 50 modelos. A captura do Blender é uma prévia técnica e não equivale a um screenshot Unity, teste FPS ou aprovação artística.
7. Executar testes de integridade e subir o FBX consolidado, render e relatórios na branch R5 através do GitHub Actions. Só após isso integrar ao projeto principal.

## Saídas previstas

- `UnityProject/Assets/Architecture/R5_Pilot50/R5_Copacabana_50_Fachadas_Derivado.fbx`
- `UnityProject/Assets/Architecture/R5_Pilot50/R5_SOURCE_MASK_QA.json`
- `UnityProject/Assets/Architecture/R5_Pilot50/R5_BLENDER_SCENE_QA.json`
- `ArtSource/Previews/R5_Copacabana_50_Predios_Blender_Real_QA.png`

**Escopo real:** *50 edifícios* em cenário derivado, com os 1.418 restantes preservados como volumes originais. Ainda **não** representa implantação final de todos os 1.468, nem importa automaticamente o novo FBX na cena principal Unity. Para ampliar a região, repetiremos o procedimento por blocos com o workflow R4 e o controle de duplicidades por OSM ID.

**Proibições:** sobrescrever `ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend` ou `UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx`, colocar modelo novo por cima da massa GIS sem removê-la, chamar alturas estimadas de medições, afirmar material PBR aprovado apenas porque foi exportado para FBX, apresentar a prévia do Blender como screenshot do jogo Unity.

**Próxima inspeção:** abrir o FBX derivado no editor Unity 6.x, examinar materiais URP, sombras e escala em perspectiva de pedestre, realizar benchmark antes de ampliar a densidade dos modelos 3D. O sistema comercial do quiosque e os NPCs permanecem arquivados para depois da etapa visual.

© OpenStreetMap contributors — ODbL 1.0 (dados geográficos). Modelos procedurais próprios Project Resort.
