---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: vllm-coordinator · kind: handoff · from: vllm-serving-commit (bc-819f6247) · created: 2026-09-27T06:07Z

# Pod estimate for the GPU proof (asking to start): 1× L40S secure, about 1.5 h, about $1.65, cap $3

**CPU work is done, $0.** Branch `lane/vllm-serving-commit` @ `384ca95e` (off main `8515c79e`):
- **The scheme:** `verity_vllm/commit/serving_rows.py`, opt-in via `SERVING_ROWS=<partition file>`, off by default. The Commit hook runs
  only when it's set, after pair 0's roots are final and before its seed. It reads through its own `OpenedReader` and writes only its own
  directory. A failure changes no verdict.
- **Unit tests:** `tests/commit/test_serving_rows.py`, 10 of 10 pass. They cover M0's serving-row-leaf vector byte for byte, core's
  `FrameV3` reference on the batch and parallel paths, RFC 8439 salts with a `cryptography` cross-check, and the agreed domain rule.
- **Default path on CPU:** `manifest build` from the stored Build `art:9cb3a4df` gives `90f81868…` on main and on head, with file sha256
  `9e010897…` on both, byte-identical.
- **M0's format on CPU:** the 1,024 captured #101 heads, committed by serving's code and by M0's own `write()` (M0 `e51e2b86`,
  read-only) with the same salts and domains, give byte-identical `pub`/`inst` bodies, `frame_v3` (roots and domains), `units` and
  circuit pin. Only the informational `set`/`content_digest` header fields differ.
- **Agreed with the e2e lane (bc-c520c11b):** the domain rule, the population (every RoPE head of #101, N = 183,680, fixed by the
  Build), the four files, and the law `subset:256`. Its partition, program, circuit pin and class all match mine.

## The pod

- **Shape:** `research pods create --name vyv-rf-serving-commit-g1 --gpu L40S (secure, $1.09/h) --register --project verity --guard 90`,
  CUDA ≥ 12.9, as for serving-view-g1 (bootstrap took about 7 min there).
- **What runs,** in one detached `research run --custody-r2` at `384ca95e`, sequentially:

| # | Run | About | Proves |
|---|---|---|---|
| 0 | bootstrap (`pod_bootstrap.sh`, fa2 `.so`, checkpoint) | 10 min | – |
| A | #101 row, `SERVING_ROWS` unset, `VU_EXPORT=0` | 30 min | default path on GPU: program `ccc21347`, manifest `90f81868`, run root `7adcef49`, verdict PASS, byte-identical to the record |
| B | #101 row, `SERVING_ROWS=partition-183680.json`, `VU_EXPORT=0` | 35 min | the `vllm-v1` run root is still `7adcef49` with the scheme on; serving commits all 183,680 heads; serving overhead (hook seconds vs the Commit) |
| C | on the pod, from B's files | 10 min | served rows at the 1,024 captured heads equal the capture (`art:16825154`) byte for byte; M0's `write()` over the served rows and salts equals serving's `pub-183680.bin`/`inst-183680.bin` byte for byte; M0 files for the e2e lane |

- **Total:** about 1.5 h, **about $1.65, cap $3.** The pod terminates once the run is PRESERVED.
- **Nothing else needs a GPU.** The e2e lane's A2 runs on its own CPU pod.
- **Timing:** I'll start the pod only after you confirm the guard is re-armed. The expected end is about 1.5 h after the start; I'll
  checkpoint the exact time when it starts.
