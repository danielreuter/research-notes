---
id: r21-infra/store-core/20260922T1735Z-report-store-core
campaign: r21-infra
lane: store-core
kind: report
status: closed
repo: verity-main@7444636
---

# store-core: storage half of `research.store` (lane report, 2026-09-22)

Branch `lane/store-core` in worktree `/Users/danielreuter/projects/verity-main-wt/store-core`, based on `main` = a0f0eb9
(the spec commit). Final SHA **7444636** (4 commits, not pushed). `main` has since moved to a966615 (hygiene/notes-migration
merge + `tests/test_repository.py` gates); this branch touches only files the gates allow (two `README.md`, `.py`), so it
merges without conflict on the changed paths.

## Files

Added under `tools/research/src/research/store/`: `__init__.py`, `canon.py`, `ids.py`, `model.py`, `kinds.py`, `local.py`,
`index.py`, `remote.py`, `remote_s3.py`, `cli.py`. Added `tools/research/tests/test_store.py` (25 tests, ~0.8 s).
Edited: `tools/research/src/research/cli.py` (dispatch `data` + one docstring line), `tools/research/README.md` (layout line,
commands line, a `research data` section), `tools/research/src/research/store/README.md` (spec reconciled, see below).
Not created: `env.py`, `tool.py`, `derivation.py`, `attempt.py`, `tools_registry.py`, `cli_prov.py`, `fixtures/artifacts.json`.

## Tests

`uv run pytest tools/research -q` → **84 passed, 1 skipped** (baseline before this lane: 59 passed, 1 skipped; the skip is
pre-existing). `test_no_packages_import` passes; the package is stdlib only (`sqlite3`, `hashlib`, `hmac`, `urllib`,
`tomllib`, `xml.etree`). Coverage as asked: canon determinism/rejections; id stability; put/fetch round trip for file and tree
(bytes + paths); idempotent put; snapshot dedup identity; labels append-only + history order + `by` glob; attempt write-once;
index rebuild == incremental (delete `catalog.sqlite`, reindex, identical rows in every table); FsRemote push → delete local →
fetch from remote → PRESERVED, plus same-size tampering detected by read-back; repo replica map verified + mismatch fallback
with warning + NotFound wording; CLI smoke for every command through `main([...])` and through `research data …`; SigV4
against all four AWS documented vectors (GET object with Range, PUT `test$file.text` with payload, `?lifecycle`,
`?max-keys=2&prefix=J`); S3Remote plumbing (path-style URL, signed payload hash, HEAD 404, list-type=2 paging, size
conflict, oversize → NotImplementedError) against an in-process fake bucket.

## Public API as implemented

~~~python
research.store.local.LocalStore(root: str | PathLike | None = None, *, config_path=None, repo: Path | None = None)
  .root: Path            .index -> Index (lazy)        .remote -> Remote | None (lazy; ConfigError if configured but unusable)
  .repo -> Path | None   .replica_map() -> dict[str, str]
  put_artifact(kind: str, meta: dict, refs: dict | None = None, *, file: Path | None = None, tree: Path | None = None) -> str
  put_manifest(m: ArtifactManifest) -> str                 # blobs must already be in objects/ (used by snapshot)
  get_manifest(art_id: str) -> ArtifactManifest            # local, else remote (cached); NotFound
  has_local(art_id: str) -> bool                           # manifest + every blob present
  fetch(art_id: str, to: Path | None = None) -> Path       # file: object path, or copy at to/<name> (to a dir) or to; tree: to or trees/<hex>/
  where(art_id: str) -> list[dict]                         # [{"location": "local"|"repo"|"remote", "present", "verified_utc", "path"|"remote"|"configured": False, ...}]
  put_attempt(doc: dict) -> None                           # write-once; same content no-op; AttemptExists otherwise
  get_attempt(run_id: str) -> dict | None                  # local, else remote (cached), else None
  push_attempt(run_id: str) -> None                        # upload attempts/<id>.json (for §10 step 4)
  add_label(target, key, value, by, ref=None, ts=None) -> Path
  labels(target, key=None, by_glob=None) -> list[Label]    # sorted by ts, then file name
  snapshot(name: str, members: list[str], note=None, query=None) -> str
  verify(art_id: str) -> dict                              # {"id", "preserved", "remote", "checked", "errors", "verified_utc", "reason"?}
  push(art_id: str, preserve: bool = True) -> dict         # verify report (preserve) or {"pushed": True, "preserved": None}
  reindex(remote: bool = False) -> dict                    # {"artifacts", "attempts", "labels"} counts
  artifact_ids() / attempt_ids() -> list[str]; object_path/manifest_path/attempt_path/labels_dir(...) -> Path; close()
