# Project Resort — R13 | Plano mestre de aprimoramento visual de TODA a orla de Copacabana
**Diretor de arte e integração:** ChatGPT (coordenação); **executor designado:** Codex Sol 6.1, esforço **medium**.  
**Base verificável:** branch `codex/r12-urban-storefronts`, commit `afa4dfaf9d0bca735c574b0f72c10411d7968ad0`.  
**Branch exclusiva:** `codex/r13-sol61-orla-premium`.  
**Motor e pipeline:** Unity **6000.6.2f1**, URP 17.6 / Blender 4.5+ (Windows QA Blender 5.2), GitHub Actions, C# / Python.  
**Data do contrato:** 2026-10-09. **Não é especificação de feature jogável concluída.**

## 0 — Missão, prioridade e direção artística inegociáveis
Elevar os **2 km inteiros de frente marítima de Copacabana e seus 1 km de profundidade interior** a um bairro urbano tropical brasileiro **convincente na escala humana**, com riqueza de superfícies e fachadas, coerência viária e costeira, iluminação fotográfica contida, alta diversidade visual e bom desempenho. **PROIBIDO low-poly aparente**, massa de prédios brancos ou cinzentos sem textura, árvores genéricas, quadrado azul plano de mar, chão sem contexto, cru/pouco trabalhado, texturas esticadas, blocos repetidos de arquitetura e captura falsa de execução. Não se exige cópia cadastral/fotográfica de imóveis de particulares nem precisão cartográfica onde a fonte não a fornece. O resultado deve parecer uma produção comercial de simulação para PC/Steam, não demo de geração procedural.

A orla deve ter continuidade natural em todos os 2.000 metros, do começo ao fim do recorte, não apenas 50 metros bem-polidos diante da câmera de teste. **O eixo de 2 km precisa ser paralelo ao litoral**; o segundo eixo de 1 km é profundidade terrestre. **Não diminuir nem ampliar**, deslocar, girar, descaracterizar ou desconfigurar os lotes OSM. Preservar a orientação geográfica `R4_SOURCE_FRAME.json` e os materiais/texturas anteriores, aprimorando sem regredir.

### 0.1 — REGRA DE REALIDADE E FONTES
- O conjunto R7–R12 é a base visual **técnica**, mas **não** a versão final aprovada. Nenhum frame de Blender, arte conceitual ou imagem sintetizada deve ser chamado de screenshot do jogo. Use capturas **reais** da Unity e metadados de versão de Editor, câmera, renderer, dispositivo e SHA do PNG.
- OpenStreetMap é base de posição e de alguns atributos; não afirmar que a altura, fachada, uso comercial, espécie botânica, vitrine, largura da praia ou entrada foram medidos sem fonte. Respeitar ODbL e documentos de licenças de assets externos. Imóveis/marcas reais identificáveis não devem ganhar letreiros inventados apresentados como autênticos. Letreiros R12 são **fictícios**.
- **Só usar assets legalmente compatíveis com redistribuição** (CC0, CC-BY atribuído, conteúdo autoral etc.) e registrar: URL, autor, licença, data, pasta e atribuição. Não puxar texturas protegidas do Google Maps/Street View.
- Aplicar PBR URP/Lit ou shader URP próprio testado. Todo material deve ter BaseColor, rugosidade/smoothness plausível, metallic coerente, normal/height quando útil e UV0 reais. Proibir renderizadores Unity com material branco padrão como substituto de arte ausente.
- Nunca chamar de concluído o que ainda não foi compilado, renderizado ou testado em runtime. Falhou algum gate? Documentar e manter pendente. **Não fazer merge na main**.

## 1 — Estado que já existe e DEVE ser aproveitado, não recriado do zero
| Etapa | Artefato/implementação | Números/limitação |
|---|---|---|
| R4 | `geo/procedural/R4_SOURCE_FRAME.json`, atribuições OSM | **2.000 × 1.000 m**; 1.468 edifícios mapeados |
| R7 | 50 construções-piloto PBR, GIS vias | **3.731 triângulos reais de ruas**; estilos e materiais aprovados tecnicamente |
| R8 | `Tools/Blender/generate_r8_full_city_facades.py` | **1.418** edifícios restantes, 50 estilos, fachadas + vidros; winding CW corrigido |
| R9 | `Tools/Blender/generate_r9_urban_environment.py`; `select_r9_vegetation.py` | praia/mar pelo OSM, 19 áreas verdes/água, 48 árvores selecionadas, excluídas de ruas |
| R10 | `generate_r10_coastal_details.py`, `R10_AnimatedOcean.shader` | mosaico e espuma costeira ilustrativos, shader temporal, 150 materiais de fachada |
| R11 | `generate_r11_architectural_detail.py` | 6.048 varandas em 888 edifícios, 1.414 coberturas técnicas, 1.355 cornijas; **formas ainda repetitivas** |
| R12 | `generate_r12_storefronts.py`, `ResortR12StreetFinish.cs` | 1.411 entradas decorativas, 320 lojas fictícias, 1.627 vitrines, 12 artes e 2 mapas de vidro **não físico** |

