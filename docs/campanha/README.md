# Campanha narrativa — Copacabana Empire: Ouro, Sal e Concreto

## Fonte da verdade
- **Texto do usuário, preservado integralmente como recebido:** [COPACABANA_EMPIRE_OURO_SAL_E_CONCRETO.md](./COPACABANA_EMPIRE_OURO_SAL_E_CONCRETO.md).
- **Natureza:** roteiro de campanha ficcional para o jogo Unity atualmente denominado `Resort Simulator — Costa Carioca`.
- **Nome da campanha:** `Copacabana Empire: Ouro, Sal e Concreto`, sem alteração automática do nome do repositório, do aplicativo ou do jogo.
- **Estado:** foram recebidas as seções **1 (lore)**, **2 (personagens)** e o **título da seção 3**. A descrição detalhada dos atos, missões e desfechos de 0 a 50 horas **não veio no texto enviado**; não marcar a campanha como roteiro completo nem inventar sua conclusão.

## Registro canônico para integração futura
Estes identificadores são *proposta técnica*, não alterações no texto narrativo original.

| ID persistente | Referência narrativa | Papel de gameplay |
|---|---|---|
| `npc_agenor_silveira` | Agenor "Sombra" Silveira | Herança, memória e documentos do quiosque |
| `npc_dona_carmen` | Dona Carmen | Fornecimento e mentoria |
| `npc_tiago_mendes` | Tiago "Traço" Mendes | Construção e expansões |
| `npc_mauricio_valadares` | Dr. Maurício Valadares | Antagonista e disputa imobiliária |
| `npc_inspetor_brandao` | Inspetor Brandão | Inspeções e regulamentação |
| `npc_chloe_davenport` | Chloe Davenport | Avaliação hoteleira |
| `poi_sol_de_prata` | Quiosque O Sol de Prata | Propriedade inicial do jogador |
| `org_apolo_capital` | Apolo Capital / Grupo Valadares | Pressão corporativa |
| `poi_torre_atlantica` | Torre Atlântica | Projeto do antagonista |

## Sistemas de campanha já implicados pelo enredo
- **Início:** propriedade degradada, dívida fiscal de R$ 180.000 e escrituras parciais; nenhum dado deve ser convertido em débito real do usuário.
- **Evolução:** reconstrução do quiosque, fornecimento, aquisição e expansão de empreendimentos, avaliação da experiência hoteleira.
- **Conflitos:** pressão jurídica/econômica, inspeções, eventos de suprimento e reputação, com contrajogadas claras e escolhas de identidade.
- **Decisões:** tradição cultural ou expansão agressiva, sem forçar final ou missão ainda não escritos.
- **Sem missões de enredo implementadas em Unity nesta etapa.** Só a fonte narrativa e os vínculos técnicos são entregues aqui.

## Compatibilidade com o mapa já preservado
O roteiro fornecido cita **2 × 2 km (4 km²)**, enquanto a fonte geográfica já versionada em `geo/data/report.json` usa **2 km² de recorte**. São especificações diferentes. **Não esticar nem regenerar o modelo Blender/FBX** para mascarar a divergência. A abrangência final da campanha deverá ser reconciliada em planejamento, preservando a geometria geográfica que já existe.

## Gates antes da implementação narrativa
1. Consolidar a R1 de importação e primeira cena Unity; verificar build e localização real dos POIs.
2. Associar os identificadores a dados de história serializáveis, sem nomes hardcoded na lógica.
3. Elaborar o conteúdo da seção 3 em seguida, com atos, objetivos, estados e duração aproximada, mantendo o roteiro recebido como texto original.
4. Vincular quests, salvamento e reputação à progressão de negócios; validar consequências e conflitos de narrativa antes da campanha jogável.
5. Testar gameplay em Unity; a existência deste documento **não** significa missão jogável.

## Direção de produção
Manter visual **Realismo Estilizado Premium**, preservar autoria e não inventar ruas, prédios ou referências geográficas. Personagens e empresas da trama são ficcionais.
