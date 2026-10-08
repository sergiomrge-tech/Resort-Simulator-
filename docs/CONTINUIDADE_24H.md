# Protocolo de continuidade e anti-travamento — Resort Simulator

## O que é e o que não é possível

- **Não existe garantia de que o aplicativo ChatGPT nunca trave.** Prevenimos a perda de contexto com checkpoints, commits, logs e tarefas curtas.
- O ChatGPT não executa uma sessão de código local permanentemente em 24/7 nem controla Unity sem acesso a uma execução real. A **automação horária** é uma invocação periódica, sujeita a cotas, ferramentas e condições.
- **GitHub Actions** usa runners efêmeros; pode auditar arquivos e executar Blender/Python com o PC desligado. Build Unity requer licença/Editor aptos no runner.
- Prometer uma atividade futura não substitui agendá-la; cron do GitHub só fica ativo na branch default depois da integração do workflow.

## 1. Fragmentação deliberada da produção

- Executar por unidade de trabalho de **um PR ou um componente**, com critérios de aceite e testes.
- Na mesma iteração, ler o HEAD e PRs antes de editar, para não duplicar tarefas ou sobrescrever commits de outra sessão.
- Comitar alterações testáveis em branch nova; não deixar o único resultado em texto de chat.
- Manter `docs/checkpoints/LATEST.md` conciso e atualizado **após marcos verificáveis**, não após cada mensagem. Arquivar decisões complexas em `docs/`.
- Se uma ferramenta falha, registrar a falha e seguir apenas tarefas independentes; nunca inventar avanço.

## 2. Recuperação rápida de um chat travado

1. Abrir nova conversa dentro do **mesmo projeto** ChatGPT.
2. Escrever: `Retome o Resort pelo GitHub. Leia docs/checkpoints/LATEST.md, identifique a branch mais recente e os Actions, e continue sem repetir etapas prontas.`
3. O novo chat deve ler o checkpoint, comparar commits e PRs reais, escolher próximo menor marco e dar sequência ao código.
4. Capturas reais de Blender/Unity devem preservar proveniência. Nunca usar imagem conceitual como print do jogo.

## 3. Agenda automática

- **ChatGPT Automations:** revisão horária do projeto, trabalhos pequenos e seguros possíveis e notificações só quando houver mudança relevante.
- **GitHub Actions:** auditoria de integridade do mapa, estrutura e PRs a cada 6 horas após merge do workflow; sem merge automático.
- Nada executa instruções de edição infinitas sem supervisão. Evitar conflitos: uma branch por iteração, verificação de lease de HEAD ao gravar.

## 4. Gates e bloqueios que não se pode esconder

- R1: 7/7 testes estáticos, mas **SEM Unity compilada** até ativação licenciada e execução com logs; PR #5 permanece draft.
- R2: não produzir muitas fachadas genéricas antes de aprovar três fachadas diferentes na Unity.
- R3: resort e calçadão apenas depois de trecho inicial realista e integração de gameplay, sem áreas vazias.
- Exigência de origem: preservar Blender 3,1 MB e FBX métrico; mapa tem **2 km²**, não 4.

## 5. Regras de segurança

- Não modificar `Simulador-predial`.
- Não colocar segredos ou arquivos Unity license no commit, nos relatórios nem nos logs.
- Não tornar QA estática equivalente a gameplay testado.
- Não autorizar merge automático de código não executado.
- A auditoria automática é **read-only**; seu relatório é artifact, não reescreve `main`.

## Diagnóstico da falta de build

GitHub R1 Actions 37854021618: static QA sucesso, etapa GameCI SKIPPED por `NOT_BUILT: LICENSE_MISSING`. Essa limitação é visível ao proprietário; a auditoria não pode inventar outro resultado.
