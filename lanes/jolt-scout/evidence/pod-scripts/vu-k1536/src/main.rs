//! jolt-scout VU host: synthetic in-domain BF16 rows (the frozen vu-k1536 rows are not on the pod), y from the same
//! kernel natively, then per (B, mode): trace length (analyze), prove wall time, verify.
//! Env: VU_NS (default "1,4,16"), MODES (default "0,1"), REPS (default 2).
use std::time::Instant;

fn xorshift(s: &mut u64) -> u64 {
    *s ^= *s << 13;
    *s ^= *s >> 7;
    *s ^= *s << 17;
    *s
}

/// A normal BF16 word with exponent field 118..=136 (|v| about 2^-9 .. 2^10), or +0 with probability 1/256.
fn word(s: &mut u64) -> u64 {
    let r = xorshift(s);
    if r & 0xFF == 0 {
        return 0;
    }
    let sign = (r >> 8) & 1;
    let exp = 118 + (r >> 9) % 19;
    let man = (r >> 20) & 0x7F;
    (sign << 15) | (exp << 7) | man
}

fn gen(n: usize, seed: u64) -> (Vec<u64>, Vec<u16>) {
    let rw = guest::kernel::ROW_WORDS;
    let mut s = seed | 1;
    let (mut rows, mut y) = (Vec::with_capacity(n * 2 * rw), Vec::with_capacity(n));
    while y.len() < n {
        let vu: Vec<u64> = (0..2 * rw)
            .map(|_| word(&mut s) | word(&mut s) << 16 | word(&mut s) << 32 | word(&mut s) << 48)
            .collect();
        if let Some(out) = guest::kernel::check_vu(&vu[..rw], &vu[rw..]) {
            rows.extend_from_slice(&vu);
            y.push(out);
        }
    }
    (rows, y)
}

fn list(key: &str, default: &str) -> Vec<usize> {
    std::env::var(key).unwrap_or(default.into()).split(',').map(|v| v.trim().parse().unwrap()).collect()
}

pub fn main() {
    tracing_subscriber::fmt::init();
    let reps = list("REPS", "2")[0];
    let t = Instant::now();
    let mut program = guest::compile_vu_batch("/tmp/jolt-guest-targets");
    println!("COMPILE_GUEST {:.2}s", t.elapsed().as_secs_f64());
    let t = Instant::now();
    let shared = guest::preprocess_shared_vu_batch(&mut program).unwrap();
    let prover_pp = guest::preprocess_prover_vu_batch(shared.clone());
    let verifier_pp = guest::verifier_preprocessing_from_prover_vu_batch(&prover_pp);
    println!("PREPROCESS {:.2}s", t.elapsed().as_secs_f64());
    let prove = guest::build_prover_vu_batch(program, prover_pp);
    let verify = guest::build_verifier_vu_batch(verifier_pp);
    for &n in &list("VU_NS", "1,4,16") {
        for &mode in &list("MODES", "0,1") {
            let (words, y) = gen(n, 0x5eed_0000 + n as u64);
            let rows = serde_bytes::ByteBuf::from(words.iter().flat_map(|w| w.to_le_bytes()).collect::<Vec<u8>>());
            let native = guest::vu_batch(rows.clone(), y.clone(), mode as u8);
            assert!(native.0, "native check failed");
            let summary = guest::analyze_vu_batch(rows.clone(), y.clone(), mode as u8);
            let tl = summary.trace_len();
            println!("TRACE B={n} mode={mode} trace_len={tl} per_vu={:.0}", tl as f64 / n as f64);
            for rep in 0..reps {
                let t = Instant::now();
                let (output, proof, io) = prove(rows.clone(), y.clone(), mode as u8);
                let tp = t.elapsed().as_secs_f64();
                let padded = proof.trace_length;
                let t = Instant::now();
                let valid = verify(rows.clone(), y.clone(), mode as u8, output.clone(), io.panic, proof);
                let tv = t.elapsed().as_secs_f64();
                println!(
                    "RESULT B={n} mode={mode} rep={rep} trace_len={tl} proof_trace_length={padded} prove_s={tp:.3} verify_s={tv:.3} ok={} valid={valid}",
                    output.0
                );
            }
        }
    }
}
