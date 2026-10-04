---
cursor:
  subagentId: "bc-1a23b70c-8ce6-52de-9b80-c005acb94607"
---

# Kernel tooling: harness self-recording (#583) and its pilot

Worker bc-1a23b70c. The report is `docs/pouw/kernel-tooling-report.md`. The pilot's ask and steps are in `server.md` (17:20Z).

## Checkpoints

- 01:05Z: compute-accounting (bc-e90634dd) is my coordinator (Daniel, 5:52 PM PDT). I hold no goal-critical job. Per the pinned 4:26 PM PDT order, no v2 figure is cited in my documents any more: v2-h1 is D, with a charged floor of at least 0.946% packed. That covers `docs/pouw/tried-techniques.md` and its `curate.py`, and the kernel tooling report's pilot section; my status file and PR texts cited none. GPU 1's binary check (18:40Z) confirmed the pilot's packed cast, so attempt 67 (v1-h1) is cited at 0.519%, and both documents now say so.
- 19:45Z: both pages are up. `docs/pouw/tried-techniques.md`: 326 techniques, the FP4 lanes included. `docs/pouw/sm120-gotchas.md`: 251 facts; it replaces research-notes `kb/sm120-kernels.md`, which now points at it (notes `1361356`). Every run and art id on both traces to a store note. The skill's self-recording and gotchas sections are rewritten in #595 (on #577), for bc-c5df929f. Open: GPU 1's cast check for attempts 67 and 68.
- 18:56Z: the tried-techniques catalogue's first version is `docs/pouw/tried-techniques.md`: 265 techniques (127 kept, 71 dropped, 39 open, 28 superseded), with the kernel-ledger lineage (the pilot's four records; γ cites the cast GPU 1 confirms). Every run id on it traces to a store note. The inputs and the generator are in `internal/pouw/tried-techniques/`; the FP4 lanes' pass is still running, and folds in next.
- 18:38Z: the pilot's result is in the report (`docs/pouw/kernel-tooling-report.md`, "The pilot's result"): 1 of 1 runs recorded, 10.1 min from run end to panel row (5.5 of them a cold index refresh), no hand appends. The publish gap is fixed in #590 `bd5b284f` (the runner publishes what verify declares in `outputs.json`; no credential change; clean on #491's `80bff34cc`, 132 CPU tests). The cast on attempts 67 and 68 stays open for GPU 1; the source at `e0902b4a` runs `form_s5`'s packed cast (`server.md` 18:37Z). The catalogue's extraction has 4 of 6 parts.

- 18:20Z: GPU 2's pilot run `r20260930-174917-2585` is running from `0cb23bfd` (first record pending). Its finding, that forms picked at run time shared a variant id, is fixed in #590 `6b356a8b` (`variant_record(config=...)`). My answer is `server.md` 18:15Z, with the #567 point for bc-f4e8ae34. The tried-techniques catalogue's first version is being extracted from the panel, `server.md` and the workers' files, and goes to `docs/pouw/tried-techniques.md`.

- 17:55Z: pilot started. bc-2aa33ad8 confirmed GPU 2 (17:27Z) and kept #583's `dump` poisoning (17:31Z). #491's gate fix `e22a2808` is on origin in `216143c7`, which carries #583 and passes 230 tests. GPU 2's steps are in `server.md` 17:55Z, and the clock starts at its first published record. #583 `316705c6`: the README's timed runs pass `--no-sampler`.
- broker: source=broker 2026-09-30T17:43Z
- 17:20Z: [#583](https://github.com/danielreuter/verity/pull/583) is a draft at `65e70059`, stacked on #491. The pilot (GPU 2, bc-7442ca43) waits on bc-2aa33ad8's confirmation and on #491's gate fix.
