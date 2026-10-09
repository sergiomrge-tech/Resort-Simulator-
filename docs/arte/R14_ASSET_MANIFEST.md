# R14 — autoria, licenças e inventário

Data: 09/10/2026. Conteúdo autoral Project Resort criado proceduralmente nesta
sessão para o proprietário. Uso comercial no projeto; sem imagens/modelos/packs
de terceiros. Plantio decorativo e quiosques são ficcionais e não representam
estabelecimentos, espécies ou equipamentos medidos em Copacabana.

| Conteúdo criado | Fonte | Evidência |
|---|---|---|
| Guias de 14 cm, sarjetas e calçadas sólidas | `generate_r14_urban_connectors.py`, união dos triângulos GIS originais | 31 meshes, 381.594 triângulos; FBX e `.blend` próprios R14 |
| Mobiliário / palmeiras / quiosques | `generate_r14_coastal_art.py`, seed 14061+setor | 49 grupos urbanos, 12 palmeiras, sete quiosques em três variantes |
| Trims de fachada | Mesma regra de janela R8, IDs OSM persistentes | 37 fachadas de fundo; piloto R7 excluído por lattice diferente; sem novos vidros transparentes |
| Arte PBR | `generate_r14_surface_art.py` | 24 PNGs originais, oito famílias × base/normal/mask, 1024², repetição 2×2 m |
| Builder/capturador Unity | `ResortR14UrbanFinish.cs`, `ResortR14UrbanCapture.cs` | Cena derivada própria; captura exige frame real URP |

Famílias PBR: Asphalt, Sidewalk, Curbstone, Gutter, StoneTile, Timber, Foliage,
Granite. Base sRGB; normal tangent linear; mask linear com metallic em R=0,
AO em G=1 e smoothness plausível em A. Mips, textureShape 1, importador completo
v13 e GUIDs determinísticos. FBX globalScale 1 / useFileUnits 1.

Hashes dos PNGs em `R14_SURFACE_ART.json`; hashes dos FBX, meshes, material slots,
bounds por setor e originais em `R14_CONNECTORS_NATIVE.json` / `R14_ART_NATIVE.json`.
O censo de arte inclui três LODs reais por batch material/setor, sem um objeto
para cada folha/junta. Os conectores preservam a borda sem decimation de LOD;
otimização de LOD/culling para esses sólidos ainda pendente de profiler.

Fonte cartográfica: © OpenStreetMap contributors, [ODbL 1.0](https://www.openstreetmap.org/copyright).
Snapshot local, EPSG:32723, 46°, 1.468 footprints, 3.731 triângulos viários e
48 posições de árvores preservados por SHA-256. Shapely/GEOS e Blender são
ferramentas de geração, não modelos/texturas externos incorporados ao jogo.

Referências técnicas: [API Blender](https://docs.blender.org/api/main/mathutils.geometry.html)
e [escala de importação Unity](https://docs.unity3d.com/cn/6000.0/ScriptReference/ModelImporter-globalScale.html).
Nenhuma imagem de satélite, Google, marca comercial, licença Unity ou segredo
foi incluído. Qualidade premium depende de aprovação do diretor.
