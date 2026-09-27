#!/usr/bin/env python3
"""red-team-flock-3: labels for flock-backend's 9 total-unit L40S cells and the 2 refused interaction attempts, from
total_cells_check.sh's run log (GEMMCELL and NATCELL lines) and each result's interaction record (views.interaction at the
cells' commit 852816d6).

  label_total_cells.py RUN_STDOUT_LOG [--dry]
"""
import json
import subprocess
import sys

sys.path[:0] = ["/tmp/rtf3-wt-852816d6/backends/numerical/python", "/tmp/rtf3-wt-852816d6/packages/verity/src"]
from verity_numerical.bench import views as V  # noqa: E402

REF = "lanes/coordinator/20260927T0515Z-handoff-from-red-team-flock-3.md"
NAME = {"art:199bccee": ("#39 K1536", "Chunk(3)", "art:4e3f5048 + cross-DC diagnostic art:04688422"),
        "art:c6b96f7e": ("#57/#67 K2048", "Chunk(4)", "art:aea553ae"), "art:c3a3d2c7": ("#60 K4096", "Chunk(8)", "art:86780ca6"),
        "art:3e1bf074": ("#57 K9216", "Chunk(18)", "art:4a319a65"), "art:5bdcd1d1": ("#60 K14336", "Chunk(28)", "art:89dab836"),
        "art:216143fd": ("#101 K2048", "Chunk(4)", "art:73a9e9f3"), "art:3367e633": ("#101 K8192", "Chunk(16)", "art:8bc3dba2"),
        "art:b1e5fed5": ("#57 K2304", "ChunkTail(4)", None), "art:062f4951": ("#39 K8960", "ChunkTail(17)", None)}
#: the retried cells: (refused attempt result, its run)
REFUSED = {"art:199bccee": ("art:706121e5", "r20260927-032848-14a5"), "art:3e1bf074": ("art:62ebb4ff", "r20260927-033831-2860")}


def sh(*a):
    return subprocess.run(["research", *a], capture_output=True, text=True).stdout


def ix_of(art):
    meta = json.loads(next(l.split(None, 1)[1] for l in sh("data", "show", art).splitlines() if l.startswith("meta")))
    ix = V.interaction(meta, interactive=True)
    bw = ix.get("bandwidth_bps") or V.REF_BANDWIDTH_BPS
    model = V.interaction_time(ix, ix["rtt_ms"] / 1e3, bw)
    meas = ix["prover_s"] + ix["wait_s"]
    return {"dev": 100 * (meas - model) / model, "rtt": ix["rtt_ms"], "compute": ix["prover_s"], "wait": ix["wait_s"],
            "ref_vus": meta["workload_fingerprint"]["B"] / V.interaction_time(ix), "B": meta["workload_fingerprint"]["B"]}


def label(art, key, value, dry):
    if dry:
        print(f"  {art} {key} = {value[:300]}{'…' if len(value) > 300 else ''}  ({len(value)} chars)")
        return
    out = subprocess.run(["research", "data", "label", art, key, value, "--by", "red-team-flock-3", "--ref", REF], capture_output=True, text=True)
    print(f"  {art} {key}: rc {out.returncode} {(out.stdout + out.stderr).strip()[:160]}")


