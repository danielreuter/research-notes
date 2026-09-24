# verify-night: 4 faster B-Ligero results are payload-only (Table 2 cannot see them); one has dumps and would move H100 BF16 2.0e7x -> 1.4e7x

From verify-night, 06:55Z. For your decision; nothing blocks me.

State after my first two rounds (render 06:48Z, `lanes/verify-night/evidence/render-0648Z.md`): all 15 instance-equiv/v1
labelled verified=accepted, and reverify PASS + statement-vs-frozen binding on the new cells H100 BF16 art:44c768cd (0.2525 s),
H100 FP8 art:1e73dc00 (0.1342 s), 4090 art:fb4934af (0.0907 s), 4090 + hash art:9167ed22 (0.3879 s), 5090 art:885eec16 (0.0383 s).

D2 shows faster results that tables.py cannot place: their meta is a lane summary and the envelope sits in the JSON payload,
so the renderer lists them as "not candidates" and drilldown adds X "register the result.json as --meta". Re-registering
gives a new art id, so verifying the old ids now would not help; I verify whatever gets re-registered.

| D2 variant | row | t.total | current cell | art | producer | dumps |
|---|---|---|---|---|---|---|
| v1 | H100 BF16 | 0.1815 s (~1.4e7x) | 0.2525 s | art:75fb468b | v3-scout | yes (refs.run_files) |
| v3 private selection | H100 BF16 | 0.1967 s | 0.2525 s | art:99e1cd62 | wave-h100-2 | no run_files ref |
| v3x4 fold | H100 FP8 | 0.0750 s (~1.2e7x) | 0.1342 s | art:4864dd93 | wave-h100-2 | no run_files ref |
| v2x4 public selection | 4090 FP8 | 0.0701 s (~1.8e6x) | 0.0907 s | art:db32dd62 | hints-fused-2 | no run_files ref |

Only art:75fb468b could become a verified cell, after someone other than me re-registers its result.json as meta (plus
lane/run_id, keeping refs.run_files). A verifier must not register the result it then labels. The others need a re-run
(fill lanes).
