---
name: hud-ux-gestao
description: Build accessible and clear mouse-keyboard HUD and management interfaces for a realistic PC tycoon game.
---

# HUD de gestão e primeira pessoa

**Quando usar:** menu, inventário, construção, contratos, dinheiro, missões, avaliação e relatórios de hotel.

## Processo
1. Separar interface de dados e gameplay; UI só recebe modelos/estados e dispara comandos validados.
2. Priorizar PC 1920×1080 com escalonamento para 1366×768 e ultrawide; testar teclado, mouse, navegação e resolução.
3. HUD compacto: dinheiro, reputação, demanda/ocupação, hora, objetivo atual e ações contextuais. Não obstruir visão do quiosque ou praia.
4. Menu de obras com categorização, custo, pré-visualização, aprovação/cancelamento e propriedade; resumo de hotel por ocupação, quartos, salários e manutenção.
5. Texto legível em paisagens claras/escura, contraste e feedback claro sobre por que a ação falhou.
6. Em geral não usar `OnGUI` como interface final: usar UI Toolkit ou Canvas/uGUI conforme fluxo e compatibilidade do projeto.
7. Versionar wireframes/estados aprovados; não alterar mecânicas apenas para acomodar o layout.
8. Testar fluxos críticos antes de afirmar usabilidade.

## Critério de saída
- Menus navegáveis sem esconder o cenário, estado consistente com economia e testes de resoluções.

## Referências
- https://docs.unity3d.com/Manual/UI-system-compare.html
- https://github.com/Unity-Technologies/skills
