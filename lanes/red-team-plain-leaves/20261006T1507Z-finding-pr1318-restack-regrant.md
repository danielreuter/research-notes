---
id: red-team-plain-leaves/20261006T1507Z-finding-pr1318-restack-regrant
campaign: flock
lane: red-team-plain-leaves
kind: finding
status: final
repo: verity
origin: pr:1318@3c3b4267a82c9ff7b96adee11c6002c6246e5b6d
---

# red-team-plain-leaves: PR #1318 re-grant at `3c3b4267a` (after the restack)

## Verdict: GRANT

My verdict on PR #1318 at `3c3b4267a82c9ff7b96adee11c6002c6246e5b6d` is GRANT. Since my grant at `f74a2905a`
(`note:red-team-plain-leaves/20261006T1058Z-finding-pr1318-regrant`), the PR has been restacked onto rec-step3's
`77acebf9d`, and it has received the L1 and L2 comment fixes. Neither changes what the PR does. I used git and reading
only.

## (1) The restack carries the same change

**The two patches are equal file by file.** I compared `git diff 273017068 f74a2905a` with `git diff 77acebf9d df5578531`
per file, ignoring `index` lines and hunk line numbers:

- Eight of the nine files are identical, context lines included.
- In `verity/Security/lean-audit.json`, the same hunks only sit at different line numbers, because the base file changed
  under them.
- The one difference is in `PROTOCOL.md` §16.15: "the gateway commits" became "the firewall commits" inside the wrapped
  quote of `leafSchemePlain`'s `use` string.

**That hunk is restored, not rewritten.** At `3c3b4267a`, §16.15 equals `f74a2905a`'s once whitespace is normalized. The
quoted `use` string now sits on one line, and it is the pinned string. Every other copy of the string reads "the gateway
commits…", and none was renamed:

- `backends/flock/live/src/circuit.rs`
- `backends/flock/python/verity_flock/circuit.py`
- `backends/flock/tests/lean/InnerFold.lean`
- `Flock/Tags.lean`
- `tools/move/rename_map.toml`'s `[keep] strings`
- `tools/move/tests/test_rename.py`

**The merge.** `git merge-tree --merge-base a3312e653 7b43fdc5f 77acebf9d` is conflict-free and reproduces
`df5578531`'s tree, `bd53107a74df8a7d802bef117919babb60f37e8b`.

- `a3312e653` is the merge base the recipe passed explicitly. Git's natural merge base is `9859b89d6`, from which a plain
  merge conflicts, because both sides reran `rename.py` on their own.
- Over `a3312e653`, `7b43fdc5f` adds exactly the PR's nine files (+161/−12).

## (2) L1 and L2 are my text

`git diff df5578531 3c3b4267a` touches three files (+6/−5):

- **L1.** `Tags.plainLeaves`'s docstring is my text word for word.
- **L2.** `85-rec-reprice.sh`'s `INNER_LEAN` comment is my text word for word, wrapped at a different word.
- **The quote.** The third file is `PROTOCOL.md`, where the one-line pinned quote is restored.

## (3) Nothing else moved

- **The file set.** `git diff --name-status` over `273017068..f74a2905a` and over `77acebf9d..3c3b4267a` gives the same
  nine files. The only added file is `backends/flock/tests/test_lean_plain_leaves.py`, which the PR has always added.
- **The records.** `verity/Security/lean-audit.json` is the only `lean-audit.json` that differs from `77acebf9d`. Its
  eight changed lines equal the eight lines at `f74a2905a`.

## Run evidence (read, not rerun)

Run `r20261006-143230-d675` (vy-nebius-1, source `3c3b4267a`, rc 0,
`art:207f85f6a0e08b4644a4c5aa810b88ac3e5c4d04fa0c69c515e55ec88d3941c9`) gives:

- `bash -n` ok;
- `lake build` ok;
- the quick flock suite passed;
- `test_lean_plain_leaves.py` 6 passed, both refusal modes included;
- the verifier audit PASS: 5562 declarations, axioms `propext`, `Classical.choice` and `Quot.sound`, 7 guarantees.

## Label

`grant red-team` on `pr:1318@3c3b4267a82c9ff7b96adee11c6002c6246e5b6d`, by `red-team-plain-leaves`, with this note as
its ref. `research data labels … --key grant --remote` reports
`pr:1318@3c3b4267a82c9ff7b96adee11c6002c6246e5b6d: 1 on both, 0 local only, 0 remote only`.
