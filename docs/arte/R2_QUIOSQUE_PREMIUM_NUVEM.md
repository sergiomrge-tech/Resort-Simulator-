# R2 — Quiosque Premium Autoral, Blender Cloud → Unity Assets

**Status:** modelo detalhado reproduzido no Blender e armazenado como FBX na pasta Assets. Testes cloud passaram; **Unity Editor, gameplay, captura de cena real e avaliação visual final ainda pendentes**.

## Origem e prova de fidelidade

O fonte `ArtSource/LocalProjectOwned/KioskPremium_20261008/build_kiosk_premium.py` foi arquivado anteriormente a partir do PC do proprietário. O novo `Tools/Blender/rebuild_owned_kiosk_cloud.py` executa **o mesmo código autoral**, substituindo apenas os dois caminhos de saída Windows que apontavam a `D:\\`, para funcionar no runner Linux de GitHub Actions.

As saídas reais do Blender foram geradas pela execução [37861618298](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37861618298).

| Indicador | Código original | Gerado na nuvem |
|---|---:|---:|
| Componentes | 307 | **307** |
| Polígonos | 34.468 | **34.468** |
| Triângulos | 68.008 | **68.008** |

Foi gerado `UnityProject/Assets/Architecture/OwnedKiosk/KioskPremium_Detailed.fbx` (FBX binário, aprox. 1,47 MB, GUID estável, SHA256 no relatório). O gerador não substitui a geometria de Copacabana e não depende de sessão Windows.

## Prévia real Blender

[Owned_KioskPremium_Blender_QA.png](../../ArtSource/Previews/Owned_KioskPremium_Blender_QA.png) — Blender Cycles CPU 1600 × 900.

A imagem é uma **renderização genuína da geometria original** reaberta a partir do arquivo .blend regenerado. As cores e propriedades de materiais foram aplicadas apenas para a revisão; elas **não** validam a integração com as texturas PBR finais do Unity.

## Reprodutibilidade e limites

- `Tools/Blender/rebuild_owned_kiosk_cloud.py`: reconstrói a obra original, exporta FBX, define GUID e gera o render.
- `Tools/tests/test_owned_kiosk_cloud.py`: verifica SHA256, componentes e polígonos, formato FBX, PNG e preservação das fontes GIS (quatro testes).
- `ArtSource/Previews/Owned_KioskPremium_QA.json`: inventário de evidências verificáveis.
- Arquivos .blend originais em `ArtSource/LocalProjectOwned/KioskPremium_20261008/` foram **preservados**, sem alteração.
- O jogo já possui roteiro narrativo de quiosque herdado, mas **nada nesta PR implementa a economia e a IA de clientes**.
- Para fazer parte do jogo, o modelo ainda precisará de importação Unity, materiais URP, posicionamento real na orla, LOD/colliders, testes com FPS e screenshot Unity genuíno.

**Próxima prioridade:** avaliar a direção premium do quiosque com a identidade da orla, integrar materiais e testar na Unity quando o GameCI estiver licenciado, continuando todo o desenvolvimento-fonte pelo GitHub.
