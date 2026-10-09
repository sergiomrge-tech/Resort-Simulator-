# R4.1 — Gerador procedural 3D: biblioteca materializada de 50 estilos

**Execução real no Blender 4.5.14 / Cycles CPU — [GitHub Actions 37867377447](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37867377447) — SUCCESS.**

## Dados comprovados pelo relatório de geração

| Indicador | Valor |
|---|---:|
| Receitas autorais distintas **materializadas em modelos FBX reais** | **50/50** |
| Edifícios de exemplo obtidos de footprints OSM congelados | **50** |
| Polígonos criados pelo gerador | **577.770** |
| Módulos de janelas construídos | **9.389** |
| Módulos de sacadas construídos | **3.886** |
| Volume total de bytes FBX | **16.913.160 bytes** |
| Pranchas reais renderizadas no Blender Cycles | **5** |
| Resolução de cada prancha | **1.800 × 1.080 pixels** |
| Testes da galeria | **3/3 PASS** |
| Exceções/edifícios ignorados na galeria | **0** |

**O gerador não é mais apenas catálogo:** os 50 FBX foram escritos em `UnityProject/Assets/Architecture/R4_Procedural/FBX/`, cada um com `.fbx.meta` e GUID persistente, e estão versionados nesta branch. Os shaders de teste (Blender Principled BSDF) têm vidro, superfícies, metal e pedra, mas o ajuste final **URP da Unity ainda não foi realizado**.

## Prévia real da galeria (não mockup)

- [Prancha 1, fachadas 1–10](../../ArtSource/Previews/R4_Procedural_gallery_Sheet_01_Blender.png)
- [Prancha 2, fachadas 11–20](../../ArtSource/Previews/R4_Procedural_gallery_Sheet_02_Blender.png)
- [Prancha 3, fachadas 21–30](../../ArtSource/Previews/R4_Procedural_gallery_Sheet_03_Blender.png)
- [Prancha 4, fachadas 31–40](../../ArtSource/Previews/R4_Procedural_gallery_Sheet_04_Blender.png)
- [Prancha 5, fachadas 41–50](../../ArtSource/Previews/R4_Procedural_gallery_Sheet_05_Blender.png)

Arquivo de prova de geometria/arquivos SHA256: `UnityProject/Assets/Architecture/R4_Procedural/R4_GALLERY_GENERATION_REPORT.json`.

## Onde e como gerar os 1.468 edifícios do mapa

- `Tools/Blender/generate_r4_buildings.py`: gerador único com `pilot`, `gallery`, `city`. Integra contornos OSM locais, 50 receitas R4.0, geometrias trianguladas, sacadas e janelas estruturadas, material de fachada e hashes.
- `.github/workflows/r4-city-osm-batch.yml`: workflow manual `start` + `count` de 1–100 por execução, entrega os FBX num ZIP de GitHub Actions. Divide a cidade em lotes. **Não coloca prédios no mapa automaticamente**.
- `geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json`: associação de **todos os 1.468 prédios** reais do mapa, sem reembaralhar estilos entre execuções.
- Dois `way`s especiais já ocupados pela R3 são excluídos da substituição automática. Os lotes com footprint inviável exigem revisão e não são alterados à força.
- O mapa BlenderGIS original e os originais FBX têm SHA256 registrados para atestar ausência de alterações.

**Limites atuais:** os 50 modelos são arquétipos demonstrativos **baseados em footprints geográficos**, não uma reconstrução fotogramétrica dos prédios existentes. O destino urbano completo precisa preservar a malha de ruas e **remover a volumetria original do mesmo ID OSM** antes de criar a cópia com fachada nova, como já foi testado na R3. Também faltam auditoria artística em perspectiva de pedestre, ajuste de materiais URP, LOD e FPS, validação Unity nativa e build instalável. Não aprovar visual final nem alegar os 1.468 FBX prontos: esta etapa entregou a **biblioteca 50/50** e o **gerador de lotes**.

© OpenStreetMap contributors (ODbL 1.0) — dados geográficos. Modelagem e receitas de fachada: Project Resort.
