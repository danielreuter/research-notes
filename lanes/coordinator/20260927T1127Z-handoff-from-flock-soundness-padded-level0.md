---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open · repo: danielreuter/verity

# flock-soundness → coordinator: the padded level 0 is #153; the zero-knowledge statement is #152

- **[PR #153](https://github.com/danielreuter/verity/pull/153)** is a draft on `main`: branch `cursor/flock-padded-level0-8569`
  at `27add24d`.
  - It proves the oracle-layer table theorem with M1's padded level 0, parameterized over the padding `t` and the extra
    lanes per rep `e` (`table_sound_pad`).
  - At #123 `8d621454`'s values it gives at most 2^-196.5 per table at m = 25–27 (`table_sound_pad_m1`).
  - There is no `sorry`, and all 91 axiom checks are standard.
  - It touches no file that #122, #124, #133, #136, #141 or #144 change, except the append-only import list, `Check.lean`,
    and new rows in ASSUMPTIONS §1.1 and §1.4.
- **[PR #152](https://github.com/danielreuter/verity/pull/152)** is a draft on `main`: branch `cursor/flock-zk-statement-8569`.
  It makes ASSUMPTIONS §6 and §8 and DESIGN §11.1 state the zero-knowledge theorem as the M1/M2 red team requires. It is
  wording only.
- **New documents:**
  - `internal/lanes/audit-lean/20260927T1126Z-handoff-from-flock-soundness-instance-rows.md`, answering audit-lean's
    question about an instance's `Rows`;
  - `internal/lanes/flock-zk/20260927T1126Z-handoff-from-flock-soundness-padded-theorem.md`, with the padded theorem and
    one relation to confirm: which weight M1's `e_i` is taken against.
- **Edited:** the checkpoint in my lane report.
- **No directories created, moved or renamed.** The bundle `artifacts/flock-zk-statement-715e7d71.bundle` is deleted, since
  its branch is pushed.
