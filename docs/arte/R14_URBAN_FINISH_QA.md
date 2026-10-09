# R14 — acabamento urbano efetivamente criado, arte pendente

Branch exclusiva: `codex/r14-sol61-orla-fullfinish`, base R13 Pass2 `5217a65`.
PR draft existente #36, base `codex/r13-sol61-orla-premium`. Nunca fazer merge.
Nenhum acesso ao jogo Simulador-predial, executável ou arquivos do outro agente.

## Geometria nativa

O gerador extrai os 3.731 triângulos de rua do `.blend` original em modo somente
leitura, une seus polígonos e produz sólidos aditivos recortados por setor e
contra os 1.468 footprints, margem de 25 cm. Guia 18 cm de largura / 14 cm de
ressalto sobre a rua em z=0,06 m; sarjeta 28 cm; calçada até 2,32 m útil.
Rebaixos são inferidos em nós OSM highway=crossing, sem afirmar levantamento
ou conformidade regulamentar. Portas anteriores permanecem decorativas.

Blender 5.2.1: 31 malhas de conectores, **381.594 triângulos**, 95.291 triângulos
superiores testados depois de reimportar o FBX. Normais superiores corretas,
UV0 finita/métrica, zero projeção 100×, exclusão de lotes/vias checada sobre
centroides reimportados e domínios integrais. **27 interfaces** com geometria
presente comparadas nos nove limites internos, tolerância 2 mm. Onde não há
domínio da fonte em um limite não é inventada uma continuidade.

Removidos 86 slivers numéricos, área total 0,009486 m² (inclui lados e base),
que poderiam inverter no float32 do FBX. Nenhuma coordenada original movida.
Faces duplicadas de coberturas corrigidas antes do gate; LODs realmente
reexportados e reimportados. R14 não altera fontes/cenas anteriores.

## Cobertura real

Os sete setores BASE recebem 49 novos conjuntos (sete por setor) com banco,
jardineira/folhas curvas, lixeira, paraciclos e poste; 12 palmeiras com tronco
segmentado/frondes pinadas; sete quiosques (pergolado, duas águas, radial).
S00 não recebe palmeiras porque o envelope foi rejeitado pela curva do passeio.
37 fachadas recebem rodapé e molduras rasas com lattice R8; o prédio-piloto R7
encontrado na seleção foi excluído para preservar seu grid diferente.
105 malhas agrupadas de arte incluem LOD0/1/2; contagens finais no JSON nativo.
Distribuição varia por seed e respeita envelopes completos contra vias/lotes.

S04/S05/S06 recebem os conectores R14; os 24 grupos e detalhes R13 anteriores
continuam preservados. Não foi implementado novo refinamento de areia/mar nesses
três setores. Cobertura e bounds completos: `ArtSource/Previews/R14_SectorCoverage.json`.
Nenhum setor é PREMIUM_APROVADO. INTERMEDIARIO indica geometria real produzida,
com limitações; não certifica acabamento completo dos 2 km.

## Gates e evidências

- Blender export/reimport: PASS, UV0/materials/LOD/source hashes.
- Três renders reais Blender de assets S01/S05/S08 com câmera/hash: produzidos;
  mostram conectores contra via GIS, sem edifícios/cidade completa, não Unity.
- Unity: execução em cópia isolada `build/R14_NativeWorkspace`, com Editor
  6000.6.2f1 e URP17.6; resultado nativo/capturas será registrado no checkpoint.
  As primeiras tentativas falharam no IPC UPM; não confundidas com compilação.
- CI R7–R14: workflow implementado para regenerar toda cadeia, reimportar e
  enviar assets/logs; execução GitHub precisa de resultado real antes de PASS.
- FPS/CPU/GPU/drawcalls/VRAM 1080p, gameplay e animação de água: **PENDENTE**.

## Limitações materiais

A costa R13 curva passa fora de y=-500 nos extremos; a via GIS original é
recortada em y=-500. Conectores ficam dentro do frame 2.000×1.000 m e não criam
avenida no trecho sem substrato GIS. Entre passeio e rua, o preenchimento busca
apenas gaps até 8 m; gaps maiores continuam abertos. Não afirmar conexão
pedonal completa, ausência de colisões de gameplay ou cidade tropical final.
Em S05 o bordo do mosaico R13 está a 85–94 m da via GIS, medido a cada 10 m;
o gate de conexão total **não passou**. S01 recebe 78,38 m² de transição StoneTile.

O solo interior, diversidade de fachadas completas, mar/areia finais, grelhas,
bueiros e sinalização ainda precisam de trabalho. Colisores de calçadas/guias
no builder são preparação, não prova de percurso em Play Mode. LOD de sólidos
urbanos e desempenho precisam de profiler. Renders de assets não substituem
inspeção da cidade nativa e aprovação do diretor.
