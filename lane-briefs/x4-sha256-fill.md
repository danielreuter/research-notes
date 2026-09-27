---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Lane x4-sha256-fill: RTX 4090 and A100 SHA-256 Table 2 cells at the x4 fold

Budget $30 · FINAL 7 PM PT (02:00Z) · base `origin/main` (`cd963fd4` or later) · branch `lane/x4-sha256-fill`.
Read first: `internal/lane-briefs/cloud-lane-setup.md` (sections 1, 4, 5, 6: notes token, pods, idle while waiting),
`$RESEARCH_NOTES/kb/LANE-CONTRACT.md`, `$RESEARCH_NOTES/kb/TABLES.md` (rules I, M and plateau).

## Why

The first SHA-256 cells are H100 only (BF16 1.1e8× art:fcd6a623, E4M3 1.0e8× art:4aa258ee, both x4, verified and
labelled). The RTX 4090 and A100 SHA-256 rows are empty.

## Goal

1. **RTX 4090 · E4M3 · SHA-256:** `fp8-ada-x4+sha256`. It's already pinned on main, and the red team passed the
   relation at `da74b03e` (coordinator log 10:25Z). So this is only a plateau sweep plus rule I.
2. **A100 SXM4 80GB · BF16 · SHA-256:** `bf16-ampere-x4+sha256`. There's no PINS row yet: fixtures and a gate first (86
   negatives), then a merge-ready handoff with the PINS row and a red-team class-grant request, then the sweep.

## Steps

- **Scripts:** b-ligero-sha256 ran exactly this flow on H100. Its report and `evidence/pod-scripts/` are in the notes clone
  under `lanes/b-ligero-sha256/`. For a pin gate, see also `lanes/b-ligero-standard-hash/evidence/pod-scripts/10-pins-gates.sh`
  with `LEAF=sha256`.
- **Sweep:** x4 at 4096 / 8192 / 16384 / 32768 instances (stop when throughput stops rising), with the `env.sh` allocator
  defaults. Register every result (`bench-result/v1`, `--preserve`) as it lands.
- **Rule I:** one `instance-equiv/v1` per plateau size (`python -m verity_numerical.bench.instance_equiv --vus <n>`),
  registered and **not** labelled by you. Pitfalls: reverify-fp4's handoff `lanes/coordinator/20260925T1706Z-handoff-from-reverify-fp4.md`.
- **Handoffs to `lanes/coordinator/`:** (a) merge-ready for the A100 PINS row, as soon as its gate passes; (b)
  verification-ready, with result and equivalence art ids and the tree. A non-producer verifies and labels.

## Pods and rules

- An RTX 4090 (`vy-x4-sha256-4090`) and an A100 SXM 80GB (`vy-x4-sha256-a100`), both with
  `--register --project verity --guard 60`. Run everything through `research run --on ... --custody-r2 --custody-ttl 8h`.
  **End your turn while a job runs** (setup section 6).
- Terminate the pods at FINAL; say the spend.
