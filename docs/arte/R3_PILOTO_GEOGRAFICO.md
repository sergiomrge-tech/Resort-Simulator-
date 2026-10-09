# R3 — Piloto real de Copacabana, 300 × 300 metros

**Escopo:** estudar implantação visual em três edifícios reais da malha OpenStreetMap, sem reconstruir a cidade, alterar o FBX original ou inferir direitos de propriedade.

## Fonte geográfica

O recorte mantém os mesmos eixos e coordenadas da malha BlenderGIS existente:
- `geo/data/copacabana.osm.gz` — dados OSM congelados;
- `geo/pilot/COPACABANA_FRAME_SOURCE.json` — EPSG:32723, orientação da avenida e deslocamento métrico já usados na geração do mapa;
- `geo/pilot/R3_EXACT_OSM_PARCELS.json` — **três polígonos fechados reais** reprojetados do OSM, não lotes cadastrados/legalmente concedidos;
- `geo/pilot/R3_MODEL_FIT_STUDY.json` — compatibilidade dos modelos originais FBX e contornos OSM.

O [pipeline matemático de encaixe](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37862663423) executou com sucesso na nuvem. O teste verifica se os quatro cantos da volumetria de cada edifício ficam dentro do contorno e se suas arestas não cruzam a borda.

## Resultado do encaixe (estudo de geometria, não implantação)

| OSM Way | Contorno real | Modelo do acervo próprio | Encaixe com escala original |
|---|---:|---|---|
| `1048277518` | 479,37 m², 5 vértices | `hotel.fbx` | **Sim**, escala 1,00 e giro 165° |
| `1048277521` | 421,76 m², 4 vértices | `residencial_sacadas.fbx` | **Sim**, escala 1,00 e giro 90° |
| `1308635852` | 102,10 m², 7 vértices | `townhouse.fbx` | **Não** com margem adequada; **bloqueado** |

Os dois encaixes aprovados **não** autorizam inserir modelos diretamente na cena, pois já existe um prédio no mesmo local da malha BlenderGIS. Não foram usadas alturas reais, dados de matrícula ou promessas de construção. A altura no manifesto é apenas a dimensão original do FBX.

## Como evitar sobreposição/baixo nível visual

Foi criado `Tools/Blender/probe_r3_real_building_faces.py` para inspecionar a cobertura de faces da malha combinada da cidade sobre os três footprints. Esse diagnóstico deve demonstrar a presença de um edifício original antes de uma futura substituição.

- **Não** renderizar duas volumetrias uma sobre a outra como se fossem cenário definitivo.
- **Não** apagar indiscriminadamente faces do mapa; o próximo gate exigirá isolamento de componentes de edifícios e manutenção de todas as faces de vias.
- **Não** expandir/encolher construções arbitrariamente para caber em lotes pequenos.
- A direção de arte segue **Realismo Estilizado Premium**; os modelos autorais ainda precisam de inspeção de escala, shader, geometria e texturas na Unity.

## Evidência visual Blender

O arquivo `ArtSource/Previews/R3_Orla_300m_OSM_Real_Blender_QA.png` é gerado por `Tools/Blender/render_r3_real_osm_sites.py` com **geometria GIS real** e três contornos/etiquetas sobrepostos, sem prédios novos ou areia/mar fictícios. Ele é apenas diagnóstico de coordenadas, não imagem final do jogo.

O procedimento de renderização está em `.github/workflows/r3-visual-bpy.yml`; conferir o resultado real do Actions antes de declarar a captura aprovada. A origem original `ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend` e `UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx` nunca devem ser sobrescritas.

## Próxima fase R3

1. Inspecionar o diagnóstico de componentes conexos do mesh GIS para os dois candidatos viáveis.
2. Só após prova de seleção isolada, gerar um **asset derivado** de cenário piloto e inserir edifícios autorais, mantendo a origem intacta.
3. Integrar URP e validar o resultado em um **Editor Unity de verdade** (incluindo screenshot genuíno e logs), quando GitHub Actions tiver credenciais de ativação Unity válidas.
4. Refinar quiosque, hotel, revestimentos, calçadão, areia, praia e vegetação sem sacrificar geografia e FPS.
5. Sistemas de vendas, estoque, filas e IA de clientes seguem arquivados em `docs/backlog/fase2-quiosque/`.

© OpenStreetMap contributors — ODbL 1.0.
