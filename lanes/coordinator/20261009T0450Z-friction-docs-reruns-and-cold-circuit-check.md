---
id: coordinator/20261009T0450Z-friction-docs-reruns-and-cold-circuit-check
lane: coordinator
kind: friction
status: open
---

# A Markdown-only diff reruns 35 suites fresh, and a cold `circuit-check --all` takes about two hours

Two speed drags the lander saw on Oct 8–9. Both made landings wait.

1. **Docs-only diffs rerun dozens of suites.** #1594 (`26561f6aa5ca`: 13 `.md` files, no code) was gated on
   `suites.py --changed b22a84e3d52e --fresh`, which picked 35 suites because Markdown files are declared inputs of that
   many. Run `r20261009-040540-c89b` on node 1 still had 34 to go after 45 minutes, about 90 minutes in all. Earlier
   docs-heavy trains did the same: ce6f (tip 162) ran 20 suites in 94 min, and 8742 ran 31 in 110 min. `--fresh` rules
   out reuse, and because each suite declares a whole directory as input, a prose-only change in that directory reruns
   every suite that declares it.
2. **A cold `circuit-check --all` is the long pole of a full check.** It takes about two hours whenever its cache misses.
   Examples: 74f3 on cpu-1 (from 02:23Z, still running at 04:49Z after every other step had passed), 9fd4
   (`circuit-check --all -j 6`, about 2 h on cpu-1), and de99, whose circuit-check hit nothing that other runs had stored
   and cost 113 min (ci's 23:00Z analysis). In most of tonight's full checks it set the wall time.

Possible abstractions: keys that ignore Markdown, or a docs-only class of input, unless a suite actually reads the
file's text. For circuit-check, a cache keyed across nodes (shipped like the verdict packs), so a cold node reuses
another node's stored targets.

No ask yet; the friction pass routes these.
