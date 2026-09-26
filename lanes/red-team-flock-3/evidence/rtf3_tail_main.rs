// red-team-flock-3 harness (not part of the reviewed code): the attention tail's primitives through `ir_tail::apply`.
//   rtf3-tail TABLES lines                 stdin lines `PRIM hex...` -> one hex result per line
//   rtf3-tail TABLES exhaustive PRIM LO HI  every u32 input in [LO<<24, HI<<24) -> raw u32 LE results on stdout
// PRIM: addf subf mulf fmaf fmasubf max guard ex2 invsum f2fp. Included by src/bin/rtf3-tail.rs (pod) or a local shim crate.
use std::io::{BufRead, Write};

fn prim(name: &str) -> ir_tail::Prim {
    use ir_tail::Prim::*;
    match name {
        "addf" => F32AddFtz,
        "subf" => F32SubFtz,
        "mulf" => F32MulFtz,
        "fmaf" => F32FmaFtz,
        "fmasubf" => F32FmaSubFtz,
        "max" => F32Max,
        "guard" => GuardNegInfZero,
        "ex2" => MufuEx2Ftz,
        "invsum" => Fa2InvSum,
        "f2fp" => F2fpBf16,
        other => panic!("unknown prim {other}"),
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let need = ["rcp", "ex2"].into_iter().collect();
    let t = ir_tail::Tables::load(&a[1], &need).expect("tables");
    let mut out = std::io::BufWriter::with_capacity(1 << 24, std::io::stdout());
    match a[2].as_str() {
        "lines" => {
            for line in std::io::stdin().lock().lines() {
                let line = line.unwrap();
                let v: Vec<&str> = line.split_whitespace().collect();
                let x: Vec<u32> = v[1..].iter().map(|s| u32::from_str_radix(s, 16).unwrap()).collect();
                writeln!(out, "{:08x}", ir_tail::apply(prim(v[0]), &x, &t)).unwrap();
            }
        }
        "exhaustive" => {
            let p = prim(&a[3]);
            let (lo, hi): (u64, u64) = (a[4].parse().unwrap(), a[5].parse().unwrap());
            let mut buf = vec![0u8; 4 << 24];
            for c in lo..hi {
                for (i, o) in buf.chunks_mut(4).enumerate() {
                    let x = ((c << 24) | i as u64) as u32;
                    o.copy_from_slice(&ir_tail::apply(p, &[x], &t).to_le_bytes());
                }
                out.write_all(&buf).unwrap();
            }
        }
        m => panic!("mode {m}"),
    }
}
