---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff (urgent) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-29T20:30Z · re: `lanes/vllm-epoch-run/20260929T2010Z-answers-from-vllm-coordinator-67-4-onpod-record.md`

**#4 is written** as `45b9125c` (pushed): reclassified FAIL → GREEN on Daniel's decision (2026-09-29T20:12Z, via root); `fixtures.toml` class is GREEN in the same commit. `verdict` was re-lifted from the run's own `verdict.json` under GREEN and now matches with nothing forced; `coverage` is forced. The record is `art:7b437ce1…` (preserved), from record run `r20260929-194627-4b5f`. The digest line says "written (reclassified FAIL → GREEN: Daniel, 2026-09-29T20:12Z, via root)". One caveat: `lift_expected.py` regenerates `fixtures.toml`'s class from the vault INDEX.json, so a regeneration must carry the change.

**Decision needed before I launch #67. The OLMoE B32 3-pair Commit takes about 3 h, not 1 h.**
- #68, the same model and batch, started its Commit at 19:13Z. At 20:26Z, `commit/runs.jsonl` has 1 of 3 runs. #68's job end is 20:53Z, so **#68 will be cut there** like #67 was. Its Build, Match and strict word check (32/32) passed and will be stored.
- #67's resume at $8 cannot hold a 3-pair Commit. Bootstrap and Build restore take about 0.45 h, Match 0.77 h, the Commit about 3 h and the store 0.7 h: about 5 h. That is about $11 on 2× L40S SECURE ($2.18/h) or $8 on COMMUNITY ($1.58/h, whose L40S hosts ran driver 550 twice). Even on COMMUNITY, the job end (3.7 h after launch at $8) would cut the Commit.
- **Option A:** the 1-pair time fallback for #67 and #68 (a 1-pair Commit is about 1 h; n_runs 6 → 2, as the digest notes for earlier 1-pair rows). Each resume is then about 3 h, about $6.5 SECURE, inside $8.
- **Option B:** 3 pairs with a cap of about $12 each on SECURE, which passes the $260 line (committed $214 + #23 $18 + #57 $15 = $247 before these two).
- **Option C:** defer both.

Tell me A, B or C, and the cap. The resume is ready to launch as soon as you answer. It runs the unmodified `epoch_row.sh` at `14f027c3` with every guard, deadline, stop, store and record stage; only its `row run --stages build` restores the stored Build of record, through a wrapper launcher beside `$PY`, and a `build RESTORED … from art:…` line goes into `stages.txt`. Match reruns, because its large files were omitted from the stored records.
