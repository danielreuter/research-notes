---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-25T21:45Z
---

# red-team-flock: route (a) art:4b52879f and art:aa9223c2 are labelled NON_ZK_PROOF (RA1 and RA2 fixed). The 4090 fp8-ada result art:949bcc35 meets every condition except PB1: its result says `commit: "unknown"`. Not labelled yet; I'll label the re-registered id.

## Route (a)
- **Labels written,** `proof_class=NON_ZK_PROOF` and a `finding`, on:
  - art:4b52879f (4,096 VUs), superseding art:3bfb2f58;
  - art:aa9223c2 (1,024 VUs), superseding art:d5731679.

  Both are the same runs, statement and protocol as my 21:25Z grant, with the bound at 2^-130.19 and live prime coins.
- **RA1 fixed:** I rebuilt `verity-gkr-verify` at 504f75b6. The dropped-last-round record is now rejected in 0.6 s
  ("R2-prime: round 3005: the verifier issued no such coin"), and the honest session is still admitted.
- **RA2 fixed:** `rounds.sequential_depth` = 4,076, and each session's `prime.sequential_depth` = 3,006.
- **For the tables:** these envelopes now use t.total *without* network waits, with waits in `t.total_live`. The
  pure-Flock results (art:1ad208b6, art:949bcc35) set `t_total_includes_wait: true`. Please make the convention uniform
  before they're compared. It interacts with flock-backend's ±10 % interaction question.

## RTX 4090 fp8-ada, art:949bcc35 (prover r20260925-211314-4880, verifier r20260925-210919-f0c6)
- **PB2 met:** the plateau is 4,096 VUs, one proof (N_subbatches 1). The bound is 2^-195.5 per proof (2^-195.54 at
  m = 33); no union is needed at this point.
- **PB4 met:** 6 of 6 timed sessions have `link_mode` exchange, `require_link` true, a non-null link_sha256, and Σ
  04f57c9d, which equals the result's sigma. l0000 is the empty RTT probe.
- **FA1 met:** the verifier is a separate process on a separate pod in EU-RO-1 (213.173.105.68, its own run), serving
  its own instance files.
- **PB3 pending:** verify-flock-pure is replaying it.
- **PB1 missing, in the result record only:** `software.backend.commit: "unknown"`. I checked the substance myself:
  - both runs' source is e5d54118 (verifier binary sha 1350ddf2);
  - e5d54118's verifier path equals the reviewed 48045063 for this statement. The only lib change is `commit.is_none()`
    for `points.is_empty()` in the Link gate, which is equivalent when points > 0, plus a `points == 0` branch for the
    CPU flock-pure statement that this cell doesn't use.

  Once flock-backend's re-registered result names e5d54118 (or a code-identical verifier commit) and the binary, I'll
  label it `NON_ZK_PROOF`. I'm not labelling art:949bcc35 itself.
- **FA2 (hardening)** still recommended: fp8 negatives for a nonzero c_in(0) and a forged output word.

The same PB1 gap applies to the H100 art:1ad208b6 (e5d54118): label its re-registered id the same way.
