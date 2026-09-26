#!/usr/bin/env python3
"""red-team-flock-3: env-driven prover-side attack knobs for flock-ir-frame.rs (verity/flock-ir-frame/v3, PR #54 @ 22dc6320 /
0839742b); the verifier is untouched. Run with `selftest --only honest`; `accepted` is the verdict (each must be refused).

  RT3=zero_leaf_run_message     a real P.V unit's zero leaf (a masked key's V word): its empty run slot's message set to 1.0
                                (0x3F80) at the wired bytes and the slot re-hashed; the unit reads it; P = 0 there, so the unit's
                                output is unchanged: only the empty run's verifier-fixed chaining values can refuse it
  RT3=zero_leaf_run_published   the same, with the re-hashed value published as that slot's public
  RT3=hole_cut_input            a hole (an empty unit slot of a real block, a masked key's QK step) reads a = 1.0 in its first
                                cut port (b = 0 there, so its output stays the dummy +0): only the CutIn region can refuse it
  RT3=pv_acc_rescale_forged     the first P.V unit whose accumulator is the tail's rescaled O (F32MulFtz, a block boundary)
                                reads that accumulator with bit 5 flipped
  RT3=pv_p_word_forged          the first P.V unit reading a tail P word (F2fpBf16) reads it with bit 3 flipped
  RT3=short_chunk_end_moved     the last run of a short last chunk (a multi-chunk row): CHUNK_END moved from its last block to
                                the one before, the run re-hashed, publics honest
  RT3=short_chunk_counter       the same run's counter + 1, re-hashed, publics honest
  RT3=short_chunk_cv_public     the same run's published chunk value forged (what C4 folds into the row digest)
"""
import sys

EDITS = [
    ("""    let rows_s = t0.elapsed().as_secs_f64();
    let publics = FrameStmt::publics_bytes(&cvs);
""",
     """    let rt = std::env::var("RT3").unwrap_or_default();
    let (cs, nb) = (st.lay.comp_slots, st.lay.nb);
    let short_last = || -> (usize, usize) {
        inst.blocks.iter().enumerate().take(st.blocks_real).find_map(|(b, bl)| bl.0.iter().position(|c| c.is_some_and(|(_, p, ci, r)|
            inst.chunks_of(p) > 1 && inst.blocks_of(p, ci) < 16 && r + 1 == inst.runs_of(p, ci))).map(|q| (b, q)))
            .expect("a short last chunk of a multi-chunk row")
    };
    match rt.as_str() {
        "zero_leaf_run_message" | "zero_leaf_run_published" => {
            let (b, u, j, q, off) = inst.blocks.iter().enumerate().take(st.blocks_real).find_map(|(b, bl)| {
                bl.1.iter().enumerate().filter(|x| x.1.is_some()).find_map(|(u, _)| st.lay.wiring[u].iter().enumerate()
                    .find(|(_, w)| bl.0[w.0].is_none()).map(|(j, w)| (b, u, j, w.0, w.1)))
            }).expect("a real unit reading a zero leaf");
            let at = b * cs + q * nb + off / 64;
            let (w, sh) = ((off % 64) / 4, 8 * ((off % 64) % 4));
            comps[at].1[w] |= 0x3F80 << sh;
            let v = rechain(&mut comps, b * cs + q * nb, nb);
            if rt == "zero_leaf_run_published" {
                cvs[b][q] = v;
            }
            eprintln!("RT3 {rt}: block {b} unit slot {u} port {j} reads empty run slot {q} byte {off}");
        }
        "short_chunk_end_moved" => {
            let (b, q) = short_last();
            let at = b * cs + q * nb;
            comps[at + nb - 1].4 &= !flock_live::chunk::CHUNK_END;
            comps[at + nb - 2].4 |= flock_live::chunk::CHUNK_END;
            rechain(&mut comps, at, nb);
            eprintln!("RT3 {rt}: block {b} run slot {q}");
        }
        "short_chunk_counter" => {
            let (b, q) = short_last();
            let at = b * cs + q * nb;
            for c in &mut comps[at..at + nb] {
                c.2 += 1;
            }
            rechain(&mut comps, at, nb);
            eprintln!("RT3 {rt}: block {b} run slot {q}");
        }
        "short_chunk_cv_public" => {
            let (b, q) = short_last();
            cvs[b][q][0] ^= 1;
            eprintln!("RT3 {rt}: block {b} run slot {q}");
        }
        _ => {}
    }
    let rows_s = t0.elapsed().as_secs_f64();
    let publics = FrameStmt::publics_bytes(&cvs);
"""),
    ("""        inputs: Box::new(move |b, u| {
            let mut r = st2.unit_inputs(&i2, &c2, b, u);
""",
     """        inputs: Box::new(move |b, u| {
            let mut r = st2.unit_inputs(&i2, &c2, b, u);
            let rt = std::env::var("RT3").unwrap_or_default();
            let put = |r: &mut Vec<F128>, c: usize, bit: u64| if c % 128 < 64 { r[c / 128].lo ^= bit << (c % 128) } else { r[c / 128].hi ^= bit << (c % 128 - 64) };
            if rt == "hole_cut_input" && b < st2.blocks_real && i2.blocks[b].1[u].is_none()
                && i2.blocks[b].1.iter().any(|x| x.is_some())
            {
                let c = st2.cm.unit_in[0][0].0;
                put(&mut r, c, 0x3F80);
            }
            if rt == "pv_acc_rescale_forged" || rt == "pv_p_word_forged" {
                let want = if rt == "pv_acc_rescale_forged" { flock_live::ir_tail::Prim::F32MulFtz } else { flock_live::ir_tail::Prim::F2fpBf16 };
                let by: std::collections::BTreeSet<usize> = st2.cm.tail.iter().filter(|o| o.prim == want).map(|o| o.out).collect();
                let pick = (0..i2.upi).find_map(|lu| st2.cm.unit_in[lu].iter().position(|&(c, k)| by.contains(&k)
                    && (rt == "pv_p_word_forged" || c == st2.cm.unit_in[lu].last().unwrap().0)).map(|j| (lu, st2.cm.unit_in[lu][j].0)));
                if let (Some((lu, c)), Some(g)) = (pick, i2.blocks.get(b).and_then(|bl| bl.1[u])) {
                    if g == lu {
                        put(&mut r, c, if rt == "pv_acc_rescale_forged" { 1 << 5 } else { 1 << 3 });
                    }
                }
            }
"""),
]


def main(path):
    src = open(path).read()
    for old, new in EDITS:
        if src.count(old) != 1:
            sys.exit(f"anchor found {src.count(old)} times: {old[:70]!r}")
        src = src.replace(old, new)
    open(path, "w").write(src)
    print(f"rtf3_frame_patch: {len(EDITS)} edits applied to {path}")


if __name__ == "__main__":
    main(sys.argv[1])
