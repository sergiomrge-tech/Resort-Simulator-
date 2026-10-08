---
name: qa-capturas-sem-fraude
description: Validate 3D game deliverables with genuine Blender/Unity screenshots, explicit pipeline status and traceable CI evidence.
---

# QA de imagens e artefatos verificáveis

**Quando usar:** aprovação de qualquer nova cena, material, transformação geográfica, build, vídeo ou screenshot.

## Classificação obrigatória
- **Blender REAL render:** output de `bpy.ops.render.render` com geometria carregada, provenance no JSON e GitHub Actions run ID.
- **Unity REAL screenshot:** somente quando processou um frame no Unity Editor ou player real e há log ou processo que comprova; nunca render Blender, imagem gerada ou mockup.
- **Mapa cartográfico:** SVG/GeoJSON e não render Unity.
- **Conceito:** pode ser ilustração, com aviso claro de que NÃO é screenshot do jogo.

## Pipeline de qualidade
1. Testar existência de geometria, bounds, materiais e objetos visíveis.
2. Calcular enquadramento pelo bounds, fundo contrastante e iluminação; não aceitar imagem toda cinza, branca, preta ou saturada.
3. Salvar PNG mestre, JPEG prévia e `*_report.json` com contagem de malhas, faces, origem, renderer, hora e CI run.
4. Examinar imagem visualmente: densidade, fachadas diferentes, rua conectada, texturas, praia, iluminação, cortes/corpos invisíveis.
5. Reportar incertezas: Unity parser, FBX import, licenciamento, performance e FPS, se não houver execução real.
6. Somente após revisão/aprovação visual marcar etapa como aceita e abrir próxima fase.

## Critério de saída
- Identificação explícita do renderizador e proveniência.
- Evidência observável e link/artefato GitHub; nenhuma afirmação de execução sem log.
- Imagem repetível a partir do commit.

## Referências
- `Tools/Blender/render_copacabana_qa.py`
- `ArtSource/Previews/Copacabana_QA_report.json`
- `docs/qa/R1_MAPA_UNITY.md` (branch R1)
