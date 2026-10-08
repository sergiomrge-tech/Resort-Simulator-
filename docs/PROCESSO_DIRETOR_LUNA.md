# Protocolo do ChatGPT — Resort Simulator (histórico antigo: Diretor e Luna)

## Hierarquia

1. **ChatGPT: Diretor e programador único, conforme pedido atual do usuário.** Planeja, implementa Unity C#, coordena Blender e GameCI, testa, documenta e faz revisão das próprias alterações com PR e logs.
2. **Codex/Luna: dispensados.** As instruções históricas Luna contidas em Issues anteriores são apenas legado de planejamento; não invocar agentes.
3. **GitHub: fonte da verdade**, incluindo branches, PRs, Issues e evidências. Uma afirmação de conclusão exige commit e evidência verificável.
4. **PC: QA interativo eventual**, não dependência diária. GitHub Actions executa batch; não equivale a Unity Editor gráfico e requer licença apropriada para compilar.

## Frentes, arquivos e exclusividade

- **R1 Geografia, importação Unity e CI:** `UnityProject/Assets/Editor/`, `Assets/Scenes/` relativos, `Packages/`, `ProjectSettings/`, workflows Unity e `docs/qa/R1_MAPA_UNITY.md`. Não reexportar cidade sem ordem.
- **R2 Arquitetura:** `UnityProject/Assets/Art/Architecture/` e `docs/arte/CATALOGO_FACHADAS.md`. R2 não muda cena-base nem pipeline CI do R1.
- **R3 Resort, orla e luz:** `UnityProject/Assets/Art/Resort/`, cenas aditivas e `docs/arte/PLANO_ORLA_RESORT_300m.md`. R3 não muda malha geográfica e não pisa nos arquivos de R1/R2.

Quando alterações cruzarem fronteiras, solicitar review do Diretor por Issue/PR; nenhum agente altera `main` diretamente. **Regra atual: apenas ChatGPT na direção e no código, sem agentes Codex.** Executar R1 → revisão → R2 → revisão → R3; automações GitHub Actions independentes são permitidas.

## Regras visuais vinculantes

- **2 km²** fixos. Base OSM/Blender original preservada e georreferenciada (source read-only).
- Visual final premium realista, sem low-poly, sem edifícios repetidos, sem vazios cinzentos ou ruas desconectadas.
- Primeiro **vertical slice 300 × 300m** com densidade e acabamentos, depois ampliar.
- Prints têm que ser **realmente da ferramenta declarada**. Captura do Blender não é foto do Unity nem prova de jogo jogável.
- Usar ativos comerciais/CC0 somente com proveniência e licenças; respeitar ODbL no conteúdo derivado.
- Não medir nem alegar FPS sem profile real. Não afirmar builds/parsing Unity quando só testes Python/Blender passaram.

## Handoff para R1

O escopo técnico continua definido na **Issue #1**. O ChatGPT trabalha em `chatgpt/r1-unity-foundation` e entrega um PR à `main` com:
- diff limitado ao escopo;
- como reproduzir os testes;
- evidências reais do que rodou e o que foi bloqueado;
- análise de orientação FBX e material URP;
- limitações sobre falta de licença de Unity;
- screenshot Unity **somente se Unity realmente rodou**.

O ChatGPT valida logs e capturas com transparência, registra aceite ou solicita correção; não confundir testes estáticos com execução Unity. Só então R2 começa. A documentação do R2 pode ser preparada sem iniciar implementação.

## Checkpoint

Ver `docs/STATUS.md` e Issues #1–#3. Atualizar o checkpoint após cada gate, incluindo SHA do commit, data, ferramentas e resultados. **Nunca marcar trabalho futuro como concluído.**

## Skills internas

Toda implementação consulta `docs/SKILLS_DE_PRODUCAO.md` e o `SKILL.md` específico dentro de `.agents/skills/`. São procedimentos locais para acelerar trabalho ChatGPT/GitHub; não instalam softwares por conta própria.
