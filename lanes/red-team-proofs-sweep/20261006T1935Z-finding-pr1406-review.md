---
id: red-team-proofs-sweep/20261006T1935Z-finding-pr1406-review
campaign: proofs
lane: red-team-proofs-sweep
kind: finding
status: final
repo: verity
origin: pr:1406@cd35a55a41cbde9d91d37e9fa223483f6c147f55
---

# Red team on #1406 (C-Flock text sweep): GRANT

PR #1406 (`cursor/proofs-sweep-95d4` at `cd35a55a4`, base `cb50af5e8`, which is still `origin/main`) is a text sweep
of 170 files in 5 commits. No Lean code changed and no blocking finding. Label
`grant=red-team by red-team-proofs-sweep ref r20261006-180059-4eb8` on `pr:1406@cd35a55a…`. The comparison scripts and
their outputs are `art:2e9b6230963081e74de4e06aabc8d858fa3b5e0874c15540b6f0f899b2b2d954`.

## What was checked

1. **Text only.** All 170 files are modifications (`git diff --name-status`: 170 `M`; no add, delete or rename). No
   `lean-audit.json` changes, and `git diff --check` is clean. By extension: 148 `.lean`, 13 `.py`, 3 `.md`, 2 `.rs`,
   2 `.sh`, 1 `.cuh` and 1 `.toml`.
   - `strip_compare.py` compares base and head with comments stripped. Python uses `ast.dump` with module, class and
     function docstrings removed. Lean drops `--` and nested `/- -/` blocks (doc comments included), treating strings,
     char literals, raw strings and `«»` names as code. Rust drops `//` and nested `/* */`, CUDA non-nested `/* */`,
     shell `#` comments outside quotes and heredocs (shebang kept), and TOML is compared parsed with `package.description`
     set aside. It finds 3 non-comment differences:
     - `benchmarks/one_stage/a2.py`: the `--unbind` and `--unbound-m0-pythonpath` help strings (allowed).
     - `backends/flock/live/Cargo.toml`: `description` (allowed; nothing else in the TOML differs).
     - **`backends/flock/python/verity_flock/lean_rows.py:213`**, not in the allowed list: the `--out` argparse help
       changes from `"the directory of FlockSoundness/Rope"` to `"the directory of
       verity/Security/Proofs/Flock/Soundness/Rope"`. It is inert (help text only, no test pins it) and correct (the
       directory exists). Commit 4's message declares it, but the PR body says the only help strings are `a2.py`'s and
       that its script "shows no difference apart from `a2.py`'s two help strings". Non-blocking; the body should say so.
   - `char_mask.py` is an independent, naive per-character comment mask. It diffs lines, then characters inside changed
     line blocks, over the 153 Lean, Rust, CUDA and shell files: 0 changed spans outside comments, and no changed Lean
     comment shares a line with code.
   - `mut_test.py` checks both scripts on mutations. Each detects a code edit in a Lean file (an inserted tactic, a
     changed keyword, a line after a doc comment), a Rust code edit and a Python help-string edit, and ignores a
     docstring edit.
2. **Meaning.** I read every hunk of all five commits: commit 1 has 92 hunks, commit 2 has 138, commit 3 has 261, and
   commits 4 and 5 I read in full. Most replacements follow the Glossary.
   - "Coin server" (commit 1): every instance is the live-coin service, which commits coins at `Hello`, issues per-round
     coins, keeps the round bytes and writes the record. That is the Glossary's challenger, so the edits hold. What
     remains in changed files is only the claim id `uniform/flock-coin-server`.
   - M0, M1 and M2 (commit 2): in ZK files, "M0's" (`rep_refines`, `opening_refines`, `ReqOK`, `LoopRel`, `zcShape` …)
     is the non-ZK session's, and "at M0" becomes "without `--zk`"; both are right. M0 as the prover (tree, row format,
     `hm96-sha512` leaf layout, seed-derived coins, default of one table) becomes "the circuit prover" correctly. M1 and
     M2 become "C-Flock ZK", and the test docstrings disambiguate transcript (M1) from rewinding (M2) statistics. What
     remains is only code names (`TabZK.M1`, `hM1`, `m1Schedule`, `padOnto_M1`).
   - VU (commit 3): almost every hunk is the block slot `g` that holds `upv` stacked copies of the unit net and proves
     one drawn unit. The new text is true under the PR's reading of that slot as a template instance. Where VU meant a
     count ("a proof holds at most 32,768 / n …", "a count over …"), the edit reads correctly. Where it meant the
     program's unit (`Integrate/Headline.lean`, about line 95: "the headline bounds template instances that fail …"), it
     is true for `keyProg`, whose units are the template's instances. `HmRegion.lean`'s "the VU's instance" becomes "the
     template instance's input", which matches the Glossary's instance→input row.
   - Retained exceptions, all real:
     - `uniform/flock-coin-server` (`verity/claims/__init__.py:84`);
     - `Flock/Tags.lean`'s pinned `round_digest` strings (lines 169 and 192);
     - the wire fields `vus_per_block` and `units_per_vu` (`Flock/Circuit.lean:282-283`, `live/src/circuit.rs`);
     - the Lean names above;
     - "red-team-flock-3's M0", a finding label in test docstrings this PR doesn't touch.
   - Commit 4 is correct: the new relative paths exist (`Rope/{Gates,Pinned,Checkpoints,Chunks}.lean`, `GateRows.lean`,
     `CROnly/`), and `CROnly`'s statements are guarantees in `verity/Security/lean-audit.json`. RegDraw's "every
     guarantee about `audit L_c`" stays true, since the transfer is `rfl` for any theorem.
