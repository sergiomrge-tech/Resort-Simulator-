---
name: unity-github-sem-pc
description: Modify Unity 6 project on GitHub using code, batchmode and GameCI with explicit license gate; never claim compilation without logs.
---

# Unity sem PC: scripts, testes e build

**Quando usar:** qualquer C# Unity, cena, prefabs, pipelines de render, input, compilação ou testes.

## Fonte do projeto
- `UnityProject/ProjectSettings/ProjectVersion.txt` — versão alvo.
- `UnityProject/Packages/manifest.json` — pacotes; a presença de URP não garante Asset URP ativo.
- `UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx` — mapa real.
- `UnityProject/Assets/Editor/ResortWorldBuilder.cs` — builder de cena.
- `.github/workflows/r1-unity-cloud.yml` na branch R1 — validador e gate de build.

## Procedimento
1. Consultar instruções Unity oficiais e adaptar apenas a versão realmente suportada pela versão do projeto.
2. Usar branch por etapa e diff pequeno. O `Assets` exige arquivos `.meta` de GUID estável; não reatribuir a cada build.
3. Criar C# modular e Editor methods invocáveis por `-executeMethod`; preferir gerador de cena determinístico ao YAML manual com IDs inválidos.
4. Validar compilação **somente via Unity real** quando houver licença/runner Unity disponível. GitHub Actions com apenas unittest/Python é «QA estático», não «Unity compilou».
5. Gate `NOT_BUILT: LICENSE_MISSING` impede falsa conclusão. Nunca colocar segredos `UNITY_*` no repositório; configuração em Secrets requer ação do proprietário.
6. Com compilação ativa, colher Editor log, lista de cenas, erros, BuildReport, conteúdo de EXE e Artifact de Actions; na ausência, seguir tarefas que não exigem Editor e declarar bloqueio.
7. Checar referências de FBX, transformação de eixos, `CharacterController`, versão do Input System, pipeline e shader em runtime quando for possível.
8. Abrir PR e registrar fatos no `docs/qa/`.

## Critério de saída
- Código versionado, QA automatizada com logs identificáveis, limites explícitos.
- Unity build e screenshot declarados **somente** após execução e inspeção.
- Sem sobrescrever `main` sem gate de revisão.

## Referências
- https://github.com/Unity-Technologies/skills (biblioteca oficial)
- https://github.com/Unity-Technologies/skills/blob/main/skills/unity-cli/SKILL.md
- https://game.ci/docs/3/github/activation/
- https://game.ci/docs/3/github/builder/
