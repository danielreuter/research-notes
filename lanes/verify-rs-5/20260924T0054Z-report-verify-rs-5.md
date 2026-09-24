---
lane: verify-rs-5
kind: report
created: 2026-09-24T00:54Z
status: final
---

CHECKPOINT a87edaa0 (01:10Z) [final] FINAL a87edaa0 (pushed): Rust --session takes the RO verifier's whole store (subbatches-only records = 0 batches; neither key still an error); laptop cargo test --release 98 pass + 1 ignored (coordinator-approved); whole-store claims 5aa5 ZK 2^-128.435, a1a0 ZK 2^-126.422, f283 non-ZK 2^-125.416 = c-only values; art:f2f27f16 art:d04ee43a; all predecessor handoffs named
CHECKPOINT a87edaa0 (01:09Z) [final] FINAL a87edaa0 (pushed): Rust --session takes the RO verifier's whole store (subbatches-only records = 0 batches; neither key still an error); laptop cargo test --release 98 pass + 1 ignored (coordinator-approved); whole-store claims 5aa5 ZK 2^-128.435, a1a0 ZK 2^-126.422, f283 non-ZK 2^-125.416 = c-only values; art:f2f27f16 art:d04ee43a
CHECKPOINT a87edaa0 (01:07Z) [open] 01:10Z a87edaa0 (pushed): laptop cargo test --release 98 pass + 1 ignored (83 lib + 9 cli + 6 session; new subbatches/neither-key asserts pass); binary sha256 4bdc3ad8. Whole RO store (5 c + 45 s, art:d04ee43a) --session reruns, pinned keys: 5aa5 ZK 2^-128.435 (3 batches), a1a0 ZK 2^-126.422 (3), f283 non-ZK 2^-125.416 (6) = c-only claims; art:f2f27f16. Next: handoff to coordinator, FINAL
CHECKPOINT a87edaa0 (01:06Z) [open] 01:07Z acted on coordinator 01:15Z handoff: laptop cargo test --release approved (one-off), FINAL by 02:30Z, hand back to lanes/coordinator. Running vrs5.sh on laptop @ a87edaa0: cargo test + build --release, then 3 whole-store --session reruns (store art:d04ee43a)
CHECKPOINT none (01:03Z) [blocked] 01:05Z still blocked on a build place (coordinator asked 01:03Z). Acted on relation-3's 01:05Z handoff (pod terminated at its FINAL; dumps on laptop ~/lr3-art = art:ef6b9392). Fresh read-only RO store copy 01:02Z: 50 sessions (5 c, 45 s, all recorded) art:d04ee43a; no s-record value equals a recorded STMT; batches per STMT: f283 6, a1a0 3, 5aa5 3 -> expected claims unchanged. Fix @ 1ece0c34 unbuilt.
CHECKPOINT 1ece0c34 (01:01Z) [blocked] 01:03Z 1ece0c34: subbatches-as-zero-batches fix + tests committed, NOT built: relation-3's pod vy-ligerito-relation-2 terminated ~01:00Z during my sync (404). Asked coordinator (lanes/coordinator/20260924T0103Z-handoff-from-verify-rs-5.md) for laptop-cargo OK or a pod. Meanwhile: RO store JSON pull (read-only)
CHECKPOINT 0e4ef1d1 (00:54Z) [open] 00:55Z start: took over lane/verify-rs-3 @ 0e4ef1d1 (clean). Read contract, inbox (sumcheck-4 00:25Z: LGSC0004 11 coins, no Rust change; relation-3 00:50Z: --session loader gap = my goal). Next: session.rs subbatches fix + tests, build on vy-ligerito-relation-2 /workspace/vrs5

# verify-rs-5: Rust `--session` over the verifier's whole store (records with `subbatches` count as zero batches)

## Handoffs received
* `verify-rs-4/20260924T0025Z-handoff-from-ligerito-sumcheck-4.md` (LGSC0004 default 11 coins at N = 2^30): no wire-format
  change, and `lgsc4.rs` already takes the data-driven header (`MAX_VF = 12`, arity <= 6). Nothing to do for this lane.
