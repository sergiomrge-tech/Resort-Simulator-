# R13 — checkpoint nativo de 200 m, 09/10/2026

> **Atualização posterior (09/10):** Os bloqueios de Unity, importação de texturas/escala e capturas foram corrigidos e testados nativamente. O conteúdo abaixo é o checkpoint histórico do Sol ANTES dessas correções. Consulte **[R13_UNITY_SOL61_BLOCKERS_FIXED_20261009.md](R13_UNITY_SOL61_BLOCKERS_FIXED_20261009.md)** para os resultados novos. **Arte final, FPS e gameplay continuam pendentes.**


**Resultado:** assets e geradores materializados; Blender e regressões aprovados. **Arte, Unity e gameplay PENDENTES.** Não é versão comercial aprovada nem executável R13.

## Arte realmente produzida

- Piloto S05: eixo longitudinal **1.000–1.200 m**, x local **0–200 m**. Costa derivada do OSM `way/70574890`, mantendo frame 2.000 × 1.000 m / 46°.
- Mosaico com peças de aproximadamente 7 cm e rejunte/normal; mapas métricos próprios de areia, calcário e madeira. **12 PNGs PBR** (base/normal/metallic-smoothness), seed 13061.
- **8 conjuntos** com bancos de ripas, jardineiras abertas com solo, folhas curvas, lixeiras e paraciclos; bordas manufaturadas com bevel. LOD0/1/2 reais, agrupados por setor/material.
- Rodapés de pedra, reveals e weatherline aditivos em **14 fachadas OSM**. IDs enumerados em `R13_COVERAGE.json`. Não há cortes de portas nem novos interiores jogáveis.
- Água: geometria costeira com distância assinada em UV0 e shader URP candidato de swell, normal, Fresnel e espuma. **Shader ainda não compilado/testado em Unity; animação não comprovada em Play Mode.**
- FBX reimportado: **120 meshes, 274.745 triângulos**, incluindo superfícies/fallback dos dez setores e todos os três LODs do mobiliário piloto. Isso não é número de triângulos visíveis em runtime. FBX: 8.156.476 bytes nesta geração; hash em `R13_COVERAGE.json`.
- Fonte Blender e FBX reais versionados, texturas com caminhos relativos, `.meta` com GUIDs estáveis. Sem download de assets externos.

## Gates

| Gate | Estado | Evidência / limite |
|---|---|---|
| Fonte GIS | PASS | Hashes originais `.blend`, FBX, OSM, frame, assignments e 48 árvores preservados; 1.468 footprints intactos |
| Blender geração/export | PASS | Blender **5.2.1 LTS**, geometria construída e FBX exportado de verdade |
| Blender reimportação | PASS | `test_r13_coastal_native.py`, exit 0; contagem por malha idêntica, UV0/coords finitos e materiais não nulos |
| Continuidade longitudinal | PASS geométrico | **54 fronteiras compartilhadas**, comparadas em vértices reimportados das seis superfícies por setor; 2.000 m sem lacunas longitudinais |
| Mobiliário × vias | PASS limitado | Pontos amostrados dos oito conjuntos fora dos **3.731 triângulos originais**; não certifica toda colisão, acessibilidade ou footprint de cada friso |
| LOD | PASS Blender | LOD0 > LOD1 > LOD2 em todas as cinco categorias; distâncias/transições ainda precisam de tuning na Unity |
| Python / regressões | PASS | **27 testes**: R7 contrato 13, R8 winding/frame 1, integridade de capturas históricas R10 2 / R11 2 / R12 3, R13 dados/PBR/capturas 6. `py_compile` dos cinco scripts R13 passou |
| Render de assets Blender | PASS de produção | Dois PNGs Cycles reais 1600×900, hashes e câmeras em `R13_BlenderAssetVisualQA.json`; inspeção visual feita; **não são capturas do jogo** |
| Unity compilação/import/cena | PENDENTE — tentativa bloqueada | Unity **6000.6.2f1** instalada, mas servidor IPC do Package Manager não abriu; não chegou à compilação R13 |
| Imagens Unity antes/depois | PENDENTE | Capturador de 12 frames com mesma câmera/luz e cinco quadros de aquecimento implementado, ainda não executado |
| Arte premium 200 m | PENDENTE | Há melhoria materializada de piso/mobiliário; aprovação estética e contexto urbano na Unity faltam |
| Arte premium 2 km | PENDENTE | Apenas **S05** recebeu detalhes R13. S00–S04 e S06–S09 têm fallback do padrão R10, sem aprovação |
| FPS/CPU/GPU/VRAM | PENDENTE | Nenhum benchmark nesta sessão; 120 meshes não equivale a drawcalls ou 60 FPS |
| Gameplay/Windows | PENDENTE | Outro checkout preservado; nenhum teste de menus/saves/NPCs/build |
| Commit nesta branch | BLOQUEADO pelo filesystem | `git add` não pôde criar `D:/ProjectResort_GitHub/.git/worktrees/ProjectResort_R13_Sol61_Orla/index.lock`; metadados do worktree estão fora da área gravável. Nenhum commit criado na branch |
| GitHub/PR | BLOQUEADO pela rede local | Push tentou conectar a github.com:443 e falhou; sem publicação, PR ou merge |