Documentos de leitura obrigatória: `docs/arte/R8_GERADOR_1468_PREDIOS_2X1KM.md`, `R9_ORLA_SOLO_ARBORIZACAO_QA.md`, `R10_ORLA_50_FACHADAS_ILUMINACAO.md`, `R11_ARQUITETURA_VOLUMETRIA_QA.md`, `R12_FACHADAS_LOJAS_VITRINES.md`, `README.md`, `AGENTS.md` e workflows GitHub R8–R12. Ler as capturas reais R10–R12 em `ArtSource/Previews` como evidência de problemas e diretriz de contraste, não como arte final.

**Repositórios NÃO são iguais!** A fonte visual atual é `sergiomrge-tech/Resort-Simulator-`. O jogo principal com gameplay está no repositório **separado** `sergiomrge-tech/Simulador-predial`, cuja cópia de PC é `D:\sergi\Documents\Simulador-predial\FacilityOps` e contém mudanças locais não commitadas. **NÃO misturar árvores Git, não sobrescrever esse checkout sujo, não copiar `FacilityOps` para `UnityProject` cegamente.** Preparar plano/integração por branch limpa e cópia de QA isolada, somente depois de gates. O PC já tem dois atalhos: jogo principal jogável e visualizador 3D R12, distintos.

## 2 — Auditoria P0 antes de criar arte
1. Inventariar **todos** os geradores R7–R12: entradas, saídas, meshes, source frame, coord OSM e nome de materiais; gerar `docs/arte/R13_BASELINE_AUDIT.md` com lacunas concretas em vez de números inventados. Conferir geometria do litoral original e transparência das texturas R12; evitar colisão visual de múltiplos planos `R9_URBAN_PAVEMENT`, areia, asfalto, mosaico e espuma.
2. Criar matriz de teste do mundo em segmentos de **200 m**, dez segmentos (0–200 até 1800–2000 m) + pontos transversais de calçadão, beira da água e quarteirão interior. Para cada: posição (mundo), orientação, material, defeito, severidade, antes/depois com câmera igual.
3. Auditoria de referências rotas: praia vs. ruas vs. lotes; fachadas voltadas para fora, triângulos de calçada sem z-fighting, terreno dentro do recorte; UV sem espelhamento de sinalização; escala humana (portas ~2–2,5m, árvores proporcionais, passeios plausíveis).
4. Dar inventário dos assets prontos e faltantes. Sempre preferir geradores **paramétricos, determinísticos e com presets** ao trabalho manual 1.468 vezes. Prever meshes/material atlases por bairro e fachada com instancing/LOD; não produzir 1.468 drawcalls únicos para detalhes minúsculos.
5. Criar relatório que discrimine o que é verificável do OSM e o que é *ambientação ficcional plausível*.

