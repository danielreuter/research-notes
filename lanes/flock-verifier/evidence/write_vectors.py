"""Write backends/flock/verifier/vectors.json (flock-verifier lane, phase 1)."""
import json

honest = json.load(open("/tmp/vec/manifest-honest.json"))

LAYOUT = {  # cell -> (statement detail) from the lane reports
    "art:6d1295ed": "Chunk(3) bf16-hopper, H100", "art:1589ffe1": "Chunk(3) bf16-hopper, H100 (re-run)",
    "art:167e64a8": "Chunk(3) bf16-ampere, A100", "art:d1961ba4": "Fp8 fp8-ada, RTX 4090", "art:7afeecbe": "Fp8 fp8-ada, RTX 4090",
    "art:c3e83404": "Fp8 fp8-hopper, H100", "art:728d8724": "ShaBf16 (sha256/row/v1)", "art:324888c5": "ShaBf16 (sha256/row/v1)",
    "art:df857ea6": "ShaFp8 (sha256/row/v1)", "art:fd772057": "ShaFp8 (sha256/row/v1)",
    "art:2753a371": "Fp4 (blake3-keyed/row-nvfp4/v1), RTX 5090", "art:db7f48de": "ShaFp4 (sha256/row-nvfp4/v1), RTX 5090",
    "art:5d2a91a7": "Chunk(n) fp8 real K, spine set", "art:ab115376": "Chunk(n) fp8 real K, spine set",
    "art:66d2412c": "Chunk(n) fp8 real K, spine set", "art:1c520240": "Chunk(n) fp8 real K, spine set",
    "art:149cdaf9": "Chunk(n) bf16 real K", "art:673c1835": "Chunk(n) real K", "art:c767e092": "Chunk(n) real K",
    "art:bbb95342": "Chunk(n) real K", "art:df3d63e4": "Chunk(2)/(4) K2048, L40S", "art:8bc3dba2": "Chunk(n) K8192, L40S",
    "art:73a9e9f3": "Chunk(n) K2048, L40S (#101 re-run)",
    "art:dd27fdab": "frame/v2 elementwise", "art:8a07b80f": "frame/v2 elementwise", "art:9563d2c8": "frame/v2 elementwise",
    "art:dc9b92f6": "frame/v3 #101 elementwise, L40S", "art:6dc1f392": "frame/v3 #101 elementwise, L40S",
    "art:1e7cdc41": "frame/v3 #101 elementwise, L40S",
    "art:ba046ee8": "frame/v3 served elementwise", "art:6f8219df": "frame/v3 served elementwise", "art:d3be6792": "frame/v3 served elementwise",
    "art:a7a31593": "frame/v3 served elementwise", "art:27a119c9": "frame/v3 served elementwise", "art:bd1b1770": "frame/v3 served elementwise",
    "art:08a853f6": "frame/v3 attention T=4", "art:73bd2c2b": "frame/v3 attention T=128", "art:d5b0ae9f": "frame/v3 attention T=129",
    "art:3117572d": "frame/v3 attention T=130", "art:645a8359": "frame/v3 attention T=131", "art:d18e0ae3": "frame/v3 attention T=132",
    "art:ccede46a": "frame/v3 attention T=256", "art:73750ffa": "frame/v3 attention T=257",
    "art:4fb2de9c": "frame/v3 attention class c1 (T 1-128)", "art:b61eafa9": "frame/v3 attention class c2 (T 129-256)",
    "art:4dd2069b": "frame/v3 attention class c3 (T 257-512)",
    "art:a330c568": "flock-ir-sampling/v1 (verifier-evaluated noise: not strict-rule)", "art:26b5f7d8": "flock-ir-sampling/v1 (verifier-evaluated noise: not strict-rule)",
    "art:56f792bd": "flock-vllm-block/v1 (out of scope, same verifier path)",
}
G2 = lambda h: h.get("cell") not in {"art:6d1295ed", "art:d1961ba4", "art:1589ffe1", "art:c3e83404", "art:7afeecbe",
                                     "art:167e64a8", "art:728d8724", "art:df857ea6", "art:fd772057", "art:324888c5"}

sets = []
for h in honest:
    stmt = h["statement"]
    if h["cell"] in ("art:a330c568", "art:26b5f7d8"):
        stmt = "flock-ir-sampling"
    sets.append({
        "cell": h["cell"], "statement": stmt, "detail": LAYOUT.get(h["cell"], ""), "table": h["table"],
        "record": h["record"], "verifier_run": h["verifier_run"], "verifier_commit": h["verifier_commit"],
        "sessions_with_proofs": h["sessions_with_proofs"], "g2_record": G2(h),
        "statement_digest": h["statement_digest"], "hello": h["hello"], "rounds_per_stream": h["rounds_per_stream"],
        "public_input": {"instances": h["instances"], "statement_files": h["statement_files"]},
        "labels": h["labels"], "vectors": h["vectors"],
    })

