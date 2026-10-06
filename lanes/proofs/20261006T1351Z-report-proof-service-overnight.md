---
id: proofs/20261006T1351Z-report-proof-service-overnight
campaign: proof-service
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs coordinator), for note:verity-root/20261006T0550Z-report-proof-service-implementation
---

CHECKPOINT none (13:52Z) [open] 6:55 AM PDT FINAL (note:proofs/20261006T1351Z-report-proof-service-overnight): landed #1264 #1258 #1271 #1272 #1253 #1286; granted, priority tiers on node 1 for the next tip #1261 #1273 #1330 #1274 #1283; open (pushed, not ready): #1324 #1340 #1316 #1319 #1257 #1332-#1335 #1270 #1303 #1323 #1339 #1343 #1349 #1315 #1318 #1347 #1284 #1289-#1297 #1307 #1313 #1325 #1326 #1331 #1320 #1350; no strong reason; open: #1339 B1', #1343 r7, #1320 B1, cross-session release decisions and the record contract, inner firewall in Python, D2 D6 D9.

Earlier checkpoints: `note:proofs/20260930T1958Z-report-proofs`.

# Proofs overnight: the proof service, P1–P8 (5–6 Oct)

**Summary.**
- **On main tonight:** #1264 (P5's J-table repair), VBridge A, B1 and B2 (#1258, #1271, #1272), #1253 and #1286.
- **Granted, waiting on node 1:** #1261, #1273, #1330, #1274 and #1283 are red-team granted. Their quick tiers wait on
  vy-nebius-1 with slot priority (the advisor's grant, 6:16 AM PDT). Each tier's client writes its ready mark, and I tell
  @ci for the next tip.
- **No strong-reason report from proofs.** Everything else is pushed as an open PR. Each one's state is below.
- **What held most of the stack back** was the check queue, not the code. The two mig check pods have one slot each, about
  2 h per tier. Research-suite tiers fail there until #1342 lands. Most PRs restacked across the 3:09 AM PDT rename move
  need a new tier at their new head.

## The items

| Item | PRs | State at 14:00Z |
|---|---|---|
| P1 proof service | #1324 (`sampled_proofs.service`: Spec, the public-items rule, Stream; no retries, failure budget), #1340 (TwoStage in a Stream, on #1324) | Pushed. #1324 has no ready mark at `147339ab3`; its tier `r20261006-110153-c9be` is still waiting on vy-mig-check-19. PoUW's served-zk calls it in compute-accounting's #1314 |
| P2 firewall | #1270 (send check), #1303 (lean: `Flock.Firewall.run`), #1323 (the contract, `Flock.Firewall.Contract`), #1339 (outer transcript and public input), #1343 (release side), #1349 (release side in Rust) | #1270 granted at `9cced3479`, but its base (rec-reprice) isn't on main. #1303 granted. #1323 granted in round 9 at `5f2fb2322`; its head `888c56772` follows #1303's rename, and the reviewer is re-checking it as renames. #1339 refused in round 9 (B1′, below); the fix is under way. #1343 refused in round 7 (B1, B2); the fix is under way. #1349 is new and unreviewed |
| P3 fixed outer shape | #1315 (the inner statement padded to a public cap) | Granted; stacked on rec-step3 (#1284) |
| P4 VBridge | C1 #1273, C2 #1274 and #1283; E0–E7 #1289–#1297; V* registers `coef` (gap 3) #1347; the Lean tag for plain SHA-512 leaves #1318 | C1 and C2 granted and in tiers. #1347 granted on #1284, which closes #1261's gap 3. #1318 granted at `f74a2905a`; its restack waits on rec-step3. Pieces D and F are still with the vbridge lane. The escapes answer (05:55Z): none of the verifier lock's 25 `partial def` escapes is on the accept path VBridge concludes about |
| P5 | #1264, #1261, #1257 | #1264 landed 1:12 AM PDT. #1261 (RecursiveSound/ZK) granted at `9c9828557`, tier running. #1257 was ready at `a294e8f5e` before the move; its new head `2f74abe2` needs a new tier. flock-e2e's steps A–D (#1332–#1335) stack on it |
| P6 one hash | inventory `note:one-hash/20261006T0706Z-finding-one-hash-inventory` (37 rows); #1307, #1313, #1325, #1326, #1331 | #1331 granted. #1307 and #1313 have been in mig-pod tiers since 4:12 AM PDT. #1325's and #1326's tiers failed in the research suite's check-slot tests on the mig pods (#1342's bug), not in their own code; both need a new tier. The beacon and BLS deletion (D5) is compute-accounting's #1311 |
| P7 registered row/v2 | #1320 | Not landing tonight: red team B1 is open (below) |
| P8 two-stage, hidden layout | #1316 (the two-stage law in core), #1319 (the driver, on #1324) | #1316 was ready at `cb4574780` before the move; its new head needs a new tier. The hidden layout (`Check.window`, position reads) is not started |
| (tooling) | #1350, `research queue ready --on M --priority` | Opened tonight so a granted tier can join the slot line with priority. The five relaunches used it |

## Open, and not fixed tonight

- **#1339 B1′:** nothing holds the outer phase's order and count. The harness fix comes first: one item sequence across
  honest sessions, each control matching it up to its cut, with a negative test. The limit is stated in live PROTOCOL.md
  §10.4. A public input that carries the outer sequence, in Lean, follows.
- **#1343 B1 and B2, and #1349:**
  - B1: the relay doesn't enforce §10.5's order or completeness. As built, the first row is about 18.0 bits plus the
    order's bits, not 2,336 endings. The fix is the text in #1343, plus `admit` in Rust (#1349) refusing everything but
    the next unreleased part.
  - B2: the firewall's record stays with the developer.
  - Then the red team reviews both.
- **The firewall's cross-session decisions are outside `FirewallComputes` in either language.** These are whether a
  recursive session's next outer session goes on, and when its proofs are released. That follows the owner's D8 ruling,
  and no contract checks them yet. The record contract that would check them is not started.
- **The inner side's decisions are still in Python** (`firewall.py`). If "one implementation" covers them too, it needs a
  `flock-circuit firewall open|finish|stop` subcommand.
- **#1320 B1:**
  - The five registered `--zk` guarantees (`zk_session_soundR`, `…HR`, `…HJR`, `…HR_custody`, `…HJR_custody`) hold of
    no session with a registered port: their scope admits only v1 rows, and the verifier now requires v2.
  - Under way: the re-proof over v2 rows, and a theorem that an honest v2 session meets both premises.
  - Asked @old-circuits-and-proofs (1791293972.223949) whether the v2 statements replace these five under their names (my
    recommendation) or are pinned beside them.
- **Proof gaps carried in the PR bodies' "not in this PR" sections:**
  - every-coin zero knowledge at hidden J. The ZK half is proved among the coins the prover refuses; the coin server's
    commitment at `Hello` is under `keyed-cr`, which no statement models yet;
  - `avoidsMask`, a hypothesis that no check implies yet;
  - Option H, the stratified law, custody, finder budgets and Fiat–Shamir, as #1261's and flock-e2e's bodies list them.
- **D2 (|W| public), D6 (the audit window) and D9 (the lottery):** open. Proofs follows the joint note's recommendations.

## For Daniel

- **The check queue's admission gate.** Should a ready mark need a quick tier when the train's own full check runs every
  suite at the tip anyway? top has it for the morning report. Tonight it cost the stack most of its landings.
- **#1320's replace-or-beside**, if the advisor leaves it to you. Replacing changes five pinned statements, and you get
  the DM showing each.
