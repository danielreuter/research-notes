---
lane: pouw-prs
kind: report
created: 2026-10-01T02:05Z
status: open
---

CHECKPOINT 2066d383 (07:56Z) [open] Open: 5 (#525 #588 #640; bc-c62f9726's #593 #610). #491 and #570 landed in T49. #525 at 6c9832660 has main merged in, check r20261001-073529-9e61 passed, and its ready note is sent. #640 is in T640, #588 in train 1.
CHECKPOINT 22fd1772 (06:54Z) [open] Open: 10. #588 @ 947f1de2c passed check r20261001-063447-4b26; ready note 20261001T0654Z sent to the captain. #590 and #595 go to compute accounting to close as contained in #588, which makes 8.
CHECKPOINT ef125815 (06:36Z) [open] Open: 10 (#491 #525 #570 #580 #588 #590 #593 #595 #610 #640). #588 at 947f1de2c times the served deferred schedule (tile hashing on the side stream, the screen on the main lane); check r20261001-063447-4b26 running. #590 and #595 are contained in #588 and go to compute accounting to close; that makes 8.
CHECKPOINT c1e920090 (06:11Z) [open] Landed #577 (C4), #602 (T602); closed #548 #534 #556 #471. Refusal PR (fbce5a2f) not yet opened; asked compute accounting. #588 fold now has main 72aacf9b + #595 (1ebc04ac), waits on DEFERRED ruling. Open: 14.
CHECKPOINT c1e920090 (06:09Z) [open] #570 ready note sent (efd5739b, r20261001-054235-c715). #580 ready note withdrawn per pouw-fp4 0551Z (tip changes for B-OVF beta table); #602 trains alone. Inbox 0551Z acted on. Open: 20.
CHECKPOINT c1e920090 (05:48Z) [open] #580 ready note sent (37008e8a, r20261001-021907-53ce), train after #602 (b7dd48f0, r20261001-044641-ba55 passed). Open: 20.
CHECKPOINT c1e920090 (05:47Z) [open] #491 ready note sent (f50b7605, r20261001-052513-3604). #471 -> cursor/pouw-quant-param-refusal-645d fbce5a2f (r20261001-045449-cd17 passed), awaiting open+close by compute accounting. #570 main merged efd5739b, check running. #588 fold 9566c906 blocked on DEFERRED ruling. perdie outputs preserved r20261001-053555-4ee7. Open: 20.
CHECKPOINT c1e920090 (04:51Z) [open] #567 landed (5b4815a6). #577 ready note sent (209cce5a, r20261001-022520-abd4 passed). #471: main's ncp-v2 is the circuit; #471's scheme ncp-v2 collides, asking compute accounting. Open: 20.
CHECKPOINT 7a8536708 (02:23Z) [open] checks on vy-nebius-2: #433 7a853670 r20261001-020542-d600, #389 0e0f9678 r20261001-020814-1aaa (stale: +94592b22 pod_bootstrap fix), #435 c354ca9e r20261001-020904-3bbd (stale), #567 5b4815a6 r20261001-022236-9433. #540 main merged e0db4e6b. ncp-v2 sans fixtures: cursor/ncp-v2-rebased-645d f1f5ba20.
CHECKPOINT 7a8536708 (02:05Z) [open] PR steward for PoUW shared code (agent bc-fb6cc95b, replaces bc-0de2d624 bc-6da61042 bc-1a23b70c bc-fb55a759 bc-f4e8ae34 bc-9914c188 bc-f9184c6e#471). #433 main merged at 7a853670, pushed; recording check on vy-nebius-2 next.
