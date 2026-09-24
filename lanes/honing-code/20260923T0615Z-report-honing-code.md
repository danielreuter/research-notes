# Lane honing-code — report (2026-09-23)

CHECKPOINT 77033bf  mergeable: ALL nine items (1-9).  `uv run pytest tools/research` 178 passed, 1 skipped; `uv run pytest backends/numerical/tests/bench` 155 passed, 5 skipped.  `git status --short` empty.  No store mutation (temp stores + FsRemote + in-process FakeS3 only; `~/.research/store` read through a /tmp copy of its metadata).
CHECKPOINT 614fc68  mergeable: items 1-8 (item 7 multipart landed).
CHECKPOINT b8fe016  mergeable: items 1-6, 8 (item 5 tar-streamed pull, item 6 dead pod).
CHECKPOINT 8dd14c9  mergeable: items 1, 2, 3, 8.
CHECKPOINT c8044dd  mergeable: item 1, item 8.

Branch `lane/honing-code` on `~/projects/verity/.git`, worktree `~/projects/verity-main-wt/honing-code`, base `main` = 6babe27.  Commits, oldest first:
c8044dd (evict, fetch --path/--list, where parallel) · 8dd14c9 (labels-sync, catalog schema) · 1ecd49d (vocab hygiene, vocab-check) ·
b8fe016 (pull tar stream, dead pod) · 614fc68 (multipart) · 77033bf (store_tables collapse).  `git log main..lane/honing-code` lists them.
Before/after renders kept at `/tmp/honing-render/{before,after}/` (tables.md, tables.json, l4l.md, l4l_rt.md; `cmp` all identical).

## What landed, per item

1. **evict / fetch --path / fetch --list** — `store/evict.py` (new), `store/cli.py` (`evict`, `fetch --path GLOB [--path ...] --list [--json]`),
   `store/local.py` (`fetch(paths=)`, `listing()`, `select_files()`).  A store blob is evicted only when EVERY artifact holding it has a
   remote replica with `verified_utc` (PRESERVED), the local object has the manifest's size, and it is >= `--min-mb` (default 1);
   largest first until `--target-free-gb` is free.  Never touched: unverified/pending blobs, `labels/`, `manifests/`, `attempts/`,
   `catalog.sqlite`.  `trees/` (materialised cache) is cleared whole unless `--keep-trees`.  `--runs` also evicts big files from
   finished, quiet (>30 min) run dirs whose `run_files` artifact is PRESERVED and whose bytes still hash to it, leaving
   `run-files.evicted.json` with the restore command.  Prints every blob/file; `--json`.  `has_local`/`where` report evictions honestly;
   `_resolve_blob` re-fetches on demand.  Tests: 4 (`test_store_honing.py`: evict store, evict runs, fetch --path/--list, listing json).
2. **Labels durability** — `store/labels_sync.py` (new).  Remote layout `labels/<target dirname>/<sha256 of the canonical assertion>.json`:
   content-named and immutable, so two laptops/pods never overwrite each other and the same assertion from two machines is one key
   (second put = `skipped`).  Local layout unchanged (`labels/<target>/<ts>-<by>[~N].json`, O_EXCL), pulled files are indexed.  `sync()`
   lists the prefix once, pushes local-only, pulls remote-only, idempotent, no catalog state.  CLI `research data labels-sync
   [--push-only|--pull-only|--from-backup ART|--from-dir DIR] [--json]`; `push --pending` also pushes labels (`--no-labels` opts out);
   `reindex --remote` pulls labels first.  `labels-backup/v1` stays readable (`--from-backup` unions the tarball).  Tests: 3.
3. **Catalog schema version** — `index.py`: `PRAGMA user_version` = `SCHEMA_VERSION` (1).  Open: newer catalog -> `CatalogVersionError`
   (CLI exit 3, message names file, both versions, the fix; `RESEARCH_CATALOG_IGNORE_VERSION=1` overrides); older -> forward migration
   step by step (`MIGRATIONS[v]`, one IMMEDIATE transaction; v0->v1 = the `replicas.verified` column fix).  `research data catalog`
   prints version / migration performed / row counts.  Tests: 2.
