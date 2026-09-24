import json, sys
for path in sys.argv[1:]:
    r = json.load(open(path)); fp = r["workload_fingerprint"]; m = {x["name"]: x["value"] for x in r["measurements"]}
    sec = fp["security"]
    print(f'{r["run_id"]} {fp["proof_class"][:14]:14s} l={sec["rs_l"]:5d} n={sec["rs_n"]:6d} t={sec["opened_columns"]} D={sec["challenge_coords"]} N={fp["N_subbatches"]:2d} per={m["split.per_proof_vus"]:4.0f} '
          f't.total={m["t.total"]:.3f} hints={m["split.hints_seconds"]:.3f} wit={m["split.witness_torch_seconds"]:.3f} enc={m["split.encode_seconds"]:.3f} mk={m["split.merkle_seconds"]:.3f} '
          f'tests={m["split.tests_seconds"]:.3f} open={m["split.openings_seconds"]:.3f} zk={m["split.zk_masks_seconds"]:.3f} ser={m["t.serialization"]:.3f} '
          f'peak={m["mem.peak_device_bytes"]/1e9:.2f}GB bits={-sec["achieved_log2"]:.2f} per_proof_bits={-sec["per_proof_total_log2"]:.2f} MB={m["proof_bytes"]/1e6:.1f} '
          f'R={m.get("R_proved", 0):.3g} ovh={m.get("overhead", 0):.3g} sw.hints={fp["software"]["backend"].get("hints","?")[:20]}')