* `verify-rs-4/20260924T0050Z-handoff-from-ligerito-relation-3.md` (the `load_sessions` gap): this lane's goal. Done in 1ece0c34.
* `verify-rs-5/20260924T0105Z-handoff-from-ligerito-relation-3.md`: relation-3 terminated its 4090 at its FINAL (01:00Z)
  before it read the coordinator's 00:58Z note; it says the dumps are on the laptop at `~/lr3-art` (= art:ef6b9392, checked
  15/15 files by sha256).
* `verify-rs-5/20260924T0115Z-handoff-coordinator.md`: laptop cargo approved, FINAL 02:30Z, hand back to the coordinator. Done.

Handoffs to my predecessors. The finish check lists them; all were acted on before I started, so nothing is left for this lane:
* `verify-rs-4/20260923T2358Z-handoff-from-ligerito-sumcheck-4.md` (LGSC0004 default 12 coins, no wire change): superseded
  by its 00:25Z note (11 coins). `lgsc4.rs` takes the data-driven header, and the `lgsc0004-underblinded` label exists.
* `verify-rs-4/20260924T0030Z-handoff-from-ligerito-relation-3.md` (the `--zk` keys = verify-rs-4's derivation, gate dumps):
  acted on by verify-rs-4 (00:28Z e1114b4c 10/10 batch; FINAL: all five gate ZK keys and 875f45c5 pinned by derivation).
* `verify-rs-3/20260923T2235Z-handoff-from-ligerito-relation-2.md` (V1 opening layout, fixtures, pins, F11, F5): acted on by
  verify-rs-3 (report 21:55Z-22:36Z: V1 reader, pins, F5 in `batch`).
* `verify-rs-3/20260923T2245Z-handoff-from-ligerito-sumcheck-3.md` and `verify-rs-3/20260923T2300Z-handoff-from-ligerito-sumcheck-3.md`
  (LGSC0004 wire format, fixture, then the new default schedule): acted on by verify-rs-3 (c049225 `lgsc4.rs`, e2037b5 default).
* `verify-rs-3/20260923T2252Z-handoff-from-red-team-ligerito-3.md` and `verify-rs-3/20260923T2309Z-handoff-from-red-team-ligerito-3.md`
  (LGTO0001 reader review; R3-2 framing and R3-3 pad-unit words open in Rust): closed by verify-rs-3 2dfbb90 (R3-2/R3-3) and
  75ec753 (R3-1).
* `verify-rs-3/20260923T2255Z-handoff-from-red-team-leaf-3.md` (H2: unpinned `statement.steps`) and
  `verify-rs-3/20260923T2258Z-handoff-coordinator.md` (does the verifier bind every statement dimension?): answered by
  verify-rs-3 75ec753f. `steps`, K and word widths are bound to the relation constants (test `statement_steps_bound_to_the_relation`).

## Log
* 00:55Z start. Worktree `verify-rs-3` clean at 0e4ef1d1 (verify-rs-4's FINAL, pushed).
* 00:58Z cause: `read_record` (`src/session.rs`) does `s.get("batches")...ok_or("session record: no batches")?`. The kept RO
  verifier's store holds `live.Session` records (ids `s…`, `session.json` = `{"verdict", "subbatches"}`, written by
  `backends/direct/ligero/live.py` `Session`) next to the `live.ChallengeServerSession` ones (ids `c…`, `{"hello", "batches"}`).
  Python `run.py verify_session(--sessions-root)` (relation-3 498f9014) counts `session.json.get("batches", [])` per STMT,
  so a `subbatches` record adds 0 attempts.
* 01:01Z **1ece0c34** `read_record`: `batches` absent and `subbatches` a list -> `Ok(vec![])` (no batch on any statement).
  Every other path is unchanged: a record with `batches` is read as before, even if it also has `subbatches`; a record with
  neither key (or a `subbatches` that is not a list) still errors "session record: no batches". `attempts()` still counts
  every recorded batch on the statement over the records given, and the whole-store rule (0e4ef1d1) is untouched. Tests:
  - `tests/session.rs` `reads_the_verifier_record_format`: `subbatches`-only -> empty; `batches` + `subbatches` -> the
    batch; `{"hello":{}}` and `subbatches: {}` -> "no batches".
  - `tests/cli.rs` `batch_with_verifier_sessions`: a scratch store = the fixture's four real `c…` records plus a real `s…`
    record (new fixture `fixtures/session/subbatch_record/s20260923T210807Z-dac0`, 37 KB, from art:ef6b9392's copy of the
    RO store) must give the c-only store's claim 2^-126.030 ("4 recorded batch(es)"); adding a neither-key record must fail
    with "session record: no batches".
* 00:59Z-01:00Z `research pods sync vy-ligerito-relation-2 ... --dest /workspace/vrs5` failed: "connection closed by remote
  host"; `pods get 52tgms6kjphi6k` -> 404. Relation-3 had terminated the pod at its FINAL. Asked the coordinator
  (`lanes/coordinator/20260924T0103Z-handoff-from-verify-rs-5.md`) for either an OK to run cargo on the laptop or a pod.
* 01:02Z fresh read-only copy of the RO verifier's store (pod `vy-live2b-verifier-ro`, `/workspace/live/sessions`; verifier
  `serve --listen 0.0.0.0:7000` running, not touched): `tar` of `hello/session/verdict.json` + `index.jsonl` only, 151
  files, all match the pod-side `sha256sum` -> **art:d04ee43a** (dataset-snapshot/v1, preserved). 50 sessions: 5 `c…`
  (only `batches`), 45 `s…` (only `subbatches`), all with a record (no open session). The store is unchanged since
  relation-3's 00:40Z copy (same 5 + 45).
