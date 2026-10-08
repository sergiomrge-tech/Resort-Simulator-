# Checkpoint — 08/10/2026

Novo repositório `Resort-Simulator-`, **inteiramente independente** de `Simulador-predial`.

| Item | Estado |
|---|---|
| Unity 6.3 LTS / URP 17.3 fixados | Estrutura fonte, sem parser Unity executado |
| Script de gerar cena real a partir de OSM OBJ | Código-fonte criado, importação Unity pendente |
| Aquisição independente de OpenStreetMap | Workflow GIS preparado; execução e resultado ainda não confirmados |
| Validação Python no GitHub | Pendente |
| GameCI Windows | Workflow preparado; licença nos Secrets necessária |
| APK/EXE, FPS ou prints Unity | NÃO gerados / NÃO validados |
| Fachadas PBR premium, resort e montanhas | Planejados; não implementados |

Próximo gate: exportação GIS real pela Actions -> commit modelo OBJ -> ativação Unity/GameCI -> build Windows -> captura Unity -> aprovado vertical slice.

## Mapa Blender existente (pedido do usuário)

`Copacabana_BlenderGIS_UTM23S.blend` já existe e foi validado no GitHub do projeto anterior. O novo workflow copia a fonte real para este repo e gera FBX para Unity; execução e inspeção Unity pendentes. Nenhuma malha de Copacabana é gerada novamente.
