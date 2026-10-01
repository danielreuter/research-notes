---
id: 20261001T1653Z-report-from-circuits-epoch-audit-final
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-epoch-audit (bc-dab39801)
---

9:53 AM PDT, final (supersedes note:20261001T1640Z-report-from-circuits-epoch-audit-counts). Every failed or stopped coverage-grid deployment outside cov-gm* is named: 149, of which 57 are superseded by a later pass. 119 `ov.cause --by circuits-epoch-audit` labels are on the remote (97 runs, 22 evidence arts); bundle art:45ffc9f95d2de2b65bfe777dc0fc785386e537f08d62037b27701d8033cc488f. By family: stopped on purpose 58, harness/config/staging errors since fixed 63, stopped by a guard 10, the pipeline refusing correctly 18. By class: TP2 world-2 rejected 18, unapproved filler withdrawn 17, TP2 hold 15, replay task with no bundle 12, 04:42Z release duplicates/B64 withdrawn 11, Qwen2.5-7B bootstrap rc 3 10, Pythia-160m rotary 9, model not staged on node 2 9, Gemma-2 Commit stopped (held class) 9, Commit watchdog 7, TP2 Commit illegal memory access 6, EOS-stopped request 3, TP B8 staging 3, word-check gate guard 3, node-1 disk emergency 4, compose timeout 2, OLMoE TP all-gathers 2, fill withdrawn 2, and one each of splits unbound at top_p=1, W1 OLMoE shard pin, TP2 MoE blocks, Gemma-2 TP2 softcap, uv.toml config error, served-tap dir not writable, and hang-check false positive. Node 1 has 77 failed attempts, not 83: 76 in the 9:11 AM snapshot (84 failed lines, 8 of them cov-gm*) plus cov-cg04-served-tap at 9:34 AM. Corrections to the 9:40 note: n050-2 and n051-2 aren't running, their Commits are held in release.py; g2b-bool ended succeeded; n051 and n052's labels no longer say superseded; m004-2 and n044 are superseded by their twins cg05 and cg18. Table: internal/circuits/epoch-failures-named.md in the Project store.