* 01:04Z what the whole-store run must give, read from that snapshot: recorded batches per STMT digest: 628a1870 = 6
  (c8a8 x3 + f283 x3), 0b42eb08 = 3 (a1a0), 59ae8873 = 3 (5aa5), 86911ac4 / 85126ad7 = 2 each (da81); no 64-hex value in
  any `s…` record equals any of them. So the claims should stay at 2^-(128.001 - log2 6) = 2^-125.416 (f283),
  2^-(128.007 - log2 3) = 2^-126.422 (a1a0), 2^-(130.020 - log2 3) = 2^-128.435 (5aa5). The store's JSON is also
  plain (no NaN/Infinity, valid UTF-8), which matters because `read_record` parses the whole record before looking at its keys.
* Run script: `evidence/pod-scripts/vrs5.sh CRATE TARGET DUMPS STORE OUT` (cargo test + build --release, binary sha256,
  the three `batch --dir … --session STORE` runs).
* 01:05Z `verify-rs-5/20260924T0115Z-handoff-coordinator.md`: laptop `cargo test --release` for this crate approved as a
  one-off exception to §7 (no pod; `cargo clean` not required; FINAL moved to 02:30Z; hand back to `lanes/coordinator/`).
* 01:06Z a87edaa0: reflowed the `load_sessions` doc comment (no code change). Ran `vrs5.sh` on the laptop at a87edaa0 (clean
  tree) in 20 s, incremental build:
  - `cargo test --release`: **98 pass + 1 ignored** (83 lib + 1 ignored, 9 cli, 6 session). The counts are the same as at
    0e4ef1d1 because the new asserts sit inside `batch_with_verifier_sessions` and `reads_the_verifier_record_format`,
    and both pass.
  - release binary `backends/ligerito-verify/target/release/ligerito-verify` (laptop, macOS arm64), sha256
    `4bdc3ad884a3ee72df6b8e35402615a2730727b0a48a802f34f233d833d4924b`.
  - **whole-store reruns**, `batch --dir ~/lr3-art/<dump> --session /tmp/vrs5/ro-store/sessions` (all 50 sessions of
    art:d04ee43a), pinned keys only (no `--allow-any-key`):

    ~~~text
    dump (art:ef6b9392)        session                  sumcheck / key                  union       batches  claim
    live-7f35c223/dump_ro-zk   c20260924T003626Z-5aa5   LGSC0004 / 875f45c5 (da27387b)  2^-130.020  3        2^-128.435
    live-6dda159a/dump_ro-zk   c20260924T003234Z-a1a0   LGSC0004 / 875f45c5 (da27387b)  2^-128.007  3        2^-126.422
    live-6dda159a/dump_ro      c20260924T003303Z-f283   LGSC0003 / da27387b             2^-128.001  6        2^-125.416
    ~~~
    All three authenticated, and the claims equal relation-3's c-only values (0e4ef1d1 over symlinks to the 5 `c…`
    sessions, and Python `--sessions-root`). Before the fix, the same `--session` path panicked (relation-3, 00:50Z).
  - JSONs, logs, cargo test log, summary and script: **art:f2f27f16** (verification-verdict/v1, preserved; refs store
    art:d04ee43a, dumps art:ef6b9392). Pushed origin `lane/verify-rs-3` 0e4ef1d1..a87edaa0.
