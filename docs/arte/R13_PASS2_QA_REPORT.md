# R13 Passo 2 — QA da camada derivada, 09/10/2026

Geometria/arte produzidas; aprovação artística PENDENTE. Cena alvo: `Assets/Scenes/R13_VisualPass2.unity`. R7–R13 anterior preservadas.

## Entrega materializada

Dez setores com areia seca/úmida de albedo contido, normal fina, mosaico métrico global e superfícies conectadas. Praia/passeio são ilustrativos, não levantamento. S04/S05/S06 recebem 24 grupos de banco, jardineira/folhas curvas, lixeira, paraciclos e postes novos de 3,55 m, em batches por material/setor com LOD0/1/2. Acessórios seguem individualmente a curva costeira e larguras variam por hash. As 24 fachadas próximas têm overlays decorativos de rodapé/reveals e três presets por building_id; sem interiores acessíveis ou recorte de portas.

21 PNGs autorais PBR: mosaico, areia seca/úmida, calcário, madeira, asfalto e pavimento (base/normal/mask). Shader URP Pass2Sand mistura a faixa úmida/seca entre 2,5 e 10 m com normal fina, desgaste próximo do passeio e sombra do sol. Mantém shader de água R13; animação em Play Mode PENDENTE. Builder cria UV0 em cópias das 48 árvores, mantém seus pontos e aplica pavimento/asfalto às malhas existentes, sem modificar fontes anteriores.

## Gates

| Gate | Estado | Evidência/limite |
|---|---|---|
| Blender geração/export/reimport | PASS | 5.2.1 LTS: 105 meshes, 516.024 triângulos incluindo LODs, UV0 finito, materiais presentes e contagem por malha idêntica |
| Continuidade | PASS geométrico | 54 fronteiras reimportadas; seis superfícies em dez setores |
| GIS | PASS | Hashes preservados, 1.468 footprints, frame 2.000×1.000 m, 48 nós e 3.731 triângulos de vias |
| Mobiliário × vias | PASS limitado | Âncoras/amostras de 24 grupos contra a malha original; não certifica toda colisão/acessibilidade |
| Importers | PASS estático | 21 TextureImporter v13/textureShape 1; ModelImporter globalScale 1; GUIDs preservados |
| Contratos Python | PASS | 37 testes: 6 Pass2 + 31 regressões R7/R8/R10/R11/R12/R13; py_compile de sete arquivos Pass2 |
| Blender imagens | PASS produção | Dois Cycles 1600×900 reais com hashes/câmeras; inspeção de assets sem cidade, não Unity |
| Unity import/shaders/UV | PASS final | 6000.6.2f1 / RTX 4060 Ti / D3D11: meshes=105, missingUV=0, shaderErrors=0, roads=3731, trees=48, treeUVmissing=0, 21 Texture2D, zero slots de material ausentes |
| Capturas Unity | PASS produção e pareamento | 60 PNGs reais: 30 antes + 30 depois, S04/S05/S06 × cinco vistas × dia/tarde, mesma câmera/luz/GPU/URP17.6, cinco quadros de aquecimento |
| Arte por setor | PENDENTE aprovação | S04–S06 INTERMEDIÁRIO; demais BASE com novas superfícies, sem novos detalhes |
| FPS/drawcalls/VRAM | PENDENTE | Não medidos; contagem de malhas/LOD não é benchmark |
| Gameplay/Windows/Steam | PENDENTE | Sem acesso ao gameplay, EXE, atalhos ou merge |

Tentativas Unity iniciais falharam pela separação de IPC entre sandbox e execução nativa. UPM e Editor no mesmo contexto resolveram licença/UPM. A captura seguinte detectou ausência de pipeline ativo no checkout limpo; o builder/capturador agora ativam explicitamente o asset R7. Versão do projeto alinhada a 6000.6.2f1 / URP 17.6.0. Nenhum segredo foi versionado.

## Reprodução

Gerar `generate_r13_pass2_surface_art.py`, executar Blender com `generate_r13_pass2.py` e `test_r13_pass2_native.py`, normalizar com `normalize_r13_pass2_meta.py`, produzir `report_r13_pass2_coverage.py` e executar `test_r13_pass2_contract.py`. Workflow recompõe cadeia R7–R13 antes do Pass2; não fabrica frames Unity em Linux.

No Editor real: `ResortR13Pass2Finish.Build`, `ResortR13Pass2Capture.RunBefore` / `RunAfter` em processos separados e `Assemble`. Copiar evidências de build/R13_Pass2_QA para ArtSource/Previews e regenerar cobertura. As fontes e cenas antigas permanecem intactas.

## Limites e próximo checkpoint

Pavimento continua plano urbano texturizado, não uma rede recortada de calçadas/sarjetas/guias. Arquitetura de fundo R8/R11 ainda repete. Sem quiosques novos, árvores novas de porte, interiores, fiação ou noite. Dossel R9 preservado com UV0 no derivado. Distribuição do mobiliário ainda regular; postes sem luz noturna ativa. Nenhum setor é PREMIUM aprovado. Revisar os frames Unity, enriquecer conexões rua/passeio com geometria real e diversidade antes de expandir detalhes aos sete setores restantes. Não declarar concluídos os 2 km.

