---
name: catalogar-assets-licenca
description: Track commercial rights for every third-party 3D model, texture, HDRI, sound and animation before importing into GitHub.
---

# Cadastro de assets e licença comercial

**Quando usar:** download ou reaproveitamento de qualquer asset externo para o jogo Steam.

## Fontes recomendadas
- Poly Haven: HDRI, materiais PBR e objetos, CC0.
- ambientCG: materiais PBR com indicação CC0.
- Unity Asset Store: somente depois de verificar EULA, Standard/Non-standard, Restricted e regras por seat; não subir pacote comprado para Git público indiscriminadamente.
- Dados OSM: © OpenStreetMap contributors, ODbL; manter relatório e atribuição.

## Procedimento obrigatório
1. Antes de baixar: URL do item, autor, versão/data, licença explícita e prova de autorização comercial; sem fontes obscuras.
2. Escolher versão/LOD/resolução por uso: 2–4K para fachada perto apenas onde justificável, 1K para detalhes médios, texturas pequenas para distantes.
3. Identificar textura baseColor, normal e convenção OpenGL/DirectX, roughness e metallic; converter para Unity pipeline escolhido.
4. Evitar download de dezenas de gigabytes sem auditoria. Pré-selecionar, validar um exemplar e medir qualidade/importação.
5. Manter `docs/assets/REGISTRO_ASSETS.csv` com ID, caminho, URL, licença, autor, objetivo, estágio QA e hash quando importado.
6. Preferir materiais com redistribuição permitida no repositório público; se licença restringir redistribuição de arquivos-fonte, manter fora do Git público e descrever processo legal de importação.
7. Nunca assumir que «gratuito» significa CC0 nem que uma imagem de busca pode virar textura do jogo.

## Critério de saída
- Origem documentada para cada asset; direitos comerciais verificáveis; consistência visual; sem dependências injustificadas.

## Referências
- https://polyhaven.com/license
- https://ambientcg.com/
- https://assetstore.unity.com/browse/eula-faq
- https://www.openstreetmap.org/copyright
