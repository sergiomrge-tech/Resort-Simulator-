# R2 — Biblioteca arquitetônica inicial | Realismo Estilizado Premium

**Status:** 3 PROTÓTIPOS Blender gerados, exportados e submetidos ao QA automático; **ainda não são edifícios completos nem estão aplicados ao mapa real**.  
**Criados:** 08/10/2026.  
**Fonte:** `Tools/Blender/build_r2_facades.py` (procedural original, sem materiais de terceiros).  
**Prévia REAL do Blender:** [Resort_R2_Fachadas_Premium_Blender_QA.png](../../ArtSource/Previews/Resort_R2_Fachadas_Premium_Blender_QA.png) (Cycles CPU, estúdio de QA, *não screenshot da Unity*).

## Catálogo persistente

| ID | Linguagem arquitetônica | Módulos e acabamentos | Arquivo FBX |
|---|---|---|---|
| `arch_r2_artdeco_orla_01` | Art déco histórico | calcário, pilastras caneladas, janelas altas, caixilhos bronze, molduras | `UnityProject/Assets/Architecture/R2_Prototypes/R2_ArtDeco_Orla.fbx` |
| `arch_r2_residencial_varandas_01` | Residencial com varandas | vidro, guarda-corpo, jardineiras, detalhes terracota e madeira | `UnityProject/Assets/Architecture/R2_Prototypes/R2_Residencial_Varandas.fbx` |
| `arch_r2_hotel_contemporaneo_01` | Hotel contemporâneo | vidro fumê, alumínio, brises, marquise, detalhes bronze | `UnityProject/Assets/Architecture/R2_Prototypes/R2_Hotel_Contemporaneo.fbx` |

Estes são **módulos de fachada de aproximadamente um pavimento**, não prédios completos de centenas de metros, nem malhas geográficas já adaptadas aos lotes. Não os replicar em todos os edifícios até a aprovação visual e a adaptação à tipologia local.

## Evidência disponível

- GitHub Actions (Blender headless): https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37858437555
- `ArtSource/Previews/Resort_R2_Fachadas_Premium_QA.json`: contagens por modelo, materiais, tamanho e SHA-256 de cada FBX + screenshot Blender.
- **4 testes Python reais aprovados**: presença de três tipologias, materiais diferentes, formato e SHA-256 dos três FBX, variação visual da imagem e integridade da fonte geográfica.
- Código Unity de revisão `UnityProject/Assets/Editor/ResortFacadePreviewBuilder.cs` gera `Assets/Scenes/R2_ArchitecturalReview.unity`, quando rodar no Editor com URP. Ainda não foi compilado/executado em Unity.
- Dados BlenderGIS e FBX de Copacabana continuam sendo a fonte de verdade; **não foram substituídos**.

## Materiais e limites

Os protótipos têm cores e valores de **metallic/roughness** controlados no Blender e material correspondente `URP/Lit` preparado no código Unity. **Mapas PBR de alta resolução, atlas, trims, normal maps e o acabamento final ainda precisam ser criados e integrados.** Portanto a biblioteca atual é um primeiro passe, não o padrão artístico aprovado de um jogo comercial.

**É proibido** preencher Copacabana com paredes modulares sem referência a lotes reais. A etapa de implantação requer os IDs dos lotes/footprints, correspondência entre altura/estilo e vias, afastamentos, entradas, navmesh, visibilidade e LOD.

## Próximas etapas visuais (sem voltar ao gameplay)

1. Avaliar a prévia Blender das três fachadas e corrigir aspectos que aparentem geometria simplificada.
2. Executar no Editor real da Unity 6.3 a cena de revisão R2, resolvendo eventuais erros de compilação e material.
3. Selecionar com base no OSM três lotes verificáveis na orla piloto 300 × 300 m, posicionar fachadas e validar com capturas reais da Unity.
4. Adicionar texturas PBR adequadas, volumetria de edifícios, quinas, térreos, cobertura e otimização progressiva.
5. Depois do piloto arquitetônico: praia, calçadão, mar, quiosques e resort, sempre preservando a geografia original.

**Regra de release:** não anunciar "R2 aprovada" sem captura real Unity, comparação entre edifícios e validação visual. Fase 2 de economia/IA de clientes continua arquivada em `main/docs/backlog/fase2-quiosque/`.
