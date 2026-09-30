---
id: 20260930T2140Z-handoff-from-node2-ops-kinds-table-and-monitors
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

# Console: `infra-pool.json` gains a per-kind efficiency table and the live monitors from about 3:10 PM PDT (backward compatible, still `infra-pool/v1`)

These fields are new under `nodes.n2`. Nothing existing changes (`note:20260930T2127Z-reply-from-node2-ops-infra-pool-schema`).

~~~json
"unlabeled_waiting": 20,
"monitors": [{"kind": "gpu-idle-in-lease", "gpu": 0, "owner": "bc-…", "job_kind": "unlabeled:gpu1-pearlc", "mean_util_5m": 3.1,
              "lease_since": "…Z", "key": "…", "msg": "…"},
             {"kind": "gpu-unleased", "gpu": 1, "pid": 123, "cmd": "…", "lease": null, "key": "…", "msg": "…"}],
"kinds": [{"kind": "unlabeled:kt-e70b", "owners": ["bc-…"], "leases": 41, "leased_gpu_h": 6.2, "useful_gpu_h": 5.9,
           "idle_gpu_h": 0.3, "efficiency": 0.95}]
~~~

- `kinds` covers the leases that ended in the last 24 h, the most idle GPU-h first. Filler counts as leased time only.
- `efficiency` is useful ÷ leased.
- A kind is the fill header's `kind=`, else `unlabeled:<first two words of the job name>`, or `direct:<holder>` for leases outside
  the fill queue.
- **Daniel's per-kind table** goes next to `infra/pool-utilization`: kind, owners, leased GPU-h, efficiency and idle GPU-h,
  sorted by idle GPU-h.
- `monitors` holds the flags in force now; they suit a small "now" list on `infra/pool-gpus`.
- Node 1 should arrive as `nodes.n1` in the same shape by noon tomorrow (kueue-fold, merged by my publisher). Read `nodes.*`, not
  `nodes.n2`.
