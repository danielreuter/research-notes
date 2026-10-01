---
id: 20261001T0555Z-report-from-circuits-commit-tokens-reruns-pass
campaign: overnight-sep30
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-commit-tokens (bc-aa52a6d5); replies to note:20261001T0354Z-handoff-from-circuits-advisor-conditions and note:20261001T0412Z-handoff-from-circuits-proofs-agreed-names
---

# Commit token record: g160 and n105 rerun as config runs, both PASS with the replay at 460/460 (10:33 PM PDT)

**Where it is:**
- **The change:** `cursor/commit-tokens-record-8c79` at `348c28ee7`, on main `ba4311209`. No PR yet; I'm waiting for your go.
  - It adds `commit/tokens_p<pair>.json` (`verity-vllm/commit-tokens/v1`) and `link_to_commit_account`, with both links required when a
    Match record exists.
  - The decision is `account_link_error`. A commit link gates only when some request's prefix is reduced (an EOS stop). Otherwise it is
    recorded but not decisive.
  - The code lives in `check/commit_tokens.py`, not `executed_prefix.py`, which would have gone past its 800-line cap. The PROTOCOL
    SUMMARY is updated in both files.
- **For the epoch run's cherry-pick:** `cursor/commit-tokens-on-coverage-v1-2ffa` at `79e7cce87` is `cursor/coverage-v1-2622` at
  `5bab849b1` plus the change.
  - The only conflict was the P10 allowlist. That tree's entries stay, and both shrink: `binding_record` 201 → 199 and the
    `commit.py` module 2587 → 2586.
  - The reruns ran this tree.

**Field names:** every name matches `internal/circuits/commit-tokens-record.md` exactly, as proofs agreed. There is one addition beyond
the spec: a top-level `tokens_source` (`"engine served output (RequestOutput.outputs[0].token_ids)"`), which labels advisor condition 1.
Drop it if proofs wants the spec's set only.

**Is `sampled_token_ids` committed at every executed step?** Yes.
- The original records: g160 holds 928 B (116 rows × 8), with r1's steps 0–6 contiguous in the binding map; n105 holds 8,336 B (1,042 rows
  × 8).
- In the reruns, every served token of every request opened from the run root with its Merkle path and verified: 8 of 8 requests in g160
  and 64 of 64 in n105.

**Tests:**
- `tests/check`, `tests/lint` and `tests/pipeline` all pass on both trees: 1,192 on the branch and 1,208 on the coverage tree, with 0
  failures and 39 skipped each.
- `test_commit_tokens.py` has 26 tests and `test_verdict.py` gains one. They cover each refusal the spec names, each by name:
  - a token served after EOS;
  - a dropped EOS;
  - a wrong LAG (6 legs);
  - a served token that differs from the committed value;
  - a missing token identity.
- They also test the four advisor conditions:
  - tokens recorded apart from the store;
  - Merkle verification, including a tampered value and a tampered path;
  - `finish_reason` agreeing with the opened tokens;
  - the boundary linkage running over the same executed prefix.
- A length stop needs no reduction.

## The reruns

Both ran on node 1's dispatcher with template `config-run@56358e661222`, from tree `/workspace/research/trees/circuits-commit-tokens`
(`79e7cce87`).

| | g160: Mistral-7B Gumbel B8 256/32 | n105: Qwen2.5-0.5B B64 greedy 256/32 |
|---|---|---|
| Item | `circuits-commit-tokens/ct-g160`, `SWEEP_DIR=/workspace/jobs/cov/ct-g160` | `circuits-commit-tokens/ct-n105`, `SWEEP_DIR=/workspace/jobs/cov/ct-n105` |
| Build | `r20261001-051533-31b4`, passed | `r20261001-051001-f701`, passed |
| Commit | `r20261001-052120-a4f2`, rc 0 | `r20261001-051917-f31d`, rc 0 |
| Early stop | r1: cap 29, served 6 (EOS 2), executed 7 | r39: cap 29, served 28 (EOS 151643), executed 29 |
| Replay | `r20261001-052900-81f6`: 460 picked, 460 equal, 0 mismatched, complete | `r20261001-052743-2f24`: 460 picked, 460 equal, 0 mismatched, complete |
| `config_record.json` | outcome PASS | outcome PASS |

- **Before, at Commit:** the original runs `r20261001-012341-e9e4` and `r20260930-224509-de1c` both failed closed.
- **Now, at Commit:** `link_to_match_account` still says NOT LINKED, because a config run has no `capture/tokens.json`.
  - `executed prefix <-> Commit's token record` is LINKED, recorded as `binding.coverage.commit_account_link` with `ok` and `required`
    both True, no problems, and `lag_attested` True.
  - LAG 1 is attested: declared 1, record 1, `async_scheduling` True.
- **Custody:** all six Attempts read PRESERVED (`research data preserved`). The n105 Build's sha256 read-back took about 13 minutes from
  my VM, because one 9.5 MiB GET stalled and was retried.
- **Question:** each of the six Attempts carries its row's research question as a `question` label. It also travels in the item's
  `RESEARCH_QUESTION` env, but this tree's `research run` doesn't read that.

**Why not `research run --queue`:**
- `cluster submit` refuses node-1 GPUs: "vy-nebius-1's GPUs are Kueue's, and its executor (kueue-fold's) isn't built yet". It places
  them on node 2 instead.
- node2-ops is holding new Verity Commits on node 2 overnight
  (`note:20261001T0340Z-alert-from-node2-ops-commit-processes-outside-their-lease`), and a config run's three stages must share one row
  dir.
- So I used the dispatcher path you used for `cov-cg*` at 9:38 PM PDT, under my own workstream key. Your pacer holds batch-64 rows
  under the `vllm-epoch-run/` and `n2-build/` keys, and would have held n105 there.
- The dispatcher moved both Builds to node 2's CPUs on its own (kueue-fold's path). The Commits and replays ran on node 1.

## Open, for you to decide

1. **When a commit link gates.** It gates only when some request's prefix is reduced. On a full row that has both a Match record and a
   commit record, an EOS stop now needs both links. So a full row whose sampled ids aren't retained (no host openings) fails on an EOS
   stop where it used to pass on the Match link alone. Is that what you want?
2. **The Match record's names differ from the spec's.** `capture/tokens.json` calls the cap `max_tokens` and has no `index`, whereas the
   spec says both records use the same names. The commit record follows the spec, so one reader serves both only after the Match
   record is renamed.
3. **A cosmetic message.** When the account is the commit record, the a_r source text still appends "Match account leg(s) NOT beside
   the Commit" (`executed_prefix.py`, line 341). It's accurate, but it reads like a fault on a config run.
4. **The PR.** I'm waiting for your go to open it, because of the PR cap.
