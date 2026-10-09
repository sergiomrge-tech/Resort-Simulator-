# Project Resort — QA nativo Unity R7 (09/10/2026)

Status: **ENGINEERING PASS / VISUAL FAIL**. Capturas nesta pasta são imagens reais geradas por Unity 6000.6.2f1, NVIDIA RTX 4060 Ti, Direct3D11 via `ResortR7VisualCapture.Run`, não Blender nem mockups.

## Gates nativos executados no PC do projeto
- `ResortR7FacadeFinish.Build`: PASS, **50 edifícios reais OSM, 50 estilos, 370 renderizadores, 370 materiais em URP/Lit, 40 mapas de textura, 0 fallbacks de semântica**.
- `ResortR7VisualCapture.Run`: PASS, **370/370 malhas com UV0**, 4 capturas reais 1600×900, pipeline **UniversalRenderPipelineAsset** ativo.
- FBX R7 foi exportado em Blender e reimportado; manifesto `R7_FBX_UV_NATIVE_QA.json` registra 50 formas OSM, 370 malhas, 9 categorias de acabamento.
- `R7_VisualNativeQA.json` guarda SHA256, dados da GPU, IDs OSM, vias de câmera e flags `artistic_gate_passed=false`, `fps_measured=false`.
- A geometria de origem GIS/FBX não foi sobrescrita.

## Resultado visual: **REPROVADO**
- `R7_01_art_deco_carioca_RealUnity.png`: fachada detalhada visível, porém entre volumetrias antigas dominantes e paisagem urbana inacabada.
- `R7_02_residencial_orla_RealUnity.png`: vários prédios detalhados aparecem; enorme quantidade de edifícios legados continua em massa branca ou cinza.
- `R7_03_hotel_contemporaneo_RealUnity.png`: hotel detalhado visualmente menor/oculto pelas massas brancas.
- `R7_04_Pedestrian_RealUnity.png`: câmera pedestre **totalmente obstruída por parede/volumes legados**, sem ver o objeto alvo.

**Consequência:** sucesso de importação PBR/UV0 não prova acabamento premium, navegação ou FPS. Não se deve mesclar como arte final.

## Prioridades abertas para Codex Sol 6.1
1. Correlacionar câmera/colisões com os footprints reais, escolher vistas pedestres válidas sem apagar edificações e expor o problema em QA.
2. Criar acabamentos/contexto coerentes para os 1.418 edifícios legados em lotes controlados após validar 50; substituir blocos brancos gradualmente, sem alterar ruas ou OSM.
3. Refinar a aparência e variação arquitetônica PBR, evidenciar claramente vidro, metal, pedra, esquadrias e janelas; validar em capturas autênticas.
4. Medir FPS e consumo no PC usando sessão de jogo real; QA `Camera.Render` estática não mede FPS de gameplay.
5. Manter gate de aprovação artística **false** até revisão de novos frames.

© OpenStreetMap contributors, ODbL 1.0.
