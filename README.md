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

**ChatGPT = Diretor. Codex Luna Alto = Programador. GitHub = fonte da verdade.** Outros modelos de agente, inclusive Sol, não serão usados nas frentes de execução.

As instruções Luna com detalhamento por arquivo estão nas Issues [#1 (R1 mapa/Unity)](https://github.com/sergiomrge-tech/Resort-Simulator-/issues/1), [#2 (R2 arquitetura)](https://github.com/sergiomrge-tech/Resort-Simulator-/issues/2) e [#3 (R3 resort)](https://github.com/sergiomrge-tech/Resort-Simulator-/issues/3).

**Somente R1 está liberada inicialmente.** O agente deve trabalhar na branch `luna/r1-copacabana-unity-gate` e entregar PR revisável antes de integrar. Criar Issues e branches não inicia automaticamente o Codex.

## Documentação atual

- `docs/STATUS.md` — checkpoint com resultados verdadeiros e bloqueios.
- `docs/PROCESSO_DIRETOR_LUNA.md` — acordos de escopo, agentes, gates e aprovação.
- `docs/DIRECAO_ARTISTICA.md` — referência visual não negociável.
- `docs/FONTE_MAPA_BLENDER.md` — proveniência do .blend e exportação FBX.

Este repositório **não reutiliza código ou assets do jogo de manutenção predial**. A malha geográfica OSM é uma fonte cartográfica reutilizada com atribuição, não o antigo jogo.
