---
name: otimizar-cidade-unity
description: Keep detailed 2 km2 Unity coastal city performant with streaming, occlusion, LOD and actual profiler evidence.
---

# Performance de cidade e resort detalhados

**Quando usar:** importação de muitos meshes, vegetação, iluminação, multidões, grande extensão, builds lentas ou FPS baixo.

## Regras
- Não trocar toda a arquitetura premium por low-poly final. O LOD distante pode ser simplificado sem comprometer close-ups.
- Não alegar 60 FPS nem uso de CPU/GPU sem profiling em cena executada.
- Partir da geometria 2 km² e medir densidade visível, não carregar tudo com milhares de scripts per-GameObject.

## Estratégia
1. Separar geometria por quadras/lotes e zonas de distância, mantendo IDs GIS, para futura ativação aditiva e streaming.
2. Reduzir renderizações desnecessárias: frustum/occlusion culling, LODGroups para edifícios/árvores, luzes por distância e limites de sombras.
3. Reutilizar materiais e malhas onde coerente sem repetir aparência de fachada; testar GPU instancing e GPU Resident Drawer com cenários reais.
4. Usar atlas/material variants com cuidado; preservar normal maps/smoothness e aparência dos pisos.
5. Setorizar colisões; não criar MeshCollider pesado por triângulo quando colisores simplificados preservarem o gameplay.
6. Cache/pooling para pedestres/veículos; atualizar IA de acordo com LOD de simulação e distância.
7. Perfil de QA: draw calls/batches, SetPass, memória, frame CPU/GPU, FPS p95, distâncias de sombra, contagem renderers e tamanho da build.
8. Testar otimizações **uma de cada vez** e rejeitar opções mais lentas; occlusion GPU nem sempre ajuda.

## Critério de saída
- Antes/depois comparáveis na mesma máquina/câmera e qualidade, sem perda visual perceptível no foco.
- Quando sem Unity/licença, registrar hipótese técnica e testes estáticos; nenhuma métrica inventada.

## Referências
- https://docs.unity.com/en-us/engine/6000.6/manual/analysis/graphics-performance-profiling/in-urp/gpu-culling
- https://unity.com/how-to/gpu-optimization
- https://github.com/Unity-Technologies/skills
