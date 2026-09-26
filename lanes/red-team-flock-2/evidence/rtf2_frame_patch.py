#!/usr/bin/env python3
"""red-team-flock-2: env-driven prover-side attack knobs for flock-ir-frame.rs (PR #54 @ c53d9148); the verifier is untouched.
Run with `selftest --only honest`; `accepted` is the verdict.

  RT2=counter_forged       a run past its chunk's first run: its first compression's counter +1, the run re-hashed, publics honest
  RT2=blen_forged          compression 0's block_len 32, the run re-hashed, publics honest
  RT2=empty_run_message    an empty run slot of a real block: a message bit set, the slot re-hashed (the Cv claim is the verifier's dummy)
  RT2=empty_run_published  the same, with the slot's re-hashed value published as that slot's public (a public past the real runs)
  RT2=empty_unit_input     every unit slot of the padding blocks proves unit slot 0 of block 0's inputs (a consistent witness)
  RT2=public_other_run     run slot 0's public replaced by run slot 1's (both real), witness honest
"""
import sys

EDITS = [
    ("""    let rows_s = t0.elapsed().as_secs_f64();
    let publics = FrameStmt::publics_bytes(&cvs);
""",
     """    let rt = std::env::var("RT2").unwrap_or_default();
    let (cs, nb) = (st.lay.comp_slots, st.lay.nb);
    match rt.as_str() {
        "counter_forged" => {
            let (b, q) = inst.blocks.iter().enumerate()
                .find_map(|(b, bl)| bl.0.iter().position(|c| c.is_some_and(|x| x.3 > 0 || x.2 > 0)).map(|q| (b, q))).expect("a run");
            comps[b * cs + q * nb].2 ^= 1;
            rechain(&mut comps, b * cs + q * nb, nb);
        }
        "blen_forged" => {
            comps[0].3 = 32;
            rechain(&mut comps, 0, nb);
        }
        "empty_run_message" | "empty_run_published" => {
            let (b, q) = inst.blocks.iter().enumerate()
                .find_map(|(b, bl)| bl.0.iter().position(|c| c.is_none()).map(|q| (b, q))).expect("an empty run slot in a real block");
            comps[b * cs + q * nb].1[0] ^= 1;
            let v = rechain(&mut comps, b * cs + q * nb, nb);
            if rt == "empty_run_published" {
                cvs[b][q] = v;
            }
        }
        "public_other_run" => {
            cvs[0][0] = cvs[0][1];
        }
        _ => {}
    }
    eprintln!("RT2 {rt:?} blocks_real {} blocks {} units/block {}", st.blocks_real, st.blocks(), st.lay.units);
    let rows_s = t0.elapsed().as_secs_f64();
    let publics = FrameStmt::publics_bytes(&cvs);
"""),
    ("""        inputs: Box::new(move |b, u| {
            let mut r = st2.unit_inputs(&i2, &c2, b, u);
""",
     """        inputs: Box::new(move |b, u| {
            let pad = std::env::var("RT2").as_deref() == Ok("empty_unit_input") && b >= st2.blocks_real;
            let mut r = st2.unit_inputs(&i2, &c2, if pad { 0 } else { b }, if pad { 0 } else { u });
"""),
]


def main(path):
    src = open(path).read()
    for old, new in EDITS:
        if src.count(old) != 1:
            sys.exit(f"anchor found {src.count(old)} times: {old[:70]!r}")
        src = src.replace(old, new)
    open(path, "w").write(src)
    print(f"rtf2_frame_patch: {len(EDITS)} edits applied to {path}")


if __name__ == "__main__":
    main(sys.argv[1])