## Erros encontrados e corrigidos

A primeira reimportação detectou **841 faces duplicadas em LODs reduzidos**. A decimação fechava detalhes finos sobre a mesma posição; o importador FBX descartava essas duplicatas. O gerador agora triangula e remove duplicatas/degenerações explicitamente preservando UV por loop. A rodada final passou com igualdade por malha, sem enfraquecer o teste.

O Blender emitiu deprecation de `Material.use_nodes` e aviso/erro ao escrever **thumbnail de interface** em `/.thumbnails`; exportação, salvamento do `.blend`, reimportação e renders reais concluíram com exit 0. Não foi erro do FBX nem do PNG de QA.

Unity local: o log `build/R13_Initial_Unity.log` registrou `Could not connect to IPC stream ... after 30.0 seconds` e `Failed to start the Unity Package Manager local server process`, seguido de saída de erro. Não atribuir a ausência do teste a falta de instalação/licença sem evidência. O launcher retornou 0 pelo shell, mas o **log nativo registra falha**, por isso não há PASS Unity.

Reconstrução local da cadeia R7–R12: R7 gerou os 50 modelos, mas não foi completada a máscara GIS/reconstrução por ausência de `pyproj`/`shapely`; pip foi bloqueado por WinError 10013. Modelos intermediários locais não fazem parte do commit R13. Workflow instala dependências em runner GitHub e recompõe a cadeia completa; **a execução Actions R13 ainda não aconteceu**.

A limpeza dos intermediários R7 foi rejeitada pela revisão automática (`blocked by policy`). Eles e o backup `.blend1` ficaram locais, fora da seleção de entrega. O stage também foi bloqueado por permissão nos metadados Git externos; **não houve commit**. O pacote de mudanças está nos arquivos novos do worktree e em `build/R13_DELIVERY.patch`, preparado com índice/objetos temporários dentro do workspace, sem escrever nas referências/índice do repositório original. Para finalizar o commit na branch solicitada é necessário um contexto com escrita autorizada nos metadados reais desse worktree.

## Evidências reais e execução

- `ArtSource/Previews/R13_Furniture_RealBlender_AssetQA.png`
- `ArtSource/Previews/R13_Mosaic_RealBlender_AssetQA.png`
- `ArtSource/Previews/R13_BlenderAssetVisualQA.json` — renderizador, versão, posição/target e SHA256.
- `UnityProject/Assets/Architecture/R13_Coastal/R13_COVERAGE.json` — setores, fontes/hash, meshes, câmeras e gates.

```powershell
python Tools/geo/generate_r13_surface_art.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b -t 4 --factory-startup --python-exit-code 1 --python Tools/Blender/generate_r13_coastal_slice.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b -t 4 --factory-startup --python-exit-code 1 --python Tools/tests/test_r13_coastal_native.py
python -m unittest discover -s Tools/tests -p test_r13_contract.py -v
```

Expansão posterior: mesmo gerador com `-- --sectors 0,1,2,3,4,5,6,7,8,9`; reexecutar reimportação e gates. Isso substitui **somente os derivados R13** e não aprova automaticamente os dez setores. O workflow `.github/workflows/r13-orla-premium.yml` usa a cadeia nativa R7→R12, gera o piloto R13 e publica assets/relatórios/renders Blender; não fabrica imagens Unity.

Após resolver Package Manager e materializar a base, executar `ResortR13CoastalFinish.RebuildChain` e `ResortR13VisualCapture.Run` no Editor real. A cena só será criada em `Assets/Scenes/R13_Copacabana_200m_Premium.unity` após passar os gates. Próximo checkpoint: **Unity compilada, shader/UV/materials conferidos, capturas pareadas dia/tarde e teste temporal da água**, depois revisão artística e expansão gradual. Não integrar gameplay nem fazer merge nesta fase.
