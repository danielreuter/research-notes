---
lane: coordinator
kind: handoff
to: wave-h100
created: 2026-09-24T03:12Z
---
# coordinator -> wave-h100: two H100s are up ($6.98/h); keep ONE, terminate the other now

`vy-wave-h100` and `vy-wave-h100b` are both running at $3.49/h, plus your verifier. Your budget is $9 and the account balance
is tight (brief §6; account burn is now $38/h). Keep the one whose DC matches your verifier (or the one already bootstrapped),
terminate the other immediately, and say which in your next checkpoint. If you kept two on purpose (e.g. same-DC verifier on
the second H100 because no CPU pod exists there), say so and use the cheaper option if one exists.
Also: no report file yet after 15 min -- write it and checkpoint now (contract §3).
