# Resort Simulator — regras de produção e roteador de skills

Equipe nesta fase: **o ChatGPT assume direção e programação**, por solicitação do proprietário; **não invocar agentes Codex externos automaticamente**. Todo trabalho é conduzido a partir deste repositório; PC não é necessário para escrever código ou para os workflows Blender/Python, mas a Unity precisa de Editor real/licença para importação e build.

Antes de modificar qualquer coisa: ler `docs/STATUS.md`, `docs/DIRECAO_ARTISTICA.md`, `docs/FONTE_MAPA_BLENDER.md` e `docs/SKILLS_DE_PRODUCAO.md`. Consultar a skill mais específica em `.agents/skills/*/SKILL.md`.

**Mapa existente:** preservar `ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend` e `UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx`; área correta 2 km² = 2.000 × 1.000 m; jamais substituí-lo por cidade aleatória.

**Processo:** trabalhar em branch curta, testes automatizados, PR; registrar evidências e limitações honestas. Prioridade R1 Unity → R2 fachadas → R3 resort/orla. Não fingir screenshot Unity com imagem Blender e não anunciar build sem executar Unity.

**Licenças:** somente ativos com licença comercial verificável, OSM/ODbL sempre atribuído. Não armazenar senhas, tokens, licenças Unity nem ferramentas de acesso remoto no Git público.
