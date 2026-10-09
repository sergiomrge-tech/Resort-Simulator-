"""Run regression + R14 evidence checks and record actual results."""
from pathlib import Path
import sys,json,unittest,py_compile
ROOT=Path(__file__).resolve().parents[2]
def main():
    for directory in ('Tools/Blender','Tools/geo','Tools/tests'):
        for p in (ROOT/directory).glob('*r14*.py'):py_compile.compile(str(p),doraise=True)
    patterns=['test_r7_contract.py','test_r8_winding_geo.py','test_r10_capture_integrity.py','test_r11_capture_integrity.py','test_r12_capture_integrity.py','test_r13_unity_native_import_contract.py','test_r13_contract.py','test_r13_pass2_contract.py','test_r14_contract.py']
    loader=unittest.TestLoader();suite=unittest.TestSuite()
    for pattern in patterns:suite.addTests(loader.discover(str(ROOT/'Tools/tests'),pattern=pattern))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    q={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'skip_reasons':[reason for test,reason in result.skipped],'patterns':patterns,'python_version':sys.version,'unity_compilation_evidence':False}
    (ROOT/'ArtSource/Previews/R14_PythonQA.json').write_text(json.dumps(q,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
if __name__=='__main__':main()
