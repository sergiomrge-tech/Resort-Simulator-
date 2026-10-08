# Resort Simulator — Costa Carioca

Jogo original para PC/Steam em Unity, construído em um **repositório independente**. Referência geográfica: **Copacabana (Rio de Janeiro)**, recorte jogável **2.000 × 1.000 m (2 km²)**.

O objetivo é um resort cinco estrelas realista cercado de orla densa, avenidas conectadas, fachadas distintas, quiosques, jardins, piscinas, rio lento artificial e montanhas litorâneas. A orla de **300 × 300 m** será refinada antes da expansão visual por todo o mapa.

## Estado real

- **Blender**: `ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend` — modelo OSM já produzido.
- **Unity**: `UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx` — FBX derivado do mesmo Blender; importação/compilação Unity ainda precisam ser executadas e comprovadas.
- **Captura real do Blender**: `ArtSource/Previews/Copacabana_REAL_BLOCO_3D_QA_COLOR.jpg` — preview técnico, **não** screenshot da Unity e **não** arte final.
- **Fonte e licença geográfica**: `geo/data/report.json`, `geo/data/copacabana.osm.gz`. © OpenStreetMap contributors, ODbL 1.0.
- **Projeto Unity**: `UnityProject/` com fontes C#, configuração inicial Unity 6.3 LTS e script editor `Assets/Editor/ResortWorldBuilder.cs`; o gerador ainda não foi executado na Unity.
- **GitHub Actions**: validações e conversões Blender executadas; **GameCI/Windows build não está validado** e depende de licença adequada.

## Modelo de produção aprovado

**ChatGPT = Diretor e programador. GitHub = fonte da verdade.** O usuário optou por desenvolver sem Luna/Codex nem manter o PC ligado; verificações e renders podem ocorrer pelo GitHub Actions.

As instruções Luna com detalhamento por arquivo estão nas Issues [#1 (R1 mapa/Unity)](https://github.com/sergiomrge-tech/Resort-Simulator-/issues/1), [#2 (R2 arquitetura)](https://github.com/sergiomrge-tech/Resort-Simulator-/issues/2) e [#3 (R3 resort)](https://github.com/sergiomrge-tech/Resort-Simulator-/issues/3).

**Somente R1 está liberada inicialmente.** Código de exploração na branch `chatgpt/r1-unity-foundation` (PR #5 draft). Não confundir QA estática aprovada com compilação Unity: a licença adequada para o GameCI ainda precisa ser configurada.

## Continuidade automática e anti-travamento

- `docs/checkpoints/LATEST.md` — **comece aqui em uma conversa nova**; estado, branches, bloqueios e próximos passos.
- `docs/CONTINUIDADE_24H.md` — recuperação após chat travado, rotina horária ChatGPT e auditoria GitHub programada.
- `AGENTS.md` / `docs/SKILLS_DE_PRODUCAO.md` — 13 skills e regras de desenvolvimento já integradas.
- `.github/workflows/continuity-guard.yml` — auditoria **somente de leitura**, de seis em seis horas, com relatório preservado em artifact.

## Documentação atual

- `docs/STATUS.md` — checkpoint com resultados verdadeiros e bloqueios.
- `docs/PROCESSO_DIRETOR_LUNA.md` — acordos de escopo, agentes, gates e aprovação.
- `docs/DIRECAO_ARTISTICA.md` — referência visual não negociável.
- `docs/FONTE_MAPA_BLENDER.md` — proveniência do .blend e exportação FBX.

Este repositório **não reutiliza código ou assets do jogo de manutenção predial**. A malha geográfica OSM é uma fonte cartográfica reutilizada com atribuição, não o antigo jogo.
