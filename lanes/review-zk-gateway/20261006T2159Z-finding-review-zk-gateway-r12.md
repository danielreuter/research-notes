---
id: review-zk-gateway/20261006T2159Z-finding-review-zk-gateway-r12
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1303@ceb25c35a545188eda36dd4f712898c8da125e5f, pr:1323@7c965ddc57463f9959dd57450c4ddd0143b4a05b, pr:1339@a1adb7a173eedfbee77417596b049dba768bf840]
---

# Red-team round 12: #1303, #1323 and #1339 at zk-gateway's final heads, GRANT

This round relabels the contract chain that round 11 (`note:review-zk-gateway/20261006T1945Z-finding-review-zk-gateway-r11`)
granted at #1303 `0699540a7`, #1323 `638c24ead` and #1339 `04d003c7b`. I checked each claim locally with my own `.lake`;
nothing ran on a pod.

**Verdict: GRANT** at #1303 `ceb25c35a`, #1323 `7c965ddc5` and #1339 `a1adb7a17`. No blocking items.

- **The heads and their history.** Each new head descends from its round-11 head. The interdiffs are +30/−12 over 4 files,
  +33/−14 over 5 and +32/−13 over 5, as claimed. #1323's and #1339's interdiffs carry #1303's four files byte for byte;
  #1339's index lines for `live/PROTOCOL.md` differ only because its own patch edits that file. Apart from those four
  files and the README, no file changed. Each PR's own patch is round 11's plus exactly the README edit: #1323 over
  `ceb25c35a` against `0699540a7..638c24ead`, and #1339 over `7c965ddc5` against `638c24ead..04d003c7b`, compared without
  index lines or hunk offsets.
- **The first round** (`de0f60826`, merged by `8d03f8022` and `6da5692fd`, both with an empty remerge-diff). The
  `PROTOCOL.md` prose at lines 552, 616, 621 and 634 is v1's and agrees with `rec_outer`'s `TopValue`.
  `80-rec-inner.sh`'s line-3 comment says "salted tops", and its line-95 summary counts `tops` and `level0`, which is
  what the v1 record holds. `bash -n` passes. `a56f87cb0` makes line 618 read "its one row committed under a fresh salt".
- **`ceb25c35a` restores the name check.** `rec_vstar.py:250-251` match `8c9a6631d`'s `root()` and `caps()` check lines
  word for word (`8c9a6631d:rec_vstar.py` 218-219 and 231). The remerge-diff of `a83c72890` shows the merge dropping them,
  together with the #1270 side's `root` and `caps`.
- **The check can't be bypassed.** It compares both `public.json` and `private.json` to `RL.TOPS` with `!=`, so any
  other value is refused with the pinned reason, including a missing key, an empty string, a v0 name, v1's name after
  #1320's bump, and a non-string. `opened_top` is called only inside `tops()`. `tops()` is the one reader of the clear
  tops and roots, and it is called from `queries` (V*'s `check`) and from `rec_vstage.py:296`. `rec_outer` takes its
  tops from it. `rec_vstar.py:217` reads only the round counts. `rec_live` writes the name to both files
  (`rec_live.py:508` and `:721`). `rec_inner.py`'s `unsalted` forgery deletes `pub["tops"]` and is now refused by name.
- **The test catches the regression.** The six parameter cases (`public` or `private` × a missing, empty or v0 name)
  pass at `ceb25c35a`: 20 of 20 in `test_rec_vstar.py`. With the two lines removed, exactly those six fail ("DID NOT
  RAISE") and the other 14 pass. I also applied `ceb25c35a` onto the row-v2 fold `a9c858edb`, where `TOPS` is
  `hm96-sha512/row/v2/node-row`, and all 20 pass.
- **#1323's merge and README.** `bbd0303bf` has an empty remerge-diff. `7c965ddc5`'s README sentence holds against the
  store. `r20261006-021550-4e4b` (commit `273017068`, done, rc=0) recorded a `rec/inner-transcript/v1` session at
  `k4096s3` with 2048 instances, and V* accepted it. Its record lists 52 files and no `private.json`, although `sizes.txt`
  shows a 750,017-byte one written on the pod. `firewall_agree.replay` reads the salts from `private.json`, so the
  replay does need it.
- **#1339's merge.** `a1adb7a17`'s one conflict is the README paragraph. Its resolution takes #1323's new sentence up
  to "whose salts the replay needs." and then keeps #1339's "The outer phase: `firewall_outer_agree.py` …" paragraph,
  which, as in round 11, replaces "The outer phase (`firewall.rs`) is not covered yet". Neither side's text is lost.
- **Lean.** No `.lean`, lakefile, toolchain or manifest file changed in any interdiff, and all five `lean-audit.json`
  files are byte-identical to the previous heads'. `lake build flock-firewall` at `a1adb7a17` is up to date.
- **Tests.** `r20261006-210518-2e64` ran at `a1adb7a17` (clean, rc=0) and reports 151 passed and 2 skipped: the Lean
  verifier isn't built for `test_rec_outer`, and `VERITY_FLOCK_INNER_FOLD` is unset for `test_rec_vstage`. Locally, the
  same eleven files plus `tests/test_module_strings.py` give 155 passed and 2 skipped (the same two).

Non-blocking:

- N1. `r20261006-021550-4e4b`'s `public.json` has no `tops` key. Its commit, `273017068`, is on the rec-step3 side,
  which `8c9a6631d` (where `TOPS` and the name come from) is not an ancestor of. So today's V* would refuse that session
  by name even with its `private.json`. The README's sentence is about the replay, which compares only the keys
  `public.json` holds, so the sentence is accurate. A future K=4096 v1 recording should come from a tree that writes
  the name and should declare `private.json` as an output.
- N2. After #1320 bumps `TOPS`, the test's refused names don't include v1's `hm96-sha512/v1/node-row`. The `!=` check
  refuses it anyway, and the v0 case stands for "an older name".
- N3. Round 11's N1 still stands: the fold's row-v2 commits must move the three row-v1 constants of the chain
  (`Flock/Firewall.lean:186` `rowDigest`, `:470` the record's `tops` string, and `firewall_transcript.py:43-45`
  `row_message`).