errors: StoreError > NotFound, AttemptExists, IntegrityError   (research.store.local)
        RemoteConflict, ConfigError                            (research.store.remote)
module helpers: store_root(), find_repo(), sha256_file(), object_key/manifest_key/attempt_key(), write_once(dst, bytes|Path)

research.store.index.Index(path)
  index_artifact(manifest_doc, art_id, local=None, remote=None, repo_path=None)   # None keeps the current flag
  index_attempt(doc); index_label(label: Label | dict, path); set_presence(art_id, *, local=None, remote=None, repo_path=None)
  set_replica(art_id, location, verified_utc, detail=None); rebuild(artifacts, attempts, labels) -> counts
  artifact(art_id) -> dict | None; artifacts() -> list[dict]; attempt(run_id) -> dict | None
  attempts_by_reuse_key(key) -> list[dict]; attempts_by_derivation(drv) -> list[dict]; attempts_by_output(art_id) -> list[str]
  select_artifacts(kind=None, where: dict[str, str] | None = None, label: tuple[str, str] | None = None, attempt=None, tool=None, derivation=None) -> list[dict]
  labels(target, key=None) -> list[dict]; replicas(art_id) -> dict[location, {"verified_utc", "detail"}]
  sql(query, params=()) -> list[tuple]; sql_with_columns(query, params=()) -> (cols, rows)   # read-only ?mode=ro connection
  flatten(obj) -> [(dotted_key, text)]  (module function)
artifact rows: {"id", "kind", "bytes", "payload_type", "manifest", "local", "remote", "repo_path"}; attempt queries return the documents.

research.store.canon: check(obj), dumps(obj) -> bytes, loads, sha256(obj) -> hex, sha256_bytes(b)
research.store.ids: art_id(manifest|dict), drv_id(doc), is_art, is_drv, is_run_id, is_sha256, hex_of, target_dirname, kind_of_id
research.store.model: ARTIFACT_SCHEMA, ATTEMPT_SCHEMA, LABEL_SCHEMA, META_MAX_BYTES, ATTEMPT_KEYS, utc_now();
  TreeFile(path, sha256, bytes); Payload(type, sha256, bytes, name=None, files=None) .file()/.tree() ctors, .blobs(), .to_doc()/.from_doc(), .errors();
  ArtifactManifest(kind, meta={}, refs={}, payload=None, schema=...) .id, .canonical(), .blobs(), .errors(), .validate(), .to_doc()/.from_doc();
  Label(target, key, value, by, ts, ref=None) .to_doc()/.from_doc()/.validate(); attempt_errors(doc) -> list[str]; validate_attempt_doc(doc) -> doc
research.store.remote: Remote (Protocol: put/get/head/list/describe), FsRemote(root), config_path(), load_remote(path=None) -> Remote | None
research.store.remote_s3: S3Remote(endpoint, bucket, access_key, secret_key, region="auto", timeout=120); pure signer functions
  uri_encode, canonical_query, canonical_request, string_to_sign, signing_key, signature, sign_headers; EMPTY_SHA256, SINGLE_PUT_MAX
research.store.kinds: KINDS: dict[str, str] (9 kinds of §11), KIND_RE, is_kind(s), is_known(kind)
research.store.cli: COMMANDS: dict[str, Callable[[list[str]], int]] (put show where fetch verify select snapshot labels label reindex sql),
  main(argv) -> int; tail of module merges `from .cli_prov import COMMANDS` when importable.  research/cli.py dispatches `data`.
