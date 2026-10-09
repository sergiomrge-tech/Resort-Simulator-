# SOL 6.1 — correções dos geradores R7

Checkpoint local em 09/10/2026, exclusivamente em `D:\ProjectResort_R7_Sol61`, branch `codex/sol61-geradores-local`, HEAD de base `ae098d7` (`codex/r7-acabamento-urbano-uv-pbr`). Durante esta sess?o o supervisor gravou externamente o checkpoint `3b48abf` neste checkout; o agente n?o executou esse commit. Destino autorizado para publicação pelo supervisor: **somente `HEAD:codex/sol61-geradores-r7`**.

**Estado: correções de código e testes locais concluídos; Blender/Unity nativos deste patch NÃO EXECUTADOS; arte NÃO APROVADA.** Os fatos R6 rejeitado, compile Unity R7 anterior aprovado e `R7_DERIVED_FBX_MISSING` foram fornecidos pelo supervisor. Não equivalem a validação deste patch.

## Evid?ncia nativa registrada pelo supervisor

O commit externo `3b48abf` acrescentou notas do supervisor, preservadas aqui sem executar ou acessar sua outra c?pia QA:

- Unity **6000.6.2f1**, Direct3D11, NVIDIA RTX 4060 Ti, sobre FBX R7 anterior SHA256 `576b01384531361a5218ee211c2d4f6176615440ac7f1bcd59e9547e96435a67`, com snapshot dos scripts C# SOL61.
- `ResortR7FacadeFinish.Build`: **PASS t?cnico registrado**; 50 edif?cios/50 estilos, 370 pe?as, fallback sem?ntico 0, 372 materiais incluindo dois de fundo, 40 texturas.
- `ResortR7VisualCapture.Run`: **PASS t?cnico registrado**; quatro capturas Unity reais, URP ativo, zero renderizadores sem UV0. As imagens ainda usam a geometria R7 anterior.
- Revis?o visual do supervisor: **FAIL**; aproximadamente 1.418 massas de fundo continuam simplificadas, e a c?mera de pedestre ficou obstru?da. Exposi??o/material URP melhoraram a apar?ncia, sem aprovar arquitetura ou enquadramento.
- O supervisor registrou os outputs em `D:\ProjectResort_R5_UnityQA\build\R7_PBR_FacadeQA`; o agente n?o acessou nem alterou essa pasta. N?o s?o capturas da nova geometria SOL61 nem medi??o de FPS.

## Falhas corrigidas

1. **Materiais após FBX import:** Blender pode duplicar datablocks como `R7_..._wall.001`. A montagem usava `rsplit('_')` sem remover o sufixo, rejeitando `wall.001`. `r7_contract.semantic_part` remove apenas sufixos numéricos finais, exige prefixo R7 e uma das nove categorias. Unity aceita esses sufixos e confronta a categoria do objeto com todos os slots, sem inferência visual ou Standard.
2. **Nomes individuais truncáveis:** o FBX individual usava estilo + `way_...` + categoria + `_mesh`. Agora objeto e mesh recebem, antes da primeira exportação, `R7B_<way>__<style>__<categoria>`; os nomes são verificados contra 63 bytes. OSM ID, estilo e categoria também são exportados como propriedades informativas; a integração exige nomes/slots e relatório, sem depender dessas propriedades sobreviverem à Unity. Todos os 1.468 IDs, inclusive `#part`, foram testados nas nove categorias.
3. **Janelas/sacadas invisíveis:** a parede contínua passava diante das peças recuadas. O gerador agora particiona a parede original ao redor de aberturas reais, cria revelos e separa pane, caixilho e fundo escuro em profundidade. Sacadas elegíveis têm abertura até a laje. O perímetro exterior continua no anel OSM; não se move rua ou centroide. A orientação das caixas e paredes agora funciona para anéis horários e anti-horários. A largura de janelas alternadas não diminui cumulativamente ao percorrer as baias.
4. **UV métrico nas diagonais:** a projeção pelo eixo dominante comprimia texturas em fachadas diagonais. A nova base ortonormal projeta cada face com 2 m por repetição. Todas as categorias emitidas passam pela mesma função, e a malha GIS derivada também recebe UV0. O teste nativo de reimportação exige UV finito, não colapsado e escala por aresta em cada mesh arquitetônico; compara a contagem exata com o relatório gerado, em vez de aceitar apenas `>=300`. **Não foi verificado nativamente neste checkout que os 370 meshes passaram.**
5. **Tesselação:** o código assumia que cada retorno de `tessellate_polygon` era índice. O adaptador aceita índices inteiros e pontos vetoriais, sem inferir a API pela versão. As faces superiores de cobertura têm normal para cima em ambos os sentidos do anel. O smoke nativo exerce a API real instalada antes do lote de 50.
6. **Mistura de artefatos/alinhamento:** a montagem valida hashes do gallery, máscara e OBJs, além de fontes e triângulos. Composição é matriz GIS original × translação do centroide × transform importado, com gate de frame rígido métrico Z-up. A máscara confronta anel e centroide do modelo com a atribuição congelada. O novo teste nativo abre o `.blend` original em memória, reimporta o FBX derivado e compara as 3.731 faces de rua em coordenadas mundiais, além do perímetro/altura das paredes. Fontes originais nunca são salvas.
7. **URP e exposição:** a cena usa seu próprio asset URP persistente, em vez de selecionar o primeiro asset arbitrário encontrado. Recursos de postprocess são exigidos. HDR, sombras do pipeline e sol com sombras são configurados; há luz ambiente explícita. ACES e exposição usam `Override`, e componentes do VolumeProfile são salvos como subassets e marcados dirty. Também se aplica URP/Lit aos dois slots da malha GIS de fundo; isso não converte os 1.418 volumes em arquitetura final. Texturas normais recebem importação linear e não são reconvertidas como mapas de altura.
8. **Captura SRP:** `Camera.Render()` foi substituído por `RenderPipeline.SubmitRenderRequest` com `UniversalRenderPipeline.SingleCameraRequest`, suportado pela API URP. A captura exige GPU real, pós-processamento salvo, shader URP/Lit em todos os materiais, UV0 e contagem exata igual ao material pass. Verifica frames uniformes/majoritariamente pretos ou brancos, preserva targets anteriores e registra SHA do FBX. O relatório corrige `materials_using_r6` para `materials_using_r7`. A inspeção humana continua necessária: diversidade de pixels não prova boa arte nem câmera desobstruída.
9. **Persistência:** regeneração preserva `.meta` já existente; GUIDs de novos assets usam caminhos POSIX determinísticos. A cena é salva como cena ativa R7, sem `saveAsCopy=true` deixar a identidade de uma cena temporária vazia.
10. **Expansão:** o antigo `start` do manifesto ordenado não correspondia ao `--mode city --start` do gerador. Agora o manifesto usa `plan_start`, registra esse frame de índices, marca os dois lotes R3 reservados para revisão manual e mantém os gates false. `--mode city` falha explicitamente nesta fase. Sem máscara R7 gerada, o plano diz `R5_BASELINE_SELECTION_R7_NOT_GENERATED` e materialized count R7 = 0. Nenhum lote restante foi aplicado.

