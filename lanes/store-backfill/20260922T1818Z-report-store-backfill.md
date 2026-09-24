---
id: r21-infra/store-backfill/20260922T1818Z-report-store-backfill
campaign: r21-infra
lane: store-backfill
kind: report
status: closed
repo: verity-main@fad5f4b8867e6c4c25db70db65081cf921782f32
---

# The evidence store is the source of truth for the r20 numbers (lane/store-backfill, 2026-09-22)

Branch `lane/store-backfill`, worktree `/Users/danielreuter/projects/verity-main-wt/store-backfill`, HEAD `fad5f4b`
(4 commits on `main` 72e8c7a, not pushed). `uv run pytest tools/research backends/numerical tests/test_repository.py -q`:
698 passed, 9 skipped (11 new tests). Real store `~/.research/store` after the reindex: 930 artifacts, 382 attempts
(399 by the end of this note: other lanes keep finishing runs; the sweep is idempotent), 3640 labels.

## 1. Back-fill (`research data attempt publish --all --runs-dir ~/.research/runs`)

First real pass (10:55 PDT): 365 published, 0 already present, 0 errors, the rest refused (still running). Last pass while
writing this: 410 run dir(s): 17 published, 382 already present, 11 refused (not terminal), 0 error(s). Refused =
`RuntimeError: run <id> is running: the store only sees completed or failed attempts`, correct for the 11 runs whose
`status.json` is still `running` (r20260922-053831-0305 … r20260922-181404-e39d). 82 more directories under
`~/.research/runs` have no `job.json` and are not swept.

Bug fixed on the way (the one error class hit): `attempt.publish` raised
`ConfigError: ~/.research/store.toml: credentials env vars AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY are not set` from
`LocalStore.get_attempt` (it consults the remote when the local copy is absent) before writing anything. Now the publish
stays local, records the error as `preserve_error`, pushes nothing (`attempt.py::_existing_attempt`; test
`test_publish_is_local_when_the_remote_is_configured_but_unusable_here`). `--all` prints
`published / already present / refused (not terminal) / errors` with one line per error class (`cli_prov.publish_counts`).

FINDING: the same `ConfigError` is in 364 of the 374 `store_publish_error.json` files under `~/.research/runs`, i.e. the
runner's auto-publish has failed on this machine for every run since `store.toml` gained its `[remote]`. The attempt the
brief called "already in the store" (r20260922-174533-b2db) was one of them; the back-fill created it. Until this branch
lands, other worktrees' `research run` still fail to publish locally.

Also fixed: `LocalStore.labels()` sorted the same-second `~N` suffix lexically (`~10` before `~2`); now numeric.
`research data where` on a broken vault reports `remote UNUSABLE <error>` instead of failing the local answer.

## 2. Ledger import (`python -m verity_numerical.bench.ledger_to_store [--store ROOT] [--dry-run]`)

235 ledger rows -> 185 on attempts, 50 on `ledger-row/v1` artifacts (rows whose run id is None or whose run never reached
`~/.research/runs`; kind added to `kinds.py`, `meta` = the row as written). Labels: 3594 + 11 red-team assertions
(`red-team-zk`, ref r20260922-100305-2b13 -> r20260922-092404-2a1b, the three b-ligero2 `--zk` rows
081245-1e0d / 082245-c96b / 092841-94ac, each `proof_class=NON_ZK_PROOF_DIAGNOSTIC`; `red-team-zk-2`, ref
r20260922-112029-2db3 -> r20260922-105905-2021, EARNED). Every non-structural field of a row is a label `key=value`
(`assumptions` as JSON), `--by <lane>`, `--ref backends/numerical/reports/ledger/<lane>.jsonl:<line>` (several rows share a
run id and a ts; the file:line is what makes a row addressable), `ts` = the row's ts. Second run against the real store:
`labels 0 added, 3594 already present; red-team assertions 0 added, 11 already present`. `--dry-run` writes nothing.
`research data labels r20260922-092404-2a1b --history` shows the lane's three claims (ZK / HVZK / NON_ZK across its own
rows) and the red-team's downgrade; `… r20260922-105905-2021 --history` shows the b-zk-fix claims and the EARNED re-audit.

## 3. Tables from the store (`python -m verity_numerical.bench.store_tables [--proof-class-by PATTERN] [--diff-ledger]`)

