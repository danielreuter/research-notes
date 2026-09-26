import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ENV = dict(os.environ, PYTHONPATH="/workspace/tools/research/src", RESEARCH_STORE=os.path.expanduser("~/.research/store"))
man = json.load(open("/workspace/backends/flock/verifier/vectors.json"))


def one(s):
    v = s["vectors"][0]
    dst = f"/tmp/vec/sessions/{s['record'][4:16]}"
    args = [sys.executable, "-m", "research", "data", "fetch", s["record"], "--to", dst, "--path", v["session"]]
    for p in v["proofs"]:
        args += ["--path", p]
    subprocess.run(args, env=ENV, cwd="/workspace", capture_output=True)
    out = subprocess.run([sys.executable, "/tmp/vec/replay_transcript.py", f"{dst}/{v['session']}"] + [f"{dst}/{p}" for p in v["proofs"]],
                         capture_output=True, text=True)
    return s["cell"], s["statement"], s["detail"], (out.stdout.strip() or out.stderr.strip()[-300:]).replace("\n", " | ")


with ThreadPoolExecutor(6) as ex:
    for r in ex.map(one, man["honest"]):
        print(*r, sep="\t", flush=True)
