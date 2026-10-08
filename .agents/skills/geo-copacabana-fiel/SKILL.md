---
name: geo-copacabana-fiel
description: Preserve real Copacabana OSM geodata, metric geometry, Blender original and 2 km2 world bounds.
---

# Geografia autêntica da Copacabana

**Quando usar:** qualquer mudança no mapa, modelagem costeira, ruas, escala ou exportação GIS.

## Fonte da verdade
- `ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend` original read-only.
- `UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx` foi exportado da fonte.
- `geo/data/report.json`, `geo/data/roi.geojson`, `geo/data/copacabana.osm.gz`.
- Dimensões do recorte **2.000 × 1.000 m = 2 km²**; não interpretar como 2 × 2 km.
- O relatório marca 1.468 edifícios, 468 trechos de via e 563 pontos de árvores, que **não** significam 563 árvores 3D. 1.398 alturas são aproximação, não medições.

## Procedimento
1. Antes da alteração, registrar hashes SHA-256 do .blend e FBX e ler o relatório.
2. Para inserir terreno de relevo/DEM, validar a mesma CRS e origem; **não** mover ou recriar ruas/lotes para caber na arte.
3. Ler os eixos de importação e medir bounding box no Blender/Unity. Não adicionar uma segunda rotação de -90° no Unity ao FBX que já foi convertido.
4. Usar camadas aditivas para praia, calçadão, relevo e vegetação; preservar geografia original.
5. Provar que o limite do gameplay não cresceu silenciosamente; montanhas podem existir apenas como background fora do recorte.
6. Nunca baixar geodados inventando precisão. Salvar fonte, URL, data e licença.

## Critério de saída
- Modelos originais inalterados, ou alteração específica autorizada com diff/hashes.
- 2 km² e integridade do relatório verificados.
- Ruas e lotes continuam identificáveis e conectados.
- QA técnico registrado; não confundir fonte OSM com fotografia da cidade.

## Referências
- https://github.com/domlysz/BlenderGIS
- https://www.openstreetmap.org/copyright
- https://github.com/Unity-Technologies/skills
