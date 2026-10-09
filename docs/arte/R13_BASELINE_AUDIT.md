# R13 — auditoria da base R12 (09/10/2026)

Brief aprovado: `R13_SOL61_PROMPT_DE_EXECUCAO.md` e capítulos 0–13 de `R13_PLANO_COMPLETO_ORLA_PREMIUM_SOL61.md`, lidos antes da implementação. Branch exclusiva `codex/r13-sol61-orla-premium`. Nenhuma operação no checkout de gameplay.

## Evidências e severidades

| Severidade | Evidência concreta | Consequência / tratamento R13 |
|---|---|---|
| Alta | `R12_05_Mosaico_RealUnity.png`: três faixas lisas; areia com desenho de grande escala | Mosaico autoral com peças de aproximadamente 7 cm, normal e smoothness; areia granular em UV métrica |
| Alta | `generate_r9_urban_environment.py`: areia constante de 42 m e terreno horizontal | Continuar explicitando largura artística; linha costeira OSM preservada, areia seca/úmida e subdivisão sem alterar recorte |
| Alta | `R10_AnimatedOcean.shader`: cor por seno, sem iluminação normal/Fresnel físico coerente | Novo shader candidato R13 com normal temporal, iluminação URP, Fresnel e espuma em distância costeira; compilação/Play Mode pendentes |
| Alta | `R12_09_Vitrine_Letreiro_RealUnity.png`: repetição de vitrine, refletância desenhada, portas fechadas | Manter R12 e adicionar rodapé de pedra/reveals em 14 fachadas próximas; sem alegar interiores acessíveis |
| Alta | R8 agrupa 1.418 prédios por 50 estilos; R11 repete grades e coberturas | Não reduzir isso a “cidade premium pronta”. Detalhamento da cidade inteira permanece futuro |
| Média | Gerador R10 não contém mobiliário; R9 só 48 árvores OSM | Piloto recebe 8 conjuntos com banco de ripas, jardineira de pedra, folhas curvas, lixeira e paraciclos; plantio ficcional explicitado |
| Alta | Superfícies R9/R10 contínuas sobrepostas | Builder R13 desativa as superfícies substituídas somente na cena derivada e mantém via GIS, edifícios e árvores |
| Alta | Base de geração presente, mas FBX R7–R12/cenas R12 não materializados neste worktree | Workflow recompõe a cadeia; execução Unity local bloqueada por IPC do Package Manager, reconstrução local GIS sem dependências |
| Média | Nenhuma medição de FPS desta entrega | Budgets e LOD são engenharia, não benchmark ou aprovação |

## Inventário dos geradores preservados

| Gerador | Entrada / saída relevante | Extensão |
|---|---|---|
| R7 `generate_r7_buildings.py`, `assemble_r7_city_50.py` | Catálogo/OSM, 50 FBX UV0, cidade GIS mascarada | Reutilizado pelo workflow, fontes intocadas |
| R8 `generate_r8_full_city_facades.py` | 1.418 anéis/alturas/estilos, 350 meshes | Mantido |
| R9 `generate_r9_urban_environment.py`, `select_r9_vegetation.py`, `r9_tree_canopy.py` | OSM `way/70574890`, 48 árvores e superfícies | Costa e frame reutilizados; posições de árvores intocadas |
| R10 `generate_r10_coastal_details.py` | Buffers artísticos 25,5–38 m, mosaico/espuma | Padrão antigo preservado como fallback nos outros nove setores |
| R11 `generate_r11_architectural_detail.py` | Anéis reais, prismas outward, volumetria | Primitiva geométrica reutilizada para detalhes aditivos |
| R12 `generate_r12_storefronts.py`, `ResortR12StreetFinish.cs` | Entradas opacas, lojas fictícias, 19 meshes | Derivação da cena, sem sobrescrita |
| R13 `generate_r13_coastal_slice.py`, `generate_r13_surface_art.py` | Mesmas fontes, 10 setores e piloto S05 | Novos FBX/PBR/LOD/manifestos próprios |

## Piloto e realidade geográfica

S05 = distância longitudinal **1.000–1.200 m**, coordenada local **x=0–200 m**, EPSG:32723 relativo ao frame original, rotação 46°. O JSON de cobertura contém os endpoints costeiros, matriz de três câmeras por setor e hashes. Comprimento é medido no eixo longitudinal do recorte, não comprimento topográfico de arco. A largura de praia/passeio e o mobiliário são ambientação autoral, não levantamento. A altura e o footprint dos prédios não mudam.

Os nove demais setores têm geometria de continuidade/fallback; **nenhum tem acabamento R13 aprovado**. A captura antes/depois com mesma câmera permanece pendente de Unity. Render Blender de inspeção de assets, se produzido, não substitui esse gate.
