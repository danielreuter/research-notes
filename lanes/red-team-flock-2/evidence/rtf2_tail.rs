//! red-team-flock-2 harness (not part of the reviewed code): `ir_tail::apply` on stdin lines `PRIM hex...`, one hex result
//! per line. PRIM: add mul div fma rsq sqrt rcp scale. Tables from argv[1] (sha256-checked by `Tables::load`).
use flock_live::ir_tail::{Prim, Tables, apply};
use std::io::{BufRead, Write};

fn main() {
    let dir = std::env::args().nth(1).expect("tables dir");
    let need = ["rsq", "sqrt", "rcp"].into_iter().collect();
    let t = Tables::load(&dir, &need).expect("tables");
    let mut out = std::io::BufWriter::new(std::io::stdout());
    for line in std::io::stdin().lock().lines() {
        let line = line.unwrap();
        let v: Vec<&str> = line.split_whitespace().collect();
        let p = match v[0] {
            "add" => Prim::F32Add,
            "mul" => Prim::F32Mul,
            "div" => Prim::F32Div,
            "fma" => Prim::F32Fma,
            "rsq" => Prim::RsqrtApprox,
            "sqrt" => Prim::MufuSqrtFtz,
            "rcp" => Prim::DivFullRcp,
            "scale" => Prim::DivFullScaleA,
            other => panic!("unknown prim {other}"),
        };
        let a: Vec<u32> = v[1..].iter().map(|x| u32::from_str_radix(x, 16).unwrap()).collect();
        writeln!(out, "{:08x}", apply(p, &a, &t)).unwrap();
    }
}
