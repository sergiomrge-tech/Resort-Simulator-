# Resort R6 — Primeiro acabamento material autoral para os 50 edifícios OSM

**Status em 09/10/2026: fonte Unity preparada em branch; SEM validação nativa ou captura R6 ainda.**
O gate artístico do usuário continua pendente. Esta etapa não afirma fotorrealismo, jogo final
ou substituição dos outros 1.418 edifícios do mapa.

## O que foi implementado em código

- `UnityProject/Assets/Editor/ResortR6FacadeFinish.cs`: método de Editor
  `ResortR6FacadeFinish.Build` e menu **Resort → R6 → Gerar fachadas PBR dos 50 prédios**.
- Lê a cena existente `R5_Copacabana_50_Predios_EditorQA.unity` e gera
  **uma cena independente** `R6_Copacabana_50_Fachadas_PBR_VisualQA.unity`.
  A fonte geográfica BlenderGIS, seu FBX, a cena e a build R5 existentes
  não são sobrescritas.
- Identifica cada `way/...` e `cop_<familia>_<01..05>` no nome real do
  objeto derivado. Reprova a geração se não houver **50 OSM ways distintos,
  50 estilos distintos e pelo menos 300 renderizadores**.
- Paleta coerente e reproduzível de **10 famílias x 5 variantes**, sem
  cores aleatórias a cada execução. Cada parte recebe acabamento semântico:
  paredes, pedras, ornamentos, vidro, metal, madeira, telhado,
  vegetação em jardineiras e recessos sombreados.
- Gera no Unity texturas **256×256 tileáveis** com microgrão procedural
  e normal maps correspondentes, por família e revestimento (estuque/pedra).
  Serão 40 PNGs autorais persistentes no projeto quando o Editor executar;
  mipmaps, repeat, anisotropia e instancing ficam configurados.
- Cria materiais `URP/Lit` editáveis em `Assets/Materials/R6_Facades/`,
  associados apenas às malhas dos 50 edifícios. **Vidro nesta etapa usa
  aparência opaca e lustrosa; transparência e reflexos físicos exigem QA
  posterior.** Outros 1.418 blocos e geometria de ruas permanecem como antes.
- Grava um `build/R6_PBR_FacadeQA/material_pass.json` com contagens,
  caminhos, IDs, hashes da fonte e limitações.

O gerador **não executa automaticamente no GitHub Actions sem Editor Unity
licenciado**. O workflow R6 verifica a fonte e os vínculos reais com os
50 edifícios; isso não é compilação, captura Unity, validação PBR visual
nem medição de FPS.

## Execução posterior em ambiente Unity válido

Com o projeto do GitHub aberto em um Unity Editor 6.x com URP disponível:

```text
Unity.exe -batchmode -quit -projectPath <pasta-repositorio>/UnityProject -executeMethod ResortR6FacadeFinish.Build -logFile <log>
```

A versão declarada no repositório é **6000.3.9f1**, enquanto o teste
R5 foi executado com **6000.6.2f1** em uma cópia separada. Não migrar
as configurações do projeto na branch sem gate real.

A cena R6 exportada deve ser inspecionada com câmera real na altura do
pedestre e foco em pelo menos três prédios diferentes; registrar prints
genuínos da Unity, avaliar texturas e junções, perfis de memória e FPS.
Somente após aprovação avançar com calçadas, praia, quiosques,
LOD/streaming e expansão dos demais quarteirões.

**Restrições inalteradas:** Copacabana original de 2.000 x 1.000 metros,
sem low-poly como acabamento final; preservar todos os lotes OSM,
ruas e suas coordenadas, sem gerar cidade artificial por cima.

© OpenStreetMap contributors, ODbL 1.0. Materiais procedurais próprios Project Resort.
