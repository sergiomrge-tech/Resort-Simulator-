---
name: construcao-modular-lotes
description: Implement a grid-assisted construction simulator that respects actual OSM parcels, upgrades and zoning constraints.
---

# Construção e ampliação de quiosque até resort

**Quando usar:** compra de terrenos, grid building, colocação de cômodos, hotel, mobília, permissões e progressão de propriedades.

## Processo
1. Definir área editável do jogador em polígonos locais, **não** todo mapa OSM. O que não pertence ao jogador é cenário visual e não pode ser demolido casualmente.
2. Grids auxiliares alinhados à construção/lote, não forçar a malha OSM inteira a uma grade artificial.
3. Ferramenta de posicionamento: preview com colisão, rotação em passos, snap de parede/chão, validadores de suporte, lotes, acessibilidade e custo.
4. Introduzir peças por módulo: piso, parede, porta, janela, teto, mobiliário, elétrica e hidráulica em complexidade crescente.
5. Evitar paredes voadoras, portas sem abertura, áreas sem entrada ou construção invadindo calçadão e avenida.
6. A compra/aprovação da construção deve ser atômica: validar dinheiro, posse, encaixe e regras antes de descontar saldo e persistir save.
7. Peças precisam ter GUID/ID estável, catálogo versionado, materiais licenciados e histórico de upgrades.
8. Testar: colocar, girar, cancelar, vender/remover onde permitido, save/load e upgrade; nenhuma duplicação de valores.

## Critério de saída
- Ao menos um cômodo completo com porta e caminho acessível, construído com custo correto, persistente e sem conflitos espaciais.
- Respeita lote aprovado; não altera mapa GIS global.

## Referências
- `docs/DIRECAO_ARTISTICA.md`
- https://github.com/Unity-Technologies/skills