sets.append({
    "cell": None, "statement": "flock-circuit", "detail": "PR #83 generic circuit statement (tag verity/flock-netlist/v1), SiLU 128 rows, L40S loopback (co-resident verifier: a vector, not evidence)",
    "table": "nl", "record": "art:6250c04f", "verifier_run": "r20260926-181746-69fe", "verifier_commit": "PR #83 before f1112817 (no coin seed)",
    "sessions_with_proofs": 6, "g2_record": True, "statement_digest": None,
    "hello": {"flavor": "rs", "link": {"m": 31, "points": 2, "sigma": "445fbde41baa430371fffe7f1327b54178910129f995b3b299770a520e63c4da"},
              "profile": "fast100", "reps": 2, "tables": ["nl"]},
    "rounds_per_stream": None,
    "public_input": {"instances": ["out/cell/p2-128/instances-s0.bin"], "statement_files": ["out/cell/p2-128/stage-s0/net.txt"]},
    "labels": {}, "vectors": [
        {"session": f"out/cell/p2-128/loopback-sessions-s0/l000{i}-10584/session.json",
         "proofs": [f"out/cell/p2-128/loopback-sessions-s0/l000{i}-10584/nl.rep{r}.bin" for r in (0, 1)], "expect": "accept"}
        for i in range(2)],
})

negatives = {
    "recipe_source": "backends/flock/pod/31-replay.sh (verify-flock-pure); apply to any honest vector",
    "recorded_outcomes": ["art:487b77de (run r20260925-222222-a2cf): out/h100n/negatives.jsonl on art:6d1295ed, out/adan/negatives.jsonl on art:d1961ba4"],
    "cases": [
        {"name": "proofs_from_other_session", "mutation": "use the proof files of another session of the same point", "expect": "reject", "why": "S17"},
        {"name": "reps_swapped", "mutation": "pass rep1's proof as rep0 and the reverse", "expect": "reject", "why": "S17"},
        {"name": "rep1_second_round_coin_low_bit", "mutation": "flip bit 0 of coin 5 of round 1 of <t>/rep1", "expect": "reject", "why": "zerocheck final check"},
        {"name": "rep0_mid_round_coin_low_bit", "mutation": "flip bit 0 of coin 0 of round 70 of <t>/rep0", "expect": "reject", "why": "opening"},
        {"name": "link_point_changed", "mutation": "flip bit 0 of coordinate 0 of link point 0", "expect": "reject", "why": "S14"},
        {"name": "publics_digest_changed", "mutation": "set link.publics_sha256.<t> to 32 zero bytes", "expect": "reject", "why": "S7"},
        {"name": "round_message_digest_changed", "mutation": "set streams[0].rounds[0].msg_sha256 to 32 zero bytes", "expect": "reject", "why": "R2 (§6.2)"},
        {"name": "require_link_false", "mutation": "set config.require_link to false", "expect": "reject", "why": "S3"},
        {"name": "other_instance_file", "mutation": "verify against another point's public input", "expect": "reject", "why": "S2 (Σ differs)"},
        {"name": "unused_high_bits_of_query_coin", "mutation": "flip bit 127 (the top bit of hi) of coin 0 of the last round of <t>/rep1", "expect": "accept",
         "why": "query indices use only the low bits of each coin (§13); a verifier that rejects this reads bits it must not"},
        {"name": "zerocheck_coin_low_bit", "mutation": "flip bit 0 of coin 0 of round 0 of <t>/rep0", "expect": "info",
         "recorded": "accepted", "why": "see §19: which coins an honest proof's checks do not depend on"},
        {"name": "last_coin_low_bit", "mutation": "flip bit 0 of coin 0 of the last round of <t>/rep1", "expect": "info", "recorded": "accepted", "why": "§19"},
        {"name": "rep_root_differs", "mutation": "set root_sha256 of <t>/rep1 to another value", "expect": "reject", "why": "S13 (R-BREAK at record level)"},
        {"name": "third_rep_stream", "mutation": "duplicate <t>/rep1 as <t>/rep2", "expect": "reject", "why": "S11"},
        {"name": "lone_rep", "mutation": "delete <t>/rep1 and its proof entry", "expect": "reject", "why": "S11, S17"},
        {"name": "extra_round", "mutation": "append a copy of the last round to <t>/rep0", "expect": "reject", "why": "S15"},
        {"name": "child_stream", "mutation": "add a stream <t>/rep0/f0 with zero rounds", "expect": "reject", "upstream_expect": "accept", "why": "S11, intended divergence D2"},
        {"name": "root_f_not_sigma", "mutation": "set link.root_f to 32 zero bytes and root_f_sha256 and link_sha256 accordingly", "expect": "reject", "upstream_expect": "accept", "why": "S6, intended divergence D1"},
        {"name": "proof_byte_flip", "mutation": "flip one byte of the rep0 proof and set its proof_sha256 accordingly", "expect": "reject", "why": "decode, transcript or check failure"},
        {"name": "fast_params_relabel", "mutation": "rewrite commitment.params.profile in the rep0 proof to Fast and fix proof_sha256", "expect": "reject", "why": "params pin (§8)"},
    ],
    "note": "The first 12 cases ran on two cells with the recorded outcomes; the remaining 8 are new record-level cases this spec adds (their outcome under upstream is recorded in phase 2; upstream_expect marks the two intended divergences D1, D2 of PROTOCOL.md §17.1).",
}