* 01:11Z handback `lanes/coordinator/20260924T0111Z-handoff-from-verify-rs-5.md` (relation-3 is final). kb: new
  `kb/live-verifier.md` (the store's two record kinds, the read-only copy recipe, which verifier accepts the whole store).

## FINAL (01:11Z)

~~~text
tip: lane/verify-rs-3 @ a87edaa0 (base lane/verify-rs-3@0e4ef1d1)        merge-with: none
known-failures: none    pod: none (relation-3's 4090 was terminated by relation-3 at 01:00Z; nothing of mine kept); $0
artifacts: art:f2f27f16 art:d04ee43a
~~~

**Change** (1ece0c34; a87edaa0 only reflows a doc comment; pushed): `session::read_record` reads a record with `subbatches`
and no `batches` (`live.Session`, the `s…` ids) as zero batches on every statement, as Python `run.py verify-session
--sessions-root` does. So `ligerito-verify verify|batch --session <store>/sessions` now takes the verifier's whole store,
which is the R3-10 input. A record with `batches` is read as before (even alongside `subbatches`). A record with neither
key, or with a `subbatches` that is not a list, still errors. R3-7 is unchanged: slots come from the record only, and one
recorded batch authenticates one proof. So is R3-10: attempts are every recorded batch on the statement, and a claim is
made only over a complete store.

**Tests** (laptop, coordinator-approved one-off): `cargo test --release` 98 pass + 1 ignored (83 lib, 9 cli, 6 session).
New asserts: a store of four real `c…` records plus a real `s…` record gives the c-only claim 2^-126.030; adding a
neither-key record fails with "session record: no batches"; `read_record` unit cases. Fixture:
`fixtures/session/subbatch_record/` (37 KB, from art:ef6b9392).

**Real check**, RO verifier's whole store (read-only copy 01:02Z, 5 `c…` + 45 `s…`, art:d04ee43a), pinned keys only:
ZK `c20260924T003626Z-5aa5` **2^-128.435**, ZK `c20260924T003234Z-a1a0` **2^-126.422**, non-ZK `c20260924T003303Z-f283`
**2^-125.416**, all authenticated and equal to the c-only values (art:f2f27f16). Binary:
`backends/ligerito-verify/target/release/ligerito-verify` in the worktree (laptop, macOS arm64), sha256 `4bdc3ad8…d4924b`
(full value in the log). There is no pod build.

**Deviations from the launch message:** relation-3's pod was gone at 01:00Z, so the build ran on the laptop with the
coordinator's OK (01:15Z note), and the store copy and results live in art instead of `/workspace/vrs5`. The handback
went to `lanes/coordinator/` because relation-3 is final. `--keep-pod` was not passed: the binding is pod none, and no pod
exists to keep. No `cargo clean`: the coordinator said it is not required, and the handed-back binary lives in that target dir.

**Left:** nothing on this item. Live `--session` has still been exercised only on fp8-ada (the only relation with live
records). Gotcha for the contract owner: `research data put --preserve` needs `set -a; source ~/.config/verity/r2.env`
first (the hint is only in `~/.research/store.toml`); otherwise it fails with "credentials env vars … are not set".
