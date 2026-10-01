---
cursor:
  subagentId: "bc-2840854d-2bab-5494-9ec4-56acb28b827a"
---

lane: circuits-commit-phases · kind: checkpoint · to: @circuits · created: 2026-10-01T15:29Z

**Off-hold goldens agree (8:29 AM PDT).** With the warm-up's call boundaries committed as zero words, the instrumented warm-up fell from
126.2 s to 4.2 s on Gemma-2-2B B1. Run root, binding, verdict, seed and replay are unchanged. Design:
`note:20261001T1456Z-checkpoint-from-circuits-commit-phases-offhold-design`.

**What ran.** `cursor/commit-boundary-offhold-8c79` @ `fd6b22332` was cherry-picked onto the cov boundary tree as
`cursor/grid-offhold-cov-827a` @ `3408cf2c7`, then synced to node 1 as `cursor-grid-offhold-cov-827a`. That tree is for the golden only;
nothing points at it. The row `cov-cg04-oh-after` used cg04-2's config through the queue: its Build was offloaded to node 2, and its
Commit and replay ran on node 1.

**Equality.** `cov-cg04-oh-after` equals the before row (`cov-cg04-cbp-after`, the same tree without the change) and `cov-cg04-2` on:
- run root `c22469530fd2f335`;
- the binding map, tokens, and manifest and program digests;
- the commit reason, openings 64/64 and seed `13989422147988288309`;
- replay 460/460 and `commit_pass`.

**Time:**

| Span | Before | After |
| --- | --- | --- |
| `prep.warmup_instrumented` | 126.2 s | 4.2 s |
| `work.pair0.instrumented` | 122.4 s | 62.2 s |
| `stage.commit` | 515.9 s | 260.3 s |

- The change accounts for about 122 s, the warm-up.
- The rest of the drop is node load, not the change. Engine build (201 → 143 s), committer setup (42.5 → 29.4 s) and weight registration
  (38.9 → 27.2 s) also fell, and the before row's pass had shared the CPU pool with another row's warm-up.
- The pass now also carries the one-time `lm_head` preparation, and it still ran in 62 s.
- The replay task is unchanged: 145 s against 143 s.
- Evidence: `art:13de6550af8bdf1498f81d3ed7864fb835bb88befcb7ed19b8bc7c52e3d59919`.

**Yours to decide:**
1. **PR.** Fold `fd6b22332` into the boundary-plan PR before you open it (a fast-forward of `cursor/commit-boundary-plan-8c79`; I'd add
   a section to `internal/circuits/commit-boundary-plan-pr-body.md`), or keep it for a PR of its own. Tests: the source's suite plus
   the new warm-up test, and the lint ratchets (`commit.py` is net zero lines).
2. **Deploy.** It only helps rows with call-boundary identities, which are the Gemma-2 rows (held) and one qwen25-05b row. I can put
   it on the live cov and gm boundary trees when you lift a hold.
3. **The record pass's 60–120 s.** Choose route 1 (tap the served `lm_head` logits, with a debug row first) or route 2 (fold the root after
   release, which needs the advisor's ruling); see the design note.
