---
lane: research-papercuts
to: coordinator
kind: ready
branch: lane/research-papercuts
tip: 77025d05
base: origin/main@0b0768ed (unchanged at 07:42Z; `git merge-tree` clean)
---
# research-papercuts ready: lane/research-papercuts @ 77025d05 (r21 close-out papercuts 1–6 + source shipping)

Seven commits, one per item, all pushed. Only `tools/research` is touched (20 files, +1171/−140). No overlap with ops-tools' files
(`research notes`, `pod_bootstrap.sh`, `pods health`). Not merged.

## Fixes
1. **Published FAIL verdict → terminal `done`, outcome FAIL** (9c908309). `research run` passes `<run dir>/outputs.json` as the
   check record. `classify.read_check_record` reads either a `verdict` document or the published `meta.outcome` in outputs.json
   (NOT_RUN or no outcome counts as no verdict). When a non-PASS verdict was published and the process exited on its own,
   `tele run` records `done` plus `outcome`, classed WORKLOAD_CHECK_FAILED, not UNKNOWN_EXIT. A signal death stays `failed`, and
   a timeout stays `cancelled`. The outcome appears in the list, `inspect`, the summary line and the attempt manifest's status.
   Classifier 0.1.4.
2. **Drain names the failing check** (25d4d155). `preserved.failures()` produces one entry per failing leg: the manifest key;
   each unpreserved artifact (output name, art id, first object errors); each label target (count of local-only assertions,
   first missing key). Drain and unpreserved print these under the NOT preserved line, and a refusal counts attempts per leg.
3. **machines.toml retired after a confirmed terminate** (05912a80). `confirm_terminated` treats RunPod GET 404 or
   desiredStatus TERMINATED as confirmation; an API that can't answer doesn't confirm. Only after confirmation does
   `remote.retire_machines` comment out every entry for the pod, under a `# retired: pod <id> terminated (...)` line. The rest
   of the hand-written file is kept byte for byte, re-parsed, and written atomically. A DELETE that answers 404 counts as
   already gone. An unconfirmed terminate keeps the entry and says why.
4. **Targeted label push** (374c2997). `labels_sync.closure_targets` / `push_closure` push and then verify only the assertions
   that one run (attempt, derivation, artifacts) or one art:/drv: id needs. No blob or manifest is touched. New CLI:
   `research data push --labels-only RUN|ART...`. Drain now repairs by itself: for each attempt whose labels leg failed, it
   pushes and re-verifies this store's assertions before deciding. `--no-push-labels` only reports. The rule still holds: a
   preserved Attempt counts as fully preserved only once its labels verify durable.
5. **`data preserved` default no longer reads blobs back** (75b9fcdf). The default `head` mode HEADs each blob in parallel
   (`--jobs`, 32). A multipart ETag is checked against the put's `<key>.parts.json` (sha256, size, part plan, md5-of-md5s-n ==
   ETag). A single-part blob is checked by ETag == local MD5 when held locally, otherwise by present-with-right-size
   (`head-size`). Blobs over 5 GiB are now checked too; they weren't before. `--mode readback` is the explicit full read-back.
6. **mint-credential message** (bdb2a7fc). `--via auto` with neither the parent key nor a token now says: which parent-key
   variables are set or unset (store.toml's names), that CLOUDFLARE_API_TOKEN is unset, and what works: source
   `~/.config/verity/r2.env` and use `--via local`, or set the token for `--via api`. Explicit local/api failures name the other
   mode when it would work.
7. **Source shipping over a slow link** (77025d05). Design: plan, fill, verify, then READY.
   - **Plan.** The launcher sends the archive manifest (path → sha256 plus the executable bit, about 150 KB gzip'd). On the
     machine, `source_ship.py` (stdlib only, run as `python -c`, so it doesn't depend on which research package is there)
     copies every file that any tree under `<root>/src/` already holds by content, including manual or legacy trees. Each
     source is hashed as it is read. It answers with the paths it lacks. The content index lives in `<root>/cache/src-index/`;
     it is derived data, and a stale entry is caught by the copy-time hash.
   - **Fill.** The lacking files go as one gzip'd tar, which is sha256-checked as received before extraction (the r20 guard
     is kept). The timeout is 600 s plus the tar's size at 64 KiB/s.
   - **Verify.** Every file of the partial tree must match the manifest: same path set, same sha256, same executable bit.
     This is stronger than the old archive digest plus file-name set, because it checks the bytes that actually landed.
   - **READY.** READY.json is written, the tree moves into place with a single rename, and the marker is read back, as before.
   - **Measured** on vyv-v2cpu2 with this repo (2892 files, 229 MB). A first ship sends 148 KB plus 107 MB (was 229 MB). A
     one-file change sends 148 KB plus 7.5 KB, with 2891 files reused. At 0.3 MB/s that is under a second instead of about
     13 minutes.

## Tests (vyv-v2cpu2, `tools/research/tests`, python 3.12)
- tip 77025d05: **317 passed, 1 skipped, 5 failed**. main@0b0768ed on the same pod: 302 passed, 6 failed. There are no
  lane-only failures; all 5 also fail on main (the 6th main failure, `test_remote_cwd` concurrent cwd, is flaky and passed here).
- The 5 are environmental:
  - `test_notes::test_relaunch_...` and `test_store_honing::test_evict_...`: ties in directory or size order.
  - `test_store::test_put_fetch_roundtrip_file_and_tree` and `test_store::test_labels_append_only`: root ignores read-only
    modes.
  - `test_pods_connect::test_sync_...[rsync]`: the pod has no rsync.
- New tests: 14, one or more per item (test_cli, test_telemetry, test_pods_drain, test_store_labels_durability, test_store,
  test_remote_ship_source).

## For a decision
- Item 1 edits `telemetry/classify.py` (rule 1 reads outputs.json's `meta.outcome`; classifier 0.1.4). If that module is
  meant to stay frozen, the reader could move to run.py, at the cost of a second copy of the verdict logic.
- Item 5: `head-size` (a single-part blob not held locally) doesn't check content. It relies on every put signing its payload
  sha256, which for a single-part blob is its key, so R2 refuses a body that doesn't hash to it. Content needs `--mode readback`.
- Item 7: the ship now needs the machine's python at ship time (launch-request already needs it), and READY.json's
  `verified` field reads `file-sha256+mode-manifest` instead of `archive-sha256+file-manifest`. Nothing in the repo matches on
  the old string.

## vllm coordinator (eb746331), 07:45Z: decisions
Accept all three: (1) the verdict reader lives in telemetry/classify.py (classifier 0.1.4) -- the classifier is versioned, not frozen; (5) size+existence for non-local single-part blobs is sound because every put is signed with its sha256, and `--mode readback` remains for content; (7) pod python at ship time is already a launch requirement. Ready to merge from our side.
