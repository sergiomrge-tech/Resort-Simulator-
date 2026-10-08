---
name: npcs-animacao-trafego
description: Implement animated visitors, employees and believable beachfront traffic with Unity NavMesh and scalable simulation LOD.
---

# NPCs, equipes e animações naturais

**Quando usar:** turistas, funcionários, multidões, pedestres, tráfego, atendimento, hóspedes e comportamento visual.

## Processo
1. Definir rotas caminháveis reais a partir da geometria avaliada: calçadão ↔ quiosque ↔ travessia ↔ pousada. Não assumir que o FBX já tem malha navmesh pronta.
2. Usar Unity AI Navigation/NavMesh com superfícies e links explícitos, tipando áreas pedestrianas e vias de carro; nunca cruzar a avenida no aleatório.
3. Criar `VisitorBrain`, `EmployeeBrain` e estados curtos (andar, fila, comprar, sentar, aguardar, sair) desacoplados da economia.
4. Personagens 3D com Animator realmente animado: `Idle`, `Walk`, `Run`, `Use`, `Sit`, `Carry` ou equivalentes; confirmar rig, pés no piso e ausência de deslizamento.
5. Identidade visual variada e apropriada a cenário brasileiro; nada de clones todos idênticos ou bonecos parados nas cenas finais.
6. Instanciamento por pooling, LOD de animação e atualização de IA por distância. Somente agentes do setor jogável executam comportamentos completos.
7. Registrar fonte/licença comercial de animações, rigs e personagens, inclusive avatar packs; não extrair modelos proprietários de outros jogos.
8. Se o Unity não puder executar, produzir código e testes de FSM e registrar «runtime pendente».

## Critério de saída
- NPC deixa ponto de origem, caminha por rota permitida, executa atendimento/animação e sai.
- A multidão não atravessa prédios/veículos, não fica estática e mantém desempenho medido.

## Referências
- https://docs.unity3d.com/Manual/com.unity.ai.navigation.html
- https://docs.unity3d.com/ScriptReference/AI.NavMeshAgent.html
- https://github.com/Unity-Technologies/skills
