import os, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, "benchmarks/pouw/tests")
os.environ.setdefault("PYTEST_CURRENT_TEST", "x")
import test_pearl_c_sm120 as T
tmp = Path(tempfile.mkdtemp())
ship = tmp / "ship"; ship.mkdir()
subprocess.run(["cc", "-O1", "-Wall", "-Werror", "-shared", "-fPIC", "-o", str(ship / "fake_cuda.so"), str(T.HERE / "fake_tma.c")], check=True)
shutil.copy(T.HERE / "run.py", ship)
(ship / "pearl_c_sm120.cubin").write_bytes(b"\x7fELF" + bytes(14) + bytes([190, 0]) + bytes(44))
fx = Path(os.environ["FX"]) if os.environ.get("FX") else tmp / "fx"
if not os.environ.get("FX"): fx.mkdir(); T.F.build(fx, 128, 128, 1024)
h = tmp / "harness"; h.mkdir(); (h / "arm.py").write_text(T.ARM_V0); (h / "refs.py").write_text(T.REFS_STUB)
env = T.dry_env(ship, tmp / "accept.jsonl", PEARLC_SHIP=str(ship), PEARLC_ROWS=str(tmp / "rows"), REFS_LOG=str(tmp / "refs.log"), PYTHONFAULTHANDLER="1")
r = subprocess.run([sys.executable, "benchmarks/pouw/tests/pearlc_arm_dry.py", str(h), "PearlCSm120", "accept", str(tmp / "run"), str(fx / "check.json")], env=env, capture_output=True, text=True)
print("rc", r.returncode); print(r.stdout[-2000:]); print(r.stderr[-6000:])
print((tmp / "refs.log").read_text() if (tmp / "refs.log").exists() else "no refs log")
