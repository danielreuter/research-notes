---
lane: verify-night-2
kind: report
created: 2026-09-25T06:45Z
brief: launch message (coordinator), kb/TABLES.md (+ Amendment 2026-09-24 11:36 PM PT), kb/LANE-CONTRACT.md v2.0
branch: lane/verify-night-2 (worktree ~/projects/verity-main-wt/verify-night-2), base main@7fcedf47
final: 16:00Z hard; budget $12
status: open
---

CHECKPOINT 7fcedf47 (06:45Z) [open] started 06:40Z; pod vy-verify-night-2 (cpu3c 16 vCPU, no guard) created, syncing @ main 7fcedf47; next: bootstrap, then hash-commit 4090 fp8-ada P2 baselines art:71a37756 art:abb219fa + 20-run byte identity
# verify-night-2: non-producer verifier for the Proof optimization workstream (night 2)

Inbox at startup (06:40Z): nothing new. First request from the launch message: hash-commit's 4090 fp8-ada Poseidon2
committer baselines (`lanes/coordinator/20260925T0612Z-handoff-from-hash-commit.md`).

## Pod
- vy-verify-night-2 24p5jceya2gfbn: RunPod cpu3c, 16 vCPU / 32 GB, 60 GB disk, no GPU, host AMD EPYC 9655, created 06:42Z.
  No `guard` (idles between requests by design). Registered (machines.d/vy-verify-night-2.toml).

## Method (as verify-night / verify-po)
- B-Ligero: `backends.direct.ligero.reverify` from my tree with `ligero-verify` built on my pod from my tree
  (`evidence/pod-scripts/03-reverify.sh`): custody, system-digest pin, `batch --target-bits 128` on every rep; PASS writes a
  preserved verification-verdict/v1 and `verified=accepted --by verify-night-2`. Statement binding (`04-stmt-binding.py`):
  the dumped statements' chain-end y words equal the frozen set my tree draws. Negatives: `05-negatives.sh` plus the
  producer's. Commitment roots (`06-core-roots.py`): the statement's tree roots recomputed from my tree's instance set with
  the core reference only (`verity.commitments`: `CommitmentDomain`, `MerkleTree`, `rowleaf`, `poseidon2_babybear` /
  the scheme's leaf), compared with the dumped statements' auth block and the run's commit-evidence.
- Credential: minted on the laptop per request (short ttl, prefixes objects/ manifests/ labels/ attempts/), piped into
  /root/r2.env on the pod, deleted after the request.

## Requests
| # | from | result(s) | cell | verdict | verdict art |
|---|---|---|---|---|---|

## Log
- 06:42Z pod created; syncing lane/verify-night-2 @ 7fcedf47 (= main).
