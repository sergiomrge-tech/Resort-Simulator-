# Art Bible — Copacabana / Resort Simulator

## Padrão aprovado em 08/10/2026 — Realismo Estilizado Premium

**Direção oficial para todos os assets finais:** realismo estilizado premium (semi-realista), adequado a um simulador de resort comercial para PC/Steam. Este estilo substitui a meta de fotorrealismo absoluto, **não** a exigência de qualidade. Não usar low-poly aparente, estética cartoon, aparência plástica nem cubos OSM como prédios definitivos.

- **Geografia preservada:** a fonte Copacabana BlenderGIS/OSM existente fica intacta; os footprints originais, posições de vias e a escala métrica não são substituídos por arruamentos inventados. O recorte documentado da fonte é **2.000 × 1.000 m (2 km²)**, diferente de 2 × 2 km.
- **Prédios:** silhuetas e alturas compatíveis com a fonte; janelas, sacadas, molduras, portas, gradis, marquises e coberturas em módulos arquitetônicos detalhados com variedade observável entre quarteirões.
- **Materiais:** PBR bem calibrados (albedo, metalness, roughness/smoothness, normal maps e ambient occlusion quando apropriado), variação de fachadas, atlas/trim sheets e decals; sem textura genérica única.
- **Orla:** praia, mar, calçadão de pedras portuguesas, quiosques, mobiliário, postes, drenagem, asfalto e calçadas com materiais reconhecíveis; não permitir vazios cinzas ou ruas desconectadas.
- **Natureza e iluminação:** árvores e palmeiras volumosas, vegetação tropical coerente e sombra estável; oceano estilizado fisicamente plausível, horário solar quente, reflexos controlados e boa legibilidade dia/noite.
- **Performance:** geometria detalhada perto do jogador, LODs e impostors à distância, culling/streaming em setores, materiais compartilhados e técnicas de instancing/batching escolhidas após profiling real na Unity. Estilização não significa apenas diminuir polígonos.
- **Validação visual:** fotografia e concept art podem inspirar a direção, mas só screenshots genuínos da Unity contam para aprovar visual de gameplay. A preview do Blender é QA de geometria, não arte final nem screenshot da Unity.

**Ordem de execução:** R1 importar e inspecionar o FBX real na Unity; R2 provar ao menos três fachadas distintas dentro da cena real; R3 validar piloto de orla/resort 300 × 300 m; só então expandir produção e gameplay.

## Direção obrigatória

- Jogo de gestão de resort **original**, cidade brasileira costeira com distribuição geográfica baseada em Copacabana, não cópia visual de obras de terceiros.
- Footprint de gameplay **2,0 km²**, sem ampliar com distritos repetidos. Relevo exterior e montanhas são background visual, detalhados por distância.
- Densidade verdadeira de quarteirões e ruas, como Avenida Atlântica, Nossa Senhora de Copacabana e Barata Ribeiro.
- Não existem grandes campos cinza nem quarteirões urbanos com buracos injustificados: usar lotes/edifícios compatíveis, praças reais, parques e áreas de serviço.
- **Sem low-poly final.** OSM, cubos e extrusões são SOMENTE guia de urbanismo temporário; não entregar como visual aprovado.
- Arquitetura variada por época, tipologia, alturas, janelas, varandas, cores e revestimentos. Evitar material único e repetição óbvia.
- Prioridade de acabamento: primeiro trecho **300×300m** de orla + quiosques + calçadão + avenida + fachadas + acesso ao resort; depois hotéis, piscina, rio lento artificial, spa, paisagismo e iluminação cinematográfica.
- Pessoas animadas, veículos e som ambiente serão incluídos após padrão visual e base do mapa aprovados.
- PBR, iluminação coerente, sombras, decals, LOD, streaming, instancing, otimização baseada em FPS medido, não em promessas.
- Não usar fotogrametria, satélite ou imagens proprietárias sem licença para jogo comercial.

## Critérios de aprovação do piloto

1. Captura REAL do Unity em cena produzida pelos scripts.
2. Uma sequência contínua de ruas/avenidas, sem cruzamentos quebrados.
3. Prédios sem duplicidade colados uns nos outros, sem grandes vazios.
4. Fachadas distintas suficientes para não parecer uma cidade de clones.
5. Praia, quiosques e acesso ao resort coerentes com direção visual.
6. Medições reais de CPU, GPU, uso de memória e FPS após integração.

## Modelo de desenvolvimento atual

**ChatGPT + GitHub** como fluxo principal, sem depender de PC ligado ou de agentes externos. Mudanças versionadas em branches e revisadas por PR; GitHub Actions automatiza verificações viáveis. Não afirmar compilação/prints da Unity sem execução real do editor.
