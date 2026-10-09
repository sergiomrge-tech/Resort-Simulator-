# R4.0 — Catálogo de 50 fachadas e distribuição OSM confirmados

**Resultado verificado no GitHub Actions [37866087509](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37866087509): SUCESSO.** A auditoria executou o gerador, 3 testes Python e uma segunda execução para comparar o hash SHA256 do arquivo gerado.

| Medida | Resultado |
|---|---:|
| Famílias arquitetônicas | **10** |
| Variações por família | **5** |
| **Receitas de fachadas distintas** | **50** |
| **Edifícios reais do mapa OSM associados** | **1.468** |
| Variações diferentes efetivamente atribuídas | **50** |
| Alturas informadas diretamente pelo OSM | **14** |
| Alturas calculadas por número de andares no OSM | **56** |
| Alturas **estimadas, não levantadas** | **1.398** |
| Outras construções do snapshot OSM excluídas por estarem fora do ROI original | **1.131** |

A ROI reproduz o quadro **EPSG:32723 / 46° / 2 km de extensão × 1 km de profundidade**, idêntico à fonte geográfica atual; **não** se confunde com eventual objetivo futuro de 2 × 2 km. Formato exportado em `geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json`: lista classificada por OSM ID, geometria fechada do footprint local já recortada na ROI, seed estável, visual style ID, distância aproximada à Avenida Atlântica, origem de altura, sinalização de `has_final_generated_mesh: false`.

O planejador preserva localização e identidade do edifício e pode ser reexecutado quantas vezes necessário sem embaralhar fachadas. Usar etiquetas `OSM_USE_HINT` ou `UNVERIFIED_VISUAL_STYLE_ONLY`: um hotel aparente não é prova de que o prédio tenha uso real hoteleiro.

## O que existe hoje e o que não existe

- **Existe:** cinquenta fichas autorais com composição de janelas, tipo e profundidade da sacada, entrada, coroamento, telhado, cor/paleta, molduras, relevos e fachada térrea; mapeamento completo dos edifícios OSM; teste automatizado offline; planejamento de geração em `docs/arte/R4_GERADOR_PROCEDURAL_50_ESTILOS.md`.
- **Ainda não existe:** cinquenta FBX novos, 1.468 prédios com novas fachadas na cena, PBR validado em Unity, LOD em runtime, teste de FPS em mundo aberto ou aprovação artística. As imagens atuais do jogo não foram alteradas pelo R4.0.

## Próximo passo de produção

Construir um protótipo real Blender de **10 edificações** com footprints e IDs OSM, renderizar fachadas em perspectiva da rua, comparar detalhes e acabamento premium. Só então expandir para as 50 receitas e bairros inteiros; geração com qualidade implica geometria de peitoris/sacadas, materiais PBR, instancing, LOD e inspeções visuais reais. O processo de implantação por lotes precisa da mesma garantia R3 de nunca duplicar um prédio antigo.

Fontes verificáveis:
- [Receitas R4.0](../../ArtSource/ProceduralBuildings/Resort50Styles.json)
- [Mapeamento OSM R4.0](../../geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json)
- [Pipeline automatizado](../../Tools/geo/assign_r4_city_styles.py)
- [Testes](../../Tools/tests/test_r4_procedural_styles.py)

© OpenStreetMap contributors (ODbL 1.0) — dados; regras estilísticas: autoria Project Resort.
