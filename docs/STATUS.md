# Estado verificado — 08/10/2026

Projeto: **Resort Simulator — Costa Carioca**. Repositório único: `sergiomrge-tech/Resort-Simulator-` (independente de `Simulador-predial`).

## Entregas efetivamente verificadas

- Mapa Blender real de Copacabana **preservado no próprio Resort** em `ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend`.
- Exportação FBX original disponível em `UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx`; workflow de importação Blender no GitHub Actions concluiu com **success** (execução 37849494931).
- `geo/data/report.json`: 1.468 footprints de edifícios, 468 trechos de vias e 563 pontos de árvores **mapeados** no OSM; 2 km² de recorte previsto, com 1.398 alturas estimadas. Os dados OSM não criam 563 árvores 3D.
- Screenshot de **Blender** legível e produzido sobre a malha original: `ArtSource/Previews/Copacabana_REAL_BLOCO_3D_QA_COLOR.jpg`; workflow de QA visual **success** (execução 37850410679).
- Cena Unity ainda é **código editor de geração** `UnityProject/Assets/Editor/ResortWorldBuilder.cs`. Não há evidência de execução, compilação, captura ou FPS **na Unity**.
- Fontes Unity 6.3 / pacotes URP disponíveis; **não foi comprovada compatibilidade por compilação**.
- Não existe build Windows do Resort validada e publicada neste repositório.
- Sem arte final: fachadas premium, orla com areia/calçadão, resort cinco estrelas, montanhas e sistemas jogáveis continuam pendentes.

## Gestão de produção aprovada

- **Diretor (ChatGPT):** coordena, define especificações, faz review visual, escolhe prioridades e aprova gates. Trabalha em documentação e acompanhamento, não disputa arquivos de código do Luna.
- **Programador:** Codex **Luna Alto exclusivamente**, nunca Sol. Não atribuir a outra variante por conveniência. Execução depende de iniciar uma sessão de Codex; abrir Issue no GitHub **não inicia o agente**.
- Até três frentes, somente quando não colidirem em arquivos. Começar com R1 como **única frente liberada**. R2 e R3 estão descritas, mas bloqueadas por dependências visuais/técnicas.
- PC autorizado identificado como offline nesta verificação; este estado não implica falha do GitHub.
- Não prometer execução contínua em segundo plano; usar commits, Issues, PRs, testes e relatórios concretos por sessão.

## Backlog GitHub

1. **R1 — P0, liberada para Luna:** https://github.com/sergiomrge-tech/Resort-Simulator-/issues/1 — importar, validar e executar Copacabana na Unity, configurar CI com gate de licença. Branch: `luna/r1-copacabana-unity-gate`.
2. **R2 — P1, bloqueada por R1:** https://github.com/sergiomrge-tech/Resort-Simulator-/issues/2 — fachadas premium, texturas PBR, diversidade e LOD.
3. **R3 — P1, bloqueada por R1/R2:** https://github.com/sergiomrge-tech/Resort-Simulator-/issues/3 — resort cinco estrelas e orla piloto 300 × 300m.

## Gates de aceitação

- **Gate GIS/Unity (R1):** capturas reais Unity, orientação/eixos e escala por referência real, import sem erros, câmera operável, logs e build Windows quando licença permite. Sem licença, apresentar motivo, não inventar aprovação.
- **Gate de linguagem (R2):** pelo menos três prédios realmente distintos com screenshot verificável da Unity antes de expandir fachadas.
- **Gate de atratividade (R3):** validar visualmente trecho 300 × 300m com mar/praia, avenida, calçadão, quiosques e resort (não blocos cinzas), sem violar a geografia.
- **Mapa final:** preservar área 2 km², conter grandes vazios com vegetação/praças/edificações coerentes, não derrubar FPS e não depender de máquinas sempre ligadas.

© OpenStreetMap contributors, ODbL: https://www.openstreetmap.org/copyright.
