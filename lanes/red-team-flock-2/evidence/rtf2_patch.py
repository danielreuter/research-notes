#!/usr/bin/env python3
"""red-team-flock-2: add attack knobs to flock-pure-gpu.rs (flock-gpu-link 7b3ba797) for the NVFP4 layout review.

Prover side only: a `rt` field on Plan, witness tampers in `session`, the RT2_CASES list, and a `--only` lookup in it.
PureVerifier, `pure_block.rs` and the producer's CASES are untouched.  Usage: rtf2_patch.py backends/flock/live/src/bin/flock-pure-gpu.rs
"""
import sys

EDITS = [
    ("    profile: [LigeritoProfile; 2],\n    substitute: Option<Vec<Vec<u8>>>,\n}",
     "    profile: [LigeritoProfile; 2],\n    substitute: Option<Vec<Vec<u8>>>,\n    rt: &'static str,\n}"),
    ("profile: [LigeritoProfile::Fast100; 2], substitute: None }",
     "profile: [LigeritoProfile::Fast100; 2], substitute: None, rt: \"\" }"),
    ("|| plan.acc_in_wrong || plan.rep1_other_witness || plan.unit_flip);",
     "|| plan.acc_in_wrong || plan.rep1_other_witness || plan.unit_flip || !plan.rt.is_empty());"),
    ("    let comps = Arc::new(comps);\n",
     """    match (&mut comps, plan.rt) {
        (Comps::B3(c), "fp4_root_flag_dropped") => { let j = st.lay.chunks()[0] - 1; c[j].4 &= !flock_live::chunk::ROOT; }
        (Comps::B3(c), "fp4_tail_word_nonzero") => { let j = st.lay.chunks()[0] - 1; c[j].1[8] ^= 1; }
        (Comps::B3(c), "fp4_scale_block_forged_digest_only") => {
            c[12].1[5] ^= 1;
            let p = c[12];
            c[13].0 = flock_hash::blake3_compress(&p.0, &p.1, p.2, p.3, p.4)[..8].try_into().unwrap();
        }
        (Comps::B3(c), "fp4_dummy_block_forged") => { let j = st.blocks_real * st.lay.comp_slots() + 3; c[j].1[0] ^= 1; }
        (Comps::Sha(c), "sha_fp4_dummy_block_forged") => { let j = st.blocks_real * st.lay.comp_slots() + 3; c[j].1[0] ^= 1; }
        (Comps::Sha(c), "sha_fp4_pad_marker_dropped") => { let j = st.lay.per_role() - 1; c[j].1[8] ^= 0x8000_0000; }
        (Comps::Sha(c), "sha_fp4_last_block_data_forged") => { let j = st.lay.per_role() - 1; c[j].1[3] ^= 1; }
        (Comps::Sha(c), "sha_fp4_scale_block_forged") => {
            c[12].1[5] ^= 1 << 24;
            let p = c[12];
            c[13].0 = flock_prover::r1cs_hashes::sha2::sha256_compress(&p.0, &p.1);
        }
        _ => {}
    }
    let comps = Arc::new(comps);
"""),
    ("    let (operand_flip, acc_in_wrong) = (plan.operand_flip, plan.acc_in_wrong);\n",
     """    let (operand_flip, acc_in_wrong) = (plan.operand_flip, plan.acc_in_wrong);
    let rt_scale: Option<(usize, usize, bool, u32)> = match plan.rt {
        "fp4_x_scale_operand_free_u5" => Some((0, 5, false, 32)),
        "fp4_x_scale_operand_free_u20" => Some((0, 20, false, 32)),
        "fp4_w_scale_operand_free_u7" => Some((0, 7, true, 8)),
        _ => None,
    };
    let rt_free: Option<u64> = plan.rt.strip_prefix("free_scale_").map(|s| u32::from_str_radix(s, 16).unwrap() as u64);
"""),
    ("            if operand_flip && b == 0 && u == 3 {\n                r[0].lo ^= 1 << 9;\n            }\n",
     """            if operand_flip && b == 0 && u == 3 {
                r[0].lo ^= 1 << 9;
            }
            if let Some((bb, uu, hi, bit)) = rt_scale {
                if b == bb && u == uu {
                    if hi { r[4].hi ^= 1u64 << bit } else { r[4].lo ^= 1u64 << bit }
                }
            }
            if let Some(s) = rt_free {
                r[4].lo |= s << 32;
                r[4].hi |= s;
            }
"""),
    ("    let inputs = make_inputs(false);\n",
     """    let inputs = make_inputs(false);
    if let Some((bb, uu, hi, bit)) = rt_scale {
        let tampered = inputs(bb, uu);
        let mut honest = tampered;
        if hi { honest[4].hi ^= 1u64 << bit } else { honest[4].lo ^= 1u64 << bit }
        let ev = |r: &[F128; 5]| -> u32 {
            let (z, _, _) = st.net.eval64(|x| { let w = r[x >> 7]; let j = x & 127; (if j < 64 { w.lo >> j } else { w.hi >> (j - 64) }) & 1 });
            (0..32).fold(0u32, |w, t| w | (((z[st.net.out_cols[0] * 128 + t] & 1) as u32) << t))
        };
        eprintln!("RT2 isolation {}: honest c_out {:08x}, tampered c_out {:08x}, unchanged {}", plan.rt, ev(&honest), ev(&tampered), ev(&honest) == ev(&tampered));
    }
"""),
    ("    (\"cross_session_replay_both_reps\", false, false),\n];\n",
     """    ("cross_session_replay_both_reps", false, false),
];

const RT2_CASES: &[(&str, bool, bool)] = &[
    ("fp4_root_flag_dropped", false, true),
    ("fp4_tail_word_nonzero", false, true),
    ("fp4_scale_block_forged_digest_only", false, true),
    ("fp4_x_scale_operand_free_u5", false, true),
    ("fp4_x_scale_operand_free_u20", false, true),
    ("fp4_w_scale_operand_free_u7", false, true),
    ("fp4_dummy_block_forged", false, true),
    ("sha_fp4_dummy_block_forged", false, true),
    ("sha_fp4_pad_marker_dropped", false, true),
    ("sha_fp4_last_block_data_forged", false, true),
    ("sha_fp4_scale_block_forged", false, true),
    ("free_scale_38383838", true, false),
    ("free_scale_40404040", true, false),
];
"""),
    ("        _ => h,\n    }\n}\n",
     "        _ => Plan { rt: RT2_CASES.iter().find(|c| c.0 == name).map_or(\"\", |c| c.0), ..h },\n    }\n}\n"),
    ("    let want = CASES.iter().find(|c| c.0 == name).expect(\"case\");",
     "    let want = CASES.iter().chain(RT2_CASES.iter()).find(|c| c.0 == name).expect(\"case\");"),
]


def main(path):
    src = open(path).read()
    for old, new in EDITS:
        n = src.count(old)
        if n != 1:
            sys.exit(f"anchor found {n} times: {old[:80]!r}")
        src = src.replace(old, new)
    open(path, "w").write(src)
    print(f"rtf2_patch: {len(EDITS)} edits applied to {path}")


if __name__ == "__main__":
    main(sys.argv[1])