~~~

## Spec deviations / decisions (all written into the store README)

1. **§3 layout** gains `trees/<hex>/` (LOCAL ONLY): where `fetch ART` without `--to` materialises a tree payload. A file payload
   fetched without `to` returns its read-only object path (no copy). Blobs/manifests/attempts are written temp + hard-link and
   chmod 0444, so "never overwritten" is enforced by the filesystem, not by convention.
2. **§5** gains `replicas(id, location, verified_utc, detail)`; it is the one table `reindex` keeps (a verification is a
   remote round-trip, not a local fact). `remote` on a plain `reindex` is restored from it, so pushed-ness survives rebuilds.
   Flattening rules and the `--where`/`--label` text comparison are spelled out.
3. **§8 label file names**: compact ts (`20260922T112029Z`), `by` restricted to `[A-Za-z0-9._-]`, `~N` suffix on a same-second
   collision by the same asserter (`~` sorts after `.`, so history order survives). `labels TARGET` default view is the latest
   assertion per (key, by); `--history` is every assertion in ts order. `label … --value-json` parses VALUE as JSON.
4. **§7**: a `[remote]` table that is present but unusable (unknown type, missing field, credential env vars unset) is a
   `ConfigError`, not "no remote" — a broken vault must not look like local-only. `region` is optional (default `auto`).
   `push` refuses without a remote; `verify` reports `preserved=False, reason="no remote configured"` without raising.
   The repo replica map supplies bytes only (manifest must resolve locally or remotely); bytes arriving from repo or remote
   are hashed against the manifest before entering `objects/` (`IntegrityError` on remote mismatch; repo mismatch warns and falls
   through). Remote key `describe()` was added to the Protocol for `where`.
5. **§2**: tree rules made explicit (no `.`/empty components, no duplicates, no file-and-directory clash, `bytes` = sum, empty
   tree legal); `payload.name` must be a bare file name.
6. **§4**: `validate_attempt_doc` requires all 16 top-level keys of §4 present; `reuse_key`, `closure`, `cost`, `telemetry`
   may be `null`; `tool.name` str, `derivation` a `drv:` id, `inputs`/`outputs` values `art:` ids, whole doc canonicalisable.
   (store-prov: include every key, `null` where unknown.)
7. **§9 CLI**: `--store ROOT` on every command; `select --ids`; `verify` and `put --preserve` exit 1 unless PRESERVED (id still
   printed); `snapshot --select` takes the rest of the line as select flags and records them as `meta.query` (so a
   query-frozen snapshot differs from an explicit member list); `show DRV` lists attempts with that derivation.
8. **S3 multipart > 4 GiB**: `NotImplementedError` from `put`; the sidecar design (`<key>.parts.json` with per-part sha256,
   256 MiB parts) is noted in the module docstring and README. `verify` reports objects ≥ 4 GiB as unverifiable for now.
9. `S3Remote` uses an env-only `ProxyHandler` opener: the default `urlopen` consults macOS `_scproxy`, which leaves a system
   thread behind and made the telemetry fork tests warn.

## Left out / notes for integration

- No `fixtures/artifacts.json` in the repo (optional; would need a real fixture registered — its manifest still has to live in a
  store or remote, so registering one is best done once a remote exists). Reading/verifying the map is implemented and tested.
- Labels are local only (no `push` of `labels/`); `reindex --remote` lists `manifests/` and `attempts/` only.
- Live R2 untested (no credentials); the signer matches the AWS vectors and the HTTP plumbing is exercised against a fake bucket.
- `LocalStore.repo` auto-detects from `$RESEARCH_REPO` or the nearest ancestor of cwd with `fixtures/artifacts.json`;
  store-prov's `attempt publish` should pass `repo=` explicitly when it knows the checkout.
- Hooks for store-prov: `put_attempt(doc)` + `push_attempt(run_id)` for §10 steps 3–4; `Index.attempts_by_reuse_key` /
  `attempts_by_derivation` for `lookup`; `cli.COMMANDS.update(cli_prov.COMMANDS)` happens automatically when `cli_prov.py` exists.
