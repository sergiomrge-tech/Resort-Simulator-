---
name: blender-sem-pc
description: Build and render Blender scenes in headless GitHub Actions, use source .blend unchanged, verify geometry and screenshot clarity.
---

# Blender automatizado, sem PC

**Quando usar:** modelagem procedural, FBX export, renders reais e revisão visual de geometria.

## Ferramentas existentes
- `Tools/Blender/export_copacabana_fbx.py` exporta o BlenderGIS original para FBX.
- `Tools/Blender/render_copacabana_qa.py` renderiza a geografia real enquadrando pelo bounding box.
- `.github/workflows/mapa_blender_para_unity.yml` e `copacabana_qa_render.yml` já tiveram execuções bem-sucedidas.
- Exemplo de comando em runner: `blender --background --factory-startup -b <arquivo.blend> --python Tools/Blender/render_copacabana_qa.py`.

## Procedimento
1. Executar Blender headless somente em runner com dependências instaladas de modo explícito; exportação FBX requer `numpy` no Python do Blender.
2. Ler o .blend real e testar existência de vértices, faces, materiais, dimensões e câmera. Se faltar objeto, **falhar**, não renderizar vazio.
3. Usar limites reais do modelo para posição da câmera. Aplicar iluminação suficiente e materiais temporários diferenciados, sem modificar a malha original.
4. Salvar PNG, JPEG e relatório JSON (dimensões da imagem, geometria, câmera, status).
5. Validar a diversidade de pixels e a existência de silhuetas reais. Rejeitar imagens cinza, brancas, vazias ou fotomontagens.
6. Registrar número da execução Actions, hashes e caminho da imagem. Dizer sempre «render real do Blender», nunca «print da Unity».
7. Não importar addons desconhecidos com `curl|sh` nem executar Python remoto sem revisão. O Blender MCP comunitário é opcional e depende de Blender Editor rodando; **não é requisito do fluxo cloud**.

## Critério de saída
- Arquivo renderizado realmente visualizável e conferível.
- Imagem construída a partir de geometria real; relatório de QA; source intacta.
- Não chamar foto/render de jogo jogável.

## Referências
- https://docs.blender.org/manual/en/4.5/advanced/command_line/arguments.html
- https://github.com/domlysz/BlenderGIS
- https://github.com/ahujasid/blender-mcp (opcional, requer Editor; terceiro)
