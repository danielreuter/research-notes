---
id: review-zk-gateway/20261006T1830Z-finding-r9-onto-rec
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1270@2f2a58de5894014d7d5868d96d12942b820e29b7, pr:1343@3399b71f5b441e3c85b919bb303fa36680687209, pr:1349@83a3f5f43868f7299b8458d9fa73caefe637c0b3]
---

# Red-team round 9 (onto the rec stack): #1270'', #1343'' and #1349'' GRANT

This is @proofs' round 9: #1270 forward-merged onto #1284 (rec-step3) and #1347, and its two dependants relabelled.
Detail is in the store's `private/red-team-reviews/1270/review-r9.md`. I ran nothing on a pod.

## #1270'' (`cursor/zk-gateway-95d4`): GRANT at `2f2a58de5894014d7d5868d96d12942b820e29b7`

- **The resolutions.** My own `--remerge-diff` and `--cc` of `a83c72890` and `2f2a58de5` match
  art:ac07a26671c8485e43fe1b2cabf06f912a2c5a6512d107af4cac450b51fd7228 byte for byte. `3e0b8c46e` (the #1245 merge) carries r7's
  grant: its own patch is byte-identical.
- **The schedule pins every field the coin server records.** Each round's stream, `k`, `n`, its fresh tops' node counts, its
  `level0` count and its `commits` (0 or 1) are compared against `schedule["rounds"][i]` by global index. A level-0 copy
  can't pass as a top, or a top as a copy, without changing a pinned count. The binding round's cap must be `root_B`.
  Nothing the prover chooses reaches the record unpinned, apart from `end`, which is §10.5's stop channel. §10.5's numbers
  don't move: 2336 counts messages, and the rounds stay at 139 a rep.
- **Both sides' behaviour.**
  - rec-step3's v1 record, salted tops and V* (`tops`, `opened_top`) are intact, with `FIREWALL-REFUSED` renamed in three raises and one `startswith`.
  - #1270's refusals are all kept, and its old V* checks are covered by rec-step3's.
  - The Rust is rec-step3's `pcs_of`/`salted` with #1270's `Result`s, plus one conjunction in `session_proved`.
  - #1347's hunk is comment-only, and the script body keeps its `FORGE` default.
- **Non-blocking.**
  1. `live/PROTOCOL.md` §10 and §10.3's prose is #1270's pre-merge text. It still says v0, level-0 copies salted, rows a
     round, `rec_vstar.root`/`caps`, and `rec_outer` registering clear caps; the code is v1 and right.
  2. `pod/80-rec-inner.sh`'s summary reads `r["caps"]`. That is rec-step3's (#1284's) bug, older than this merge.

## #1343'' at `3399b71f5b441e3c85b919bb303fa36680687209` and #1349'' at `83a3f5f43868f7299b8458d9fa73caefe637c0b3`: GRANT, on review

- **Q5's letter fails.** Neither own patch is byte-identical. The added and removed lines are, but each has one context line
  from the new base: #1343 in `serve`'s result dict (`tops`/`top_nodes`), #1349 in `Plan { …, zk_self_check }`. I read both
  hunks, and neither change interacts with the patch.
- **Tests at `83a3f5f43`:** the firewall/release and rec Python suites, 147 passed and 2 skipped (the Lean-gated ones), in 3.5 minutes.
- **Process.** The lane's identity check compares the added and removed lines, but Q5 asks for bytes, so a context-only change forces a review.
  A rule of "line-identical, with the reviewer reading only the hunks whose context changed" would have cost a minute here.
