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
| Contratos Python | PASS | 5 Pass2, 4 import/capturas R13, 6 contratos R13, 13 R7, 1 winding R8 |
| Blender imagens | PASS produção | Dois Cycles 1600×900 reais com hashes/câmeras; inspeção de assets sem cidade, não Unity |
| Unity import/shaders/UV | PASS inicial | 6000.6.2f1 / RTX 4060 Ti / D3D11: meshes=105, missingUV=0, shaderErrors=0, roads=3731, trees=48 |
| Capturas Unity | PENDENTE execução | Primeiro capturador recusou pipeline inativo; correção ativa o asset URP R7 na cópia derivada |
| Arte por setor | PENDENTE aprovação | S04–S06 INTERMEDIÁRIO; demais BASE com novas superfícies, sem novos detalhes |
| FPS/drawcalls/VRAM | PENDENTE | Não medidos; contagem de malhas/LOD não é benchmark |
| Gameplay/Windows/Steam | PENDENTE | Sem acesso ao gameplay, EXE, atalhos ou merge |

Tentativas Unity iniciais falharam pela separação de IPC entre sandbox e execução nativa. UPM e Editor no mesmo contexto resolveram licença/UPM. A captura seguinte detectou ausência de pipeline ativo no checkout limpo; o builder/capturador agora ativam explicitamente o asset R7. Versão do projeto alinhada a 6000.6.2f1 / URP 17.6.0. Nenhum segredo foi versionado.

## Reprodução

Gerar `generate_r13_pass2_surface_art.py`, executar Blender com `generate_r13_pass2.py` e `test_r13_pass2_native.py`, normalizar com `normalize_r13_pass2_meta.py`, produzir `report_r13_pass2_coverage.py` e executar `test_r13_pass2_contract.py`. Workflow recompõe cadeia R7–R13 antes do Pass2; não fabrica frames Unity em Linux.

No Editor real: `ResortR13Pass2Finish.Build`, `ResortR13Pass2Capture.RunBefore` / `RunAfter` em processos separados e `Assemble`. Copiar evidências de build/R13_Pass2_QA para ArtSource/Previews e regenerar cobertura. As fontes e cenas antigas permanecem intactas.

## Limites e próximo checkpoint

Pavimento continua plano urbano texturizado, não uma rede recortada de calçadas/sarjetas/guias. Arquitetura de fundo R8/R11 ainda repete. Sem quiosques novos, árvores novas de porte, interiores, fiação ou noite. Dossel R9 preservado com UV0 no derivado. Distribuição do mobiliário ainda regular; postes sem luz noturna ativa. Nenhum setor é PREMIUM aprovado. Revisar os frames Unity, enriquecer conexões rua/passeio com geometria real e diversidade antes de expandir detalhes aos sete setores restantes. Não declarar concluídos os 2 km.
