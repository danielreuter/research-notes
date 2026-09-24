"""Labels for lane fp4-fast's rows (vocabulary keys; --by fp4-fast --ref <run>; NO verified= labels) + the snapshot fp4-fast-v1."""
import json
import re
import subprocess
import sys

BY = "fp4-fast"
WT = "/Users/danielreuter/projects/verity-main-wt/fp4-fast"
EV = "/Users/danielreuter/.research/notes/lanes/fp4-fast/evidence"
# run -> (tree, zk, proof_class, source commit, warm-up sub-batches, role)
STAGES = {
    "r20260923-061128-3edc": ("main 6babe27", True, "COMPLETE_ZK_BACKEND", "6babe273535fdb95d6d0e628659caca61076b37c", 1, "baseline int-ZK at main's operating point l=4096"),
    "r20260923-070527-cfe9": ("main 6babe27", False, "NON_ZK_PROOF_DIAGNOSTIC", "6babe273535fdb95d6d0e628659caca61076b37c", 1, "baseline non-ZK at main's operating point l=4096"),
    "r20260923-071655-984d": ("main 6babe27", True, "COMPLETE_ZK_BACKEND", "6babe273535fdb95d6d0e628659caca61076b37c", 1, "baseline int-ZK at the lane's operating point l=16384 (attribution: isolates the hint generator)"),
    "r20260923-061300-a452": ("lane/fp4-fast 3dfdb21", True, "COMPLETE_ZK_BACKEND", "3dfdb21d39ea700c8cc7c6d639e03e200d0dcc08", 1, "device hints at main's operating point l=4096 (attribution: isolates the operating point)"),
    "r20260923-061823-38a5": ("lane/fp4-fast 3dfdb21", True, "COMPLETE_ZK_BACKEND", "3dfdb21d39ea700c8cc7c6d639e03e200d0dcc08", 1, "operating-point sweep l=8192"),
    "r20260923-061902-1209": ("lane/fp4-fast 3dfdb21", True, "COMPLETE_ZK_BACKEND", "3dfdb21d39ea700c8cc7c6d639e03e200d0dcc08", 1, "operating-point sweep l=16384"),
    "r20260923-072012-01ac": ("lane/fp4-fast a440565", True, "COMPLETE_ZK_BACKEND", "a440565", 1, "HEADLINE int-ZK l=16384 (main's harness: one warm-up sub-batch)"),
    "r20260923-071746-aa14": ("lane/fp4-fast a440565", True, "COMPLETE_ZK_BACKEND", "a440565", 7, "int-ZK l=16384 repeat with --warmup-subs 7 (a full untimed rep): run-to-run spread"),
    "r20260923-071925-be77": ("lane/fp4-fast a440565", False, "NON_ZK_PROOF_DIAGNOSTIC", "a440565", 7, "non-ZK l=16384"),
}
PULL = open("/tmp/fp4fast/pull.log").read()


def run(args):
    r = subprocess.run(["uv", "run", "research", "data", *args], capture_output=True, text=True, cwd=WT)
    out = re.sub(r"(Uninstalled|Installed) 1 package in \d+ms\n", "", r.stdout + r.stderr)
    if r.returncode != 0 or "warn" in out.lower():
        print("!!", args[:3], out.strip()[:300])
    return re.sub(r"(Uninstalled|Installed) 1 package in \d+ms\n", "", r.stdout)


arts = {}
for run_id in STAGES:
    m = re.search(rf"pulled attempt {run_id} from vy-fp4-fast: .*?result=(art:[0-9a-f]+) \(0 blobs\), run_files=(art:[0-9a-f]+) \((\d+) blobs\)", PULL)
    assert m, run_id
    arts[run_id] = {"result": m.group(1), "run_files": m.group(2), "n_files": int(m.group(3))}

