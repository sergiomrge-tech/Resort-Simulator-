---
name: agua-praia-piscinas-iluminacao
description: Develop realistic but optimized ocean, Copacabana beach, hotel pools, lazy river and daylight with URP compatibility.
---

# Água, praia, paisagismo e luz costeira

**Quando usar:** oceano, faixa de areia, piscinas, espuma/ondas, céu, tempo, HDRI e paisagismo.

## Processo
1. Partir de dados geográficos confiáveis e do modelo real; verificar posição costa/mar. Praia e relevo ainda não são DEM fiel e não podem ser rotulados como tais.
2. Manter URP até teste e decisão formal do pipeline. Não depender de shaders HDRP sem migração aprovada.
3. Para oceano no URP, especificar materiais Shader Graph/URP Lit adequados e comprovar suporte: normal waves, Fresnel, gradiente de profundidade aproximado, espuma de costa e reflexo possível no hardware; **não afirmar ocean shader final antes da validação**.
4. Água da piscina e rio lento é outro sistema (volumetria rasa, bordas, ladrilhos, iluminação noturna) separado do oceano.
5. Criar praia realista: areia PBR CC0, variação úmida/seca, desgaste, vegetação costeira adequada, quiosques com cores variadas.
6. Luz do sol de acordo com o relógio, sombras e tonemapping consistentes. Otimizar superfícies transparentes e efeitos reflexivos antes de espalhar por 2 km².
7. Visuais para aprovação: close da água/areia, calçadão, piscina, vista do mar e imagem noturna, sempre **render verdadeiro da ferramenta declarada**.

## Critério de saída
- Uma área de teste visualmente convincente, sem água violeta/rosa, textura repetida óbvia ou praia de geometria inventada.
- FPS e consumo medidos quando houver Unity; caso contrário registrar hipótese e pendência.

## Referências
- https://docs.unity3d.com/Manual/urp/prebuilt-shader-graphs-urp.html
- https://polyhaven.com/license
- https://ambientcg.com/
