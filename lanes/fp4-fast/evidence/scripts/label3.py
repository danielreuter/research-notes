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
    # run -> (tree, zk, proof_class, source commit, warm-up sub-batches, role)
    "r20260923-092817-6220": ("integration 0d33ee7", True, "COMPLETE_ZK_BACKEND", "0d33ee7", 7, "throwaway integration tree 0d33ee7 = main 9d35c4e (hp2-host commit graph 820dc9d + tests graph 0d8e178) + lane fp4-fast 69a3b04 (bc671b0 pipelined fp4 runner + median-rep bucket accounting) + 6babe27 encode_simt.py; sequential"),
    "r20260923-093153-c519": ("integration 0d33ee7", True, "COMPLETE_ZK_BACKEND", "0d33ee7", 7, "throwaway integration tree 0d33ee7 (main 9d35c4e + lane 69a3b04 + 6babe27 encoder); --pipeline 3; rep 1 = 0.238 s outlier (tail sub-batch graph captures, fixed by 07c3039), median rep reported"),
    "r20260923-093243-5079": ("integration 0d33ee7", True, "COMPLETE_ZK_BACKEND", "0d33ee7", 7, "throwaway integration tree 0d33ee7 (main 9d35c4e + lane 69a3b04 + 6babe27 encoder); --pipeline 4; rep 1 = 0.291 s outlier (tail sub-batch graph captures, fixed by 07c3039), median rep reported"),
    "r20260923-093332-a522": ("integration 0d33ee7", False, "NON_ZK_PROOF_DIAGNOSTIC", "0d33ee7", 7, "throwaway integration tree 0d33ee7 (main 9d35c4e + lane 69a3b04 + 6babe27 encoder); non-ZK --pipeline 3; rep 1 = 0.216 s outlier (tail sub-batch graph captures, fixed by 07c3039), median rep reported"),
    "r20260923-093520-244b": ("integration 7c3b157", True, "COMPLETE_ZK_BACKEND", "7c3b157", 7, "HEADLINE: throwaway integration tree 7c3b157 = main 9d35c4e + lane fp4-fast 07c3039 (bc671b0 pipelined fp4 runner, median-rep buckets, full pipelined warm-up pass) + 6babe27 encode_simt.py; --pipeline 3"),
    "r20260923-093832-4eab": ("integration 7c3b157", True, "COMPLETE_ZK_BACKEND", "7c3b157", 7, "throwaway integration tree 7c3b157 (main 9d35c4e + lane 07c3039 + 6babe27 encoder); --pipeline 4"),
    "r20260923-093904-5bbd": ("integration 7c3b157", False, "NON_ZK_PROOF_DIAGNOSTIC", "7c3b157", 7, "throwaway integration tree 7c3b157 (main 9d35c4e + lane 07c3039 + 6babe27 encoder); non-ZK --pipeline 3"),
    "r20260923-093936-0e3e": ("integration 7c3b157", True, "COMPLETE_ZK_BACKEND", "7c3b157", 7, "throwaway integration tree 7c3b157 (main 9d35c4e + lane 07c3039 + 6babe27 encoder); --pipeline 5"),
    "r20260923-094026-27ab": ("integration 7c3b157", True, "COMPLETE_ZK_BACKEND", "7c3b157", 13, "throwaway integration tree 7c3b157 (main 9d35c4e + lane 07c3039 + 6babe27 encoder); l=8192 (13 x 341 VUs) --pipeline 4"),
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
    r = subprocess.run(["uv", "run", "research", "data", "show", run_id, "--json"], capture_output=True, text=True, cwd=WT)
    outs = json.loads(re.sub(r"(Uninstalled|Installed) 1 package in \d+ms\n", "", r.stdout))["outputs"]
    arts[run_id] = {"result": outs["result"], "run_files": outs["run_files"], "n_files": 0}

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
        "note": f"lane fp4-fast ({role}). hints: {hints_path}. source commit {commit} (= software.backend.commit; integration trees are throwaway detached commits, not branches: reproduce = main at the stated sha + lane/fp4-fast bc671b0 fp4/chain.py, fp4/hints_device.py, run.py --warmup-subs, + 6babe27 encode_simt.py); pipeline depth {fp['software']['backend'].get('pipeline', 0)}; "
                f"impl {fp['software']['backend'].get('impl')}; warm-up rep 0 = {warm} untimed sub-batch(es) (+ one pipelined pass: every slot once before 07c3039, the full pass since). Host: {hw['cpu']['model']} ({hw['cpu']['count']} threads visible, cgroup quota 12.75 CPUs), "
                f"VRAM {hw['gpu']['memory_total_bytes']/2**30:.1f} GiB, peak device {ms['mem.peak_device_bytes']/2**30:.2f} GiB, exclusive run, pod idle otherwise (host load ~5-10). "
                f"Self-checks on the pod (not independent): runner cold Python verify {dumps['accepted']}/{dumps['total']}; "
                f"Rust ligero-verify batch --target-bits 128 rep1: {rust['accepted']}/{rust['n']} accepted, batch_accepted {rust['batch_accepted']} ({rust['batch_bits']:.2f} bits), python_agree {rust['python_agree']}/{rust['n']}, system pinned {rust['system_pinned']} (fp4-nvf4). "
                f"Bit-exactness at l=4096 (seeded coins + mask keys, 6 sub-batches): main 6babe27 == lane a440565 == integration 1986953 sequential == integration 1986953 --pipeline 3, 19/19 files int-ZK and 19/19 non-ZK (evidence/bitexact2).",
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
    snap = run(["snapshot", "--name", "fp4-fast-v3", "--members", ",".join(members), "--note",
                "lane fp4-fast round 3 (final rows): fp4-nvf4 on one RTX 5090 (vy-fp4-fast), throwaway integration tree = main 9d35c4e + lane/fp4-fast 69a3b04/07c3039 (pipelined fp4 runner, median-rep contract buckets, full pipelined warm-up) + 6babe27 encode_simt.py "
                "(main's 429f8ea kernel exceeds the 5090's 99 KB shared memory at l=16384): l=16384, sequential, --pipeline 3/4/5, non-ZK, l=8192 --pipeline 4; results + run-files (rep 1 dumps, Rust batch verdicts). Rounds 1/2 = fp4-fast-v1 art:73db01f7, fp4-fast-v2 art:91546081"])
    print("snapshot:", snap.strip())
    json.dump({"rows": rows, "snapshot": snap.strip()}, open("/tmp/fp4fast/rows_summary3.json", "w"), indent=1)
