# R1 — Copacabana Blender → Unity | relatório verificável

**Data:** 08/10/2026. **Branch:** `chatgpt/r1-unity-foundation`. **PR:** https://github.com/sergiomrge-tech/Resort-Simulator-/pull/5

## Fonte original já entregue ao projeto Unity
- Fonte geográfica: `ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend` (3.097.440 bytes).
- Malha FBX pronta para importação na Unity: `UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx` (665.388 bytes).
- Modelo de origem OpenStreetMap: 1.468 footprints de prédios, 468 trechos de vias, 563 pontos de árvores (pontos GIS, não árvores modeladas), com aproximadamente 2 km² de ROI no relatório.
- AABB **efetiva dos vértices no espaço de mundo do Blender**: 1832,8505 × 2071,2070 × 90 m. Esse bounding box não é equivalente à área de recorte GIS de 2 km²; não inferir que se trata de uma malha retangular de 2000 × 1000 m preenchida.
- `ArtSource/Blender/` e `UnityProject/Assets/ImportedBlender/` já estão no repositório. Não recriar Copacabana nem alterar a fonte.

## Teste de exportação geográfica executado e aprovado
**GitHub Actions:** https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37856310773

O workflow executou Blender **4.0.2**, carregou o arquivo `.blend`, reinicializou a cena e reimportou o FBX, comparando a geometria em coordenadas de mundo:

| Medida | Blender original | FBX reimportado |
|---|---:|---:|
| Objetos mesh | 1 | 1 |
| Vértices | 62.980 | 62.980 |
| Faces | 26.764 | 26.764 |
| Extensão X (m) | 1832,8505 | 1832,8503 |
| Extensão Y (m) | 2071,2070 | 2071,2066 |
| Extensão Z (m) | 90,0000 | 90,0002 |
| Materiais | Road / Building | Road / Building |

**Resultado:** PASS no Blender roundtrip; sem perda de vértices/faces, materiais ou escala mensurável acima de 0,5m. Relatório `Resort-R1-Blender-FBX-Roundtrip-QA` publicado como artifact no Actions, não é captura da Unity.

A revisão com os dois testes estáticos adicionais (materiais persistentes e QA Blender independente da licença) também passou no Actions https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37856350413.

## Código da cena Unity pronto para executar, mas NÃO executado
- `ResortWorldBuilder.cs`: referencia o **FBX real** da pasta ImportedBlender; instancia o prefab, mede os bounds, separa cores temporárias de ruas/prédios, constrói colisão estática, solo provisório e câmera de primeira pessoa.
- Materiais temporários agora persistem como assets `Assets/Materials/QA/*.mat` quando o Editor executar o gerador; tratam `_BaseColor` em URP Lit e `_Color` em Standard.
- `PlayerController.cs`: WASD, mouse, corrida, salto e gravidade; `DayNightCycle.cs`: relógio/sol.
- **Controle de inspeção programado:** F alterna caminhada com `CharacterController` e sobrevoo livre; no sobrevoo usar WASD e Q/E para subir/descer, Shift acelera; F12 solicita screenshot **do Unity em execução** em `Application.persistentDataPath/Captures` (não foi testado, nenhuma captura Unity existe por isso).
- O código do PlayerController e seus testes estáticos fazem parte da mesma PR; compilar e validar em runtime continuam pendentes.
- A cena `Assets/Scenes/Copacabana_Pilot.unity` **ainda será gerada** pelo Editor/Build. Sua existência não pode ser inferida do script C#.
- Os assets gerados (cena e materiais QA) foram incluídos no plano de artifacts do workflow de build quando habilitado.

## Bloqueios que impedem aprovação da R1
- **GameCI/Unity 6000.3.9f1 Windows job: SKIPPED, falta licença no runner**. Nunca declarar que scripts C# compilaram, que a cena foi renderizada ou que um EXE existe sem prova.
- PC remoto visto offline na consulta de 08/10/2026. O GitHub + Blender cloud continuam independentes do PC.
- URP package declarado no `manifest.json`; ainda falta configurar/verificar URP pipeline asset no Editor e validar materiais em runtime.
- Captura real Unity, colisões, referência geográfica e escala dentro da Unity, desempenho e build Windows **pendentes**.

## Próximo gate
1. Habilitar execução real do Editor Unity 6.3 em ambiente licenciado sem publicar segredos.
2. Rodar `ResortSimulator.Editor.ResortWorldBuilder.Generate` e `BuildWindows`; coletar logs, scene asset, QA materials, screenshot real e BuildReport.
3. Verificar orientação, medidas, entrada, colisões e performance; não aprovar a arte OSM como final.
4. Só então avançar R2: fachadas premium **realistas estilizadas** e texturas PBR sobre o mapa real, com piloto visual 300 × 300 m.

**Direção visual aprovada:** Realismo Estilizado Premium, sem low-poly aparente. © OpenStreetMap contributors, ODbL 1.0.