## Revisão visual efetivamente realizada

A areia S05 perdeu a faixa branca estourada do checkpoint e tem transição úmida/seca gradual; os frames dia/tarde mantêm a mesma luz do antes. As primeiras imagens do Pass2 revelaram quadriculado macro e UV de piso esticada. A versão entregue remove a macrotextura periódica na areia, usa variação lenta global no shader e projeta pavimento/asfalto pelos pontos transformados do FBX em metros no mundo; há gate de extensão UV para detectar novo colapso. Renders Blender e PNGs Unity foram refeitos após essas correções.

As câmeras herdadas tinham vista transversal; foram preservadas para o comparativo e complementadas por vistas `pedestrian` e `city` orientadas pelo vetor real entre setores importados. Todas as cinco vistas têm pares dia/tarde nos três setores. Foram inspecionadas as vistas de pedestre, costa e cidade, incluindo S04 e S06. A areia ainda é simplificada e o piso urbano segue extenso e uniforme; postes e vegetação melhoram a faixa costeira, mas a distribuição continua regular. A arquitetura e os térreos não atingiram o padrão premium final.

| Setor | Estado real | Malhas novas (inclui LODs) | Grupos mobiliário | Fachadas decorativas | PNGs depois |
|---|---|---:|---:|---:|---:|
| S00 | BASE costeira atualizada, revisão visual pendente | 6 | 0 | 0 | 0 |
| S01 | BASE costeira atualizada, revisão visual pendente | 6 | 0 | 0 | 0 |
| S02 | BASE costeira atualizada, revisão visual pendente | 6 | 0 | 0 | 0 |
| S03 | BASE costeira atualizada, revisão visual pendente | 6 | 0 | 0 | 0 |
| S04 | INTERMEDIÁRIO, capturado, arte pendente | 21 | 8 | 6 | 10 |
| S05 | INTERMEDIÁRIO, capturado, arte pendente | 21 | 8 | 14 | 10 |
| S06 | INTERMEDIÁRIO, capturado, arte pendente | 21 | 8 | 4 | 10 |
| S07 | BASE costeira atualizada, revisão visual pendente | 6 | 0 | 0 | 0 |
| S08 | BASE costeira atualizada, revisão visual pendente | 6 | 0 | 0 | 0 |
| S09 | BASE costeira atualizada, revisão visual pendente | 6 | 0 | 0 | 0 |

Evidências principais:
- [S05 antes, costa de dia](../../ArtSource/Previews/R13_Pass2_S05_before_day_coast_RealUnity.png) / [S05 depois, mesma câmera e luz](../../ArtSource/Previews/R13_Pass2_S05_after_day_coast_RealUnity.png).
- [S05 pedestre](../../ArtSource/Previews/R13_Pass2_S05_after_day_pedestrian_RealUnity.png), [S04 pedestre](../../ArtSource/Previews/R13_Pass2_S04_after_day_pedestrian_RealUnity.png), [S06 pedestre](../../ArtSource/Previews/R13_Pass2_S06_after_day_pedestrian_RealUnity.png).
- [S06 cidade](../../ArtSource/Previews/R13_Pass2_S06_after_day_city_RealUnity.png), [S05 fim de tarde](../../ArtSource/Previews/R13_Pass2_S05_after_late_pedestrian_RealUnity.png).
- `R13_Pass2_VisualNativeQA.json`: 60 hashes PNG, câmera, resolução 1600×900, FOV 53, clipping, sol/intensidade, GPU, renderer e URP.
- `R13_Pass2_NativeExecution.json`: hashes dos scripts/arte/cenas QA e linhas de gates nativos sanitizadas, sem licenças ou tokens.
- `R13_Pass2_PythonQA.json`: resultado de 37 testes locais; não é prova de build Unity.

O pipeline ativo e os pacotes do checkout limpo estavam atrasados em relação ao checkpoint do PC: alinhados a Unity 6000.6.2f1, URP17.6.0, InputSystem1.20.0 e Navigation2.0.14. InputSystem1.18 gerou CS0619 antes da correção. Configuração final compilou, importou e renderizou nativamente. Os arquivos de origem na outra cópia QA foram apenas lidos; toda geração ocorreu neste workspace.

No CI, um FBX reexportado com bpy4.5 pode ter bytes diferentes do checkpoint Windows Blender5.2. O relatório de cobertura só associa os PNGs Unity ao FBX quando o hash técnico coincide; caso contrário as imagens históricas continuam preservadas, mas o artefato regenerado fica com visual Unity PENDENTE. Isso evita certificar por screenshot um FBX diferente.

Publicação GitHub/CI: em verificação após push; este relatório será suplementado com a URL e resultado reais. Nenhum merge foi autorizado/executado.