## Testes e saídas verificadas localmente

- `test_r7_contract.py`: **12/12 PASS**. Exercita parsing real de sufixos, nomes de todos os IDs, formatos de tesselação, escala UV, partição de aberturas, normais dos boxes e o loop real de fachadas dos 50 estilos nos dois sentidos de anel. Esses testes de aritmética extraem as funções Python; não emulam Blender nem validam sua tesselação/exportação.
- `test_r7_uv_pbr_pipeline.py`: **9/9 PASS**, contratos estáticos de fonte, proteção de GIS, gates Unity e workflow. Dois asserts antigos, ligados à implementação literal de UV/nome, precisaram acompanhar a mudança; os testes executáveis acima cobrem seu comportamento.
- `py_compile`: PASS nos geradores, helper, máscara, expansão e testes nativos. Não valida a API bpy nem compila C#.
- Plano regenerado: **1.418 IDs, 29 lotes**, não aplicado; usa a máscara R5 como seleção provisória porque não há relatório R7 nativo neste checkout. Os 50 IDs de gallery correspondem a 50 estilos originais distintos; nenhum piloto selecionado tem anel interior.
- `git diff --check`: PASS. Avisos LF/CRLF do Git são informativos.
- Hashes originais, conferidos antes e após as alterações:
  - `.blend`: `2384c677bbb2ef8ef6275cb567ec52e69ff4b9e55d204d76eb0b10dfde2e4ac4`.
  - FBX: `2546ad26546713d40008c395a1a0d00eb2a3f90c1681f0bbbe3ad2c5410d9339`.

## CI, Git e limites reais

`gh run view 37902602095 --json status,conclusion,jobs` falhou por bloqueio de socket da rede gerenciada. O navegador também não conseguiu abrir o run. Não foram obtidos logs atuais ou resultado desse run; nenhum novo run foi iniciado. Blender executável e módulo bpy não estão disponíveis no Python local 3.14.7; bpy 4.5.3 exige Python 3.11. Unity Editor/licença/GPU não foram executados neste worktree. A compilação C# anterior do supervisor não cobre as mudanças novas.

`git add` dos arquivos explícitos falhou com `Unable to create .../index.lock: Permission denied`. O Git deste checkout guarda o índice do worktree em metadados fora da raiz gravável. Não foi tentado contornar a restrição, alterar outro worktree ou escrever naquele diretório. **Nenhum arquivo foi staged, nenhum commit/push/PR foi criado nesta sessão.** O supervisor deve publicar o patch a partir da sua autorização externa ao sandbox.

