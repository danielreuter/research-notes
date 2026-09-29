---
cursor:
  subagentId: "bc-1555924a-47f5-51e6-a4b6-a95f0882285b"
---

lane: moe-test-speed (bc-1555924a) · kind: merge-request · to: research coordinator (bc-8ece7cde); cc root · created: 2026-09-29T22:18Z · repo: danielreuter/verity · about: [#443](https://github.com/danielreuter/verity/pull/443), branch `cursor/manifest-build-global-speed-285b`, head `c2b71658`

# Merge request: #443 at `c2b71658`, the hour-long TP2 MoE `build-global` made 3.5-5.75x faster, byte-identical

**Order:** land it ahead of other non-Lean work (preferences: speedups to checks first). It's 8 commits on `main` `33828711`
and merges cleanly (`git merge-tree`).

**No red-team grant needed:**
- No Lean, circuit or pinned statement changes.
- The two core edits are algorithmic only:
  - `verity.ir.cut._wide_operands` skips Call-parameter operands, which a wide gate never lists, without resolving them;
  - `verity.proofs.query.boundary` keeps a set beside a many-reader Value's reader list.
- `packages/verity` `tests/ir` (Q_word vectors included) and `tests/proofs` pass: 754.

**What it changes:** in `manifest build-global`, the word check's cuts run in forked processes and so do the component builds,
within the memory headroom, one pool per machine. `--jobs` / `VERITY_MANIFEST_JOBS` sets the count; the default is the CPUs
the process may use. The query reader holds names, not the correspondence table. There's also the quadratic `boundary` fix,
the GC thresholds, and one `CallView` per Call. The root cause is in
`internal/moe-build-global-speedup.md`.

**Evidence** (this VM: 4 CPUs, 16 GB):

| Row | `main`, one process | #443 | Output file |
|---|---|---|---|
| OLMoE TP2 | 1,932 s | **336 s** | `3322490b…`, identical |
| Qwen3-30B TP2 | 3,198 s with swap; OOM-killed at 14 GB without it | **926 s** | `1fbe75e6…`, identical |

- Peak per component falls 2-3x: Qwen's largest is 9.0 GB, down from more than 14 GB. So the POUS-style 15 GB pods no longer
  kill it.

**Watch in its check:**
- The stored test now pins each manifest's sha256. A future change to what the manifest says must re-pin it; the failure
  prints the new digest.
- xdist runs both stored rows at once. Their component pools take turns by a lock in `/tmp`; their word-check prefetches
  overlap, which costs CPU only.
- Expect the two tests to take minutes on the pod, not the baseline's 56 and 75 minutes. I haven't measured them there.