## 3 — P1 A orla inteira: geometria e paisagem costeira
**3.1 Mar e praias.** Reavaliar a faixa gerada na R9: largura constante de 42m foi ilustrativa. Usar linha costeira OSM para orientar a praia contínua, com transição areia seca/úmida, curva sem retas artificiais, granulação, duna/marcas, microvariação de tonalidade, áreas de pisoteio sem ruído exagerado. Implementar albedo/roughness/normal de areia realista, tiling em metros, ruído multifrequência com limites, transição suave do oceano à areia, espuma à margem, ondas deslocando-se na direção certa, movimento temporal lento e não padrão repetitivo. O mar deve ter cor azul/esmeralda costeira, variação de profundidade e brilho por ângulo, sem chapa chapada, clipping, reflexo impossível, ondulação em escala errada ou malha brilhante uniforme. Evitar volumetria pesada no horizonte. Atualizar o shader URP e testar Play Mode com `_Time`; **captura parada não comprova animação**.
**3.2 Calçadão de Copacabana.** Corrigir padrão ondulado para leitura de pedra portuguesa em escala aproximada de pessoa, com peças de mosaico físico / detalhe normal/mapa, rejunte sutil, duas tonalidades de pedra, acabamento UV metrificado e curvas que acompanhem todo litoral. O modelo R10 é aproximação de 25,5–38m da água; não afirmar medida real. Não sobrepor faixas de rua. Incluir rampas de acesso/limites apropriados, transições pedestre/ciclovia/asfalto onde fizerem sentido; faixa verde entre avenida e calçadão quando coerente, sem cacos ou descontinuidades.
**3.3 Mobiliário fixo da orla.** Quiosques distintos e completos (coberturas, balcões, mobiliário, detalhes PBR, luminárias, lixeiras), bancos, canteiros, jardineiras, guarda-sóis, chuveiros/lava-pés, bebedouros, placas públicas, postes, caixas de utilidades, paraciclos, proteções e sinalização apropriada. Conjunto modular coerente (ex.: 8–16 famílias reutilizáveis, com variações de material e composição), nunca 2.000 cópias idênticas. Distribuir com regras de acessibilidade/circulação e espaçamento; evitar objetos dentro de via/água ou suspensos.
**3.4 Conexões.** Acesso ininterrupto à orla a partir dos quarteirões interiorizados; calçadas conectadas, travessias apropriadas, guias e sarjetas coerentes. Sem beco/cinza sem significado; evitar sobreposições com árvores e o vidro das lojas.

## 4 — P2 Cidade urbana realista a nível do pedestre (prioridade visual ALTA)
**4.1 Edifícios:** preservar 1.468 contornos e estilo base, porém quebrar monotonia. Presets coerentes por família: residenciais antigos anos 60/70, modernos com varandas, fachada Art Déco, hotéis e edifícios icônicos inspirados genericamente na tipologia local, uso misto, escritórios/serviços, comércio térreo. Variar altura aparente **somente dentro da altura visual já adotada pela base** salvo correção justificada; material PBR de reboco, concreto pintado, pastilhas, pedra, vidro, metais, granito, venezianas; linhas de cornija, balanços, recessos e vãos realisticamente posicionados. Não criar mar de prédios identicamente quadrados.
**4.2 Fachadas:** melhorar molduras das 182.847 janelas R8 (conforme relatório R8) onde visível; janelas agrupadas por pavimento e estilo, vidros reflexivos plausíveis, diferentes acabamentos de caixilhos, janelas parcialmente abertas sem quebrar estabilidade; varandas R11 com guarda-corpos articulados, profundidade, suportes, pequenos objetos pontuais e acabamento, alinhadas ao grid R8. Corrigir texturas UV esticadas, cores uniformes e superfícies brancas.
**4.3 Coberturas:** substituir caixas de serviço exageradas por composição crível de platibanda, caixas d'água, lajes, terraços, ar-condicionado/condensadoras, antenas, tubulações, marquises, áreas técnicas e telhados; volumes contidos **dentro dos footprints** e com altura/escala realista. Introduzir alguns exemplares singulares visíveis da orla sem inventar marcos geográficos específicos.
**4.4 Térreo:** R12 hoje tem portas **decorativas opacas** e 320 lojas com letreiros **fictícios**. Melhorar recessos reais nos módulos novos quando tecnicamente seguro, sombreamento de vãos, soleiras, esquadrias, divisões de vidro, vitrines com interiores parallax/reflexo moderado, lojas e portarias distintas por família; se ainda não houver boolean/corte real da parede, documentar honestamente. **Não anunciar edifícios acessíveis** sem colisão/portas/ambiente interno testado. Adequar os 12 sinais fictícios e criar mais variedade moderada sem logotipos roubados. Evitar letreiro invertido de footprint horário.
**4.5 Replicação disciplinada:** não pintar cada prédio manualmente; usar ferramenta parametrizada `R13FacadeDetailGenerator` baseada em ID persistente, seed e estilo. Material atlas/instances, trims reutilizáveis, regras de alinhamento de janela/porta/varanda. Garantir que todos os blocos (frente mar e interior) tenham acabamento, ainda que LOD inferior à distância.