`store_tables.render_like_for_like(index, by_glob)` builds the like-for-like table from three queries on `Index.sql`
only: `ATTEMPT_SQL` (is the run an attempt), `LEDGER_ROW_SQL` (the `ledger-row/v1` artifact of (lane, run id, label prefix)
through `artifact_meta`), `ROW_LABELS_SQL` = `SELECT key, value, by, ts, ref, path FROM labels WHERE target = ? ORDER BY
ts, path`; the producing lane's assertions grouped by `ref` give the row, `policy_proof_class` picks the class.

~~~text
--diff-ledger --proof-class-by 'red-team-*' : 28/28 rows match (100.0%)
--diff-ledger (the producing lane's own claim): 26/28 rows match (92.9%)
  row 3  (B-Ligero v1 (b-ligero2 --zk), 8b masking -- gate4 same-card) [label]: store=COMPLETE_HVZK_BACKEND ledger=NON_ZK_PROOF_DIAGNOSTIC
  row 18 (B-Ligero: b-zk --zk + HM96 coins, fused tests, L40S (b-zk, P) [label]: store=COMPLETE_ZK_BACKEND   ledger=NON_ZK_PROOF_DIAGNOSTIC
~~~

Those two are exactly the downgraded rows: the ledger has the red-team's verdict baked into the row; in the store the lane's
claim and the red-team's verdict are two assertions and the policy picks (`min(lane's claim, latest matching audit event)`;
downgrades stand, nothing is upgraded, the EARNED re-audit leaves b-zk-fix's claim in place). No class of rows is
irreproducible: rows without a run id come back from their `ledger-row/v1` artifact. One comparison caveat: the `label`
column is compared by class token only, because `decision_tables.label_override` appends hand-written prose.
`test_campaign_ledger_round_trips_through_a_fresh_store` imports the committed ledger into an empty store (every row an
artifact) and asserts the same 28/28 and the same two differences.

## 4. Repo replicas (`fixtures/artifacts.json`, kind `fixture/v1`)

~~~text
art:4f8e9ff844325c68da26ead9d9f9f85f2859d8a7470829fa2541ada1d9109801  fixtures/hawkeye/PIN.json
art:cf4699436015c096941a361160b5bcb570d02d469ad014988e99aeab0fb022c8  packages/verity/tests/ml/fixtures/golden/ada_bf16_m16n8k16.json
art:592130d2c1e0d166446c59cb43795e090e99695e2f110523715e93a52746010e  fixtures/bench-instances/v1/manifest.json
art:c94fae7b8f1c37950b8bb13e76221948057b0bfa4d616ca0a7644ca74a39d3df  fixtures/bench-instances/v1/vu-k1536.index.json
art:9e977c565a9468b46936120b1d09495786ffaf308963409a350f565426cc9169  fixtures/bench-instances/v1/vu-k1536-neg.index.json
art:19f80a238753239044f5f850e9907259a53938522512eed40a53ea1f5fd7fd53  fixtures/bench-instances/v1/tu-k16.index.json
art:cbc34932768dc7f427fa0110f8544fdf491a61b833ad30209a821139f5f2b40e  fixtures/discrepancy_log.json
~~~

The bench-instances arrays (`*.bin`, gitignored, > 20 MB) stay out. `research data where art:4f8e…` prints `local present`,
`repo present verified=… fixtures/hawkeye/PIN.json`, `remote UNUSABLE …`. `tools/research/tests/test_repo_replicas.py`
rebuilds each manifest from the tracked file and checks it hashes to its id, and that every path is git-tracked.

## 5. Reindex proof

`rm ~/.research/store/catalog.sqlite && research data reindex` -> `930 artifacts, 382 attempts, 3640 labels`. The rendered
table (31 lines, md5 f7742a2d3fc52a7d987d7a01ef608660) and both `--diff-ledger` outputs were captured before and after and
compared with `cmp`: byte-identical under both policies.

## 6. AGENTS.md / docs

Five lines under "Where writing goes" (evidence through `research run`, claims as labels, the ledger frozen, repo replicas).
Commands documented in `tools/research/README.md`; `ledger-row/v1`, the label ordering and the broken-vault behaviour in
`tools/research/src/research/store/README.md`.

## Not done / to watch

- Nothing pushed; no remote push (credentials absent here), so nothing is PRESERVED.
- Concurrent `reindex` from two lanes on the shared `catalog.sqlite` briefly showed missing labels once (a `LookupError` in
  `store_tables`); a clean reindex restored it. The catalog is disposable, but two writers rebuilding it at once is a race.
- `decision_tables`' bucket and census tables are not rebuilt from the store yet; the like-for-like table is.