4. **Vocabulary hygiene** — `store/vocab.py`: canonical candidates `A-GKR`/`B-Ligero`/`SP1`/..., `KEY_ALIASES` (`notes`,`verify_note`->`note`,
   `batch`->`B`, `checker`->`verifier`), `VALUE_ALIASES` (`candidate=A`->`A-GKR`), `REF_KEYS` (`path`, `result_artifact`,
   `constructed_from_attempt`), `canonical_key/value/coerce`.  Writers: `research data label` canonicalises key+value and coerces
   `true`/`false`/ints/floats to real JSON types for bool/int/number keys (warns what it changed; refuses nothing); a ref-like key
   used as a label warns to use `--ref`.  `bench/ledger_to_store.py` writes `note`, `B`, `verifier`, `A-GKR`; its idempotency signature
   accepts old spellings so re-import adds nothing.  Readers: `tables.py` `canonical_label` (+ `store_tables.py`) accept every spelling
   ever written.  `research data vocab-check [--strict] [--json]` (new, `store/vocab_check.py`) reads the assertion FILES (the catalog
   stores every value as text) and reports unknown_keys / alias_keys / alias_values / string_typed / off_enum / ref_keys / unreadable.
   Existing labels untouched.  Tests: 4 new + `test_store_vocab.py` updated.
