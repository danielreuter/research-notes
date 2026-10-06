---
id: red-team-flock-e2e/20261006T2105Z-finding-flock-e2e-onto-1330
campaign: proofs
lane: red-team-flock-e2e
kind: finding
status: final
repo: verity
origin: [pr:1257@9f791e48a1e19aa054b29a9f0429a7dc0f7871e7, pr:1332@00a7c304e15f2cc05df3d006e6b3e7ef8e0fefcd, pr:1333@bae15ab087b8db4169e47e3e8ff797a14db1b72d, pr:1334@5f7a6d4191cfd073011fdf4dca79541f2d56ce61, pr:1335@fd538b3311ab08e35182868d9c7f281202d65704]
---
# Red team, C-Flock end to end on #1330: #1257 and steps A–D carried, all five GRANT

Checked 2:00 to 2:05 PM PDT, 6 Oct, by red-team-flock-e2e (agent bc-c688b28a-d1e3-5ecd-ad60-f304761b82be) for the proofs
coordinator. flock-e2e-tip merged #1330's head `8fecfbe34`, which contains #1261's, into #1257 and carried A–D onto it,
with each statement moved from `Specs/Flock/Guarantees/<N>.lean` to `Proofs/Flock/<N>/Statement.lean`. This carries
#1257's grant at `6c8ee376f` and the grants of `note:red-team-flock-e2e/20261006T1645Z-finding-flock-e2e-round2`.

- #1257, `cursor/flock-e2e-95d4` at `9f791e48a1e19aa054b29a9f0429a7dc0f7871e7`: **GRANT**.
- #1332 (A), `cursor/flock-e2e-inputs-95d4` at `00a7c304e15f2cc05df3d006e6b3e7ef8e0fefcd`: **GRANT**.
- #1333 (B), `cursor/flock-e2e-drawn-95d4` at `bae15ab087b8db4169e47e3e8ff797a14db1b72d`: **GRANT**.
- #1334 (C), `cursor/flock-e2e-hidden-95d4` at `5f7a6d4191cfd073011fdf4dca79541f2d56ce61`: **GRANT**.
- #1335 (D), `cursor/flock-e2e-zk-95d4` at `fd538b3311ab08e35182868d9c7f281202d65704`: **GRANT**.

Each is labelled `grant=red-team` by red-team-flock-e2e with this note as ref, on the local and remote stores.

## What I checked

- **Heads and audits.** Each head fast-forwards from its old head and contains the head below it. #1257, #1332 and
  #1335 have their audited commit's tree. #1332's audited commit is `ec9835d4b`, the single-parent commit that
  `00a7c304e` gives `9f791e48a` as a second parent without changing a file. #1333 and #1334 differ from their audited
  commits only in `lean-audit.json`, which is the same JSON with the moved statements' `reads` keys in sorted position.
  Each head's lock is byte for byte the one its run wrote:
  - `r20261006-190303-33b9` for #1257;
  - `r20261006-191856-74bf`, `-191915-290b`, `-191932-9e0d` and `-191948-2b20` for A to D.

  Each run is `audit.py --build --update --owner @proofs verity/Security` on the run's own source, with the kernel
  replay and the tests. Each passes, with only the axioms `propext`, `Classical.choice` and `Quot.sound`, and 1680,
  1680, 1681, 1686 and 1687 guarantees.
- **#1257's resolution is the union and nothing more.** Re-merging `6c8ee376f` with `8fecfbe34` conflicts only in
  `Proofs/Flock.lean` and `lean-audit.json` (merge.py refuses `meaning`), and the head differs from git's merge only
  in those two files.
  - `Proofs/Flock.lean` is the base plus both sides' imports, `EndToEnd` then `Recursive`.
  - In the lock, a three-way check against the merge base `a7134c413` finds no entry that differs from the side that
    changed it. Where both sides changed an entry, it is the union of their additions, with nothing removed: `meaning`
    is #1330's list followed by `Proofs.Flock.EndToEnd`, and each shared `reads` module's reader list holds both sides'
    readers in sorted order. `reads_exempt` is #1330's keys followed by `Proofs.Flock.EndToEnd`.
- **The moved statements are byte-identical.** Each `Proofs/Flock/<N>/Statement.lean` at the new heads is byte for byte
  `Specs/Flock/Guarantees/<N>.lean` at the old heads, for EndToEnd, EndToEndDrawn, EndToEndHidden, EndToEndRegistered
  and ZeroKnowledgeHidden, at each PR's own head and at D's. Each one's `reads` entry is identical under its new name,
  with the same digest, definitions and readers. `meaning` and `reads_exempt` name `Proofs.Flock.<N>` where they named
  `Specs.Flock.Guarantees.<N>`, with the same reasons.
- **The own patches are the same.** Each PR's patch against its parent's new head has the same files and the same
  added and removed lines as before, once the moved paths and the 4 old Lean lines naming `Specs.Flock.Guarantees.<N>`
  (imports) are read under the new names. #1257's own patch over #1330 has the same three Lean files and lines as over main, and the
  same 245 lock changes. In the lock, each step's effect, entry by entry, is the old one less its `exempt` entries:
  - B drops EndToEndDrawn's;
  - C drops EndToEndHidden's and EndToEndRegistered's;
  - D drops ZeroKnowledgeHidden's;
  - A has none to drop.

  These entries excused a `Specs` module from importing `security_proofs`, which a module under `Proofs/` doesn't need.
- **Only #1261's guarantees are new.** Against the old heads, at each of the five heads, the only guarantee records
  added are `RecursiveSound` and `RecursiveZK`. None is removed or changed, and no module's digest or definitions
  change. The new `reads` modules are #1261's 12, and the only new readers are those two guarantees.
- **Merges.** Each head merges onto main `d21be99ba` without a conflict. Main contains neither #1330 nor `6c8ee376f`,
  so the chain lands after #1330 and #1261, with them or in a later train.

No replay of my own: the five runs replayed the kernel at these trees, and `check` replays it again at merge.
