---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: note · from: flock-verifier (bc-8e519ca0) · to: research coordinator (bc-8ece7cde) · created:
2026-09-28T18:45Z · repo: danielreuter/verity · re: the approved T = 130 attention selftest (regression set 17, #317)

# Pod ledger entry: prefix `vy-fv-attn130`, cap $3, deadline 20:30Z

- **Prefix:** `vy-fv-attn130`. One pod, `vy-fv-attn130-selftest`: a RunPod CPU pod, `cpu3m` × 16 vCPU, about 128 GB.
- **Cap:** $3 hard, charged to the research line. **Deadline:** 20:30Z.
- **Guard:** `research pods guard --prefix vy-fv-attn130 --deadline 2026-09-28T20:30:00Z --cap-usd 3 --pod-max-hours 1.75`,
  detached, started before the pod. The pod is drained and terminated when the run ends.
- **The run:** `backends/flock/pod/60-circuit.sh MODE=selftest GPU=0 RECORD=1 SELF_N=4`.
  - The source is #317's branch `cursor/flock-verifier-attention-sets-7ab3` at `4ccad6b6`, which is `main` `ac412eb8` plus
    the regression files.
  - The input is the T = 130 attention set, `TM.attention_head(64, 64, T=130)`, seed 20260926.
- **The result:** if it's clean, I add it to #317 as regression set 17.

## 18:52Z: not running. New pods under the prefix are terminated within about a minute

- **Stock:** RunPod had no 16-vCPU `cpu3m` stock, and none at 16 or 32 vCPUs in any cloud or data center I tried.
- **Three pods came up and were gone within about a minute.** The API answered "not found (terminated, or never
  existed)":
  - `lrc2u5d9zszubc` (`cpu3m` × 32);
  - one `cpu3m` × 16;
  - `2p6t3xhnjo5n0x` (`cpu5m` × 16, $1.04/h, registered, seen once by my guard).
- **My guard didn't do it.** Its log has no trip; it shows the pod once at $1.04/h and $0.02 spent.
- **The likely cause:** a guard over a wider `vy` prefix with `--rate-max` sheds the newest pods first, and about $25/h of
  `vy*` pods are running.
- **Please:** admit `vy-fv-attn130` to that guard's budget (one pod, $1.04/h, $3 cap, until 20:30Z), or tell me which guard
  it is. I'll retry once you do.
- **Spend so far:** $0.02. My guard is still up; no pod exists.

## 19:30Z: done. The pod is terminated at about $0.26

- **After your guard was cleared (18:53Z),** one pod ran: `vy-fv-attn130-selftest` = RunPod `qc8b6tdyrhik7v`,
  `cpu3m` × 16 (128 GB), $0.88/h, from 19:13Z to 19:29Z.
- **Run `r20260928-191348-adc0`** is `SUCCESS` and preserved. The selftest has `all_pass`, `k_log` 26, and 23 sessions
  recorded. Peak memory was 69 GB.
- **Stored as fixture `art:b1d6f11c`,** preserved: the pod's stage and every record.
- **Spend:** my guard's tally was $0.26, plus $0.02 from the pods your guard terminated earlier.
  - The pod was drained and terminated at 19:29Z, and my guard stopped at 19:30Z.
  - Nothing is left under `vy-fv-attn130`.
- **Next, local only:** `ci.py --sets 17` compares Lean with upstream's live verdicts. If it's clean, set 17 goes into
  #317.
