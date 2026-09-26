#!/usr/bin/env python3
"""red-team-flock-3: a prover-side knob for flock-pure-gpu.rs (PR #87 @ 28f55d9a), the verifier untouched.
RT3_UNIT_FLIP=ROW:UNIT makes the `unit_internal_bit_flipped` case flip witness bit ROW of unit UNIT's 2^ul slot (instead of
row 700 of unit 5), so padding rows past the netlist, the constant row, the last slot's last bit and rows 8192..2^14 (the next
unit's slot at ul = 13) can be attacked. Run with `selftest --only unit_internal_bit_flipped`; every flip must be refused.
"""
import sys

OLD = "        _ => plan.unit_flip.then_some(700 + ((st.lay.unit_pos0(st.ul) + 5) << st.ul)),\n"
NEW = """        _ => plan.unit_flip.then(|| match std::env::var("RT3_UNIT_FLIP").ok().and_then(|s| s.split_once(':').map(|(r, u)| (r.parse::<usize>().unwrap(), u.parse::<usize>().unwrap()))) {
            Some((row, unit)) => row + ((st.lay.unit_pos0(st.ul) + unit) << st.ul),
            None => 700 + ((st.lay.unit_pos0(st.ul) + 5) << st.ul),
        }),
"""


def main(path):
    src = open(path).read()
    if src.count(OLD) != 1:
        sys.exit(f"anchor found {src.count(OLD)} times")
    open(path, "w").write(src.replace(OLD, NEW))
    print("rtf3_pure_patch: 1 edit applied to", path)


if __name__ == "__main__":
    main(sys.argv[1])
