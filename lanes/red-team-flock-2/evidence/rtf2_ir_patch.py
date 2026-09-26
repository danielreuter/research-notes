#!/usr/bin/env python3
"""red-team-flock-2: env-driven attack knobs for flock-ir-block.rs (PR #54 @ 366befc4), prover side plus one verifier-file
tamper. With RT2 unset the binary behaves exactly as before; the verifier (IrVerifier, ir_block.rs) is untouched.

  RT2=padding_nonzero_input   the first padding unit (g = units_real) proves unit 0's (nonzero) input and output
  RT2=swap_units_0_1          units 0 and 1 prove each other's words
  RT2=const_row_flip_u3       unit 3's constant bit set to 0 (the Δ copy of the pinned column)
  RT2=unused_input_bit_u2     unit 2's input column 100 (an unused, forced-zero input bit) set to 1
  RT2=out_unused_bit_claim    the verifier's file claims bit 40 (unused) of unit 7's output word
Run with `selftest --only honest`; `accepted` is the verdict.  Usage: rtf2_ir_patch.py backends/flock/live/src/bin/flock-ir-block.rs
"""
import sys

EDITS = [
    ("""fn wit(st: &Arc<IrStmt>, inst: &Arc<IrInstances>, input_flip: bool, flip_z: Option<usize>, zero: bool) -> Wit {
    let (st2, inst2) = (st.clone(), inst.clone());
    Wit {
        inputs: Box::new(move |g| {
            if zero {
                return vec![F128::ZERO; st2.net.in_words];
            }
            let mut r = st2.honest_inputs(&inst2)(g);
""",
     """fn wit(st: &Arc<IrStmt>, inst: &Arc<IrInstances>, input_flip: bool, flip_z: Option<usize>, zero: bool) -> Wit {
    let (st2, inst2) = (st.clone(), inst.clone());
    let rt = std::env::var("RT2").unwrap_or_default();
    Wit {
        inputs: Box::new(move |g| {
            if zero {
                return vec![F128::ZERO; st2.net.in_words];
            }
            let g = match rt.as_str() {
                "padding_nonzero_input" if g == st2.units_real => 0,
                "swap_units_0_1" if g < 2 => 1 - g,
                _ => g,
            };
            let mut r = st2.honest_inputs(&inst2)(g);
"""),
    ("""    let flip = plan.unit_flip.then_some((5 << st.unit_log) + st.net.in_words * 128 + 40);
""",
     """    let flip = match std::env::var("RT2").unwrap_or_default().as_str() {
        "const_row_flip_u3" => Some((3 << st.unit_log) + st.net.const_pos),
        "unused_input_bit_u2" => Some((2 << st.unit_log) + 100),
        _ => plan.unit_flip.then_some((5 << st.unit_log) + st.net.in_words * 128 + 40),
    };
    eprintln!("RT2 {:?} flip_z {:?} units_real {} per_block {} blocks {}", std::env::var("RT2").ok(), flip, st.units_real, st.units, st.blocks());
"""),
    ("""    let vinst = if name == "output_claim_false" { Arc::new(false_claim(inst)) } else { inst.clone() };
""",
     """    let vinst = if name == "output_claim_false" {
        Arc::new(false_claim(inst))
    } else if std::env::var("RT2").ok().as_deref() == Some("out_unused_bit_claim") {
        let mut bad = (**inst).clone();
        bad.outputs[7 * bad.out_words].lo ^= 1 << 40;
        Arc::new(bad)
    } else {
        inst.clone()
    };
"""),
]


def main(path):
    src = open(path).read()
    for old, new in EDITS:
        n = src.count(old)
        if n != 1:
            sys.exit(f"anchor found {n} times: {old[:80]!r}")
        src = src.replace(old, new)
    open(path, "w").write(src)
    print(f"rtf2_ir_patch: {len(EDITS)} edits applied to {path}")


if __name__ == "__main__":
    main(sys.argv[1])
