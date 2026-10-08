# Project Resort — Desenvolvimento GitHub-first (sem PC ligado)

**Decisão do proprietário em 08/10/2026:** o GitHub é a fonte da verdade para desenvolvimento, assets, histórico e builds distribuíveis. Não exigir desktop remoto, PC Windows, Unity local ou agentes externos para as etapas rotineiras. O PC só é recurso opcional para importações pontuais, execução humana e recebimento de executável.

## Repositório principal

- Repositório: https://github.com/sergiomrge-tech/Resort-Simulator-
- `main`: fonte cartográfica real, documentação canônica, 13 skills, história de campanha e a biblioteca de modelos autorais importados do PC.
- [R1 — PR #5](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/5): geração da cena geográfica, URP, primeira pessoa, câmera e build Windows em C# (ainda sem compilação do Editor real).
- [R2 — PR #10](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/10): três módulos de fachada, texturas PBR, preview Blender e candidatos OSM para um piloto de 300 × 300 m. Desenvolvimento visual ainda em revisão.
- `docs/backlog/fase2-quiosque`: prompts originais, fila, CustomerNPC e OrderBubbleUI preservados para depois de finalizar a arte; **não incluir no build agora**.

## Fonte de materiais agora disponível sem PC

Exportação feita uma única vez, da biblioteca local de autoria própria, para `ArtSource/LocalProjectOwned/` via [PR #12](https://github.com/sergiomrge-tech/Resort-Simulator-/pull/12), já integrada à `main`.

- **38 arquivos de origem:** 13 fontes Blender, 8 FBX, 8 previews Blender, 2 scripts e 7 documentos/manifestos próprios.
- Kit de oito tipologias arquitetônicas costeiras (`CoastalUrbanKit`).
- Quiosque premium, versão LOD1, terminal POS e assets adicionais (guarda-sol, quiosque base).
- Declarações de origem em `SOURCE.md`/`SOURCE.json`; não foram copiados pacotes proprietários, Asset Store, Renderpeople ou segredos.
- Manifesto `ArtSource/LocalProjectOwned/SOURCE_SHA256_MANIFEST.json` registra SHA256 do arquivo local original e dos bytes do GitHub. Normalização de EOL nos textos e compressão Zstandard de `.blend` foram contabilizadas na auditoria.
- QA `.github/workflows/source-assets-archive-qa.yml` **executado com sucesso sem acesso ao PC**: https://github.com/sergiomrge-tech/Resort-Simulator-/actions/runs/37860807539.
- Estão **arquivados como materiais-fonte**, não posicionados na geografia, nem automaticamente aprovados como visual de produção.

## Fluxo de produção sem desktop remoto

1. Atualizar sempre o **GitHub** em branch específica de cada etapa e abrir PR com checklist e evidências.
2. **Blender:** gerar FBX, texturas, previews verdadeiros, testes de geometria e logs via GitHub Actions. Salvar os FBX/PNG e relatórios na branch, com licença e SHA.
3. **Unity:** manter fontes em `UnityProject/`, criar materiais/cenas via scripts Editor idempotentes, e configurar Actions para compilar com Unity 6000.3.9f1. A versão local 6000.6.2f1 pertence a uma linha antiga separada; não misturar cenas e prefabs sem migração testada.
4. **Build cloud:** `.github/workflows/r1-unity-cloud.yml` já define `game-ci/unity-builder@v4` para Windows, porém necessita credenciais válidas `UNITY_LICENSE` ou conjunto `UNITY_SERIAL`/`UNITY_EMAIL`/`UNITY_PASSWORD` no GitHub Actions Secrets. **Nunca versionar chave de licença no repositório.** Enquanto estiver ausente, o job Unity é `SKIPPED`, mas Blender, Python, arte e documentação devem continuar.
5. **Entrega:** a primeira fonte verificável de novo EXE será um artifact ou release do GitHub gerado por build Unity concluído. Apenas em segundo plano, se Desktop Commander estiver online, copiar o pacote completo `.exe` + `_Data` e dependências para `D:\ProjectResort_Entregas_ChatGPT` com verificações de hashes. PC offline **não suspende produção nem impede publicação do artifact**.
6. Atualizar `docs/checkpoints/LATEST.md` após cada marco aprovado; manter nomenclatura e links únicos.

## Atenção a outro projeto Unity local

Foi encontrado um projeto antigo mais avançado de quiosque/resort em um repositório distinto (`sergiomrge-tech/Simulador-predial`), que usa Unity 6000.6.2f1. Existe um executável local testado em 08/10/2026, mas sua presença **não significa que os assets/cenas dessa linha já foram integrados** ao novo `Resort-Simulator-`. A fonte autoral extraída dessa instalação encontra-se agora na biblioteca GitHub acima; os demais scripts e scenes dependentes devem ser migrados seletivamente em PR própria, sem sobrescrever o mapa real.

**Bugs, logs, QA e screenshots devem vir da execução real da ferramenta.** Nenhuma imagem criada fora da Unity vale como prova da compilação da cena Unity. © OpenStreetMap contributors — ODbL 1.0.
