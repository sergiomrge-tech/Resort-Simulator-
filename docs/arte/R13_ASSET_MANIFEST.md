# R13 — autoria, licença e fontes

| Conteúdo | Autor / fonte | Direitos / localização |
|---|---|---|
| Costa, footprints e frame | © OpenStreetMap contributors, snapshot local preservado | ODbL 1.0, https://www.openstreetmap.org/copyright ; `geo/data/copacabana.osm.gz`, frame/assignments em `geo/procedural` |
| Mosaico, areia, calcário, madeira | Arte procedural original criada para Project Resort, seed 13061 | Sem imagens, modelos ou packs externos; código e PNG em `Tools/geo/generate_r13_surface_art.py` e `UnityProject/Assets/Textures/R13_Coastal` |
| Bancos, jardineiras, plantas de folhas curvas, lixeiras, paraciclos, frisos de fachada | Geometria autoral gerada em Blender | `Tools/Blender/generate_r13_coastal_slice.py`; fonte `.blend` em `ArtSource/Blender`, FBX em `UnityProject/Assets/Architecture/R13_Coastal` |
| Shader de mar, integração e capturador | Código autoral para URP | `UnityProject/Assets/Shaders/R13_ShoreOcean.shader`, `Assets/Editor/ResortR13*.cs` |
| Letreiros, vidro e árvores anteriores | R7–R12, manifestos anteriores | Reutilizados pela cena-base, sem novas marcas ou downloads |

Não foram comprados ou baixados assets visuais. Os hashes dos 12 mapas estão em `R13_SURFACE_ART.json`; os hashes GIS/FBX e IDs OSM estão em `R13_COVERAGE.json`. Data de geração: 09/10/2026. Plantas adicionais são ambientação ficcional, não árvores OSM novas. Fonte geográfica original e FBX original permanecem intactos.

Os mapas seguem BaseColor sRGB, normal tangent linear e mapa RGBA com metallic no vermelho (zero para superfícies dielétricas) e smoothness no alpha. O material Unity importa os canais separadamente, usa mipmaps e escala UV em metros. A qualidade final é pendente; autoria própria não certifica realismo fotográfico.