5. **`data pull` with thousands of files** — `store/cli_prov.py`: blob paths go to `tar -T -` on stdin (never in the ssh argv), in batches
   of `PULL_BATCH_FILES`=4000 / `PULL_BATCH_BYTES`=512 MiB by manifest sizes, streamed extraction (`r|`), blobs already local are hard-linked
   not fetched, staged tree built with links under the store's `scratch/`, sha256 per blob on arrival unchanged.  On-disk layout identical.
   Measured (laptop, fake ssh = local shell, 10 000 x ~10-byte files): pull_artifact 16 s = 4.7 s bsdtar (the remote's cost) + 6.3 s
   `put_artifact` (hash + write_once) + 4.4 s links; 3 tar round trips; the old one-argv form would have been 850 kB of argv.  Tests: 2
   (10k synthetic tree + batching), plus the existing prov pull test updated to assert the stdin form.
6. **Dead pod** — `pods/runpod.py`: `PodError(code, pod_id)` replaces `SystemExit` in `_request`/`wait_ssh` (the standalone `runpod` CLI
   still exits with one line).  `remote.pod_target` -> `Refused("pod <id> (machine <name>) no longer exists on runpod (HTTP 404: terminated?)")`,
   also for API-down (URLError) and missing config.  `research run --on <dead>` exits 3 with that line, no traceback, run recorded as
   `refused`; `data pull/fetch` print it and exit 1.  `pods/part.check_pod` catches `PodError`.  Tests: 1 (covers all paths).
7. **Multipart > 5 GiB** — `store/remote_s3.py`: `put()` dispatches above `single_put_max` to `put_multipart()`: `POST ?uploads`, one
   `PUT ?partNumber&uploadId` per `part_size` (256 MiB, grown in whole MiB so parts <= 10 000; every part but the last equal, as R2
   requires; `PART_JOBS`=4 in flight), `POST ?uploadId` complete, `DELETE ?uploadId` abort on any failure.  The service's multipart ETag must
   equal `md5(md5(part_i)...)-n` computed locally (`multipart_etag`); a later HEAD is the same check (`verified: etag-multipart`); a part
   whose ETag != its MD5, or a file changed mid-upload, aborts.  Sidecar `<key>.parts.json` (`research/parts/v1`: part size, per-part
   sha256/md5, whole sha256, etag).  `push`/`verify` no longer refuse big blobs (`verify` reads back streamed).  Pure helpers unit-tested
   (`choose_part_size`, `plan_parts`, `multipart_etag`, `parts_of`, `hash_parts`, `parts_sidecar`); end-to-end against the in-process
   `FakeS3` HTTP server, which now speaks multipart.  No boto3 (the remote is hand-rolled SigV4 over urllib; the credentials policy already
   grants the multipart actions).  Tests: 3.
8. **`where` parallel** — `LocalStore.where(jobs=16)` HEADs manifest + blobs in a bounded pool; `missing` count.  Tests: 1.
9. **store_tables vs tables** — `store_tables.py` now reads `tables._Label` (one assertion shape, `path` added as optional), `tables.RANK`
   (one class order; `COMPONENT`, the ledger's class, added at the bottom of `tables.RANK` -- previously the two modules ranked classes
   DIFFERENTLY: tables had NO_PROOF < ARITHMETIC_DIAGNOSTIC and no COMPONENT; store_tables had ARITHMETIC_DIAGNOSTIC < COMPONENT <
   NO_PROOF), `tables.canonical_label`, and `tables._redteam_ceiling(by_glob=)` for the audit-event policy.  Own to store_tables: the
   catalog SQL, `_value` (undo scalar_text), file-order sort, `lane_row`, the ledger diff.  **Before/after render, byte-identical**:
   Table 1-3 markdown (sha256 74e44375cac2aa05…) and JSON, and the like-for-like table with and without `--proof-class-by 'red-team-*'`,
   rendered from a /tmp copy of the store's metadata (objects/ symlinked read-only) with main's code (`git archive main`) vs the lane.
   Tests: 1 new (`test_store_tables_shares_the_label_semantics_of_tables`).

## COORDINATOR RUNBOOK (run only once all writers are idle; dry-run first; in this order)

~~~
cd ~/projects/verity                                   # after merging lane/honing-code into main
uv run pytest tools/research backends/numerical/tests/bench -q

# 0. catalog: the FIRST command run with the merged code migrates ~/.research/store/catalog.sqlite v0 -> v1 (adds nothing but
#    user_version; the replicas.verified column, if present, is handled).  Do it explicitly, alone:
uv run research data catalog                          # expect: "schema v1 (code v1); migrated v0->v1 on this open"; run again: "current"
#    pre-merge worktrees keep working (they never read user_version).  A worktree on NEWER code than the catalog migrates it; a
#    worktree on OLDER code than a future catalog gets exit 3 "catalog is v2, this code reads v1" instead of a traceback.

# 1. vocabulary audit (read-only) -- what is off the vocabulary today is in "store findings" below
uv run research data vocab-check                      # exit 0 always; --strict exits 1 when anything is off; --json for the full list

# 2. labels to R2 (idempotent, content-named keys, nothing is ever overwritten), then union anything a pod pushed
source <R2 credentials>
uv run research data labels-sync --push-only --json | tee /tmp/labels-sync-push.json
uv run research data labels-sync                      # both ways; exit 1 only if a remote key's bytes do not hash to its name
uv run research data labels-sync --from-backup art:246aae6f88aac808a84d0dc0e8cf00e205bd5f913ff679f9877f3b300a85ee52   # optional: interim backup (adds 0 if nothing was lost)
#    from now on `research data push --pending` carries labels too (on each pod before it dies).  `reindex --remote` pulls labels first.

# 3. eviction (dry-run first).  Expect little: only ~0.7 GB of objects/ is PRESERVED-evictable today (see findings); ~/.research is 4.2 GB total.
uv run research data evict --target-free-gb 40 --dry-run             # store blobs + trees/ cache; exit 1 when the target is unreachable
uv run research data evict --target-free-gb 40 --dry-run --runs      # + finished, quiet run dirs under ~/.research/runs (2.7 GB)
uv run research data evict --target-free-gb 40 --runs                # real; prints each blob/file; --json
uv run research data fetch <run-files art> --list                    # evicted files list as `remote`; `--path 'rep1/*'` restores a subtree

# 4. relabel corrections (append-only: a correction is a NEW assertion by the coordinator; `research data label` now writes canonical
#    key/value/type, so these land clean).  Suggested, from the audit:
uv run research data label r20260922-181917-0877 proof_class NON_ZK_PROOF --by coordinator --ref <fp8-proof report>   # x5 rows written `non-zk` by fp8-proof
uv run research data label r20260922-183412-7a35 proof_class COMPLETE_ZK_BACKEND --by coordinator --ref <...>          # `zk-fiat-shamir` -> the class it meant (check the report first)
#    `verified=ligero-verify` (31, b-sweep) / `verified=python-live` (3): decide whether these mean `accepted`; if so one label each by the coordinator.
#    String-typed bools/ints (399 files) need NO relabel: every reader (tables.py, store_tables, vocab.canonical) coerces on read.
uv run research data vocab-check --strict             # re-audit
~~~

## Store findings (read-only; from a /tmp copy of manifests/attempts/labels/catalog taken 06:40Z)

- Catalog: `user_version` 0 (will migrate to 1), 2095 artifacts, 675 attempts, 6406 labels, 2088 remote replicas ALL with `verified_utc`
  (`replica_checks` 1035).  1837 artifacts flagged local (0.50 GB by manifest bytes) but `objects/` holds 1.5 GB: ~1 GB of objects belongs to
  artifacts flagged `local=0` or to no catalog artifact -- `reindex` would refresh presence; worth a look before evicting.
- Eviction potential is small: dry-run says 55 blobs / 0.68 GB evictable now, 0.40 GB held back (below 1 MB or not fully verified), `trees/` empty.
  The disk (Data volume 99% full, 6.3 GiB free at 06:45Z) is NOT `~/.research` (4.2 GB: store 1.6, runs 2.7).  Eviction will not fix the laptop's disk.
- `vocab-check`: 866 of 6406 assertion files off the vocabulary:
  - unknown keys (202): `same_device` 46, `sweep` 36, `lane` 23, `threads` 22, `axis` 19, `stage` 16, `milestone` 8, `self_proved` 6, `dtype` 5,
    `superseded_by` 4, `accumulate`/`native_peak`/`verified_by_python_only` 3 each, `encoder`/`kind`/`outcome` 2, `anomaly`/`replicate` 1 --
    mostly b-sweep, b-verify-par, fill-a100, b-hopper.  Either add to `vocab.py` or leave (they are harmless to the tables).
  - alias keys (158): `verify_note` 131 (verify, auth-included), `batch` 11, `checker` 11, `notes` 5 (red-team-zk).  alias values: `candidate=A` 62.
  - string-typed (399): `independently_verified` 90, `zk` 104, `model_agrees` 39, `breakthrough` 7 as the words; `B` 32, `K` 31, `jobs` 22 as strings;
    `overhead`/`seconds_per_vu` 30 each, `verifier_seconds` 14 as strings.  All coerced on read by every reader now.
  - off-enum (40): `verified=ligero-verify` 31 and `python-live` 3 (b-sweep); `proof_class=non-zk` 5 and `zk-fiat-shamir` 1 (fp8-proof, run ids
    r20260922-181917-0877, -182131-1099, -182930-bf16, -183412-7a35).  These are NOT read as any class by `tables.py` (rank -1).
  - ref keys written as labels (5): `path` x3 (h100-bestvsbest, fill-a100), `constructed_from_attempt`, `result_artifact` (fill-a100).
- `proof_class` values in the store: ARITHMETIC_DIAGNOSTIC 39, COMPLETE_HVZK_BACKEND 33, COMPLETE_ZK_BACKEND 43, COMPONENT 100, NON_ZK_PROOF 2,
  NON_ZK_PROOF_DIAGNOSTIC 120, non-zk 5, zk-fiat-shamir 1.

## What remains / caveats

- Multipart is tested against the in-process FakeS3 and pure unit tests only; the first real > 5 GiB push to R2 should be watched
  (`research data push <art> --json`, look for `verified: etag-multipart`).  R2 requires equal-size non-trailing parts (we do that) and a
  5 MiB minimum part (256 MiB).  An aborted upload that could not be DELETEd leaves an orphan on R2 until a lifecycle rule clears it.
- `labels-sync` is tested against `FsRemote`; against R2 it uses only `list/put/get/head`, all already exercised by `push`.
- `pull` measurement is against a local shell, not ssh; over ssh the batch round trips (3 per 10k files) dominate less than the transfer.
- Table 2 byte-identity was checked on the store as of 06:40Z; the catalog migration does not touch any row the tables read.
- Not done: nothing from the list.  Not attempted: a `vocab.py` entry for the 18 unknown keys (a vocabulary decision, not code).

## Anything wrong in the spec

- "evict local blobs that are known to be on R2 (`remote=1`)": `artifacts.remote=1` alone is presence, not verification; I required a remote
  replica with `verified_utc` (PRESERVED, README §7) -- stricter than asked, and the reason only 0.7 GB is evictable.  `--min-mb 0` and a
  `reindex` would widen it; relaxing to `remote=1` is a one-line change in `evict.py` (`_preserved`) if the coordinator wants it.
- Item 7 says "boto3 multipart API": the store's S3 client is hand-rolled SigV4 over urllib (no boto3 dependency), so multipart is the
  REST protocol directly; the docstring's promised `<key>.parts.json` sidecar is implemented as designed.
- Item 9 named `python -m verity_numerical.bench.tables` as the Table 2 entry: correct (`--root <store> --format md|json`); `store_tables`
  is the like-for-like table, which I also checked.  Rendering against the real store with the merged code MIGRATES its catalog on open
  (item 3) -- hence the /tmp copy for the read-only check; the coordinator's first run does the migration deliberately (runbook step 0).
- The `~/.research/store` catalog held `user_version` 0 and the current schema already (the `replicas.verified` column story from the spec
  is handled by the v0->v1 step either way).
