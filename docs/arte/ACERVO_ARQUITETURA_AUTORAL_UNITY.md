# Resort Simulator — oito modelos originais disponíveis para Unity (R2)

**Status:** exportados anteriormente do computador do usuário e preservados no GitHub; agora **copiados byte a byte para a pasta Assets da Unity**, com metadados/GUID estáveis. **Não houve importação/compilação no Editor Unity e não houve aprovação visual.**

## Biblioteca (identificadores persistentes)

| ID de catálogo | Origem | Papel arquitetônico |
|---|---|---|
| `coastal_owned_casa_terrea_01` | `casa_terrea.fbx` | Casa térrea |
| `coastal_owned_sobrado_01` | `sobrado.fbx` | Sobrado |
| `coastal_owned_loja_01` | `loja.fbx` | Loja |
| `coastal_owned_misto_01` | `misto.fbx` | Uso misto |
| `coastal_owned_apartamento_01` | `apartamento.fbx` | Apartamento |
| `coastal_owned_hotel_01` | `hotel.fbx` | Hotel |
| `coastal_owned_townhouse_01` | `townhouse.fbx` | Townhouse |
| `coastal_owned_residencial_sacadas_01` | `residencial_sacadas.fbx` | Residencial com sacadas |

Fonte editável de cada arquivo em `ArtSource/LocalProjectOwned/CoastalUrbanKit/` e cópia para importação em `UnityProject/Assets/Architecture/OwnedCoastal/`.

O arquivo `docs/arte/R2_OWNED_COASTAL_UNITY_ASSETS.json` registra os oito caminhos, os hashes SHA256 e os GUIDs. A origem das malhas é declarada em `ArtSource/LocalProjectOwned/CoastalUrbanKit/SOURCE.md`.

## Pipeline 100% GitHub
- `Tools/automation/stage_owned_coastal_fbx.py` compara origem/manifesto, copia sem modificar vértices ou geometrias e escreve GUIDs determinísticos.
- `Tools/tests/test_owned_coastal_fbx.py` verifica integridade binária, hashes, GUIDs e preservação do mapa.
- GitHub Actions: https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37861262361 — **SUCCESS; testes estáticos, não Unity Editor**.

## Regras de integração ao mundo
- É proibido preencher automaticamente os 1.468 footprints de edifícios OSM com oito modelos clonados. Primeiro conferir a identidade, escala, altura, orientação, estilo e acesso de cada lote.
- Não substituir `Copacabana_Real_Blender.fbx`, `Copacabana_BlenderGIS_UTM23S.blend`, estradas nem calçadão já georreferenciados.
- R2 (propostas de fachada PBR) continua como PR #10 draft; os novos modelos originais são um **acervo complementar**, não substitutos automáticos.
- As texturas PBR não estão garantidas no FBX; os materiais importados exigem ajuste URP e comparação com imagens originais. Nenhuma afirmação de shaders compilados.
- Teste posterior no editor Unity para ver sombras, escala métrica, colisões, variações de materiais, desempenho e captura **real Unity** antes de implantar.
- Fase de gameplay do quiosque (economia, NPCs e filas) permanece arquivada para depois de aprovação visual.

**Identidade visual:** Realismo Estilizado Premium, sem low-poly aparente. © OpenStreetMap contributors — ODbL 1.0 para os dados GIS separados.
