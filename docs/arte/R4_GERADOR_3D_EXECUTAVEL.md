# Project Resort R4 — Gerador procedural 3D de Copacabana

**Código-fonte executável:** `Tools/Blender/generate_r4_buildings.py`

O R4 cria geometria real no Blender 4.5+: paredes seguindo os **polígonos OSM congelados**, fachadas com janelas, vidro, molduras, peitoris, portas, marquises, sacadas com estrutura e guarda-corpos, cornijas e elementos de cobertura. Exporta **FBX binário** para `UnityProject/Assets/Architecture/R4_Procedural/FBX/`, com UUID/GUID estável de Unity e manifesto JSON com posição geográfica, origem de altura e hash do modelo. O modo piloto também gera uma imagem **real de Blender**.

## Como executar

```bash
# Instale o Blender Python 4.5 no ambiente de teste.
python -m pip install "bpy>=4.3,<5" pillow

# Dez prédios diferentes (um representante de cada família)
python -c "import bpy,runpy,sys;sys.argv=['blender','--','--mode','pilot'];runpy.run_path('Tools/Blender/generate_r4_buildings.py',run_name='__main__')"

# Galeria de 50 receitas arquitetônicas materializadas em 50 FBX
python -c "import bpy,runpy,sys;sys.argv=['blender','--','--mode','gallery'];runpy.run_path('Tools/Blender/generate_r4_buildings.py',run_name='__main__')"

# Gerar edifícios do mapa em lotes pequenos sem renderizações adicionais
python -c "import bpy,runpy,sys;sys.argv=['blender','--','--mode','city','--start','0','--count','50','--no-render'];runpy.run_path('Tools/Blender/generate_r4_buildings.py',run_name='__main__')"
```

Alternativamente, o Blender instalado pode executar `blender --background --factory-startup --python Tools/Blender/generate_r4_buildings.py -- --mode pilot`.

## Saídas, integridade e limitações

- Os FBX são **centrados na origem do próprio edifício**. Reposicione usando `local_osm_centroid_xy_m` do relatório e a transformação existente em `geo/procedural/R4_SOURCE_FRAME.json`. **Não** posicionar no mundo sem validar e remover a massa original do mesmo prédio. O BlenderGIS tem rotação de 46° no objeto original.
- A receita `style_id` é persistente por ID OSM e seed, independente de reiniciar o gerador.
- `--mode pilot`: escolhe dez footprints viáveis, um por família, preserva os usos OSM como *indicações*, nunca como prova de atividade comercial.
- `--mode gallery`: exemplifica todas as **50 receitas**, cada uma sobre um footprint OSM real compatível, com hasta cinco pranchas de referência.
- `--mode city --start N --count X`: processa **1–100 edifícios por lote**, inclui os 1.468 IDs originais; dois edifícios especiais de R3 ficam reservados, sem substituição automática. Contornos estreitos incompatíveis são assinalados como `requires_manual_review`, não distorcidos artificialmente.
- `--no-render`: reduz tempo para geração em lotes de cidade.
- As texturas são propriedades PBR/procedurais de materiais Blender; os parâmetros *não equivalem* a materiais Unity URP testados. O visual ainda requer imagens reais no Unity.
- As alturas OSM explícitas (14) são distintas das estimadas por andares (56) e dos 1.398 valores de visualização sem medição; o gerador não inventa altura cadastrada.
- Cornijas e guarda-corpos têm espessura geométrica. Sacadas são essencialmente reentrantes para minimizar invasão de calçada; ainda **não há um gate de colisão tridimensional com ruas**.
- A iluminação, bases e rótulos da galeria são **apenas elementos da prancha Blender** e não são incluídos nos FBX.
- `Assets/ImportedBlender/Copacabana_Real_Blender.fbx` e a origem `ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend` são somente leitura.

## Gates de aprovação

1. Executar e testar o piloto de dez edifícios e inspecionar a prévia real.
2. Gerar, comparar e aprovar cinco pranchas das 50 receitas antes de preencher os lotes.
3. Verificar importação/quantidade de triângulos na Unity, materiais URP, distância de LOD e velocidade.
4. Só depois gerar o bairro com os edifícios antigos removidos pelo processo derivado seguro de R3 e sem sobreposição.
5. Nenhuma etapa cria economia, filas ou NPCs: continuam arquivados para depois da fase visual.

A fonte geográfica utiliza © OpenStreetMap contributors (ODbL 1.0). A geometria e receitas de fachada são de autoria do Project Resort.
