---
id: red-team-vbridge-relabel/20261006T1759Z-finding-vbridge-c-relabel
campaign: proofs
lane: red-team-vbridge-relabel
kind: finding
status: final
repo: danielreuter/verity
origin: pr:1273@498a6af0fbf4c886fad91ce48c1ab0afc55ec6bd, pr:1274@829304af4bd0c2e305c732aacc984e6b98f20d22, pr:1283@4453b9453e60e777442cf11f0d0deeb0886ba5a6
---

# VBridge C (#1273, #1274, #1283): Q5 carry to the frozen heads

The red-team grants carry, by Daniel's Q5 ruling, from the granted heads to the frozen heads. I labeled
each frozen head `grant=red-team` (refs: `note:red-team-vbridge-c/20261006T0402Z-finding-vbridge-c-review`
for #1273 and #1274, `note:red-team-vbridge-c/20261006T0708Z-finding-pr1283-review` for #1283), and
`research data labels --remote` shows each on both stores.

| PR | Granted at | Frozen head | Verdict |
|---|---|---|---|
| #1273 | `50bf1c080` | `498a6af0f` | Q5 carry |
| #1274 | `2434949b9` | `829304af4` | Q5 carry |
| #1283 | `3d9977368` | `4453b9453` | Q5 carry |

Each PR's own patch is the diff from its merge-base with its base (`origin/main`; `50bf1c080`/`498a6af0f`;
`2434949b9`/`829304af4`) to its head, and I compared its `+`/`-` lines at the old and the new head.

**Lean.** `Climb.lean` (#1273), `Open.lean` (#1274) and `RecOpen.lean` (#1283) are line-identical own patches,
and the blobs are the same at both heads (`29c0c3d63`, `fe09fe9a3`, `be3936e6c`). The `VBridge.lean` import
line is identical for #1273 and #1274. In #1283 the only difference is that the old own patch also added the
`Karatsuba` and `Residuals` imports. Those are now in the base, and the old head's `Karatsuba.lean` and
`Residuals.lean` are byte-identical to `main`'s (`9d882b974`, `fb29f150b`).

**Lock (`verity/Security/lean-audit.json`).** These checks were done on the parsed values:
- `sound_climbFrom`, `sound_climbRow` and `sound_recOpen` have the same records at the old and the new head.
- All six `FlockVBridge.*` records are unchanged wherever both heads have them. The new heads of #1273 and
  #1274 also carry `sound_mul128` and `sound_residualForms`, which came in from `main`.
- Every `reads[M]` that an own guarantee reads has the same digest and definitions at both heads. Only its
  `guarantees` list differs: it gained names that `main` added. None were removed.
- At both heads, each own patch's edit is the same: it adds the PR's guarantee record and its own read group,
  and appends its name to the same read groups' `guarantees` lists without changing any digest or definition.
- The new own patches touch no guarantee except their own and no other section of the lock.

What differs in the text is JSON punctuation: the new name is appended after a different last list entry, so
a comma and a `},` move. #1283 also differs by B1's and B2's entries leaving the own patch: the
`sound_mul128` and `sound_residualForms` records, the `Karatsuba`, `Residuals` and `Level3.GF128` read-group
edits, and their names in the shared groups. Those records equal `main`'s as landed. `main`'s
`Karatsuba`/`Residuals` groups differ from #1283's only by `sound_recOpen` in their `guarantees` list.

**Scope.** Each new own patch touches only `verity/Security/` and nothing under `backends/flock/verifier/lean/`.
I ran no Lean audit, because the tip's full `check` runs the audit with kernel replay on the merged tree.
