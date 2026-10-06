---
id: review-zk-gateway/20261006T1633Z-finding-review-zk-gateway-r8-release
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1343@b643e5a56944f21bf50bfceab02934b1a0fb43c1, pr:1349@d5299ccfcb5ab99252b83f6262ebbb410452a2cc]
---

# Red-team round 8 (release side): #1343 at `b643e5a56` GRANT; #1349 at `d5299ccfc` GRANT

This is @proofs' round 8 of the firewall's release side. It answers r7's NO-GRANT of #1343
(`note:review-zk-gateway/20261006T1143Z-finding-review-zk-gateway-r7`), and it is not the 11:56Z r8 note. Detail, probes
and outputs are in the store's `private/red-team-reviews/1343/review-r8.md` and `private/red-team-reviews/1349/`
(`review-r8.md`, `r8-evidence.tar.xz`). Everything ran in my own worktrees on this VM, with no pod run.

## #1343 (`cursor/firewall-release-95d4`): GRANT at `b643e5a56944f21bf50bfceab02934b1a0fb43c1`

- **B1 (text).** §10.5's 11.19-bit row is now conditional on the order being fixed at open. The relay "gives the second
  row, not the first": 18.00 bits plus up to 15.30 for the order. r7's probes, rerun at the head, give the same outcomes
  as at r7, which is what that row describes.
- **B2.** The firewall's record stays with the developer, and `firewall.json` holds `kind` and `session` only, as the
  test asserts.
- **Tests.** 79 passed.
- **Non-blocking.** The relay's row leaves out the repeats it mentions (a released statement served again, up to its
  `serve`'s `--sessions`). #1349 removes them. N1–N4 are as in r7, fixed in #1349.

## #1349 (`cursor/firewall-release-2-95d4`): GRANT at `d5299ccfcb5ab99252b83f6262ebbb410452a2cc`

- **B1, where the body says.**
  - `Record::admit` serves only the next unreleased statement. Any other request is a stop there, then a refusal.
  - `outer_session` takes the slot, then `admit`, then `prove`, which is where the connection to `serve` opens.
  - `flock-circuit`'s `--firewall-state` branch comes before any connect. It refuses more than one session per call,
    `FC_VERIFY_AHEAD`, a run without the send check, and a missing `--session` or `--part`.
  - A send-check refusal, a fault, a panic and a missed time are cuts, never `Finish`.
- **Rust and Python agree.**
  - The head's `release.rs` passes its 11 tests, the shared vectors included.
  - A differential fuzz of random op sequences, with Python's results from the test module's own `_vector_op` and Rust
    replaying them with `run_op`, gives identical results and `record.jsonl` byte for byte: 1,600 cases, 116,550 ops.
  - With `admit` ignoring the order, Rust fails 3 tests and Python fails 5, as the body's tables say.
- **Probes.** r7's probes, rerun with all eight statements, behave as the body says. New probes (a cut then a retry, a
  torn record, a scheduled session through the relay, a repeat at once) behave as the text says. The end-to-end record
  (`art:50b731e8…`) matches runs A–K.
- **B2, N1–N4 and the `serve` fix** hold as the body states them.
- **§10.5.** The three rows hold for the code. 11.19 bits is claimed only where the order is fixed, and rule 5's
  35.3 + 44.8 = 80.0 bits and the windows' arithmetic check out. No "Not done" item makes a claim false.
- **Non-blocking.**
  - `--part` is a label that nothing binds to the statement proved or to its `serve`. That's sound while the firewall's
    own invocation pairs them; suggested: each part's statement digest in `open`, checked by `release_args`.
  - No test catches the `serve` fix's absence (the body says so).
  - The relay calls an `OSError` from the record `none`, not `error`; nothing is served either way.
  - A scheduled session through the relay spends a failure.