3. **Soundness `DESIGN.md` §8** states the 5 Oct ruling as worded in `.agents/skills/friction/SKILL.md` ("Live coins
   only; Fiat–Shamir is out"). Its "live coins from the challenger" agrees with the Glossary's challenger ("issues live
   coins, committed in advance"), which also covers the `seed` coin mode. The `seed`-mode paragraph is kept, and the
   mode is still in code (`FC_COINS`, whose default is `seed`, at `live/src/bin/flock-circuit.rs:103-106`). The section
   claims no code was removed.
   The lemmas it says stay proved exist: `rep_sound` (`RepSound.lean:181`), whose phases are per-coin round-by-round
   lemmas (`Rounds.lean`, `Game/Poly.lean`). The 1c row and the performance-stages line point at §8, and dropping
   Table 1 from §9 leaves both sentences true.
4. **Audit evidence.** `research inspect r20261006-180059-4eb8`: vy-nebius-1, `tree_sha=cd35a55a41cbde9d…`, command
   `python3 tools/lean/audit.py --build --update verity/Security/Proofs backends/flock/verifier/lean`, rc 0, class
   SUCCESS. The fetched `stdout.log` shows `AUDIT … backends/flock/verifier/lean: PASS` (5556 declarations in 47 modules,
   7 guarantees, replay 5.4 s) and `AUDIT … verity/Security/Proofs: PASS` (57845 declarations in 884 modules, replay
   311.5 s, runs 259.9 s), then `AUDIT: PASS`. The written verifier lock has the same sha256 as the branch's
   (`2912aa8d…`). The `security_proofs` lock parses equal to the branch's and differs only in the order of its two
   `runs` keys, as the body says. With no Lean code change, no new audit was needed and no pod time was spent.
5. **Merges.** `git merge-tree --write-tree origin/tip67 cd35a55a4` (`tip67` = `b0d0b1600`) is clean, rc 0, tree
   `45c22779`.

## Non-blocking notes

- PR body: add `lean_rows.py`'s `--out` help string to "What it changes" and to the "Verified" sentence.
- The Glossary's retired-terms row maps "verification unit (VU)" to *proof unit*, and this PR uses "template instance"
  in C-Flock's layout without a Glossary line. AGENTS.md: "when a term changes, update the Glossary and roll it out in
  the same change". The Glossary's template instance is "one occurrence of a subcircuit template in a program"; in
  C-Flock it is the block slot that holds one. A one-line Glossary note, such as "in C-Flock's layout, a template
  instance is also the slot of `units_per_vu` unit-net copies that proves one", would make these sentences read
  directly:
  - "put one registered unit at two template instances" (`Discharge/Hidden/Theorems.lean:18`; also
    `Hidden/Defs.lean:174`, `Hidden/Wide/Defs.lean:54`);
  - "at the unit the template instance proves" (`Hidden/Defs.lean:142-143`, `Hidden/Wide/Defs.lean:28`).
- Misleading under the Glossary: `backends/flock/python/verity_flock/templates/gemm_coordinate.py:59`, "Template
  instances `[lo, hi)` of `input_set`". These are inputs of an input set, and the Glossary says a template instance is
  never an input. Something like "Inputs `[lo, hi)` of `input_set`, one template instance each" would be accurate.
- Ambiguous: `Discharge/Layout/OutPin.lean:11`, "a template instance copy `u'`", meaning unit-net copy `u'` inside the
  template instance, can read as a copy of the template instance.
- `backends/flock/live/Cargo.toml:8` now says "a forwarding prover challenger, the challenger's live-coin part, …". The
  first is `LiveChallenger` (the prover's `Challenger`, Fiat–Shamir's sense) and the second the auditor's challenger:
  two senses on one line.
- "Server" alone is left at `DESIGN.md:368` ("whose bytes the server keeps") and
  `Discharge/DrawWords/Statements.lean:28` ("the server's draw file").
- Held files, not this PR's to fix: `Rounds.lean:14-15` (held by #1355) still says "a Fiat–Shamir proof would reuse
  them unchanged (`DESIGN.md` §8)", which now points at "Fiat–Shamir is out". `Flock/Tags.lean`'s doc comments
  (lines 44 and 161, held by #1318 and #1383) still say "coin server"; its `round_digest` strings rightly stay.