## 5 — P3 Solo, ruas, calçadas e urbanismo coerente
- Construir um material universal URP PBR para **asfalto real**, com normal leve, rugosidade, juntas/remendos sutis, guias, sarjetas, calçadas portuguesas/concreto, pavimento comercial, canteiros e gramados; substituir plano uniforme sob prédios. Largura/traçado de vias deve seguir dados cartográficos existentes; se largura for estimada, documentar.
- Revisar junções de **todas as ruas** e acessos pedonais; sem desconexão, pavimentação atravessando fachadas, via terminando no mar sem contexto ou zebra sem travessia. Aplicar faixas, linha central/lateral, lombadas/sinalização somente quando plausíveis; inserir pequenos detalhes: tampas de bueiro, grelhas, hidrantes, postes e lixeiras.
- Tratar esquinas, faixas de pedestre, rampas de guia, ciclovia onde cartografia/ambientação indicar, e limite quarteirão-calçada. Cortar/mascarar subsolo quando preciso para prevenir z-fighting e duplicação de planos.
- Material diferenciado por área: setor hoteleiro, quarteirão residencial, área comercial, orla/praia. A noção de escala deve aparecer a pé, não somente vista aérea.

## 6 — P4 Paisagismo tropical, vida visual e cidade habitável
- R9 contém apenas 48 árvores piloto em pontos OSM validados contra a malha viária. Expandir cobertura com **fontes georreferenciadas ou regras documentadas de plantio** sem deslocar os 48 nós verificados, e sem inventar árvore real no mapa sem marcar como ambientação. Usar árvore tropical naturalista com tronco/galhos e densidade interna; folhas finas, translucência/two-sided limitada, 2–4 espécies visuais plausíveis + palmeiras, arbustos baixos/canteiros/gramíneas/trepadeiras conforme região. **Não usar esferas low-poly** ou cardboards que dominam a câmera. Não sobrepor ruas, placas ou portas; checar altura de copa vs. fiação/postes.
- Preparar LOD0/1/2, billboards apenas longe e de alta qualidade, instancing quando possível, wind vertex animation sutil e desligável por tier. Testar densidade em toda a extensão; garantir vegetação no entorno onde verde aparece nos dados de parques e acesso à orla.
- Pessoas/ciclistas/carros/quiosques podem usar sistemas existentes do *jogo principal* depois da integração; não introduzir NPCs sem animação mínima, objetos pairando, carros em calçadas ou simuladores completos de tráfego nessa etapa. Se adicionar como ambientação, usar instâncias eficientes e persistentes coerentes com a via.

## 7 — P5 Luz, atmosfera, clima e composição cinematográfica
- Avaliar sistema de sol URP, céu, névoa atmosférica leve, exposição, color grading/tonemapping com teste **diurno, fim de tarde e noturno** sem saturação artificial. Praia ensolarada e sombra abaixo de marquise precisam ter contraste plausível, sem a cidade preta da R9.
- Preservar correção da R10: após abrir cena/câmera em batch mode, capturar pelo menos **cinco quadros GPU reais de aquecimento** antes de avaliar imagem; identificar separadamente sombra real de cold-start. Cascaded shadows com limites, contato leve e temporização equilibrados. Evitar desligar sombras globalmente para maquiar o defeito.
- Vidro translúcido/espelhado seletivo baseado em roughness, fresnel e ambiente urbano sem substituir tudo por azul uniforme; refletir o necessário sem SSR universal caro. Mar com brilho solar suave, sem ondas estroboscópicas.
- Materiais e cenas precisam funcionar em **Direct3D11 na Unity 6000.6.2f1**; não adicionar dependência HDRP ou soluções incompatíveis com o pipeline instalado. Ajustar resolução/FOV para experiência 1080p realista no PC.

## 8 — P6 Qualidade de produção e desempenho: obrigação, não opcional
- Estabelecer três tiers: Alto (RTX 4060 Ti 1080p, objetivo 60 FPS real), Médio e Baixo PC. Nunca mentir resultado sem profiler. Medir **Frame time CPU/GPU, FPS min/mediano/p95, draw calls/batches, triangles visíveis, VRAM, GC alloc por quadro e carregamento** em cenas equivalentes. Reportar dispositivo, resolução, qualidade, modo de tela e local. *Se não for possível medir, escrever explicitamente pendente*.
- Dividir 2 × 1 km em **células/setores espaciais**, ex.: tiles 100–200m, culling/occlusion espacial apropriado, LOD por distância, instanced repeated details, atlases texturizados por família, materiais compartilhados, meshes batch por tipo, compressão texture/mipmaps/anisotropy apenas quando útil. Evitar 1.400 GameObjects dinâmicos de fachada se já há malha agrupada; evitar 200 mil vidros com transparente real individual.
- Testar clipping, sombras à distância, tamanho de textura, UV0, normais outward, materiais cinzas default, sort transparency e hierarquia. Usar testes de referências quebradas e fontes inalteradas.
- Definir budgets progressivos e ajustar depois do profiling. Proposta inicial para investigação, **não aprovação automática**: drawcalls <2500 nas câmeras representativas, <=10 ms GPU em cenas comuns no preset alto 1080p e FPS alvo 60, sem exigir isso de cenas ainda não otimizadas. Não sacrificar realismo com low-poly na visão do jogador.

