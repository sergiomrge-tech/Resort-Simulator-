# Project Resort — Executável de inspeção R5 para Windows

**Natureza:** visualização técnica executável **Windows x64**, não o jogo da campanha, build Steam, nem arte final.

## Build nativo realizado e verificado

- Editor: **Unity 6.6.2f1**, execução autorizada no PC de validação (disco D:).
- Origem: `UnityProject/Assets/Scenes/R5_Copacabana_50_Predios_EditorQA.unity`, que já havia passado na importação DX11 com 50 IDs OSM distintos e 1.181.354 triângulos.
- Cena jogável de voo livre (somente inspeção): `UnityProject/Assets/Scenes/R5_Copacabana_50_Predios_PreviewWindows.unity`.
- Builder reexecutável: `UnityProject/Assets/Editor/ResortR5WindowsPreviewBuild.cs`; navegação: `UnityProject/Assets/Scripts/R5VisualPreviewFlyCamera.cs`.
- Unity BuildPipeline result: **Succeeded**, `RESORT_R5_WINDOWS_PREVIEW_BUILD_PASS`, duração 59,19 segundos, tamanho de arquivos da build ~174,4 MB. A primeira tentativa de build foi interrompida porque o argumento de IPC do Package Manager tinha prefixo incorreto; a execução corrigida passou.
- **Smoke test real do EXE**: player nativo iniciado em modo `-batchmode -nographics`, permaneceu ativo 13 segundos, carregou Unity/Mono/PhysX/Input sem erro fatal, e foi encerrado pelo teste. Não equivale a FPS ou funcionamento de uma sessão gráfica de jogo.
- EXE SHA256: `af88b840e599661ac63fc10ae27ac77dd97cd46b44df8a7ce60eb0dcfacfc99e`
- EXE tamanho: 667.136 bytes. **Dependências acompanhando a pasta** (UnityPlayer.dll, `_Data`, `MonoBleedingEdge`, etc.) totalizam cerca de 174,4 MB; **não enviar o executável isolado**.

## Arquivos no PC (disco D:)

```text
D:\ProjectResort_Visual_Test_R5\Project_Resort_R5_Visual.exe
D:\ProjectResort_Visual_Test_R5\Project_Resort_R5_Visual_Data\
D:\ProjectResort_Visual_Test_R5\LEIA_ANTES_DE_TESTAR_R5.txt
D:\ProjectResort_Visual_Test_R5\R5_WINDOWS_BUILD_QA.json
D:\ProjectResort_R5_UnityQA\UnityProject\
```

**A build compilada está instalada/local no PC, não foi afirmada como download sandbox do chat ou release GitHub.** Os arquivos-fonte, cena Unity e builder estão no GitHub para reprodução. As configurações migradas automaticamente pela Unity 6.6 foram mantidas na cópia de testes e **não** foram incorporadas ao repositório de origem, que continua declarando Unity 6000.3.9f1.

## Controles

- `W A S D`: mover câmera;
- segurar **botão direito do mouse** e mover: olhar em todas as direções;
- `Q / E`: descer/subir;
- **Shift**: acelerar;
- **F11**: alternar tela cheia e janela;
- **Esc** ou botão **SAIR**: fechar a versão de teste.

## Limitações que permanecem

- 50 novos prédios modelados **no mapa real OSM** e 1.418 volumetrias antigas, ainda sem tratamento premium.
- O **voo livre não é gameplay final**, não há inventário, administração do resort, compras/estoque, campanha, NPCs ou quiosque funcional.
- Faltam materiais PBR premium, substituição progressiva dos blocos antigos, calçadas, areia, paisagismo e refinamento arquitetônico. O gate visual não foi aprovado.
- A build **não foi testada com jogador usando a janela gráfica**, só importação e câmera reais no Editor Unity DX11 + inicialização do standalone headless.
- Não há FPS médio medido, testes de gameplay completos nem publicação Steam.

**Próximo passo:** inspeção visual real no Windows, refinamento dos materiais e da paisagem, sistema de LOD e verificação de desempenho antes de ampliar os 50 edifícios procedurais para mais quarteirões.

© OpenStreetMap contributors — ODbL 1.0.
