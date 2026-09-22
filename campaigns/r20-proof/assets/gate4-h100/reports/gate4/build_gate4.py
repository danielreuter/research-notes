"""Assemble ``backends/numerical/reports/GATE4_H100.json`` from this lane's raw results (the gate-4 table, one row per
(design, checker variant, mode)).  Every H100 number is a recorded ``research run`` on ``vy-g4``; the SP1 and C rows are
cited with their own hardware and run ids.  The Markdown report is written by hand next to it.

    uv run --package verity-numerical python backends/numerical/reports/gate4/build_gate4.py
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
NATIVE = 9.846153846153846e-12  # s per K=1536 VU at the A100 dense BF16 peak (contract.NATIVE_REFERENCE)
B = 4096
H100 = "NVIDIA H100 80GB HBM3 (vy-g4)"


def overhead(seconds_per_vu: float) -> float:
    return seconds_per_vu / NATIVE


def row(**kw) -> dict:
    base = {"design": None, "checker_variant": None, "mode": None, "hardware": H100, "scope": None, "B": B, "N_subbatches": 1,
            "prover_s_per_batch": None, "us_per_vu": None, "overhead_vs_native_peak": None, "verifier_s": None,
            "proof_or_transcript_MB": None, "sequential_depth": None, "security": None, "proof_class": None,
            "statement_bound": None, "measured_fraction": None, "run_id": None, "note": ""}
    base.update(kw)
    if base["prover_s_per_batch"] is not None and base["us_per_vu"] is None:
        base["us_per_vu"] = base["prover_s_per_batch"] / base["B"] * 1e6
    if base["us_per_vu"] is not None and base["overhead_vs_native_peak"] is None:
        base["overhead_vs_native_peak"] = overhead(base["us_per_vu"] * 1e-6)
    for k in ("us_per_vu", "overhead_vs_native_peak", "prover_s_per_batch"):
        if isinstance(base[k], float):
            base[k] = float(f"{base[k]:.4g}")
    return base


def kernel_column() -> dict:
    """Section (b): the shared kernel families re-measured on the H100 (run r20260922-093941-aebe),
    next to the 4090 numbers the lanes recorded and the anchor lane's A100 column (anchor_a100.md)."""
    kc = HERE / "kernel_column"
    mb = json.loads((kc / "microbench.json").read_text())
    hashes = {h["hash"]: h for h in json.loads((kc / "hash.json").read_text())["ligero"]}
    enc = {(e["encoder"], e["shape"]): e for e in json.loads((kc / "encode.json").read_text())["encoders"]}
    fused = json.loads((kc / "fused_bench.json").read_text())
    r21 = {k["impl"]: k for k in fused["kernels"] if k["n"] == 2097152 and k["mode"] == "fold+eval"}
    lg = json.loads((kc / "fused_logup.json").read_text())
    lg_rows = lg if isinstance(lg, list) else next(v for v in lg.values() if isinstance(v, list))
    lg21 = min((r for r in lg_rows if r.get("n") == 2097152), key=lambda r: r["fold_eval_us"])
    copy_gbps = mb["bandwidth"]["copy"]["gb_per_s"]
    # (name, 4090 recorded, A100 measured [anchor], H100 measured here, unit, bound)
    fam = [
        ("HBM copy 1 GiB (read+write)", None, 1754, copy_gbps, "GB/s", "datasheet 3,350 (H100) / 2,039 (A100) / 1,008 (4090; no 4090 microbench recorded)"),
        ("cuBLAS `_int_mm` 8192^3", 6.6, 14.5, mb["int8"]["8192x8192x8192"]["seconds"] * 1e3, "ms", "INT8 tensor: 660 / 312 / 1,979 dense TOPS"),
        ("BF16 matmul 8192^3", None, 3.77, mb["bf16"]["8192^3"]["seconds"] * 1e3, "ms", "BF16 tensor"),
        ("hash_gpu SHA-256 Merkle tree, B (20.4 GB)", 446, 190, hashes["sha256"]["tree_bytes_per_s"] / 1e9, "GB/s", "INT32 SIMT"),
        ("hash_gpu SHA-256 chunked, B", None, None, hashes["sha256-chunked"]["tree_bytes_per_s"] / 1e9, "GB/s", "INT32 SIMT"),
        ("hash_gpu Blake3 Merkle tree, B", 359, 377, hashes["blake3"]["tree_bytes_per_s"] / 1e9, "GB/s", "INT32 SIMT"),
        ("hash_gpu Poseidon2-16 (cuda), B", 57.7, 26.1, hashes["poseidon2-16"]["tree_bytes_per_s"] / 1e9, "GB/s", "INT32 SIMT (Montgomery)"),
        ("encode SIMT NTT v2 t1024, B batch", 32.7, 57.4, enc[("ntt_simt_v2_t1024", "B")]["ms_median"], "ms", "INT32 SIMT + HBM"),
        ("encode Triton INT8 matrix DFT, B", 171.7, 607.1, enc[("matdft_int8_triton", "B")]["ms_median"], "ms", "INT8 tensor (Triton)"),
        ("fused checker round SIMT 2^21 ext", 273, 474, r21["simt"]["seconds"] * 1e6, "us", "INT32 SIMT / HBM"),
        ("fused checker round TC 2^21 ext", 506, 1569, r21["tc"]["seconds"] * 1e6, "us", "INT8 tensor (Triton)"),
        ("fused 130-round layer model SIMT graphed", 6.2, 12.3, fused["layers"]["simt"]["graphed_seconds"] * 1e3, "ms", "INT32 SIMT, launch-bound tail"),
        ("fused logUp round 2^21 (best block)", 600, 1469, lg21["fold_eval_us"], "us", "INT32 SIMT"),
        ("packed sumcheck 2^26 k=0 (anchor: H100 recorded)", None, 50.2, 30.9, "ms", "HBM-bound"),
        ("Montgomery packed sumcheck 2^26 k=3 (anchor: H100 recorded)", None, 11.5, 6.0, "ms", "HBM-bound"),
    ]
    rows = []
    for name, r4090, a100, h100, unit, bound in fam:
        faster = unit in ("GB/s",)
        def ratio(x):
            if x is None or h100 is None:
                return None
            return round(h100 / x, 2) if faster else round(x / h100, 2)
        rows.append({"kernel": name, "rtx4090": r4090, "a100": a100, "h100": round(h100, 1) if h100 else None, "unit": unit,
                     "h100_speed_vs_4090": ratio(r4090), "h100_speed_vs_a100": ratio(a100), "bound": bound})
    return {"run_id": "r20260922-093941-aebe", "note": "speed ratios > 1 = H100 faster; bandwidth ratio H100/4090 = 3.32, H100/A100 = 1.64; INT32 issue-rate ratio H100/4090 ~ 0.81 (132 SMs x 64 INT32 x 1.98 GHz vs 128 x 64 x 2.52), H100/A100 ~ 1.7. microbench and fused benches used the 4090/A100 peak tables (no H100 table): their printed 'fraction of floor' columns are NOT used here.",
            "h100_measured_peaks": mb["measured_peaks"], "rows": rows}


