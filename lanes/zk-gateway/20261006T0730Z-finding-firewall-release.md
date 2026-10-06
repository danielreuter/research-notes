---
id: zk-gateway-20261006T0730Z-firewall-release
campaign: proof-service
lane: zk-gateway
kind: finding
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
---
# The firewall's release side: rules 0–2 built, and rule 3's honest prove times on node 1

**Rules 0–2** are on `cursor/firewall-release-95d4`, stacked on #1270 at `d828d3ea9`. The work is four commits: the rename, `verity_flock.firewall`, `rec_live --firewall`, and §10.5. The PR body is at `internal/proofs/firewall-release-pr.md` in proofs' store.

- A recursive session ends at its first stop. The firewall's record and relay enforce it: they sit between `flock-circuit prove --zk` and `serve`, and their state directory is shared across processes.
- A stop the firewall makes reaches `serve` as a cut, never `Finish`.
- One outer slot covers all streams.
- §10.5's first row holds through the relay at 11.19 bits (`log₂ 2336`), lower than 12.1 because there is no outer `Finish` bit and a cut before the first request looks like a session never opened.
- `85-rec-reprice.sh` does not run the relay yet, so node 1's sessions are still the second row's (80.1 bits).

**Rule 3's input.** Run `r20261006-065256-f517` on node 1 (K = 4096, `MODES=gate` at `d828d3ea9`, which is today's `FC_FIREWALL=1`) covered the eight V* statements, each with 10 timed sessions after 1 warm, and one GPU leased around each prove. `e2e_s` runs from `Register`, the slot grant, to the end of proving. The verdict is serve's verification after `Finish`.

| statement | e2e median (s) | e2e max (s) | verdict median (s) |
|---|---|---|---|
| L0 | 7.65 | 7.84 | 1.32 |
| L1 | 4.54 | 4.92 | 1.18 |
| L2 | 4.74 | 5.02 | 1.27 |
| L3 | 2.95 | 3.11 | 1.13 |
| L4 | 3.00 | 3.23 | 1.04 |
| L5 | 1.85 | 2.13 | 0.66 |
| L6 | 2.00 | 2.32 | 1.13 |
| alg | 11.33 | 16.99 | 7.96 |

- Summed over the eight statements, `e2e` has a median of 38.1 s and a maximum of 44.2 s. Slot time, which includes the verdicts, has a median of 54.3 s and a maximum of 60.5 s.
- The tail is the algebra statement. Its sessions are bimodal: 8.8–9.5 s in four of them and 13.1–17.0 s in five, while the levels stay within 5–17% of their medians.
- The prover's 16 cores are shared with the firewall's threads, and node 1's load average was 113 at the start. Dedicated cores (infra's I1) should remove the contention, which §10.4 puts at about 10 s, and most of the algebra statement's spread.
- A period per statement position (`T_p`, public, since the statement shapes are) fits much better than one period for every outer proof. One period would have to cover the algebra statement's 17 s eight times.

**Rule 4.** P1's `Stream` (`origin/cursor/proof-service-95d4`, `sampled_proofs/service.py`) calls the budget `budget` (b). A stream stops at its `budget`-th failure, and the stream's digest binds the value. The firewall's budget for a stream has to be that same number, and it has to count the same failures: stops, refusals and missed times.
