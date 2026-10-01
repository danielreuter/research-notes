---
id: 20261001T0208Z-handoff-from-71c6ab78-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: GPU 5, FP4 design, Pearl-C4 (bc-71c6ab78)
---

# Migration handoff from GPU 5 (bc-71c6ab78): Pearl-C4's #580 and #548. Nothing in flight, nothing unpreserved

Written at 7:08 PM PDT for the 0157Z order. My status file, with every run, art id and rule, is research store
`internal/pouw/rtx-pro/workers/5-fp4-design.md`, and the design note is `fp4-design.md` beside it.

## 1. Branches and PRs

- **#580**, `cursor/pearl-c4-f1f2-3084`, head `639128c87`: draft, mergeable, base #556's `cursor/pearl-c4-f1prime-f2-2cf6`.
  - **What it enforces:** F1′, F2 and R1, B-OVF, V-EX, the tightened D-NF (bytes 0x08–0x7E, a NaN or infinite β rejected),
    the pinned c_L table, and the registered-weights rule (`pearl_c4.check_registration`): the keyed 8-block rotation, with
    V/O plus head interleave inside it only.
  - **Tests:** at 6:32 PM PDT, 1,691 of #580's tests passed (verity 1,351, pouw 278, pouw benchmarks 62), and the repository
    suite's 32 did too.
  - **No `check` has been recorded for it.** Its diff over its base is 13 files, all in `protocols/pouw` and
    `benchmarks/pouw`, so no lean-agreement is needed.
  - **A correction to the backlog and to 2aa33ad8's handoff, both of which list "the B-OVF port" as left:** B-OVF is
    already in #580. It came in with the merge `fb251c6e` (`a097a30e`, under V-EX's `a1b72fd0`), and `7a75614a` regenerated
    its vectors' tile caps. `credit_of` reads the β table, `check` refuses n < 128, and R1 and the tile cap read the
    discounted credit, each with a test.
  - **What's left:**
    - take #556's head `9363e5012` (main's MKL warm-up, a `real.py` pool-fork test fix, Slack tooling);
    - `check --record` on a CPU pod;
    - a merge train with #556.
    - The assessor's two open B-OVF conditions belong to others: the exact search at n = 256 and 512 is bc-a8466279's,
      queued, and #556's tests.
- **#548**, `cursor/pearl-c-fp4-3084`, head `7a30515b7`: draft. `check` passed (`r20261001-000221-f7ef`), and it's
  ready for the next train with #449, #534, #556 and #602. Others merged into it; I don't push to it (frozen for me). Nothing
  is left.

## 2. Runs and jobs in flight

- **None.** No fill job of mine is queued or running on node 2, and nothing runs on my VM.
- Every run of mine is in the store. The last ones:
  - **The verify at 14d6f1bb:** `r20260930-193145-e83c`.
  - **The 16k row's files:** `r20260930-193258-561d` (`art:c64abd83…`).
  - **The re-verify at 486eb171:** `r20260930-215734-5a45`. Its files are `art:8387bebc…`, which I put by hand.
  - **The re-verify at 92ab31dc:** `r20260930-222837-f8a5` (`art:64c1b8ca…`). All three rows ACCEPT and all three no-write
    controls REJECT.
  - The real-activation replays at 7B and 70B are `art:c32b23dd…` and `art:447ecc62…`, and the lut256 fill is
    `art:e8129179…` / `art:da7430ab…`.

## 3. Half-done state

- **Nothing is only on my VM.** #580 and the notes are pushed, and the VM was wiped by a reset anyway.
- **On node 2, kept for reference only (nothing reads them):**
  - `/workspace/pouw/gpu5-fp4/`: scripts with their `.sha256` files, `src-*/` trees, and `gate-cache-14d6f1bb/`;
  - `/workspace/pouw/fill-out/gpu5-fp4/` (`v1-16k-0fa9ff70/`, `lut256-bca8de21/`, `arm-v04*`, `gate-cache-14d6f1bb/`);
  - `/workspace/pouw/fill-out/pearl-c4-real/`;
  - all of these are preserved in the store.
- **The transcripts that re-verify the panel rows:**
  - attempt 21 at 8,192³ and m32-n8192: `art:b0b75c63…` (`transcripts/*/transcript.json`);
  - the 16k row: `art:cdd007b5…` (`r3/transcripts/*`);
  - the verify script: `verify.sh` inside `art:8387bebc…`.

## 4. Next step per kept item, and what I'd stop

- **#580's merge:** take `9363e5012`, re-run the four suites and push. Then run `check --record`, and merge it with #556
  in a train.
- **The registered-weights switch for Pearl-C4** (Daniel, 1:36 and 5:52 PM PDT): the rule is in #580 and lands with it.
  - **A default to confirm:** V/O and the interleave register only together, after the rotation, because only that pair
    was measured (`rotb8s-nvfp4_al_voi`). If either alone should pass, it's one line in `REGISTRATION_STACKS`.
- **The FP4 small-widths line (B-OVF):** it is enforced in #580. The panel's small-n flag lifts when the assessor closes the
  n = 256/512 search and #556's tests.
- **The panel rows** (attempt 21 at 8,192³, decode, and 16,384³ logged): they stand. They were re-verified at `92ab31dc`,
  tile for tile identical to `486eb171`. Nothing is pending.
- **What I'd stop:** Pearl-C4 rows at 7B or 70B shapes (off the headline, server.md 3:22 PM PDT), and MXFP4 beyond its
  contrast line.

## 5. Traps

- **A VM reset** lands the checkout on `main` and wipes uv, `~/.research` and `/tmp`. Check
  `git rev-parse --abbrev-ref HEAD` before merging, and reinstall uv (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
- **A 403 on a notes push:** the global `url.…insteadOf` rewrites github.com URLs to the bot's token. Push to
  `https://x-access-token@github.com/danielreuter/research-notes.git` with
  `-c credential.helper= -c credential.helper='!f() { echo username=x-access-token; echo "password=$RESEARCH_NOTES_TOKEN"; }; f'`.
  The token is never printed.
- **#580's `tests/vectors/pearl_c4.json` pins each case's tile debit and cap, and #556's doesn't.** So any upstream change
  to `credit_of` or the debit fails `test_pinned_vectors_*` only in #580. Regenerate with
  `python tests/pearl_c4_vectors.py` and check that only the expected fields moved.
- **`benchmarks/pouw/pearl_c4/real_table.py` conflicts on every #556 merge.** Keep #580's `TERMS` (`split`, `int8` and
  the retired `two_four`, read as 0 when absent).
- **#556's merges carry main's trains.** Run `suites.py verity-pouw verity-pouw-benchmarks verity repository`, about
  9 min on a 4-core VM.
- **A local `research run`:** `--send` doesn't apply, and the cwd is the run dir. `result.json` needs `run_id` from
  `$RESEARCH_RUN_ID`, or the run files don't publish.
- **The re-verify is slow:** about 25 CPU-min for all three rows on 4 workers (16k alone about 13).
- **Store reads can return EAGAIN or stall:** retry and verify.
- **On node 2:** `gpu-lease 1 -- …` for every GPU command, and `prio=10` with chunks of 8 min or less for GPU fill. Don't
  pass `--timeout` to `research run --on vy-nebius-2`.
