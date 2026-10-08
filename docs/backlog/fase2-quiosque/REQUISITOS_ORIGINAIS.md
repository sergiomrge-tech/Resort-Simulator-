# Prompt de Desenvolvimento - Fase 2: O Quiosque, Economia Base e IA de Clientes
Olá Luna! Concluímos a Fase 1 (Setup Visual em HDRP, mapa de 2x2km e movimentação). Agora vamos implementar a **Fase 2: O Quiosque e Economia Base** do nosso jogo *Copacabana Dreams: Do Quiosque ao Império*.

Preciso que você escreva os scripts em C# limpos, modulares e orientados a eventos, além de me guiar no setup dos componentes dentro da Unity.

---

### 1. Escopo Funcional da Fase 2
*   **Economia e Inventário:** Sistema de carteira (dinheiro em R$), compra de caixas de insumos (atacado) e venda fracionada no balcão.
*   **Itens Iniciais:**
    *   *Água Mineral:* Custo R$ 1,50 | Venda R$ 6,00
    *   *Água de Coco:* Custo R$ 3,00 | Venda R$ 12,00
    *   *Caipirinha Tradicional:* Custo R$ 5,50 | Venda R$ 25,00
*   **IA de Clientes (NavMesh):** Turistas e banhistas que spawnam no calçadão, caminham até o balcão do quiosque, fazem um pedido com tempo de espera limitado, pagam e vão embora (ou saem frustrados se demorar).
*   **Interação em Primeira Pessoa:** O jogador interage com o balcão/estoque usando Raycast (tecla `E`).
*   **HUD/UI:** Contador de dinheiro, indicador de reputação (0 a 5 estrelas) e balão de pedido flutuante no cliente.

---

### 2. O que você deve entregar nesta resposta:

Escreva o código C# completo e com comentários didáticos para os seguintes sistemas:

#### A. Arquitetura de Dados e Economia
1.  **`ItemData.cs` (ScriptableObject):** Contendo `itemName`, `costPrice`, `sellPrice`, `preparationTime`, `itemIcon` e `prefab`.
2.  **`EconomyManager.cs` (Singleton / Service):**
    *   Variável de saldo (`currentMoney`).
    *   Métodos `AddMoney(float amount)` e `SpendMoney(float amount)`.
    *   Evento C# `Action<float> OnMoneyChanged` para atualizar a UI sem polling.
    *   Sistema de reputação (`reputationScore`, variando de 0 a 5 estrelas).

#### B. Estoque do Quiosque
3.  **`KioskStockManager.cs`:**
    *   Dicionário ou lista serializável de `ItemData` e quantidade disponível.
    *   Métodos para adicionar estoque (comprar insumos) e subtrair estoque (ao servir cliente).

#### C. Inteligência Artificial de Clientes
4.  **`CustomerNPC.cs` (NavMeshAgent):**
    *   Máquina de Estados finita básica (*FSM*): `ApproachingKiosk`, `WaitingForOrder`, `Satisfied`, `AngryLeaving`.
    *   Timer de paciência (barra de espera). Se o jogador não entregar a tempo, o cliente perde a paciência, reduz a reputação do quiosque e sai.
    *   Geração aleatória de pedido baseado nos itens disponíveis.
5.  **`CustomerSpawner.cs`:** Spawner no calçadão com taxa de surgimento controlável (intervalo em segundos e limite máximo de clientes na fila).

#### D. Interação do Jogador e UI
6.  **`PlayerInteractionRaycast.cs`:** Script anexado à câmera do jogador para disparar Raycast, detectar objetos com a interface `IInteractable` e exibir um prompt "Pressione E para Interagir".
7.  **`UIManager_HUD.cs`:** Script para escutar os eventos do `EconomyManager` e atualizar os textos de Dinheiro e Reputação na tela (usando TextMeshPro).

---

### 3. Passo a Passo de Setup na Unity
Ao final do código, forneça:
1.  Instruções de como configurar a malha de navegação (**NavMesh Surface**) na areia e no calçadão de Copacabana.
2.  Como associar os pontos de parada (fila do quiosque) para que os NPCs não colidam uns com os outros.
