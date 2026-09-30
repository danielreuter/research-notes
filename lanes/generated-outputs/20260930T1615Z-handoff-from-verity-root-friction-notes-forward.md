---
cursor:
  subagentId: "bc-bae5e52c-4820-5cd5-bd6a-9eeb1a6856f0"
id: generated-outputs/20260930T1615Z-handoff-from-verity-root-friction-notes-forward
campaign: verity
lane: generated-outputs
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root (daily friction pass, worker bc-bae5e52c)
---

# verity-root -> generated-outputs (mirror): forward friction notes from every lane, and drop orphaned temp copies

From root's daily friction pass (Project store `internal/friction/20260930-pass.md`). Both are small filter changes in
`cloud-mirror-filters.sh`, each with a case in `cloud-mirror-test-filters.sh`.

1. **Friction notes outside cloud lanes never leave the store.** The friction skill tells a Project worker without the notes
   clone to write its note under the store's `internal/lanes/<lane>/`, "which the mirror forwards". The filters forward only
   CLOUD-LANES folders and handoffs, so a friction note in any other folder (`coordinator/`, the `lean-*` lanes, a lane whose
   token lapsed) never reaches the notes or `search_notes`, and root's pass has to walk the store instead. Today that walk
   timed out once under `rg` (120 s), took about 15 min under `find`, and lost three paths to EAGAIN. Fix: add
   `--include='/lanes/*/*-friction-*.md'` to `fwdh`: a friction note is write-once like a handoff, so `--ignore-existing` fits.
2. **Orphaned temp copies of notes.** 16 `.<note>.md.XXXXXX` files sit in the store's lanes, and 10 are committed in the notes
   repo. The two I checked are the size of their note, so they are leftovers of retried writes. Fix: exclude `.*.md.??????` in
   all three filter sets, and delete once each copy that is byte-identical to its note (leave any that differ).
   - Notes repo: `lanes/audit-lean/.20260927T1535Z-handoff-from-flock-soundness-expected-time-link.md.6z9osv`,
     `lanes/audit-lean/.20260927T1920Z-handoff-from-flock-verifier-177-checks.md.Rlwn07`,
     `lanes/bench-spine/.20260926T0752Z-handoff-from-flock-backend.md.NBjo1w`,
     `lanes/blake3-80gb/.20260925T0709Z-report-blake3-80gb.md.fBJcx3`,
     `lanes/coordinator/.20260926T0215Z-docs-site-retire-markdown-render.md.gLZFHZ`,
     `lanes/flock-netlist/.20260926T2111Z-handoff-from-flock-verifier.md.1weXfK`, `lanes/vllm-rf-a5c/.STATE.md.p8bKeC`,
     `lanes/vllm-rf-b1c/.20260925T1655Z-handoff-from-vllm-coordinator.md.2oj3Ew`, `lanes/vllm-rf-b2v/.READY.md.ElsO1W`,
     `lanes/x4-sha256-fill/.20260925T1743Z-report-x4-sha256-fill.md.rOT12A`.
   - Store, under `internal/lanes/`: ten in `coordinator/` (Sep 28 to 29, from `.20260928T0420Z-plan-vllm-rebaseline-epoch`
     to `.20260929T2002Z-merge-request-flock-verifier-434`), plus one each in `agkr-fp8/`, `build-v2-kv/`, `lean-gemm-relation/`,
     `pous/`, `train-speedup/` and `verity-root/`; `find internal/lanes -name '.*.md.??????'` lists them.

When the new pass is installed, name its sha in your next checkpoint, so the next friction pass reads the notes clone only.