rows = []
only = sys.argv[1:] or list(STAGES)
for run_id, (tree, zk, cls, commit, warm, role) in STAGES.items():
    if run_id not in only:
        continue
    r = json.load(open(f"{EV}/{run_id}/result.json"))
    fp, ms = r["workload_fingerprint"], {x["name"]: x["value"] for x in r["measurements"]}
    sec, hw = fp["security"], fp["hardware"]
    overhead = ms["overhead.vs_native_peak"]
    dumps = r["validation"]["evidence"]["dumps"]
    rust = json.load(open(f"{EV}/{run_id}/proofs/rust_batch_rep1.json"))
    split = {k[6:]: round(v, 4) for k, v in ms.items() if k.startswith("split.") and k.endswith("seconds")}
    hints_path = fp["software"]["backend"].get("hints", "?")
    kv = {
        "campaign": "r21-fp4-fast", "candidate": "B-Ligero", "track": "B", "scope": "vu",
        "hardware": f"{hw['gpu']['name']} (RunPod SECURE pod vy-fp4-fast 6jdyrmzdz39tif, reference part, driver {hw['gpu']['driver']}), host {hw['cpu']['model']} x{hw['cpu']['count']}",
        "relation": "fp4-nvf4", "mode": "interactive", "zk": "true" if zk else "false", "proof_class": cls, "authentication": "excluded",
        "B": fp["B"], "K": fp["K"], "l": sec["rs_l"], "n": sec["rs_n"], "subbatches": fp["N_subbatches"], "per_proof_vus": int(ms["split.per_proof_vus"]),
        "soundness": f"target 2^-128; achieved 2^{sec['achieved_log2']:.2f} (union bound over {sec['union_over']} sub-batches, interactive statistical bound)",
        "instances_dataset": fp["instances"]["dataset"], "instances_tier": fp["instances"]["tier"],
        "seconds_per_vu": f"{ms['vu.seconds_per_vu']:.8f}", "overhead": f"{overhead:.4g}", "R_proved": f"{ms['rate.proved_flop_per_second']:.4g}",
        "label": f"{tree}: fp4-nvf4 interactive{' ZK' if zk else ' non-ZK'} on RTX 5090, l={sec['rs_l']} ({fp['N_subbatches']} x {int(ms['split.per_proof_vus'])} VUs): t.total {ms['t.total']:.3f} s per 4096 VUs "
                 f"(hints {split['hints_seconds']:.3f} + witness {split['witness_torch_seconds']:.3f} + tests {split['tests_seconds']:.3f} + encode {split['encode_seconds']:.3f} "
                 f"+ merkle {split['merkle_seconds']:.3f} + openings {split['openings_seconds']:.3f} + zk_masks {split.get('zk_masks_seconds', 0.0):.3f}), {ms['proof_bytes']/1e6:.1f} MB, rep 1 dumps in run-files; {role}",
        "note": f"lane fp4-fast ({role}). hints: {hints_path}. source commit {commit} (= software.backend.commit); "
                f"impl {fp['software']['backend'].get('impl')}; warm-up rep 0 = {warm} untimed sub-batch(es). Host: {hw['cpu']['model']} ({hw['cpu']['count']} threads visible, cgroup quota 12.75 CPUs), "
                f"VRAM {hw['gpu']['memory_total_bytes']/2**30:.1f} GiB, peak device {ms['mem.peak_device_bytes']/2**30:.2f} GiB, exclusive run, pod idle otherwise (host load ~5-10). "
                f"Self-checks on the pod (not independent): runner cold Python verify {dumps['accepted']}/{dumps['total']}; "
                f"Rust ligero-verify batch --target-bits 128 rep1: {rust['accepted']}/{rust['n']} accepted, batch_accepted {rust['batch_accepted']} ({rust['batch_bits']:.2f} bits), python_agree {rust['python_agree']}/{rust['n']}, system pinned {rust['system_pinned']} (fp4-nvf4). "
                f"Bit-exactness lane vs main 6babe27 at l=4096 (seeded coins + mask keys): 10/10 int-ZK + 10/10 non-ZK files identical (evidence/bitexact).",
    }
    for k, v in kv.items():
        run(["label", arts[run_id]["result"], k, str(v), "--by", BY, "--ref", run_id])
    rows.append({"run": run_id, "tree": tree, "zk": zk, "cls": cls, "role": role, "result": arts[run_id]["result"], "run_files": arts[run_id]["run_files"],
                 "n_files": arts[run_id]["n_files"], "t_total": ms["t.total"], "overhead": overhead, "R_proved": ms["rate.proved_flop_per_second"], "split": split,
                 "l": sec["rs_l"], "achieved_log2": sec["achieved_log2"], "proof_mb": ms["proof_bytes"] / 1e6, "peak_gb": ms["mem.peak_device_bytes"] / 1e9,
                 "rust": {k: rust[k] for k in ("n", "accepted", "batch_accepted", "batch_bits", "python_agree")}})
    print("labelled", run_id, arts[run_id]["result"][:20], f"t.total={ms['t.total']:.3f} overhead={overhead:.4g}", flush=True)

if not sys.argv[1:]:
    members = [a for r_ in rows for a in (r_["result"], r_["run_files"])]
    snap = run(["snapshot", "--name", "fp4-fast-v1", "--members", ",".join(members), "--note",
                "lane fp4-fast: fp4-nvf4 on one RTX 5090 (vy-fp4-fast): main 6babe27 int-ZK/non-ZK at l=4096 and int-ZK at l=16384 vs lane/fp4-fast "
                "(device hint generator) int-ZK at l=4096/8192/16384 and the final int-ZK (x2) + non-ZK rows at l=16384; results + run-files (rep 1 dumps each)"])
    print("snapshot:", snap.strip())
    json.dump({"rows": rows, "snapshot": snap.strip()}, open("/tmp/fp4fast/rows_summary.json", "w"), indent=1)
