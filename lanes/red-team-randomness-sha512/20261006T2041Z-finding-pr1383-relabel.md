---
id: red-team-randomness-sha512/20261006T2041Z-finding-pr1383-relabel
campaign: proofs
lane: red-team-randomness-sha512
kind: finding
status: final
repo: verity
origin: pr:1383@7f8e8c976a5e2e97a409bca930d857a4e68d0830
---

# #1383 relabel at `7f8e8c976` (main `d21be99ba` merged in): the grant carries

Addendum to `note:red-team-randomness-sha512/20261006T1855Z-finding-pr1383-review`. The head moved by fast-forward,
`5c54ab971` → `e695e0ee2` (merge of main `d21be99ba`) → `7f8e8c976` (PoUW epoch-coin vectors repinned).

- **Same patch.** `git diff d21be99ba 7f8e8c976` and `git diff f5df3bbc5 5c54ab971` touch the same 34 files plus
  `epoch_coins_v1.json`. Changed lines (`-U0`) are identical in all 34; `-U3` hunks without line numbers are identical in
  all but `.agents/skills/friction/SKILL.md`, whose hunk only places #1383's 8:07 AM ruling between main's entries.
- **Lean records.** A three-way JSON check of both `lean-audit.json` files: #1383's changed paths (16: `reads` of
  `Flock.Tags` and `Proofs.Flock.Soundness.Randomness`; 3: `upstream.watch["A4-prf-sha512"]`) and main's (124; 1) are
  disjoint, and the merged file is exactly their union. The watch entry is identical to the granted one. Main touched no
  Flock Lean (Tags, Randomness and their imports `Flock.Hash`, `Flock.Draw`, `Flock.Hm96` unchanged), so those reads stand.
- **Grant paths.** Main's only changes there are `verity_flock/circuit.py` and `test_circuit.py` (row-tree binding on
  `identity_digest_sha512`), which call no randomness function.
- **`epoch_coins_v1.json`.** At `7f8e8c976`, `epoch_coins_vectors.py` regenerates it byte-identically, and with
  `f5df3bbc5`'s v1 randomness swapped in it regenerates main's file byte-identically: the repin is `derive` alone.
  `test_pouw_epoch_coins.py` 9 passed and the randomness suite 50 passed at the head.
