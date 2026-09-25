//! flock-bench (verity): O(N) primitives of the survey's §3.8 public-coin bit link, timed at verity's
//! batch bit counts. Not the link protocol: no commitment, no prime-field proof.
//!   eq:     E_i = eq(r, i) in GF(2^128) for all i < 2^m (flock_multilinear::eq_table)
//!   count:  prover side, c_t = sum_i b_i * bit_t(E_i) for t < 128 (integer identity c_t = y_t + 2 u_t),
//!           via 16 byte-position histograms per set bit; checks c_t mod 2 == bit_t(y), y = z-hat(r) = XOR_{b_i=1} E_i
//!   fold:   coefficient vector w_i = sum_t alpha_t * bit_t(E_i) over Goldilocks, 16 byte-table lookups per i
//!           (the dense linear constraint's coefficients after a prime-field batching challenge)
//! env: LP_LOGS="24 26 27 28" (m = log2 N bits), LP_RUNS=3. Output: `RESULT\t{json}` per m.

use std::{env::var, hint::black_box, time::Instant};

use flock_core::test_rng::Rng;
use flock_multilinear::{IndexOrder, eq_table};
use flock_prover::field::F128;
use rayon::prelude::*;

const P: u64 = 0xFFFF_FFFF_0000_0001;
fn addp(a: u64, b: u64) -> u64 {
    let (s, c) = a.overflowing_add(b);
    let (s2, c2) = s.overflowing_sub(P);
    if c || !c2 { s2 } else { s }
}

fn main() {
    let logs: Vec<usize> = var("LP_LOGS")
        .unwrap_or_else(|_| "24 26 27 28".into())
        .split([' ', ','])
        .filter(|t| !t.is_empty())
        .map(|t| t.parse().unwrap())
        .collect();
    let runs: usize = var("LP_RUNS").ok().and_then(|s| s.parse().ok()).unwrap_or(3);
    let threads = rayon::current_num_threads();
    let mut rng = Rng::new(0x11A4_0001);
    let mut r64 = move || (rng.next_u32() as u64) << 32 | rng.next_u32() as u64;
    for &m in &logs {
        let n = 1usize << m;
        let point: Vec<F128> = (0..m).map(|_| F128 { lo: r64(), hi: r64() }).collect();
        let mut bits = vec![0u64; n / 64];
        let mut s = 0x9E37_79B9_7F4A_7C15u64 ^ m as u64;
        for w in bits.iter_mut() {
            s ^= s << 13;
            s ^= s >> 7;
            s ^= s << 17;
            *w = s;
        }
        let alpha: Vec<u64> = (0..128).map(|_| r64() % P).collect();
        let mut table = vec![[0u64; 256]; 16];
        for pos in 0..16 {
            for byte in 0..256usize {
                let mut acc = 0u64;
                for b in 0..8 {
                    if byte >> b & 1 == 1 {
                        acc = addp(acc, alpha[pos * 8 + b]);
                    }
                }
                table[pos][byte] = acc;
            }
        }
        let (mut t_eq, mut t_cnt, mut t_fold) = (f64::INFINITY, f64::INFINITY, f64::INFINITY);
        let mut parity_ok = true;
        for _ in 0..runs {
            let t0 = Instant::now();
            let e = eq_table(&point, F128::ONE, IndexOrder::LowToHigh);
            t_eq = t_eq.min(t0.elapsed().as_secs_f64());
            assert_eq!(e.len(), n);

            let t1 = Instant::now();
            let (hist, y) = e
                .par_chunks(1 << 16)
                .zip(bits.par_chunks(1 << 10))
                .map(|(ec, bc)| {
                    let mut h = vec![[0u32; 256]; 16];
                    let mut y = F128::ZERO;
                    for (j, &w) in bc.iter().enumerate() {
                        let mut w = w;
                        while w != 0 {
                            let i = j * 64 + w.trailing_zeros() as usize;
                            w &= w - 1;
                            let v = ec[i];
                            y = y + v;
                            let lo = v.lo.to_le_bytes();
                            let hi = v.hi.to_le_bytes();
                            for p in 0..8 {
                                h[p][lo[p] as usize] += 1;
                                h[8 + p][hi[p] as usize] += 1;
                            }
                        }
                    }
                    (h, y)
                })
                .reduce(
                    || (vec![[0u32; 256]; 16], F128::ZERO),
                    |(mut a, ya), (b, yb)| {
                        for p in 0..16 {
                            for k in 0..256 {
                                a[p][k] += b[p][k];
                            }
                        }
                        (a, ya + yb)
                    },
                );
            let mut counts = [0u64; 128];
            for p in 0..16 {
                for k in 0..256 {
                    for b in 0..8 {
                        if k >> b & 1 == 1 {
                            counts[p * 8 + b] += hist[p][k] as u64;
                        }
                    }
                }
            }
            t_cnt = t_cnt.min(t1.elapsed().as_secs_f64());
            for t in 0..128 {
                let yt = if t < 64 { y.lo >> t & 1 } else { y.hi >> (t - 64) & 1 };
                parity_ok &= counts[t] & 1 == yt;
            }

            let t2 = Instant::now();
            let w: Vec<u64> = e
                .par_iter()
                .map(|v| {
                    let lo = v.lo.to_le_bytes();
                    let hi = v.hi.to_le_bytes();
                    let mut acc = 0u64;
                    for p in 0..8 {
                        acc = addp(acc, table[p][lo[p] as usize]);
                        acc = addp(acc, table[8 + p][hi[p] as usize]);
                    }
                    acc
                })
                .collect();
            t_fold = t_fold.min(t2.elapsed().as_secs_f64());
            black_box(&w);
            drop(e);
        }
        assert!(parity_ok, "count parity != z-hat(r)");
        println!(
            "RESULT\t{{\"m\":{m},\"n_bits\":{n},\"threads\":{threads},\"eq_s\":{t_eq:.4},\"count_s\":{t_cnt:.4},\"fold_s\":{t_fold:.4},\
             \"eq_ns_per_bit\":{:.3},\"count_ns_per_bit\":{:.3},\"fold_ns_per_bit\":{:.3},\"parity_ok\":{parity_ok}}}",
            t_eq * 1e9 / n as f64,
            t_cnt * 1e9 / n as f64,
            t_fold * 1e9 / n as f64
        );
    }
}
