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
- Unity: **PASS nativo**, cópia isolada `build/R14_NativeWorkspace`, Editor
  6000.6.2f1 / URP17.6 / D3D11 / RTX4060Ti. 31+105 meshes, 24 Texture2D,
  zero UV0/material slots/default material/shader ausentes; sem escala 100×.
  48 árvores e 3.731 triângulos viários preservados. As primeiras tentativas
  falharam no IPC UPM; servidor exclusivo e ProgramData nativo resolveram.
- Capturas: **72 PNGs Unity reais**, 36 antes + 36 depois, S01/S05/S08 ×
  seis vistas × dia/tarde. Mesmo dispositivo/câmera/luz/FOV53/1600×900,
  cinco warmup frames, processos Editor separados e SHA-256 checados.
  A câmera próxima da guia foi revisada para apontar ao detalhe real.
  Relatórios técnico/pareamento/execução sanitizados em ArtSource/Previews.
- Testes locais: **46/46**, regressões R7–R13 e nove contratos R14; sem skips
  depois de obter Unity real. Testes não equivalem a aprovação premium.
- CI R7–R14: **PASS** no checkpoint `ad162e8`, execução
  [37959339234](https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37959339234).
  Cadeia completa, reimportação de conectores e kit costeiro, renders/contratos
  e upload aprovados. CI Linux Blender não fabrica novas capturas Unity.
  O checkpoint com os PNGs/cena Unity finais será validado em outra execução.
- FPS/CPU/GPU/drawcalls/VRAM 1080p, gameplay e animação de água: **PENDENTE**.

## Limitações materiais

A costa R13 curva passa fora de y=-500 nos extremos; a via GIS original é
recortada em y=-500. Conectores ficam dentro do frame 2.000×1.000 m e não criam
avenida no trecho sem substrato GIS. Entre passeio e rua, o preenchimento busca
apenas gaps até 8 m; gaps maiores continuam abertos. Não afirmar conexão
pedonal completa, ausência de colisões de gameplay ou cidade tropical final.
Em S05 o bordo do mosaico R13 está a 85–94 m da via GIS, medido a cada 10 m;
o gate de conexão total **não passou**. S01 recebe 78,38 m² de transição StoneTile.
O kit costeiro acompanha a faixa R13, inclusive os extremos fora de y=-500.
Isso é registrado por mesh na cobertura; o gate desses assets contra o limite
terrestre está **PENDENTE**, não constitui expansão de gameplay aprovada.
Reconciliar faixa artística/costa/frame antes de tratá-la como mundo jogável.

O solo interior, diversidade de fachadas completas, mar/areia finais, grelhas,
bueiros e sinalização ainda precisam de trabalho. Colisores de calçadas/guias
no builder são preparação, não prova de percurso em Play Mode. LOD de sólidos
urbanos e desempenho precisam de profiler. Renders de assets não substituem
inspeção da cidade nativa e aprovação do diretor.

Inspeção real: S01 pedestre mostra banco/mosaico PBR; S08 costa mostra quiosque
e plantio novo. O fallback branco de mosaico nos sete setores foi substituído
somente na cena R14 pelo PBR R13 já testado. S05 cidade ainda revela piso grande
e repetição arquitetônica; a vista de guia expõe a separação entre calçada
aditiva e underlay. Nenhuma dessas imagens recebe aprovação artística.

Fotos: [S01 pedestre](../../ArtSource/Previews/R14_S01_after_day_pedestrian_RealUnity.png),
[S08 costa](../../ArtSource/Previews/R14_S08_after_day_coast_RealUnity.png),
[S05 guia](../../ArtSource/Previews/R14_S05_after_day_curb_RealUnity.png).
Cena nativa R14 foi produzida e copiada para Assets/Scenes, com oito materiais.
Um checkout limpo precisa reconstruir os assets R7–R13 antes de abrir a cena;
builder/CI e cópia isolada garantem reprodução sem mexer nas cenas fontes.
