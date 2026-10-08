# R2 — revisão real no Blender das oito edificações originais

**Status:** biblioteca visual de referência, ainda aguardando revisão artística e validação Unity. **Nenhum modelo foi inserido em lotes geográficos ou considerado definitivo.**

## Prévia e relatórios

- [Prancha Blender 1600 × 1000 (Cycles CPU, render real)](../../ArtSource/Previews/Owned_CoastalUrbanKit_Blender_QA.png)
- [Laudo original do import Blender/FBX](../../ArtSource/Previews/Owned_CoastalUrbanKit_QA.json)
- [Fonte editável e FBX originais](../../ArtSource/LocalProjectOwned/CoastalUrbanKit/SOURCE.md)
- [GitHub Actions — importação FBX, render, testes](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37861282583)

Todos os modelos foram importados dos FBX versionados no GitHub, medidos no espaço de mundo **antes** de ajustar o tamanho para a prancha. A renderização em galeria escalonou cada tipologia **somente para enquadramento da revisão**, não aplicou escala ao modelo original nem editou o mapa de Copacabana.

## Catálogo verificado em Blender

| Tipologia original | Faces no FBX reimportado | Dimensões geométricas X × Y × Z (m) |
|---|---:|---|
| Casa térrea | 2.046 | 9,45 × 14,13 × 4,82 |
| Sobrado | 3.768 | 9,22 × 15,88 × 6,88 |
| Loja | 1.344 | 10,22 × 13,49 × 5,31 |
| Uso misto | 3.444 | 10,22 × 16,88 × 7,11 |
| Apartamento | 7.440 | 11,22 × 17,88 × 9,88 |
| Hotel | 9.276 | 12,22 × 18,68 × 10,11 |
| Townhouse | 2.796 | 6,62 × 15,88 × 6,98 |
| Residencial com sacadas | 4.692 | 12,22 × 16,88 × 8,08 |

Estas medidas são do **FBX importado de volta ao Blender** e não alturas reais dos edifícios de Copacabana. Os modelos são originais do projeto local, não cópias de prédios fotografados. As texturas PBR usadas no jogo e materiais URP necessitam configuração/inspeção própria.

## Integração com Unity

Os mesmos oito arquivos estão no UnityProject, com GUIDs e hashes estáveis, por meio da [PR #14](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/14) integrada à `main`.

- `UnityProject/Assets/Architecture/OwnedCoastal/` contém os modelos prontos para importação **ao abrir o Editor**.
- `docs/arte/R2_OWNED_COASTAL_UNITY_ASSETS.json` registra IDs de catálogo e SHA256.
- O scanner de SHA256 e Blender QA rodam na nuvem, sem acesso ao computador do proprietário.
- A fonte `Copacabana_Real_Blender.fbx` continua preservada.

**Gate visual:** comparar modelos a partir de capturas reais na Unity 6.3, corrigir low-poly aparente, repetição de fachada, cor/textura PBR, encaixe em lotes, LOD, colisões e performance. Só depois instalar no piloto da Avenida Atlântica, nos três IDs OSM já selecionados em R2. Nenhuma dessas verificações Unity está concluída nesta PR.

**Fase 2 de gameplay:** economia, estoque, interações e IA de clientes continuam arquivados, sem interferir na produção visual.
