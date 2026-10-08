# Origem do mapa real — importação do Blender

Usar exclusivamente o mapa georreferenciado que já foi construído a partir dos dados OpenStreetMap de Copacabana em 08/10/2026. A fonte original foi `Tools/Copacabana/data/Copacabana_BlenderGIS_UTM23S.blend` na branch `codex/copacabana-osm-real-20261008` do repositório anterior, que não é fonte de código do Resort.

O workflow `mapa_blender_para_unity.yml` copia uma única vez a fonte existente para `ArtSource/Blender/`, preserva o relatório GIS e exporta automaticamente o FBX no diretório `UnityProject/Assets/ImportedBlender/`. Não recriar, randomizar, substituir ou gerar nova malha sobre os edifícios originais.

Geografia: recorte 2000 × 1000 metros (2 km²), 1468 edifícios, 468 trechos de vias e 563 árvores identificadas como nós OSM. A malha existente é **blockout geográfico real**, mas 1398 alturas foram arbitradas para visualização; a densidade está correta conforme fonte mapeada, a aparência final e relevo não. O mapa 3D não contém todas as 563 árvores; são pontos nos dados GIS.

Depois da exportação validar dentro do Unity (versão do projeto): renderizadores, escala 1m, eixos georreferenciados; registrar prints **reais**. Blender exporta FBX com conversão de Z-up para Y-up, portanto **não rodar -90° na Unity**. GitHub Actions não valida Unity sem licença adequada.

© OpenStreetMap contributors — ODbL 1.0 https://www.openstreetmap.org/copyright
