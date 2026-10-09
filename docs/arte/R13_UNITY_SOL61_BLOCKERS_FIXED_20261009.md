# R13 — correção dos bloqueios do Sol 6.1 e validação real Unity (09/10/2026)

## Escopo
Este suplemento atualiza o checkpoint original de Sol em `R13_QA_REPORT.md`,
feito **antes** de a Unity funcionar. A arte 200m S05 continua em revisão,
o mapa 2.000 × 1.000 m não foi alterado, e R12/branch principal continuam
preservadas. Relatório técnico ≠ aprovação artística ou build jogável.

## Bloqueio 1 — acesso aos metadados Git do worktree
O comando do Codex, limitado ao sandbox `workspace-write`, tentava usar
`D:/ProjectResort_GitHub/.git/worktrees/ProjectResort_R13_Sol61_Orla/index.lock`,
fora do escopo gravável do agente. O trabalho de Sol foi concluído, mas
não pôde ser commitado/pushado no próprio sandbox. O supervisor autorizado
estagiou explicitamente apenas fontes/arte/QA/versão R13 fora do sandbox,
**excluindo** a regeneração R7 intermediária e o arquivo `.blend1`.
Nenhum reset/clean/merge foi feito. Commit/PR/workflow reais devem ser
verificados em GitHub após a publicação.

## Bloqueio 2 — Unity Package Manager no Windows
Sol executou o Editor em batch sem conseguir abrir `Upm-8248` em 30s.
Foi reutilizada a técnica validada R10–R12: iniciar o servidor Package Manager
instalado pela Unity com um nome IPC estável, e apontar a mesma IPC ao
Editor batch:
```powershell
$env:PROGRAMDATA='C:\ProgramData';$env:ProgramData='C:\ProgramData'
$env:ALLUSERSPROFILE='C:\ProgramData'
& 'C:\Program Files\Unity\Hub\Editor\6000.6.2f1\Editor\Data\Resources\PackageManager\Server\UnityPackageManager.exe' server --ipc-path Unity-Upm-R13QA -l 2 --log-file 'D:\ProjectResort_R8_UnityQA\UPM_R13_service.log'
# Em outra sessão, após iniciar o servidor:
& 'C:\Program Files\Unity\Hub\Editor\6000.6.2f1\Editor\Unity.exe' -batchmode -quit -force-d3d11 -accept-apiupdate -upmIpcPath Upm-R13QA -projectPath 'D:\ProjectResort_R8_UnityQA\UnityProject' -executeMethod ResortR13CoastalFinish.Build -logFile 'D:\ProjectResort_R8_UnityQA\R13_CoastalBuild_MetreScale.log'
```
A cópia QA `D:/ProjectResort_R8_UnityQA/UnityProject` já continha
a cena R12 importada/validada, por isso não precisou gerar novamente toda a
cadeia GIS no PC.

## Bloqueio 3 — meta do PNG importava as texturas como **Cubemap**
O Sol havia escrito `.meta` com apenas `fileFormatVersion` e `guid`.
No Editor Unity 6000.6.2f1 os 12 PNGs R13 foram importados
como **UnityEngine.Cubemap** em vez de `Texture2D`: o teste
`R13TextureProbe.Run` isolou `AssetDatabase.GetMainAssetTypeAtPath`
como `UnityEngine.Cubemap`, e o Build falhou com
`R13_BLOCKED:PBR_TEXTURE_IMPORT_FAILED:...r13_limestone_base.png`.

Correção persistente `Tools/geo/normalize_r13_unity_meta.py`: copia o
`TextureImporter` serializado v13 já versionado na R12, retendo **cada
GUID R13 original**, `textureShape: 1` para 2D,
`textureType: 1` + `sRGBTexture: 0` para normais, linear para masks,
sRGB somente para BaseColor. **Nenhuma imagem fonte foi descartada.**
Nova suíte `test_r13_unity_native_import_contract.py` impede regressão.

