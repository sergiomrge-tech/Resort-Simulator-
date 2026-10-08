# Arquivo de prompts e scripts recebidos — Fase 2 do Project Resort

**Registrado em:** 08/10/2026  
**Status:** ARQUIVADO / NÃO IMPLEMENTAR ANTES DE CONCLUIR A FASE VISUAL  
**Motivo:** o usuário solicitou guardar o conteúdo colado na conversa para desenvolvimento posterior, após concluir o processo visual do jogo.

## Conteúdo original preservado

| Conteúdo | Arquivo | Estado |
|---|---|---|
| Prompt completo da Fase 2: quiosque, itens, economia, IA e interface | [REQUISITOS_ORIGINAIS.md](REQUISITOS_ORIGINAIS.md) | Texto do usuário preservado |
| Script `KioskQueueManager` — lista, slots, reorganização, gizmos | [rascunhos/KioskQueueManager.cs.txt](rascunhos/KioskQueueManager.cs.txt) | Rascunho C# original preservado |
| Script `CustomerNPC` — posição na fila e orientação | [rascunhos/CustomerNPC.cs.txt](rascunhos/CustomerNPC.cs.txt) | Rascunho C# original preservado |
| Script `OrderBubbleUI` — balão world-space, billboard, timer radial, animação | [rascunhos/OrderBubbleUI.cs.txt](rascunhos/OrderBubbleUI.cs.txt) | Rascunho C# original preservado |
| História e personagens de `Copacabana Empire: Ouro, Sal e Concreto` | [docs/campanha/COPACABANA_EMPIRE_OURO_SAL_E_CONCRETO.md](../../campanha/COPACABANA_EMPIRE_OURO_SAL_E_CONCRETO.md) | Salvo anteriormente na `main`, não duplicado |
| Índice narrativo e personagens | [docs/campanha/README.md](../../campanha/README.md) | Salvo anteriormente na `main` |

**Observação:** o pedido menciona também `ItemData.cs`, `EconomyManager.cs`, `KioskStockManager.cs`, `CustomerSpawner.cs`, `PlayerInteractionRaycast.cs`, `UIManager_HUD.cs` e `IInteractable`, mas o usuário **não colou os arquivos C# dessas classes** na conversa. Portanto estão especificados no prompt, mas não arquivados como código preexistente.

## Regras antes de retomar a Fase 2

1. **Prioridade ativa:** concluir mapa, arquitetura e orla no padrão Realismo Estilizado Premium e aprovar evidências reais de Unity (R1/R2/R3).
2. Manter `docs/backlog/fase2-quiosque/rascunhos/*.cs.txt` **fora de `UnityProject/Assets`** para impedir compilação acidental, colisões de nomes e erros de dependência.
3. Quando autorizado a implementar, usar os rascunhos como **fonte de referência**, não presumir que estejam prontos para produção. O `CustomerNPC` colado é parcial e não implementa a FSM/pedidos; o `KioskQueueManager` chama `SetDestination` sem checar `agent.isOnNavMesh` ou amostragem do slot; o giro `LookRotation(transform.forward)` no NPC não altera a direção; o `OrderBubbleUI` requer Canvas world-space, imagens e Canvas/UI configurados no Inspector. Esses itens exigirão integração e testes.
4. O prompt original menciona **HDRP e mapa 2 × 2 km como concluídos**, mas o repositório atual utiliza **URP** e a origem GIS declara recorte de **2 km²**. Não reconfigurar pipeline ou alterar a geografia com base nessa frase histórica.
5. Consolidar economia por serviço orientado a eventos, operações atômicas de estoque+dinheiro, fila por reservas de slots NavMesh válidos, tratamento de saída/destruição dos NPCs, UI por eventos e saves versionados.
6. Os preços iniciais do prompt devem ser tratados como dados de **game design** e configurados em assets, não como valor monetário de transação real.
7. A história enviada anteriormente termina no título da seção 3; os atos detalhados da campanha ainda não foram enviados.

## Como retomar no futuro

> Retome o Project Resort a partir do GitHub. Consulte `docs/checkpoints/LATEST.md`, `docs/campanha/` e este índice. Termine primeiro a validação da fase visual e só então implemente os sistemas arquivados da Fase 2; use as fontes originais sem substituí-las silenciosamente.

**Estes arquivos não representam código Unity compilado, cenas geradas, personagens prontos, testes de runtime nem promessa de implementação concluída.**