## 9 — Integração ao JOGO principal no PC (objetivo da tarefa, mas com gate)
O usuário espera a orla no **jogo jogável**, não apenas em um visualizador. O checkout de jogo está em `D:\sergi\Documents\Simulador-predial` (repositório `sergiomrge-tech/Simulador-predial`, projeto Unity `FacilityOps`); possui lógica de construção/gestão, quiosques, ciclo dia/noite, pessoas, materiais e mudanças locais **NÃO COMMITADAS**. NÃO usar git checkout/reset/clean sobre ele. Outro repositório `Resort-Simulator-` contém pipeline R7–R12 e cenas de QA visual. 

Fluxo obrigatório:
1. Fazer comparação dos dois projetos e mapear arquitetura de cenas, pipelines, materiais, input, render pipeline e IDs. Apresentar plano de integração sem duplicar oceanos, solos, ruas, câmeras, NPCs ou quiosques.
2. Implementar visual R13 e validar primeiro na branch isolada do repositório visual. Não substituir o protótipo jogável atual sem backup/PR/gates.
3. Criar integração em **clone limpo** do jogo ou branch separada do repositório gameplay quando possível; preferir carregar o visual geográfico como subcena, asset bundle, prefab gerado por Editor, Addressables ou loader organizado, nunca copiar `Library/`/cache nem atualizar a mão milhares de assets.
4. Manter menu, controles primeira/terceira pessoa, missões, construção, HUD, quiosques, saves, economia e interação existentes. Validar o fluxo abrir → iniciar/continuar → caminhar → interagir → salvar/carregar → sair. Evitar perda de progresso.
5. Só chamar **executável do jogo R13** após build Windows e smoke test que comprovem **o mapa novo efetivamente presente no gameplay**; diferenciar **prévia visual** de **jogo integrado** em documentação. Colocar no D: com versão única e criar atalho próprio depois da aprovação; nunca sobrescrever o último jogo funcional.
6. O fluxo de implementação preferencial é **GitHub-first**. PC é recurso pontual de build/QA, não requisito de presença constante nem servidor persistente.

## 10 — Plano de execução AUTÔNOMA em marcos verificáveis
**A tarefa é grande; não gastar a franquia inteira sem um resultado reproduzível.** Responder em checkpoints, não pedir ao usuário confirmação trivial. Em cada etapa: alterar código de verdade, adicionar testes nativos, gerar relatório e commit. Se não der para terminar R13 numa sessão, parar num checkpoint honesto e branch estável.

**Entrega A / Fundação + amostra premium:** auditar bugs das vistas R12 (P0); corrigir anti-repetição do piso, geometria costeira e materiais PBR no trecho representativo de **200 m** de orla; mostrar **captura Unity real antes/depois na mesma câmera**. Validar source geo, FBX no Blender, materiais URP e manter 2×1km.
**Entrega B / Continuidade 2 km:** parametrizar e aplicar o mesmo padrão ao longo dos 10 trechos de 200m sem lacunas; adicionar variações de letreiro/arquitetura/quiosque/mobiliário; ler da geometria OSM; gerar uma cobertura por setor e panorâmicas reais.
**Entrega C / Arquitetura premium:** passar detalhamento visual para todos os edifícios visíveis da frente mar e quarteirões adjacentes, sem prédios brancos e sem clones obviamente idênticos; vistas de pedestre e rua. Reutilizar R8/R11/R12 com substituição limitada e teste.
**Entrega D / Vegetação + iluminação:** integrar dossel tropical naturalista, calçadão completo, transições, luz e sombra, água animada; perfilagem real de 1080p e fallback quality tiers.
**Entrega E / Integração gameplay:** fazer comparação/branch do repositório principal, preservar funcionamento, entregar um Windows exe separado e testado depois dos gates anteriores. Não bloquear A–D aguardando PC.

