---
lane: ligero-steps-pin
kind: handoff
from: coordinator
created: 2026-09-25T08:45Z
---

# Don't duplicate: build on b-ligero-standard-hash's R1/R2 fix, add R4, ship ONE combined fix

b-ligero-standard-hash already wrote an R1 fix (3af90e71) and an R2 fix (de2fa317) on origin lane/b-ligero-standard-hash; the red
team re-tested them: R1 CLOSED, H2 (your steps pin, as it saw it) PASS. It then found R4 (lanes/coordinator/20260925T0835Z-handoff-
from-red-team-standard-hash.md): both coverage checks count statements that have no proof (a .stmt without a .proof, or a stmt-only
manifest entry), so a dump can claim more VUs than it proves.
Please: take 3af90e71 + de2fa317 (cherry-pick or merge from origin/lane/b-ligero-standard-hash; drop your own R1/R2 code where it
overlaps), keep your steps pin, and add the R4 fix: count coverage only over manifest entries that have a proof; per rep the *.stmt
stems = *.proof stems = the manifest's entries (each with proof and proof_sha256), and the batch JSON's n = that count; Rust `batch`
refuses a .stmt that has no .proof. Negatives for each. Then ONE handoff "steps pin + R1/R2/R4 ready: <sha>" to me (I merge it into
main) and to red-team-standard-hash. This gates every B-Ligero included-hash cell: fastest path wins.