def main():
    log, dry = sys.argv[1], "--dry" in sys.argv
    g, n = {}, {}
    for l in open(log):
        tag, _, js = l.rstrip("\n").partition("\t")
        if tag == "GEMMCELL":
            d = json.loads(js); g[d["cell"]] = d
        elif tag == "NATCELL":
            d = json.loads(js); n[d["cell"]] = d
    for art, (name, lay, old) in NAME.items():
        c, p = g[art], n[art]
        assert c["ok"] and p["ok"], art
        ix = ix_of(art)
        hist = f"interaction {ix['dev']:+.1f}% (first attempt)"
        if art in REFUSED:
            ra, rr = REFUSED[art]
            r = ix_of(ra)
            hist = (f"interaction: 2 attempts on this pair. First {rr} ({ra}): {r['dev']:+.1f}% at a {r['rtt']:.3f} ms RTT estimate, refused "
                    f"(±10%), kept. This one: {ix['dev']:+.1f}% at {ix['rtt']:.3f} ms, with compute {r['compute']:.3f} / {ix['compute']:.3f} s and "
                    f"wait {r['wait']:.3f} / {ix['wait']:.3f} s. Published figure (formula at the reference network) {r['ref_vus']:.0f} (B {r['B']}) vs "
                    f"{ix['ref_vus']:.0f} VU/s (B {ix['B']}): the same within {100 * abs(r['ref_vus'] - ix['ref_vus']) / ix['ref_vus']:.1f}%. ACCEPTED WITH "
                    f"THE HISTORY DISCLOSED under red-team-flock-3's IX4. Retry-until-pass is refused as a rule: IX1 keep and link every attempt, "
                    f"IX2 one attempt then exactly two more and the median of three, IX3 fix the check's RTT input")
        elif art == "art:c6b96f7e":
            hist += "; an earlier 02:20Z attempt measured +15% and is not in the store (IX4: register it or name its run)"
        finding = (
            f"red-team-flock-3: GRANTED WITH CONDITIONS, verity/flock-pure-block-total (bf16-ampere-total, pin fef256df, domain total; "
            f"PR #87's 2^14-row slots with UL2; unit = IR tc_dot_total + F2fpBf16 on 10,485,760 adversarial vectors, r20260926-201903-d07c; "
            f"GPU gate r20260927-031817-cf7d). This cell: {name} {lay}, K {c['K']}, B {c['B']} ({c['proofs']} proof(s), 2^{c['achieved_log2']}), "
            f"verifier run {c['verifier_run']}, commit {c['commit']} (= the granted d2292e3b on the pure-block path, + UL2 + the probe fix), "
            f"binary {c['binary']}. TG6: relation, pin and domain recorded; the statement digest my build recomputes equals the one bound "
            f"in every session ({', '.join(c['statement_digests'])}). PB3: my CPU replay (own build of {c['commit']}) accepted "
            f"{c['sessions_accepted']}/{c['sessions_replayed']} recorded sessions; other-session and swapped-rep proofs rejected. PB1 named; "
            f"PB2 union; PB4 require_link, exchange link, one Sigma per sub-batch. The verifier's staged instance files regenerated from the "
            f"registered input set: byte-identical. Contended false. Placement: shared NAT {p['prover']['public_ip']} under PR #91's "
            f"exception, re-checked from the runs' own probes (evidence/nat_check.py). Pod ids agree 3 ways (probe via /proc/1/environ = "
            f"runner = plan: {p['prover']['pod_id']} / {p['verifier']['pod_id']}, U3). Machine ids {p['prover']['machine_id']} / "
            f"{p['verifier']['machine_id']} and boot ids {p['prover']['boot_id'][:8]} / {p['verifier']['boot_id'][:8]} differ. Both bare metal "
            f"(S1): {p['prover']['product_name']} {p['prover']['cpu_model']} vs {p['verifier']['product_name']} {p['verifier']['cpu_model']}, "
            f"no hypervisor flag. DMI uuid unreadable on both (U2). Link {p['link']['peer']} at {p['link']['peer_ip']} from "
            f"{p['link']['source_ip']} (S3). RTT 30/30 connects, median {p['rtt']['median_ms']:.3f} ms (R1, S4). assess() re-run: no problem. "
            f"{'Supersedes ' + old + '.' if old else 'No earlier cell.'} {hist}.")
        print(f"== {art} {name}: {len(finding)} chars")
        label(art, "proof_class", "NON_ZK_PROOF", dry)
        label(art, "verified", "accepted", dry)
        label(art, "verifier", f"flock-pure-gpu replay (CPU, red-team-flock-3 build of {c['commit']}), every recorded session", dry)
        label(art, "finding", finding, dry)
    for cell, (ra, rr) in REFUSED.items():
        r, x = ix_of(ra), ix_of(cell)
        why = (f"the retry passed with the same compute ({r['compute']:.3f} / {x['compute']:.3f} s) and wait ({r['wait']:.3f} / {x['wait']:.3f} s) "
               f"at a higher RTT estimate ({x['rtt']:.3f} ms)" if r["B"] == x["B"] else
               f"the retry chose a different plateau (B {x['B']} against {r['B']}) and passed at {x['dev']:+.1f}%")
        f = (f"red-team-flock-3: a refused interaction attempt of cell {cell} ({NAME[cell][0]}), run {rr}, on the cell's own pair: "
             f"{r['dev']:+.1f}% from the model at a {r['rtt']:.3f} ms RTT estimate (±10%). Kept and linked (IX1). Its published figure at the "
             f"reference network is {r['ref_vus']:.0f} VU/s (B {r['B']}), the cell's {x['ref_vus']:.0f}; {why}. No proof_class is claimed for "
             f"this attempt (it was not replayed).")
        print(f"== {ra} (refused attempt of {cell})")
        label(ra, "finding", f, dry)


if __name__ == "__main__":
    main()
