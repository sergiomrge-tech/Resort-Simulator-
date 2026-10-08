# R1 — Unity Copacabana | evidência de desenvolvimento

Data: 2026-10-08. Responsável: ChatGPT, trabalhando diretamente no GitHub.

## Implementado em código (ainda sem validação Unity)

- `ResortWorldBuilder.cs`: mantém FBX/Blender real e gera cena de inspeção com limites medidos, dois materiais contrastantes, iluminação, colisão estática, piso exclusivamente temporário e jogador em primeira pessoa.
- `PlayerController.cs`: WASD, corrida, pulo, mouse, gravidade e CharacterController; suporta novo Input System e fallback legado por compilação condicional.
- `DayNightCycle.cs`: relógio e sol configuráveis, independente de economia/clima.
- FBX com GUID de importação versionado, sem alterar bytes do modelo.
- GitHub Actions de static QA, gate de licença e tentativa de build Windows GameCI se credenciais existirem.
- Testes estáticos locais/CI escritos; aguarda resultado efetivo do workflow.

## Não realizado / não aprovado

- **Ainda não houve compilação, parsing, execução ou screenshot real da Unity.**
- **Não há Windows EXE jogável validado.** Com GitHub Actions sem licença compatível, o job Windows fica bloqueado.
- O projeto possui URP 17.3 em `manifest.json`, mas não tem URP pipeline asset configurado/validado. O builder evita material rosa usando shader compatível com o pipeline atualmente ativo.
- Falta verificar se a Unity 6000.3.9f1 e os pacotes configurados estão disponíveis/compatíveis no runner.
- Modelo real é volumetria geográfica; fachadas finais, morros, calçadão, praia, piscinas, água e resort não estão prontos.
- Configuração dos pontos de spawn, renderização, colisões, desempenho, orientação local e capturas dependem de validação na Unity.

## Regras de controle de qualidade

- Manter originais `ArtSource/Blender/Copacabana_BlenderGIS_UTM23S.blend` e `UnityProject/Assets/ImportedBlender/Copacabana_Real_Blender.fbx` inalterados.
- Área **2 km²** (não 2×2 km); validação geométrica do FBX em execução Unity pendente.
- Toda alteração vai a PR para revisão antes de `main`.
- O workflow não substitui a inspeção da cena Unity.

## Próximas ações

1. Aguardar CI estático e corrigir erros reais.
2. Configurar licença apropriada da Unity para cloud, caso disponível; rodar GameCI e avaliar log.
3. Capturar imagem do **Unity** e avaliar qualidade/colisões.
4. Só após aprovação liberar R2 (biblioteca arquitetônica).
