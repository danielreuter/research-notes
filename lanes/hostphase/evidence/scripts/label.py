"""Labels for lane hostphase's rows (vocabulary keys only; --by hostphase --ref <run>; NO verified= labels) + the snapshot."""
import json
import re
import subprocess

BY = "hostphase"
PULL = open("/tmp/hostphase/pull.log").read()
STAGES = {
    "r20260923-030235-4817": ("baseline main 5a8a744", "bf16-hopper", "interactive", True, "COMPLETE_ZK_BACKEND", "5a8a7444f1722abe274aac5c92b073923d1e1903"),
    "r20260923-031611-55f1": ("lane/hostphase d8f896c", "bf16-hopper", "interactive", True, "COMPLETE_ZK_BACKEND", "d8f896cca0788c3df245fb478513db2412d193c4"),
    "r20260923-031657-a769": ("lane/hostphase d8f896c", "bf16-hopper", "fiat-shamir", True, "COMPLETE_HVZK_BACKEND", "d8f896cca0788c3df245fb478513db2412d193c4"),
    "r20260923-031744-b10b": ("lane/hostphase d8f896c", "bf16-hopper", "interactive", False, "NON_ZK_PROOF_DIAGNOSTIC", "d8f896cca0788c3df245fb478513db2412d193c4"),
    "r20260923-031830-65d9": ("lane/hostphase d8f896c", "fp8-hopper", "interactive", True, "COMPLETE_ZK_BACKEND", "d8f896cca0788c3df245fb478513db2412d193c4"),
    "r20260923-031855-bef9": ("lane/hostphase d8f896c", "fp8-hopper", "fiat-shamir", True, "COMPLETE_HVZK_BACKEND", "d8f896cca0788c3df245fb478513db2412d193c4"),
    "r20260923-031920-d2ae": ("lane/hostphase d8f896c", "fp8-hopper", "interactive", False, "NON_ZK_PROOF_DIAGNOSTIC", "d8f896cca0788c3df245fb478513db2412d193c4"),
}
TARGET = {"bf16-hopper": "bf16-hopper-mma-draft/2026-09-22", "fp8-hopper": "fp8-hopper-wgmma-draft/2026-09-22"}


def run(args):
    r = subprocess.run(["uv", "run", "research", "data", *args], capture_output=True, text=True,
                       cwd="/Users/danielreuter/projects/verity-main-wt/hostphase")
    out = re.sub(r"(Uninstalled|Installed) 1 package in \d+ms\n", "", r.stdout + r.stderr)
    if r.returncode != 0 or "warn" in out.lower():
        print("!!", args[:3], out.strip()[:300])
    return re.sub(r"(Uninstalled|Installed) 1 package in \d+ms\n", "", r.stdout)


arts = {}
for run_id in STAGES:
    m = re.search(rf"pulled attempt {run_id} from vy-hostphase: .*?result=(art:[0-9a-f]+) \(0 blobs\), run_files=(art:[0-9a-f]+) \((\d+) blobs\)", PULL)
    arts[run_id] = {"result": m.group(1), "run_files": m.group(2), "n_files": int(m.group(3))}