forgeries = {
    "note": "The red-team forgeries were run in-process against upstream's verifier or the live server; each run stored its harness and a verdict table, not the forged record and proof bytes. Phase 2 materialises them as replayable (record, proofs) pairs with the dump plan below.",
    "runs": [
        {"art": "art:8d04b53f", "run": "r20260925-112210-2d3d", "by": "red-team-flock", "name": "R-BREAK: reps unbound to one root",
         "files": ["inputs/rtf_unlinked_reps.rs", "out/rtf.tsv"], "statement": "BLAKE3 table (upstream FS), n 4096 and 16384",
         "cases": {"honest_pair_same_witness": "accept", "unlinked_pair_rep1_other_witness": "accepted by upstream FS r2 (the break); must be rejected (S13/S16/S18)",
                   "fast_proof_under_fast100_verifier": "reject", "fast100_proof_relabelled_fast_params": "reject",
                   "fast100_proof_under_fast_verifier": "reject", "rep0_replayed_as_rep1": "reject",
                   "padding_rows_filled_with_dummy_invocations": "accept (same root as zero padding)"},
         "materialise": "prove witness A and witness B in two live sessions of the same statement; splice B's rep-1 stream, root and proof into A's record; expect reject at S13"},
        {"art": "art:1bd3368b", "run": "r20260925-124333-1a03", "by": "red-team-flock", "name": "live attacks R1/R2/R3/R7, n 4096",
         "files": ["inputs/rtf_live_attacks_tail.rs", "out/attacks.tsv", "out/selftest.tsv"]},
        {"art": "art:12a6b845", "run": "r20260925-124555-21d5", "by": "red-team-flock", "name": "live attacks, n 4096 and 16384",
         "files": ["inputs/rtf_live_attacks_tail.rs", "out/attacks.tsv", "out/selftest.tsv"]},
        {"art": "art:20545959", "run": "r20260925-155333-c658", "by": "red-team-flock", "name": "link attacks L1-L4",
         "files": ["inputs/rtf_link_attacks_tail.rs", "out/attacks.tsv", "out/selftest.tsv"]},
        {"art": "art:ac1aeeeb", "run": "r20260925-210925-a744", "by": "red-team-flock", "name": "flock-pure-block/v2 selftest 18/18 at 8 and 64 VUs"},
        {"art": "art:1f2fe1e9", "run": "r20260925-212534-f9f0", "by": "red-team-flock", "name": "fp8-ada selftest 16/16, bf16 18/18"},
        {"art": "art:0f0b6f41", "run": "r20260925-230859-6d32", "by": "red-team-flock", "name": "fp8-hopper 16/16, bf16-ampere 18/18"},
        {"art": "art:08295fa2", "run": "r20260925-232225-1b40", "by": "red-team-flock", "name": "SHA-256 layouts 13/13 x4"},
        {"art": "art:cf130873", "run": "r20260926-025249-6192", "by": "red-team-flock-2", "name": "NVFP4: 12 negatives refused (rtf2)"},
        {"art": "art:ac3dac64", "run": "r20260926-040359-a5da", "by": "red-team-flock-2", "name": "NV1-NV5: 12 negatives, 7 admission refusals, consistent output forgery"},
        {"art": "art:25c96f97", "run": "r20260926-103512-bb40", "by": "red-team-flock-3", "name": "attention v3: 19 prover-side attacks refused"},
        {"art": "art:49512aff", "run": "r20260926-175514-5b86", "by": "PR #83 lane (producer)", "name": "circuit-statement selftests RoPE 18 / SiLU 19 cases",
         "files": ["out/rope-head/selftest-gpu.txt", "out/silu-mul/selftest-gpu.txt"]},
    ],
    "dump_plan": "Add `--dump DIR` to the selftest subcommand of flock-pure-gpu, flock-ir-frame and the PR #83 circuit-statement binary so every case writes its session.json and proofs; run once on a CPU pod at 8 VUs (a few minutes); preserve the tree as one artifact; each case's expected verdict is its selftest `pass` line.",
}

out = {
    "format": "flock-verifier-vectors/v1",
    "spec": "backends/flock/verifier/PROTOCOL.md",
    "spec_transcript_check": "backends/flock/verifier/transcript_check.py reproduces every recorded round digest of the first vector of each honest set from the spec alone (50 of 50 sets, both reps)",
    "fetch": "research data fetch <record> --path <path> (the evidence store; records are run-record/v1 trees)",
    "honest": sets, "file_negatives": negatives, "forgeries": forgeries,
}
json.dump(out, open("/workspace/backends/flock/verifier/vectors.json", "w"), indent=1)
print(len(sets), "honest sets;", sum(len(s["vectors"]) for s in sets), "vectors;", len(negatives["cases"]), "negative recipes;", len(forgeries["runs"]), "forgery runs")