## 11 — Gates objetivos de aceitação, devem passar para anunciar QUALQUER versão aprovada
- **GEO:** fonte OSM 1.468 prédios, 2 km × 1 km; 3.731 triângulos de ruas preservados ou alteração justificadamente auditada; não inventar água invadindo mapa; 48 árvores originais protegidas.
- **ARTE:** 0 edifícios brancos por material ausente; sem placeholders, low-poly aparente, materiais roxos, janelas espelhadas, letras invertidas; 100% dos 10 setores com transição mar/areia/calçadão/avenida contínua e detalhes visuais humanos; PBR correto ao nível da rua.
- **NATIVO:** Blender executa e reimporta FBX; testes Python versionados aprovados; Unity Editor compila em 6000.6.2f1 sem erros (warnings avaliados), valida UV0/material/shader, não quebra sistemas anteriores.
- **IMAGEM:** câmera por setor com **PNG real da Unity e hash**, 1600×900 ou 1920×1080; 3 pontos focais (cidade/lojas, calçadão/praia e mar), dois horários mínimo; 5-quadros aquecimento se captura batch, verificação de exposição. Nunca gerar render sintético rotulado Unity.
- **MÉTRICAS:** relatório de FPS e memória somente quando medidos; falha de FPS não é motivo para maquiar medição. Se 60 FPS não alcançado, fazer otimização/budgets por tier e declarar limite.
- **GAMEPLAY:** nenhum merge/build jogável R13 até que comportamento do player, saves, menus, quiosques e interação sejam testados em jogo principal realmente integrado.
- **GitHub:** commits limpos e pequenos, PR draft, workflow sem depender de computador ligado, artifact verificável e `docs/arte/R13_QA_REPORT.md` explícito: PASS/FAIL/PENDENTE por gate.

## 12 — Estrutura de entregáveis exigida do agente Sol
Em `codex/r13-sol61-orla-premium`:
- Novos scripts Blender/Python em `Tools/Blender` / `Tools/geo`, preservando geradores R7–R12; build determinístico, seeds/IDs e relatórios QA JSON.
- Unity `Assets/Editor` para montar a **cena R13 derivada** e scripts/shaders/materiais novos (sem gravar por cima das cenas R7–R12), guardas contra FBX/UV/shader errados.
- `docs/arte/R13_BASELINE_AUDIT.md`, `docs/arte/R13_ASSET_MANIFEST.md` (autoria/licenças), `docs/arte/R13_QA_REPORT.md`, `docs/arte/R13_GAMEPLAY_INTEGRATION_PLAN.md`, capturas reais e parâmetros de câmeras; se etapa de arte não passar, registrar blockers.
- Workflow `.github/workflows/r13-orla-premium.yml` com reconstrução Blender nativa + reimportação + contratos anteriores, scripts de QA sem segredos e artifacts; NÃO gerar PNG de Unity fictício em CI se não houver runner Unity.
- Preview técnico demonstrável dos 10 trechos e relatório de cobertura, sem alegar build Windows testado sem tê-lo feito.
- Abrir PR **draft** e finalizar com: commit(s), links GitHub, o que funciona, o que ainda falta, caminhos de execução/validação e próximo checkpoint.

## 13 — REGRAS PARA SOL (interação)
Trabalhar como artista técnico sênior, level/environment artist e programador Unity. **Não parar apenas para escrever recomendações**: primeiro audite e implemente a Entrega A até seu limite real de sessão, execute testes nativos, comite e reporte. Se tiver problemas de DNS/download, não fabricar resultado; priorizar assets locais e materiais autorais PBR. Nunca recriar o jogo em outro motor, e jamais mudar a orientação de 2 km / 1 km.

**Aprovação artística fica a cargo do usuário/diretor.** Não confundir verde em CI com aprovação estética. Durante o trabalho, verifique por captura Unity quando houver Editor. O projeto deve permanecer utilizável sem PC ligado, com fontes e pipeline no GitHub.

---
**Contrato da primeira chamada ao Sol:** ler tudo, auditar, implementar um **trecho premium de 200m da orla** com visual claramente melhorado, parametrizado para expansão aos 2km, executar testes que o ambiente permita, comitar no branch isolado e documentar limitações honestamente. O plano completo é obrigação futura em etapas, não promessa de uma única sessão.
