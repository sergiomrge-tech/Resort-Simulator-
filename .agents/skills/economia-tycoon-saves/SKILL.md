---
name: economia-tycoon-saves
description: Implement transparent kiosk-to-resort economics, guest satisfaction, staff expenses and resilient versioned game saves.
---

# Tycoon: caixa, operação e dados persistentes

**Quando usar:** economia, reputação, inventário, estoque, receitas, funcionários, contratos, aluguel e saves.

## Objetivo do gameplay
Criar ciclo satisfatório de **quiosque → quarto → pousada → resort**. Regras fictícias originais que façam sentido no Rio; evitar reproduzir burocracias reais sem dados e licenças.

## Processo
1. Definir `GameClock`, `Economy`, `Inventory`, `GuestNeeds`, `Staff`, `Construction`, `Save` em módulos com interfaces pequenas; cena e UI não conhecem detalhes de cálculo.
2. Tudo que altera dinheiro deve produzir **transação imutável** `id`, instante, origem, valor, motivo e saldo; nunca deixar saldo negativo sem regra.
3. Custos consistentes por unidade e tipo (suprimentos, energia, salários, reparos e manutenção); balancear com cenários determinísticos.
4. Realizar testes de compra/venda, reposição, abertura/fechamento do quiosque, aluguel, cancelamento, manutenção, limite de lotes e upgrades.
5. Save local versionado com schema, cópia de segurança e migração; não usar PlayerPrefs para estado principal; write-then-rename seguro.
6. Separar todos os números de jogo em `ScriptableObject`/arquivos versionados legíveis; criar telemetria de simulação sem dados pessoais.
7. Não ativar simulação de cidade inteira quando um lote inicial é suficiente.

## Critério de saída
- Ciclo comprar → vender → lucrar comprovado por testes determinísticos; saves recuperam progresso sem duplicar operações.
- HUD refletindo valores verdadeiros; nenhuma economia improvisada via `Update()` ou números mágicos escondidos.

## Referências
- https://docs.unity3d.com/ScriptReference/JsonUtility.ToJson.html
- https://github.com/Unity-Technologies/skills
