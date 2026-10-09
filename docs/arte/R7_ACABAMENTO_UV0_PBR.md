# R7 — UV0, semântica FBX e acabamento dos 50 edifícios reais

**Estado deste checkout:** código e gates preparados; render Blender R7 e execução nativa Unity ainda pendentes. O gate artístico permanece **REPROVADO/PENDENTE**, seguindo a reprovação visual R6. Nenhuma captura sintética foi criada.

## Causa encontrada

- `generate_r4_buildings.py` criava submalhas separadas por classe de material, mas não escrevia UV maps. O FBX resultante, portanto, não tinha UV0 utilizável para texturas.
- A classificação por nomes longos de objeto/material podia ser truncada no FBX. R6 observou 370 nomes/classificações perdidos.
- `ResortR6FacadeFinish.Build` substituía cada slot pelo mesmo material de acabamento. Isso apagava as categorias existentes por submalha e usava inferência de material R5 como fallback.
- A presença do pacote URP não significava que havia um Render Pipeline Asset ativo; R6 capturou com Standard.

## Mudanças R7

- `Tools/Blender/generate_r7_buildings.py` é um gerador independente com saída `UnityProject/Assets/Architecture/R7_Pilot50/`. Calcula UVs por face com projeção pelo eixo dominante, `UVMap` e escala de 2 metros por repetição. Cria IDs curtos com semântica no nome dos materiais (`R7_<família>_<variante>_<categoria>`) e propriedades informativas no objeto. Mantém nove classes: parede, pedra, ornamento, vidro, metal, madeira, cobertura, plantas e sombra.
- `Tools/geo/r7_mask_city_50.py` e `Tools/Blender/assemble_r7_city_50.py` geram a máscara e a cena/FBX derivados em caminhos R7 próprios. Mantêm os 50 IDs OSM reais, verificam hashes das fontes originais, triângulos não selecionados, 3.731 faces de rua, footprint, frame GIS e rotação de 46°. Não substituem FBX/cena R5 nem as fontes originais.
- `ResortR7FacadeFinish.Build` abre o FBX derivado R7 numa cena independente. Procura um URP asset no projeto QA; se não houver, tenta criá-lo pelo menu oficial “URP Asset (with Universal Renderer)” dentro do projeto QA e o define para Graphics e nível de qualidade ativo. Falha se asset/shader `Universal Render Pipeline/Lit` não ficarem ativos. Exige UV0 em cada renderer dos 50 edifícios e ID semântico consistente em cada slot; nunca usa Standard nem fallback de categoria. Albedo procedural foi escurecido, com normal/PBR; vidro usa superfície transparente; volume da cena usa ACES e `postExposure=-0.25`. Isso ainda exige inspeção visual real.
- `ResortR7VisualCapture.Run` só captura se UV0 existir em todos os renderizadores arquitetônicos e URP estiver ativo; reporta que a aprovação artística continua pendente e não mede FPS.
- `Tools/geo/r7_expansion_plan.py` organiza os 1.418 footprints reais restantes em lotes determinísticos de até 50, com IDs, estilos, footprints e provenance de altura. O plano não materializa os lotes.
- `Tools/tests/test_r7_uv_pbr_pipeline.py` cobre a origem dos UVs, IDs/slots, bloqueios Unity, separação R5/R7, paridade de ruas e contagem 1.468/50/1.418. `.github/workflows/r7-uv-pbr-pilot.yml` contém QA estático e execução Blender real no Actions, com upload de FBX, relatório e render.

## Execução reproduzível

No runner Blender do workflow, em sequência:

```text
python -c "import bpy,sys,runpy;sys.argv=['blender','--','--mode','gallery'];runpy.run_path('Tools/Blender/generate_r7_buildings.py',run_name='__main__')"
python Tools/geo/r7_mask_city_50.py
python -c "import bpy,runpy;runpy.run_path('Tools/Blender/assemble_r7_city_50.py',run_name='__main__')"
python Tools/geo/r7_expansion_plan.py
```

Com os artefatos Blender R7 disponíveis em `D:\ProjectResort_R5_UnityQA\UnityProject` por transferência do supervisor, execute com Editor/licença real:

```text
Unity.exe -batchmode -quit -projectPath D:\ProjectResort_R5_UnityQA\UnityProject -executeMethod ResortR7FacadeFinish.Build -logFile D:\ProjectResort_R5_UnityQA\R7_Build.log
Unity.exe -batchmode -quit -projectPath D:\ProjectResort_R5_UnityQA\UnityProject -executeMethod ResortR7VisualCapture.Run -logFile D:\ProjectResort_R5_UnityQA\R7_Capture.log
```

O primeiro método exige `Assets/Architecture/R7_Pilot50/R7_Copacabana_50_Fachadas_Derivado.fbx`; o segundo gera capturas reais Unity após o primeiro. Sem Editor URP/ativo e licença, resultado é `NOT_RUN`, não aprovação. Não execute esses comandos em outra pasta sem autorização do supervisor.

## Estado nativo e limitações

- Hashes observados antes da mudança: `.blend` original `2384c677bbb2ef8ef6275cb567ec52e69ff4b9e55d204d76eb0b10dfde2e4ac4`; FBX original `2546ad26546713d40008c395a1a0d00eb2a3f90c1681f0bbbe3ad2c5410d9339`.
- Blender executável não está disponível neste ambiente. Unity não foi executada nesta sessão e não existem logs que comprovem compilação/execução. Não foi gerado FBX R7, render Blender R7, cena Unity R7, print Unity nem medição de FPS.
- A cena Unity produzida pelo código R7 é baseada no FBX de cidade derivada, não na cena R5; isso permite conferir as meshes novas sem editar a cena R5.
- O manifesto versionado lista os 1.418 remanescentes usando a máscara R5 já validada como baseline; a etapa Blender R7 recalcula e grava sua própria máscara R7 antes de o workflow regenerar esse manifesto.
- Relatório/família de expansão depende do resultado real do mask/Blender R7. Nenhum dos 1.418 remanescentes foi aplicado ao mapa.
- Nenhum gate visual foi autoaprovado. A revisão de colisões, diversidade percebida, transparência, exposição, performance e capturas reais ainda precisa ocorrer.
- O checkout não pode gravar fora do workspace gerenciado. Assim, `D:\CodexTemp\codex_r7_acabamento_resultado.txt` não foi criado; este documento no repositório contém o relatório desta sessão.

© OpenStreetMap contributors — ODbL 1.0: https://www.openstreetmap.org/copyright.
