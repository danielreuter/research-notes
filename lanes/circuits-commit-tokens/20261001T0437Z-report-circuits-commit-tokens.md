---
id: 20261001T0437Z-report-circuits-commit-tokens
campaign: overnight-sep30
lane: circuits-commit-tokens
kind: report
status: open
repo: danielreuter/verity
origin: circuits-commit-tokens (bc-aa52a6d5)
---

CHECKPOINT 0b1787843 (07:38Z) [open] 12:38 AM PDT: PR branch cursor/commit-tokens-record-8c79 at 0b1787843 merges main 4e2a7abcd (P10 conflict resolved to measured sizes), 1,233 tests 0 failures; grid branch cursor/coverage-v1-2622 at 8185e277e; PR not opened by this lane (no PR tool in this session, gh read-only): title and body for circuits in the Project store, internal/circuits/commit-tokens-pr-body.md
CHECKPOINT 6106fa814 (07:31Z) [open] 12:31 AM PDT: circuits' four decisions in (token-record link beside a Match record only when the sampled ids are committed; one reader with max_tokens->cap and index from request order; tokens_source kept; config-run note on a_r_source); cursor/commit-tokens-record-8c79 @ 6106fa814 (1,195 tests, 0 failures); cursor/coverage-v1-2622 @ 8185e277e, a fast-forward merging 4764da87e (1,216 tests, 0 failures); handoff note:20261001T0729Z-handoff-from-circuits-commit-tokens-coverage-v1-head; PR not opened (no PR tool in this session, gh read-only): circuits to open it
CHECKPOINT 348c28ee7 (06:33Z) [open] 11:33 PM PDT: g160 and n105 config-run reruns PASS, replay 460/460 each (g160 commit r20261001-052120-a4f2 + replay r20261001-052900-81f6; n105 commit r20261001-051917-f31d + replay r20261001-052743-2f24), all 6 attempts PRESERVED and labelled with their question; agreed-names handoff acted on (every spec name matches; one extra field tokens_source); report note:20261001T0555Z-report-from-circuits-commit-tokens-reruns-pass; PR waits for circuits' go
CHECKPOINT 348c28ee7 (05:00Z) [open] 10:00 PM PDT: reruns submitted on node 1's Kueue dispatcher (research run --queue refuses node-1 GPUs; node 2 holds Commit guests overnight): circuits-commit-tokens/ct-g160, ct-n105, config-run@56358e661222, tree = coverage-v1-2622 + the change (cursor/commit-tokens-on-coverage-v1-2ffa 79e7cce87, check/lint/pipeline tests pass there); advisor conditions handoff acted on
CHECKPOINT 348c28ee7 (04:37Z) [open] commit tokens record + link pushed: cursor/commit-tokens-record-8c79 @ 348c28ee7; check/pipeline/lint suites pass; next: confirm sampled_token_ids on g160/n105 records, then the config-run reruns
