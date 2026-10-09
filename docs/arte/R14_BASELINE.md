# R14 — baseline e riscos, 09/10/2026

Base: R13 Pass2 `5217a65`; branch exclusiva `codex/r14-sol61-orla-fullfinish`.
Contrato R13, geradores, importadores, testes e PNGs reais S04/S05/S06 lidos.
Leitura visual: S05 pedestre, S04 cidade e S06 costa revelam piso urbano extenso,
sem ressalto de guia ou sarjeta distinguindo avenida/passeio. Mobiliário se repete
em cadência regular, fachadas ainda repetem vidros azuis e a praia é simplificada.

| Trechos | Estado anterior | Risco a resolver |
|---|---|---|
| S00–S03 / S07–S09 | BASE, sem novos grupos/fachadas | Prioridade de expansão; não herdar aprovação dos três setores capturados |
| S04–S06 | INTERMEDIARIO; oito grupos por setor | Evitar duplicar mobiliário e overlays anteriores |
| Dez fronteiras | Superfícies costeiras contínuas | Recortar uma geometria global em setores, sem offsets por setor |
| Avenida / ruas transversais | 3.731 triângulos GIS | Derivar bordas da união dos triângulos; não bloquear cruzamentos com guias inventadas |
| Footprints e acessos | 1.468 footprints; alturas estimadas | Recortar calçadas contra lotes com margem; portas continuam decorativas, não levantamento |
| Solo / R9 / R13 | planos em -0,17; -0,078; -0,032 m | Novas superfícies devem ter separação vertical explícita; nunca deslocar triângulos originais |

`R14_SourceAudit.json` extrai triângulos e cotas diretamente do Blender original,
sem salvar a fonte. Hashes incluem frame, OSM, 48 árvores, footprints e R13.
O recorte costeiro e larguras de passeio permanecem artísticos; não há levantamento
de guias, sarjetas, portas, rampas, redes subterrâneas ou relevo. Os conectores
aditivos usam a borda real da malha viária como referência horizontal.
Colisões de gameplay, acessibilidade regulamentar e desempenho dependem de
validação runtime. União/recorte geométrico é evidência técnica, não aprovação visual.

Medição adicional: samples a cada 10 m do bordo terrestre do mosaico R13 à
malha viária original mostram gaps de **85–94 m em S05**, 83–94 m em S04,
84–87 m em S06; S00 chega a 165 m porque parte da costa está fora do recorte.
Somente S01 possui samples a menos de 8 m (mínimo 1,77 m). Portanto a faixa
costeira artística de 42 m da R13 não coincide com a borda real da avenida.
R14 não pode certificar conexão mosaico–avenida completa. O fechamento correto
exige uma nova composição costeira derivada das duas bordas GIS, mantendo
fontes e coordenadas intactas, e revisão visual; não estender asfalto para
encobrir o vazio. Medições por setor no JSON nativo e na cobertura R14.
