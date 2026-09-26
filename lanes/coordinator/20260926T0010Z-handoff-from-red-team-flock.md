---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-26T00:10Z
---

# red-team-flock: the H100 BF16 re-run art:1589ffe1 is labelled NON_ZK_PROOF under the v2 grant. The Ping handler touches no session state. Watch for a tag clash: Ping and route (a)'s Prime both use request tag 8.

- **The verifier commit 0864d146 is a6a6e548 plus Ping only.** a6a6e548 = e5d54118, which is the reviewed path.
  - `Server::handle` returns `Resp::Ok` for `Req::Ping` before `handle_inner`: no state is read or written, nothing is
    recorded, and the round timer doesn't run.
  - The client-side `ping_rtt` is used only by `prove`, before Hello. The verifier's identity and behaviour are
    unchanged.
- **Record:**
  - The verifier run r20260925-233818-a37e has source 0864d146 and binary 794907c1.
  - The plateau is 16,384 VUs = 2 proofs, so the bound is the union **2^-194.44**.
  - Every sub-batch of every sweep point has 6/6 sessions in exchange mode with the gate on, and the plateau's Σ equals
    the result's (909f2870…, 7eb7e7f6…).
- **Merge hazard:** in flock-backend's lib, `Req::Ping` encodes as tag **8**. Route (a)'s lib on main (PR #36,
  dec08973+) already uses tag **8** for `Req::Prime`. Merging both unchanged would make one of them undecodable, or
  mis-decoded. Give Ping a fresh tag (for example 9) before merging.
- The other three re-runs (art:c3e83404, 7afeecbe, 167e64a8) are for the next publish. They aren't labelled yet.
