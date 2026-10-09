# R6 — inspeção visual real Unity (09/10/2026)

**Veredicto: execução nativa APROVADA; arte final REPROVADA.**
Capturas abaixo são **arquivos PNG genuínos de Unity Camera.Render / Direct3D11**
executados no computador autorizado, não renders Blender nem imagens sintéticas.
Não são screenshots da gameplay, Steam ou prova de FPS.

## Validação nativa executada no PC

- Editor Unity **6000.6.2f1**, GPU NVIDIA GeForce RTX 4060 Ti, API Direct3D11.
- Método `ResortR6FacadeFinish.Build`: **passou**, criando uma cena de teste
  R6 independente da R5, 160 materiais e 40 mapas de textura, 50 edifícios,
  50 estilos e 370 renderizadores.
- Nomes de malha truncados na exportação FBX: fallback controlado em 370
  renderizadores; a classificação exata das categorias perdidas requer correção
  no Blender/origem, não pode ser reconstituída pelo nome já truncado.
- Projeto de teste sem URP Pipeline Asset ativo: **shader Standard** usado
  como fallback técnico, NÃO foi validada a aparência dos materiais URP/Lit.
- Método `ResortR6VisualCapture.Run`: **passou**, produzindo 4 capturas
  genuínas 1600×900 e manifesto com SHA256.
- Diagnóstico decisivo: **370/370 renderizadores de arquitetura sem UV0**;
  mapas de albedo e normal não podem ser aplicados corretamente.
- **Nenhuma medição de FPS de gameplay**. Não anunciar otimização/aprovação.

## Evidências reais versionadas

- [Art Déco — oblíqua](../../ArtSource/Previews/R6_01_art_deco_carioca_RealUnity.png)
- [Residencial de orla — oblíqua](../../ArtSource/Previews/R6_02_residencial_orla_RealUnity.png)
- [Hotel contemporâneo — oblíqua](../../ArtSource/Previews/R6_03_hotel_contemporaneo_RealUnity.png)
- [Pedestre — câmera obstruída por massa antiga](../../ArtSource/Previews/R6_04_Pedestrian_RealUnity.png)
- [Manifesto nativo com hashes/estatísticas](../../ArtSource/Previews/R6_VisualNativeQA.json)
- [Relatório nativo de materiais e hashes de fontes](../../ArtSource/Previews/R6_Material_Pass_NativeQA.json)

## Avaliação visual crítica

As fachadas novas apresentam volumes, janelas e sacadas reais, mas materiais
sem textura UV exibem blocos brancos superexpostos e detalhes pouco legíveis.
Aproximadamente 1.418 volumetrias antigas ainda circundam o piloto e
bloqueiam vistas úteis. A captura pedestre ficou inteiramente obstruída.
Faltam calçadas, paisagismo, praia, superfícies urbanas, reflexos plausíveis
e acabamento condizente com Realismo Estilizado Premium. **Gate visual FALSE.**

## Próximo ciclo técnico obrigatório

1. Corrigir **UV0 e nomes semânticos persistentes** no gerador Blender,
   exportar FBX de 50 modelos novamente e validar preservação de geografia
   original/OSM/road meshes antes de substituir a cena derivada.
2. Configurar um Render Pipeline Asset **URP real na cópia de avaliação**;
   reproduzir materiais URP/Lit e confirmar mapas Albedo, Normal, Metallic
   e escala UV de mundo. Só então revisar cores/exposição e luzes.
3. Corrigir câmera pedestre para identificar obstruções/colisões, por
   exemplo por raycasts e acessos reais, nunca remover edifícios originais
   apenas para falsificar foto.
4. Validar 300 × 300 m de orla com ruas, calçadas, praia e vegetação coerentes,
   com capturas de nível de rua e medições reais de memória e FPS.
5. Só promover arte após inspeção e aprovação visual expressa.

**Originals preservados**: BlenderGIS, FBX original, malha geográfica/OSM,
cena técnica R5 e build R5. Os assets Standard da inspeção R6 permanecem na
cópia local do PC, pois não devem ser confundidos com materiais URP finais.

© OpenStreetMap contributors — ODbL 1.0.
