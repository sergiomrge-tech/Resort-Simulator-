# Vegetação R6 de Copacabana — gerador e piloto

## Escopo e fonte

O gerador usa somente o snapshot `geo/data/copacabana.osm.gz`, o frame imutável `geo/procedural/R4_SOURCE_FRAME.json` e o relatório OSM existente. A área continua em **2.000 × 1.000 m (2 km²)**, EPSG:32723, com o eixo costeiro girado exatamente **46° anti-horário a partir do leste**. O BlenderGIS original e o FBX importado são tratados como fontes protegidas; este trabalho não os abre para escrita nem modifica geometria urbana.

`Tools/geo/generate_r6_vegetation.py` lê nós OSM `natural=tree`, transforma os pares longitude/latitude no mesmo frame métrico e elimina pontos fora da ROI, árvores dentro de edifícios disponíveis, áreas OSM marcadas como areia/água e árvores dentro do envelope viário. A largura de via OSM é usada quando tagueada; quando falta, o gerador aplica uma estimativa conservadora conforme a classe `highway` e mais 0,75 m além da borda estimada. Onde existe linha costeira explícita, aplica afastamento mínimo de 8 m. Em seguida, seleciona até 48 pontos espalhados deterministicamente por amostragem de maior distância, com separação mínima de 3 m. A posição é sempre um nó OSM real; a orientação e as variações de kit usam uma semente estável derivada do ID do nó.

O piloto versionado fica em `geo/procedural/R6_VEGETATION_INSTANCES.json`. Nesta fonte há 632 nós de árvores no XML completo, dos quais 563 caem no retângulo correto; os restantes ficam fora. Na geração atual, 446 posições passaram os guardas GIS antes da amostragem de 48. O JSON informa as recusas, categoria por relação espacial a áreas verdes/vias, espécie atribuída, coordenadas geográficas e locais, semente, origem e distâncias calculadas.

## Kit 3D autoral

`Tools/Blender/generate_r6_vegetation_kit.py` produz quatro modelos próprios: palmeira de tronco curvo e folhas pinadas em lâminas curvas, duas árvores tropicais de copa orgânica e tronco ramificado, e arbusto tropical. Os meshes são compostos por tubos afunilados e superfícies de folhas criados por Python, com materiais autorais em nós Principled. Cada espécie tem LOD0, LOD1 e LOD2. O pacote reúne os níveis por espécie em quatro FBX binários, sem gerar centenas de clones, e guarda o projeto editável `.blend`, manifesto com faces/vértices e hashes e uma renderização QA real do Blender.

Os pontos do snapshot não identificam palmeiras ou espécies botânicas. Como nenhum dos pontos tem tags de espécie/gênero no recorte que entrou no piloto, o gerador atribuiu as duas variantes de árvore tropical de forma estável; a palmeira continua disponível como modelo autoral no kit, sem inventar ocorrências no mapa. Os arbustos também são ativos do kit, não plantações inseridas em coordenadas arbitrárias.

## Dados incompletos e limites

- Guardas viários usam as linhas centrais disponíveis. OSM não traz largura medida de pista, limite de meio-fio, polígono completo de calçada, canteiro de árvore ou redes subterrâneas neste processamento.
- Edifícios são polígonos de ways fechadas `building=*`; relações multipolygon e footprints ausentes/incompletos não são reconstruídos.
- Areia, água e vegetação usam somente polígonos OSM fechados com tags compatíveis. A cobertura não é completa e não há DEM para verificar cota, substrato, inundação ou contato da copa com redes.
- Uma classificação como “calçada ou lote” não comprova domínio público nem canteiro. A posição OSM também pode representar o centro aproximado do tronco, sem levantamento topográfico.
- O modelo de palmeira ou broadleaf do kit não determina espécie real. Variação de yaw é gráfica, pois o OSM não codifica orientação do tronco.
- FBX/blend e render são gerados pelo workflow dedicado em Blender headless. Este ambiente não tem Blender nem o pacote `bpy`, então resultados binários/render devem ser lidos do workflow e manifesto, não presumidos localmente.
- Unity LODGroup, importação de materiais, colisão, FPS e memória permanecem pendentes de Editor/build licenciados. Nenhum render Blender é uma captura Unity.

## Reprodução e validação

```powershell
python Tools/geo/generate_r6_vegetation.py --pilot-count 48
python -m unittest discover -s Tools/tests -p "test_r6_vegetation_*.py" -v
```

Com Blender Python `bpy` disponível, executar `Tools/Blender/generate_r6_vegetation_kit.py`. O workflow `.github/workflows/r6-vegetacao-osm-copacabana.yml` executa a geração real e os testes da estrutura/FBX/render, publica os artefatos da execução e versiona o kit gerado somente na branch dedicada `codex/vegetacao-osm-copacabana-r6`.

Dados OSM © OpenStreetMap contributors, ODbL 1.0: https://www.openstreetmap.org/copyright
