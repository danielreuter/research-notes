# M0 (verity/flock-circuit): RoPE/SiLU/RMSNorm proved private-by-default with every tail in the circuit; attention and salted leaves left (~3-4 agent-days)

From the flock-circuit statement lane (agent bc-ff572e70), PR #83 (draft), report `lanes/flock-netlist/20260926T1740Z-report-flock-netlist.md`.

- **Daniel's rule (verifier evaluates nothing) is enforced by the statement:** a CUT line or any verifier-tail META key is
  refused at parse (negative `verifier_evaluated_tail_refused`). RMSNorm fused/Triton tails now run as circuit stages with MUFU
  lookup slots (rsq; sqrt + rcp), +0.75% / +1.2% ANDs per row; CPU and GPU selftests 24/24 each on L40S.
- **Changes the M1/M2 plan:**
  - Attention softmax in circuit: one ex2 lookup slot per score is ~41k ANDs (two-level one-hot over the 2^23 table), so the
    softmax is ~8M ANDs per T=128 head against 8.8M for the tensor-core steps: ~1.9x attention ANDs (the scoping assumed
    1.28x). A cheaper exact ex2 (a structural model of MUFU.EX2 instead of the table) is the lever.
  - Sampling: the Gumbel noise of the public seed is ~140k ANDs per vocabulary lane (Philox4x32-10 + libdevice logf/log1pf),
    ~27x today's 5,099-AND lane: ~1.8e10 ANDs per row, ~5.8e11 for #101's 32 rows (+0.37% of #101's ANDs, ~+1% of its L40S
    time at 1 G AND/s). The top-p keep word adds the scoping's x2 plus EX2/RCP lookup slots. Not lowered yet.
- **M0 left:** attention (one T class) in the circuit (stage batching per MUFU level, multi-round device witness, the FA2 tail
  pieces, the query hashed, variable-T rows) ~2-3 agent-days, ~$5 GPU; salted proof-internal leaves (Flock CPU + CUDA Merkle
  leaves, opened salts in the proof) ~1 agent-day. Pinned honestly as `flock-leaf/sha256-unsalted` meanwhile (HM96 room
  reserved). Single-run 2^-128 (vs one root bound by both reps, built) is an M1 item (F256 coins or a doubled PIOP).
- **Spend** ~$6 of $40 so far.
