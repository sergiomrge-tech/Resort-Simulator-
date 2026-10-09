# Resort Simulator — CHECKPOINT DE CONTINUIDADE

**Atualizado em 08/10/2026**. Ponto de recuperação durável para novos chats. Não presumir que informações antigas da conversa são mais recentes que os commits; conferir GitHub antes de escrever.

## Atualização R3 — piloto fiel Copacabana 300 × 300 m (08/10/2026)

**Desenvolvimento exclusivamente no GitHub, sem PC.** [PR #18 — R3 piloto geográfico](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/18) permanece **draft** e não foi integrada à `main`. Antes de retomar, ler `docs/arte/R3_PILOTO_GEOGRAFICO.md` nessa branch.

**Fatos testados e aprovados:**

- Polígonos exatos de três edifícios reais (`way/1048277518`, `way/1048277521`, `way/1308635852`) reconstruídos do OSM arquivado na mesma projeção/transformação da fonte BlenderGIS, sem chamadas externas, em `geo/pilot/R3_EXACT_OSM_PARCELS.json`.
- Estudo conservador em `geo/pilot/R3_MODEL_FIT_STUDY.json`: `hotel.fbx` (OSM 1048277518) e `residencial_sacadas.fbx` (OSM 1048277521) cabem no polígono em escala 1:1 e giro validado. `townhouse.fbx` não cabe no terceiro contorno, portanto **bloqueado**, sem deformação. [Actions 37862663423](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37862663423) **SUCCESS**.
- [Blender Cycles: imagem geográfica real com três contornos OSM](https://github.com/sergiomrge-tech/Resort-Simulator-/blob/chatgpt/r3-piloto-osm-implantacao-real/ArtSource/Previews/R3_Orla_300m_OSM_Real_Blender_QA.png). [Actions 37862776640](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37862776640) **SUCCESS**, mas apenas preview de localização, não screenshot Unity nem arte final.
- Sondagem real da malha original: edifícios OSM 1048277518 e 1048277521 têm faces mapeadas; o terceiro não tem faces correspondentes nesta versão da cidade. Não inventar geometria no terceiro local.
- Método de apagar componentes conectados do `.blend` foi corretamente **rejeitado**: a seleção abrangia um edifício vizinho. Nova estratégia usa o **gerador OSM original**, portado de `Simulador-predial` com origem documentada, para regenerar uma cópia omitindo somente dois IDs, sem editar fonte original.
- [Actions 37863719605](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37863719605) **SUCCESS**: reconstrução original com **62.980 vértices e 26.764 faces**; omitir dois IDs remove **23 faces de edifícios e ZERO faces de ruas**, preservando exatamente as outras 26.741 faces trianguladas no OBJ. Essa prova de paridade OBJ ainda precisa de comparação final com o `.blend` antes de declarar um FBX derivado seguro.

**Pendências/gates:** pipeline experimental `Tools/Blender/generate_r3_derived_pilot.py` e `.github/workflows/r3-derived-city.yml` deve comprovar a equivalência geométrica com o `.blend` original, gerar FBX derivado, renderizar, rodar testes e não tocar em originais. **Nenhum FBX derivado ou implantação Unity deve ser anunciado até passar.** O build Windows da R1 segue dependente de ativação legítima da Unity no GitHub Actions. Fase de economia/IA continua arquivada.

---

## Marco visual GitHub-first — nove FBX originais na main (08/10/2026)

**Concluído e aprovado em QA de arquivos/Blender, mas ainda não validado no Editor Unity:**

1. **PR #14 [mesclada](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/14)** — oito edificações costeiras autorais copiaram os mesmos bytes de `ArtSource/LocalProjectOwned/CoastalUrbanKit/*.fbx` para `UnityProject/Assets/Architecture/OwnedCoastal/*.fbx`, com GUIDs Unity determinísticos. [QA Python success 37861262361](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37861262361). Não implica que foram posicionadas no mapa ou importadas no Unity Editor.
2. **PR #15 [mesclada](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/15)** — oito FBX originais reimportados **realmente no Blender**, medidos em metros e renderizados em [prancha real de QA 1600 × 1000](../../ArtSource/Previews/Owned_CoastalUrbanKit_Blender_QA.png). Contagens de faces entre 1.344 (loja) e 9.276 (hotel). [QA Blender success 37861282583](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37861282583).
3. **PR #16 [mesclada](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/16)** — quiosque detalhado reproduzido do **script autoral original** via Blender headless no GitHub, sem acesso ao PC: 307 objetos, 34.468 faces e 68.008 triângulos. FBX binário em `UnityProject/Assets/Architecture/OwnedKiosk/KioskPremium_Detailed.fbx`, [render real de QA 1600 × 900](../../ArtSource/Previews/Owned_KioskPremium_Blender_QA.png), [QA Blender success 37861618298](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37861618298). Não é screenshot Unity nem prefab posicionado.
4. **Total de nove FBX** do acervo local, prontos na estrutura de arquivos Unity do `Resort-Simulator-`. Agora existe `.github/workflows/visual-asset-integrity.yml` para revalidar automaticamente hashes, origens e previews em novas alterações visuais, sem PC.
5. **PR #5 R1 draft** mantém o primeiro build Windows automatizado no GameCI, e a verificação exige agora EXE + `_Data` + `UnityPlayer.dll` + `SHA256SUMS.txt`, para impedir entrega incompleta. Esse gate continua **SKIPPED sem credenciais de licença Unity nos Secrets do GitHub**; nenhuma compilação da linha atual foi aprovada ainda.

**Próxima fase, executar somente no GitHub:** avaliar se o visual dos modelos corresponde ao Realismo Estilizado Premium, planejar implantação dos modelos em apenas três footprints OSM verificados do piloto de 300 × 300 m, configurar URP/materiais, e obter validação de Editor Unity quando o runner GitHub licenciado estiver disponível. **Não** preencher Copacabana com clones sem referências; não antecipar os sistemas de economia/NPC já arquivados em `docs/backlog/fase2-quiosque/`.

---

## Política definitiva — desenvolvimento sem dependência do PC

**Decisão de 08/10/2026:** todas as fases deverão prosseguir **no GitHub**, ainda que o desktop remoto permaneça desligado por dias. O PC do proprietário só poderá servir como fonte ocasional de material autoral, validação opcional da Unity e destino de builds prontos. Leia [docs/GITHUB_FIRST_SEM_PC.md](../GITHUB_FIRST_SEM_PC.md) antes de preparar novas tarefas.

**Importação concluída na main via [PR #12](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/12):** 38 arquivos autorais da antiga biblioteca local estão em `ArtSource/LocalProjectOwned/` com manifesto de hashes de origem/Git, oito tipologias costeiras, quiosque premium e LOD1, POS e objetos complementares. Testes independentes do PC em [GitHub Actions 37860807539](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37860807539) passaram. Esses arquivos ainda são fontes aguardando integração visual, não cidade final.

**Executável antigo:** o PC já possui um build local da linha `Simulador-predial`, copiado para `D:\ProjectResort_Entregas_ChatGPT` após smoke test; **não corresponde à R1/R2 atual**. A disponibilidade desse PC não pode bloquear etapas futuras. Para um novo EXE de `Resort-Simulator-`, preferir artifacts e releases do GitHub. O pipeline GameCI da R1 ainda aguarda licença válida no Actions (secret, nunca no Git).

---

## Atualização mais recente — R2 visual, fim de 08/10/2026

**Prioridade do usuário:** continuar a arte e o mapa REALISTA ESTILIZADO PREMIUM; **não** antecipar a Fase 2 de economia, NPCs e estoque. Essa fase foi arquivada e mesclada na `main` via [PR #9](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/9) em `docs/backlog/fase2-quiosque/`, junto à história já salva da campanha em `docs/campanha/` ([PR #8](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/8)).

**R1** permanece em [PR #5 draft](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/5). O modelo de Copacabana original Blender (`ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend`) e o FBX (`UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx`) estão intactos e tiveram roundtrip Blender aprovado. URP e gerador de cena foram preparados em C# e QA estática; **não há execução/compilação Unity, screenshot Unity nem EXE Windows validados**. Build GameCI foi pulado por falta de licença de Editor no runner.

**R2** agora avançou tecnicamente no [PR #10 draft — fachadas premium](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/10), baseado na branch R1 e **não mesclado** à `main`. Artefatos verificados no PR #10:

- Três módulos arquitetônicos autênticos do Blender: `R2_ArtDeco_Orla.fbx`, `R2_Residencial_Varandas.fbx`, `R2_Hotel_Contemporaneo.fbx` em `UnityProject/Assets/Architecture/R2_Prototypes/` (todos com GUID estável). Módulos **não** são prédios completos.
- Prévia genuína Blender `ArtSource/Previews/Resort_R2_Fachadas_Premium_Blender_QA.png`, re-renderizada após integração de materiais: [Action 37859137005](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37859137005) **SUCCESS** (QA das fachadas), **não** screenshot Unity.
- Seis materiais autorais, com 24 mapas PNG de Albedo, Normal, Roughness e Mask 512², e GUIDs determinísticos em `UnityProject/Assets/Textures/R2_PBR/`. [Action 37859035759](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37859035759) **SUCCESS**. O código de preview `UnityProject/Assets/Editor/ResortFacadePreviewBuilder.cs` prepara URP Lit para os mapas, **ainda não executado/compilado na Unity**.
- A fonte cartográfica foi usada para selecionar **três candidatos reais** (não edifícios construídos): OSM `way/1048277518`, `way/1308635852`, `way/1048277521` no recorte de 300 × 300 m, excluindo `building=roof` e garagens. Evidência `geo/pilot/R2_PILOT_BUILDING_CANDIDATES.json`. [Action 37859390469](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37859390469) **SUCCESS**.
- Testes Python reais verificaram FBX, imagens, texturas e OSM. **Não** equivalem a homologação visual, jogos prontos ou FPS.

**Próximos passos seguros:** ler [PR #10](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/10), inspecionar o novo preview Blender; melhorar arte arquitetônica (texturas, detalhes, volumes) sem substituir os footprints; procurar forma legítima de executar Unity 6.3 em ambiente licenciado; validar cena de R1 e R2 com logs e screenshots reais; só depois posicionar módulos adaptados aos lotes OSM e produzir piloto completo de praia/quiosque/resort. Não mesclar R1/R2 como "jogável" até as evidências reais do Editor.

---

## Identidade e objetivo

- Repositório único: `sergiomrge-tech/Resort-Simulator-`. NÃO reutilizar nem alterar `Simulador-predial`.
- Desenvolvimento **somente pelo ChatGPT + GitHub**, conforme última decisão do usuário. Não exigir Luna/Codex, PC online ou outros agentes.
- Unity para Windows/Steam; mapa de **2.000 × 1.000 m = 2 km²** baseado em Copacabana RJ. Piloto visual **300 × 300 m**.
- Jogo Tycoon de quiosque herdado → quarto/pousada → hotel → resort cinco estrelas; cidade coerente, fachadas variadas PBR, sem grandes áreas cinzas.
- Mapas 3D originais não devem ser substituídos por cidade inventada, nem confundidos com a qualidade final.

## Estado concreto verificado

| Recurso | Estado |
|---|---|
| `ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend` | Fonte original real preservada |
| `UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx` | Exportação FBX real preservada, ainda sem importação Unity validada |
| OSM `geo/data/report.json` | 1.468 footprints, 468 trechos de ruas, 563 pontos de árvores; árvores não são meshes |
| Screenshot `ArtSource/Previews/Copacabana_REAL_BLOCO_3D_QA_COLOR.jpg` | Render **Blender real**, não print Unity |
| R1 — cena Unity, PlayerController, DayNightCycle | Implementados **em código**, PR **#5** draft, sem compilação Unity verificada |
| CI R1 | 7/7 testes estáticos Python passaram em GitHub Actions **37854021618**; etapa Unity/Windows **SKIPPED por licença ausente** |
| Biblioteca de skills | 13 playbooks para Unity/Blender/GIS/fachadas/águas/tycoon **integrados à `main` via PR #4**, QA Python aprovada |
| Unity EXE e screenshots Unity | **NÃO GERADOS / NÃO VALIDADOS** |
| Resort premium, NPCs e arquitetura final | Ainda não implementados |

## Trabalho em curso por branch

- `main`: geografia, preview Blender, 13 skills e auditoria de integridade; commit verificado `0af25438b7d6b55293f88684aab407f541e66bc0` após mescla de PRs #6 e #4 em **08/10/2026**. Reconfirmar HEAD real antes de editar.
- [PR #5 — R1 Unity (draft)](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/5) — branch `chatgpt/r1-unity-foundation`, commit verificado `e55e54c5f970e6f0c310a4aaa5816ba1f825882e`. Não mesclar enquanto faltar parser/build Unity real.
- [PR #4 — Skills de produção](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/4) — **mesclada na `main`**; os 13 procedimentos e `AGENTS.md` estão disponíveis a novos chats.
- [PR #6 — Auditoria e recuperação](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/6) — **mesclada na `main`**; primeira auditoria executada em `main` no GitHub Actions **37855108001** com sucesso.
- Recuperação anti-travamento e auditoria agora **estão em `main`**. Branch original `chatgpt/continuity-guard-20261008` serve apenas como histórico.

## Próxima prioridade absoluta

**R1:** executar importação, validação de eixos/escala, colisão e player/controller da Unity **de verdade** quando acesso licenciado ao Editor/runner permitir. Não declarar sucesso apenas com testes Python. Paralelamente, pequenas verificações estáticas/documentais são possíveis na nuvem.

R2 (fachadas realistas distintas) e R3 (orla/resort 300×300 m) só avançam após aprovações visuais e técnicas compatíveis. Não reconstruir os 2 km² usando blocos clones.

## Checkpoints e ritmo 24h

- Automação ChatGPT agendada **1 vez/hora** para revisar status e, se viável, realizar uma iteração segura em branch; não garante trabalho de CPU ininterrupto nem compilação Unity.
- GitHub Actions `continuity-guard.yml` **integrado na `main`**, agendado a cada 6 horas (execução periódica pode atrasar por políticas do GitHub). Auditoria inicial na branch padrão **SUCCESS** em `37855108001`. Não compila Unity.
- Não salvar segredos da Unity no Git; licença precisa ser configurada explicitamente pelo proprietário em GitHub Secrets.
- Não fazer merge automático. Toda fase vira PR e requer QA honesta.
- Se o chat travar, **iniciar nova conversa neste mesmo Projeto** e dizer: `Retome o Resort pelo GitHub, leia docs/checkpoints/LATEST.md e o status das PRs, continue a R1 sem repetir código pronto.`

## Como verificar em qualquer retomada

1. Ler `docs/checkpoints/LATEST.md`, `docs/CONTINUIDADE_24H.md`, `AGENTS.md`, `docs/SKILLS_DE_PRODUCAO.md` e `docs/STATUS.md` **diretamente da `main`**.
2. Consultar HEAD de `main` e das branches R1/skills, PRs abertas e últimos GitHub Actions.
3. Respeitar precedência: **resultado real do Actions + arquivo GitHub no HEAD atual > resumo histórico > promessa antiga**.
4. Rodar `python3 Tools/automation/continuity_guard.py --output continuity_report.json`; usar `--github` no Actions com token read-only para resumo de PRs.
5. Escolher **uma única tarefa de código** na etapa atual; versionar, testar e registrar antes de iniciar outra.

© OpenStreetMap contributors — ODbL 1.0.