rows = []
for run_id, (tree, rel, mode, zk, cls, commit) in STAGES.items():
    r = json.load(open(f"/tmp/hostphase/results/{run_id}.json"))
    fp, ms = r["workload_fingerprint"], {x["name"]: x["value"] for x in r["measurements"]}
    sec, hw = fp["security"], fp["hardware"]
    overhead = ms["rate.native_peak_flop_per_second"] / ms["rate.proved_flop_per_second"]
    dumps = r["validation"]["evidence"]["dumps"]
    rust = json.load(open(f"/Users/danielreuter/.research/notes/lanes/hostphase/evidence/{run_id}/rust_batch_rep1.json"))
    split = {k[6:]: round(v, 4) for k, v in ms.items() if k.startswith("split.") and k.endswith("seconds")}
    kv = {
        "campaign": "r21-hostphase", "candidate": "B-Ligero", "track": "B", "scope": "vu",
        "hardware": f"{hw['gpu']['name']} (SXM, RunPod SECURE pod vy-hostphase ms2c0dq167fl0f, driver {hw['gpu']['driver']}), host {hw['cpu']['model']} x{hw['cpu']['count']}",
        "relation": rel, "mode": mode, "zk": "true" if zk else "false", "proof_class": cls, "authentication": "excluded",
        "B": fp["B"], "K": fp["K"],
        "soundness": f"target 2^-128; achieved 2^{sec['achieved_log2']:.2f} (union bound over {sec['union_over']} sub-batches, "
                     f"{'Fiat-Shamir q x eps accounting' if mode == 'fiat-shamir' else 'interactive statistical bound'})",
        "instances_dataset": fp["instances"]["dataset"], "instances_tier": fp["instances"]["tier"],
        "seconds_per_vu": f"{ms['vu.seconds_per_vu']:.8f}", "overhead": f"{overhead:.4g}",
        "label": f"{tree}: {rel} {mode}{' ZK' if zk else ' non-ZK'} on H100 SXM: t.total {ms['t.total']:.3f} s per 4096 VUs "
                 f"(witness {split['witness_torch_seconds']:.3f} + hints {split['hints_seconds']:.3f} + tests {split['tests_seconds']:.3f} + encode {split['encode_seconds']:.3f} "
                 f"+ merkle {split['merkle_seconds']:.3f} + openings {split['openings_seconds']:.3f}), {ms['proof_bytes']/1e6:.1f} MB, one rep's dumps in run-files",
        "note": f"lane hostphase (host-bound phases moved to the device; protocol/format/Rust unchanged). source commit {commit} (the result's software.backend.commit is null: "
                f"the shipped tree is a git archive); prover impl {fp['software']['backend'].get('impl') or 'legacy (main)'}. Host: {hw['cpu']['model']} ({hw['cpu']['count']} threads), "
                f"VRAM {hw['gpu']['memory_total_bytes']/2**30:.1f} GiB, peak device {ms['mem.peak_device_bytes']/2**30:.2f} GiB, pod load ~3-5 (208-thread host, exclusive run). "
                f"Self-checks on the pod (not independent): runner cold Python verify {dumps['accepted']}/{dumps['total']}; serialize verify-batch --target-bits 128 ACCEPT; "
                f"Rust ligero-verify batch --target-bits 128 rep1: {rust['accepted']}/{rust['n']} accepted, batch_accepted {rust['batch_accepted']}, python_agree {rust['python_agree']}/{rust['n']}, system pinned {rust['system_pinned']}. "
                f"Bit-exactness vs main 5a8a744 (same coins/mask keys): 64/64 files identical over 7 mode pairs (run r20260923-031046-9e90).",
    }
    for k, v in kv.items():
        run(["label", arts[run_id]["result"], k, str(v), "--by", BY, "--ref", run_id])
    rows.append({"run": run_id, "tree": tree, "rel": rel, "mode": mode, "zk": zk, "cls": cls, "result": arts[run_id]["result"],
                 "run_files": arts[run_id]["run_files"], "n_files": arts[run_id]["n_files"], "t_total": ms["t.total"], "overhead": overhead,
                 "R_proved": ms["rate.proved_flop_per_second"], "split": split, "achieved_log2": sec["achieved_log2"], "proof_mb": ms["proof_bytes"] / 1e6,
                 "verify_wall": ms["verify_wall"], "t": {k[2:]: round(v, 4) for k, v in ms.items() if k.startswith("t.")}})
    print("labelled", run_id, arts[run_id]["result"][:20], f"t.total={ms['t.total']:.3f} overhead={overhead:.4g}")

members = [a for r_ in rows for a in (r_["result"], r_["run_files"])]
snap = run(["snapshot", "--name", "hostphase-v1", "--members", ",".join(members), "--note",
            "lane hostphase: baseline main 5a8a744 bf16-hopper int-ZK + lane/hostphase d8f896c bf16-hopper {int-ZK, FS-ZK, int non-ZK} and fp8-hopper "
            "{int-ZK, FS-ZK, int non-ZK} on H100 80GB HBM3 (vy-hostphase); results + run-files (one rep's dumps each)"])
print("snapshot:", snap.strip())
json.dump({"rows": rows, "snapshot": snap.strip()}, open("/tmp/hostphase/rows_summary.json", "w"), indent=1)