def main() -> None:
    rows: list[dict] = []

    # A end-to-end (main 38757ed = a-gpu v2e), warm 5-rep run
    a = json.load(open(HERE / "a_gpu_e2e_main_r20260922-091718-45c3.json"))["runs"]
    a_cold = json.load(open(HERE / "a_gpu_e2e_main_r20260922-090931-b5be.json"))["runs"]
    med = statistics.median(r["prover_s"] for r in a)
    rows.append(row(design="A", checker_variant="v1 (WP2 checker contracts)", mode="end-to-end, non-ZK (a-gpu v2e, main 38757ed)",
                    scope="end-to-end proof, verified", prover_s_per_batch=med,
                    verifier_s=float(f"{statistics.median(r['verifier_s'] for r in a):.3g}"),
                    proof_or_transcript_MB=round(a[0]["proof_bytes"] / 1e6, 1), sequential_depth=a[0]["sequential_depth"],
                    security="2^-127.7 (accounting; SHA-256 collision term)", proof_class="NON_ZK_PROOF_DIAGNOSTIC", statement_bound="yes (F11: circuit hashes, B, root, public words absorbed before any challenge)",
                    measured_fraction=1.0, run_id="r20260922-091718-45c3",
                    note=f"median of 5 warm reps {[round(r['prover_s'], 2) for r in a]} (spread = host-side t_open {[round(r['t_open'], 2) for r in a]}); cold run r20260922-090931-b5be: {[round(r['prover_s'], 2) for r in a_cold]} (rep 0 = Triton compile); a-gpu's own record 4.43 s (r20260922-074455-d0b6). 4096/4096 accepted; peak device 46.7 GB; 1920 transcript slots; verifier is Python."))
    rows.append(row(design="A", checker_variant="v1", mode="end-to-end, non-ZK (a-gpu2 head f87b096 and merge 179d509)", scope="end-to-end proof: FAILED",
                    prover_s_per_batch=None, security="--", proof_class="NO_PROOF", statement_bound="n.a.", measured_fraction=0.0,
                    run_id="r20260922-091947-822f, r20260922-092252-3ebd",
                    note="both heads raise `logup_packed: LogUp: fractional sum is not zero (a query is not in its table)` at B=4096 (the lane validated at 64 VUs); not fixed here."))

    # A buckets (a-fusion kernels re-run) -> reprice_v2 output
    rp = json.load(open(HERE / "a_buckets/a_kernels_h100_gate4.json"))
    rows.append(row(design="A", checker_variant="v1 (WP2 checker contracts)", mode="measured buckets: fused sumcheck + level-graphed logUp; rest modelled",
                    scope="measured buckets (kernels on random tables)", prover_s_per_batch=0.285, overhead_vs_native_peak=7.07e6,
                    sequential_depth="438 (a-gpu proof; kernels use transcript-independent coins)", security="2^-128 target (BabyBear^6)",
                    proof_class="ARITHMETIC_DIAGNOSTIC", statement_bound="n.a.", measured_fraction=round(1 - 0.086 / 0.285, 2), run_id="r20260922-092450-5b79",
                    note="sumcheck v1 batch 100.5 ms (2^28 k=3 layer 12.6 ms), logUp v1 88.3 ms device / 91.1 wall (per-round Fiat-Shamir graphs 112.6 -> 7.72e6); encoding/row-combination/hash/hints/PRG modelled at 0.172 (86 ms). a-fusion recorded 7.06e6 on the same card."))
    rows.append(row(design="A", checker_variant="v2 (checker-min gadgets)", mode="measured buckets: fused sumcheck + 10-stream logUp; rest modelled",
                    scope="measured buckets (kernels on random tables)", prover_s_per_batch=0.184, overhead_vs_native_peak=4.55e6,
                    sequential_depth="n.a. (no v2 proof exists)", security="2^-128 target (BabyBear^6)", proof_class="ARITHMETIC_DIAGNOSTIC", statement_bound="n.a.",
                    measured_fraction=round(1 - 0.058 / 0.184, 2), run_id="r20260922-092450-5b79",
                    note="sumcheck v2 census shape 36.4 ms; logUp ten tables on ten streams 81.2 ms (+ 11th table pro rata = 89 ms; sequential level graphs 212.6 -> 8.08e6); modelled 58 ms. a-fusion recorded 4.64e6."))

    # B end-to-end (b-ligero2)
    for f, mode, cls, omitted in (("result_vu4096_b16384.json", "end-to-end, non-ZK (b-ligero2)", "NON_ZK_PROOF_DIAGNOSTIC", "ZK masking"),
                                  ("result_vu4096_zk_b16384.json", "end-to-end, HVZK (b-ligero2 --zk)", "COMPLETE_HVZK_BACKEND", "malicious-verifier coin commitment (HM96)")):
        d = json.load(open(HERE / "b_e2e" / f))
        m = {x["name"]: x["value"] for x in d["measurements"]}
        sec = d["workload_fingerprint"]["security"]
        split = {k.replace("split.", "").replace("_seconds", ""): round(v, 3) for k, v in m.items() if k.startswith("split.") and k.endswith("seconds")}
        rows.append(row(design="B", checker_variant="v1 (WP2 checker; bits + one-hot selectors, no lookups)", mode=mode, scope="end-to-end proof, verified (every rep)",
                        N_subbatches=int(m["split.subbatches"]), prover_s_per_batch=m["t.total"], verifier_s=round(m["verifier.seconds"], 3),
                        proof_or_transcript_MB=round(m["transcript.bytes"] / 1e6, 1), sequential_depth=int(m["rounds.sequential_depth"]),
                        security=f"2^{sec['achieved_log2']:.2f} union over {sec['union_over']} sub-batches (per proof 2^{sec['per_proof_total_log2']:.1f}, t={sec['opened_columns']})",
                        proof_class=cls, statement_bound="yes (statement_digest in both challenges)", measured_fraction=1.0, run_id=d["run_id"],
                        note=f"25 x 170 VUs, l={sec['rs_l']}, k={sec['rs_k']}, n={sec['rs_n']}; split s: {split}; peak device {m['mem.peak_device_bytes'] / 1e9:.1f} GB; hash + SHAKE expander are host placeholders; omitted: {omitted}, external authentication. L40S record 5.63 / 6.43 s (r20260922-082245-c96b)."))

    # B buckets
    bb = json.load(open(HERE / "b_buckets/b_measured_h100_gate4.json"))
    for r, cv in zip(bb["rows"], ("v1 (WP2 checker; 310,602 Ligero rows)", "v2 (checker-min; 104,217 rows, helper_rows table side)")):
        rows.append(row(design="B", checker_variant=cv, mode="measured buckets (b-commit / b-lintest / b-v2 kernels)", scope="measured buckets (resident pseudo-random data)",
                        prover_s_per_batch=r["total_ms"] / 1e3, overhead_vs_native_peak=r["overhead"], sequential_depth=2, security="2^-128 target (BabyBear^6, t=192)",
                        proof_class="ARITHMETIC_DIAGNOSTIC", statement_bound="n.a.", measured_fraction=r["measured_fraction"], run_id=r["run_id"],
                        note=f"buckets ms: {r['measured_ms']}; modelled {r['modelled_ms']} ms. " + r["note"]))

    # cited
    rows.append(row(design="SP1 (candidate 0)", checker_variant="Rust guest (statement parsing + opening table + relation + auth hashing)", mode="sound authenticated core proof, 1 VU per proof",
                    hardware="RTX 4090 (vy-sp1), SP1 6.4.0 cuda prover -- CITED", scope="cited end-to-end proof", B=1, N_subbatches=1, prover_s_per_batch=3.580119322,
                    verifier_s=0.245, proof_or_transcript_MB=5.9, sequential_depth="n.a. (non-interactive STARK)", security="SP1 core (~100 bits, STARK params)",
                    proof_class="NON_ZK_PROOF (authentication included)", statement_bound="yes", measured_fraction=1.0, run_id="r20260921-220722-019b",
                    note="benchmarks/dot_product/baselines.json; 10.1M cycles, 4 shards; 82% of the guest is statement parsing + opening-table construction; not rebuilt on the H100 (hours)."))
    rows.append(row(design="SP1 (candidate 0)", checker_variant="relation-only guest (statement, table, authentication removed)", mode="relation-only diagnostic, 1 VU",
                    hardware="RTX 4090 (vy-sp1), SP1 cuda core mode -- CITED", scope="cited diagnostic", B=1, prover_s_per_batch=0.868055971, security="SP1 core",
                    proof_class="ARITHMETIC_DIAGNOSTIC (INCOMPLETE_CHECKER: relation only)", statement_bound="no", measured_fraction=1.0, run_id="r20260922-050349-3373",
                    note="406,671 cycles, 2 shards; the arithmetic floor of the SP1 route."))
    rows.append(row(design="C (QuickSilver VOLE-ZK)", checker_variant="one relation, dietmc F61p", mode="designated-verifier ZK, 4096 VUs one batch",
                    hardware="AMD EPYC 9655P (vy-cpu), 1 thread -- CITED, CPU", scope="cited end-to-end (designated verifier)", B=4096, N_subbatches=1,
                    prover_s_per_batch=0.40835 * 4096, security="2^-30.1 (F61p r=1: sensitivity point, NOT 2^-128)", proof_class="COMPLETE_ZK_BACKEND (designated-verifier; LPN + OT assumptions)",
                    statement_bound="n.a. (Verity external binding omitted)", measured_fraction=1.0, run_id="r20260922-053613-d110",
                    note="0.408 s/VU; communication 8.58 MB/VU; the 2^-128-class run (F384p, 8 VUs) is 4.74 s/VU = 4.81e11 (r20260922-061644-5d62)."))
    rows.append(row(design="C (QuickSilver VOLE-ZK)", checker_variant="one relation, dietmc F384p", mode="designated-verifier ZK, 8 VUs",
                    hardware="AMD EPYC 9655P (vy-cpu), 1 thread -- CITED, CPU", scope="cited end-to-end (designated verifier)", B=8, N_subbatches=1,
                    prover_s_per_batch=4.736 * 8, security="2^-128 (computational cap of AES-128/KOS/LPN; statistical 2^-359)", proof_class="COMPLETE_ZK_BACKEND (designated-verifier)",
                    statement_bound="n.a.", measured_fraction=1.0, run_id="r20260922-061644-5d62", note="4.74 s/VU; 54.4 MB/VU P->V."))

    out = {"schema": "gate4/v1", "lane": "gate4-h100", "generated_from": "backends/numerical/reports/gate4/", "native_seconds_per_vu": NATIVE,
           "hardware": {"gpu": "NVIDIA H100 80GB HBM3 SXM (vy-g4)", "driver": "580.126.20", "torch": "2.6.0+cu124", "triton": "3.2", "cupy": "14.2.0"},
           "runs": {"a_e2e_cold": "r20260922-090931-b5be", "a_e2e_warm": "r20260922-091718-45c3", "a_gpu2_head": "r20260922-091947-822f", "a_gpu2_179d509": "r20260922-092252-3ebd",
                    "a_buckets": "r20260922-092450-5b79", "b_e2e": "r20260922-092841-94ac", "b_buckets": "r20260922-093147-3d6c", "h100_kernel_column": "r20260922-093941-aebe"},
           "rows": rows, "reprice_a": rp.get("designs", rp) if isinstance(rp, dict) else rp, "b_buckets": bb,
           "kernel_column": kernel_column()}
    (HERE.parent / "GATE4_H100.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    for r in rows:
        print(f"{r['design']:<24} {r['mode'][:48]:<48} {str(r['prover_s_per_batch']):>8} s  {str(r['us_per_vu']):>8} us/VU  {r['overhead_vs_native_peak']}")


if __name__ == "__main__":
    main()
