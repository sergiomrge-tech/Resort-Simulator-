# Project Resort R12 — comércio de rua e entradas arquitetônicas (09/10/2026)

## Progresso realizado, não imagens-conceito
**R12 é uma cena técnica derivada da R11, não modifica arquivos geográficos nem as cenas R7–R11.** Preserva Copacabana com 2 km paralelos à orla e 1 km de profundidade, os 1.468 lotes/edifícios fonte, 3.731 triângulos GIS de ruas, 48 árvores e os complementos de volumetria da R11. Os edifícios continuam nas posições OSM originais.

### Componente 3D procedural de rua
Gerador `Tools/Blender/generate_r12_storefronts.py`, feito para Blender 5.2 e pipeline CI GitHub. Lê os 1.418 footprints R8 não-piloto; a R7 mantém os 50 edifícios de origem. Calcula a aresta de fachada mais longa e usa **a mesma grade de janelas e a mesma baia central de porta que R8** para impedir entradas flutuantes ou fora de alinhamento.

Blender gerou:
- **1.411 entradas arquitetônicas** com portas duplas de vidro escuro, ombreiras de pedra, molduras de alumínio, puxadores metálicos e soleira visual.
- **320 lojas/frentes comerciais** com **1.627 vitrines**, marquises de alumínio e faixas decorativas.
- **320 painéis de letreiro** distribuídos entre 12 artes gráficas independentes feitas para o projeto e exportadas como PNGs comerciais 1024×256, com tipografia em português: Café, Boutique, Mercado, Padaria, Galeria, Farmácia, Hotel, Restaurante, Serviços, Clínica, Floricultura e Ateliê.
- Tratamento de vidraçaria revisado depois das primeiras capturas: **dois mapas raster autorais de 512×1024** para vidro de vitrine e entrada, com reflexos difusos de céu/edificações e indícios visuais de mobiliário interno. São superfícies emissivas/refletivas simuladas, **não espelhamento físico ou interiores transitáveis**.
- **19 malhas semânticas**, agrupadas por acabamento/letreiro (sem renderizador para cada uma das 1.411 entradas); FBX independente de ~7,45 MB, 153.680 faces.

### Integridade e não indução a erro
Os letreiros são **fictícios e genéricos**, não identificam estabelecimentos reais dos dados do OpenStreetMap. Aparência comercial é apenas ilustração. Os fundos das portas R8 permanecem fechados — a R12 **não recortou portas na malha principal** e não implementou interiores jogáveis; sua porta 3D é revestimento de fachada, não passível de atravessamento. Não prometer portas funcionais nem navegação.

Marquises são colocadas somente acima da linha das portas, sem deslocamento horizontal dos polígonos OSM no chão. Não foi feito survey detalhado de calçadas, tráfego, acessibilidade ou lotação real.

### Testes realmente executados
- Blender 5.2.1: geração FBX nativo com geometria real, seguido de importação independente e validação de UV0, materiais, SHA-256 das fontes e todas as 12 texturas de letreiro em `Tools/tests/test_r12_storefront_native.py`.
- Unity 6000.6.2f1, RTX 4060 Ti, Direct3D11/URP: `ResortR12StreetFinish.Build` importou 19 malhas, 12 artefatos gráficos de letreiro e dois mapas de vidro; 0 erros de shader e 0 malhas sem UV0, preservando R11+árvores/ruas. Cena técnica `Assets/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity` criada na máquina de QA, sem sobrescrever cenas anteriores.
- **9 capturas reais 1600×900 da Unity** gravadas em `ArtSource/Previews/R12_*_RealUnity.png`. Inspecionadas duas vistas comerciais: imagens 08 (fachada) e 09 (detalhe); a segunda rodada confirmou que vitrines deixaram de ser superfícies azuladas vazias. O registro `R12_VisualNativeQA.json` contém hash do PNG e metadados da GPU; `test_r12_capture_integrity.py` valida a integridade.
- O enquadramento aéreo R12 mantém o gate anti-cidade-preta: 5 quadros reais de aquecimento GPU e teste de luminosidade contra regressões.
- `.github/workflows/r12-streetlevel-storefronts.yml` deve reconstruir a cadeia R7→R12 diretamente no GitHub com Blender nativo e reimportação de FBX R12. O Editor Unity Windows foi usado somente para auditoria visual local; **não afirmar que o GitHub gera automaticamente EXE/Steam**.

### Pendências de arte e desempenho
**ART GATE AINDA NÃO APROVADO.** Ainda são necessárias vitrines com transparência/reflexos verdadeiros, variação por lote, interiores comerciais que permitam interação, entradas com colisão/corte de malha, soleiras e rampas apropriadas, fachadas singulares, asfalto/calçadas realistas e iluminação física. O mar R10 permanece aproximado, vegetação R9 é piloto. Antes de liberar versão jogável: perfilagem de FPS, LOD, draw calls, streaming urbano, efeitos de reflexo, circulação e testes de jogo.

**Licenciamento**: dados espaciais © OpenStreetMap contributors sob ODbL 1.0. Arte de letreiros, filtros de vidro e geometria R12 criados proceduralmente para este jogo. Fontes do sistema são utilizadas somente para rasterizar textos; arquivos .ttf não são distribuídos.
