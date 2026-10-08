# Biblioteca de skills — Simulador de Resort
Atualizado em 08/10/2026. Objetivo: acelerar a criação do jogo diretamente pelo ChatGPT/GitHub, sem PC ligado.

**Estas skills são playbooks internos autorais, não plugins instalados e não executam sozinhas.** Reutilizar as instruções por tarefa; instalar integrações externas apenas se forem necessárias, revisadas e compatíveis com a nuvem.

## Prioridade e localização

| Etapa | Skill | Gatilho | Estado |
|---|---|---|---|
| R1 — fonte geográfica | `.agents/skills/geo-copacabana-fiel/SKILL.md` | Trabalhar no mapa OSM original | Pronta para uso |
| R1 — Blender | `.agents/skills/blender-sem-pc/SKILL.md` | Exportar FBX, renderizar e verificar | Pronta; já temos scripts reais |
| R1 — Unity Cloud | `.agents/skills/unity-github-sem-pc/SKILL.md` | Unity, scene builders, CI, input | Pronta; execução Unity requer licença |
| R2 — Arquitetura | `.agents/skills/predios-premium-pbr/SKILL.md` | Fachadas variadas e materiais premium | Preparada; gate R1 pendente |
| R3 — Resort | `.agents/skills/orla-resort-vertical-slice/SKILL.md` | Orla e resort cinco estrelas | Preparada; gates R1/R2 pendentes |
| Transversal | `.agents/skills/otimizar-cidade-unity/SKILL.md` | FPS/memória/LOD/culling | Preparada |
| Transversal | `.agents/skills/catalogar-assets-licenca/SKILL.md` | Adicionar qualquer asset externo | Pronta |
| Transversal | `.agents/skills/qa-capturas-sem-fraude/SKILL.md` | Validar screenshots/CI | Pronta |

| R4 — Operação do Tycoon | `.agents/skills/economia-tycoon-saves/SKILL.md` | Economia, estoque, funcionários, save | Preparada; posterior à R3 |
| R4 — Pessoas | `.agents/skills/npcs-animacao-trafego/SKILL.md` | Animação, pedestres, clientes e equipes | Preparada; posterior à R3 |
| R3 — Águas/terreno | `.agents/skills/agua-praia-piscinas-iluminacao/SKILL.md` | Oceano, praia, piscina, iluminação | Preparada; gate visual |
| R4 — Construção | `.agents/skills/construcao-modular-lotes/SKILL.md` | Lotes e construção modular | Preparada; posterior à R3 |
| R4 — Interface | `.agents/skills/hud-ux-gestao/SKILL.md` | HUD, menus e gestão | Preparada; posterior à R3 |

## Fontes pesquisadas na web (não copiados scripts terceiros)

1. **Unity Technologies/skills** — fonte oficial de skills para Unity: https://github.com/Unity-Technologies/skills
2. **Unity CLI / Unity Package Management** — skills oficiais: https://github.com/Unity-Technologies/skills/blob/main/skills/unity-cli/SKILL.md e https://github.com/Unity-Technologies/skills/blob/main/skills/unity-package-management/references/select-packages.md
3. **BlenderGIS** — integração entre Blender e dados reais GIS/DEM/OSM: https://github.com/domlysz/BlenderGIS
4. **Blender headless** — referência de execução sem janela: https://docs.blender.org/manual/en/4.5/advanced/command_line/arguments.html
5. **Blender MCP comunitário** — https://github.com/ahujasid/blender-mcp ; só considerar em máquina/Editor executando, pois não liga magicamente Blender ao GitHub; executar Python remoto é capacidade sensível e exige auditoria.
6. **GameCI** — automação Unity com credenciais/licenciamento: https://game.ci/docs/3/github/builder/ e https://game.ci/docs/3/github/activation/
7. **Poly Haven** — materiais, HDRI e modelos CC0: https://polyhaven.com/license
8. **ambientCG** — materiais PBR CC0: https://ambientcg.com/
9. **Unity Asset Store EULA** — verificar licença comercial e restrição de redistribuição: https://assetstore.unity.com/browse/eula-faq
10. **Performance Unity GPU** — profiling, render e occlusion: https://unity.com/how-to/gpu-optimization
11. **Unity AI Navigation** — NavMesh, rotas e agentes: https://docs.unity3d.com/Manual/com.unity.ai.navigation.html
12. **Unity JsonUtility** — persistência e serialização: https://docs.unity3d.com/ScriptReference/JsonUtility.ToJson.html
13. **Unity Shader Graph URP** — materiais água/efeitos: https://docs.unity3d.com/Manual/urp/prebuilt-shader-graphs-urp.html
14. **OSM copyright** — atribuição e licenças: https://www.openstreetmap.org/copyright

## Regras de adoção

- **Agora:** reutilizar biblioteca oficial Unity como **referência técnica**, sem instalar o cliente Unity CLI em ambiente que não tenha Editor.
- **Agora:** usar Blender headless existente no GitHub Actions. Não ativar servidor Blender MCP por padrão: exige addon/Editor e traz execução arbitrária de Python.
- **Agora:** skills de GIS/QA ativos para proteger fonte OSM e assegurar screenshots reais.
- **Depois do gate R1:** catálogo de três fachadas distintas com Poly Haven/ambientCG CC0, sem presumir que já foram baixados.
- **Depois de R2:** orla e construção do resort 300 × 300 m, progressivamente.
- **Depois do piloto visual R3:** NPCs, economia tycoon, construção modular, HUD e save, sempre com testes determinísticos.
- **Sempre:** códigos e dados integrados apenas por PR; **não confundir testes Python com build Unity**, não divulgar senhas, não importar software de terceiro sem revisão da licença e código.

## Limites de execução reais

O repositório já contém fonte Blender 3,1 MB, FBX real, previews Blender e C# Unity, mas **ainda não há prova de uma compilação Unity bem-sucedida**. O QA estático da branch `chatgpt/r1-unity-foundation` passou 7/7 em 08/10/2026, porém o GameCI foi pulado porque o projeto ainda não tem licença Unity nos Secrets. A próxima prioridade técnica é viabilizar o gate Unity sem tornar o PC obrigatório.
