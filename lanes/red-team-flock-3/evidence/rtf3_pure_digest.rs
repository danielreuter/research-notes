// red-team-flock-3 harness (not reviewed code): the flock-pure-block statement digest, dense m and region count for every
// layout, from `PureStmt::new(net, vus, layout)` only, so one source compiles against main and PR #87 alike.
//   rtf3-pure-digest NET544 NET608 [VUS]
use flock_live::pure_block::{Layout, PureStmt, UnitNet};

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let vus: usize = a.get(3).map(|s| s.parse().unwrap()).unwrap_or(8);
    let lays: Vec<(String, Layout, bool)> = vec![
        ("Chunk(2)".into(), Layout::Chunk(2), false),
        ("Chunk(3)".into(), Layout::Chunk(3), false),
        ("Chunk(4)".into(), Layout::Chunk(4), false),
        ("Chunk(8)".into(), Layout::Chunk(8), false),
        ("Chunk(16)".into(), Layout::Chunk(16), false),
        ("ChunkTail(4)".into(), Layout::ChunkTail(4), false),
        ("ChunkTail(17)".into(), Layout::ChunkTail(17), false),
        ("Fp8".into(), Layout::Fp8, false),
        ("ShaFp8".into(), Layout::ShaFp8, false),
        ("ShaBf16".into(), Layout::ShaBf16, false),
        ("Fp4".into(), Layout::Fp4, true),
        ("ShaFp4".into(), Layout::ShaFp4, true),
    ];
    for (name, lay, fp4) in lays {
        let net = UnitNet::load(if fp4 { &a[2] } else { &a[1] });
        let r = std::panic::catch_unwind(|| {
            let st = PureStmt::new(net, vus, lay);
            (st.digest.iter().map(|b| format!("{b:02x}")).collect::<String>(), st.m, st.regions.len())
        });
        match r {
            Ok((d, m, nr)) => println!("DIGEST\t{name}\tvus={vus}\tm={m}\tregions={nr}\t{d}"),
            Err(_) => println!("DIGEST\t{name}\tvus={vus}\tPANIC"),
        }
    }
}