Workflow corrigido: trigger na branch `codex/sol61-geradores-r7` e PR; `contents: read`, sem commit/push automático de assets, concorrência por ref. Blender fixado em 4.5.3/Python 3.11; smoke nativo antes do lote, geração gallery sem cinco renders caros, máscara, assembly sem render e reimportação independente. Logs/provenance são enviados com `always()`, inclusive quando um estágio falha. O render real Blender de cidade é opcional via `render_preview=true` e só ocorre depois do primeiro gate de reimportação; o FBX é novamente validado após essa montagem. Um artifact parcial de run com falha **não é entrega aprovada**.

Não há FBX/cena/render novo nativo produzido nesta sessão. Renderizações, aparência de vidro/iluminação, colisões em polígonos côncavos, câmera em rua livre, escala Unity, API URP 17.3 em Editor 6000.6.2f1 e desempenho ainda precisam de prova nativa. Texturas procedurais são autorais; não se adicionou asset externo. Vegetação da branch separada não foi incorporada; refinamento das folhas fica após os gates R7.

## Reexecução exata

Na raiz deste repositório, para os checks locais:

```powershell
python -m unittest discover -s Tools/tests -p test_r7_contract.py -v
python -m unittest discover -s Tools/tests -p test_r7_uv_pbr_pipeline.py -v
python -m py_compile Tools/Blender/generate_r7_buildings.py Tools/Blender/assemble_r7_city_50.py Tools/Blender/r7_contract.py Tools/geo/r7_mask_city_50.py Tools/geo/r7_expansion_plan.py Tools/tests/test_r7_geometry_native.py Tools/tests/test_r7_exported_fbx_native.py
python Tools/geo/r7_expansion_plan.py
git diff --check
```

Em runner Linux com as dependências declaradas no workflow, Python 3.11/bpy 4.5.3:

```text
python Tools/tests/test_r7_geometry_native.py
python -c "import bpy,sys,runpy;sys.argv=['blender','--','--mode','gallery','--no-render'];runpy.run_path('Tools/Blender/generate_r7_buildings.py',run_name='__main__')"
python Tools/geo/r7_mask_city_50.py
python -c "import bpy,sys,runpy;sys.argv=['blender','--no-render'];runpy.run_path('Tools/Blender/assemble_r7_city_50.py',run_name='__main__')"
python Tools/tests/test_r7_exported_fbx_native.py
python Tools/geo/r7_expansion_plan.py
```

O supervisor deve transferir o artifact bem-sucedido completo: diretório `R7_Pilot50`, suas metas, gallery/scene/mask reports e `ArtSource/Previews/R7_FBX_UV_NATIVE_QA.json`. O builder Unity exige o hash do relatório de reimportação igual ao FBX. Na cópia QA autorizada do supervisor, com Editor real, executar `ResortR7FacadeFinish.Build`, depois `ResortR7VisualCapture.Run`. Não usar `-nographics` na captura. Exemplo com parâmetros preenchidos pelo supervisor para **sua** cópia isolada, não executado aqui:

```text
<UnityEditor.exe> -batchmode -quit -projectPath <QA_COPY>/UnityProject -executeMethod ResortR7FacadeFinish.Build -logFile <QA_COPY>/R7_Build.log
<UnityEditor.exe> -batchmode -quit -force-d3d11 -projectPath <QA_COPY>/UnityProject -executeMethod ResortR7VisualCapture.Run -logFile <QA_COPY>/R7_Capture.log
```

Próximo gate: commit/push exclusivo para `codex/sol61-geradores-r7`, Actions nativo bem-sucedido desse commit, importação/compilação e capturas Unity reais na cópia QA do supervisor, então revisão humana dos três estilos/rua. Expansão permanece bloqueada até aprovação visual e medição de desempenho.

Referências primárias consultadas: [bpy 4.5.3/Python 3.11](https://pypi.org/project/bpy/4.5.3/), [URP render requests](https://docs.unity3d.com/ja/current/Manual/urp/User-Render-Requests.html), [código oficial RenderPipeline](https://github.com/Unity-Technologies/UnityCsReference/blob/master/Runtime/Export/RenderPipeline/RenderPipeline.cs), [API oficial URP asset](https://github.com/Unity-Technologies/Graphics/blob/master/Packages/com.unity.render-pipelines.universal/Runtime/Data/UniversalRenderPipelineAsset.cs). Código atual das referências não substitui teste no Editor alvo.

© OpenStreetMap contributors — ODbL 1.0: https://www.openstreetmap.org/copyright.

## Triangulacao OBJ/Blender 4.5.3 (gate corrigido)
A auditoria de CI identificou 42 triangulos de rua particionados por diagonais diferentes (21 quadrilateros coplanares), sem alterar nenhum dos vertices, areas, contornos ou a contagem de 3.731 triangulos de rua. O montador so aceita a variacao quando os quatro vertices sao identicos, o quadrilatero e coplanar e as duas triangulacoes possuem exatamente a mesma borda e area. Toda outra discrepancia continua sendo erro. A remocao dos 50 lotes continua verificada contra o OBJ original importado pelo mesmo Blender, exigindo subtracao de edificios e vias absolutamente preservadas.
