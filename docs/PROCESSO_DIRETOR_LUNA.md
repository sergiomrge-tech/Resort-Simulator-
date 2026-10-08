# Protocolo do Diretor e dos Agentes — Resort Simulator

## Hierarquia

1. **ChatGPT: Diretor principal.** Faz a leitura do estado do GitHub, define prioridades, regras, arquitetura, autorização de expansão, audit visual e aceitação/rejeição dos PRs.
2. **Codex Luna Alto: executor de código.** Implementa Unity C#, assets técnicos, ferramentas Blender necessárias, GameCI, testes e relatórios solicitados. **Não usar Sol**.
3. **GitHub: fonte da verdade**, incluindo branches, PRs, Issues e evidências. Uma afirmação de conclusão exige commit e evidência verificável.
4. **PC: QA interativo eventual**, não dependência diária. GitHub Actions executa batch; não equivale a Unity Editor gráfico e requer licença apropriada para compilar.

## Frentes, arquivos e exclusividade

- **R1 Geografia, importação Unity e CI:** `UnityProject/Assets/Editor/`, `Assets/Scenes/` relativos, `Packages/`, `ProjectSettings/`, workflows Unity e `docs/qa/R1_MAPA_UNITY.md`. Não reexportar cidade sem ordem.
- **R2 Arquitetura:** `UnityProject/Assets/Art/Architecture/` e `docs/arte/CATALOGO_FACHADAS.md`. R2 não muda cena-base nem pipeline CI do R1.
- **R3 Resort, orla e luz:** `UnityProject/Assets/Art/Resort/`, cenas aditivas e `docs/arte/PLANO_ORLA_RESORT_300m.md`. R3 não muda malha geográfica e não pisa nos arquivos de R1/R2.

Quando alterações cruzarem fronteiras, solicitar review do Diretor por Issue/PR; nenhum agente altera `main` diretamente. Orçamento de concorrência: **1 agente inicialmente**, até **3** apenas em tarefas independentes e com consumo controlado.

## Regras visuais vinculantes

- **2 km²** fixos. Base OSM/Blender original preservada e georreferenciada (source read-only).
- Visual final premium realista, sem low-poly, sem edifícios repetidos, sem vazios cinzentos ou ruas desconectadas.
- Primeiro **vertical slice 300 × 300m** com densidade e acabamentos, depois ampliar.
- Prints têm que ser **realmente da ferramenta declarada**. Captura do Blender não é foto do Unity nem prova de jogo jogável.
- Usar ativos comerciais/CC0 somente com proveniência e licenças; respeitar ODbL no conteúdo derivado.
- Não medir nem alegar FPS sem profile real. Não afirmar builds/parsing Unity quando só testes Python/Blender passaram.

## Handoff para R1

O comando de execução é a descrição integral da **Issue #1**. Luna Alto lê os arquivos nela indicados, trabalha em `luna/r1-copacabana-unity-gate` e entrega um PR à `main` com:
- diff limitado ao escopo;
- como reproduzir os testes;
- evidências reais do que rodou e o que foi bloqueado;
- análise de orientação FBX e material URP;
- limitações sobre falta de licença de Unity;
- screenshot Unity **somente se Unity realmente rodou**.

O Diretor lê logs e capturas, registra aceite ou solicita correção. Só então R2 começa. A documentação do R2 pode ser preparada sem iniciar implementação.

## Checkpoint

Ver `docs/STATUS.md` e Issues #1–#3. Atualizar o checkpoint após cada gate, incluindo SHA do commit, data, ferramentas e resultados. **Nunca marcar trabalho futuro como concluído.**
