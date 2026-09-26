import json, os, sys
H = os.path.expanduser("~/.research/runs/")
PEAK, HBM = 362.05e12, 864e9  # L40S BF16 dense tensor peak, HBM bandwidth (datasheet)
runs = dict(line.split() for line in open("/tmp/cover_runs.txt") if line.strip())  # label run
# per-instance native seconds (Table 2 convention for GEMM; bytes moved at HBM bandwidth otherwise)
native = {"gemm2048": 2 * 2048 / PEAK, "gemm8192": 2 * 8192 / PEAK, "fused": 5 * 2048 * 2 / HBM, "triton": 3 * 2048 * 2 / HBM,
          "rope": 3 * 64 * 2 / HBM, "silu": (16384 + 8192) * 2 / HBM}
# alternative basis: every template memory-bound (a GEMM coordinate reads its K-word bf16 weight row; batch-1 decode)
native_mem = dict(native, gemm2048=2 * 2048 / HBM, gemm8192=2 * 8192 / HBM)
unit = {"gemm2048": "coords", "gemm8192": "coords", "fused": "rows", "triton": "rows", "rope": "heads", "silu": "rows"}
# the protocol's draw on #101 (replay_partition.sample: 1,374 VUs), in instances of each template
drawn_vus = {"gemm2048": 391, "gemm8192": 128, "fused": 256, "triton": 8, "rope": 256, "silu": 128}
drawn_inst = {"gemm2048": 7 * 128256 + 128 * (16384 + 2048 + 3072), "gemm8192": 128 * 2048, "fused": 256, "triton": 8,
              "rope": 128 * 32 + 128 * 8, "silu": 128}
# excluded from the cover: native estimates (attention: 32 heads per VU, K/V bytes 256*T + 256 per head, T by key-block count)
att = (48 * 64 + 48 * 192 + 96 * 272) * 32 * 256 / HBM + 192 * 32 * 256 / HBM
excluded = {"Attention_v3 (192 VUs)": att, "GumbelTopPTokenSelect_v1 (7 VUs)": 7 * (128256 * 2 * 2) / HBM}
rows, tot_sp1, tot_nat = [], 0.0, 0.0
for label, run in runs.items():
    r = json.load(open(H + run + "/result.json"))
    M = {m["name"]: m["value"] for m in r["measurements"]}
    B, t = M["vu.count"], M["t.total"]
    nat = B * native[label]
    tot_sp1 += t; tot_nat += nat
    nat_mem = B * native_mem[label]
    tot_nat_mem = globals().get("tot_nat_mem", 0.0) + nat_mem
    globals()["tot_nat_mem"] = tot_nat_mem
    rows.append({"native_seconds_membound": nat_mem, "drawn_native_seconds_membound": drawn_inst[label] * native_mem[label],"template": label, "run": run, "status": r["validation"]["status"], "instances": B, "unit": unit[label],
                 "drawn_vus": drawn_vus[label], "drawn_instances": drawn_inst[label], "covered_fraction": B / drawn_inst[label],
                 "prove_seconds": t, "setup_seconds": M["fixed.setup_seconds"], "cycles": M["total_cycles"], "chunks": M["chunks"],
                 "proof_bytes": M["transcript.bytes"], "verify_seconds": M["verifier.seconds"], "soundness_log2": -M["soundness_bits"],
                 "seconds_per_instance": t / B, "native_seconds": nat, "overhead": t / nat,
                 "drawn_native_seconds": drawn_inst[label] * native[label]})
drawn_nat = sum(x["drawn_native_seconds"] for x in rows)
drawn_mem = sum(x["drawn_native_seconds_membound"] for x in rows)
summary = {"sp1_prove_seconds": tot_sp1, "native_seconds": tot_nat, "work_weighted_overhead": tot_sp1 / tot_nat,
           "drawn_native_seconds_supported": drawn_nat, "drawn_native_seconds_excluded": excluded,
           "covered_share_of_supported_draw": tot_nat / drawn_nat,
           "covered_share_of_whole_draw": tot_nat / (drawn_nat + sum(excluded.values())),
           "membound": {"native_seconds": tot_nat_mem, "work_weighted_overhead": tot_sp1 / tot_nat_mem,
                        "covered_share_of_supported_draw": tot_nat_mem / drawn_mem,
                        "covered_share_of_whole_draw": tot_nat_mem / (drawn_mem + sum(excluded.values())),
                        "drawn_native_seconds_supported": drawn_mem},
           "rows": rows}
json.dump(summary, open("/tmp/cover_summary.json", "w"), indent=1)
print("| template | run | instances proven | drawn (VUs / instances) | prove s | s/inst | proofs | verify s | soundness | overhead |")
for x in rows:
    print(f"| {x['template']} | {x['run']} | {x['instances']:,} {x['unit']} | {x['drawn_vus']} / {x['drawn_instances']:,} ({100*x['covered_fraction']:.2f}%) | "
          f"{x['prove_seconds']:.1f} | {x['seconds_per_instance']:.4f} | {x['chunks']} ({x['proof_bytes']/1e6:.1f} MB) | {x['verify_seconds']:.2f} | "
          f"2^{x['soundness_log2']:.1f} | {x['overhead']:.2e}x |")
print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=1))
