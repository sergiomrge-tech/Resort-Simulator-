# Resort Simulator — Costa Carioca

Jogo original de gestão e evolução de resort cinco estrelas na costa brasileira, desenvolvido **do zero em Unity 6.3 LTS** para Windows/Steam. Sem código, assets ou dependência do antigo Simulador Predial.

**Checkpoint: 08/10/2026 — W1 fundação geográfica.** Fonte do mapa: OpenStreetMap real; área jogável 2.000 × 1.000 m (2 km²) junto à orla de Copacabana. A geração em Python da malha geográfica e a configuração de Unity/GameCI são fases técnicas; **não confundir volumetria OSM com arte final ou build jogável**.

## Diretórios

- `UnityProject/`: projeto Unity 6000.3.9f1 (Unity 6.3 LTS); cena gerada via editor.
- `geo/`: geografia da Copacabana, exportação real OSM para OBJ e relatório/licença.
- `docs/`: direção artística, roadmap e checkpoints.
- `.github/workflows/`: validação Python e builds de Windows via GameCI.

## Como trabalhar

1. Fluxo padrão sem PC: GitHub Actions obtém dados OSM e compõe OBJ + metadados. A saída pode ser baixada como artifact; o workflow pode persistir malhas na branch `main` via commit automatizado.
2. Somente após existir `UnityProject/Assets/ImportedOSM/copacabana_base.obj`, o pipeline Unity gera a cena `Assets/Scenes/Copacabana_Pilot.unity`.
3. Com licença Unity adequada em GitHub Actions Secrets, o GameCI tenta importar, compilar e publicar um artefato Windows. Sem licença, o job informa bloqueio e não diz que compilou.
4. No PC, abrir `UnityProject/` pela Unity 6.3 LTS e gerar/corrigir/aprovar uma captura **real** da execução.

## Controles do protótipo geográfico

WASD deslocamento, Q/E subida/descida, Shift velocidade e botão direito do mouse para olhar.

## Documentação

`docs/DIRECAO_ARTISTICA.md` define a cidade e a evolução do Resort. `docs/STATUS.md` registra exatamente o que já foi testado.

## Licenças

Mapa: © OpenStreetMap contributors — ODbL 1.0, https://www.openstreetmap.org/copyright.
Código original deste repositório não incorpora materiais proprietários de terceiros.

**Atenção:** no primeiro estágio não existem fachadas PBR finais, modelos premium de hotel, piscina nem relevo DEM real. Arquivos 3D por extrusão são uma **referência métrica transitória**, não o acabamento aprovado.
