---
lane: verify-po
kind: report
created: 2026-09-24T21:12Z
brief: launch message (coordinator), kb/TABLES.md
branch: lane/verify-po (worktree ~/projects/verity-main-wt/verify-po), base main@ab9573fd
final: 03:45Z hard; budget $6
status: open
---

CHECKPOINT 891572a0 (21:57Z) [open] arith 4090 FP8 s1+s5: 7/7 reverify PASS + BOUND, labelled verified=accepted --by verify-po; verdicts art:7dae93fd art:9a59e106 art:4ecc7aee art:00dabdc8 art:11c4595f art:6a6c101b art:1ca0fbef; now B-Ligero negatives + A-GKR 4090 art:1b4fd4a1 (r20260924-215649-a2c4)
CHECKPOINT df48ecf3 (21:49Z) [open] pod bootstrapped (ligero-verify d89cffc7 from main ab9573fd); arith s1 reverify r20260924-213516-228f: labels pulled (11224), pod catalog reindex --remote in progress; next reverify+binding+negatives
CHECKPOINT 92dab0ad (21:29Z) [open] started; pod vy-verify-po (cpu3c 16 vCPU, no guard) synced @ main ab9573fd, bootstrapping (r20260924-212919-b175); next: reverify arith step-1 4090 FP8 art:7775888d art:1523b35c art:021aeabb
# verify-po: non-producer verifier for the Proof optimization workstream

Inbox at startup (21:13Z): nothing new. First request from the launch message: lane arith step 1 (4090 FP8 B-Ligero).

## Pod
- vy-verify-po 4tnxm5mqtez2v1: RunPod cpu3c, 16 vCPU / 32 GB, 60 GB disk, no GPU, host AMD EPYC 9754, created 21:17Z.
  No `guard` (idles between requests by design). machines.toml entry added.
- /workspace/src = `research pods sync` of lane/verify-po @ ab9573fd (= main), clean, tree bdf6fec1.
- Bootstrap: run r20260924-212919-b175 (`evidence/pod-scripts/01-bootstrap.sh`, CPU torch, HEALTH=0).

## Method (as verify-night)
- B-Ligero: `backends.direct.ligero.reverify` from my tree with `ligero-verify` built on my pod from my tree
  (`evidence/pod-scripts/03-reverify.sh`): custody, system-digest pin, `batch --target-bits 128` on every rep; PASS writes a
  preserved verification-verdict/v1 and `verified=accepted --by verify-po`. Then statement binding
  (`04-stmt-binding.py`, verify-night's 08): the dumped statements' chain-end y words equal the frozen set my tree draws.
- Credential: minted on the laptop per request (short ttl, prefixes objects/ manifests/ labels/ attempts/), piped into
  /root/r2.env on the pod, deleted after the request.

## Requests

## Log
