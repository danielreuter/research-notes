"""verify-night: register one verification-verdict/v1 per instance-equiv/v1 file (payload: that relation's evidence) and label
the equivalence verified=accepted --by verify-night --ref <verdict>, only when all three checks passed for it.

    python3 label_equivs.py EVIDENCE_DIR [REL ...]     # default: all 15, priority order
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

R = str(Path.home() / ".research" / "bin" / "research")
ARTS = {
    "fp8-ada-v2": "art:68466c4ad6b8197ea9624fb6b50037f5338e098a1cec9bfa03c014e86eb8c3f2",
    "fp8-ada-v3x4": "art:d40f506558d4018603db042cb5acee0bc970669440dae1457dbce553e79a79b6",
    "bf16-hopper-v3x4": "art:bfd18a1dd63ce548a54dfc4ecfdf7577ee377b6a599d39dd75017e798b16347a",
    "fp8-hopper-v3x4": "art:0749fa9dcecddd0878f753f010c87f7d3cfd43e3a356a1680a4a333acbbc35c5",
    "fp8-ada-v3": "art:574f35193ba5abb8a5d068547e6ced872006d987ade31f65aa234c52a025743d",
    "fp8-ada-v2x4": "art:f355573b4b2caa5ac595bb13142fa3084d364145907670827e4e3b54514eb300",
    "fp8-ada-x4": "art:f70cf39fef166b540e60ccc48a55fed4babd55fdfef40179c4bfaf9dff744eef",
    "bf16-hopper-v2": "art:b5584b28cabbf0c4570c3d2554c969389461abe74f4f37b268b7f35ddfb43648",
    "bf16-hopper-v3": "art:5133f6c11ad967763ccf855af7a1b16096e96eee1a1615fa2003b86396020812",
    "bf16-hopper-v2x4": "art:95df4a8ebc29c4a27be68933637afc620189917a0b3750990fd593683cd92850",
    "bf16-hopper-x4": "art:9c8c306ce225c2642dfe46415f36872892835ffd55ed9062d0c996f2aaddb741",
    "fp8-hopper-v2": "art:539af2c6e68ba85b1d2dd7cc2783b11cc7a9db72b8b5dc2e206a30a953a8aa64",
    "fp8-hopper-v3": "art:8036d0ba0d79158bf24c22522879690ceba456f5023595cc1640947886730178",
    "fp8-hopper-v2x4": "art:59193d43fe1b8b4d3fd7dc2a8be0844e014faf51170925a747821b07d78af257",
    "fp8-hopper-x4": "art:4cd768c2ae554be61e74874c5dca7f31bcdf0cc1a5bcb6898e0e5f2829c0dca4",
}
TOOL = ("verity_numerical.bench.instance_equiv --check and --out-dir regeneration at lane/verify-night@1b3c7be6 (instance_equiv.py as "
        "fused-phases 9989797f) + verify-night's independent full-chain cross-check (lanes/verify-night/evidence/pod-scripts/"
        "05-equiv-independent.py), on pod vy-verify-night (CPU, torch 2.6.0+cpu, no instance cache)")


def run(*a):
    r = subprocess.run([R, *a], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{' '.join(a[:3])}: rc {r.returncode}: {r.stderr[-800:]}")
    return r.stdout.strip()


def main():
    ev = Path(sys.argv[1])
    rels = sys.argv[2:] or list(ARTS)
    check = (ev / "equiv-check.out").read_text()
    indep = {r["relation"]: r for r in json.loads((ev / "equiv-indep.json").read_text())}
    for rel in rels:
        art = ARTS[rel]
        line = next((x for x in check.splitlines() if f"/{rel}.json/" in x), "")
        regen = json.loads((ev / "equiv-regen" / f"instance-equiv-{rel}-4096.json").read_text())
        ind = indep[rel]
        ok_check = f": {rel} reproduces; equal=True;" in line and "check rc=0" in check
        ok_regen = regen["equal"] is True and "regen rc=0" in check
        ok_ind = ind["ok"] is True
        if not (ok_check and ok_regen and ok_ind):
            print(f"{rel} {art[:12]}: NOT labelled (check={ok_check} regen={ok_regen} independent={ok_ind})")
            continue
        detail = (f"{rel} vs frozen {ind['base']} ({ind['target']}), B = 4096: (1) instance_equiv --check re-derives the registered file "
                  f"field for field (except tool), equal=True; (2) regeneration from scratch: equal=True, digests x/W/y = "
                  f"{regen['arrays']['x']['candidate_sha256'][:12]}/{regen['arrays']['W']['candidate_sha256'][:12]}/"
                  f"{regen['arrays']['y']['candidate_sha256'][:12]}; (3) independent: both sides drawn by relchain.instances without a "
                  f"cache, 0 of 4096 VUs differ in a, b, every public accumulator (fold {ind['fold'][1]}) or y_final; my sha256 of x, W, y "
                  f"equal the file's frozen and candidate digests; file.frozen == FROZEN_INSTANCES[target], file.candidate == "
                  f"relchain.instances_ref({rel}, 4096)")
        payload = {"relation": rel, "equiv": art, "check_line": line, "regenerated": regen, "independent": ind}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(payload, f, indent=1)
            pf = f.name
        meta = {"result": "PASS", "verifier": TOOL, "detail": detail, "subject_kind": "instance-equiv/v1", "lane": "verify-night"}
        vid = run("data", "put", "--kind", "verification-verdict/v1", "--meta", json.dumps(meta), "--ref", f"result={art}", "--file", pf,
                  "--preserve").splitlines()[-1].split()[0]
        for key, val in (("verified", "accepted"), ("verifier", TOOL), ("note", detail)):
            run("data", "label", art, key, val, "--by", "verify-night", "--ref", vid)
        print(f"{rel} {art}: verified=accepted by verify-night, verdict {vid}")


if __name__ == "__main__":
    main()
