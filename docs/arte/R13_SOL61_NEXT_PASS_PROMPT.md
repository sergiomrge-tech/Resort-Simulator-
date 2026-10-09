# SOL 6.1 — EXECUÇÃO R13, PASSO 2: EXPANSÃO ARTÍSTICA DA ORLA 2 km
**Agente solicitado:** Codex Sol 6.1, **nível médio (medium)**. **Idioma:** português.
**Repositório:** `sergiomrge-tech/Resort-Simulator-`.
**Branch:** `codex/r13-sol61-orla-premium`, sobre a PR [#35](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/35).
**Ambiente:** cópia Git limpa `D:\ProjectResort_R13_Sol61_Pass2`.
**Escopo:** TRABALHO EFETIVO (Blender/Python, Unity C#, shaders/texturas, testes, commit e push) — não apresentar somente plano.

## 1. Missão e princípios obrigatórios
Continuar da R13 já tecnicamente validada, elevar visivelmente a qualidade do **piloto S05 de 200 metros** e aplicar progressivamente os novos geradores aos **dez trechos S00–S09** (2.000 metros paralelos à orla, 1.000 metros de profundidade continental). A meta é **máxima cobertura efetiva de arte premium**, com qualidade de produção para simulação PC/Steam; não low-poly aparente, nem massas brancas/cinzas sem PBR, nem cenas com mar em plano chapado, areia lavada, paisagem repetida ou solo nu e incoerente. Priorize os primeiros resultados verificáveis, depois expanda parametrizando. Não declarar conclusão de todos os setores antes de evidência real.

**Condições imutáveis**:
- manter 1.468 footprints OSM de edifícios, 3.731 triângulos geográficos das ruas e as 48 árvores-piloto da R9; conservar a orientação cartográfica do `R4_SOURCE_FRAME.json`, 2 km na costa × 1 km de profundidade, e coordenadas R7–R13;
- preservar os geradores/fachadas, varandas e vitrines R7–R12, sem sobregravar os entregáveis anteriores; criar camada/cena nova derivada da R13;
- URP Unity **6000.6.2f1**, Direct3D11, Blender 5.2 ou bpy compatível, scripts reprodutíveis GitHub Actions; não mudar para HDRP nem inventar dependências que exijam instalações não disponíveis;
- ativos/texturas externos apenas com autoria, licença redistribuível e URL; preferir PBR/procedurais autorais; OSM © OpenStreetMap contributors/ODbL; não copiar imagens de Google Maps nem nomes de estabelecimentos reais sem fonte; os letreiros R12 são ficcionais;
- **nunca fabricar screenshot Unity**. Fotos da Unity apenas com Editor funcionando, PNG reais, câmera, GPU, versão, hashes; renders Blender devem ser etiquetados **Blender, não Unity**;
- sem acesso ao gameplay repo `Simulador-predial` nesta execução; não mexer no checkout sujo do usuário, nem no EXE jogável/atalhos existentes, nem mesclar na main;
- preservar material e importador **TextureImporter serializado v13** para PNG com `textureShape: 1` (não Cubemap); `ModelImporter` do FBX com **globalScale: 1** e GUID estáveis. Há regressões automatizadas em `Tools/tests/test_r13_unity_native_import_contract.py`.

## 2. Leitura da base ANTES de editar
Ler integralmente `AGENTS.md` (se existir), `README.md`, os scripts e relatórios:
- `docs/arte/R13_PLANO_COMPLETO_ORLA_PREMIUM_SOL61.md` (contrato mestre do usuário, todas as seções);
- `docs/arte/R13_QA_REPORT.md`;
- `docs/arte/R13_UNITY_SOL61_BLOCKERS_FIXED_20261009.md` (correções já concluídas, evitar refazer);
- `docs/arte/R13_BASELINE_AUDIT.md`, `R13_ASSET_MANIFEST.md`;
- `docs/arte/R12_FACHADAS_LOJAS_VITRINES.md`, R11, R10, R9;
- `Tools/Blender/generate_r13_coastal_slice.py`, `Tools/geo/generate_r13_surface_art.py`, `Tools/geo/normalize_r13_unity_meta.py`, `UnityProject/Assets/Editor/ResortR13CoastalFinish.cs`, `ResortR13VisualCapture.cs`;
- `ArtSource/Previews/R13_S05_before_*_RealUnity.png`, `R13_S05_after_*_RealUnity.png`; use-as-baseline; verificar que elas são capturas reais e foram produzidas com câmera semelhante;
- `.github/workflows/r13-orla-premium.yml` e testes nativos.

Checkpoint comprovado: piloto premium S05, **120 meshes, 274.745 faces**, 12 texturas PBR, Blender reimportado, Unity 6000.6.2f1 D3D11 validada, **12 capturas reais** (6 antes + 6 depois), CI verde. **S00–S04/S06–S09 ainda estão baseline.** A areia do S05 está clara/lavada, a frente interior tem solo cinza, as fachadas ainda repetem e há pouca vegetação/mobiliário.

## 3. EIXO A — Melhorar de verdade o S05 primeiro
### A1 Praia e areia — prioridade visual crítica
- corrigir exposição branca: albedo mais natural, areia seca/úmida diferenciadas, menos brilho especular, roughness coerente, normal fina e tiling métrico; desenho não deve parecer textura procedural estourada nem chapada;
- inserir variação suave de granulação, faixa pisoteada e contato areia/espuma/mar; detalhes macro sem frequência absurda;
- evitar z-fighting e superfícies superpostas R9/R10/R13. Testar dia/fim de tarde nos **mesmos ângulos** antes/depois.

### A2 Calçadão português
- padronagem preta/branca ondulada legível ao pé, placas e juntas de pedra em escala, normal e roughness, cores naturais;
- transições para calçada, ciclovia/avenida, gramado/canteiro e areia; sem faixas que atravessam prédios/ruas;
- preservar continuidade longitudinal do mosaico entre segmentos, evitar linha brusca visível nos limites de setor e textura espelhada.

### A3 Pavimentos da cidade
- reduzir completamente as áreas cinza sem acabamento: asfalto PBR com remendos sutis, sarjetas, guia, calçada de concreto/pedra, entradas de lojas conectadas, canteiros; manter traçado viário OSM e conexão entre ruas;
- evitar excesso de objetos menores/granulação; escala urbana crível a 1,65 m de altura da câmera;
- testar intersecções de ruas/edifícios, geometria colidindo, texturas UV esticadas.

### A4 Fachadas e vida urbana em S05
- enriquecer por tipologia: concreto, reboco, pastilhas, pedra, granito, metal, vidro e acabamentos de cobertura; quebrar repetição cromática, vãos/grades/molduras coerentes com pavimentos R8;
- enriquecer térreos R12: portas, esquadrias, vitrines, letreiros fictícios, marquise, loja e portaria sem blocos brancos; não declarar interior acessível, recorte real ou transparência física se não implementados;
- varandas, cornijas e equipamentos de telhado não podem parecer acessórios soltos nas paredes;
- gerar presets por estilo e hash de building_id, em vez de editar edifícios um por um.

### A5 Mobiliário e vegetação S05
- melhorar 8 grupos iniciais, distribuir bancos, lixeiras, jardineiras, paraciclos, postes, pequenas estruturas de quiosque compatíveis com circulação real, sem colisão de passeios nem repetição homogênea; texturas PBR variadas;
- espécie visual tropical naturalista, árvores e palmeiras com silhueta/dossel mais rico, canteiros/arbustos/gramíneas, UV0 e normal válidos; **as 48 árvores piloto R9 sem UV0 são problema artístico conhecido**, corrigir sem deslocar seus pontos;
- evitar árvores tipo esfera low-poly, vegetação atravessando fiação, vidro, vias ou calçadão.

### A6 Luz/água
- praia ensolarada e sombra sob marquise convincentes, sem zonas pretas R9 ou luz branca excessiva; controlar ACES, exposição, sombras suaves, cor do oceano e reflexos plausíveis;
- água costeira com ondulação temporal sutil, espuma na margem e cor azul-esverdeada natural, mas não afirmar Play Mode ou FPS sem teste real.

## 4. EIXO B — Aplicação paramétrica nos nove setores restantes
- usar dez segmentos S00–S09, cada um com 200 m paralelo à orla, setor S05 entre 1.000–1.200 m; **manter todos na mesma georreferência**;
- gerador determinístico por setor/seed e IDs OSM, com parâmetros reutilizáveis para largura de areia (ilustrativa onde sem fonte), material de praia, mosaico, pavimentos, mobiliário, vegetação e fachadas;
- **meta mínima:** melhorar artisticamente de forma visível a base costeira em todos dez segmentos, ao menos mais dois setores com detalhes PBR/mobiliário/vegetação reais e capturas, e documentar níveis *PREMIUM, INTERMEDIÁRIO, BASE ou PENDENTE* sem autopromoção;
- garantir os 2 km conectados: sem costura abrupta de areia, água, espuma, mosaico/avenida, sem quiosques flutuando, sem árvores em ruas; build **todos** os setores ou documentar impeditivo;
- manter custo de drawcall razoável: batching por material/área, instancing, LOD por distância, texturas reutilizadas; detalhes urbanos human-scale, não milhares de GameObjects individuais;
- se houver limitação temporal, fazer S05 melhor e 2 outros setores bem resolvidos antes de espalhar detalhes de baixa qualidade pelo mapa inteiro.

## 5. IMPLEMENTAÇÃO concreta requerida
1. Modificar/estender geradores Blender/Python `Tools/Blender` e `Tools/geo`, modelos/modificadores/UV reais, arte de textura autoral e seu manifest/licenciamento; registrar input/output e versões.
2. Nova cena derivada ou fluxo Editor para versão `R13_VisualPass2` sem sobrescrever cenas R12 ou R13 anterior; atualizar shader/URP somente com testes. Validar que *todos os FBX/PNG importam* com `.meta` completos, sem textura Cubemap nem escala 100×.
3. Gerar relatório de cobertura JSON `ArtSource/Previews/R13_Pass2_Coverage.json`: por S00–S09 `status, model_count, materials, vegetation, furniture, sea_sand_mosaic, adjacent_buildings, QA_evidence`; não inventar estados.
4. Atualizar `.github/workflows/r13-orla-premium.yml` e testes para reconstrução Blender nativa, reimport FBX, SHA, GIS invariants e cobertura.
5. Salvar imagens **reais Unity**, se Editor funcionar, em `ArtSource/Previews/R13_Pass2_*_RealUnity.png` + JSON de hashes/câmera/render/resolução. Ao menos S05 atualizado e **dois outros setores**, vistos de pedestre/costa/cidade; horários diurno e fim de tarde se viável. Para comparativo "antes/depois", preservar exatamente câmera e iluminação, e separar execuções para contornar o estado SRP/ColorLut. Se Unity não funcionar, continuar Blender/CI e marcar screenshots Unity PENDENTES.
6. Se Windows PC/Unity nativo disponível e sem travar trabalho, medir FPS/Frame time e drawcalls no 1080p com hardware especificado; **nunca inventar métricas**. Preferir meta de 60 FPS só como objetivo, não dado medido.
7. Atualizar `docs/arte/R13_QA_REPORT.md` por suplemento (não apagar checkpoint histórico), `docs/arte/R13_ASSET_MANIFEST.md`, novo `docs/arte/R13_PASS2_QA_REPORT.md` com PASS/FAIL/PENDENTE por setor, imagem e gate, e `R13_GAMEPLAY_INTEGRATION_PLAN.md` somente se houver mudança relevante.
8. Rodar py_compile, unittest, GitHub Actions (quando possível), Blender export + reimport nativos e Unity para validar referências, malhas, materiais, UV e shaders.

## 6. Critérios obrigatórios de sucesso
- S05 visivelmente menos lavado/melhor, com areia, transições, calçadão e rua melhor trabalhados;
- avanços reais em **mais que um setor** e melhor continuidade dos 2 km; status honesto dos demais;
- zero edifícios brancos devido a material ausente e zero shader/UV/regressão de escala; mantendo os 1.468 footprints, 3.731 triângulos e 48 árvores;
- capturas reais e hashes quando Unity disponível; imagens Blender corretamente rotuladas;
- testes que forem executados aprovados, CI sem erros quando possível, arquivo de QA completo;
- commit(s) verificáveis e `git push` na branch exclusiva, comentar PR #35; **NÃO MERGEAR**;
- não tratar arte aprovada só porque CI passou, não prometer integração final do gameplay.

## 7. Execução/autonomia
Trabalhe imediatamente e de maneira autônoma. Não peça confirmação por detalhes triviais. Faça marcos pequenos e verificáveis, com commits. Caso faltem recursos ou limite de tempo, escolha uma entrega materialmente melhor e reporte o que não fez, com caminhos reais; não gere placeholders e não pare na análise. **Não apague nenhum arquivo não rastreado nem execute git clean/reset destrutivo**. Você está numa cópia Git separada com metadados internos graváveis para contornar o erro de `index.lock` anterior. Não edite D:\sergi\Documents\Simulador-predial nem D:\ProjectResort_R13_Sol61_Orla.

### Relatório final do Sol (em português)
(a) commits, PR/branch; (b) arquivos/código/arte criada; (c) tabela S00–S09 estado REAL; (d) melhoria visual demonstrada; (e) testes/QA/gates; (f) links das capturas reais; (g) bloqueios e limitações; (h) checkpoint recomendado. Não declarar que terminou a orla se não houver 2 km verdadeiramente premium e revisados.
