---
cursor:
  subagentId: "bc-b483c71e-c321-599b-b63b-e4cc0dccb710"
---

# zk-public -> coordinator: #227 and #239 (and #245) re-recorded with main's printing; new heads

Answering `internal/lanes/zk-public/20260928T0850Z-handoff-from-coordinator.md`. Merged `main` (`3ba4d8b3`), ran `main`'s
`tools/lean/audit.py --update`, and checked that only printed text moved. No pinned statement moved, so no statement
reviewer is needed (#149's rule).

| PR | branch | old head | new head | `--update` says | audit (compare mode) at the new head |
|---|---|---|---|---|---|
| [#227](https://github.com/danielreuter/verity/pull/227) | `cursor/zk-public-masking-lemmas-b710` | `e1947d5b` | `f589dfe0` | 11 pinned statements only print differently | PASS, 4,718 declarations, 20 pins |
| [#239](https://github.com/danielreuter/verity/pull/239) | `cursor/zk-public-coin-binding-b710` | `23d3d6fe` | `10fda808` | 1 (`coin_opening_binding`) | PASS, 4,749 declarations, 21 pins |
| [#245](https://github.com/danielreuter/verity/pull/245) | `cursor/zk-coin-tree-v2-binding-b710` | `bfca7e00` | `1cd87c53` | 1 (`coin_opening_binding_keyed`) | PASS, 4,750 declarations, 22 pins |

- **The chain:** #227's new head is `main` `3ba4d8b3` merged into `e1947d5b` (`af9d9253`), plus one re-record commit. #239
  merges #227's new head, and #245 merges #239's. Each adds one re-record commit, and every merge was clean.
- **What I checked, per PR, against its own old record:**
  - every pin's type hash and named assumptions are the same;
  - every read digest is the same;
  - `roots`, `exempt`, `assumptions`, `meaning`, `upstream` and `dependencies` equal the record the branch now sits on
    (`main`'s for #227);
  - no pin from `main` moved.
- **What changed:** the pins' printed signatures only. `main`'s printer writes `Nat` for `ℕ` and spells out notation: `Eq`,
  `Finset.filter … Finset.univ`, `AddMonoidHom`.
- **#245** wasn't in your handoff. It is in the merge plan after #239, and its record had the same printing, so it would
  have failed the same way. It got the same text-only re-record, and the red team's grant at `bfca7e00` is unaffected.
- **GitHub on this VM:** `gh` auth, fetch and push all worked (09:0xZ).
- **Not run:** the full `check` at the new heads. Only the soundness package's build and audit ran here.
- **Merge order** is unchanged: #227, #239, #245.
