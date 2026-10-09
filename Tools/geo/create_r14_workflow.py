"""Derive full R7-R14 CI from frozen R13 workflow without editing its source."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    s=(ROOT/'.github/workflows/r13-orla-premium.yml').read_text(encoding='utf-8')
    s=s.replace('name: Resort R13 | native OSM coast premium 200m and scalable sectors','name: Resort R14 | real GIS urban connectors and seven-sector coastal art')
    s=s.replace('branches: [codex/r13-sol61-orla-premium]','branches: [codex/r14-sol61-orla-fullfinish]')
    s=s.replace("paths: ['Tools/**', 'UnityProject/Assets/Editor/ResortR13*.cs', 'UnityProject/Assets/Shaders/R13*.shader', '.github/workflows/r13-orla-premium.yml']", "paths: ['Tools/**', 'UnityProject/Assets/Editor/ResortR14*.cs', 'UnityProject/Assets/Architecture/R14_Urban/**', 'UnityProject/Assets/Textures/R14_Urban/**', '.github/workflows/r14-orla-urban-connectors.yml']")
    s=s.replace('resort-r13-${{ github.ref }}','resort-r14-${{ github.ref }}').replace('timeout-minutes: 65','timeout-minutes: 85')
    i=s.index('      - uses: actions/upload-artifact@v4')
    extra='''      - name: R14 read-only source audit, real 3D connectors and native reimport
        run: |
          set -euo pipefail
          mkdir -p build/R14_QA
          python Tools/geo/generate_r14_surface_art.py
          python -c "import bpy,runpy;runpy.run_path('Tools/Blender/audit_r14_source.py',run_name='__main__')" 2>&1 | tee build/R14_QA/source-audit.log
          python -c "import bpy,runpy;runpy.run_path('Tools/Blender/generate_r14_urban_connectors.py',run_name='__main__')" 2>&1 | tee build/R14_QA/connectors-generation.log
          python -c "import bpy,runpy;runpy.run_path('Tools/tests/test_r14_connectors_native.py',run_name='__main__')" 2>&1 | tee build/R14_QA/connectors-reimport.log
      - name: R14 original coastal kit in seven BASE sectors and real Blender asset renders
        run: |
          set -euo pipefail
          python -c "import bpy,runpy;runpy.run_path('Tools/Blender/generate_r14_coastal_art.py',run_name='__main__')" 2>&1 | tee build/R14_QA/art-generation.log
          python -c "import bpy,runpy;runpy.run_path('Tools/tests/test_r14_art_native.py',run_name='__main__')" 2>&1 | tee build/R14_QA/art-reimport.log
          python -c "import bpy,runpy;runpy.run_path('Tools/Blender/render_r14_asset_qa.py',run_name='__main__')" 2>&1 | tee build/R14_QA/blender-render.log
          python Tools/geo/normalize_r14_meta.py
          python Tools/geo/report_r14_coverage.py
          python -m unittest discover -s Tools/tests -p 'test_r14_contract.py' -v 2>&1 | tee build/R14_QA/contracts.log
          echo 'Unity native and runtime benchmarks require licensed Windows Editor; Linux CI does not generate Unity PNGs.'
'''
    s=s[:i]+extra+s[i:]
    s=s.replace('Resort-R13-Pass2-2km-S04-S06-Art-Pending','Resort-R14-Urban-Connectors-Seven-Sectors-Art-Pending')
    s=s.replace('Resort-R13-Diagnostic-Logs-No-Release','Resort-R14-Diagnostic-Logs-No-Release')
    s=s.replace('            build/R12_CIQA/','''            build/R12_CIQA/
            build/R14_QA/
            UnityProject/Assets/Architecture/R14_Urban/
            UnityProject/Assets/Textures/R14_Urban/
            ArtSource/Blender/R14_*.blend
            ArtSource/Previews/R14_*
            UnityProject/Assets/Materials/R14_Urban/
            UnityProject/Assets/Scenes/R14_Copacabana_*
''')
    s=s.replace('          path: build/R12_CIQA/','          path: |\n            build/R12_CIQA/\n            build/R14_QA/')
    (ROOT/'.github/workflows/r14-orla-urban-connectors.yml').write_text(s,encoding='utf-8',newline='\n')
if __name__=='__main__':main()
