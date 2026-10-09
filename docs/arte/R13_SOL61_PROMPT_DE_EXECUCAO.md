# PROMPT OPERACIONAL — CODEX SOL 6.1 (ESFORÇO MÉDIO) — PROJECT RESORT R13

Você é **Sol 6.1 via OpenAI Codex**, configurado em **model_reasoning_effort=medium**, responsável por implementar aprimoramento visual real em toda a orla do jogo Project Resort. O dono do projeto não quer conceitos, mockups, imagens geradas artificialmente ou baixa complexidade low-poly. Ele exige código/arte integrada na Unity, e o mapa está restrito a **2 km paralelos à praia de Copacabana x 1 km de profundidade**, preservando os OSM 1.468 prédios e as ruas reais.

## PRIMEIRA AÇÃO OBRIGATÓRIA
Abra e LEIA INTEGRALMENTE `docs/arte/R13_PLANO_COMPLETO_ORLA_PREMIUM_SOL61.md`. Este arquivo é o contrato de produto e técnico; **TODOS** os capítulos 0 a 13 são parte do seu prompt. Depois leia `AGENTS.md`, `README.md`, relatórios R8–R12, os scripts Blender/Unity e os testes. Não invoque outros agentes nem altere nome de modelo.

**Branch de trabalho:** `codex/r13-sol61-orla-premium`, derivada da `codex/r12-urban-storefronts` commit `afa4dfaf9d0bca735c574b0f72c10411d7968ad0`. **Não alterar branch/main nem mexer na pasta suja `D:\sergi\Documents\Simulador-predial`.** Trabalhe neste worktree e faça os commits aqui. Cópia PC atualizada do jogo e visualizador R12 já existem, não os substitua.

## FAÇA NESTA PRIMEIRA EXECUÇÃO (trabalho concreto até o limite da sessão)
1. Audite as lacunas reais dos geradores e capturas R12, com ênfase em repetição de fachadas, praia chapada, mar artificial, calçadão fino, praça/passeio vazio, vegetação pobre, imóveis sem acabamento PBR e riscos de artefatos. Faça `docs/arte/R13_BASELINE_AUDIT.md` com severidades, referências geográficas e lista de geradores que serão estendidos, sem inventar medições.
2. Selecione **um segmento representativo de 200 metros junto à orla** baseado nas coordenadas da moldura geográfica. Gere efetivamente o primeiro pacote R13 de acabamento premium por código: não é para apenas escrever uma proposta. O segmento deve conter **soluções paramétricas escaláveis aos dez segmentos**, priorizando (i) calçadão e transições pavimento/areia/mar, (ii) superfície PBR plausível no nível do pedestre, (iii) mobiliário e paisagismo costeiro com variações, (iv) fachada próxima sem branca/placeholder e (v) sombra/luz controladas. Se tiver de escolher por tempo, faça menos áreas com acabamento melhor em vez de vinte placeholders.
3. Não crie um mapa concorrente: DERIVE as geometrias da costa real OSM e dos presets R7–R12; preserve eixo de 2km no litoral, 1km interior, todos os 1.468 footprints, 3.731 triângulos de via e 48 árvores piloto. Guarde um JSON de cobertura por setor com georreferenciamento, fontes e hash dos FBX.
4. Usar Blender verdadeiro via Python para gerar modelos; reimportar o FBX para validar UV0 e materiais; integrar de maneira modular à Unity URP 6000.6.2f1 em **cena R13 derivada**, sem sobrescrever R12. Usar texturas realistas, PBR e LOD adequado; evitar milhares de renderers novos. Adicionar validações reais de dados e referências. Se a Unity não estiver disponível nesse contexto, informar ausência e NÃO produzir screenshot falso; mas continue Blender/CI.
5. Faça teste de cobertura geométrica e visual de continuidade longitudinal. Crie scripts para gerar todos os 10 trechos de 200m automaticamente mais tarde, mas só marque os segmentos efetivamente terminados como PASS. Sem afirmação de '2km completos' se apenas os primeiros 200m foram refinados.
6. Documente em `docs/arte/R13_QA_REPORT.md` evidência materializada, check PASS/PENDENTE, contagem de malhas/UV, segmentação e gargalos. Crie `docs/arte/R13_ASSET_MANIFEST.md` com licença/autor/link de qualquer asset externo. Se puder capturar Unity real via Editor, salve PNG e hash em `ArtSource/Previews`.
7. Deixe um workflow `.github/workflows/r13-orla-premium.yml` reprodutível via GitHub Actions para export/reimport Blender, regressões R7–R12, relatório de cobertura e upload de artifacts de fonte/FBX. NÃO depender de PC sempre ligado. Antes de fechar, comite suas mudanças em R13 e tente enviar branch ao GitHub (não forçar push e não fazer merge). Pode abrir PR draft, sem aprovar arte.
8. Prepare `docs/arte/R13_GAMEPLAY_INTEGRATION_PLAN.md`: plano concreto de como levar a orla R13 do repo visual ao game `sergiomrge-tech/Simulador-predial` sem sobrescrever checkout principal sujo; preservar missões, NPCs, HUD, quiosques, construção e saves. NÃO executar uma integração destrutiva.

## PADRÃO DE ACEITAÇÃO
- **Nunca entregar mapa branco, sem texturas ou low-poly como acabamento comercial.**
- Não comprar nem baixar assets sem licença verificável; preferir os originais locais, PBR próprio e packs CC0.
- Não modificar renderização além daquilo que for reproduzível com Unity/URP; mesmo zoom/câmera antes/depois; não maquiar imagem.
- Não reportar 60 FPS sem profiling real; não fazer screenshot sintética.
- Gate visual continua **PENDENTE** até eu aprovar imagens reais.
- Terminar primeira iteração em estado reproduzível, com hash de arquivos e commit; não interromper para perguntas de baixo impacto.

## RELATÓRIO FINAL OBRIGATÓRIO DESTA CHAMADA
Produza texto conciso em português com:
(a) commits/branch/PR; (b) arte realmente adicionada; (c) mapas/setores cobertos e contagens verificadas; (d) testes que rodaram e erros/bloqueios; (e) caminhos das capturas **reais**; (f) por que ainda falta acabamento em toda a orla e qual o checkpoint seguinte.

**Prioridade absoluta: trabalho artístico no código de fato, começando por 200 m replicáveis e depois expandindo com padrão premium. Não só plano.**
