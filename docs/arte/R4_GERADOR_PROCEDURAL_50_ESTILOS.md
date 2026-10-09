# R4 — Gerador de fachadas premium para Copacabana (proposta de produção)

**Situação neste commit:** catálogo determinístico de **50 receitas arquitetônicas** + planejador OSM, **não 50 meshes FBX já renderizados**. Nenhuma fachada nova foi inserida no jogo. O resultado precisa de imagens reais Blender e Unity e gate do Diretor antes de substituir visuais atuais.

## O problema

Nossa base real GIS possui **1.468 footprints OSM** dentro de uma ROI reportada de **2.000.000 m²**, com 1.398 alturas estimadas apenas para visualização, 56 derivadas de níveis OSM e 14 alturas OSM explícitas. A descrição narrativa original fala em *2 × 2 km*; são escopos diferentes e não se deve esticar o mapa para fingir 4 km².

Gerar manualmente materiais/modelos para cada uma das 1.468 entradas é desnecessário, caro e pouco consistente. Copiar apenas os oito FBX existentes sobre os edifícios também produziria clones óbvios e prejudicaria a identidade da orla.

## Solução proposta

**Gerador procedural híbrido Blender → Unity**, offline e repetível em GitHub Actions:

1. Ler a malha OSM congelada **sem downloads**, identificar `way/<id>` e seu footprint fechado em metros e as características tags `height`, `building:levels`, `building`, `tourism`, `shop`, `office`, `building:material`. Não confundir volume procedimental com levantamento cadastral real.
2. Aplicar classificação determinística por região e uso. Faixa junto à Avenida Atlântica: hotéis e residenciais costeiros (apenas quando o lote/uso permite); ruas internas: residenciais, comércio térreo e edifícios menores; prédios especiais são **seleções manuais**, nunca substituídos por sorteio.
3. Escolher entre **10 famílias × 5 receitas distintas = 50 configurações**. Cada receita muda composição de fachada, balcão/sacadas, esquadrias, coroamento, piso térreo e materiais, e não apenas cor.
4. Gerar as paredes pela **forma exata do footprint OSM** (sem inventar um quarteirão retangular), ajustando módulos à largura de cada face: vãos proporcionais, janelas profundas, perfis, peitoris, marquises, grades, ar-condicionado, floreiras, guarda-corpos, platibandas e entradas.
5. Usar detalhes **modulares e instanciáveis** em vez de milhares de meshes diferentes; agrupar peças por material e por quarteirão, com UV e atlases PBR. LOD0 detalhado para visualização ao nível da rua, LOD1 com menos geometria e LOD2 simplificado **apenas à distância** (não transformar a arte em low-poly visível).
6. Gerar IDs e parâmetros estáveis `style_id`, `building_id` e `seed` de cada prédio. Nunca mudar o visual ao reiniciar ou regenerar o mapa. Registrar overrides artísticos por ID sem perder a derivação.
7. Exportar por **blocos geográficos** para Unity (FBX/GLB, objetos/prefabs estruturados), preservando o original `Copacabana_Real_Blender.fbx`. Antes de exportar, confirmar que o **mesmo edifício antigo não continua ocupando o local**. A etapa R3 demonstrou a substituição segura de apenas dois IDs.
8. Manter os oito modelos costeiros e o quiosque premium como **hero assets exclusivos** e preservar edifícios marcos/raros via overrides específicos, não convertê-los em genéricos.

## Alternativas reais que pesquisamos

- [Procedural Building Grammar para Blender](https://github.com/p-schulz/osm_building_grammar): **Apache-2.0**, aceita footprints e tags OSM e tem geração de sacadas, janelas, lojas, UVs, materiais e export GLB; candidato a prova de conceito, **ainda não integrado/testado no Project Resort**. Antes de executar código externo, fixar commit, auditar licença/dependências e testar no runner GitHub.
- [Blosm + Geometry Nodes](https://github.com/vvoovv/blosm/wiki/Applying-Geometry-Nodes-to-Building-Footprints): aplicação de nós em footprints OSM; a própria documentação trata o setup como demonstração. Pode ajudar na modelagem, mas não prova produção em massa.
- [Urban Building & City Generator (Unity Asset Store)](https://assetstore.unity.com/packages/tools/level-design/urban-building-city-generator-389306): opção comercial para comparação, mas não priorizada, pois os perfis e a geometria padrão podem ser inadequados à Copacabana e o projeto já preserva geometria GIS e autoria própria.

**Não adquirir nem importar automaticamente plugins pagos.** A R4 começa com geração própria controlada e poderá avaliar o addon Apache de forma isolada.

## Etapas concretas e critérios de aceitação

**R4.0 — Dados e estilos:** publicar 50 receitas no `ArtSource/ProceduralBuildings/Resort50Styles.json`; atribuições determinísticas a footprints reais em `geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json`; CI valida fonte OSM, IDs, segurança de alturas e fidelidade dos estilos. Este marco é *catálogo/planejamento*, não 50 modelos acabados.

**R4.1 — Piloto de arquitetura real:** gerar **10 edifícios individuais** em Blender headless, duas vias diferentes, cada um com detalhes visíveis e textura UV/PBR, capturar close-ups reais 1600×900 (não mockup), validar que contorno ocupa corretamente a localização.

**R4.2 — Biblioteca 50 × Blender:** renderizar 50 receitas em pranchas reais, registrar dimensão, polígonos, materiais e hash de cada uma; reprovar repetição visual evidente antes de ir ao mapa.

**R4.3 — Bairro piloto:** completar um quarteirão (faixas de edifícios reais), preservando ruas; gerar FBX + QA Blender e importar nativamente na Unity, com câmera em perspectiva de pedestre e inspeção dos materiais.

**R4.4 — Expansão da ROI:** segmentar 1.468 footprints em lotes de no máximo 50/100, evitando picos de RAM; comparar performance, overdraw, draw calls e memória no PC. Gerar LOD com distâncias por contexto, instancing de módulos, streaming por células e colliders simplificados.

**Gates inegociáveis:** sem corrupção de ruas/coastline; alturas verdadeiras somente com tag de origem (ou `ESTIMATE_NOT_SURVEYED`); nenhuma peça flutuante ou invadindo vias; não repetir hotel de fachada idêntica na mesma quadra; conservar quiosque e 9 fontes FBX anteriores; captura real no Blender/Unity; avaliação visual do Diretor; editor Unity e build Windows precisam passar antes de declarar versão jogável.

Copyright dos dados geográficos: © OpenStreetMap contributors — ODbL 1.0. O catálogo estilístico é conteúdo original do Project Resort.
