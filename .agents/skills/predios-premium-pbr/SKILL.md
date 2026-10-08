---
name: predios-premium-pbr
description: Create distinct realistic Copacabana architecture with modular facades, commercial-use PBR materials and visual acceptance gates.
---

# Fachadas reais e arquitetura premium

**Quando usar:** substituir edifícios de referência por construções realistas no trecho aprovado.

## Regra primordial
A extrusão OSM define volumes/lotes; não é arquitetura final. A fachada **não** move a rua, não sobrepõe lotes alheios, não inventa altura exata onde a fonte diz «estimada». Fazer o primeiro lote **apenas 3 edifícios visivelmente distintos** antes de escalar.

## Processo
1. Selecionar lotes apenas após confirmação da localização do piloto 300 × 300 m. Documentar OSM IDs/origem, afastamentos, acesso e relações com a via.
2. Escolher 3 tipologias divergentes: por exemplo art déco, torre moderna com varandas, hotel litorâneo contemporâneo; não usar repetição de janelas como «diversidade».
3. Criar kit modular: módulos de 1 pavimento, janelas com profundidade, sacadas, recuos, marquises, entradas térreas, coberturas, caixilhos, fachadas de esquina e sinais fictícios.
4. Usar PBR real `albedo/baseColor`, `normal`, `metallic`, `roughness/smoothness` convertido corretamente para pipeline, `AO`; medir proporções de texel, escala física e variações.
5. Materiais preferenciais CC0: Poly Haven e ambientCG. Para Unity Asset Store, verificar a licença específica e condições de distribuição **antes** de versionar.
6. Câmeras padronizadas ao nível da rua, oblíqua 45° e aérea para comprovar diferença entre edifícios.
7. Criar materiais e prefabs em `UnityProject/Assets/Art/Architecture/`; um catálogo permanente em `docs/arte/` com IDs estáveis.
8. Antes de replicar, exigir visual aprovado; modelagem volumétrica blockout não equivale a aprovação.

## Critério de saída
- 3 fachadas realmente diferentes, geografia preservada, materiais/procedência registradas.
- Com cena executável, screenshots Unity verdadeiras; caso contrário reportar «pendente de renderização».

## Referências
- https://polyhaven.com/license
- https://ambientcg.com/
- https://assetstore.unity.com/browse/eula-faq
