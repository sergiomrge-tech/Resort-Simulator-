# Resort Simulator — CHECKPOINT DE CONTINUIDADE

**Atualizado em 08/10/2026**. Ponto de recuperação durável para novos chats. Não presumir que informações antigas da conversa são mais recentes que os commits; conferir GitHub antes de escrever.

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
| Biblioteca de skills | 13 playbooks para Unity/Blender/GIS/fachadas/águas/tycoon, PR **#4**, QA Python aprovada |
| Unity EXE e screenshots Unity | **NÃO GERADOS / NÃO VALIDADOS** |
| Resort premium, NPCs e arquitetura final | Ainda não implementados |

## Trabalho em curso por branch

- `main`: base geográfica, preview Blender e configurações iniciais, commit verificado `94ce590e66920ffaefda3b926be1d155642aa0b5` **em 08/10/2026**; conferir HEAD atual antes de qualquer commit.
- [PR #5 — R1 Unity (draft)](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/5) — branch `chatgpt/r1-unity-foundation`, commit verificado `e55e54c5f970e6f0c310a4aaa5816ba1f825882e`. Não mesclar enquanto faltar parser/build Unity real.
- [PR #4 — Skills de produção](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/4) — branch `chatgpt/skills-producao-resort-v1`, commit verificado `88ebeaf0430ae57ce8e914f97b45664c036cf2c2`; aguarda revisão.
- Recuperação anti-travamento: `chatgpt/continuity-guard-20261008`; inclui esta documentação e auditoria automática, sem alterar os assets.

## Próxima prioridade absoluta

**R1:** executar importação, validação de eixos/escala, colisão e player/controller da Unity **de verdade** quando acesso licenciado ao Editor/runner permitir. Não declarar sucesso apenas com testes Python. Paralelamente, pequenas verificações estáticas/documentais são possíveis na nuvem.

R2 (fachadas realistas distintas) e R3 (orla/resort 300×300 m) só avançam após aprovações visuais e técnicas compatíveis. Não reconstruir os 2 km² usando blocos clones.

## Checkpoints e ritmo 24h

- Automação ChatGPT agendada **1 vez/hora** para revisar status e, se viável, realizar uma iteração segura em branch; não garante trabalho de CPU ininterrupto nem compilação Unity.
- GitHub Actions `continuity-guard.yml` executa checagem estática agendada a cada 6 horas **após este workflow entrar na branch padrão `main`**, além de execução em PR/push.
- Não salvar segredos da Unity no Git; licença precisa ser configurada explicitamente pelo proprietário em GitHub Secrets.
- Não fazer merge automático. Toda fase vira PR e requer QA honesta.
- Se o chat travar, **iniciar nova conversa neste mesmo Projeto** e dizer: `Retome o Resort pelo GitHub, leia docs/checkpoints/LATEST.md e o status das PRs, continue a R1 sem repetir código pronto.`

## Como verificar em qualquer retomada

1. Ler `docs/checkpoints/LATEST.md`, `docs/CONTINUIDADE_24H.md` e `docs/STATUS.md`; se ainda não estão em `main`, buscá-los na branch `chatgpt/continuity-guard-20261008`.
2. Consultar HEAD de `main` e das branches R1/skills, PRs abertas e últimos GitHub Actions.
3. Respeitar precedência: **resultado real do Actions + arquivo GitHub no HEAD atual > resumo histórico > promessa antiga**.
4. Rodar `python3 Tools/automation/continuity_guard.py --output continuity_report.json`; usar `--github` no Actions com token read-only para resumo de PRs.
5. Escolher **uma única tarefa de código** na etapa atual; versionar, testar e registrar antes de iniciar outra.

© OpenStreetMap contributors — ODbL 1.0.