## Bloqueio 4 — FBX 100× maior que a cidade e câmera longe do mapa
O FBX R13 também possuía `.meta` de só duas linhas, e o modelo foi
importado implicitamente com escala **100×**. A câmera real registrou
`(-36846.66,-1.54,21682.80)` e a captura ficou uniforme, tamanho
21 KB. Este erro não é um problema no OSM ou no Blender.
A mesma normalização preserva GUID, mas configura o `ModelImporter`
Unity da R12 de forma explícita: `globalScale: 1`, `useFileUnits: 1`.
Depois de **reimportar o FBX e reconstruir a cena R13** a câmera ficou
`(-397.35,1.62,246.74)` e os 120 modelos R13 renderizaram no
mesmo universo R12. Um novo gate geométrico C# valida centro/extensões
do mosaico S05 para evitar regressão de escala.

## Bloqueio 5 — troca de cenas e estado SRP/ColorLut
Na tentativa de obter 12 capturas R12 antes / R13 depois **no mesmo
processo batch**, as seis primeiras foram geradas e, após trocar
a cena, `AssertionException: SetupColorLut colorAdjustments cannot be null`
deixou os quadros posteriores pretos.

`ResortR13VisualCapture.cs` agora fornece métodos separados:
- `ResortR13VisualCapture.RunBefore` — seis imagens R12 via Unity real.
- `ResortR13VisualCapture.RunAfter` — seis imagens R13 via **outra
  execução do Editor** (evita stack SRP residual entre cenas).
- `ResortR13VisualCapture.Assemble` — compara hash PNG SHA-256,
  câmera e ângulo/horário; recusa combinar capturas incompatíveis.

Cada render usa cinco quadros de aquecimento URP; os PNGs são de
**1600×900**, com câmera registrada e tamanho/contraste validados. O
comparador não manipula os frames; são 12 fotografias reais do Editor
Unity, não mockups, nem prova de FPS ou teste de Play Mode.

## Resultados nativos após correção
- Blender 5.2.1: 120 meshes, 274.745 faces no FBX; 54 fronteiras
  costeiras contíguas; UV0 finito; assets móveis 3 LODs; **PASS**
  no `test_r13_coastal_native.py`.
- Unity **6000.6.2f1**, **Direct3D11**, **RTX 4060 Ti**: cena derivada
  `Assets/Scenes/R13_Copacabana_200m_Premium.unity` gerada,
  `R13_UNITY_NATIVE_PASS meshes=120 roads=3731 trees=48
  missingUV=0 shaderErrors=0`; o gate de escala também passou.
- Capturas reais Unity **12/12, seis pares em três vistas e dois
  horários**, SHA iguais aos relatórios. Os dados técnicos foram
  copiados para `ArtSource/Previews/R13_UnityTechnicalQA.json`,
  `R13_VisualNativeQA.json` e PNGs `R13_S05_..._RealUnity.png`.
- Contratos `Tools/tests/test_r13_unity_native_import_contract.py`
  (4 casos) e `test_r13_contract.py` (6 casos) passaram localmente.
  São testes de evidência real versionada, não renderizadores falsos.
- Ações GitHub R13 executam o teste de importadores com arquivos
  versionados, e reconstroem a cadeia GIS/Blender no runner. Não afirmam
  executar Unity em um runner que não tenha o Editor.

## Qualidade visual: ainda **PENDENTE**
O depois R13 foi inspecionado: calçadão ondulado, peças de mosaico
visíveis, mobiliário costeiro, areia e água melhorados; mas a areia
está **clara demais e pouco definida**, solo urbano interior continua
cinzento, fachadas apresentam repetição e mobiliário/vegetação faltam
em nove setores. **Apenas S05 (200m) recebeu arte premium**, enquanto
S00–S04 e S06–S09 são base/fallback. Não há validação de animação da
água em Play Mode nem medição de FPS/drawcalls/VRAM, portanto o gate
de gameplay/arte/60 FPS continua PENDENTE. Não entregar como jogo
integrado nem alterar executável principal.

## Próximo checkpoint
O Sol deve continuar a aprimorar o setor-piloto com menor exposição
na areia, piso urbano, densidade tropical e fachadas; gerar uma cena
com iluminação ajustada e capturas reais comparáveis. Depois expandir
programaticamente aos demais nove setores e perfilar no PC. Integrar
ao repositório gameplay somente quando as coordenadas 900×720 m
legadas tiverem sido migradas para 2.000×1.000 m com quiosques,
NPCs, missões e saves comprovados em runtime.
