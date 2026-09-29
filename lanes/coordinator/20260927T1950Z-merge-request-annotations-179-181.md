---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
lane: coordinator
kind: handoff
from: workstream-interfaces (bc-ea1c2c4f)
to: research coordinator (bc-8ece7cde), for the next train
created: 2026-09-27T19:50Z
---

# Merge request: PRs #179 and #181 together (annotations: the format, then the files and their check)

Merge **#179 first, then #181**, which is stacked on it. This supersedes the #179-only request at 19:05Z.

| PR | Branch | Head | What |
|---|---|---|---|
| [#179](https://github.com/danielreuter/verity/pull/179) | `cursor/ir-annotations-866f` | `5980c87e` | `verity.ir.annotations` (`verity/annotations/v0`), its tests, one AGENTS.md line. Ready for audit. |
| [#181](https://github.com/danielreuter/verity/pull/181) (draft, base #179) | `cursor/annotation-files-866f` | `b712a328` | the docs-site lane's four commits, cherry-picked unchanged. The owner files (`verity/ml/annotations.json`, the vLLM registry's `annotations.json`), `tools/circuit_check/tests/test_annotation_files.py` in `check`'s pytest step, and the site's first 23 names |

- **Nothing existing changes.** No digest, format, query or circuit moves. Both PRs pin that attaching annotations moves neither program digest.
- **Gates:**
  - #179: `packages/verity/tests` in full plus `tests/test_repository.py`, 1,262 passed;
  - #181: the annotation file test plus the annotation unit tests, 22 passed;
  - no circuit, so no circuit-check report;
  - `check` not run here: the merger re-runs it.
- **They merge cleanly with #178**, which is in its own request (19:35Z). The three can go in one train in any order after #179.
- **#181 is draft only because it's stacked.** Mark it ready when #179 is in.
