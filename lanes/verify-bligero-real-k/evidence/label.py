"""verify-bligero-real-k: write the verdict labels from the recorded runs' outputs (prints the commands with --dry)."""
import json, subprocess, sys
from pathlib import Path

RUN, SETRUN = "r20260926-062503-d9c2", "r20260926-061022-eac8"
BY = "verify-bligero-real-k"
cells_dir = Path.home() / ".research/runs" / RUN / "cells"
sess = json.loads((Path(__file__).parent / "sessions-check.json").read_text())
VRUN = {"US-KS-2": "r20260926-041624-7d7b (vy-bligero-real-k-verifier)", "US-GA-2": "r20260926-051030-a6fe (vy-bligero-real-k-verifier-ga2)"}
dry = "--dry" in sys.argv
for c in sys.argv[1:]:
    if c.startswith("--"):
        continue
    s = json.loads((cells_dir / c / "summary.json").read_text())
    rv, st = s["reverify"], s["input_set_check"]
    ss = next(v for k, v in sess.items() if k[4:].startswith(c))
    assert rv["status"] == "PASS" and ss["ok"] and st["ir_verify"]["ok"] and st["content_digest_eq_cell"] and st["prover_staged_copy"]["equal"]
    assert st["files_vs_manifest"] == "all match"
    reps = rv["reps"]["rep1"]
    secs = round(sum(x["verify_seconds_sum"] for x in rv["reps"].values()), 3)
    sids = [x["session"] for x in ss["sessions"]]
    vrun = VRUN[ss["sessions"][0]["verifier_dc"]]
    note = (f"{BY} (non-producer) file re-verification at main 1b818427 on pod vy-verify-bligero-real-k (run {RUN}; pins + first set "
            f"check run {SETRUN}). Input set {s['input_set'][:12]} re-staged from the store: files = its manifest, content digest = the "
            f"cell's, {st['ir_verify']['checked']}/{st['n']} outputs re-evaluated equal by the IR evaluator (input_sets.verify), byte-identical "
            f"to the prover's staged copy. reverify.verify_tree (main; reverify's entry point misses the nested sweep/*/proofs dir): custody "
            f"{rv['custody']['files']}/{rv['custody']['files']}, system PINNED {rv['relation']} (= my own compile; the 16 real-K pins "
            f"confirmed), a/b/y commitments recomputed from my staged set, every VU covered once, batch {reps['accepted']}/{reps['n']} at "
            f"2^-{reps['batch_bits']:.2f}. Live verifier records ({vrun}; {sids[0]}..{sids[-1]}): 5/5 sessions accepted "
            f"{reps['n']}/{reps['n']} with fresh verifier coins, system sha256 = my compile, rep-1 proofs/statements/coins = the dump. "
            f"Recorded coins replayed: not transferable. Not judged here: the cell's interaction cell_problem.")
    verifier = (f"{rv['verifier']['tag']} built on pod vy-verify-bligero-real-k from main 1b818427 + backends.direct.ligero.reverify."
                f"verify_tree (main) via lanes/{BY}/evidence/pod-scripts/cell_check.py")
    for key, val, extra in (("verified", "accepted", []), ("verifier", verifier, []), ("verifier_seconds", str(secs), ["--value-json"]),
                            ("same_device", "false", []), ("note", note, [])):
        cmd = ["research", "data", "label", s["cell"], key, val, "--by", BY, "--ref", RUN, *extra]
        if dry:
            print(" ".join(cmd[:6]), "...", len(val))
        else:
            r = subprocess.run(cmd, capture_output=True, text=True)
            print(c, key, r.returncode, (r.stdout + r.stderr).strip()[-200:])
            if r.returncode:
                sys.exit(1)
    if dry:
        print(note)
