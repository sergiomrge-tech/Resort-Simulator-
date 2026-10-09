# Project Resort — R11: volumetria arquitetônica geográfica, QA (09/10/2026)

## Escopo não negociável
O mapa segue **2.000 metros paralelos à orla × 1.000 metros rumo ao interior**. Nenhum edifício, rua, árvore ou calçadão do OSM mudou de posição. A R11 é um overlay volumétrico **acima do chão** aplicado em uma nova cena isolada, derivada da R10. Mantém os 50 edifícios R7, os 1.418 detalhados da R8, a vegetação R9, o mar e mosaico R10.

## Gerador real de arquitetura
`Tools/Blender/generate_r11_architectural_detail.py`: lê anéis e alturas da fonte geográfica real, preserva a orientação CW e produz complementos artísticos por edifício e estilo, com IDs determinísticos. Os 50 estilos originais ganham saliências e estruturas, sem depender de posição inventada de lotes.

- **6.048 varandas** em **888 edifícios**: alinhadas exatamente à grade original de janelas R8; lajes projetadas **0,58 a 0,74 m** no nível elevado, vigas/suportes inferiores e guarda-corpos de metal ou vidro conforme família arquitetônica. Não confundir com varanda mapeada/surveyed de prédio específico.
- **1.414 volumes de cobertura** (estruturas técnicas internas ao polígono, alturas variáveis), **569 unidades de manutenção** e **1.355 cornijas** em fachadas Art Déco/clássicas/residenciais. Essas estruturas são aproximações, não são equipamentos verificados in loco.
- **210 meshes organizadas por estilo/material**: 306.180 faces adicionais, 50 famílias de acabamento, UV0 real. Os componentes extras **reutilizam URP/Lit** com materiais R10/R7 em vez de apresentar objetos brancos sem shader.
- Fonte arquivada: `geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json`; cores/fachadas originais mantidas. As posições OSM originais não são reescritas.
- Regra de perspectiva: profundidade e suporte das varandas alinhados aos vãos, não grades soltas no pano cego (problema detectado e corrigido após as primeiras capturas).

## Validação — testes executados, não inferidos
- Blender 5.2.1 (real): exportou FBX R11 de 13.527.260 bytes, com 210 meshes e 306.180 faces; reimportação nativa `Tools/tests/test_r11_architecture_native.py` aprovada, material e UV finitos, sem alteração do hash original R8.
- Unity 6000.6.2f1 / NVIDIA RTX 4060 Ti / Direct3D11: `ResortR11ArchitectureFinish.Build` aprovou 210 renderers, **0 shaders inválidos, 0 UV0 faltantes**, 50 estilos. Preservou 3.731 triângulos GIS de ruas e 48 árvores da R9. Nova cena `Assets/Scenes/R11_Copacabana_Arquitetura_Volumetrica.unity`, sem gravar sobre a R10.
- **7 capturas 1600×900 reais da Unity**: `ArtSource/Previews/R11_01..07_*_RealUnity.png`. As fotos 06 e 07 mostram varandas/coberturas em escala próxima. Não são conceitos ou capturas sintetizadas. Metadados de GPU, ângulo de câmera e hash verificáveis em `R11_VisualNativeQA.json`; `test_r11_capture_integrity.py` compara bytes dos PNG.
- O gate de imagem R10 contra a cidade preta permanece ativo na R11 (real renderização com aquecimento do URP, média de luminância >68, fração preta <10% no enquadramento fixo). Não é medição de FPS.

## Limites de qualidade — **revisão artística obrigatória**
**ART GATE = PENDENTE**. A imagem de perto melhorou (varanda alinhada à janela, suporte/volume visíveis), mas fachadas continuam muito repetitivas, falta textura de alta definição mais rica, caixilharia detalhada, variação volumétrica em edifícios icônicos, muros/entradas e iluminação física mais profunda. O uso do termo arquitetura premium é *alvo*, não aprovação estética. Sem previsão de APK/EXE jogável nem FPS até profiling real.

## GitHub-first (não depende do PC ligado)
Workflow `.github/workflows/r11-architecture-volumetry.yml` recompõe toda a cadeia R7→R8→R9→R10→R11 com Blender real + testes dos artefatos; novo FBX R11 e relatórios são artefatos da action e não necessidade de upload binário pesado para cada commit. O Windows Unity testado é somente QA local, e a infraestrutura de compilação visual ainda depende de PC/runner com Editor Unity quando solicitada.

Dados OSM © OpenStreetMap contributors (ODbL 1.0); complemento arquitetônico é gerado proceduralmente, não prova de arquitetura real cadastrada.
