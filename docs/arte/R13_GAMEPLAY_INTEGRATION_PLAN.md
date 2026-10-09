# R13 — integração ao gameplay sem alterar o checkout sujo

Esta rodada não abriu nem modificou `D:/sergi/Documents/Simulador-predial`. A comparação de arquitetura com FacilityOps permanece pendente; não afirmar que seus componentes foram inspecionados.

1. Depois do gate visual R13, obter clone limpo do repositório gameplay, branch própria. Registrar HEAD, versão Unity, manifest/lock dos pacotes, URP ativo, cenas do menu/mundo, input, sistema de coordenadas e GUIDs. Comparar com este `UnityProject`: alvo 6000.6.2f1; o manifest local declara URP 17.3.0, enquanto o brief cita 17.6. Resolver a versão por compilação numa cópia de QA, nunca alterar silenciosamente o jogo funcional.
2. Produzir prefab/subcena visual a partir da cena derivada R13, sem câmera, sol, EventSystem, menus, NPCs, economia ou scripts de save. Manter OSM IDs, frame e origem métrica. O jogo controla câmera, ciclo diurno e qualidade; a subcena controla somente meshes/materials geográficos.
3. Fazer tabela de propriedade antes de carregar: mar/areia/passeio/ruas vêm da subcena; player/input/HUD/economia/saves/missões vêm do gameplay. Associar quiosques existentes por ID/posição; não criar um segundo sistema. Ocultar ambiente antigo somente após checar duplicidade e colisores. Não importar `Library`, caches, ferramentas remotas ou credenciais.
4. Restaurar player no mesmo referencial e validar colisões/caminhada, portas e degraus. R12/R13 são decoração; não abrir portas por aparência. Testar abrir → iniciar/continuar → caminhar → interagir → construir → salvar/carregar → sair, com fixture de save anterior e cópia de backup.
5. Testar cenas equivalentes 1080p Alto/Médio/Baixo; registrar CPU/GPU, p95, drawcalls, triângulos, memória e carregamento. Os LOD de mobiliário precisam de tuning com câmera real. Validar água animada em Play Mode, dia/tarde/noite, rampas e cruzamentos.
6. Somente após esses gates, build Windows em pasta versionada nova e smoke test do conteúdo R13 presente. PR draft em ambos os repositórios, revisão do proprietário e **sem merge automático**. Preservar atalhos e último executável funcional.

Bloqueios desta sessão: Unity Package Manager IPC local indisponível; dependências GIS ausentes e downloads bloqueados. Portanto não houve cena R13 compilada, build Windows, integração ou teste de saves. O pipeline de geração Blender continua independente de PC ligado via Actions.
